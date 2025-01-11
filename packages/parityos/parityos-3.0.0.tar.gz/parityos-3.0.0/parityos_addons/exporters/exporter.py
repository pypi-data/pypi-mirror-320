from abc import abstractmethod
from types import MappingProxyType
from typing import Generic, TypeVar

from parityos.base import Circuit, Qubit
from parityos.base.bit import Cbit

CircuitT = TypeVar("CircuitT")
QubitT = TypeVar("QubitT")
ClbitT = TypeVar("ClbitT")


class Exporter(Generic[CircuitT, QubitT, ClbitT]):
    @property
    @abstractmethod
    def qubit_map(self) -> MappingProxyType[Qubit, QubitT]:
        """
        Map of how qubits are mapped to the exported qubits, should be updated using
        information from `export` calls.
        """

    @property
    @abstractmethod
    def cbit_map(self) -> MappingProxyType[Cbit, ClbitT]:
        """
        Map of how classical bits are mapped to the exported classical bits, should be updated using
        information from `export` calls.
        """

    @abstractmethod
    def export(self, circuit: Circuit) -> CircuitT:
        """
        Exports a ParityOS circuit to an external circuit type.
        """
