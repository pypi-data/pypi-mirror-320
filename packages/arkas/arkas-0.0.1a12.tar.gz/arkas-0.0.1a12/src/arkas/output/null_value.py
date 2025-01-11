r"""Implement an output to analyze the number of null values per
column."""

from __future__ import annotations

__all__ = ["NullValueOutput"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.content.null_value import NullValueContentGenerator
from arkas.evaluator2.vanilla import Evaluator
from arkas.output.lazy import BaseLazyOutput
from arkas.plotter.null_value import NullValuePlotter

if TYPE_CHECKING:
    from arkas.state.null_value import NullValueState


class NullValueOutput(BaseLazyOutput):
    r"""Implement an output to analyze the number of null values per
    column.

    Args:
        state: The state containing the number of null values per
            column.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.output import NullValueOutput
    >>> from arkas.state import NullValueState
    >>> output = NullValueOutput(
    ...     NullValueState(
    ...         null_count=np.array([0, 1, 2]),
    ...         total_count=np.array([5, 5, 5]),
    ...         columns=["col1", "col2", "col3"],
    ...     )
    ... )
    >>> output
    NullValueOutput(
      (state): NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_content_generator()
    NullValueContentGenerator(
      (state): NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_evaluator()
    Evaluator(count=0)
    >>> output.get_plotter()
    NullValuePlotter(
      (state): NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: NullValueState) -> None:
        self._state = state

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def __str__(self) -> str:
        args = str_indent(str_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._state.equal(other._state, equal_nan=equal_nan)

    def _get_content_generator(self) -> NullValueContentGenerator:
        return NullValueContentGenerator(self._state)

    def _get_evaluator(self) -> Evaluator:
        return Evaluator()

    def _get_plotter(self) -> NullValuePlotter:
        return NullValuePlotter(self._state)
