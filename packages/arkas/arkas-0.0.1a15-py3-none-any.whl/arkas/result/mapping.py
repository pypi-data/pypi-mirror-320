r"""Implement a result that combines a mapping of result objects into a
single result object."""

from __future__ import annotations

__all__ = ["MappingResult"]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils import str_indent, str_mapping

from arkas.result import BaseResult

if TYPE_CHECKING:
    from collections.abc import Mapping


class MappingResult(BaseResult):
    r"""Implement a result that combines a mapping of result objects into
    a single result object.

    Args:
        results: The mapping of result objects to combine.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import MappingResult, Result
    >>> result = MappingResult(
    ...     {
    ...         "class1": Result(metrics={"accuracy": 62.0, "count": 42}),
    ...         "class2": Result(metrics={"accuracy": 42.0, "count": 42}),
    ...     }
    ... )
    >>> result
    MappingResult(count=2)
    >>> result.compute_metrics()
    {'class1': {'accuracy': 62.0, 'count': 42}, 'class2': {'accuracy': 42.0, 'count': 42}}

    ```
    """

    def __init__(self, results: Mapping[str, BaseResult]) -> None:
        self._results = results

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(count={len(self._results):,})"

    def __str__(self) -> str:
        args = str_indent(str_mapping(self._results))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict:
        return {
            key: result.compute_metrics(prefix=prefix, suffix=suffix)
            for key, result in self._results.items()
        }

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._results, other._results, equal_nan=equal_nan)

    def generate_figures(self, prefix: str = "", suffix: str = "") -> dict:
        return {
            key: result.generate_figures(prefix=prefix, suffix=suffix)
            for key, result in self._results.items()
        }
