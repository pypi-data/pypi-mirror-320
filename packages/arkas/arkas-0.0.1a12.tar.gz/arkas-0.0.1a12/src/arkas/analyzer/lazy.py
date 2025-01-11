r"""Define a base class to implement lazy analyzers."""

from __future__ import annotations

__all__ = ["BaseInNLazyAnalyzer", "BaseLazyAnalyzer"]

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line
from grizz.utils.column import (
    check_column_missing_policy,
    check_missing_columns,
    find_common_columns,
    find_missing_columns,
)

from arkas.analyzer.base import BaseAnalyzer

if TYPE_CHECKING:
    from collections.abc import Sequence

    import polars as pl

    from arkas.output import BaseOutput

logger = logging.getLogger(__name__)


class BaseLazyAnalyzer(BaseAnalyzer):
    r"""Define a base class to implement a lazy analyzer.

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

    def analyze(self, frame: pl.DataFrame, lazy: bool = True) -> BaseOutput:
        output = self._analyze(frame)
        if not lazy:
            output = output.compute()
        return output

    @abstractmethod
    def _analyze(self, frame: pl.DataFrame) -> BaseOutput:
        r"""Analyze the DataFrame.

        Args:
            frame: The DataFrame to analyze.

        Returns:
            The generated output.
        """


class BaseInNLazyAnalyzer(BaseAnalyzer):
    r"""Define a base class to implement analyzers that analyze
    DataFrames by using multiple input columns.

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
    ) -> None:
        self._columns = tuple(columns) if columns is not None else None
        self._exclude_columns = exclude_columns

        check_column_missing_policy(missing_policy)
        self._missing_policy = missing_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(self.get_args())
        return f"{self.__class__.__qualname__}({args})"

    def analyze(self, frame: pl.DataFrame, lazy: bool = True) -> BaseOutput:
        self._check_input_columns(frame)
        output = self._analyze(frame)
        if not lazy:
            output = output.compute()
        return output

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self.get_args(), other.get_args(), equal_nan=equal_nan)

    def find_columns(self, frame: pl.DataFrame) -> tuple[str, ...]:
        r"""Find the columns to transform.

        Args:
            frame: The input DataFrame. Sometimes the columns to
                transform are found by analyzing the input
                DataFrame.

        Returns:
            The columns to transform.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.analyzer import ColumnCooccurrenceAnalyzer
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0, 0, 1, 0],
        ...         "col2": [0, 1, 0, 1, 0, 1, 0],
        ...         "col3": [0, 0, 0, 0, 1, 1, 1],
        ...     }
        ... )
        >>> analyzer = ColumnCooccurrenceAnalyzer(columns=["col2", "col3"])
        >>> analyzer.find_columns(frame)
        ('col2', 'col3')
        >>> analyzer = ColumnCooccurrenceAnalyzer()
        >>> analyzer.find_columns(frame)
        ('col1', 'col2', 'col3')

        ```
        """
        cols = list(frame.columns if self._columns is None else self._columns)
        [cols.remove(col) for col in self._exclude_columns if col in cols]
        return tuple(cols)

    def find_common_columns(self, frame: pl.DataFrame) -> tuple[str, ...]:
        r"""Find the common columns between the DataFrame columns and the
        input columns.

        Args:
            frame: The input DataFrame. Sometimes the columns to
                transform are found by analyzing the input
                DataFrame.

        Returns:
            The common columns.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.analyzer import ColumnCooccurrenceAnalyzer
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0, 0, 1, 0],
        ...         "col2": [0, 1, 0, 1, 0, 1, 0],
        ...         "col3": [0, 0, 0, 0, 1, 1, 1],
        ...     }
        ... )
        >>> analyzer = ColumnCooccurrenceAnalyzer(columns=["col2", "col3", "col5"])
        >>> analyzer.find_common_columns(frame)
        ('col2', 'col3')
        >>> analyzer = ColumnCooccurrenceAnalyzer()
        >>> analyzer.find_common_columns(frame)
        ('col1', 'col2', 'col3')

        ```
        """
        return find_common_columns(frame, self.find_columns(frame))

    def find_missing_columns(self, frame: pl.DataFrame) -> tuple[str, ...]:
        r"""Find the missing columns.

        Args:
            frame: The input DataFrame. Sometimes the columns to
                transform are found by analyzing the input
                DataFrame.

        Returns:
            The missing columns.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.analyzer import ColumnCooccurrenceAnalyzer
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0, 0, 1, 0],
        ...         "col2": [0, 1, 0, 1, 0, 1, 0],
        ...         "col3": [0, 0, 0, 0, 1, 1, 1],
        ...     }
        ... )
        >>> analyzer = ColumnCooccurrenceAnalyzer(columns=["col2", "col3", "col5"])
        >>> analyzer.find_missing_columns(frame)
        ('col5',)
        >>> analyzer = ColumnCooccurrenceAnalyzer()
        >>> analyzer.find_missing_columns(frame)
        ()

        ```
        """
        return find_missing_columns(frame, self.find_columns(frame))

    def get_args(self) -> dict:
        r"""Get the arguments of the analyzer.

        Returns:
            The arguments.
        """
        return {
            "columns": self._columns,
            "exclude_columns": self._exclude_columns,
            "missing_policy": self._missing_policy,
        }

    def _check_input_columns(self, frame: pl.DataFrame) -> None:
        r"""Check if some input columns are missing.

        Args:
            frame: The input DataFrame to check.
        """
        check_missing_columns(
            frame_or_cols=frame,
            columns=self.find_columns(frame),
            missing_policy=self._missing_policy,
        )

    @abstractmethod
    def _analyze(self, frame: pl.DataFrame) -> BaseOutput:
        r"""Analyze the DataFrame.

        Args:
            frame: The DataFrame to analyze.

        Returns:
            The generated output.
        """
