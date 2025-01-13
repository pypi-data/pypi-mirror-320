r"""Contain the implementation of a HTML content generator that makes a
2D hexagonal binning plot of data points."""

from __future__ import annotations

__all__ = ["HexbinColumnContentGenerator", "create_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.figure.utils import figure2html
from arkas.plotter.hexbin_column import HexbinColumnPlotter

if TYPE_CHECKING:
    from arkas.state.scatter_dataframe import ScatterDataFrameState


logger = logging.getLogger(__name__)


class HexbinColumnContentGenerator(BaseSectionContentGenerator):
    r"""Implement a content generator that makes a 2D hexagonal binning
    plot of data points.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.content import HexbinColumnContentGenerator
    >>> from arkas.state import ScatterDataFrameState
    >>> dataframe = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [0, 0, 0, 0, 1, 1, 1],
    ...     }
    ... )
    >>> content = HexbinColumnContentGenerator(
    ...     ScatterDataFrameState(dataframe, x="col1", y="col2")
    ... )
    >>> content
    HexbinColumnContentGenerator(
      (state): ScatterDataFrameState(dataframe=(7, 3), x='col1', y='col2', color=None, nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: ScatterDataFrameState) -> None:
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
        logger.info(f"Generating the plot of {ncols:,} columns...")
        figures = HexbinColumnPlotter(state=self._state).plot()
        return Template(create_template()).render(
            {
                "color": self._state.color,
                "figure": figure2html(figures["hexbin_column"], close_fig=True),
                "n_samples": f"{nrows:,}",
                "x": self._state.x,
                "y": self._state.y,
            }
        )


def create_template() -> str:
    r"""Return the template of the content.

    Returns:
        The content template.

    Example usage:

    ```pycon

    >>> from arkas.content.hexbin_column import create_template
    >>> template = create_template()

    ```
    """
    return """This section shows a 2D hexagonal binning plot of data points.
<ul>
  <li> x: {{x}} </li>
  <li> y: {{y}} </li>
  <li> color: {{color}} </li>
  <li> number of samples: {{n_samples}} </li>
</ul>
{{figure}}
"""
