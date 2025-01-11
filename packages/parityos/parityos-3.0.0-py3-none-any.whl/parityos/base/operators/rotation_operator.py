"""
ParityQC GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Defines rotation operators that represent exponentials of hermitian operators.
"""

from __future__ import annotations

from attrs import Attribute, evolve, field, frozen
from symengine import Symbol
from typing_extensions import Self, override

from parityos.base.bit import Qubit
from parityos.base.operator_polynomial import OperatorPolynomial
from parityos.base.operator_product import OperatorProduct
from parityos.base.operators.operator import HermitianOperator, Operator, Parameterized, X, Y, Z
from parityos.base.utils import Weight


def _check_hermitian(
    self: RotationOperator,
    _: Attribute[OperatorPolynomial[HermitianOperator]],
    operator: OperatorPolynomial[HermitianOperator],
):
    """Check whether `operator` is hermitian."""
    if not operator.is_hermitian:
        raise TypeError(f"{type(self).__name__} requires all hermitian operators, got {operator}")


def _to_operator_polynomial(
    operator: HermitianOperator
    | OperatorProduct[HermitianOperator]
    | OperatorPolynomial[HermitianOperator],
) -> OperatorPolynomial[HermitianOperator]:
    """Convert input operator to OperatorPolynomial.

    OperatorProduct and HermitianOperator are both wrapped into a single term OperatorPolynomial.

    :param operator: a Hermitian operator or a tensor product of Hermitian operators
    :raises TypeError: if the input operator is not hermitian
    :return: resulting (possibly single term) operator product
    """
    return operator if isinstance(operator, OperatorPolynomial) else 1 * operator


@frozen(order=False)
class RotationOperator(Operator, Parameterized):
    r"""
    Represents the rotation operator

    .. math::

      R(A) = \exp\left(- i \frac{A}{2}\right)

    where `A` = `operator` is a hermitian `OperatorPolynomial`.

    The weight(s) of the term(s) in `operator` represent the rotation angle(s).

    :param operator: the hermitian operator in the exponent
    :raises TypeError: if `operator` is not hermitian
    """

    exponent: OperatorPolynomial[HermitianOperator] = field(
        validator=_check_hermitian, converter=_to_operator_polynomial
    )

    @override
    def __str__(self) -> str:
        return f"R({self.exponent})"

    @property
    def angles(self) -> frozenset[Weight]:
        return self.exponent.weights

    ## OperatorLike Interface ######################################################################

    @property
    @override
    def name(self) -> str:
        return f"r{self.exponent.name}"

    @property
    @override
    def qubits(self) -> frozenset[Qubit]:
        return self.exponent.qubits

    @override
    def get_hermitian_conjugate(self) -> Self:
        return evolve(self, exponent=-self.exponent)

    # TODO(VS): Think about an explicit Hermitian version whose angle are integer multiples of \pi
    @property
    @override
    def is_hermitian(self) -> bool:
        return False

    @property
    @override
    def parameters(self) -> frozenset[Symbol]:
        return self.exponent.parameters


def rx(qubit: Qubit, angle: Weight) -> RotationOperator:
    r"""
    Convenience function to generate a rotation by :math:`\phi` = `angle` around the X axis

    .. math::

      RX(\phi) = \exp\left(- \frac{\phi}{2} X\right)
    """
    return RotationOperator(angle * X(qubit))


def ry(qubit: Qubit, angle: Weight) -> RotationOperator:
    r"""
    Convenience function to generate a rotation by :math:`\phi` = `angle` around the Y axis

    .. math::

      RY(\phi) = \exp\left(- \frac{\phi}{2} Y\right)
    """
    return RotationOperator(angle * Y(qubit))


def rz(qubit: Qubit, angle: Weight) -> RotationOperator:
    r"""
    Convenience function to generate a rotation by :math:`\phi` = `angle` around the Z axis

    .. math::

      RZ(\phi) = \exp\left(- \frac{\phi}{2} Z\right)
    """
    return RotationOperator(angle * Z(qubit))


def rxx(qubit_1: Qubit, qubit_2: Qubit, angle: Weight) -> RotationOperator:
    r"""
    Convenience function to generate a joint two-qubit rotation by :math:`\phi` = `angle`
    around the X axis

    .. math::

      RXX(\phi) = \exp\left(- \frac{\phi}{2} X \otimes X\right)
    """
    return RotationOperator(angle * X(qubit_1) * X(qubit_2))


def ryy(qubit_1: Qubit, qubit_2: Qubit, angle: Weight) -> RotationOperator:
    r"""
    Convenience function to generate a joint two-qubit rotation by :math:`\phi` = `angle`
    around the Y axis

    .. math::

      RYY(\phi) = \exp\left(- \frac{\phi}{2} Y \otimes Y\right)
    """
    return RotationOperator(angle * Y(qubit_1) * Y(qubit_2))


def rzz(qubit_1: Qubit, qubit_2: Qubit, angle: Weight) -> RotationOperator:
    r"""
    Convenience function to generate a joint two-qubit rotation by :math:`\phi` = `angle`
    around the Z axis

    .. math::

      RZZ(\phi) = \exp\left(- \frac{\phi}{2} Z \otimes Z\right)
    """
    return RotationOperator(angle * Z(qubit_1) * Z(qubit_2))
