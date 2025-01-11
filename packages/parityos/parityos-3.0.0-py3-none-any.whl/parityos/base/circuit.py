"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Classes that store information on sequences of quantum gates
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import count
from typing import Any, overload

from attrs import define, evolve, field
from symengine import Symbol
from typing_extensions import Self, override

from parityos.base.bit import Cbit, Qubit
from parityos.base.operators.measure import MZ
from parityos.base.operators.operator import HasCBits, Operator, OperatorLike, Parameterized
from parityos.base.utils import to_list


@define(order=False)
class Circuit(OperatorLike, Parameterized, HasCBits, Sequence[Operator]):
    """Represents a quantum circuit as an ordered sequence of operators.

    This class does apply any operator ordering. Equivalent circuits where successive
    operators that act on disjoint qubit sets are swapped, are not considered equal.

    Example:
    >>> c1 = Circuit([X(get_q(1)), X(get_q(0)), cnot(get_q(0), get_q(1))])
    >>> c2 = Circuit([X(get_q(0)), X(get_q(1)), cnot(get_q(0), get_q(1))])
    >>> assert not c1 == c2

    :param operators: ordered sequence of successive operators which make up the circuit.

    TODO: previously Circuit had extra methods: remap and modify_angle, these are used in QAOA
        and ParityOSOutput.encode_problem respectively (ParityOSOutput will be refactored as well
        and remap most likely removed from there as well). It is not clear whether these methods
        should be implemented at a circuit/gate level, so they are removed for now.
        They will probably be added to a suitable addon.

    """

    operators: list[Operator] = field(factory=list, converter=to_list)

    @override
    def __str__(self) -> str:
        return "->".join([str(operator) for operator in self.operators])

    @property
    @override
    def name(self) -> str:
        return "->".join(operator.name for operator in self.operators)

    @override
    def __len__(self) -> int:
        """Number of operators in this circuit."""
        return len(self.operators)

    ## OperatorLike Interface ######################################################################
    @property
    @override
    def qubits(self) -> frozenset[Qubit]:
        """The set of all qubits this circuit acts on."""
        return frozenset().union(*[operator.qubits for operator in self.operators])

    @property
    @override
    def cbits(self) -> frozenset[Cbit]:
        return frozenset().union(
            *[operator.cbits for operator in self.operators if isinstance(operator, HasCBits)]
        )

    @override
    def get_hermitian_conjugate(self) -> Self:
        return evolve(
            self,
            operators=[operator.get_hermitian_conjugate() for operator in reversed(self.operators)],
        )

    @property
    @override
    def is_hermitian(self) -> bool:
        return all([operator.is_hermitian for operator in self.operators])

    #################################################################################################
    @property
    @override
    def parameters(self) -> frozenset[Symbol]:
        """The set of all symbolic parameters in this circuit."""
        symbols = [
            operator.parameters
            for operator in self.operators
            if isinstance(operator, Parameterized)
        ]
        return frozenset().union(*symbols)

    @overload
    def __getitem__(self, index: int) -> Operator: ...
    @overload
    def __getitem__(self, index: slice) -> list[Operator]: ...
    @override
    def __getitem__(self, index: int | slice):
        """Return a single or a range of operators.

        Operators are indexed by their order in the circuit.
        """
        return self.operators[index]

    @overload
    def __setitem__(self, index: int, item: Operator) -> None: ...
    @overload
    def __setitem__(self, index: slice, item: Sequence[Operator]) -> None: ...
    def __setitem__(self, index: Any, item: Any) -> None:
        """Set a single or a range of operators.

        Operators are indexed by their order in the circuit.
        """
        self.operators[index] = item

    def __add__(self, other: Sequence[Operator]) -> Self:
        """Concatenate this circuit with another circuit or a sequence of operators."""
        if not isinstance(other, Sequence):
            return NotImplemented
        other = other.operators if isinstance(other, Circuit) else list(other)
        return evolve(self, operators=self.operators + list(other))

    def __mul__(self, amount: int) -> Self:
        """Create a new circuit by concatenating this circuit `amount` number of times."""
        if isinstance(amount, int):
            return evolve(self, operators=amount * self.operators)
        return NotImplemented

    def append(self, operator: Operator) -> Self:
        """Append an operator to the end of the circuit."""
        self.operators.append(operator)
        return self

    def insert(self, index: int, operator: Operator) -> Self:
        """Insert an operator into the circuit between operator[index-1] and operator[index]."""
        self.operators.insert(index, operator)
        return self

    def measure_all(self) -> Self:
        """Add measurement operations for all qubits in the circuit.

        A new classical bit is created and added to the circuit for each qubit in the circuit

        :return: self
        """
        existing_classical_bit_labels = {clbit.label for clbit in self.cbits}
        output_bit_iter = iter(
            Cbit(label) for label in count() if label not in existing_classical_bit_labels
        )
        for qubit in sorted(self.qubits):
            output_bit = next(output_bit_iter)
            self.append(MZ(qubit, output_bit))
        return self

    __rmul__ = __mul__  # pyright: ignore[reportUnannotatedClassAttribute]
    __radd__ = __add__  # pyright: ignore[reportUnannotatedClassAttribute]
