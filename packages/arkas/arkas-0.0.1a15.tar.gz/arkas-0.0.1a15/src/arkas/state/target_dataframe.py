r"""Implement DataFrame state with a target column."""

from __future__ import annotations

__all__ = ["TargetDataFrameState"]

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


class TargetDataFrameState(DataFrameState):
    r"""Implement a DataFrame state with a target column.

    Args:
        dataframe: The DataFrame.
        target_column: The target column in the DataFrame.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.
        figure_config: An optional figure configuration.
        **kwargs: Additional keyword arguments.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.state import TargetDataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...     },
    ...     schema={"col1": pl.Int64, "col2": pl.Int32, "col3": pl.Float64},
    ... )
    >>> state = TargetDataFrameState(frame, target_column="col3")
    >>> state
    TargetDataFrameState(dataframe=(7, 3), target_column='col3', nan_policy='propagate', figure_config=MatplotlibFigureConfig())

    ```
    """

    def __init__(
        self,
        dataframe: pl.DataFrame,
        target_column: str,
        nan_policy: str = "propagate",
        figure_config: BaseFigureConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            dataframe=dataframe, nan_policy=nan_policy, figure_config=figure_config, **kwargs
        )

        check_column_exist(dataframe, target_column)
        self._target_column = target_column

    @property
    def target_column(self) -> str:
        return self._target_column

    def get_args(self) -> dict:
        args = super().get_args()
        return {
            "dataframe": args.pop("dataframe"),
            "target_column": self._target_column,
        } | args
