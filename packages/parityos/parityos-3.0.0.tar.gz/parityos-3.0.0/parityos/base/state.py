from __future__ import annotations

from collections.abc import Iterable, KeysView, Mapping
from enum import Enum
from functools import cached_property
from operator import itemgetter
from types import MappingProxyType

from attrs import Attribute, evolve, field, frozen
from typing_extensions import Self, TypeAlias

from parityos.base.bit import Qubit, get_q
from parityos.base.exceptions import ParityOSException
from parityos.base.utils import is_iterable_of_pairs_mapping, to_frozenset_check_unique, to_list

# In accordance with bit_to_spin_value:
# even = False
#  odd = True
Parity: TypeAlias = bool


class PauliBasis(Enum):
    """Represents the possible pauli basis choices for a state."""

    X = "X"
    Y = "Y"
    Z = "Z"


def _check_at_least_one_qubit(
    self: PauliBasisState,
    _: Attribute[frozenset[tuple[Qubit, bool]]],
    qubit_value_pairs: frozenset[tuple[Qubit, bool]],
):
    if len(qubit_value_pairs) < 1:
        raise ParityOSException(f"{self.__class__.__name__} must hold at least one qubit")


def _to_qubit_value_pair_frozenset(
    elements: Iterable[tuple[Qubit, bool]] | Mapping[Qubit, bool],
) -> frozenset[tuple[Qubit, bool]]:
    if is_iterable_of_pairs_mapping(elements):
        return frozenset(elements.items())
    else:
        return to_frozenset_check_unique(elements)


@frozen
class PauliBasisState:
    """Represents an eigenstate of a Pauli operator (either X, Y, or Z).

    The state is stored as a set of (qubit, value) paris.
    The value of each qubit is represented as a boolean, where
     - The +1 eigenstate is False
     - The -1 eigenstate is True

    :raises ParityOSException: if the amount of passed qubit_value pairs is zero
    """

    qubit_value_pairs: frozenset[tuple[Qubit, bool]] = field(
        converter=_to_qubit_value_pair_frozenset, validator=_check_at_least_one_qubit
    )
    basis: PauliBasis = field(default=PauliBasis.Z)

    @property
    def qubits(self) -> KeysView[Qubit]:
        """The set of qubits on which this state is defined."""
        return self.qubit_to_value.keys()

    @cached_property
    def qubit_to_value(self) -> MappingProxyType[Qubit, bool]:
        """A mapping from each qubit to its boolean value."""
        return MappingProxyType(dict(self.qubit_value_pairs))

    @classmethod
    def from_bitstring(
        cls,
        bitstring: str,
        qubits: Qubit | Iterable[Qubit] | None = None,
        basis: PauliBasis = PauliBasis.Z,
    ):
        """Create a `ClassicalState` from a bitstring and optionally an iterable of Qubits.

        If qubits is None (default), a sequence of qubits with labels being the integers from 0 to
        `len(bitstring) - 1` is used.

        If `qubits` is not None it must be of the same length as `bitstring`.

        The state is created by associating the n-th qubit in `qubit` with the n-th bit in
        `bitstring`, where "0" -> False and "1" -> True.

        :param bitstring: string consisting of "0" and "1".
        :param qubits: qubits on which the state is defined, defaults to None
        :raises ParityOSException: if the lengths of the bitstring and the qubits differ
        """
        qubits = [get_q(i) for i in range(len(bitstring))] if qubits is None else to_list(qubits)
        if len(qubits) != len(bitstring):
            raise ParityOSException(
                f"number of qubits ({len(qubits)}]) doesn't "
                + f"match the number of bits ({len(bitstring)})"
            )
        return cls([(qubit, bool(int(bit))) for qubit, bit in zip(qubits, bitstring)], basis)

    def to_bitstring(self) -> str:
        """Create a bitstring from this state.

        The qubits of the state are sorted and the values concatenated to a string,
        where True -> "1" and False -> "0".

        :return: a bitstring made up of "0" and "1".
        """
        return "".join(
            [str(int(value)) for _, value in sorted(self.qubit_value_pairs, key=itemgetter(0))]
        )

    def flip(self) -> Self:
        """Return a copy of this state where all qubit values are flipped (negated)"""
        return evolve(
            self,
            qubit_value_pairs={(qubit, not value) for qubit, value in self.qubit_value_pairs},
        )

    def evaluate_parity(self, qubits: Iterable[Qubit]) -> Parity:
        """Compute parity of given qubits in this state.

        The resulting parity is represented as bool, where "even" = False and "odd" = True.
        This is in accordance with the convention used in bit_to_spin_value.

        All passed qubits must be present in the state.

        :raises ParityOSException:
            - if not all of the given qubits are present in this state.
            - the passed qubits set is empty
        :return: parity of given qubits in this state. True = Odd, False = Even
        """
        try:
            values = [self.qubit_to_value[qubit] for qubit in qubits]
        except KeyError as e:
            raise ParityOSException("Not all qubits are contained in the state.") from e

        return bool(sum(values) % 2)


def bit_to_spin_value(bit: bool) -> int:
    """Transform computational state bit to spin eigenvalue following the convention
     - |+S> = |0> = False
     - |-S> = |1> = True
    with |+S>, |-S> the spin operator eigenstates and |0>, |1> the computational basis states.
    """
    return 1 - 2 * bit
