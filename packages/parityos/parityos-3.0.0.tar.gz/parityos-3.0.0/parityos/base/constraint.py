"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Representations of constraints on qubits.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import overload

from attrs import Attribute, evolve, field, frozen
from typing_extensions import Self, override

from parityos.base.bit import Qubit
from parityos.base.io_utils import register_subclasses
from parityos.base.operator_polynomial import OperatorPolynomial
from parityos.base.operator_product import OperatorProduct
from parityos.base.operators.operator import OperatorCompound, Z
from parityos.base.state import Parity, PauliBasisState, bit_to_spin_value
from parityos.base.utils import to_tuple

CONSTRAINT_TYPE_TAG = "constraint_type"


@frozen
class Constraint(ABC):
    """Interface for constraints between qubits."""

    @classmethod
    def __attrs_init_subclass__(cls) -> None:
        register_subclasses(Constraint, CONSTRAINT_TYPE_TAG)

    @property
    @abstractmethod
    def qubits(self) -> frozenset[Qubit]:
        """Qubits which are constrained by this contraint."""

    @abstractmethod
    def is_satisfied(self, state: PauliBasisState) -> bool:
        """Evaluate whether the constraint is satisfied by the given state.

        :param state: A pauli basis state.
            All qubits from the constraint must be present in the state.
        """

    @abstractmethod
    def __lt__(self, other: object) -> bool:
        """Comparison to enable sorting of constraints."""


@overload
def _check_all_z(
    self: ProductConstraint,
    _: Attribute[OperatorProduct[Z]],
    operator_compound: OperatorProduct[Z],
) -> None: ...
@overload
def _check_all_z(
    self: SumConstraint,
    _: Attribute[OperatorPolynomial[Z]],
    operator_compound: OperatorPolynomial[Z],
) -> None: ...
def _check_all_z(self: Constraint, _, operator_compound: OperatorCompound[Z]):
    if not operator_compound.is_all(Z):
        raise TypeError(f"{type(self).__name__} requires all Z operators")


@frozen
class ProductConstraint(Constraint):
    """Represents a constraint given by a tensor product of Z Operators.

    Constraints arising from the parity mapping are of this type.

    ProductConstraints can have even or odd parity. If even, passed states must evaluate
    to even parity (False). If odd, passed states must evaluate to odd parity (True).

    This is in accordance with the convention used in parityos.base.state.bit_to_spin_value

    :param operator_product: tensor product of Z operators acting on qubits which are constrained.
    :param parity: even if False, odd if True (default=False).
    :raises TypeError: if not all of the given operators are Z operators.
    """

    operator_product: OperatorProduct[Z] = field(validator=_check_all_z)
    parity: Parity = field(default=False)

    @override
    def __str__(self) -> str:
        return f"{self.operator_product} = {'odd' if self.parity else 'even'}"

    @classmethod
    def from_qubits(cls, qubits: Qubit | Iterable[Qubit], parity: bool = False) -> Self:
        return cls(OperatorProduct([Z(qubit) for qubit in to_tuple(qubits)]), parity)

    @override
    def is_satisfied(self, state: PauliBasisState) -> bool:
        return state.evaluate_parity(self.qubits) == self.parity

    ## OperatorLike Interface ######################################################################

    @property
    @override
    def qubits(self) -> frozenset[Qubit]:
        return self.operator_product.qubits

    def get_hermitian_conjugate(self) -> ProductConstraint:
        return evolve(
            self,
            operator_product=self.operator_product.get_hermitian_conjugate(),
        )

    ################################################################################################

    @override
    def __lt__(self, other: object) -> bool:
        if isinstance(other, ProductConstraint):
            return self.operator_product < other.operator_product
        # sort ProductConstraints before SumConstraints
        if isinstance(other, SumConstraint):
            return True
        return NotImplemented


@frozen
class SumConstraint(Constraint):
    """Represents a constraint given by a sum of ProductConstraints.

    :param operator_polynomial: linear combination of tensor products of Z acting on qubits which
        are constrained.
    :param value: value for which this constraint is fulfilled (default=0).
    :raises TypeError: if not all of the given operators are Z operators.
    """

    operator_polynomial: OperatorPolynomial[Z] = field(validator=_check_all_z)
    value: float = field(default=0.0, converter=float)

    @override
    def __str__(self) -> str:
        return f"{self.operator_polynomial} = {self.value}"

    @override
    def is_satisfied(self, state: PauliBasisState) -> bool:
        return (
            sum(
                [
                    weight * bit_to_spin_value(state.evaluate_parity(term.qubits))
                    for term, weight in self.operator_polynomial.term_weight_pairs
                ]
            )
            == self.value
        )

    ## OperatorLike Interface ######################################################################

    @property
    @override
    def qubits(self) -> frozenset[Qubit]:
        return self.operator_polynomial.qubits

    def get_hermitian_conjugate(self) -> SumConstraint:
        return evolve(
            self,
            operator_polynomial=self.operator_polynomial.get_hermitian_conjugate(),
        )

    ################################################################################################

    @override
    def __lt__(self, other: object) -> bool:
        if isinstance(other, SumConstraint):
            return self.operator_polynomial < other.operator_polynomial
        # sort ProductConstraints before SumConstraints
        if isinstance(other, ProductConstraint):
            return False
        return NotImplemented
