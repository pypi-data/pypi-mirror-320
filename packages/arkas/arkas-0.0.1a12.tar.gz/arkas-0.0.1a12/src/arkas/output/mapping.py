r"""Implement a output that combines a mapping of output objects into a
single output object."""

from __future__ import annotations

__all__ = ["OutputDict"]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils import str_indent, str_mapping

from arkas.content.mapping import ContentGeneratorDict
from arkas.evaluator2.mapping import EvaluatorDict
from arkas.output.lazy import BaseLazyOutput
from arkas.plotter.mapping import PlotterDict

if TYPE_CHECKING:
    from collections.abc import Mapping

    from arkas.output.base import BaseOutput


class OutputDict(BaseLazyOutput):
    r"""Implement an output that combines a mapping of output objects
    into a single output object.

    Args:
        outputs: The mapping of output objects to combine.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.output import OutputDict, Output, AccuracyOutput
    >>> from arkas.content import ContentGenerator
    >>> from arkas.evaluator2 import Evaluator
    >>> from arkas.plotter import Plotter
    >>> from arkas.state import AccuracyState
    >>> output = OutputDict(
    ...     {
    ...         "one": Output(
    ...             content=ContentGenerator("meow"), evaluator=Evaluator(), plotter=Plotter()
    ...         ),
    ...         "two": AccuracyOutput(
    ...             AccuracyState(
    ...                 y_true=np.array([1, 0, 0, 1, 1]),
    ...                 y_pred=np.array([1, 0, 0, 1, 1]),
    ...                 y_true_name="target",
    ...                 y_pred_name="pred",
    ...             )
    ...         ),
    ...     }
    ... )
    >>> output
    OutputDict(count=2)
    >>> output.get_content_generator()
    ContentGeneratorDict(
      (one): ContentGenerator()
      (two): AccuracyContentGenerator(
          (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
        )
    )
    >>> output.get_evaluator()
    EvaluatorDict(
      (one): Evaluator(count=0)
      (two): AccuracyEvaluator(
          (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
        )
    )
    >>> output.get_plotter()
    PlotterDict(
      (one): Plotter(count=0)
      (two): Plotter(count=0)
    )

    ```
    """

    def __init__(self, outputs: Mapping[str, BaseOutput]) -> None:
        self._outputs = outputs

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(count={len(self._outputs):,})"

    def __str__(self) -> str:
        args = str_indent(str_mapping(self._outputs))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._outputs, other._outputs, equal_nan=equal_nan)

    def _get_content_generator(self) -> ContentGeneratorDict:
        return ContentGeneratorDict(
            {key: output.get_content_generator() for key, output in self._outputs.items()}
        )

    def _get_evaluator(self) -> EvaluatorDict:
        return EvaluatorDict({key: output.get_evaluator() for key, output in self._outputs.items()})

    def _get_plotter(self) -> PlotterDict:
        return PlotterDict({key: output.get_plotter() for key, output in self._outputs.items()})
