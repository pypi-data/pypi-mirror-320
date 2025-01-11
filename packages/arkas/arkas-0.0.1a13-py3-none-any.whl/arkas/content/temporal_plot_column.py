r"""Contain the implementation of a HTML content generator that plots
the content of each column."""

from __future__ import annotations

__all__ = ["TemporalPlotColumnContentGenerator", "create_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.figure.utils import figure2html
from arkas.plotter.temporal_plot_column import TemporalPlotColumnPlotter

if TYPE_CHECKING:
    from arkas.state.temporal_dataframe import TemporalDataFrameState


logger = logging.getLogger(__name__)


class TemporalPlotColumnContentGenerator(BaseSectionContentGenerator):
    r"""Implement a content generator that plots the content of each
    column.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.content import TemporalPlotColumnContentGenerator
    >>> from arkas.state import TemporalDataFrameState
    >>> dataframe = pl.DataFrame(
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
    >>> content = TemporalPlotColumnContentGenerator(
    ...     TemporalDataFrameState(dataframe, temporal_column="datetime")
    ... )
    >>> content
    TemporalPlotColumnContentGenerator(
      (state): TemporalDataFrameState(dataframe=(4, 4), temporal_column='datetime', period=None, nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: TemporalDataFrameState) -> None:
        self._state = state

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def __str__(self) -> str:
        args = str_indent(str_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._state.equal(other._state, equal_nan=equal_nan)

    def generate_content(self) -> str:
        nrows, ncols = self._state.dataframe.shape
        logger.info(
            f"Generating the temporal plot of {ncols} columns using the "
            f"temporal column {self._state.temporal_column!r}..."
        )
        figures = TemporalPlotColumnPlotter(state=self._state).plot()
        return Template(create_template()).render(
            {
                "nrows": f"{nrows:,}",
                "ncols": f"{ncols:,}",
                "columns": ", ".join(self._state.dataframe.columns),
                "figure": figure2html(figures["temporal_plot_column"], close_fig=True),
            }
        )


def create_template() -> str:
    r"""Return the template of the content.

    Returns:
        The content template.

    Example usage:

    ```pycon

    >>> from arkas.content.temporal_plot_column import create_template
    >>> template = create_template()

    ```
    """
    return """This section plots the content of some columns.
The x-axis is the row index and the y-axis shows the value.
<ul>
  <li> {{ncols}} columns: {{columns}} </li>
  <li> number of rows: {{nrows}}</li>
</ul>
{{figure}}
"""
