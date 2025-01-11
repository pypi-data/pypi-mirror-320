from __future__ import annotations

from collections.abc import Iterable
from functools import reduce, singledispatchmethod
from itertools import chain
from operator import itemgetter
from types import MappingProxyType
from typing import Any, Callable, cast

import numpy as np
from attrs import frozen
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit import (
    Clbit,
    ControlledGate,
    Gate,
    IfElseOp,
    Parameter,
    ParameterExpression,
)
from qiskit.circuit import Qubit as QiskitQubit
from qiskit.circuit import library as qiskit_gates
from qiskit.circuit.classical.expr import Expr as ClExpr
from qiskit.circuit.classical.expr import bit_and, bit_or, bit_xor, equal
from qiskit.quantum_info import SparsePauliOp
from symengine import Expr, Symbol
from typing_extensions import override

from parityos.base.bit import BitT, Cbit, Qubit
from parityos.base.circuit import Circuit
from parityos.base.exceptions import ParityOSNotSupportedError
from parityos.base.operator_polynomial import OperatorPolynomial
from parityos.base.operators.conditional_operator import Condition, ConditionalOperator
from parityos.base.operators.controlled_operator import ControlledOperator
from parityos.base.operators.measure import MX, MZ, Measure
from parityos.base.operators.operator import Operator, PauliOperator
from parityos.base.operators.rotation_operator import RotationOperator
from parityos.base.utils import Weight, to_tuple
from parityos_addons.exporters.exporter import Exporter

QUBIT_REGISTER_NAME = "q"
CLBIT_REGISTER_NAME = "c"
SUPPORTED_MEASUREMENTS = (MX, MZ)

# all these gates take no parameters at instantiation
NAME_TO_GATE = {
    "x": qiskit_gates.XGate,
    "y": qiskit_gates.YGate,
    "z": qiskit_gates.ZGate,
    "h": qiskit_gates.HGate,
    "swap": qiskit_gates.SwapGate,
    "iswap": qiskit_gates.iSwapGate,
    "sx": qiskit_gates.SXGate,
}

# all these gates take an angle parameter at instantiation
NAME_TO_PARAMETERIZED_GATE = {
    # rotation gates
    "p": qiskit_gates.PhaseGate,
    "rx": qiskit_gates.RXGate,
    "rxx": qiskit_gates.RXXGate,
    "ry": qiskit_gates.RYGate,
    "ryy": qiskit_gates.RYYGate,
    "rz": qiskit_gates.RZGate,
    "rzz": qiskit_gates.RZZGate,
    "rzx": qiskit_gates.RZXGate,
}

CONDITION_TO_LOGICAL_FUNCTION: dict[Condition, Callable[[Any, Any], ClExpr]] = {
    Condition.XOR: bit_xor,
    Condition.OR: bit_or,
    Condition.AND: bit_and,
}


