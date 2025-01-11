r"""Implement the pairwise column co-occurrence output."""

from __future__ import annotations

__all__ = ["ColumnCooccurrenceOutput"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.content.column_cooccurrence import ColumnCooccurrenceContentGenerator
from arkas.evaluator2.column_cooccurrence import ColumnCooccurrenceEvaluator
from arkas.output.lazy import BaseLazyOutput
from arkas.plotter.column_cooccurrence import ColumnCooccurrencePlotter

if TYPE_CHECKING:
    from arkas.state.column_cooccurrence import ColumnCooccurrenceState


class ColumnCooccurrenceOutput(BaseLazyOutput):
    r"""Implement the pairwise column co-occurrence output.

    Args:
        state: The state with the co-occurrence matrix.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.output import ColumnCooccurrenceOutput
    >>> from arkas.state import ColumnCooccurrenceState
    >>> output = ColumnCooccurrenceOutput(
    ...     ColumnCooccurrenceState(matrix=np.ones((3, 3)), columns=["a", "b", "c"])
    ... )
    >>> output
    ColumnCooccurrenceOutput(
      (state): ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_content_generator()
    ColumnCooccurrenceContentGenerator(
      (state): ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_evaluator()
    ColumnCooccurrenceEvaluator(
      (state): ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_plotter()
    ColumnCooccurrencePlotter(
      (state): ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: ColumnCooccurrenceState) -> None:
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

    def _get_content_generator(self) -> ColumnCooccurrenceContentGenerator:
        return ColumnCooccurrenceContentGenerator(state=self._state)

    def _get_evaluator(self) -> ColumnCooccurrenceEvaluator:
        return ColumnCooccurrenceEvaluator(state=self._state)

    def _get_plotter(self) -> ColumnCooccurrencePlotter:
        return ColumnCooccurrencePlotter(state=self._state)
