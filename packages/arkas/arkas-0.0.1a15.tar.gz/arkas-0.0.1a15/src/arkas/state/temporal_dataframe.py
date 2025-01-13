r"""Implement the temporal DataFrame state."""

from __future__ import annotations

__all__ = ["TemporalDataFrameState"]

import sys
from typing import TYPE_CHECKING, Any

from arkas.state.dataframe import DataFrameState
from arkas.utils.dataframe import check_column_exist

if sys.version_info >= (3, 11):
    pass
else:  # pragma: no cover
    pass

if TYPE_CHECKING:
    import polars as pl

    from arkas.figure.base import BaseFigureConfig


class TemporalDataFrameState(DataFrameState):
    r"""Implement the temporal DataFrame state.

    Args:
        dataframe: The DataFrame.
        temporal_column: The temporal column in the DataFrame.
        period: An optional temporal period e.g. monthly or daily.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.
        figure_config: An optional figure configuration.
        **kwargs: Additional keyword arguments.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.state import TemporalDataFrameState
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
    >>> state = TemporalDataFrameState(frame, temporal_column="datetime")
    >>> state
    TemporalDataFrameState(dataframe=(4, 4), temporal_column='datetime', period=None, nan_policy='propagate', figure_config=MatplotlibFigureConfig())

    ```
    """

    def __init__(
        self,
        dataframe: pl.DataFrame,
        temporal_column: str,
        period: str | None = None,
        nan_policy: str = "propagate",
        figure_config: BaseFigureConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            dataframe=dataframe, nan_policy=nan_policy, figure_config=figure_config, **kwargs
        )

        check_column_exist(dataframe, temporal_column)
        self._temporal_column = temporal_column
        self._period = period

    @property
    def period(self) -> str | None:
        return self._period

    @property
    def temporal_column(self) -> str:
        return self._temporal_column

    def get_args(self) -> dict:
        args = super().get_args()
        return {
            "dataframe": args.pop("dataframe"),
            "temporal_column": self._temporal_column,
            "period": self._period,
        } | args
