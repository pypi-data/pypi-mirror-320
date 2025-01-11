"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Representations of combinatorial optimization problems as spin models, optionally with constraints.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from functools import cached_property
from operator import itemgetter
from typing import Any, Literal, Optional, Protocol

from attrs import Attribute, evolve, field, frozen
from typing_extensions import Self, override

from parityos.base.bit import Qubit, get_q
from parityos.base.constraint import Constraint
from parityos.base.exceptions import ParityOSException
from parityos.base.operator_polynomial import OperatorPolynomial
from parityos.base.operators.operator import Z
from parityos.base.state import PauliBasisState, bit_to_spin_value
from parityos.base.utils import (
    to_frozenset_check_unique,
)
from parityos.constants import INFINITY


class NetworkxGraphLike(Protocol):
    """
    Emulates parts of the networkx.Graph interface for type checking.
    """

    @property
    def edges(self) -> EdgeViewLike: ...


class EdgeViewLike(Protocol):
    """
    Emulates part of the networkx.EdgeView (return type of networkx.Graph.edges) for type checking.
    """

    # self.data("weight") -> Iterator(label1, label2, weight)
    def data(self, name: Literal["weight"]) -> Iterator[tuple[Any, Any, float]]: ...


def _check_all_z(
    self: ProblemRepresentation,
    _: Attribute[OperatorPolynomial[Z]],
    hamiltonian: OperatorPolynomial[Z],
):
    if not hamiltonian.is_all(Z):
        raise TypeError(f"{type(self).__name__} requires all Z operators")


