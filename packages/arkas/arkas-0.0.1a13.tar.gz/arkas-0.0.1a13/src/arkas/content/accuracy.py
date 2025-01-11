r"""Contain the implementation of a HTML content generator that analyzes
accuracy performances."""

from __future__ import annotations

__all__ = ["AccuracyContentGenerator", "create_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.evaluator2.accuracy import AccuracyEvaluator

if TYPE_CHECKING:
    from arkas.state import AccuracyState


logger = logging.getLogger(__name__)


class AccuracyContentGenerator(BaseSectionContentGenerator):
    r"""Implement a HTML content generator that analyzes accuracy
    performances.

    Args:
        state: The state containing the ground truth and predicted
            labels.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.content import AccuracyContentGenerator
    >>> from arkas.state import AccuracyState
    >>> generator = AccuracyContentGenerator(
    ...     state=AccuracyState(
    ...         y_true=np.array([1, 0, 0, 1, 1]),
    ...         y_pred=np.array([1, 0, 0, 1, 1]),
    ...         y_true_name="target",
    ...         y_pred_name="pred",
    ...     )
    ... )
    >>> generator
    AccuracyContentGenerator(
      (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
    )

    ```
    """

    def __init__(self, state: AccuracyState) -> None:
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

    def generate_content(self) -> str:
        logger.info("Generating the accuracy content...")
        metrics = AccuracyEvaluator(self._state).evaluate()
        return Template(create_template()).render(
            {
                "accuracy": f"{metrics.get('accuracy', float('nan')):.4f}",
                "count": f"{metrics.get('count', 0):,}",
                "count_correct": f"{metrics.get('count_correct', 0):,}",
                "count_incorrect": f"{metrics.get('count_incorrect', 0):,}",
                "error": f"{metrics.get('error', float('nan')):.4f}",
                "y_true_name": self._state.y_true_name,
                "y_pred_name": self._state.y_pred_name,
            }
        )


def create_template() -> str:
    r"""Return the template of the content.

    Returns:
        The content template.

    Example usage:

    ```pycon

    >>> from arkas.content.accuracy import create_template
    >>> template = create_template()

    ```
    """
    return """<ul>
  <li><b>accuracy</b>: {{accuracy}} ({{count_correct}}/{{count}})</li>
  <li><b>error</b>: {{error}} ({{count_incorrect}}/{{count}})</li>
  <li><b>number of samples</b>: {{count}}</li>
  <li><b>target label column</b>: {{y_true_name}}</li>
  <li><b>predicted label column</b>: {{y_pred_name}}</li>
</ul>
"""
