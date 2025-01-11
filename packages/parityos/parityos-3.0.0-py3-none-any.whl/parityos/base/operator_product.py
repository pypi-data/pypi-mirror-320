"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Representation of operator tensor products.
"""

from __future__ import annotations

from collections.abc import Sized
from functools import cached_property
from itertools import chain
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal, overload

from attrs import Attribute, evolve, field, frozen, resolve_types
from typing_extensions import Self, TypeGuard, override

from parityos.base.bit import Qubit
from parityos.base.exceptions import ParityOSUniquenessError
from parityos.base.operators.operator import (
    OperatorCompound,
    OperatorT,
    OtherOperatorT,
)
from parityos.base.utils import (
    Weight,
    WeightTypes,
    to_frozenset_check_unique,
)

if TYPE_CHECKING:
    from parityos.base.operator_polynomial import OperatorPolynomial

DEFAULT_WEIGHT = 1.0


def _check_qubits_unique(
    self: OperatorProduct[OperatorT],
    *_: Attribute[frozenset[OperatorT]] | frozenset[OperatorT],
):
    """validation helper to check whether all input operators"""
    # this also automatically checks for duplicate operators
    total_qubits = sum([operator.n_qubits for operator in self.operators])
    if total_qubits != self.n_qubits:
        raise ParityOSUniquenessError(
            f"{type(self).__name__} received {total_qubits- self.n_qubits} duplicate qubits"
        )


@frozen(order=False)
class OperatorProduct(OperatorCompound[OperatorT], Sized):
    """
    Represents a tensor product of operators.

    Constituent operators cannot have overlapping qubits and are considered in no particular order.
    Implements basic arithmetic like addition and multiplication with other Operators,
    OperatorProducts and OperatorPolynomials.

    :param operators: constituent operators, their qubit sets must all be disjoint
    :param weight: scalar weight of operator tensor product (default=1)
    :raises ParityOSUniquenessError: if some operators act on the same qubit(s)
    :raises ParityOSException: if weight is zero
    """

    # TODO(VS) we should think about representing empty products (used as degeneracies) otherwise
    operators: frozenset[OperatorT] = field(
        converter=to_frozenset_check_unique,
        validator=_check_qubits_unique,
    )

    @override
    def __str__(self) -> str:
        return "*".join([str(operator) for operator in sorted(self.operators)])

    @property
    def n_operators(self) -> int:
        return len(self.operators)

    @override
    def __len__(self) -> int:
        return self.n_operators

    @cached_property
    def qubit_to_operator(self) -> MappingProxyType[Qubit, OperatorT]:
        """
        A mapping from qubit to the operator that acts on it in this OperatorProduct.

        As operators are non-overlapping per definition, each qubit maps to exactly one operator.
        """
        return MappingProxyType(
            {qubit: operator for operator in self.operators for qubit in operator.qubits}
        )

    ## OperatorCompound Interface ##################################################################
    # TODO(VS) this is True for any cls for an empty product. Is this fine?
    @override
    def is_all(self, cls: type[OtherOperatorT]) -> TypeGuard[OperatorProduct[OtherOperatorT]]:
        return all([isinstance(operator, cls) for operator in self.operators])

    @property
    @override
    def is_mixed(self) -> bool:
        if self.n_operators < 2:
            return False
        return len({type(operator) for operator in self.operators}) > 1

    ## OperatorLike Interface ######################################################################
    @property
    @override
    def name(self) -> str:
        return "".join(sorted([operator.name for operator in self.operators]))

    @cached_property
    @override
    def qubits(self) -> frozenset[Qubit]:  # pyright: ignore[reportIncompatibleMethodOverride]
        qubits: frozenset[Qubit] = frozenset()
        return qubits.union(*[operator.qubits for operator in self.operators])

    @override
    def get_hermitian_conjugate(self) -> Self:
        return evolve(
            self,
            operators=[operator.get_hermitian_conjugate() for operator in self.operators],
        )

    @property
    @override
    def is_hermitian(self) -> bool:
        return all([operator.is_hermitian for operator in self.operators])

    ## Arithmetic ##################################################################################
    def __neg__(self) -> OperatorPolynomial[OperatorT]:
        return -1 * self

    @overload
    def __mul__(self, other: Weight) -> OperatorPolynomial[OperatorT]: ...
    @overload
    def __mul__(
        self, other: OperatorProduct[OtherOperatorT]
    ) -> OperatorProduct[OperatorT | OtherOperatorT]: ...
    def __mul__(  # pyright: ignore[reportInconsistentOverload]
        self, other: Weight | OperatorProduct[OtherOperatorT]
    ):
        """
        Implement multiplication with
         - scalars: only weight gets modified
         - other operator products: both products must act on disjoint qubit sets
        """
        if isinstance(other, WeightTypes):
            from parityos.base.operator_polynomial import OperatorPolynomial

            return OperatorPolynomial({self: other})
        if isinstance(other, OperatorProduct):
            return evolve(
                self,
                # the __init__ of the result OperatorProduct checks for qubit duplicates
                operators=chain(self.operators, other.operators),
            )
        return NotImplemented

    def __add__(
        self,
        other: Literal[0] | OperatorProduct[OtherOperatorT] | OperatorPolynomial[OtherOperatorT],
    ) -> OperatorPolynomial[OperatorT | OtherOperatorT]:
        from parityos.base.operator_polynomial import (
            OperatorPolynomial,
        )

        """
        Implement addition with
          - scalar zero: to enable sum()
          - other operator products: both products must be linearly independent
          - operator polynomials: operator polynomial terms must be linearly independent from self

        The result is always an OperatorPolynomial
        """

        # enable sum
        if other == 0:
            return OperatorPolynomial(((self, DEFAULT_WEIGHT),))
        if isinstance(other, OperatorProduct):
            if self == other:
                return OperatorPolynomial(((self, 2 * DEFAULT_WEIGHT),))
            else:
                return OperatorPolynomial(((self, DEFAULT_WEIGHT), (other, DEFAULT_WEIGHT)))
        if isinstance(other, OperatorPolynomial):
            return evolve(
                other,
                term_weight_pairs=chain(other.term_weight_pairs, ((self, DEFAULT_WEIGHT),)),
            )
        return NotImplemented

    def __sub__(
        self,
        other: OperatorProduct[OtherOperatorT] | OperatorPolynomial[OtherOperatorT],
    ) -> OperatorPolynomial[OperatorT | OtherOperatorT]:
        """Implement subtraction of operator tensor products or polynomials as self + (-other)."""
        return self + (-other)

    def __rsub__(
        self, other: OperatorPolynomial[OtherOperatorT]
    ) -> OperatorPolynomial[OperatorT | OtherOperatorT]:
        """Implement right subtraction of operator polynomials as -self + other."""
        return -self + other

    __rmul__ = __mul__  # pyright: ignore[reportUnannotatedClassAttribute]
    __radd__ = __add__  # pyright: ignore[reportUnannotatedClassAttribute]


# TODO(VS): This is a workaround for the issue # https://github.com/python-attrs/cattrs/issues/427
#  check regularly if this is resolved
resolve_types(OperatorProduct)
