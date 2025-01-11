"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Extensions to process the results from the ParityOS cloud services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from itertools import combinations
from random import Random

from attrs import frozen
from typing_extensions import override

from parityos.base.bit import Qubit
from parityos.base.exceptions import ParityOSException
from parityos.base.state import PauliBasisState
from parityos.encodings.parity_mapping import ParityMapping


class StateDecoder(ABC):
    """
    A base class that can be used to decode states in a code-space to the original variables
    """

    @abstractmethod
    def decode(self, state: PauliBasisState) -> frozenset[PauliBasisState]:
        """
        Decodes a physical state to a frozenset of equally likely logical states.
        """


@frozen
class ParityStateDecoder(StateDecoder):
    """
    A Parity decoder with methods `decode`, `closest_valid_physical_states`,
    `select_reduced_readout_qubits` and `make_full_state_from_partial`.
    These methods can decode physical states into logical states.

    It is possible to use a partial read-out to construct a full physical state,
    based on the redundant encoding that the parity architecture offers. This is especially
    useful if only a limited number of qubits can be read out in the hardware setup, or if
    the read-out failed on some qubits.
    """

    parity_mapping: ParityMapping

    @override
    def decode(self, state: PauliBasisState) -> frozenset[PauliBasisState]:
        """
        Decodes a physical state back to a logical one, it is important that the
        state contains enough qubits to reconstruct the logical state. If not
        enough qubits are included, a ParityOSException will be raised.

        :param state: A physical state to decode

        :return: A frozenset containing all equally-likely logical states that correspond to
                 the physical state.
        """
        # If not all physical qubits are specified in the state, we deduce the value
        # of those qubits from the constraints.
        if frozenset(state.qubits) != self.parity_mapping.physical_qubits:
            state = self.make_full_state_from_partial(state)

        # Now error correct the resulting state onto the physical code subspace.
        corrected_states = self.closest_valid_physical_states(state)

        logical_states = {
            PauliBasisState(
                frozenset(
                    {
                        (
                            tuple(operator_map.source_qubits)[0],
                            operator_map.parity
                            ^ corrected_state.evaluate_parity(operator_map.target_qubits),
                        )
                        for operator_map in self.parity_mapping.decoding_map
                    }
                )
            )
            for corrected_state in corrected_states
        }
        return frozenset(logical_states)

    def closest_valid_physical_states(self, state: PauliBasisState) -> frozenset[PauliBasisState]:
        """
        Constructs the most likely physical state that correspond to a physical
        state which does not necessarily satisfies the constraints, using the nearest
        neighbor algorithm.

        :param state: a physical state to correct for errors

        :return: A frozenset of possible physical states that satisfy all constraints
                 (and hence are part of the physical code subspace), which each were obtained
                 at the smallest possible Hamming distance from the original state.
        """
        # If we already have a valid codeword, we are done
        if self.check_parity(state):
            return frozenset({state})

        # Search the bitstring space by flipping k bits at a time, increasing k every step,
        # until we find a valid codeword.  We want to keep track of all valid codewords found
        # at the shortest distance k, since they are all equally likely.
        qubit_to_value = dict(state.qubit_value_pairs)
        for k in range(1, len(self.parity_mapping.physical_qubits)):
            # Prepare a list to accumulate valid codewords
            valid_states = set()
            # Look at every possible combination of k flipped bits
            for qubits_to_flip in combinations(self.parity_mapping.physical_qubits, k):
                flipped_configuration = qubit_to_value.copy()
                for qubit in qubits_to_flip:
                    flipped_configuration[qubit] ^= True

                flipped_state = PauliBasisState(flipped_configuration)

                if self.check_parity(flipped_state):
                    valid_states.add(flipped_state)

            # If any valid codewords were found, we can return them
            if valid_states:
                return frozenset(valid_states)

        raise ParityOSException("There are no valid codewords in the entire physical code space")

    def select_reduced_readout_qubits(
        self, random_generator: Random | None = None
    ) -> frozenset[Qubit]:
        """
        Constructs a random minimal set of qubits that can be read-out and still be used
        to recover the full logical states.

        Note that when these qubits are used for read-out, no error correction can be applied.

        :param random_generator: Optional. A random number generator that has a ```choice```
                                 and ```sample``` method. If None is given, then the default random
                                 number generator from the `random` standard library is used.

        :return: A random set of qubits that are selected for read-out.
        """
        # If there are no constraints in the compiled problem, we have to read out every qubit
        if not self.parity_mapping.constraints:
            return self.parity_mapping.physical_qubits

        if random_generator is None:
            random_generator = Random()

        # Start with only the unconstrained qubits, because those will all have to be read-out.
        # The qubits that are in constraints will be added in consecutive steps.
        readout_qubits = set(self.parity_mapping.unconstrained_qubits)
        # Make a configuration that has all the qubits that are known in it, the state of the
        # qubits does not matter
        configuration = dict.fromkeys(readout_qubits, False)

        while len(configuration) != len(self.parity_mapping.encoding_map):
            # Find the next qubits to add to the read-out set based on the constraint
            # that has the minimum number of remaining unknowns
            qubits_to_add = self._find_next_readout_qubits(configuration, random_generator)
            readout_qubits.update(qubits_to_add)
            configuration.update(dict.fromkeys(qubits_to_add, False))
            state = self.make_full_state_from_partial(
                PauliBasisState(configuration),
                return_incomplete=True,
            )
            configuration = dict(state.qubit_value_pairs)

        return frozenset(readout_qubits)

    def make_full_state_from_partial(
        self, state: PauliBasisState, return_incomplete: bool = False
    ) -> PauliBasisState:
        """
        Reconstructs a full physical state from a partial one
        using the constraints in the compiled problem.

        :param state: A partial physical state to extend.
        :param return_incomplete: If this flag is set to True, we return a physical
                                  state even if the full state could not
                                  be reconstructed. The state returned in that case
                                  contains all the qubits that could be deduced.
        :return: Full physical state deduced from the parity constraints.
        """
        # This dictionary will be used to add all reconstructed values of the qubits, we start
        # from the given state.
        deduced_configuration = dict(state.qubit_value_pairs)

        # Make a list of the unknown qubits in all constraints, the goal is to remove all unknowns
        # from the constraints until we are finished, or can not make any more progress.
        known_qubits = set(deduced_configuration)
        unknown_constraints = {
            (
                constraint.qubits - known_qubits,
                constraint.parity ^ state.evaluate_parity(constraint.qubits & known_qubits),
            )
            for constraint in self.parity_mapping.constraints
        }

        while unknown_constraints:
            new_unknown_constraints = set()
            for constraint_unknown_qubits, parity in unknown_constraints:
                deduced_qubits = set(deduced_configuration)
                new_constraint_qubits = constraint_unknown_qubits - deduced_qubits
                if not new_constraint_qubits:
                    # If there are no unknowns left in the constraint, we simply do nothing.
                    # Note that if the remaining parity is -1, the read-out contains an error,
                    # but the purpose of this function is not to do error correction (that
                    # will be done later).
                    continue

                # If the qubit is already in the deduced configuration, we do not
                # have to keep track of it anymore, we can multiply its state
                # with the constraint parity and not add it to the new unknowns.
                new_parity = parity ^ PauliBasisState(deduced_configuration).evaluate_parity(
                    constraint_unknown_qubits & deduced_qubits
                )
                if len(new_constraint_qubits) == 1:
                    # If there is exactly one qubit left in the unknowns of this constraint,
                    # we now know its value to be equal to remaining parity, so we can add it
                    # to the deduced configuration.
                    [qubit] = new_constraint_qubits
                    deduced_configuration[qubit] = new_parity
                else:
                    # If there are still more than two unknown qubits in the constraint,
                    # we have to put it back into the unknown constraints.
                    new_unknown_constraints.add((new_constraint_qubits, new_parity))

            if new_unknown_constraints == unknown_constraints:
                # We cannot make any further progress, after checking all constraints,
                # so reconstruction failed.
                if return_incomplete:
                    return PauliBasisState(deduced_configuration)
                else:
                    raise ParityOSException("Decoding failed for the given read-out set")
            else:
                # If we made some progress, continue the algorithm
                unknown_constraints = new_unknown_constraints

        return PauliBasisState(deduced_configuration)

    def check_parity(self, state: PauliBasisState) -> bool:
        """
        Checks whether a state satisfies all the constraints

        :param state: A physical state to check.

        :return: True if it satisfies all constraints, False otherwise.
        """
        return all(constraint.is_satisfied(state) for constraint in self.parity_mapping.constraints)

    def _find_next_readout_qubits(
        self, known_qubits: Iterable[Qubit], random_generator: Random
    ) -> frozenset[Qubit]:
        """
        Helper method for select_random_reduced_readout_qubits. Selects a set of qubits
        that should be added to the read-out set. Go over all constraints in the compiled
        problem and select one of the constraint with the fewest number of unknowns. Then returns
        all but one of the qubits in that constraint.

        :param known_qubits: All read-out qubits as well as all qubit  values that can be deduced
            from the read-out qubits.
        :param random_generator: Optional. A random number generator that has a ```choice```
                                 and ```sample``` method.
        :return: A set of qubits that should be added to the read-out set.
        """
        min_number_unknowns = float("inf")
        minimum_unknowns = []
        # Go over all the constraints in the compiled problem and find those with the minimum
        # number of unknown qubits.
        for constraint in self.parity_mapping.constraints:
            unknown_qubits = constraint.qubits.difference(known_qubits)
            if unknown_qubits:
                if len(unknown_qubits) < min_number_unknowns:
                    min_number_unknowns = len(unknown_qubits)
                    minimum_unknowns = [unknown_qubits]
                elif len(unknown_qubits) == min_number_unknowns:
                    minimum_unknowns.append(unknown_qubits)

        # Pick a random set of unknown qubits from the best choices.
        unknown_qubits = random_generator.choice(minimum_unknowns)

        # Add all but one of the unknown qubits because the last one can be reconstructed from the
        # constraint.
        qubits_to_add = unknown_qubits - {random_generator.choice(tuple(unknown_qubits))}

        return qubits_to_add
