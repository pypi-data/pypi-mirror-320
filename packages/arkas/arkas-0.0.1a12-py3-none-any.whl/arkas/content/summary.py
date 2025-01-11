r"""Contain the implementation of a HTML content generator that returns
a summary of a DataFrame."""

from __future__ import annotations

__all__ = [
    "SummaryContentGenerator",
    "create_table",
    "create_table_row",
    "create_template",
]

import logging
from collections import Counter
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from grizz.utils.count import compute_nunique
from grizz.utils.null import compute_null_count
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.content.utils import to_str
from arkas.utils.style import get_tab_number_style
from arkas.utils.validation import check_positive

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

logger = logging.getLogger(__name__)


class SummaryContentGenerator(BaseSectionContentGenerator):
    r"""Implement a content generator that returns a summary of a
    DataFrame.

    Args:
        frame: The DataFrame to analyze.
        top: The number of most frequent values to show.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.content import SummaryContentGenerator
    >>> content = SummaryContentGenerator(
    ...     frame=pl.DataFrame(
    ...         {
    ...             "col1": [1.2, 4.2, 4.2, 2.2],
    ...             "col2": [1, 1, 1, 1],
    ...             "col3": [1, 2, 2, 2],
    ...         },
    ...         schema={"col1": pl.Float64, "col2": pl.Int64, "col3": pl.Int64},
    ...     )
    ... )
    >>> content
    SummaryContentGenerator(shape=(4, 3), top=5)

    ```
    """

    def __init__(self, frame: pl.DataFrame, top: int = 5) -> None:
        self._frame = frame
        check_positive(name="top", value=top)
        self._top = top

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(shape={self._frame.shape}, top={self._top})"

    @property
    def frame(self) -> pl.DataFrame:
        r"""The DataFrame to analyze."""
        return self._frame

    @property
    def top(self) -> int:
        return self._top

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.top == other.top and objects_are_equal(
            self.frame, other.frame, equal_nan=equal_nan
        )

    def get_columns(self) -> tuple[str, ...]:
        return tuple(self._frame.columns)

    def get_null_count(self) -> tuple[int, ...]:
        return tuple(compute_null_count(self._frame).tolist())

    def get_nunique(self) -> tuple[int, ...]:
        return tuple(compute_nunique(self._frame).tolist())

    def get_dtypes(self) -> tuple[pl.DataType, ...]:
        return tuple(self._frame.schema.dtypes())

    def get_most_frequent_values(self, top: int = 5) -> tuple[tuple[tuple[Any, int], ...], ...]:
        return tuple(tuple(Counter(series.to_list()).most_common(top)) for series in self.frame)

    def generate_content(self) -> str:
        logger.info("Generating the DataFrame summary content...")
        return Template(create_template()).render(
            {
                "table": self._create_table(),
                "nrows": f"{self._frame.shape[0]:,}",
                "ncols": f"{self._frame.shape[1]:,}",
            }
        )

    def _create_table(self) -> str:
        return create_table(
            columns=self.get_columns(),
            null_count=self.get_null_count(),
            nunique=self.get_nunique(),
            dtypes=self.get_dtypes(),
            most_frequent_values=self.get_most_frequent_values(top=self._top),
            total=self._frame.shape[0],
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
    return """This section shows a short summary of each column.

<ul>
  <li> <b>column</b>: are the column names</li>
  <li> <b>types</b>: are the object types for the objects in the column </li>
  <li> <b>null</b>: are the number (and percentage) of null values in the column </li>
  <li> <b>unique</b>: are the number (and percentage) of unique values in the column </li>
</ul>

<p style="margin-top: 1rem;">
<b>General statistics about the DataFrame</b>

<ul>
  <li> number of columns: {{ncols}} </li>
  <li> number of rows: {{nrows}}</li>
</ul>

{{table}}
"""


def create_table(
    columns: Sequence[str],
    null_count: Sequence[int],
    nunique: Sequence[int],
    dtypes: Sequence[pl.DataType],
    most_frequent_values: Sequence[Sequence[tuple[Any, int]]],
    total: int,
) -> str:
    r"""Return a HTML representation of a table with the temporal
    distribution of null values.

    Args:
        columns: The column names.
        null_count: The number of null values for each column.
        nunique: The number of unique values for each column.
        dtypes: The data type for each column.
        most_frequent_values: The most frequent values for each column.
        total: The total number of rows.

    Returns:
        The HTML representation of the table.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.content.summary import create_table
    >>> row = create_table(
    ...     columns=["float", "int", "str"],
    ...     null_count=(1, 0, 2),
    ...     nunique=(5, 2, 4),
    ...     dtypes=(pl.Float64(), pl.Int64(), pl.String()),
    ...     most_frequent_values=(
    ...         ((2.2, 2), (1.2, 1), (4.2, 1), (None, 1), (1.0, 1)),
    ...         ((1, 5), (0, 1)),
    ...         (("B", 2), (None, 2), ("A", 1), ("C", 1)),
    ...     ),
    ...     total=42,
    ... )

    ```
    """
    rows = []
    for (
        column,
        null,
        nuniq,
        dtype,
        mf_values,
    ) in zip(columns, null_count, nunique, dtypes, most_frequent_values):
        rows.append(
            create_table_row(
                column=column,
                null=null,
                dtype=dtype,
                nunique=nuniq,
                most_frequent_values=mf_values,
                total=total,
            )
        )
    rows = "\n".join(rows)
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>column</th>
            <th>types</th>
            <th>null</th>
            <th>unique</th>
            <th>most frequent values</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": rows})


def create_table_row(
    column: str,
    null: int,
    nunique: int,
    dtype: pl.DataType,
    most_frequent_values: Sequence[tuple[Any, int]],
    total: int,
) -> str:
    r"""Create the HTML code of a new table row.

    Args:
        column: The column name.
        null: The number of null values.
        nunique: The number of unique values.
        dtype: The data type of the column.
        most_frequent_values: The most frequent values.
        total: The total number of rows.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.content.summary import create_table_row
    >>> row = create_table_row(
    ...     column="col",
    ...     null=5,
    ...     nunique=42,
    ...     dtype=pl.Float64(),
    ...     most_frequent_values=[("C", 12), ("A", 5), ("B", 4)],
    ...     total=100,
    ... )

    ```
    """
    null = f"{null:,} ({100 * null / total if total else float('nan'):.2f}%)"
    nunique = f"{nunique:,} ({100 * nunique / total if total else float('nan'):.2f}%)"
    most_frequent_values = ", ".join(
        [f"{to_str(val)} ({100 * c / total:.2f}%)" for val, c in most_frequent_values]
    )
    return Template(
        """<tr>
    <th>{{column}}</th>
    <td>{{dtype}}</td>
    <td {{num_style}}>{{null}}</td>
    <td {{num_style}}>{{nunique}}</td>
    <td>{{most_frequent_values}}</td>
</tr>"""
    ).render(
        {
            "num_style": f'style="{get_tab_number_style()}"',
            "column": column,
            "null": null,
            "dtype": dtype,
            "nunique": nunique,
            "most_frequent_values": most_frequent_values,
        }
    )
