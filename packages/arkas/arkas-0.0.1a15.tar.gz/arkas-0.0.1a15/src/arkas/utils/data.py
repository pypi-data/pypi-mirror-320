r"""Contain data utility functions."""

from __future__ import annotations

__all__ = ["find_keys", "find_missing_keys", "flat_keys", "prepare_array"]


from typing import TYPE_CHECKING

import numpy as np
import polars as pl

from arkas.utils.array import to_array

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def find_keys(data: Mapping | pl.DataFrame) -> set:
    r"""Find all the keys in the input data.

    Args:
        data: The input data.

    Returns:
        The set of keys.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.utils.data import find_keys
    >>> keys = find_keys(
    ...     {"pred": np.array([3, 2, 0, 1, 0]), "target": np.array([3, 2, 0, 1, 0])}
    ... )
    >>> sorted(keys)
    ['pred', 'target']
    >>> keys = find_keys(pl.DataFrame({"pred": [3, 2, 0, 1, 0], "target": [3, 2, 0, 1, 0]}))
    >>> sorted(keys)
    ['pred', 'target']

    ```
    """
    if isinstance(data, pl.DataFrame):
        return set(data.columns)
    return set(data.keys())


def find_missing_keys(keys: set | Sequence, queries: set | Sequence) -> set:
    r"""Return the set of queries that are not in the input keys.

    Args:
        keys: The keys.
        queries: The queries i.e. the keys to check in the input keys.

    Returns:
        The set of missing keys.

    Example usage:

    ```pycon

    >>> from arkas.utils.data import find_missing_keys
    >>> keys = find_missing_keys(
    ...     keys={"key1", "key2", "key3"}, queries=["key1", "key2", "key4"]
    ... )
    >>> keys
    {'key4'}

    ```
    """
    keys = set(keys)
    queries = set(queries)
    intersection = set(keys).intersection(queries)
    return queries.difference(intersection)


def flat_keys(keys: Sequence[str | Sequence[str]]) -> list[str]:
    r"""Flat and merge a sequence of keys or sequence of keys.

    Args:
        keys: The keys to flat.

    Returns:
        The list of keys.

    Example usage:

    ```pycon

    >>> from arkas.utils.data import flat_keys
    >>> keys = flat_keys(["key0", ["key1"], ["key2", "key3", "key4"]])
    >>> keys
    ['key0', 'key1', 'key2', 'key3', 'key4']

    ```
    """
    out = []
    for key in keys:
        if isinstance(key, str):
            out.append(key)
        else:
            out.extend(key)
    return out


def prepare_array(data: dict | pl.DataFrame, keys: Sequence[str]) -> np.ndarray:
    r"""Prepare the data and return an array.

    Args:
        data: The input data.
        keys: The keys or columns to extract from the input data.

    Returns:
        The prepared array.

    Example usage:

    ```pycon

    >>> from arkas.utils.data import prepare_array
    >>> keys = prepare_array({"key": np.array([1, 2, 3, 4, 5])}, keys="key")
    >>> keys
    array([1, 2, 3, 4, 5])

    ```
    """
    if isinstance(keys, str):
        return to_array(data[keys])
    if isinstance(data, pl.DataFrame):
        return to_array(data.select(keys))
    return np.stack([to_array(data[key]) for key in keys], axis=1)
