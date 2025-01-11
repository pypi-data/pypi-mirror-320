from abc import ABC, abstractmethod
from typing import ClassVar

from attrs import frozen
from typing_extensions import override

from parityos.base.bit import Cbit
from parityos.base.operators.operator import ElementaryOperator, HasCBits
from parityos.base.state import PauliBasis


@frozen
class Measure(ElementaryOperator, HasCBits, ABC):
    """
    A measurement operator for which the output will be read into a classical bit.
    """

    N_QUBITS: ClassVar[int] = 1

    output_bit: Cbit

    @property
    @abstractmethod
    def pauli_basis(self) -> PauliBasis: ...

    @override
    def get_hermitian_conjugate(self):
        raise NotImplementedError("Hermitian conjugate of a measurement is not implemented.")

    @property
    @override
    def cbits(self) -> frozenset[Cbit]:
        return frozenset({self.output_bit})


@frozen
class MZ(Measure):
    """A measurement in the Z basis"""

    @property
    @override
    def pauli_basis(self) -> PauliBasis:
        return PauliBasis.Z


@frozen
class MX(Measure):
    """A measurement in the X basis"""

    @property
    @override
    def pauli_basis(self) -> PauliBasis:
        return PauliBasis.X
