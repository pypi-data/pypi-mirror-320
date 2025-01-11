r"""Implement an analyzer that generates a summary of the DataFrame."""

from __future__ import annotations

__all__ = ["SummaryAnalyzer"]

import logging
from typing import TYPE_CHECKING

from arkas.analyzer.lazy import BaseLazyAnalyzer
from arkas.output.summary import SummaryOutput
from arkas.utils.validation import check_positive

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class SummaryAnalyzer(BaseLazyAnalyzer):
    r"""Implement an analyzer to show a summary of the DataFrame.

    Args:
        top: The number of most frequent values to show.
        sort: If ``True``, sort the columns by alphabetical order.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import SummaryAnalyzer
    >>> analyzer = SummaryAnalyzer()
    >>> analyzer
    SummaryAnalyzer(top=5, sort=False)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 0, 1],
    ...         "col2": [1, 0, 1, 0],
    ...         "col3": [1, 1, 1, 1],
    ...     },
    ...     schema={"col1": pl.Int64, "col2": pl.Int64, "col3": pl.Int64},
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    SummaryOutput(shape=(4, 3), top=5)

    ```
    """

    def __init__(self, top: int = 5, sort: bool = False) -> None:
        check_positive(name="top", value=top)
        self._top = top
        self._sort = bool(sort)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(top={self._top:,}, sort={self._sort})"

    def _analyze(self, frame: pl.DataFrame) -> SummaryOutput:
        logger.info("Analyzing the DataFrame...")
        if self._sort:
            frame = frame.select(sorted(frame.columns))
        return SummaryOutput(frame=frame, top=self._top)
