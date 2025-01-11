r"""Contain the implementation of a HTML content generator that returns
the pairwise column co-occurrence."""

from __future__ import annotations

__all__ = [
    "ColumnCooccurrenceContentGenerator",
    "create_table",
    "create_table_row",
    "create_table_section",
    "create_template",
]

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.figure.utils import figure2html
from arkas.plotter import ColumnCooccurrencePlotter
from arkas.utils.style import get_tab_number_style

if TYPE_CHECKING:
    from collections.abc import Sequence

    from arkas.state.column_cooccurrence import ColumnCooccurrenceState


logger = logging.getLogger(__name__)


class ColumnCooccurrenceContentGenerator(BaseSectionContentGenerator):
    r"""Implement a content generator that returns pairwise column co-
    occurrence.

    Args:
        state: The state with the co-occurrence matrix.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.content import ColumnCooccurrenceContentGenerator
    >>> from arkas.state import ColumnCooccurrenceState
    >>> content = ColumnCooccurrenceContentGenerator(
    ...     ColumnCooccurrenceState(matrix=np.ones((3, 3)), columns=["a", "b", "c"])
    ... )
    >>> content
    ColumnCooccurrenceContentGenerator(
      (state): ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: ColumnCooccurrenceState) -> None:
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
        logger.info("Generating the DataFrame summary content...")
        figures = ColumnCooccurrencePlotter(self._state).plot()
        columns = self._state.columns
        return Template(create_template()).render(
            {
                "columns": ", ".join([f"{x!r}" for x in columns]),
                "ncols": f"{len(columns):,}",
                "figure": figure2html(figures["column_cooccurrence"], close_fig=True),
                "table": create_table_section(
                    matrix=self._state.matrix,
                    columns=columns,
                ),
            }
        )


def create_template() -> str:
    r"""Return the template of the content.

    Returns:
        The content template.

    Example usage:

    ```pycon

    >>> from arkas.content.summary import create_template
    >>> template = create_template()

    ```
    """
    return """This section shows an analysis of the pairwise column co-occurrence.
{{figure}}
<details>
    <summary>[show {{ncols}} columns]</summary>
    {{columns}}
</details>
<p style="margin-top: 1rem;">
{{table}}
"""


def create_table_section(matrix: np.ndarray, columns: Sequence[str], top: int = 50) -> str:
    r"""Return the HTML code of the table section.

    Args:
        matrix: The co-occurrence matrix.
        columns: The column names.
        top: The number of co-occurrence pairs to show in the table.

    Returns:
        The HTML code of the table section.

    Example usage:

    ```pycon

    >>> from arkas.content.column_cooccurrence import create_table_section
    >>> section = create_table_section(
    ...     matrix=np.array([[5, 7, 1], [0, 6, 3], [8, 2, 4]]), columns=["col1", "col2", "col3"]
    ... )

    ```
    """
    if matrix.shape[0] == 0:
        return "<span>&#9888;</span> No table is generated because the column is empty"

    return Template(
        """<details>
    <summary>[show top-{{top}} pairwise column co-occurrence]</summary><br>
    The following table shows the top-{{top}} pairwise column co-occurrences.
    The co-occurrence matrix is symmetric and only the co-occurrences in the lower triangular matrix are shown.
    <ul>
      <li> <b>rank</b>: is the rank of the co-occurrence </li>
      <li> <b>column 1</b>: represents the first column of the co-occurrence matrix </li>
      <li> <b>column 2</b>: represents the second column of the co-occurrence matrix </li>
      <li> <b>count</b>: is the number of co-occurrences </li>
      <li> <b>percentage</b>: is the percentage of co-occurrences w.r.t. the total number of co-occurrences </li>
    </ul>

    {{table}}
</details>
"""
    ).render({"top": top, "table": create_table(matrix=matrix, columns=columns, top=top)})


def create_table(matrix: np.ndarray, columns: Sequence[str], top: int = 50) -> str:
    r"""Return the HTML code of the table.

    Args:
        matrix: The co-occurrence matrix.
        columns: The column names.
        top: The number of co-occurrence pairs to show in the table.

    Returns:
        The HTML code of the table.

    Example usage:

    ```pycon

    >>> from arkas.content.column_cooccurrence import create_table
    >>> section = create_table(
    ...     matrix=np.array([[5, 7, 1], [0, 6, 3], [8, 2, 4]]), columns=["col1", "col2", "col3"]
    ... )

    ```
    """
    total = np.triu(matrix).sum().item()
    # Fill the lower triangular part with -1 before to sort the occurrences
    half_matrix = np.triu(matrix) - np.tril(np.ones_like(matrix), -1)
    rows, cols = np.unravel_index(np.argsort(half_matrix, axis=None), matrix.shape)
    n = matrix.shape[0]
    m = min(top, int(n * (n + 1) / 2))
    rows, cols = rows[: -m - 1 : -1], cols[: -m - 1 : -1]
    table_rows = []
    for i, (r, c) in enumerate(zip(rows, cols)):
        table_rows.append(
            create_table_row(
                rank=i + 1, col1=columns[r], col2=columns[c], count=matrix[r, c].item(), total=total
            )
        )
    table_rows = "\n".join(table_rows)
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr><th>rank</th><th>column 1</th><th>column 2</th><th>count</th><th>percentage</th></tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": str_indent(table_rows, num_spaces=8)})


def create_table_row(rank: int, col1: str, col2: str, count: int, total: int) -> str:
    r"""Return the HTML code of a table row.

    Args:
        rank: The rank of the pair of columns.
        col1: The first column.
        col2:  The second column.
        count: The number of co-occurrences.
        total: The total number of co-occurrences.

    Returns:
        The table row.

    Example usage:

    ```pycon

    >>> from arkas.content.column_cooccurrence import create_table_row
    >>> row = create_table_row(rank=2, col1="cat", col2="meow", count=42, total=100)

    ```
    """
    pct = 100 * count / total if total > 0 else float("nan")
    return Template(
        "<tr><th>{{rank}}</th>"
        "<td>{{col1}}</td>"
        "<td>{{col2}}</td>"
        "<td {{num_style}}>{{count}}</td>"
        "<td {{num_style}}>{{pct}}</td>"
        "</tr>"
    ).render(
        {
            "num_style": f'style="{get_tab_number_style()}"',
            "rank": rank,
            "col1": col1,
            "col2": col2,
            "count": f"{count:,}",
            "pct": f"{pct:.4f} %",
        }
    )
