# noqa: A005
r"""Implement some utility functions for ``numpy.ndarray``s."""

from __future__ import annotations

__all__ = ["check_square_matrix", "filter_range", "nonnan", "rand_replace", "to_array"]

from typing import Any

import numpy as np
import polars as pl
from coola.utils.array import to_array as coola_to_array


def check_square_matrix(name: str, array: np.ndarray) -> None:
    r"""Check if the input array is a square matrix.

    Args:
        name: The name of the variable.
        array: The array to check.

    Raises:
        ValueError: if the array is not a square matrix.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.utils.array import check_square_matrix
    >>> check_square_matrix("var", np.ones((3, 3)))

    ```
    """
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        msg = (
            f"Incorrect {name!r}. The array must be a square matrix but received an array of "
            f"shape {array.shape}"
        )
        raise ValueError(msg)


def filter_range(array: np.ndarray, xmin: float, xmax: float) -> np.ndarray:
    r"""Filter in the values in a given range.

    Args:
        array: The input array.
        xmin: The lower bound of the range.
        xmax: The upper bound of the range.

    Returns:
        A 1-d array with only the values in the given range.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.utils.array import filter_range
    >>> out = filter_range(np.arange(10), xmin=-1, xmax=5)
    >>> out
    array([0, 1, 2, 3, 4, 5])

    ```
    """
    return np.extract(np.logical_and(xmin <= array, array <= xmax), array)


def nonnan(array: np.ndarray) -> np.ndarray:
    r"""Return the non-NaN values of an array.

    Args:
        array: The input array.

    Returns:
        A 1d array with the non-NaN values of the input array.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.utils.array import nonnan
    >>> nonnan(np.asarray([1, 2, float("nan"), 5, 6]))
    array([1., 2., 5., 6.])
    >>> nonnan(np.asarray([[1, 2, float("nan")], [4, 5, 6]]))
    array([1., 2., 4., 5., 6.])

    ```
    """
    mask = np.isnan(array)
    return array[~mask]


def rand_replace(
    arr: np.ndarray, value: Any, prob: float = 0.5, rng: np.random.Generator | None = None
) -> np.ndarray:
    r"""Return an array that contains the same values as the input array,
    excepts some values are replaced by ``value``.

    Args:
        arr: The array with the original values.
        value: The value used to replace existing values.
        prob: The probability of value replacement.
            If the value is ``0.2``, it means each value as 20% chance
            to be replaced.
        rng: The random number generator used to decide which values
            are replaced or not. If ``None``, the default random
            number generator is used.

    Returns:
        The generated array.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.utils.array import rand_replace
    >>> rng = np.random.default_rng(42)
    >>> out = rand_replace(np.arange(10), value=-1, prob=0.4, rng=rng)

    ```
    """
    if rng is None:
        rng = np.random.default_rng()
    mask = rng.choice([True, False], size=arr.shape, p=[prob, 1.0 - prob])
    return np.where(mask, value, arr)


def to_array(data: Any) -> np.ndarray:
    r"""Convert the input to a ``numpy.ndarray``.

    Args:
        data: The data to convert to a NumPy array.

    Returns:
        A NumPy array.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.utils.array import to_array
    >>> to_array([1, 2, 3, 4, 5])
    array([1, 2, 3, 4, 5])
    >>> to_array(pl.Series([1, 2, 3, 4, 5]))
    array([1, 2, 3, 4, 5])
    >>> to_array(pl.DataFrame({"col1": [1, 2, 3, 4, 5], "col2": [0, 1, 0, 1, 0]}))
    array([[1, 0], [2, 1], [3, 0], [4, 1], [5, 0]])

    ```
    """
    if isinstance(data, pl.Series):
        return data.to_numpy()
    if isinstance(data, pl.DataFrame):
        return data.to_numpy()
    return coola_to_array(data)
