r"""Implement the DataFrame summary output."""

from __future__ import annotations

__all__ = ["SummaryOutput"]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal

from arkas.content.summary import SummaryContentGenerator
from arkas.evaluator2.vanilla import Evaluator
from arkas.output.lazy import BaseLazyOutput
from arkas.plotter.vanilla import Plotter
from arkas.utils.validation import check_positive

if TYPE_CHECKING:
    import polars as pl


class SummaryOutput(BaseLazyOutput):
    r"""Implement the DataFrame summary output.

    Args:
        frame: The DataFrame to analyze.
        top: The number of most frequent values to show.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.output import SummaryOutput
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.2, 4.2, 4.2, 2.2],
    ...         "col2": [1, 1, 1, 1],
    ...         "col3": [1, 2, 2, 2],
    ...     },
    ...     schema={"col1": pl.Float64, "col2": pl.Int64, "col3": pl.Int64},
    ... )
    >>> output = SummaryOutput(frame)
    >>> output
    SummaryOutput(shape=(4, 3), top=5)
    >>> output.get_content_generator()
    SummaryContentGenerator(shape=(4, 3), top=5)
    >>> output.get_evaluator()
    Evaluator(count=0)
    >>> output.get_plotter()
    Plotter(count=0)

    ```
    """

    def __init__(self, frame: pl.DataFrame, top: int = 5) -> None:
        self._frame = frame
        check_positive(name="top", value=top)
        self._top = top

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(shape={self._frame.shape}, top={self._top})"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._top == other._top and objects_are_equal(
            self._frame, other._frame, equal_nan=equal_nan
        )

    def _get_content_generator(self) -> SummaryContentGenerator:
        return SummaryContentGenerator(frame=self._frame, top=self._top)

    def _get_evaluator(self) -> Evaluator:
        return Evaluator()

    def _get_plotter(self) -> Plotter:
        return Plotter()
