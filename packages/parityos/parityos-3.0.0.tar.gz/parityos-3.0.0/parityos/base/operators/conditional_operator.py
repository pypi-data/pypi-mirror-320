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

from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

from attrs import Attribute, evolve, field, frozen
from symengine import Symbol
from typing_extensions import Self, override

from parityos.base.bit import Cbit, Qubit
from parityos.base.exceptions import ParityOSException
from parityos.base.operator_product import OperatorProduct
from parityos.base.operators.controlled_operator import ControlledOperator
from parityos.base.operators.operator import (
    ElementaryOperator,
    HasCBits,
    Operator,
    Parameterized,
)
from parityos.base.operators.rotation_operator import RotationOperator
from parityos.base.utils import stringify_iterable, to_frozenset_check_unique


def _check_non_empty(
    self: ConditionalOperator,
    attrib: Attribute[frozenset[Cbit]],
    value: frozenset[Cbit],
):
    if len(value) == 0:
        raise ParityOSException(
            f"attribute {attrib.name} of {type(self).__name__} must not be empty."
        )


class Condition(Enum):
    OR = "OR"
    AND = "AND"
    XOR = "XOR"


@frozen
class ConditionalOperator(Operator, HasCBits, Parameterized, ABC):
    """
    Represents a conditional operator, where the application of the operator depends on a condition
    in form of a classical boolean function. The target operator is triggered when the condition
    evaluates to true. This condition must be specified in implementing subclasses.

    :param target_operator: operator acting on target qubits depending on the state of the control bits
    :param cbits: classical bit labels that go into the condition
    """

    target_operator: Union[
        ElementaryOperator, RotationOperator, ControlledOperator, OperatorProduct[Operator]
    ]
    cbits: frozenset[Cbit] = field(
        validator=_check_non_empty,
        converter=to_frozenset_check_unique,
    )

    @override
    def __str__(self) -> str:
        return f"{type(self).__name__}({stringify_iterable(sorted(self.cbits))}, {self.target_operator})"

    @property
    @abstractmethod
    def condition(self) -> Condition:
        """condition that will be applied to all classical_bits."""

    ## OperatorLike Interface ######################################################################

    @property
    @override
    def name(self) -> str:
        return f"{type(self).__name__.lower()},{self.target_operator.name}"

    @property
    @override
    def qubits(self) -> frozenset[Qubit]:
        """Combined set of control and target qubits"""
        return self.target_operator.qubits

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


class ConditionalOperatorXOR(ConditionalOperator):
    """A conditional operator where the condition is an XOR between all classical bits."""

    @property
    @override
    def name(self) -> str:
        return f"xor({self.target_operator.name})"

    @property
    @override
    def condition(self) -> Condition:
        return Condition.XOR


class ConditionalOperatorAND(ConditionalOperator):
    """A conditional operator where the condition is an AND between all classical bits."""

    @property
    @override
    def name(self) -> str:
        return f"and({self.target_operator.name})"

    @property
    @override
    def condition(self) -> Condition:
        return Condition.AND


class ConditionalOperatorOR(ConditionalOperator):
    """A conditional operator where the condition is an OR between all classical bits."""

    @property
    @override
    def name(self) -> str:
        return f"or({self.target_operator.name})"

    @property
    @override
    def condition(self) -> Condition:
        return Condition.OR
