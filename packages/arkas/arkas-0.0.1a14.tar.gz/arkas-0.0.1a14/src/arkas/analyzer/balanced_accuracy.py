r"""Contain the balanced accuracy analyzer."""

from __future__ import annotations

__all__ = ["BalancedAccuracyAnalyzer"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_mapping_line

from arkas.analyzer.columns import BaseTruePredAnalyzer
from arkas.metric.utils import check_nan_policy
from arkas.output.balanced_accuracy import BalancedAccuracyOutput
from arkas.state.accuracy import AccuracyState
from arkas.utils.array import to_array

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class BalancedAccuracyAnalyzer(BaseTruePredAnalyzer):
    r"""Implement the balanced accuracy analyzer.

    Args:
        y_true: The column name of the ground truth target
            labels.
        y_pred: The column name of the predicted labels.
        drop_nulls: If ``True``, the rows with null values in
            ``y_true`` or ``y_pred`` columns are dropped.
        missing_policy: The policy on how to handle missing columns.
            The following options are available: ``'ignore'``,
            ``'warn'``, and ``'raise'``. If ``'raise'``, an exception
            is raised if at least one column is missing.
            If ``'warn'``, a warning is raised if at least one column
            is missing and the missing columns are ignored.
            If ``'ignore'``, the missing columns are ignored and
            no warning message appears.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import BalancedAccuracyAnalyzer
    >>> analyzer = BalancedAccuracyAnalyzer(y_true="target", y_pred="pred")
    >>> analyzer
    BalancedAccuracyAnalyzer(y_true='target', y_pred='pred', drop_nulls=True, missing_policy='raise', nan_policy='propagate')
    >>> frame = pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
    >>> output = analyzer.analyze(frame)
    >>> output
    BalancedAccuracyOutput(
      (state): AccuracyState(y_true=(6,), y_pred=(6,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
    )

    ```
    """

    def __init__(
        self,
        y_true: str,
        y_pred: str,
        drop_nulls: bool = True,
        missing_policy: str = "raise",
        nan_policy: str = "propagate",
    ) -> None:
        super().__init__(
            y_true=y_true, y_pred=y_pred, drop_nulls=drop_nulls, missing_policy=missing_policy
        )
        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true,
                "y_pred": self._y_pred,
                "drop_nulls": self._drop_nulls,
                "missing_policy": self._missing_policy,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def _analyze(self, frame: pl.DataFrame) -> BalancedAccuracyOutput:
        logger.info(
            f"Evaluating the balanced accuracy | y_true={self._y_true!r} | "
            f"y_pred={self._y_pred!r} | drop_nulls={self._drop_nulls} | "
            f"nan_policy={self._nan_policy!r}"
        )
        return BalancedAccuracyOutput(
            state=AccuracyState(
                y_true=to_array(frame[self._y_true]).ravel(),
                y_pred=to_array(frame[self._y_pred]).ravel(),
                y_true_name=self._y_true,
                y_pred_name=self._y_pred,
                nan_policy=self._nan_policy,
            ),
        )
