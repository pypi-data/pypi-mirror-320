r"""Contain an average precision evaluator."""

from __future__ import annotations

__all__ = ["AveragePrecisionEvaluator"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_mapping_line

from arkas.evaluator.lazy import BaseLazyEvaluator
from arkas.metric.utils import check_label_type, check_nan_policy
from arkas.result import AveragePrecisionResult, Result
from arkas.utils.array import to_array

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class AveragePrecisionEvaluator(BaseLazyEvaluator[AveragePrecisionResult]):
    r"""Implement the average precision evaluator.

    Args:
        y_true: The key or column name of the ground truth target
            labels.
        y_score: The key or column name of the predicted labels.
        label_type: The type of labels used to evaluate the metrics.
            The valid values are: ``'binary'``, ``'multiclass'``,
            ``'multilabel'``, and ``'auto'``. If ``'auto'``, it tries
            to automatically find the label type from the arrays'
            shape.
        drop_nulls: If ``True``, the rows with null values in
            ``y_true`` or ``y_score`` columns are dropped.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import AveragePrecisionEvaluator
    >>> evaluator = AveragePrecisionEvaluator(y_true="target", y_score="pred")
    >>> evaluator
    AveragePrecisionEvaluator(y_true='target', y_score='pred', label_type='auto', drop_nulls=True, nan_policy='propagate')
    >>> data = pl.DataFrame({"pred": [2, -1, 0, 3, 1], "target": [1, 0, 0, 1, 1]})
    >>> result = evaluator.evaluate(data)
    >>> result
    AveragePrecisionResult(y_true=(5,), y_score=(5,), label_type='binary', nan_policy='propagate')

    ```
    """

    def __init__(
        self,
        y_true: str,
        y_score: str,
        label_type: str = "auto",
        drop_nulls: bool = True,
        nan_policy: str = "propagate",
    ) -> None:
        super().__init__(drop_nulls=drop_nulls)
        self._y_true = y_true
        self._y_score = y_score

        check_label_type(label_type)
        self._label_type = label_type

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true,
                "y_score": self._y_score,
                "label_type": self._label_type,
                "drop_nulls": self._drop_nulls,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def evaluate(self, data: pl.DataFrame, lazy: bool = True) -> AveragePrecisionResult | Result:
        logger.info(
            f"Evaluating the average precision | label_type={self._label_type!r} | "
            f"y_true={self._y_true!r} | y_score={self._y_score!r} | "
            f"drop_nulls={self._drop_nulls} | nan_policy={self._nan_policy!r}"
        )
        return self._evaluate(data, lazy)

    def _compute_result(self, data: pl.DataFrame) -> AveragePrecisionResult:
        return AveragePrecisionResult(
            y_true=to_array(data[self._y_true]),
            y_score=to_array(data[self._y_score]),
            label_type=self._label_type,
            nan_policy=self._nan_policy,
        )

    def _get_columns(self) -> tuple[str, ...]:
        return (self._y_true, self._y_score)
