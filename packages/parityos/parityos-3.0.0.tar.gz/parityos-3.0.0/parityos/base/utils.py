"""
ParityQC GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.
"""

from __future__ import annotations

from collections.abc import ItemsView, Iterable, Mapping, Set
from typing import (
    Protocol,
    TypeVar,
    Union,
)

from symengine import Expr
from typing_extensions import TypeAlias, TypeIs, override

from parityos.base.exceptions import ParityOSUniquenessError

T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")

WeightTypes = (int, float, Expr)
Weight: TypeAlias = Union[int, float, Expr]


class SupportsString(Protocol):
    @override
    def __str__(self) -> str: ...


def to_list(elements: T | Iterable[T]) -> list[T]:
    """Wrap a single item or an iterable of items in a list."""
    return list(elements) if isinstance(elements, Iterable) else [elements]


def to_tuple(elements: T | Iterable[T]) -> tuple[T, ...]:
    """Wrap a single item or an iterable of items in a tuple."""
    return tuple(elements) if isinstance(elements, Iterable) else (elements,)


def to_frozenset_check_unique(elements: T | Iterable[T]) -> frozenset[T]:
    """Convert input elements to frozenset and raise if there are duplicates.

    :param elements: collection of elements to be turned into a frozenset
    :raises ParityOSUniquenessError: if there are duplicate inputs
    :return: frozenset of input elements
    """
    if isinstance(elements, Set):
        return frozenset(elements)
    elements = to_tuple(elements)
    item_set = frozenset(elements)
    if len(elements) != len(item_set):
        raise ParityOSUniquenessError(f"got {len(elements) - len(item_set)} duplicate elements")
    return item_set


def collect_pairs(pairs: Iterable[tuple[T, Weight]]) -> ItemsView[T, Weight]:
    """Remove duplicate first values in an iterable of pairs by collecting pairs
    with the same first value and summing their second values.

    Beware, zero value elements are not removed and need to be filtered out separately if necessary.

    :param pairs: pairs to be collected
    :return: iterable of collected pairs
    """
    dct: dict[T, Weight] = {}
    for key, value in pairs:
        existing_value = dct.get(key)
        dct[key] = value if existing_value is None else existing_value + value

    return dct.items()


def stringify_iterable(iterable: Iterable[SupportsString], separator: str = ", ") -> str:
    """
    Stringify a sequence of elements.

    This is different from e.g. `str([obj1, obj2, obj3])` as Python stringifies containers by always
    using ", " as separator and calling the elements' __repr__ instead of __str__ method.

    Examples:

        >>> assert stringify_iterable((3,)) == "3"
        >>> assert stringify_iterable(("a", "b")) == "a, b"
        >>> assert stringify_iterable([get_q(0), get_q(1)]) == "q(0), q(1)"
        # >>> assert stringify_iterable((get_q(0), get_q(1)), separator="|") == "q(0)|q(1)"

    :param iterable: elements of a sequence to be stringified
    :param separator: (keyword-only) separator to put between stringified elements

    """
    return separator.join([str(element) for element in iterable])


def is_iterable_of_pairs_mapping(
    obj: Iterable[tuple[KT, VT]] | Mapping[KT, VT],
) -> TypeIs[Mapping[KT, VT]]:
    """Return whether a passed object is a Mapping.

    The main purpose of this method is the TypeIs return type used for type narrowing.
    """
    return isinstance(obj, Mapping)