class QiskitExporter(Exporter[QuantumCircuit, int, int]):
    _qubit_to_id: dict[Qubit, int]
    _cbit_to_id: dict[Cbit, int]
    _name_to_parameter: dict[str, Parameter]

    def __init__(
        self,
        qubits: Iterable[Qubit] | None = None,
        cbits: Iterable[Cbit] | None = None,
    ):
        self._qubit_to_id = {qubit: id_ for id_, qubit in enumerate(qubits or [])}
        self._cbit_to_id = {qubit: id_ for id_, qubit in enumerate(cbits or [])}
        self._name_to_parameter = {}

    @property
    @override
    def qubit_map(self) -> MappingProxyType[Qubit, int]:
        """
        Mapping of ParityOS Qubit to Qiskit Qubit id label.

        Values are integers, as Qiskit uses only integers to label qubits.
        """
        return MappingProxyType(self._qubit_to_id)

    @property
    @override
    def cbit_map(self) -> MappingProxyType[Cbit, int]:
        """
        Mapping of ParityOS Cbit to Qiskit Clbit id label.

        Values are integers, as Qiskit uses only integers to label classical bits.
        """
        return MappingProxyType(self._cbit_to_id)

    @property
    def name_to_parameter(self) -> MappingProxyType[str, Parameter]:
        """Mapping of named parameters that have been encountered with the exporter so far."""
        return MappingProxyType(self._name_to_parameter)

    @override
    def export(self, circuit: Circuit) -> QuantumCircuit:
        """Export ParityOS Circuit to a Qiskit QuantumCircuit.

        This is the main method and entry point of the exporter and should preferrably be used for
        any kind of exporting.

        :param circuit: ParityOS Circuit to be exported to Qiskit
        :return: Translated Qiskit QuantumCircuit
        """
        self.add_qubits(circuit.qubits)
        self.add_cbits(circuit.cbits)

        qiskit_circuit = QuantumCircuit(
            QuantumRegister(len(self._qubit_to_id), QUBIT_REGISTER_NAME),
            ClassicalRegister(len(self._cbit_to_id), CLBIT_REGISTER_NAME),
        )
        for operator in circuit.operators:
            self._add_operator_to_qiskit_circuit(operator, qiskit_circuit)
        return qiskit_circuit

    def add_qubits(self, qubits: Qubit | Iterable[Qubit]):
        _add_bits_to_mapping(qubits, self._qubit_to_id)

    def add_cbits(self, cbits: Cbit | Iterable[Cbit]):
        _add_bits_to_mapping(cbits, self._cbit_to_id)

    @singledispatchmethod
    def _add_operator_to_qiskit_circuit(
        self, operator: Operator, qiskit_circuit: QuantumCircuit
    ) -> None:
        """Translate `operator` to a qiskit operation and add it to `qiskit_circuit`

        This method is private as it does *not* update the qubit and cbit mappings.

        :param operator: operator to be mapped onto a qiskit gate operation
        :param qiskit_circuit: qiskit circuit to which the operation is added
        :raises ParityOSException: if operator is not representable as qiskit gate operation
        """
        gate = self.get_gate(operator)
        qiskit_circuit.append(
            gate, qargs=[self._qubit_to_id[qubit] for qubit in sorted(operator.qubits)]
        )

    @_add_operator_to_qiskit_circuit.register(ControlledOperator)
    def _add_controlled_operator_to_qiskit_circuit(
        self, operator: ControlledOperator, qiskit_circuit: QuantumCircuit
    ) -> None:
        for operator in operator.decompose():
            gate = self.get_gate(operator.target_operator)
            qiskit_circuit.append(
                # turns any gate into a controlled gate with a certain number of control qubits
                gate.control(len(operator.control_qubits)),
                qargs=[
                    self._qubit_to_id[qubit]
                    for qubit in chain(
                        # control qubits must come before target qubits, hence separate sorting
                        sorted(operator.control_qubits),
                        sorted(operator.target_qubits),
                    )
                ],
            )

    @_add_operator_to_qiskit_circuit.register(Measure)
    def _add_measurement_to_qiskit_circuit(self, operator: Measure, qiskit_circuit: QuantumCircuit):
        if not isinstance(operator, SUPPORTED_MEASUREMENTS):
            raise ParityOSNotSupportedError(
                f"only {SUPPORTED_MEASUREMENTS} measurements supported."
            )
        qubit_id = self._qubit_to_id[next(iter(operator.qubits))]
        clbit_id = self._cbit_to_id[operator.output_bit]

        # to measure in the x-basis, surround z-basis measurement with hadamard gates,
        # as qiskit only supports measuring in the z-basis
        transform_basis = isinstance(operator, MX)
        if transform_basis:
            qiskit_circuit.h(qubit_id)
        qiskit_circuit.measure(qubit_id, clbit_id)  # measures only in z-basis
        if transform_basis:
            qiskit_circuit.h(qubit_id)

    @_add_operator_to_qiskit_circuit.register(ConditionalOperator)
    def _add_conditional_operator_to_qiskit_circuit(
        self, operator: ConditionalOperator, qiskit_circuit: QuantumCircuit
    ):
        condition_fn = CONDITION_TO_LOGICAL_FUNCTION.get(operator.condition)
        if condition_fn is None:
            raise ParityOSNotSupportedError(f"condition '{operator.condition.name}' not supported")
        gate = self.get_gate(operator.target_operator)

        clbits = self._get_clbits_from_qiskit_circuit(operator.cbits, qiskit_circuit)
        qubits = self._get_qubits_from_qiskit_circuit(operator.qubits, qiskit_circuit)

        true_body_register = QuantumRegister(bits=qubits)
        true_body = QuantumCircuit(true_body_register)
        true_body.append(gate, qargs=qubits)

        condition = equal(reduce(condition_fn, clbits), True)

        qiskit_circuit.append(IfElseOp(condition, true_body), qargs=qubits)

    def _get_qubits_from_qiskit_circuit(
        self, qubits: Qubit | Iterable[Qubit], qiskit_circuit: QuantumCircuit
    ) -> list[QiskitQubit]:
        qubit_ids = [self._qubit_to_id[qubit] for qubit in sorted(to_tuple(qubits))]
        return [qiskit_circuit.qubits[id_] for id_ in qubit_ids]

    def _get_clbits_from_qiskit_circuit(
        self, cbits: Cbit | Iterable[Cbit], qiskit_circuit: QuantumCircuit
    ) -> list[Clbit]:
        clbit_ids = [self._cbit_to_id[qubit] for qubit in sorted(to_tuple(cbits))]
        return [qiskit_circuit.clbits[id_] for id_ in clbit_ids]

    @singledispatchmethod
    def get_gate(self, operator: Operator) -> Gate:
        gate_type = NAME_TO_GATE.get(operator.name)
        if gate_type is None:
            raise ParityOSNotSupportedError(f"export of {operator} not supported")
        return gate_type()

    @get_gate.register(ControlledOperator)
    def get_controlled_gate(self, operator: ControlledOperator) -> Gate:
        gate = self.get_gate(operator.target_operator)
        return cast(ControlledGate, gate.control(len(operator.control_qubits)))

    @get_gate.register(RotationOperator)
    def get_rotation_gate(self, operator: RotationOperator) -> Gate:
        gate_type = NAME_TO_PARAMETERIZED_GATE.get(operator.name)
        self.add_parameters(operator.parameters)

        if gate_type is not None:
            # operator is guaranteed to have a single angle at this point, but check anyway
            theta = self._convert_angle(operator)
            return gate_type(theta)

        if operator.exponent.is_all(PauliOperator):
            # TODO(VS): adapt to restrict to a single expression that can be pulled out
            # requires symbolic polynomial division for gcd, which symengine doesn't implement
            # this (issue #75)
            if len(operator.parameters) > 1:
                raise ParityOSNotSupportedError(
                    "export of operators with more than 1 parameter not supported."
                )
            parameter = next(iter(operator.parameters), None)
            angle = 1
            exponent = cast(OperatorPolynomial[PauliOperator], operator.exponent)
            if parameter is not None:
                angle = self._name_to_parameter[parameter.name]
                exponent = exponent / parameter
                if len(exponent.parameters):
                    raise ParityOSNotSupportedError(
                        "export of operators with a parameter that appears in different powers not supported."
                    )
            exponent = operator_polynomial_to_sparse_pauli(exponent)
            return qiskit_gates.PauliEvolutionGate(exponent, angle / 2)

        raise ParityOSNotSupportedError(f"export of {operator} not supported")

    def add_parameters(self, symbols: Symbol | Iterable[Symbol]):
        symbols = [symbols] if isinstance(symbols, Symbol) else symbols
        to_add = {symbol.name for symbol in symbols} - self._name_to_parameter.keys()
        self._name_to_parameter.update({name: Parameter(name) for name in to_add})

    def _convert_angle(self, operator: RotationOperator) -> ParameterExpression | float:
        """convert angle to a qiskit symbolic expression if appliccable.

        Only implemented for a single angle.

        :param operator: rotation operator with a single angle
        :raises ParityOSException: if operator has more than one angle
        :return: angle converted to ParameterExpression if it contains Symbols
        """
        # TODO(VS): this function should become obsolete with the implementation of issue #75
        # s.t. only the pulled out global angle needs to be converted.
        if len(operator.angles) != 1:
            raise ParityOSNotSupportedError(
                f"operator '{operator.name}' must have one angle, but has {len(operator.angles)}."
            )
        angle = next(iter(operator.angles))
        if isinstance(angle, Expr):
            symbols = angle.free_symbols
            return ParameterExpression(
                {self._name_to_parameter[symbol.name]: symbol for symbol in symbols}, angle
            )
        else:
            return angle


def _add_bits_to_mapping(bits: BitT | Iterable[BitT], bit_to_id: dict[BitT, int]) -> None:
    for bit in sorted(bits) if isinstance(bits, Iterable) else [bits]:
        if bit not in bit_to_id:
            bit_to_id[bit] = len(bit_to_id)


# TODO(VS): this should be replaced by a proper identity operator (issue #57)
@frozen
class Identity:
    @property
    def name(self) -> str:
        return "I"


ID = Identity()


def operator_polynomial_to_sparse_pauli(
    polynomial: OperatorPolynomial[PauliOperator],
) -> SparsePauliOp:
    pauli_strings: list[str]
    weights: list[Weight]

    pauli_strings, weights = zip(
        *[
            (
                "".join(
                    [
                        term.qubit_to_operator.get(qubit, ID).name.upper()
                        for qubit in sorted(polynomial.qubits)
                    ]
                ),
                weight,
            )
            for term, weight in sorted(polynomial.term_weight_pairs, key=itemgetter(0))
        ],
    )
    return SparsePauliOp(pauli_strings, np.asarray(weights))
