r"""Implement an analyzer that plots the content of each column."""

from __future__ import annotations

__all__ = ["TemporalPlotColumnAnalyzer"]

import logging
from typing import TYPE_CHECKING

from grizz.utils.format import str_shape_diff

from arkas.analyzer.lazy import BaseInNLazyAnalyzer
from arkas.output.temporal_plot_column import TemporalPlotColumnOutput
from arkas.state.temporal_dataframe import TemporalDataFrameState

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

    from arkas.figure import BaseFigureConfig

logger = logging.getLogger(__name__)


class TemporalPlotColumnAnalyzer(BaseInNLazyAnalyzer):
    r"""Implement an analyzer that plots the content of each column.

    Args:
        temporal_column: The temporal column in the DataFrame.
        period: An optional temporal period e.g. monthly or daily.
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
        figure_config: The figure configuration.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.analyzer import TemporalPlotColumnAnalyzer
    >>> analyzer = TemporalPlotColumnAnalyzer(temporal_column="datetime")
    >>> analyzer
    TemporalPlotColumnAnalyzer(columns=None, exclude_columns=(), missing_policy='raise', temporal_column='datetime', period=None, figure_config=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0],
    ...         "col2": [0, 1, 0, 1],
    ...         "col3": [1, 0, 0, 0],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "col1": pl.Int64,
    ...         "col2": pl.Int64,
    ...         "col3": pl.Int64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    TemporalPlotColumnOutput(
      (state): TemporalDataFrameState(dataframe=(4, 4), temporal_column='datetime', period=None, nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(
        self,
        temporal_column: str,
        period: str | None = None,
        columns: Sequence[str] | None = None,
        exclude_columns: Sequence[str] = (),
        missing_policy: str = "raise",
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        super().__init__(
            columns=columns,
            exclude_columns=exclude_columns,
            missing_policy=missing_policy,
        )
        self._temporal_column = temporal_column
        self._period = period
        self._figure_config = figure_config

    def get_args(self) -> dict:
        return super().get_args() | {
            "temporal_column": self._temporal_column,
            "period": self._period,
            "figure_config": self._figure_config,
        }

    def _analyze(self, frame: pl.DataFrame) -> TemporalPlotColumnOutput:
        logger.info(
            f"Plotting the content of {len(self.find_columns(frame)):,} columns "
            f"using the temporal column {self._temporal_column!r} and period {self._period!r}..."
        )
        columns = list(self.find_common_columns(frame))
        if self._temporal_column not in columns:
            columns.append(self._temporal_column)
        dataframe = frame.select(columns)
        logger.info(str_shape_diff(orig=frame.shape, final=dataframe.shape))
        return TemporalPlotColumnOutput(
            state=TemporalDataFrameState(
                dataframe=dataframe,
                temporal_column=self._temporal_column,
                period=self._period,
                figure_config=self._figure_config,
            )
        )