@frozen
class ProblemRepresentation:
    """
    Representation of an optimization problem as a spin Hamiltonian (diagonal in the Pauli-Z basis)
    together with an optional set of EqualityConstraint objects.

    :param hamiltonian: The logical spin Hamiltonian that represents the optimization problem,
        including the single-body terms.

    :param constraints: Optional. Product or Sum constraints which must be satisfied by the
        solutions of the optimization problem. For the compiled problem, this will contain the
        required parity constraints.

    Examples:
        >>> optimization_problem = ProblemRepresentation(
            hamiltonian=0.5 * Z(get_q((0, 0))) - 0.8 * Z(get_q((0, 1))) + 1.2 * Z(get_q((1, 0)))
            constraints=ProductConstraint(
                Z(get_q((0, 0))) * Z(get_q((0, 1))) * Z(get_q((1, 0))),
                True
            )  # odd parity constraint
        )
    """

    hamiltonian: OperatorPolynomial[Z] = field(validator=_check_all_z)
    constraints: frozenset[Constraint] = field(
        factory=frozenset, converter=to_frozenset_check_unique
    )

    @classmethod
    def from_nx_graph(cls, graph: NetworkxGraphLike) -> Self:
        """
        Construct from a logical problem given in terms of a networkx interaction graph.

        :param graph: A graph representing an optimization problem; nodes are
                      interpreted as binary variables, and edges between them
                      are interpreted as interactions between them (with strength
                      given by the ``weight`` data on each edge).
        :return: the problem representation associated with the given ``graph``
        """
        term_weight_pairs = [
            (Z(get_q(node_a)) * Z(get_q(node_b)), weight)
            for node_a, node_b, weight in graph.edges.data("weight")
        ]

        return cls(OperatorPolynomial(term_weight_pairs))

    @override
    def __str__(self):
        problem_str = f"{type(self).__name__}:\nHamiltonian:\n\t{self.hamiltonian}"
        if self.constraints:
            problem_str += "\nConstraints:\n\t" + "\n\t".join(
                [str(constraint) for constraint in self.constraints]
            )
        return problem_str

    ## OperatorLike Interface ######################################################################

    @cached_property
    def qubits(self) -> frozenset[Qubit]:
        return self.hamiltonian.qubits.union(
            *(constraint.qubits for constraint in self.constraints)
        )

    def get_hermitian_conjugate(self) -> ProblemRepresentation:
        return evolve(
            self,
            hamiltonian=self.hamiltonian.get_hermitian_conjugate(),
        )

    ################################################################################################

    # TODO(VS): the evaluate methods need to be rethought. Do they even belong here?
    def evaluate(
        self,
        state: PauliBasisState,
        constraint_strength: float = INFINITY,
    ) -> float:
        """
        Evaluate the value of the spin Hamiltonian and the constraints on a particular
        state of qubit spin values, where each qubit spin has a value Z = +1 or -1.

        Each qubit in the compiled problem must be in this dictionary. Use the ParityDecoder
        to obtain a full state from a partial state if necessary.

        :param state: a pauli basis state.

        :param constraint_strength: the strength to use for the constraints.
            By default, if no constraint_strength is given, hard constraints are used. In this
            case a float(inf) value is returned if any of the constraints is violated, or the
            unconstrained energy of the spin Hamiltonian otherwise.
            A zero value for this parameter will always result in the unconstrained energy and
            no constraints will be checked.
            A non-zero value will result in soft constraints, with a bonus proportional to the
            constraint strength for each valid constraint and a penalty of equal size for each
            constraint that is violated.
        :return: Value of the given state in this problem representation.
        :rtype: float
        """
        # TODO(VS) now with potential symbolic weights this makes even less sense
        energy_value = sum(
            [
                # even parity = -1, odd parity = +1
                weight * bit_to_spin_value(state.evaluate_parity(term.qubits))
                for term, weight in self.hamiltonian.term_weight_pairs
            ]
        )
        if not isinstance(energy_value, (int, float)):
            raise ParityOSException(
                f"energy is not numeric, convert all weights to numeric types (got {energy_value})"
            )

        num_violoated = sum([not constraint.is_satisfied(state) for constraint in self.constraints])
        if constraint_strength == INFINITY:
            return INFINITY if num_violoated > 0 else energy_value
        else:
            # TODO(VS) what do we want here for SumConstraints?
            return energy_value + constraint_strength * num_violoated

    # TODO(VS) add tests once evaluate is clear
    def evaluate_average_result(
        self,
        measurement_counts: Mapping[str, int],
        qubits: Qubit | Sequence[Qubit] | None = None,
        constraint_strength: float = INFINITY,
    ) -> float:
        """
        :param measurement_counts: A mapping of bit strings to measurement counts
            (number of times bit string was measured out of all the shots that were taken).
        :param qubits: optional argument that provides the Qubit instance for each index in the
            bitstring, by default: [get_q(0), get_q(1), get_q(2)...]
        :param constraint_strength: Optional param for evaluate method, see there for more info
        :return: A weighted average of the number produced by the evaluate method for that
            state, weighted by the proportion of measurement counts found for each bitstring
        """
        if not qubits:
            qubit_count = len(next(iter(measurement_counts)))
            qubits = [get_q(i) for i in range(qubit_count)]

        return sum(
            [
                measurement_count
                * self.evaluate(
                    PauliBasisState.from_bitstring(bitstring, qubits),
                    constraint_strength,
                )
                for bitstring, measurement_count in measurement_counts.items()
            ]
        ) / sum(measurement_counts.values())

    def evaluate_minimal_result(
        self,
        measurement_counts: Mapping[str, int],
        qubits: Optional[Qubit | Sequence[Qubit]] = None,
        constraint_strength: float = INFINITY,
    ) -> tuple[PauliBasisState, float]:
        """
        :param measurement_counts: A mapping of bit strings to measurement counts
            (number of times bit string was measured out of all the shots that were taken).
        :param qubits: optional argument that provides the Qubit instance for each index in the
            bitstring, by default: [get_q(0), get_q(1), get_q(2)...]
        :param constraint_strength: Optional param for evaluate method, see there for more info
        :return: The state produced from the bitstring that has the lowest energy with
            non-zero count, along with the corresponding energy
        """
        if not qubits:
            qubit_count = len(next(iter(measurement_counts)))
            qubits = [get_q(i) for i in range(qubit_count)]

        configs = [
            PauliBasisState.from_bitstring(bitstring, qubits)
            for bitstring, measurement_count in measurement_counts.items()
            if measurement_count > 0
        ]
        min_energy_config, min_energy = min(
            [(config, self.evaluate(config, constraint_strength)) for config in configs],
            key=itemgetter(1),
        )

        return min_energy_config, min_energy
