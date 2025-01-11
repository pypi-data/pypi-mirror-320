"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Classes to describe the properties of quantum devices.
"""

from __future__ import annotations

from functools import cached_property
from itertools import combinations, product
from typing import Generic, TypeVar

from attr import resolve_types
from attrs import field, frozen

from parityos.base import Qubit
from parityos.base.bit import GridQubit2D, get_q
from parityos.base.exceptions import ParityOSException
from parityos.base.utils import to_frozenset_check_unique

Q = TypeVar("Q", bound=Qubit, covariant=True)


def _check_more_than_one_qubit(self: Connection[Q], *_):
    if len(self) < 2:
        raise ParityOSException("A qubit connection must have more than one qubit")


def _check_quality(self: Connection[Q], *_):
    if self.quality < 0.0 or self.quality > 1.0:
        raise ParityOSException("The quality of a device connection must be between 0.0 and 1.0")


@frozen(order=True)
class DeviceNode(Generic[Q]):
    """
    Describes a node on a quantum device that holds a qubit

    :param qubit: The qubit that is part of this quantum device
    :param quality: The quality of this node, a float between 0 and 1. It describes the
        relative quality of this qubit, in relation to other qubit on this device.
        This can be used by the layout compiler to optimize which qubits are used.
    """

    qubit: Q
    quality: float = field(default=1.0, validator=_check_quality)


@frozen(order=True)
class Connection(Generic[Q]):
    """
    Describes a device connection in terms of qubit connectivity and quality.

    :param nodes: The qubits that are part of this device connection
    :param quality: The quality of this connection, a float between 0 and 1. It describes the
        relative quality of this connection, in relation to other connections on this device.
        This can be used by the layout compiler to optimize which connections are used.
    """

    nodes: frozenset[DeviceNode[Q]] = field(validator=_check_more_than_one_qubit, order=sorted)
    quality: float = field(default=1.0, validator=_check_quality)

    def __len__(self) -> int:
        """
        Returns the number of qubits in the connection
        """
        return len(self.nodes)

    @cached_property
    def qubits(self) -> frozenset[Q]:
        """
        Returns the qubits that are part of this connection
        """
        return frozenset({node.qubit for node in self.nodes})


@frozen
class DeviceConnectivity(Generic[Q]):
    """
    Abstract base model for describing the connectivity of quantum hardware.

    :param qubit_connections: A frozenset of device connections, which are the direct interactions
        that are available on the device. Single-qubit capabilities are assumed.
    """

    qubit_connections: frozenset[Connection[Q]] = field(converter=to_frozenset_check_unique)

    @cached_property
    def nodes(self) -> frozenset[DeviceNode[Q]]:
        """
        :return: all nodes from the connections on the device
        """
        return frozenset().union(*[connection.nodes for connection in self.qubit_connections])

    @cached_property
    def qubits(self) -> frozenset[Q]:
        """
        :return: all qubits from the connections on the device
        """
        return frozenset({node.qubit for node in self.nodes})

    @classmethod
    def rectangular_nearest_neighbor(
        cls, length: int, width: int
    ) -> DeviceConnectivity[GridQubit2D]:
        """
        Creates the device connectivity for a rectangular nearest-neighbor device
        according to the length and width of the device
        """
        qubit_connections = set()
        # Add the horizontal connections
        for x, y in product(range(length - 1), range(width)):
            connection = Connection(
                frozenset({DeviceNode(get_q(x, y)), DeviceNode(get_q(x + 1, y))})
            )
            qubit_connections.add(connection)

        # Add the vertical connections
        for x, y in product(range(length), range(width - 1)):
            connection = Connection(
                frozenset({DeviceNode(get_q(x, y)), DeviceNode(get_q(x, y + 1))})
            )
            qubit_connections.add(connection)

        return DeviceConnectivity(frozenset(qubit_connections))

    @classmethod
    def rectangular_plaquette(
        cls, length: int, width: int, include_triangles: bool = True
    ) -> DeviceConnectivity[GridQubit2D]:
        """
        Creates the device connectivity for a rectangular nearest-neighbor device
        according to the length and width of the device
        """
        qubit_connections = set()
        # Add the plaquettes
        for x, y in product(range(length - 1), range(width - 1)):
            plaquette = {
                DeviceNode(get_q(coordinate))
                for coordinate in [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
            }
            qubit_connections.add(Connection(frozenset(plaquette)))
            if include_triangles:
                # Generate and add the 3-body plaquettes
                triangles = [
                    Connection(frozenset(triangle)) for triangle in combinations(plaquette, 3)
                ]
                qubit_connections.update(triangles)

        return DeviceConnectivity(frozenset(qubit_connections))


# We need to resolve the types here, to make sure DeviceConnectivity serializes correctly.
# In the future, this should not be necessary anymore.
resolve_types(DeviceConnectivity)
