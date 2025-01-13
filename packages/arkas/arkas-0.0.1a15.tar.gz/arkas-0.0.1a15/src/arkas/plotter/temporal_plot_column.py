r"""Contain the implementation of a DataFrame column plotter."""

from __future__ import annotations

__all__ = [
    "BaseFigureCreator",
    "MatplotlibFigureCreator",
    "TemporalPlotColumnPlotter",
    "prepare_data",
]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import polars as pl
from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.figure.creator import FigureCreatorRegistry
from arkas.figure.html import HtmlFigure
from arkas.figure.matplotlib import MatplotlibFigure, MatplotlibFigureConfig
from arkas.figure.utils import MISSING_FIGURE_MESSAGE
from arkas.plotter.base import BasePlotter
from arkas.plotter.vanilla import Plotter
from arkas.utils.range import find_range

if TYPE_CHECKING:
    import numpy as np

    from arkas.figure.base import BaseFigure
    from arkas.state.temporal_dataframe import TemporalDataFrameState


class BaseFigureCreator(ABC):
    r"""Define the base class to create a figure with the content of
    each column."""

    @abstractmethod
    def create(self, state: TemporalDataFrameState) -> BaseFigure:
        r"""Create a figure with the content of each column.

        Args:
        state: The state containing the DataFrame to analyze.

        Returns:
            The generated figure.

        Example usage:

        ```pycon

        >>> from datetime import datetime, timezone
        >>> import polars as pl
        >>> from arkas.plotter.temporal_plot_column import MatplotlibFigureCreator
        >>> from arkas.state import TemporalDataFrameState
        >>> creator = MatplotlibFigureCreator()
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
        >>> fig = creator.create(TemporalDataFrameState(frame, temporal_column="datetime"))

        ```
        """


class MatplotlibFigureCreator(BaseFigureCreator):
    r"""Create a matplotlib figure with the content of each column.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.plotter.temporal_plot_column import MatplotlibFigureCreator
    >>> from arkas.state import TemporalDataFrameState
    >>> creator = MatplotlibFigureCreator()
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
    >>> fig = creator.create(TemporalDataFrameState(frame, temporal_column="datetime"))

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def create(self, state: TemporalDataFrameState) -> BaseFigure:
        if state.dataframe.shape[0] == 0:
            return HtmlFigure(MISSING_FIGURE_MESSAGE)

        data, time = prepare_data(
            dataframe=state.dataframe, temporal_column=state.temporal_column, period=state.period
        )

        fig, ax = plt.subplots(**state.figure_config.get_arg("init", {}))
        for col in data:
            ax.plot(time, col.to_numpy(), label=col.name)

        xmin, xmax = find_range(
            time,
            xmin=state.figure_config.get_arg("xmin"),
            xmax=state.figure_config.get_arg("xmax"),
        )
        if xmin < xmax:
            ax.set_xlim(xmin, xmax)
        ax.set_xlabel(state.temporal_column)
        if yscale := state.figure_config.get_arg("yscale"):
            ax.set_yscale(yscale)
        ax.legend()
        fig.tight_layout()
        return MatplotlibFigure(fig)


class TemporalPlotColumnPlotter(BasePlotter):
    r"""Implement a DataFrame column plotter.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.plotter import TemporalPlotColumnPlotter
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
    >>> plotter = TemporalPlotColumnPlotter(
    ...     TemporalDataFrameState(frame, temporal_column="datetime")
    ... )
    >>> plotter
    TemporalPlotColumnPlotter(
      (state): TemporalDataFrameState(dataframe=(4, 4), temporal_column='datetime', period=None, nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    registry = FigureCreatorRegistry[BaseFigureCreator](
        {MatplotlibFigureConfig.backend(): MatplotlibFigureCreator()}
    )

    def __init__(self, state: TemporalDataFrameState) -> None:
        self._state = state

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def __str__(self) -> str:
        args = str_indent(str_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> Plotter:
        return Plotter(self.plot())

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._state.equal(other._state, equal_nan=equal_nan)

    def plot(self, prefix: str = "", suffix: str = "") -> dict:
        figure = self.registry.find_creator(self._state.figure_config.backend()).create(self._state)
        return {f"{prefix}temporal_plot_column{suffix}": figure}


def prepare_data(
    dataframe: pl.DataFrame, temporal_column: str, period: str | None
) -> tuple[pl.DataFrame, np.ndarray]:
    """Prepare the data before to plot them.

    Args:
        dataframe: The DataFrame.
        temporal_column: The temporal column in the DataFrame.
        period: An optional temporal period e.g. monthly or daily.

    Returns:
        The DataFrame to plot and the array with the time steps.

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.plotter.temporal_plot_column import prepare_data
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
    >>> data, time = prepare_data(frame, temporal_column="datetime", period=None)
    >>> data
    shape: (4, 3)
    ┌──────┬──────┬──────┐
    │ col1 ┆ col2 ┆ col3 │
    │ ---  ┆ ---  ┆ ---  │
    │ i64  ┆ i64  ┆ i64  │
    ╞══════╪══════╪══════╡
    │ 0    ┆ 0    ┆ 1    │
    │ 1    ┆ 1    ┆ 0    │
    │ 1    ┆ 0    ┆ 0    │
    │ 0    ┆ 1    ┆ 0    │
    └──────┴──────┴──────┘
    >>> time
    array(['2020-01-03T00:00:00.000000', '2020-02-03T00:00:00.000000',
           '2020-03-03T00:00:00.000000', '2020-04-03T00:00:00.000000'],
          dtype='datetime64[us]')

    ```
    """
    dataframe = dataframe.sort(temporal_column)
    if period:
        dataframe = dataframe.group_by_dynamic(temporal_column, every=period).agg(pl.all().mean())
    time = dataframe[temporal_column].to_numpy()
    return dataframe.drop(temporal_column), time
