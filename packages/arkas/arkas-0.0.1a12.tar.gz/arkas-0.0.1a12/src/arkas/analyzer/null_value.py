r"""Implement an analyzer that plots the content of each column."""

from __future__ import annotations

__all__ = ["NullValueAnalyzer"]

import logging
from typing import TYPE_CHECKING

from grizz.utils.format import str_shape_diff

from arkas.analyzer.lazy import BaseInNLazyAnalyzer
from arkas.output.null_value import NullValueOutput
from arkas.state.null_value import NullValueState

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

    from arkas.figure import BaseFigureConfig

logger = logging.getLogger(__name__)


class NullValueAnalyzer(BaseInNLazyAnalyzer):
    r"""Implement an analyzer that plots the content of each column.

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
        figure_config: The figure configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import NullValueAnalyzer
    >>> analyzer = NullValueAnalyzer()
    >>> analyzer
    NullValueAnalyzer(columns=None, exclude_columns=(), missing_policy='raise', figure_config=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, None],
    ...         "col2": [0, 1, None, None, 0, 1, 0],
    ...         "col3": [None, 0, 0, 0, None, 1, None],
    ...     }
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    NullValueOutput(
      (state): NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(
        self,
        columns: Sequence[str] | None = None,
        exclude_columns: Sequence[str] = (),
        missing_policy: str = "raise",
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        super().__init__(
            columns=columns,
            exclude_columns=exclude_columns,
            missing_policy=missing_policy,
        )
        self._figure_config = figure_config

    def get_args(self) -> dict:
        return super().get_args() | {
            "figure_config": self._figure_config,
        }

    def _analyze(self, frame: pl.DataFrame) -> NullValueOutput:
        logger.info(f"Plotting the content of {len(self.find_columns(frame)):,} columns...")
        columns = self.find_common_columns(frame)
        dataframe = frame.select(columns)
        logger.info(str_shape_diff(orig=frame.shape, final=dataframe.shape))
        return NullValueOutput(
            state=NullValueState.from_dataframe(
                dataframe=dataframe, figure_config=self._figure_config
            )
        )
