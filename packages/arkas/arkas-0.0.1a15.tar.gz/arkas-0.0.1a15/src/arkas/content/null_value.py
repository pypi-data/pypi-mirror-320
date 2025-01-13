r"""Contain the implementation of a HTML content generator that analyzes
the number of null values per column."""

from __future__ import annotations

__all__ = ["NullValueContentGenerator", "create_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.figure.utils import figure2html
from arkas.plotter.null_value import NullValuePlotter

if TYPE_CHECKING:
    import polars as pl

    from arkas.state.null_value import NullValueState

logger = logging.getLogger(__name__)


class NullValueContentGenerator(BaseSectionContentGenerator):
    r"""Implement a content generator that analyzes the number of null
    values per column.

    Args:
        state: The state containing the number of null values per
            column.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.content import NullValueContentGenerator
    >>> from arkas.state import NullValueState
    >>> content = NullValueContentGenerator(
    ...     NullValueState(
    ...         null_count=np.array([0, 1, 2]),
    ...         total_count=np.array([5, 5, 5]),
    ...         columns=["col1", "col2", "col3"],
    ...     )
    ... )
    >>> content
    NullValueContentGenerator(
      (state): NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: NullValueState) -> None:
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
        ncols = len(self._state.columns)
        logger.info(f"Generating the null values bar plot for {ncols:,} columns...")
        figures = NullValuePlotter(state=self._state).plot()
        frame = self._state.to_dataframe()
        return Template(create_template()).render(
            {
                "ncols": f"{ncols:,}",
                "columns": ", ".join(self._state.columns),
                "figure": figure2html(figures["null_values"], close_fig=True),
                "table_alpha": create_table(frame.sort(by="column")),
                "table_sort": create_table(frame.sort(by="null")),
            }
        )


def create_template() -> str:
    r"""Return the template of the content.

    Returns:
        The content template.

    Example usage:

    ```pycon

    >>> from arkas.content.null_value import create_template
    >>> template = create_template()

    ```
    """
    return """This section analyzes the number and proportion of null values for the {{ncols}}
columns: <em>{{columns}}</em>.

<p>The columns are sorted by ascending order of number of null values in the following bar plot.</p>

{{figure}}

<details>
    <summary>[show statistics per column]</summary>

    <p style="margin-top: 1rem;">
    The following tables show the number and proportion of null values for the {{num_columns}}
    columns.
    The background color of the row indicates the proportion of missing values:
    dark blues indicates more missing values than light blues. </p>

    <ul>
      <li> <b>column</b>: is the column name </li>
      <li> <b>null pct</b>: is the percentage of null values in the column </li>
      <li> <b>null count</b>: is the number of null values in the column </li>
      <li> <b>total count</b>: is the total number of values in the column </li>
    </ul>

    <div class="container-fluid">
        <div class="row align-items-start">
            <div class="col align-self-center">
                <p><b>Columns sorted by alphabetical order</b></p>
                {{table_alpha}}
            </div>
            <div class="col">
                <p><b>Columns sorted by ascending order of missing values</b></p>
                {{table_sort}}
            </div>
        </div>
    </div>
</details>
"""


def create_table(frame: pl.DataFrame) -> str:
    r"""Return a HTML code of a table with the temporal distribution of
    null values.

    Args:
        frame: The DataFrame to analyze.

    Returns:
        The HTML code of the table.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.content.null_value import create_table
    >>> frame = pl.DataFrame(
    ...     {"column": ["A", "B", "C"], "null": [0, 1, 2], "total": [4, 4, 4]},
    ...     schema={"column": pl.String, "null": pl.Int64, "total": pl.Int64},
    ... )
    >>> table = create_table(frame)

    ```
    """
    rows = [
        create_table_row(column=column, null_count=null, total_count=total)
        for column, null, total in zip(
            frame["column"],
            frame["null"],
            frame["total"],
        )
    ]
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>column</th>
            <th>null pct</th>
            <th>null count</th>
            <th>total count</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": "\n".join(rows)})


def create_table_row(column: str, null_count: int, total_count: int) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        column: The column name.
        null_count: The number of null values.
        total_count: The total number of rows.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from arkas.content.null_value import create_table_row
    >>> row = create_table_row(column="col", null_count=5, total_count=101)

    ```
    """
    pct = null_count / total_count if total_count > 0 else float("nan")
    pct_color = pct if total_count > 0 else 0
    return Template(
        "<tr>"
        '<th style="background-color: rgba(0, 191, 255, {{null_pct}})">{{column}}</th>'
        "<td {{num_style}}>{{null_pct}}</td>"
        "<td {{num_style}}>{{null_count}}</td>"
        "<td {{num_style}}>{{total_count}}</td>"
        "</tr>"
    ).render(
        {
            "num_style": (
                f'style="text-align: right; background-color: rgba(0, 191, 255, {pct_color})"'
            ),
            "column": column,
            "null_count": f"{null_count:,}",
            "null_pct": f"{pct:.4f}",
            "total_count": f"{total_count:,}",
        }
    )
