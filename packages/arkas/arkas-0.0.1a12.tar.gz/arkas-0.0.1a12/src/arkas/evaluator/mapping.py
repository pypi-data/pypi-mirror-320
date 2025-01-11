r"""Contain an evaluator that evaluates a mapping of evaluators."""

from __future__ import annotations

__all__ = ["EvaluatorDict"]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping

from arkas.evaluator import BaseEvaluator
from arkas.result import EmptyResult, MappingResult, Result

if TYPE_CHECKING:
    from collections.abc import Hashable, Mapping

    import polars as pl

    from arkas.result import BaseResult

logger = logging.getLogger(__name__)


class EvaluatorDict(BaseEvaluator):
    r"""Implement an evaluator that sequentially evaluates a mapping of
    evaluators.

    Args:
        evaluators: The mapping of evaluators to evaluate.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import (
    ...     EvaluatorDict,
    ...     BinaryPrecisionEvaluator,
    ...     BinaryRecallEvaluator,
    ... )
    >>> evaluator = EvaluatorDict(
    ...     {
    ...         "precision": BinaryPrecisionEvaluator(y_true="target", y_pred="pred"),
    ...         "recall": BinaryRecallEvaluator(y_true="target", y_pred="pred"),
    ...     }
    ... )
    >>> evaluator
    EvaluatorDict(
      (precision): BinaryPrecisionEvaluator(y_true='target', y_pred='pred', drop_nulls=True, nan_policy='propagate')
      (recall): BinaryRecallEvaluator(y_true='target', y_pred='pred', drop_nulls=True, nan_policy='propagate')
    )
    >>> data = pl.DataFrame({"pred": [1, 0, 0, 1, 1], "target": [1, 0, 0, 1, 1]})
    >>> result = evaluator.evaluate(data)
    >>> result
    MappingResult(count=2)
    >>> result = evaluator.evaluate(data, lazy=False)
    >>> result
    Result(metrics=2, figures=2)

    ```
    """

    def __init__(self, evaluators: Mapping[Hashable, BaseEvaluator]) -> None:
        self._evaluators = evaluators

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping(self._evaluators))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def evaluate(self, data: pl.DataFrame, lazy: bool = True) -> BaseResult:
        out = MappingResult(
            {
                key: evaluator.evaluate(data=data, lazy=lazy)
                for key, evaluator in self._evaluators.items()
            }
        )
        if lazy or isinstance(out, EmptyResult):
            return out
        return Result(metrics=out.compute_metrics(), figures=out.generate_figures())
