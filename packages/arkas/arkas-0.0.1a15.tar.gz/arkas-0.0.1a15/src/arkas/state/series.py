r"""Implement the Series state."""

from __future__ import annotations

__all__ = ["SeriesState"]

import sys
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line, str_indent, str_mapping

from arkas.figure.utils import get_default_config
from arkas.state.base import BaseState

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )

if TYPE_CHECKING:
    import polars as pl

    from arkas.figure.base import BaseFigureConfig


class SeriesState(BaseState):
    r"""Implement the Series state.

    Args:
        series: The Series.
        figure_config: An optional figure configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.state import SeriesState
    >>> state = SeriesState(pl.Series("col1", [1, 2, 3, 4, 5, 6, 7]))
    >>> state
    SeriesState(name='col1', values=(7,), figure_config=MatplotlibFigureConfig())

    ```
    """

    def __init__(
        self,
        series: pl.Series,
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        self._series = series
        self._figure_config = figure_config or get_default_config()

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "name": self._series.name,
                "values": self._series.shape,
                "figure_config": self._figure_config,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def __str__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "name": self._series.name,
                    "values": self._series.shape,
                    "figure_config": self._figure_config,
                }
            )
        )
        return f"{self.__class__.__qualname__}({args})"

    @property
    def series(self) -> pl.Series:
        return self._series

    @property
    def figure_config(self) -> BaseFigureConfig | None:
        return self._figure_config

    def clone(self, deep: bool = True) -> Self:
        return self.__class__(
            series=self._series.clone() if deep else self._series,
            figure_config=self._figure_config.clone() if deep else self._figure_config,
        )

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self.get_args(), other.get_args(), equal_nan=equal_nan)

    def get_args(self) -> dict:
        return {
            "series": self._series,
            "figure_config": self._figure_config,
        }
