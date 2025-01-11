r"""Contain mapping utility functions."""

from __future__ import annotations

__all__ = ["find_missing_keys"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def find_missing_keys(mapping: Mapping, keys: set | Sequence) -> set:
    r"""Return the set of keys that are not in the input mapping.

    Args:
        mapping: The input mapping.
        keys: The keys to check in the input mapping.

    Returns:
        The set of missing keys.

    Example usage:

    ```pycon

    >>> from arkas.utils.mapping import find_missing_keys
    >>> keys = find_missing_keys(
    ...     mapping={"key1": 1, "key2": 2, "key3": 3}, keys=["key1", "key2", "key4"]
    ... )
    >>> keys
    {'key4'}

    ```
    """
    keys = set(keys)
    intersection = set(mapping.keys()).intersection(keys)
    return keys.difference(intersection)
