r"""Contain the average precision evaluator for multiclass labels."""

from __future__ import annotations

__all__ = ["MulticlassAveragePrecisionEvaluator"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_mapping_line

from arkas.evaluator.lazy import BaseLazyEvaluator
from arkas.metric.utils import check_nan_policy
from arkas.result import MulticlassAveragePrecisionResult, Result
from arkas.utils.array import to_array

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class MulticlassAveragePrecisionEvaluator(BaseLazyEvaluator[MulticlassAveragePrecisionResult]):
    r"""Implement the average precision evaluator for multiclass labels.

    Args:
        y_true: The key or column name of the ground truth target
            labels.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions.
        drop_nulls: If ``True``, the rows with null values in
            ``y_true`` or ``y_score`` columns are dropped.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import MulticlassAveragePrecisionEvaluator
    >>> evaluator = MulticlassAveragePrecisionEvaluator(y_true="target", y_score="pred")
    >>> evaluator
    MulticlassAveragePrecisionEvaluator(y_true='target', y_score='pred', drop_nulls=True, nan_policy='propagate')
    >>> data = pl.DataFrame(
    ...     {
    ...         "pred": [
    ...             [0.7, 0.2, 0.1],
    ...             [0.4, 0.3, 0.3],
    ...             [0.1, 0.8, 0.1],
    ...             [0.2, 0.5, 0.3],
    ...             [0.3, 0.3, 0.4],
    ...             [0.1, 0.2, 0.7],
    ...         ],
    ...         "target": [0, 0, 1, 1, 2, 2],
    ...     },
    ...     schema={"pred": pl.Array(pl.Float64, 3), "target": pl.Int64},
    ... )
    >>> result = evaluator.evaluate(data)
    >>> result
    MulticlassAveragePrecisionResult(y_true=(6,), y_score=(6, 3), nan_policy='propagate')

    ```
    """

    def __init__(
        self,
        y_true: str,
        y_score: str,
        drop_nulls: bool = True,
        nan_policy: str = "propagate",
    ) -> None:
        super().__init__(drop_nulls=drop_nulls)
        self._y_true = y_true
        self._y_score = y_score

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true,
                "y_score": self._y_score,
                "drop_nulls": self._drop_nulls,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def evaluate(
        self, data: pl.DataFrame, lazy: bool = True
    ) -> MulticlassAveragePrecisionResult | Result:
        logger.info(
            f"Evaluating the multiclass average precision (AP) | y_true={self._y_true!r} | "
            f"y_score={self._y_score!r} | drop_nulls={self._drop_nulls} | "
            f"nan_policy={self._nan_policy!r}"
        )
        return self._evaluate(data, lazy)

    def _compute_result(self, data: pl.DataFrame) -> MulticlassAveragePrecisionResult:
        return MulticlassAveragePrecisionResult(
            y_true=to_array(data[self._y_true]).ravel(),
            y_score=to_array(data[self._y_score]),
            nan_policy=self._nan_policy,
        )

    def _get_columns(self) -> tuple[str, ...]:
        return (self._y_true, self._y_score)
