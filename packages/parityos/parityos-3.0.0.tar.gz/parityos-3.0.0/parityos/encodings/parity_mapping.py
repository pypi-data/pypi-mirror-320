"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Tools to connect to the ParityOS cloud services and to process the results.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from itertools import chain
from types import MappingProxyType

from attrs import evolve, field, frozen
from typing_extensions import override

from parityos.base import (
    OperatorPolynomial,
    OperatorProduct,
    ProblemRepresentation,
    ProductConstraint,
    Qubit,
    SumConstraint,
    Z,
)
from parityos.base.exceptions import ParityOSException
from parityos.base.state import Parity, PauliBasisState, bit_to_spin_value
from parityos.base.utils import stringify_iterable, to_frozenset_check_unique


class OperatorMap(ABC):
    """
    Represents an operator map that maps to an operator product and has a parity. There
    should also be a 'source' component that indicates the source of the operator map, see
    concrete implementations below.
    """

    target_product: OperatorProduct[Z]
    parity: Parity = field(default=False)

    @property
    @abstractmethod
    def source_product(self) -> OperatorProduct[Z]:
        """
        Returns the source of the operator map as an operator product
        """

    @property
    def target_operators(self) -> frozenset[Z]:
        return self.target_product.operators

    @property
    def target_qubits(self) -> frozenset[Qubit]:
        return self.target_product.qubits

    @property
    def source_operators(self) -> frozenset[Z]:
        return self.source_product.operators

    @property
    def source_qubits(self) -> frozenset[Qubit]:
        return self.source_product.qubits

    @override
    def __str__(self):
        return (
            f"{self.source_product}: {bit_to_spin_value(self.parity)}*{self.target_product}".strip(
                "*"
            )
        )


@frozen(order=True)
class ProductToProduct(OperatorMap):
    """
    Represents a map from an operator product to an operator product.
    """

    source_product: OperatorProduct[Z]  # pyright: ignore[reportIncompatibleMethodOverride]
    target_product: OperatorProduct[Z]
    parity: Parity = field(default=False)


@frozen(order=True)
class OperatorToProduct(OperatorMap):
    """
    Represents a map from a single operator to an operator product.
    """

    source_operator: Z
    target_product: OperatorProduct[Z]
    parity: Parity = field(default=False)

    @cached_property
    def source_product(self) -> OperatorProduct[Z]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return OperatorProduct(self.source_operator)


@frozen
class ParityMapping:
    """
    Holds the Parity Architecture encoding and decoding maps.

    :param encoding_map: the encoding map as a frozenset of pairs, which specifies for each
        physical qubit, which logical qubits it encodes.
    :param decoding_map: A decoding map as a frozenset of pairs, which specifies for each
        logical qubit, which physical qubits multiply to it
    :param constraints: A specific set of constraints that can be implemented on the device
        to implement the specified encoding/decoding maps.
    :param partial_encoding_terms: Optional, in case a partial parity mapping is given,
        there will be higher-order terms in the compiled Hamiltonian. Here these terms
        can be given as an operator-to-operator map.
    """

    encoding_map: frozenset[OperatorToProduct] = field(converter=to_frozenset_check_unique)
    decoding_map: frozenset[OperatorToProduct] = field(converter=to_frozenset_check_unique)
    constraints: frozenset[ProductConstraint] = field(converter=to_frozenset_check_unique)
    partial_encoding_terms: frozenset[ProductToProduct] = field(
        factory=frozenset, converter=to_frozenset_check_unique
    )

    @override
    def __str__(self) -> str:
        separator = "\n    "
        return f"""{self.__class__.__name__}(
  encoding_map={{
    {stringify_iterable(sorted(self.encoding_map), separator=separator)}}}
  decoding_map={{
    {stringify_iterable(sorted(self.decoding_map), separator=separator)}}}
)"""

    @cached_property
    def encoding_product_to_operator_map(self) -> MappingProxyType[OperatorProduct[Z], OperatorMap]:
        return MappingProxyType(
            {
                operator_map.target_product: operator_map
                for operator_map in chain(self.encoding_map, self.partial_encoding_terms)
            }
        )

    @cached_property
    def logical_qubits(self) -> frozenset[Qubit]:
        """
        Return the logical qubits, which are the qubits as specified in the original problem
        """
        return frozenset().union(*[logical_z.source_qubits for logical_z in self.decoding_map])

    @cached_property
    def physical_qubits(self) -> frozenset[Qubit]:
        """
        Return the physical qubits, which are the qubits as specified in the compiled problem
        """
        return frozenset().union(*[physical_z.source_qubits for physical_z in self.encoding_map])

    @cached_property
    def unconstrained_qubits(self) -> frozenset[Qubit]:
        """
        Returns the physical qubits that are not in any constraints
        """
        return self.physical_qubits - set().union(
            *(constraint.qubits for constraint in self.constraints)
        )

    @cached_property
    def logical_degeneracies(self) -> list[OperatorMap]:
        """
        Logical degeneracies are symmetries in the logical Hamiltonian and show up in the decoding
        map as entries where the map does not have any qubits. The logical Hamiltonian is
        equivalent to a Hamiltonian where the logical degeneracies are mapped out using their
        trivial mapping to a parity.
        """
        return [
            operator_map for operator_map in self.decoding_map if not operator_map.target_operators
        ]

    def encode(self, state: PauliBasisState) -> PauliBasisState:
        """
        Converts a given state in the logical system to a state for the physical system

        :param state: A logical state to encode.
        :return: The state on the physical qubits.
        """
        physical_configuration = PauliBasisState(
            frozenset(
                [
                    (
                        next(iter(operator_map.source_qubits)),
                        operator_map.parity ^ state.evaluate_parity(operator_map.target_qubits),
                    )
                    for operator_map in self.encoding_map
                ]
            )
        )
        return physical_configuration

    def get_compiled_problem(self, problem: ProblemRepresentation) -> ProblemRepresentation:
        """
        Converts a logical problem to a compiled problem.
        """
        # Map the logical Hamiltonian to the compiled Hamiltonian
        encoded_interactions = self.encode_polynomial(problem.hamiltonian)

        # Map the sum constraints from the logical problem
        sum_constraints = {
            evolve(
                constraint,
                operator_polynomial=self.encode_polynomial(constraint.operator_polynomial),
            )
            for constraint in problem.constraints
            if isinstance(constraint, SumConstraint)
        }
        compiled_problem = ProblemRepresentation(
            hamiltonian=encoded_interactions,
            constraints=self.constraints | sum_constraints,
        )

        return compiled_problem

    def encode_polynomial(self, polynomial: OperatorPolynomial[Z]) -> OperatorPolynomial[Z]:
        """
        Maps a polynomial in terms of Z operators to a new polynomial in terms of Z operators,
        using the encoding map.
        """
        terms = set()
        for term, weight in polynomial.term_weight_pairs:
            operator_map = self.encoding_product_to_operator_map.get(term)
            if operator_map is None:
                raise ParityOSException("The polynomial could not be encoded")
            terms.add(
                (operator_map.source_product, weight * bit_to_spin_value(operator_map.parity))
            )

        return OperatorPolynomial(frozenset(terms))
