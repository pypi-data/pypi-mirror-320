r"""Contain the implementation of a HTML content generator that analyzes
a Series with continuous values."""

from __future__ import annotations

__all__ = ["ContinuousSeriesContentGenerator", "create_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.figure.utils import figure2html
from arkas.plotter.continuous_series import ContinuousSeriesPlotter
from arkas.utils.range import find_range
from arkas.utils.stats import compute_statistics_continuous
from arkas.utils.style import get_tab_number_style

if TYPE_CHECKING:
    from arkas.state.series import SeriesState


logger = logging.getLogger(__name__)


class ContinuousSeriesContentGenerator(BaseSectionContentGenerator):
    r"""Implement a content generator that analyzes a Series with
    continuous values.

    Args:
        state: The state containing the Series to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.content import ContinuousSeriesContentGenerator
    >>> from arkas.state import SeriesState
    >>> content = ContinuousSeriesContentGenerator(
    ...     SeriesState(pl.Series("col1", [1, 2, 3, 4, 5, 6, 7]))
    ... )
    >>> content
    ContinuousSeriesContentGenerator(
      (state): SeriesState(name='col1', values=(7,), figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: SeriesState) -> None:
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
        logger.info(f"Generating the continuous distribution of {self._state.series.name}...")
        figures = ContinuousSeriesPlotter(state=self._state).plot()
        stats = compute_statistics_continuous(self._state.series)
        null_values_pct = (
            f"{100 * stats['num_nulls'] / stats['count']:.2f}" if stats["count"] > 0 else "N/A"
        )
        xmin, xmax = find_range(
            self._state.series.drop_nulls().to_numpy(),
            xmin=self._state.figure_config.get_arg("xmin"),
            xmax=self._state.figure_config.get_arg("xmax"),
        )
        return Template(create_template()).render(
            {
                "column": self._state.series.name,
                "figure": figure2html(figures["continuous_histogram"], close_fig=True),
                "table": create_table(stats),
                "total_values": f"{stats['count']:,}",
                "unique_values": f"{stats['nunique']:,}",
                "null_values": f"{stats['num_nulls']:,}",
                "null_values_pct": null_values_pct,
                "min_value": f"{stats['min']:,}",
                "max_value": f"{stats['max']:,}",
                "xmin": f"{xmin:,}",
                "xmax": f"{xmax:,}",
                "dtype": str(self._state.series.dtype),
            }
        )


def create_template() -> str:
    r"""Return the template of the content.

    Returns:
        The content template.

    Example usage:

    ```pycon

    >>> from arkas.content.continuous_series import create_template
    >>> template = create_template()

    ```
    """
    return """<p>This section analyzes the distribution of continuous values for column <em>{{column}}</em>.</p>
<ul>
  <li> <b>total values:</b> {{total_values}} </li>
  <li> <b>number of unique values:</b> {{unique_values}} </li>
  <li> <b>number of null values:</b> {{null_values}} / {{total_values}} ({{null_values_pct}}%) </li>
  <li> <b>range of values:</b> [{{min_value}}, {{max_value}}] </li>
  <li> <b>data type:</b> <em>{{dtype}}</em> </li>
</ul>

<p>The histogram shows the distribution of values in the range [{{xmin}}, {{xmax}}].</p>
{{figure}}

<details>
    <summary>[show statistics]</summary>
    <p style="margin-top: 1rem;">
    The following table shows some statistics about the distribution for column <em>{{column}}<em>.
    </p>
    {{table}}
</details>
"""


def create_table(stats: dict) -> str:
    r"""Create the HTML code of the table with statistics.

    Args:
        stats: Specifies a dictionary with the statistics.

    Returns:
        The HTML code of the table.

    Example usage:

    ```pycon

    >>> from arkas.content.continuous_series import create_table
    >>> table = create_table(
    ...     stats={
    ...         "count": 101,
    ...         "nunique": 101,
    ...         "num_non_nulls": 101,
    ...         "num_nulls": 0,
    ...         "mean": 50.0,
    ...         "std": 29.15,
    ...         "skewness": 0.0,
    ...         "kurtosis": -1.20,
    ...         "min": 0.0,
    ...         "q001": 0.1,
    ...         "q01": 1.0,
    ...         "q05": 5.0,
    ...         "q10": 10.0,
    ...         "q25": 25.0,
    ...         "median": 50.0,
    ...         "q75": 75.0,
    ...         "q90": 90.0,
    ...         "q95": 95.0,
    ...         "q99": 99.0,
    ...         "q999": 99.9,
    ...         "max": 100.0,
    ...         ">0": 100,
    ...         "<0": 0,
    ...         "=0": 1,
    ...     },
    ... )

    ```
    """
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr><th>stat</th><th>value</th></tr>
    </thead>
    <tbody class="tbody table-group-divider">
        <tr><th>count</th><td {{num_style}}>{{count}}</td></tr>
        <tr><th>mean</th><td {{num_style}}>{{mean}}</td></tr>
        <tr><th>std</th><td {{num_style}}>{{std}}</td></tr>
        <tr><th>skewness</th><td {{num_style}}>{{skewness}}</td></tr>
        <tr><th>kurtosis</th><td {{num_style}}>{{kurtosis}}</td></tr>
        <tr><th>min</th><td {{num_style}}>{{min}}</td></tr>
        <tr><th>quantile 0.1%</th><td {{num_style}}>{{q01}}</td></tr>
        <tr><th>quantile 1%</th><td {{num_style}}>{{q01}}</td></tr>
        <tr><th>quantile 5%</th><td {{num_style}}>{{q05}}</td></tr>
        <tr><th>quantile 10%</th><td {{num_style}}>{{q10}}</td></tr>
        <tr><th>quantile 25%</th><td {{num_style}}>{{q25}}</td></tr>
        <tr><th>median</th><td {{num_style}}>{{median}}</td></tr>
        <tr><th>quantile 75%</th><td {{num_style}}>{{q75}}</td></tr>
        <tr><th>quantile 90%</th><td {{num_style}}>{{q90}}</td></tr>
        <tr><th>quantile 95%</th><td {{num_style}}>{{q95}}</td></tr>
        <tr><th>quantile 99%</th><td {{num_style}}>{{q99}}</td></tr>
        <tr><th>quantile 99.9%</th><td {{num_style}}>{{q99}}</td></tr>
        <tr><th>max</th><td {{num_style}}>{{max}}</td></tr>
        <tr><th>number of zeros</th><td {{num_style}}>{{num_zeros}}</td></tr>
        <tr><th>number of positive values</th><td {{num_style}}>{{num_pos}}</td></tr>
        <tr><th>number of negative values</th><td {{num_style}}>{{num_neg}}</td></tr>
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render(
        {
            "num_style": f'style="{get_tab_number_style()}"',
            "count": f"{stats['count']:,}",
            "mean": f"{stats['mean']:,.4f}",
            "std": f"{stats['std']:,.4f}",
            "skewness": f"{stats['skewness']:,.4f}",
            "kurtosis": f"{stats['kurtosis']:,.4f}",
            "min": f"{stats['min']:,.4f}",
            "q001": f"{stats['q001']:,.4f}",
            "q01": f"{stats['q01']:,.4f}",
            "q05": f"{stats['q05']:,.4f}",
            "q10": f"{stats['q10']:,.4f}",
            "q25": f"{stats['q25']:,.4f}",
            "median": f"{stats['median']:,.4f}",
            "q75": f"{stats['q75']:,.4f}",
            "q90": f"{stats['q90']:,.4f}",
            "q95": f"{stats['q95']:,.4f}",
            "q99": f"{stats['q99']:,.4f}",
            "q999": f"{stats['q999']:,.4f}",
            "max": f"{stats['max']:,.4f}",
            "num_pos": f"{stats['>0']:,}",
            "num_neg": f"{stats['<0']:,}",
            "num_zeros": f"{stats['=0']:,}",
        }
    )
