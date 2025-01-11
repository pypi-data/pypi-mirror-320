"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Defines the Qubit classes.
"""

from __future__ import annotations

from typing import TypeVar, overload

from attr import astuple
from attrs import frozen
from typing_extensions import final, override

from parityos.base.io_utils import register_subclasses

BIT_TYPE_TAG = "bit_type"


class Bit:
    """
    Base class for quantum bits and classical bits.
    """

    @classmethod
    def __attrs_init_subclass__(cls) -> None:
        register_subclasses(Bit, BIT_TYPE_TAG)

    @final
    def __lt__(self, other):
        """
        Comparison between any kind of Qubit types, used for sorting. It should not be overwritten.
        """
        if not isinstance(other, Bit):
            return NotImplemented
        elif type(self) is type(other):
            return astuple(self) < astuple(other)
        return type(self).__name__ < type(other).__name__


BitT = TypeVar("BitT", bound=Bit, covariant=True)


@frozen
class Cbit(Bit):
    """
    A classical bit that can be used as output for mid-circuit measurements and classical
    logic within a quantum circuit.
    """

    label: int

    @override
    def __str__(self) -> str:
        return f"c{self.label}"


class Qubit(Bit):
    """
    A base class for a qubit e.g., a physical qubit or a logical qubit.
    It is not intended for direct use, see the concrete types below.
    """

    @override
    def __str__(self) -> str:
        attr_tuple = astuple(self)
        if len(attr_tuple) == 1:
            return f"q({attr_tuple[0]})"
        else:
            return f"q{attr_tuple}"


@frozen
class IntQubit(Qubit):
    label: int


@frozen
class NamedQubit(Qubit):
    label: str


@frozen
class GridQubit2D(Qubit):
    coordinate: tuple[int, int]


@frozen
class GridQubit3D(Qubit):
    coordinate: tuple[int, int, int]


@overload
def get_q(label: int) -> IntQubit: ...
@overload
def get_q(label: str) -> NamedQubit: ...
@overload
def get_q(x: int, y: int) -> GridQubit2D: ...
@overload
def get_q(label: tuple[int, int]) -> GridQubit2D: ...
@overload
def get_q(x: int, y: int, z: int) -> GridQubit3D: ...
@overload
def get_q(label: tuple[int, int, int]) -> GridQubit3D: ...


def get_q(*args):  # pyright: ignore[reportInconsistentOverload]
    """
    Helper function to easily create different kinds of qubits, e.g.:
    >>> get_q(1) == IntQubit(1)
    >>> get_q("A") == NamedQubit("A")
    >>> get_q(0, 1) == GridQubit2D((0, 1))
    >>> get_q((0, 1)) == GridQubit2D((0, 1))
    >>> get_q(0, 1, 2) == GridQubit3D((0, 1, 2))
    >>> get_q((0, 1, 2)) == GridQubit3D((0, 1, 2))
    """
    if len(args) == 1 and isinstance(args[0], tuple):
        args = args[0]
    if len(args) == 1:
        if isinstance(args[0], int):
            return IntQubit(args[0])
        elif isinstance(args[0], str):
            return NamedQubit(args[0])
    elif all(isinstance(arg, int) for arg in args):
        if len(args) == 2:
            return GridQubit2D(args)
        elif len(args) == 3:
            return GridQubit3D(args)

    raise NotImplementedError("Unknown label type")


def get_c(label: int) -> Cbit:
    """Helper function to easily create a classical bit."""
    return Cbit(label)
