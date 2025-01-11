r"""Implement an analyzer that analyzes the correlation between numeric
columns."""

from __future__ import annotations

__all__ = ["ColumnCorrelationAnalyzer"]

import logging
from typing import TYPE_CHECKING

from grizz.utils.format import str_shape_diff
from polars import selectors as cs

from arkas.analyzer.lazy import BaseInNLazyAnalyzer
from arkas.output import EmptyOutput
from arkas.output.column_correlation import ColumnCorrelationOutput
from arkas.state.target_dataframe import TargetDataFrameState

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

logger = logging.getLogger(__name__)


class ColumnCorrelationAnalyzer(BaseInNLazyAnalyzer):
    r"""Implement an analyzer to analyze the correlation between numeric
    columns.

    Args:
        columns: The columns to analyze. If ``None``, it analyzes all
            the columns.
        exclude_columns: The columns to exclude from the input
            ``columns``. If any column is not found, it will be ignored
            during the filtering process.
        missing_policy: The policy on how to handle missing columns.
            The following options are available: ``'ignore'``,
            ``'warn'``, and ``'raise'``. If ``'raise'``, an exception
            is raised if at least one column is missing.
            If ``'warn'``, a warning is raised if at least one column
            is missing and the missing columns are ignored.
            If ``'ignore'``, the missing columns are ignored and
            no warning message appears.
        sort_key: The key used to sort the correlation table.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import ColumnCorrelationAnalyzer
    >>> analyzer = ColumnCorrelationAnalyzer(target_column="col3")
    >>> analyzer
    ColumnCorrelationAnalyzer(target_column='col3', sort_key='spearman_coeff', columns=None, exclude_columns=(), missing_policy='raise')
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...         "col2": [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...     },
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    ColumnCorrelationOutput(
      (state): TargetDataFrameState(dataframe=(7, 3), target_column='col3', nan_policy='propagate', figure_config=MatplotlibFigureConfig(), sort_key='spearman_coeff')
    )

    ```
    """

    def __init__(
        self,
        target_column: str,
        columns: Sequence[str] | None = None,
        exclude_columns: Sequence[str] = (),
        missing_policy: str = "raise",
        sort_key: str = "spearman_coeff",
    ) -> None:
        super().__init__(
            columns=columns, exclude_columns=exclude_columns, missing_policy=missing_policy
        )
        self._target_column = target_column
        self._sort_key = sort_key

    def find_columns(self, frame: pl.DataFrame) -> tuple[str, ...]:
        columns = list(super().find_columns(frame))
        if self._target_column not in columns:
            columns.append(self._target_column)
        return tuple(columns)

    def get_args(self) -> dict:
        return {
            "target_column": self._target_column,
            "sort_key": self._sort_key,
        } | super().get_args()

    def _analyze(self, frame: pl.DataFrame) -> ColumnCorrelationOutput | EmptyOutput:
        if self._target_column not in frame:
            logger.info(
                f"Skipping '{self.__class__.__qualname__}.analyze' "
                f"because the target column {self._target_column!r} is missing"
            )
            return EmptyOutput()

        logger.info(
            f"Analyzing the correlation between {self._target_column} and {self._columns} | "
            f"sort_key={self._sort_key!r} ..."
        )
        columns = list(self.find_common_columns(frame))
        out = frame.select(cs.by_name(columns) & cs.numeric())
        logger.info(str_shape_diff(orig=frame.shape, final=out.shape))
        return ColumnCorrelationOutput(
            state=TargetDataFrameState(
                dataframe=out, target_column=self._target_column, sort_key=self._sort_key
            )
        )
