r"""Contain an evaluator that evaluates a mapping of evaluators."""

from __future__ import annotations

__all__ = ["EvaluatorDict"]

import logging
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils import repr_indent, repr_mapping

from arkas.evaluator2.base import BaseEvaluator
from arkas.evaluator2.vanilla import Evaluator

if TYPE_CHECKING:
    from collections.abc import Hashable, Mapping

logger = logging.getLogger(__name__)


class EvaluatorDict(BaseEvaluator):
    r"""Implement an evaluator that sequentially evaluates a mapping of
    evaluators.

    Args:
        evaluators: The mapping of evaluators to evaluate.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.state import AccuracyState
    >>> from arkas.evaluator2 import EvaluatorDict, AccuracyEvaluator, Evaluator
    >>> evaluator = EvaluatorDict(
    ...     {
    ...         "one": AccuracyEvaluator(
    ...             AccuracyState(
    ...                 y_true=np.array([1, 0, 0, 1, 1]),
    ...                 y_pred=np.array([1, 0, 0, 1, 1]),
    ...                 y_true_name="target",
    ...                 y_pred_name="pred",
    ...             )
    ...         ),
    ...         "two": Evaluator({"accuracy": 1.0, "total": 42}),
    ...     }
    ... )
    >>> evaluator
    EvaluatorDict(
      (one): AccuracyEvaluator(
          (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
        )
      (two): Evaluator(count=2)
    )
    >>> metrics = evaluator.evaluate()
    >>> metrics
    {'one': {'accuracy': 1.0, 'count_correct': 5, 'count_incorrect': 0, 'count': 5, 'error': 0.0},
     'two': {'accuracy': 1.0, 'total': 42}}

    ```
    """

    def __init__(self, evaluators: Mapping[Hashable, BaseEvaluator]) -> None:
        self._evaluators = evaluators

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping(self._evaluators))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> Evaluator:
        return Evaluator(metrics=self.evaluate())

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._evaluators, other._evaluators, equal_nan=equal_nan)

    def evaluate(self, prefix: str = "", suffix: str = "") -> dict:
        return {
            key: evaluator.evaluate(prefix=prefix, suffix=suffix)
            for key, evaluator in self._evaluators.items()
        }
