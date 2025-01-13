r"""Contain the median absolute error (MAE) evaluator."""

from __future__ import annotations

__all__ = ["MedianAbsoluteErrorEvaluator"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_mapping_line

from arkas.evaluator.lazy import BaseLazyEvaluator
from arkas.metric.utils import check_nan_policy
from arkas.result import MedianAbsoluteErrorResult, Result
from arkas.utils.array import to_array

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class MedianAbsoluteErrorEvaluator(BaseLazyEvaluator[MedianAbsoluteErrorResult]):
    r"""Implement the median absolute error (MAE) evaluator.

    Args:
        y_true: The key or column name of the ground truth target
            values.
        y_pred: The key or column name of the predicted values.
        drop_nulls: If ``True``, the rows with null values in
            ``y_true`` or ``y_pred`` columns are dropped.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import MedianAbsoluteErrorEvaluator
    >>> evaluator = MedianAbsoluteErrorEvaluator(y_true="target", y_pred="pred")
    >>> evaluator
    MedianAbsoluteErrorEvaluator(y_true='target', y_pred='pred', drop_nulls=True, nan_policy='propagate')
    >>> data = pl.DataFrame({"pred": [1, 2, 3, 4, 5], "target": [1, 2, 3, 4, 5]})
    >>> result = evaluator.evaluate(data)
    >>> result
    MedianAbsoluteErrorResult(y_true=(5,), y_pred=(5,), nan_policy='propagate')

    ```
    """

    def __init__(
        self,
        y_true: str,
        y_pred: str,
        drop_nulls: bool = True,
        nan_policy: str = "propagate",
    ) -> None:
        super().__init__(drop_nulls=drop_nulls)
        self._y_true = y_true
        self._y_pred = y_pred

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true,
                "y_pred": self._y_pred,
                "drop_nulls": self._drop_nulls,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def evaluate(self, data: pl.DataFrame, lazy: bool = True) -> MedianAbsoluteErrorResult | Result:
        logger.info(
            f"Evaluating the median absolute error | y_true={self._y_true!r} | "
            f"y_pred={self._y_pred!r} | drop_nulls={self._drop_nulls} | "
            f"nan_policy={self._nan_policy!r}"
        )
        return self._evaluate(data, lazy)

    def _compute_result(self, data: pl.DataFrame) -> MedianAbsoluteErrorResult:
        return MedianAbsoluteErrorResult(
            y_true=to_array(data[self._y_true]).ravel(),
            y_pred=to_array(data[self._y_pred]).ravel(),
            nan_policy=self._nan_policy,
        )

    def _get_columns(self) -> tuple[str, ...]:
        return (self._y_true, self._y_pred)
