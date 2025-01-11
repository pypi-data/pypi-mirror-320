"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Representation of linear combinations of operator tensor products.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sized
from functools import cached_property
from itertools import chain
from operator import itemgetter
from types import MappingProxyType
from typing import Literal

from attrs import evolve, field, frozen, resolve_types
from symengine import Expr, Symbol
from typing_extensions import Self, TypeGuard, override

from parityos.base.bit import Qubit
from parityos.base.operator_product import OperatorProduct
from parityos.base.operators.operator import (
    OperatorCompound,
    OperatorT,
    OtherOperatorT,
    Parameterized,
)
from parityos.base.utils import (
    Weight,
    WeightTypes,
    collect_pairs,
    is_iterable_of_pairs_mapping,
)


def _to_unique_term_weight_pairs(
    elements: (
        Iterable[tuple[OperatorProduct[OperatorT], Weight]]
        | Mapping[OperatorProduct[OperatorT], Weight]
    ),
) -> frozenset[tuple[OperatorProduct[OperatorT], Weight]]:
    if is_iterable_of_pairs_mapping(elements):
        term_weight_pairs = elements.items()
    else:
        term_weight_pairs = collect_pairs(elements)
    # convert all weights to floats and remove zero weight contributions
    return frozenset({(term, weight) for term, weight in term_weight_pairs if weight != 0})


@frozen(order=False)
class OperatorPolynomial(OperatorCompound[OperatorT], Sized, Parameterized):
    """Represents a linear combinations of operator tensor products.

    Constituent operator tensor products are called `terms` and are stored together with
    their weights as a set if (term, weight) pairs.

    :param term_weight_pairs: mapping or iterable of (operator_product, weight) pairs
    """

    term_weight_pairs: frozenset[tuple[OperatorProduct[OperatorT], Weight]] = field(
        converter=_to_unique_term_weight_pairs,
    )

    @cached_property
    def term_to_weight(self) -> MappingProxyType[OperatorProduct[OperatorT], Weight]:
        return MappingProxyType(dict(self.term_weight_pairs))

    @override
    def __str__(self) -> str:
        # we can't just do " + ".join() because of negative weights
        sorted_term_weight_pairs = sorted(self.term_weight_pairs, key=itemgetter(0))
        result = " ".join(
            [f"{weight_to_prefix_str(weight)}{term}" for term, weight in sorted_term_weight_pairs]
        )
        return result.lstrip("+").strip()

    @property
    def n_terms(self) -> int:
        return len(self.term_weight_pairs)

    @override
    def __len__(self) -> int:
        return self.n_terms

    @property
    def terms(self) -> frozenset[OperatorProduct[OperatorT]]:
        return frozenset([term for term, _ in self.term_weight_pairs])

    @property
    def weights(self) -> frozenset[Weight]:
        return frozenset([weight for _, weight in self.term_weight_pairs])

    ## OperatorCompound Interface ##################################################################
    @override
    def is_all(self, cls: type[OtherOperatorT]) -> TypeGuard[OperatorPolynomial[OtherOperatorT]]:
        return all([term.is_all(cls) for term in self.terms])

    @property
    @override
    def is_mixed(self) -> bool:
        return len({type(operator) for term in self.terms for operator in term.operators}) > 1

    ## OperatorLike Interface ######################################################################
    @property
    @override
    def name(self) -> str:
        return "+".join(sorted([term.name for term in self.terms]))

    @cached_property
    @override
    def qubits(self) -> frozenset[Qubit]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return frozenset().union(*[term.qubits for term in self.terms])

    @override
    def get_hermitian_conjugate(self) -> Self:
        return evolve(
            self,
            term_weight_pairs={
                term.get_hermitian_conjugate(): weight for term, weight in self.term_weight_pairs
            },
        )

    @property
    @override
    def is_hermitian(self) -> bool:
        return all([term.is_hermitian for term in self.terms])

    @property
    @override
    def parameters(self) -> frozenset[Symbol]:
        symbols = [weight.free_symbols for weight in self.weights if isinstance(weight, Expr)]
        return frozenset[Symbol]().union(*symbols)

    ## Arithmetic ##################################################################################
    def __neg__(self) -> OperatorPolynomial[OperatorT]:
        return evolve(
            self, term_weight_pairs={term: -weight for term, weight in self.term_weight_pairs}
        )

    def __mul__(self, other: Weight) -> Self:
        if isinstance(other, WeightTypes):
            return evolve(
                self,
                term_weight_pairs=[
                    (term, other * weight) for term, weight in self.term_weight_pairs
                ],
            )
        return NotImplemented

    def __truediv__(self, other: Weight) -> Self:
        return self.__mul__(1 / other)

    __rmul__ = __mul__  # pyright: ignore[reportUnannotatedClassAttribute]
    __rtruediv__ = __truediv__  # pyright: ignore[reportUnannotatedClassAttribute]

    def __add__(
        self, other: Literal[0] | OperatorPolynomial[OtherOperatorT]
    ) -> OperatorPolynomial[OperatorT | OtherOperatorT]:
        # enable sum(polynomials)
        if other == 0:
            return self
        if isinstance(other, OperatorPolynomial):
            return evolve(
                self,
                # don't use dict.update, as it overwrites duplicate entries
                term_weight_pairs=chain(self.term_weight_pairs, other.term_weight_pairs),
            )
        return NotImplemented

    def __radd__(self, other: Literal[0]) -> OperatorPolynomial[OperatorT]:
        return self.__add__(other)

    def __sub__(
        self, other: OperatorPolynomial[OtherOperatorT]
    ) -> OperatorPolynomial[OperatorT | OtherOperatorT]:
        if isinstance(other, OperatorPolynomial):
            return self.__add__(-other)
        return NotImplemented


# TODO(VS): This is a workaround for the issue # https://github.com/python-attrs/cattrs/issues/427
#  check regularly if this is resolved
resolve_types(OperatorPolynomial)


def weight_to_prefix_str(weight: Weight) -> str:
    """
    Construct a string prefix for an OperatorProduct str representation containing the weight
    with a sign.
    """
    if weight == 1:
        return "+ "
    if weight == -1:
        return "- "

    weight_str = str(weight)
    # expression contains multiple terms
    if " " in weight_str:
        weight_str = f"({weight_str})"

    if weight_str.startswith("-"):
        weight_str = "- " + weight_str[1:]
    else:
        weight_str = "+ " + weight_str
    return weight_str.lstrip() + "*"
