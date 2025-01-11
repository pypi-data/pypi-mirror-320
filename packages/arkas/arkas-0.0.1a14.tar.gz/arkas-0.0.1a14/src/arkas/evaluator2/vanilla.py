r"""Contain the implementation of a simple evaluator."""

from __future__ import annotations

__all__ = ["Evaluator"]

from typing import Any

from coola import objects_are_equal

from arkas.evaluator2.base import BaseEvaluator


class Evaluator(BaseEvaluator):
    r"""Implement a simple evaluator.

    Args:
        metrics: The dictionary of metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.evaluator2 import Evaluator
    >>> evaluator = Evaluator({"accuracy": 1.0, "total": 42})
    >>> evaluator
    Evaluator(count=2)
    >>> evaluator.evaluate()
    {'accuracy': 1.0, 'total': 42}

    ```
    """

    def __init__(self, metrics: dict | None = None) -> None:
        self._metrics = metrics or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(count={len(self._metrics):,})"

    def compute(self) -> Evaluator:
        return Evaluator(metrics=self._metrics)

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._metrics, other._metrics, equal_nan=equal_nan)

    def evaluate(self, prefix: str = "", suffix: str = "") -> dict:
        return {f"{prefix}{key}{suffix}": value for key, value in self._metrics.items()}
