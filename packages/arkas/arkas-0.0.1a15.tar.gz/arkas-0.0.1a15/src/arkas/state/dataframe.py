r"""Implement the DataFrame state."""

from __future__ import annotations

__all__ = ["DataFrameState"]

from typing import TYPE_CHECKING, Any

from arkas.figure.utils import get_default_config
from arkas.metric.utils import check_nan_policy
from arkas.state.arg import BaseArgState

if TYPE_CHECKING:
    import polars as pl

    from arkas.figure.base import BaseFigureConfig


class DataFrameState(BaseArgState):
    r"""Implement the DataFrame state.

    Args:
        dataframe: The DataFrame.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.
        figure_config: An optional figure configuration.
        **kwargs: Additional keyword arguments.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.state import DataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [0, 0, 0, 0, 1, 1, 1],
    ...     }
    ... )
    >>> state = DataFrameState(frame)
    >>> state
    DataFrameState(dataframe=(7, 3), nan_policy='propagate', figure_config=MatplotlibFigureConfig())

    ```
    """

    def __init__(
        self,
        dataframe: pl.DataFrame,
        nan_policy: str = "propagate",
        figure_config: BaseFigureConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._dataframe = dataframe
        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy
        self._figure_config = figure_config or get_default_config()

    @property
    def dataframe(self) -> pl.DataFrame:
        return self._dataframe

    @property
    def nan_policy(self) -> str:
        return self._nan_policy

    @property
    def figure_config(self) -> BaseFigureConfig | None:
        return self._figure_config

    def get_args(self) -> dict:
        return {
            "dataframe": self._dataframe,
            "nan_policy": self._nan_policy,
            "figure_config": self._figure_config,
        } | super().get_args()
