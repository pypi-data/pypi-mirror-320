r"""Implement the DataFrame state for scatter plots."""

from __future__ import annotations

__all__ = ["ScatterDataFrameState"]

import sys
from typing import TYPE_CHECKING, Any

from arkas.state.dataframe import DataFrameState
from arkas.utils.dataframe import check_column_exist

if sys.version_info >= (3, 11):
    pass
else:  # pragma: no cover
    pass

if TYPE_CHECKING:
    import polars as pl

    from arkas.figure.base import BaseFigureConfig


class ScatterDataFrameState(DataFrameState):
    r"""Implement the DataFrame state for scatter plots.

    Args:
        dataframe: The DataFrame.
        x: The x-axis data column.
        y: The y-axis data column.
        color: An optional color axis data column.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.
        figure_config: An optional figure configuration.
        **kwargs: Additional keyword arguments.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.state import ScatterDataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [0, 0, 0, 0, 1, 1, 1],
    ...     }
    ... )
    >>> state = ScatterDataFrameState(frame, x="col1", y="col2")
    >>> state
    ScatterDataFrameState(dataframe=(7, 3), x='col1', y='col2', color=None, nan_policy='propagate', figure_config=MatplotlibFigureConfig())

    ```
    """

    def __init__(
        self,
        dataframe: pl.DataFrame,
        x: str,
        y: str,
        color: str | None = None,
        nan_policy: str = "propagate",
        figure_config: BaseFigureConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            dataframe=dataframe, nan_policy=nan_policy, figure_config=figure_config, **kwargs
        )

        check_column_exist(dataframe, x)
        check_column_exist(dataframe, y)
        if color is not None:
            check_column_exist(dataframe, color)
        self._x = x
        self._y = y
        self._color = color

    @property
    def x(self) -> str:
        return self._x

    @property
    def y(self) -> str:
        return self._y

    @property
    def color(self) -> str | None:
        return self._color

    def get_args(self) -> dict:
        args = super().get_args()
        return {
            "dataframe": args.pop("dataframe"),
            "x": self._x,
            "y": self._y,
            "color": self._color,
        } | args
