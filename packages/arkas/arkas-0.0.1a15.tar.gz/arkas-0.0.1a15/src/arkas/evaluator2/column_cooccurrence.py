r"""Implement the pairwise column co-occurrence evaluator."""

from __future__ import annotations

__all__ = ["ColumnCooccurrenceEvaluator"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.evaluator2.base import BaseEvaluator
from arkas.evaluator2.vanilla import Evaluator

if TYPE_CHECKING:
    import numpy as np

    from arkas.state.column_cooccurrence import ColumnCooccurrenceState


class ColumnCooccurrenceEvaluator(BaseEvaluator):
    r"""Implement the pairwise column co-occurrence evaluator.

    Args:
        state: The state with the co-occurrence matrix.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.evaluator2 import ColumnCooccurrenceEvaluator
    >>> from arkas.state import ColumnCooccurrenceState
    >>> evaluator = ColumnCooccurrenceEvaluator(
    ...     ColumnCooccurrenceState(matrix=np.ones((3, 3)), columns=["a", "b", "c"])
    ... )
    >>> evaluator
    ColumnCooccurrenceEvaluator(
      (state): ColumnCooccurrenceState(matrix=(3, 3), figure_config=MatplotlibFigureConfig())
    )
    >>> evaluator.evaluate()
    {'column_cooccurrence': array([[1., 1., 1.],
           [1., 1., 1.],
           [1., 1., 1.]])}

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

    def compute(self) -> Evaluator:
        return Evaluator(metrics=self.evaluate())

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._state.equal(other._state, equal_nan=equal_nan)

    def evaluate(self, prefix: str = "", suffix: str = "") -> dict[str, np.ndarray]:
        return {f"{prefix}column_cooccurrence{suffix}": self._state.matrix}
