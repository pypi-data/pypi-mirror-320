"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2024.
All rights reserved.

Tools to export ParityOS circuits to OpenQASM.
"""

from __future__ import annotations

import re
from types import MappingProxyType

from attrs import define, field
from typing_extensions import override

from parityos.base import (
    Circuit,
    ControlledOperator,
    OperatorProduct,
    RotationOperator,
)
from parityos.base.bit import Cbit, Qubit
from parityos.base.exceptions import ParityOSNotSupportedError
from parityos.base.operators.conditional_operator import (
    Condition,
    ConditionalOperator,
)
from parityos.base.operators.measure import MX, MZ, Measure
from parityos.base.operators.operator import HasCBits, OperatorLike
from parityos_addons.exporters.exporter import Exporter

OPENQASM_GATES: set[str] = {
    "ccx",
    "ch",
    "cx",
    "crx",
    "cry",
    "crz",
    "cy",
    "cz",
    "h",
    "mx",
    "mz",
    "rx",
    "ry",
    "rz",
    "swap",
    "x",
    "y",
    "z",
}

CONDITION_TO_LOGICAL_OPERATOR = {Condition.AND: "&", Condition.OR: "|", Condition.XOR: "^"}


def _check_openqasm_version(self: OpenQASMExporter, _, openqasm_version: str):
    if not re.match(r"^[23](.\d)?$", openqasm_version):
        raise ParityOSNotSupportedError(
            f"OpenQASM version {openqasm_version} not supported by {type(self).__name__}"
        )


@define
class OpenQASMExporter(Exporter[str, str, str]):
    """
    Tool to convert ParityOS circuits to OpenQASM quantum circuits.
    """

    openqasm_version: str = field(default="3", validator=_check_openqasm_version)
    _qubit_to_id: dict[Qubit, str] = field(factory=dict, init=False)
    _clbit_to_id: dict[Cbit, str] = field(factory=dict, init=False)

    @override
    def export(self, circuit: Circuit) -> str:
        """
        Converts the circuit to a list of OpenQASM statements, including quantum and classical
        register definitions.

        Note that if final measurements are desired, they should be added to the circuit
        by calling circuit.measure_all() before calling this method.

        :param circuit: A ParityOS circuit of quantum gates.

        :returns: A string listing the corresponding OpenQASM statements.
        """
        # Make the statement lines for the gates and measurements
        self.add_bits(circuit)
        statement_lines = [self.export_operator(operator) for operator in circuit]

        # Declare the quantum registers and classical registers.
        qreg_statements = [f"qreg {qreg_name};" for qreg_name in sorted(self._qubit_to_id.values())]
        creg_statements = [f"creg {creg_name};" for creg_name in sorted(self._clbit_to_id.values())]

        return "\n".join(
            [
                "",
                *self._get_openqasm_header_lines(),
                *qreg_statements,
                *creg_statements,
                "",
                *statement_lines,
                "",
            ]
        )

    @property
    @override
    def qubit_map(self) -> MappingProxyType[Qubit, str]:
        """Returns the map of how ParityOS qubits are mapped to OpenQASM qubit strings"""
        return MappingProxyType(self._qubit_to_id)

    @property
    @override
    def cbit_map(self) -> MappingProxyType[Cbit, str]:
        """
        Map of how classical bits are mapped to the exported classical bits, should be updated using
        information from export_circuit calls.
        """
        return MappingProxyType(self._clbit_to_id)

    def export_operator(self, operator: OperatorLike) -> str:
        """
        Converts the operator to an OpenQASM gate, without header lines.

        :param operator: A ParityOS operator.
        :returns: an OpenQASM program in string format.
        """
        self.add_bits(operator)
        if isinstance(operator, ControlledOperator):
            # If the target operator is a product, decompose it so it has a better chance
            # of being exportable in OpenQASM
            if isinstance(operator.target_operator, OperatorProduct):
                return "\n".join(self.export_operator(op) for op in operator.decompose())
            sorted_qubits = sorted(operator.control_qubits) + sorted(operator.target_qubits)
        else:
            sorted_qubits = sorted(operator.qubits)
        mapped_qubits = ", ".join(self._qubit_to_id[qubit] for qubit in sorted_qubits)
        parameters = _get_parameters(operator)

        if isinstance(operator, Measure):
            bit = str(operator.output_bit)
            if isinstance(operator, MX):
                return f"gate h {mapped_qubits}; \nmeasure {mapped_qubits} -> {bit}; \ngate h {mapped_qubits};"
            elif isinstance(operator, MZ):
                return f"measure {mapped_qubits} -> {bit};"
            else:
                raise ParityOSNotSupportedError(f"Unknown measurement type {operator} ")

        if isinstance(operator, ConditionalOperator):
            logical_operator = CONDITION_TO_LOGICAL_OPERATOR.get(operator.condition)
            if logical_operator is None:
                raise ParityOSNotSupportedError(
                    f"condition '{operator.condition.name}' not supported"
                )

            condition = f" {logical_operator} ".join(str(bit) for bit in sorted(operator.cbits))
            return f"if ({condition}) {{{self.export_operator(operator.target_operator)}}}"

        if operator.name not in OPENQASM_GATES:
            raise ParityOSNotSupportedError(
                f"The openqasm translation of the {operator.name} is not available"
            )

        return f"gate {operator.name}{parameters} {mapped_qubits};"

    def add_bits(self, operator: OperatorLike):
        """
        Adds the qubits and the potential classical bits to the mappings, already added bits are
        ignored.
        """
        for qubit in operator.qubits:
            if qubit not in self._qubit_to_id:
                self._qubit_to_id[qubit] = qubit_to_openqasm(qubit)

        if isinstance(operator, HasCBits):
            for bit in operator.cbits:
                if bit not in self._clbit_to_id:
                    self._clbit_to_id[bit] = f"c{bit.label}"

    def _get_openqasm_header_lines(self) -> list[str]:
        """Helper method that generates a list with the header lines of the OpenQASM program."""
        standard_library = "qelib1.inc" if self.openqasm_version < "3" else "stdgates.inc"
        return [
            f"OPENQASM {self.openqasm_version};",
            f'include "{standard_library}";',
            "// Circuit generated by ParityOS.",
            "",
        ]


def qubit_to_openqasm(qubit: Qubit) -> str:
    """
    Convert the ParityOS qubit label into a valid OpenQASM qubit identifier.

    Commas are mapped to underscores, invalid characters are removed, if necessary a `q` is
    prepended.
    """
    identifier = re.sub(",", "_", str(qubit))
    identifier = re.sub(r"[^a-zA-Z_0-9]", "", identifier)
    identifier = re.sub(r"(^[_0-9A-Z])", r"q\g<1>", identifier)
    return identifier


def _get_parameters(operator: OperatorLike) -> str:
    """
    Gets the parameters in OpenQASM format for an operator, there are two cases where the
    operator is parameterized. Either it is a rotation operator, or it is a controlled operator
    where the target operator is a rotation operator. If it is neither, an empty string is returned.
    """
    if isinstance(operator, RotationOperator):
        rotation_operator = operator
    elif isinstance(operator, ControlledOperator) and isinstance(
        operator.target_operator, RotationOperator
    ):
        rotation_operator = operator.target_operator
    else:
        return ""

    if len(rotation_operator.angles) > 1:
        raise ParityOSNotSupportedError("Only rotation operators with a single angle are supported")
    parameters = f"({str(tuple(rotation_operator.angles)[0])})"
    return parameters
