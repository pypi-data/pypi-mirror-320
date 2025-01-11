r"""Implement the column co-occurrence state."""

from __future__ import annotations

__all__ = ["ColumnCooccurrenceState"]

import sys
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line
from grizz.utils.cooccurrence import compute_pairwise_cooccurrence

from arkas.figure.utils import get_default_config
from arkas.state.base import BaseState
from arkas.utils.array import check_square_matrix

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np
    import polars as pl

    from arkas.figure.base import BaseFigureConfig


class ColumnCooccurrenceState(BaseState):
    r"""Implement the column co-occurrence state.

    Args:
        matrix: The co-occurrence matrix.
        columns: The column names.
        figure_config: An optional figure configuration.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.state import ColumnCooccurrenceState
    >>> state = ColumnCooccurrenceState(matrix=np.ones((3, 3)), columns=["a", "b", "c"])
    >>> state
    ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())

    ```
    """

    def __init__(
        self,
        matrix: np.ndarray,
        columns: Sequence[str],
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        check_square_matrix(name="matrix", array=matrix)
        if matrix.shape[0] != len(columns):
            msg = (
                f"The number of columns does not match the matrix shape: {len(columns)} "
                f"vs {matrix.shape[0]}"
            )
            raise ValueError(msg)

        self._matrix = matrix
        self._columns = tuple(columns)
        self._figure_config = figure_config or get_default_config()

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "matrix": self._matrix.shape,
                "figure_config": self._figure_config,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    @property
    def matrix(self) -> np.ndarray:
        return self._matrix

    @property
    def columns(self) -> tuple[str, ...]:
        return self._columns

    @property
    def figure_config(self) -> BaseFigureConfig | None:
        return self._figure_config

    def clone(self, deep: bool = True) -> Self:
        return self.__class__(
            matrix=self._matrix.copy() if deep else self._matrix,
            columns=self._columns,
            figure_config=self._figure_config.clone() if deep else self._figure_config,
        )

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.matrix, other.matrix, equal_nan=equal_nan)
            and objects_are_equal(self.columns, other.columns, equal_nan=equal_nan)
            and objects_are_equal(self.figure_config, other.figure_config, equal_nan=equal_nan)
        )

    @classmethod
    def from_dataframe(
        cls,
        frame: pl.DataFrame,
        ignore_self: bool = False,
        figure_config: BaseFigureConfig | None = None,
    ) -> ColumnCooccurrenceState:
        r"""Instantiate a ``ColumnCooccurrenceState`` object from a
        DataFrame.

        Args:
            frame: The DataFrame to analyze.
            ignore_self: If ``True``, the diagonal of the co-occurrence
                matrix (a.k.a. self-co-occurrence) is set to 0.
            figure_config: An optional figure configuration.

        Returns:
            The instantiate state.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.state import ColumnCooccurrenceState
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0, 0, 1, 0],
        ...         "col2": [0, 1, 0, 1, 0, 1, 0],
        ...         "col3": [0, 0, 0, 0, 1, 1, 1],
        ...     }
        ... )
        >>> state = ColumnCooccurrenceState.from_dataframe(frame)
        >>> state
        ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())

        ```
        """
        matrix = compute_pairwise_cooccurrence(frame=frame, ignore_self=ignore_self)
        return cls(matrix=matrix, columns=frame.columns, figure_config=figure_config)
