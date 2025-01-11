r"""Implement a state that contains the number of null values per
columns."""

from __future__ import annotations

__all__ = ["NullValueState"]

import sys
from typing import TYPE_CHECKING, Any

import numpy as np
import polars as pl
from coola import objects_are_equal
from coola.utils.format import repr_mapping_line
from grizz.utils.null import compute_null_count

from arkas.figure import BaseFigureConfig, get_default_config
from arkas.state.base import BaseState

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )

if TYPE_CHECKING:
    from collections.abc import Sequence


class NullValueState(BaseState):
    r"""Implement a state that contains the number of null values per
    columns.

    Args:
        null_count: The array with the number of null values for each column.
        total_count: The total number of values for each column.
        columns: The column names.
        figure_config: An optional figure configuration.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.state import NullValueState
    >>> state = NullValueState(
    ...     null_count=np.array([0, 1, 2]),
    ...     total_count=np.array([5, 5, 5]),
    ...     columns=["col1", "col2", "col3"],
    ... )
    >>> state
    NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())

    ```
    """

    def __init__(
        self,
        null_count: np.ndarray,
        total_count: np.ndarray,
        columns: Sequence[str],
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        self._null_count = null_count.ravel()
        self._total_count = total_count.ravel()
        self._columns = tuple(columns)
        self._figure_config = figure_config or get_default_config()

        if len(self._columns) != self._null_count.shape[0]:
            msg = (
                f"'columns' ({len(self._columns):,}) and 'null_count' "
                f"({self._null_count.shape[0]:,}) do not match"
            )
            raise ValueError(msg)
        if len(self._columns) != self._total_count.shape[0]:
            msg = (
                f"'columns' ({len(self._columns):,}) and 'total_count' "
                f"({self._total_count.shape[0]:,}) do not match"
            )
            raise ValueError(msg)

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "num_columns": self._null_count.shape[0],
                "figure_config": self._figure_config,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    @property
    def columns(self) -> tuple[str, ...]:
        return self._columns

    @property
    def null_count(self) -> np.ndarray:
        return self._null_count

    @property
    def total_count(self) -> np.ndarray:
        return self._total_count

    @property
    def figure_config(self) -> BaseFigureConfig | None:
        return self._figure_config

    def clone(self, deep: bool = True) -> Self:
        return self.__class__(
            null_count=self._null_count.copy() if deep else self._null_count,
            total_count=self._total_count.copy() if deep else self._total_count,
            columns=self._columns,
            figure_config=self._figure_config.clone() if deep else self._figure_config,
        )

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.null_count, other.null_count, equal_nan=equal_nan)
            and objects_are_equal(self.total_count, other.total_count, equal_nan=equal_nan)
            and objects_are_equal(self.columns, other.columns, equal_nan=equal_nan)
            and objects_are_equal(self.figure_config, other.figure_config, equal_nan=equal_nan)
        )

    def to_dataframe(self) -> pl.DataFrame:
        r"""Export the content of the state to a DataFrame.

        Returns:
            The DataFrame.

        ```pycon

        >>> import numpy as np
        >>> from arkas.state import NullValueState
        >>> state = NullValueState(
        ...     null_count=np.array([0, 1, 2]),
        ...     total_count=np.array([5, 5, 5]),
        ...     columns=["col1", "col2", "col3"],
        ... )
        >>> state.to_dataframe()
        shape: (3, 3)
        ┌────────┬──────┬───────┐
        │ column ┆ null ┆ total │
        │ ---    ┆ ---  ┆ ---   │
        │ str    ┆ i64  ┆ i64   │
        ╞════════╪══════╪═══════╡
        │ col1   ┆ 0    ┆ 5     │
        │ col2   ┆ 1    ┆ 5     │
        │ col3   ┆ 2    ┆ 5     │
        └────────┴──────┴───────┘

        ```
        """
        return pl.DataFrame(
            {"column": self._columns, "null": self._null_count, "total": self._total_count},
            schema={"column": pl.String, "null": pl.Int64, "total": pl.Int64},
        )

    @classmethod
    def from_dataframe(
        cls, dataframe: pl.DataFrame, figure_config: BaseFigureConfig | None = None
    ) -> NullValueState:
        r"""Instantiate a ``NullValueState`` object from a DataFrame.

        Args:
            dataframe: The DataFrame.
            figure_config: An optional figure configuration.

        Returns:
            The instantiated ``NullValueState`` object.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.state import NullValueState
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0, 0, 1, None],
        ...         "col2": [0, 1, None, None, 0, 1, 0],
        ...         "col3": [None, 0, 0, 0, None, 1, None],
        ...     }
        ... )
        >>> state = NullValueState.from_dataframe(frame)
        >>> state
        NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())

        ```
        """
        nrows, ncols = dataframe.shape
        return cls(
            columns=list(dataframe.columns),
            null_count=compute_null_count(dataframe),
            total_count=np.full((ncols,), nrows),
            figure_config=figure_config,
        )
