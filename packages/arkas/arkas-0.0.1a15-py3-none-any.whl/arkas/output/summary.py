r"""Implement the DataFrame summary output."""

from __future__ import annotations

__all__ = ["SummaryOutput"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.content.summary import SummaryContentGenerator
from arkas.evaluator2.vanilla import Evaluator
from arkas.output.lazy import BaseLazyOutput

if TYPE_CHECKING:
    from arkas.state.dataframe import DataFrameState


class SummaryOutput(BaseLazyOutput):
    r"""Implement the DataFrame summary output.

    Args:
        frame: The DataFrame to analyze.
        top: The number of most frequent values to show.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.output import SummaryOutput
    >>> from arkas.state import DataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...     }
    ... )
    >>> output = SummaryOutput(DataFrameState(frame))
    >>> output
    SummaryOutput(
      (state): DataFrameState(dataframe=(7, 3), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_content_generator()
    SummaryContentGenerator(
      (state): DataFrameState(dataframe=(7, 3), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_evaluator()
    Evaluator(count=0)

    ```
    """

    def __init__(self, state: DataFrameState) -> None:
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

    def _get_content_generator(self) -> SummaryContentGenerator:
        return SummaryContentGenerator(self._state)

    def _get_evaluator(self) -> Evaluator:
        return Evaluator()
