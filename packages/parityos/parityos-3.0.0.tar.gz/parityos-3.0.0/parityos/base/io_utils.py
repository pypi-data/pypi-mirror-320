"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Implements Serialization and Deserialization of attrs classes to and from dicts and json
"""

from __future__ import annotations

import json
from collections.abc import Callable, Hashable, Mapping, Set
from datetime import datetime
from functools import partial
from operator import itemgetter
from pathlib import Path
from types import GenericAlias
from typing import Any, Protocol, TypeVar, get_args, get_origin

from cattrs import Converter
from cattrs.strategies import (
    configure_tagged_union,
    include_subclasses,
)
from symengine import Expr, sympify

from parityos.base.utils import Weight

T = TypeVar("T")
KT = TypeVar("KT", bound=Hashable)
VT = TypeVar("VT")


class SupportsComparison(Protocol):
    def __lt__(self, other: object) -> bool: ...


CT = TypeVar("CT", bound=SupportsComparison)

converter = Converter(
    unstruct_collection_overrides={  # convert all tuples to lists for json compatibility
        tuple: list,
    }
)


def is_orderable(cls: type[SupportsComparison]) -> bool:
    """
    Check whether a class implements custom __lt__.

    Since every class automatically inherits __lt__ from object,
    it is not enough to check for hasattr(cls, "__lt__")
    """
    # unpack GenericAlias (e.g. list[Any] -> list)
    cls = get_origin(cls) or cls
    cls_lt: Callable[[object, object], bool] | None = getattr(cls, "__lt__", None)
    object_lt: Callable[[object, object], bool] | None = getattr(object, "__lt__", None)
    return cls_lt != object_lt


def is_set_of_orderables(cls: type) -> bool:
    """
    Check whether a type is a set of orderable objects.

    Returns true only for generics that are subtypes of collections.abc.Set
    and contain objects that are orderable.

    Examples:
    >>> is_set_of_orderables(set[int])
    True
    >>> is_set_of_orderables(frozenset[str])
    True
    >>> is_set_of_orderables(set)  # no content annotation
    False
    >>> is_set_of_orderables(list[float])  # list is not a subtype of Set
    False
    """
    return (
        isinstance(cls, GenericAlias)
        and issubclass(get_origin(cls), Set)
        and is_orderable(get_args(cls)[0])
    )


def is_dict_with_sortable_keys(cls: type) -> bool:
    """
    Check whether a type is a dict with orderable keys.

    Returns true only for generics that are subtypes of collections.abc.Mapping
    and whose key type is orderable.

    Examples:
    >>> is_dict_with_sortable_keys(dict[int, str])
    True
    >>> is_dict_with_sortable_keys(MutableMapping[str, float])
    True
    >>> is_dict_with_sortable_keys(dict)  # no content annotation
    False
    >>> is_dict_with_sortable_keys(list[tuple[str, float]])  # list is not a subtype of Set
    False
    """
    return (
        isinstance(cls, GenericAlias)
        and issubclass(get_origin(cls), Mapping)
        and is_orderable(get_args(cls)[0])  # get_args(cls)[0] is the key type
    )


def unstructure_set_to_ordered_list(set_: Set[CT]) -> Any:
    """
    Serialize unordered sets to sorted lists
    """
    return converter.unstructure(sorted(set_))


def unstructure_dict_to_ordered_list(dct: dict[KT, VT]) -> list[tuple[KT, VT]]:
    """
    Serialize unordered dicts to a sorted list of key-value pairs sorted by keys
    """
    return converter.unstructure(sorted(dct.items(), key=itemgetter(0)))


def structure_dict_from_list(lst: list[list[KT | VT]], cls: type[dict[KT, VT]]) -> dict[KT, VT]:
    """
    Deserializs a list of key-value pairs into a dict.
    """
    _KT, _VT = get_args(cls)  # get concrete runtime types
    # tuple[_KT, _VT] creates tuple[K, T] from dict[K, T]
    # this is needed for the converter to correctly structure the list of key-value pairs
    converted: list[tuple[KT, VT]] = converter.structure(lst, list[tuple[_KT, _VT]])
    return dict(converted)


converter.register_unstructure_hook_func(is_set_of_orderables, unstructure_set_to_ordered_list)
converter.register_unstructure_hook_func(
    is_dict_with_sortable_keys, unstructure_dict_to_ordered_list
)
converter.register_structure_hook(datetime, lambda dt, _: datetime.fromisoformat(dt))

converter.register_structure_hook_func(is_dict_with_sortable_keys, structure_dict_from_list)
converter.register_unstructure_hook(datetime, lambda dt: dt.isoformat())

converter.register_unstructure_hook(Expr, lambda expr: str(expr))
converter.register_structure_hook(Expr, lambda expr_str, _: sympify(expr_str))
converter.register_structure_hook(
    Weight,
    lambda weight_data, _: sympify(weight_data) if isinstance(weight_data, str) else weight_data,
)


def register_subclasses(cls: type, tag_name: str):
    """
    Convenience function to register all subclasses of `cls` with this module's converter, with the
    following settings:

        - all annotation with `cls` will be interpreted as union of all it's subclasses
        - every subclass gets serialized with an addition field with key `tag_name` and value
            its class name, to facilitate unambiguous deserialization to `cls`

    """
    include_subclasses(
        cls,
        converter,
        union_strategy=partial(configure_tagged_union, tag_name=tag_name),
    )


def to_dict(obj: object) -> dict[str, Any]:
    """Serialize `obj` into its dict representation."""
    return converter.unstructure(obj)


def from_dict(data: dict[str, Any], cls: type[T]) -> T:
    """Construct an instance of `cls` from its dict representation."""
    return converter.structure(data, cls)


def json_dumps(obj: object) -> str:
    """Convert `obj` to json string."""
    return json.dumps(to_dict(obj))


def json_dump(obj: object, filepath: str | Path):
    """Save `obj` to `filepath` as json."""
    with Path(filepath).open("w") as file:
        json.dump(to_dict(obj), file)


def json_loads(json_str: str, cls: type[T]) -> T:
    """Construct an instance of `cls` a json string representation."""
    return from_dict(json.loads(json_str), cls)


def json_load(filepath: str | Path, cls: type[T]) -> T:
    """Construct an instance of `cls` from the json file at `filepath`."""
    with Path(filepath).open("r") as file:
        return from_dict(json.load(file), cls)
