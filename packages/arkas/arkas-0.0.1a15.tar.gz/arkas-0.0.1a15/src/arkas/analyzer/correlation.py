r"""Implement an analyzer that analyzes the correlation between two
columns."""

from __future__ import annotations

__all__ = ["CorrelationAnalyzer"]

import logging
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line
from grizz.utils.column import check_column_missing_policy, check_missing_column
from grizz.utils.format import str_shape_diff

from arkas.analyzer.lazy import BaseLazyAnalyzer
from arkas.metric.utils import check_nan_policy
from arkas.output import EmptyOutput
from arkas.output.correlation import CorrelationOutput
from arkas.state.dataframe import DataFrameState

if TYPE_CHECKING:
    import polars as pl

    from arkas.figure import BaseFigureConfig

logger = logging.getLogger(__name__)


class CorrelationAnalyzer(BaseLazyAnalyzer):
    r"""Implement an analyzer that analyzes the correlation between two
    columns.

    Args:
        x: The first column.
        y: The second column.
        drop_nulls: If ``True``, the rows with null values in
            ``x`` or ``y`` columns are dropped.
        missing_policy: The policy on how to handle missing columns.
            The following options are available: ``'ignore'``,
            ``'warn'``, and ``'raise'``. If ``'raise'``, an exception
            is raised if at least one column is missing.
            If ``'warn'``, a warning is raised if at least one column
            is missing and the missing columns are ignored.
            If ``'ignore'``, the missing columns are ignored and
            no warning message appears.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.
        figure_config: The figure configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import CorrelationAnalyzer
    >>> analyzer = CorrelationAnalyzer(x="col1", y="col2")
    >>> analyzer
    CorrelationAnalyzer(x='col1', y='col2', drop_nulls=True, missing_policy='raise', nan_policy='propagate', figure_config=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...         "col2": [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...     },
    ...     schema={"col1": pl.Float64, "col2": pl.Float64, "col3": pl.Float64},
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    CorrelationOutput(
      (state): DataFrameState(dataframe=(7, 2), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(
        self,
        x: str,
        y: str,
        drop_nulls: bool = True,
        missing_policy: str = "raise",
        nan_policy: str = "propagate",
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        self._x = x
        self._y = y
        self._drop_nulls = bool(drop_nulls)

        check_column_missing_policy(missing_policy)
        self._missing_policy = missing_policy

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

        self._figure_config = figure_config

    def __repr__(self) -> str:
        args = repr_mapping_line(self.get_args())
        return f"{self.__class__.__qualname__}({args})"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self.get_args(), other.get_args(), equal_nan=equal_nan)

    def get_args(self) -> dict:
        return {
            "x": self._x,
            "y": self._y,
            "drop_nulls": self._drop_nulls,
            "missing_policy": self._missing_policy,
            "nan_policy": self._nan_policy,
            "figure_config": self._figure_config,
        }

    def _analyze(self, frame: pl.DataFrame) -> CorrelationOutput | EmptyOutput:
        self._check_input_column(frame)
        for col in [self._x, self._y]:
            if col not in frame:
                logger.info(
                    f"Skipping '{self.__class__.__qualname__}.analyze' "
                    f"because the input column {col!r} is missing"
                )
                return EmptyOutput()

        logger.info(f"Analyzing the correlation between {self._x!r} and {self._y!r}...")
        dataframe = self._prepare_data(frame)
        logger.info(str_shape_diff(orig=frame.shape, final=dataframe.shape))
        return CorrelationOutput(
            DataFrameState(
                dataframe=dataframe, nan_policy=self._nan_policy, figure_config=self._figure_config
            )
        )

    def _prepare_data(self, data: pl.DataFrame) -> pl.DataFrame:
        cols = [self._x, self._y]
        data = data.select(cols)
        if self._drop_nulls:
            logger.info(f"Dropping rows that have at least one null value in the columns: {cols}")
            data = data.drop_nulls()
        return data

    def _check_input_column(self, frame: pl.DataFrame) -> None:
        r"""Check if the input column is missing.

        Args:
            frame: The input DataFrame to check.
        """
        check_missing_column(frame, column=self._x, missing_policy=self._missing_policy)
        check_missing_column(frame, column=self._y, missing_policy=self._missing_policy)
