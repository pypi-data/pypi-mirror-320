r"""Implement the simple result."""

from __future__ import annotations

__all__ = ["EmptyResult", "Result"]

from typing import Any

from coola import objects_are_equal

from arkas.result.base import BaseResult


class Result(BaseResult):
    r"""Implement a simple result.

    Args:
        metrics: The metrics.
        figures: The figures.

    Example usage:

    ```pycon

    >>> from arkas.result import Result
    >>> result = Result(metrics={"accuracy": 1.0, "count": 42}, figures={})
    >>> result
    Result(metrics=2, figures=0)
    >>> result.compute_metrics()
    {'accuracy': 1.0, 'count': 42}

    ```
    """

    def __init__(self, metrics: dict | None = None, figures: dict | None = None) -> None:
        self._metrics = metrics or {}
        self._figures = figures or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(metrics={len(self._metrics):,}, figures={len(self._figures):,})"

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict:
        return {f"{prefix}{key}{suffix}": value for key, value in self._metrics.items()}

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(
            self._metrics, other._metrics, equal_nan=equal_nan
        ) and objects_are_equal(self._figures, other._figures, equal_nan=equal_nan)

    def generate_figures(self, prefix: str = "", suffix: str = "") -> dict:
        return {f"{prefix}{key}{suffix}": value for key, value in self._figures.items()}


class EmptyResult(Result):
    r"""Implement an empty result.

    This result is designed to be used when it is possible to evaluate a
    result.
    """

    def __init__(self) -> None:
        super().__init__(metrics={}, figures={})

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"
