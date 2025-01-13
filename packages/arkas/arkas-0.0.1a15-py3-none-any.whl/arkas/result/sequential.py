r"""Implement a result that merges multiple results."""

from __future__ import annotations

__all__ = ["SequentialResult"]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils import str_indent, str_sequence

from arkas.result import BaseResult

if TYPE_CHECKING:
    from collections.abc import Sequence


class SequentialResult(BaseResult):
    r"""Implement a result to merge multiple result objects into a single
    result object.

    Args:
        results: The results to merge. This order is used to merge
            the metrics and figures if they have duplicate keys,
            i.e. only the last value for each key is kept.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import SequentialResult, Result
    >>> result = SequentialResult(
    ...     [
    ...         Result(metrics={"accuracy": 62.0, "count": 42}),
    ...         Result(metrics={"ap": 0.42, "count": 42}),
    ...     ]
    ... )
    >>> result
    SequentialResult(count=2)
    >>> result.compute_metrics()
    {'accuracy': 62.0, 'count': 42, 'ap': 0.42}

    ```
    """

    def __init__(self, results: Sequence[BaseResult]) -> None:
        self._results = tuple(results)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(count={len(self._results):,})"

    def __str__(self) -> str:
        args = str_indent(str_sequence(self._results))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict:
        out = {}
        for result in self._results:
            out |= result.compute_metrics(prefix=prefix, suffix=suffix)
        return out

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._results, other._results, equal_nan=equal_nan)

    def generate_figures(self, prefix: str = "", suffix: str = "") -> dict:
        out = {}
        for result in self._results:
            out |= result.generate_figures(prefix=prefix, suffix=suffix)
        return out
