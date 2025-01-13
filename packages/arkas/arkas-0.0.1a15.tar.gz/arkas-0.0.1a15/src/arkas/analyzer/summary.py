r"""Implement an analyzer that generates a summary of the DataFrame."""

from __future__ import annotations

__all__ = ["SummaryAnalyzer"]

import logging
from typing import TYPE_CHECKING

from grizz.utils.format import str_shape_diff

from arkas.analyzer.lazy import BaseInNLazyAnalyzer
from arkas.output.summary import SummaryOutput
from arkas.state.dataframe import DataFrameState
from arkas.utils.validation import check_positive

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

logger = logging.getLogger(__name__)


class SummaryAnalyzer(BaseInNLazyAnalyzer):
    r"""Implement an analyzer to show a summary of a DataFrame.

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
        top: The number of most frequent values to show.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import SummaryAnalyzer
    >>> analyzer = SummaryAnalyzer()
    >>> analyzer
    SummaryAnalyzer(columns=None, exclude_columns=(), missing_policy='raise', top=5)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...     },
    ...     schema={"col1": pl.Int64, "col2": pl.Int32, "col3": pl.Float64},
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    SummaryOutput(
      (state): DataFrameState(dataframe=(7, 3), nan_policy='propagate', figure_config=MatplotlibFigureConfig(), top=5)
    )

    ```
    """

    def __init__(
        self,
        columns: Sequence[str] | None = None,
        exclude_columns: Sequence[str] = (),
        missing_policy: str = "raise",
        top: int = 5,
    ) -> None:
        super().__init__(
            columns=columns, exclude_columns=exclude_columns, missing_policy=missing_policy
        )
        check_positive(name="top", value=top)
        self._top = top

    def get_args(self) -> dict:
        return super().get_args() | {"top": self._top}

    def _analyze(self, frame: pl.DataFrame) -> SummaryOutput:
        logger.info(
            f"Analyzing {len(self.find_columns(frame))} columns and generating a summary..."
        )
        columns = self.find_common_columns(frame)
        out = frame.select(columns)
        logger.info(str_shape_diff(orig=frame.shape, final=out.shape))
        return SummaryOutput(DataFrameState(out, top=self._top))
