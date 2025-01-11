"""
ParityQC GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Defines controlled operators, where the state of one or more control qubits
controls whether a certain operator acts on one or more target qubits
"""

from __future__ import annotations

from collections.abc import Iterator
from functools import cached_property
from typing import Union

from attrs import Attribute, evolve, field, frozen
from symengine import Symbol
from typing_extensions import Self, override

from parityos.base.bit import Qubit
from parityos.base.exceptions import ParityOSException, ParityOSUniquenessError
from parityos.base.operator_product import OperatorProduct
from parityos.base.operators.operator import (
    ElementaryOperator,
    Operator,
    Parameterized,
    X,
    Y,
    Z,
)
from parityos.base.operators.rotation_operator import RotationOperator, rx, ry, rz
from parityos.base.utils import (
    Weight,
    stringify_iterable,
    to_frozenset_check_unique,
)


def _check_non_empty(
    self: ControlledOperator,
    attrib: Attribute[frozenset[Qubit]],
    value: frozenset[Qubit],
):
    if len(value) == 0:
        raise ParityOSException(
            f"attribute {attrib.name} of {type(self).__name__} must not be empty."
        )


def _check_control_target_differ(
    self: ControlledOperator, _: Attribute[frozenset[Qubit]], control_qubits: frozenset[Qubit]
):
    """check whether the control and target qubits overlap"""
    overlap = self.target_operator.qubits & control_qubits
    if overlap:
        raise ParityOSUniquenessError(
            f"got qubits that are both target and control qubits: {overlap}"
        )


@frozen(order=False)
class ControlledOperator(Operator, Parameterized):
    """
    Represents a controlled operator, where the state of one or more control qubits
    controls whether a certain operator acts on one or more target qubits

    :param target_operator: operator acting on target qubits depending on the state of the control
        qubits
    :param control_qubits: the control qubits
    """

    target_operator: Union[
        ElementaryOperator,
        RotationOperator,
        OperatorProduct[Union[ElementaryOperator, RotationOperator]],
    ] = field()
    control_qubits: frozenset[Qubit] = field(
        converter=to_frozenset_check_unique,
        validator=[_check_non_empty, _check_control_target_differ],
    )

    @override
    def __str__(self) -> str:
        return (
            f"C(control={stringify_iterable(sorted(self.control_qubits))}, {self.target_operator})"
        )

    @property
    def target_qubits(self) -> frozenset[Qubit]:
        """The qubits `operator` acts on"""
        return self.target_operator.qubits

    ## OperatorLike Interface ######################################################################

    @property
    @override
    def name(self) -> str:
        return str("c" * len(self.control_qubits)) + self.target_operator.name

    @cached_property
    @override
    def qubits(self) -> frozenset[Qubit]:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Combined set of control and target qubits"""
        return self.target_qubits | frozenset(self.control_qubits)

    @override
    def get_hermitian_conjugate(self) -> Self:
        return evolve(self, target_operator=self.target_operator.get_hermitian_conjugate())

    @property
    @override
    def is_hermitian(self) -> bool:
        return self.target_operator.is_hermitian

    @property
    @override
    def parameters(self) -> frozenset[Symbol]:
        """The parameters are the same as those of the target operator."""
        return (
            self.target_operator.parameters
            if isinstance(self.target_operator, Parameterized)
            else frozenset()
        )

    def decompose(self) -> Iterator[ControlledOperator]:
        """Decompose a controlled tensor product (OperatorProduct) into an iterator of
        controlled single operator elements of the tensor product.

        The returned iterator represents the (commuting) sequence of resulting controlled
        single operator targets.

        Examples:
            CX(1)X(2)      -> CX(1)  * CX(2)
            CCZ(1)X(2)Y(3) -> CCZ(1) * CCX(2) * CCY(3)

        >>> assert list(ControlledOperator(
                    Z(get_q(0)) * X(get_q(1)), get_q("c"))
                )) == [
                    cz(get_q("c"), get_q(0)),
                    cnot(get_q("c"), get_q(1)),
                ]

        If the target is not a tensor product, self is yielded.
        >>> assert list(cnot(get_q(0), get_q(1)).decompose()) == [cnot(get_q(0), get_q(1))]

        :yield: controlled single operator element of controlled tensor product
        """
        if isinstance(self.target_operator, OperatorProduct):
            for operator in sorted(self.target_operator.operators):
                yield ControlledOperator(operator, control_qubits=self.control_qubits)
        else:
            yield self


def cnot(control_qubit: Qubit, target_qubit: Qubit) -> ControlledOperator:
    """Convenience function to generate the controlled NOT (CNOT) or controlled X gate"""
    return ControlledOperator(X(target_qubit), control_qubit)


cx = cnot


def cy(control_qubit: Qubit, target_qubit: Qubit) -> ControlledOperator:
    """Convenience function to generate the controlled Y gate"""
    return ControlledOperator(Y(target_qubit), control_qubit)


def cz(control_qubit: Qubit, target_qubit: Qubit) -> ControlledOperator:
    """Convenience function to generate the controlled Z gate"""
    return ControlledOperator(Z(target_qubit), control_qubit)


def crx(control_qubit: Qubit, target_qubit: Qubit, angle: Weight) -> ControlledOperator:
    """Convenience function to generate the controlled X rotation gate"""
    return ControlledOperator(rx(target_qubit, angle), control_qubit)


def cry(control_qubit: Qubit, target_qubit: Qubit, angle: Weight) -> ControlledOperator:
    """Convenience function to generate the controlled Y rotation gate"""
    return ControlledOperator(ry(target_qubit, angle), control_qubit)


def crz(control_qubit: Qubit, target_qubit: Qubit, angle: Weight) -> ControlledOperator:
    """Convenience function to generate the controlled Z rotation gate"""
    return ControlledOperator(rz(target_qubit, angle), control_qubit)


def ccnot(control_qubits: tuple[Qubit, Qubit], target_qubit: Qubit) -> ControlledOperator:
    """Convenience function to generate the doubly controlled NOT (or X) gate,
    also known as the Toffoli gate.
    """
    return ControlledOperator(X(target_qubit), control_qubits)


def ccy(control_qubits: tuple[Qubit, Qubit], target_qubit: Qubit) -> ControlledOperator:
    """Convenience function to generate the doubly controlled NOT (or X) gate,
    also known as the Toffoli gate.
    """
    return ControlledOperator(Y(target_qubit), control_qubits)


def ccz(control_qubits: tuple[Qubit, Qubit], target_qubit: Qubit) -> ControlledOperator:
    """Convenience function to generate the doubly controlled NOT (or X) gate,
    also known as the Toffoli gate.
    """
    return ControlledOperator(Z(target_qubit), control_qubits)


ccx = ccnot
toffoli = ccnot
