r"""Implement a pairwise column co-occurrence analyzer."""

from __future__ import annotations

__all__ = ["ColumnCooccurrenceAnalyzer"]

import logging
from typing import TYPE_CHECKING

from grizz.utils.format import str_shape_diff

from arkas.analyzer.lazy import BaseInNLazyAnalyzer
from arkas.output.column_cooccurrence import ColumnCooccurrenceOutput
from arkas.state.column_cooccurrence import ColumnCooccurrenceState

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

    from arkas.figure import BaseFigureConfig

logger = logging.getLogger(__name__)


class ColumnCooccurrenceAnalyzer(BaseInNLazyAnalyzer):
    r"""Implement a pairwise column co-occurrence analyzer.

    Args:
        columns: The columns to analyze. If ``None``, it analyzes all
            the columns.
        exclude_columns: The columns to exclude from the input
            ``columns``. If any column is not found, it will be ignored
            during the filtering process.
        missing_policy: The policy on how to handle missing columns.
            The following options are available: ``'ignore'``,
            ``'warn'``, and ``'raise'``. If ``'raise'``, an exception
            is raised if at least one column is missing.
            If ``'warn'``, a warning is raised if at least one column
            is missing and the missing columns are ignored.
            If ``'ignore'``, the missing columns are ignored and
            no warning message appears.
        ignore_self: If ``True``, the diagonal of the co-occurrence
            matrix (a.k.a. self-co-occurrence) is set to 0.
        figure_config: The figure configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import ColumnCooccurrenceAnalyzer
    >>> analyzer = ColumnCooccurrenceAnalyzer()
    >>> analyzer
    ColumnCooccurrenceAnalyzer(columns=None, exclude_columns=(), missing_policy='raise', ignore_self=False, figure_config=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [0, 0, 0, 0, 1, 1, 1],
    ...     }
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    ColumnCooccurrenceOutput(
      (state): ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(
        self,
        columns: Sequence[str] | None = None,
        exclude_columns: Sequence[str] = (),
        missing_policy: str = "raise",
        ignore_self: bool = False,
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        super().__init__(
            columns=columns,
            exclude_columns=exclude_columns,
            missing_policy=missing_policy,
        )
        self._ignore_self = ignore_self
        self._figure_config = figure_config

    def get_args(self) -> dict:
        return super().get_args() | {
            "ignore_self": self._ignore_self,
            "figure_config": self._figure_config,
        }

    def _analyze(self, frame: pl.DataFrame) -> ColumnCooccurrenceOutput:
        logger.info(
            "Analyzing the pairwise column co-occurrence of "
            f"{len(self.find_columns(frame)):,}..."
        )
        columns = self.find_common_columns(frame)
        out = frame.select(columns)
        logger.info(str_shape_diff(orig=frame.shape, final=out.shape))
        return ColumnCooccurrenceOutput(
            state=ColumnCooccurrenceState.from_dataframe(
                frame=out, ignore_self=self._ignore_self, figure_config=self._figure_config
            )
        )
