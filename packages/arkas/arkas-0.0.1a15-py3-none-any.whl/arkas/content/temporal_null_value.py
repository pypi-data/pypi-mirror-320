r"""Contain the implementation of a HTML content generator that analyzes
the temporal distribution of null values."""

from __future__ import annotations

__all__ = ["TemporalNullValueContentGenerator", "create_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from grizz.utils.null import compute_temporal_null_count
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.figure.utils import figure2html
from arkas.plotter.temporal_null_value import TemporalNullValuePlotter
from arkas.utils.style import get_tab_number_style

if TYPE_CHECKING:
    import polars as pl

    from arkas.state.temporal_dataframe import TemporalDataFrameState


logger = logging.getLogger(__name__)


class TemporalNullValueContentGenerator(BaseSectionContentGenerator):
    r"""Implement a content generator that analyzes the temporal
    distribution of null values.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.content import TemporalNullValueContentGenerator
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
    >>> content = TemporalNullValueContentGenerator(
    ...     TemporalDataFrameState(dataframe, temporal_column="datetime")
    ... )
    >>> content
    TemporalNullValueContentGenerator(
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
        figures = TemporalNullValuePlotter(state=self._state).plot()
        return Template(create_template()).render(
            {
                "nrows": f"{nrows:,}",
                "ncols": f"{ncols:,}",
                "columns": ", ".join(self._state.dataframe.columns),
                "temporal_column": self._state.temporal_column,
                "figure": figure2html(figures["temporal_null_value"], close_fig=True),
                "table": create_table(
                    frame=self._state.dataframe,
                    temporal_column=self._state.temporal_column,
                    period=self._state.period,
                ),
            }
        )


def create_template() -> str:
    r"""Return the template of the content.

    Returns:
        The content template.

    Example usage:

    ```pycon

    >>> from arkas.content.temporal_null_value import create_template
    >>> template = create_template()

    ```
    """
    return """<p>This section analyzes the temporal distribution of null values in all columns.
The column <em>{{temporal_column}}</em> is used as the temporal column.</p>
{{figure}}
<details>
    <summary>[show statistics per temporal period]</summary>
    <p style="margin-top: 1rem;">The following table shows some statistics for each period.</p>
    {{table}}
</details>
"""


def create_table(frame: pl.DataFrame, temporal_column: str, period: str) -> str:
    r"""Create a HTML representation of a table with the temporal
    distribution of null values.

    Args:
        frame: The DataFrame to analyze.
        temporal_column: The temporal column used to analyze the
            temporal distribution.
        period: The temporal period e.g. monthly or daily.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.content.temporal_null_value import create_table
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [None, 1.0, 0.0, 1.0],
    ...         "col2": [None, 1, 0, None],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "col1": pl.Float64,
    ...         "col2": pl.Int64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> table = create_table(frame=frame, temporal_column="datetime", period="1mo")

    ```
    """
    if frame.is_empty():
        return ""

    columns = list(frame.columns)
    columns.remove(temporal_column)
    nulls, totals, labels = compute_temporal_null_count(
        frame=frame, columns=columns, temporal_column=temporal_column, period=period
    )
    rows = []
    for label, null, total in zip(labels, nulls, totals):
        rows.append(create_table_row(label=label, num_nulls=null, total=total))
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>period</th>
            <th>number of null values</th>
            <th>number of non-null values</th>
            <th>total number of values</th>
            <th>percentage of null values</th>
            <th>percentage of non-null values</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": "\n".join(rows), "period": period})


def create_table_row(label: str, num_nulls: int, total: int) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        label: The label of the row.
        num_nulls: The number of null values.
        total: The total number of values.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from arkas.content.temporal_null_value import create_table_row
    >>> row = create_table_row(label="col", num_nulls=5, total=42)

    ```
    """
    num_non_nulls = total - num_nulls
    return Template(
        """<tr>
    <th>{{label}}</th>
    <td {{num_style}}>{{num_nulls}}</td>
    <td {{num_style}}>{{num_non_nulls}}</td>
    <td {{num_style}}>{{total}}</td>
    <td {{num_style}}>{{num_nulls_pct}}</td>
    <td {{num_style}}>{{num_non_nulls_pct}}</td>
</tr>"""
    ).render(
        {
            "num_style": f'style="{get_tab_number_style()}"',
            "label": label,
            "num_nulls": f"{num_nulls:,}",
            "num_non_nulls": f"{num_non_nulls:,}",
            "total": f"{total:,}",
            "num_nulls_pct": f"{100 * num_nulls / total:.2f}%",
            "num_non_nulls_pct": f"{100 * num_non_nulls / total:.2f}%",
        }
    )
