r"""Contain an abstract state to more easily manage arbitrary keyword
arguments."""

from __future__ import annotations

__all__ = ["BaseArgState"]

import copy
import sys
from typing import Any

import numpy as np
import polars as pl
from coola import objects_are_equal
from coola.utils import str_indent, str_mapping
from coola.utils.format import repr_mapping_line

from arkas.state.base import BaseState

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )


class BaseArgState(BaseState):
    r"""Define a base class to manage arbitrary keyword arguments.

    Args:
        **kwargs: Additional keyword arguments.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = kwargs

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                key: val.shape if isinstance(val, (pl.DataFrame, np.ndarray)) else val
                for key, val in self.get_args().items()
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def __str__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    key: val.shape if isinstance(val, (pl.DataFrame, np.ndarray)) else val
                    for key, val in self.get_args().items()
                }
            )
        )
        return f"{self.__class__.__qualname__}({args})"

    def clone(self, deep: bool = True) -> Self:
        args = self.get_args()
        if deep:
            args = copy.deepcopy(args)
        return self.__class__(**args)

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self.get_args(), other.get_args(), equal_nan=equal_nan)

    def get_arg(self, name: str, default: Any = None) -> Any:
        r"""Get a given argument from the state.

        Args:
            name: The argument name to get.
            default: The default value to return if the argument is missing.

        Returns:
            The argument value or the default value.

        Example usage:

        ```pycon

        >>> from datetime import datetime, timezone
        >>> import polars as pl
        >>> from arkas.state import DataFrameState
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0, 0, 1, 0],
        ...         "col2": [0, 1, 0, 1, 0, 1, 0],
        ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        ...     },
        ...     schema={"col1": pl.Int64, "col2": pl.Int32, "col3": pl.Float64},
        ... )
        >>> state = DataFrameState(frame, column="col3")
        >>> state.get_arg("column")
        col3

        ```
        """
        return self._kwargs.get(name, default)

    def get_args(self) -> dict:
        r"""Get a dictionary with all the arguments of the state.

        Returns:
            The dictionary with all the arguments.

        Example usage:

        ```pycon

        >>> from datetime import datetime, timezone
        >>> import polars as pl
        >>> from arkas.state import DataFrameState
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0, 0, 1, 0],
        ...         "col2": [0, 1, 0, 1, 0, 1, 0],
        ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        ...     },
        ...     schema={"col1": pl.Int64, "col2": pl.Int32, "col3": pl.Float64},
        ... )
        >>> state = DataFrameState(frame, column="col3")
        >>> args = state.get_args()

        ```
        """
        return self._kwargs
