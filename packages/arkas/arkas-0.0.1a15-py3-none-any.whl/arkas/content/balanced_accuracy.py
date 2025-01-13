r"""Contain the implementation of a HTML content generator that analyzes
accuracy performances."""

from __future__ import annotations

__all__ = ["BalancedAccuracyContentGenerator", "create_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.content.section import BaseSectionContentGenerator
from arkas.evaluator2.balanced_accuracy import BalancedAccuracyEvaluator

if TYPE_CHECKING:
    from arkas.state import AccuracyState


logger = logging.getLogger(__name__)


class BalancedAccuracyContentGenerator(BaseSectionContentGenerator):
    r"""Implement a HTML content generator that analyzes balanced
    accuracy performances.

    Args:
        state: The data structure containing the states.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.content import BalancedAccuracyContentGenerator
    >>> from arkas.state import AccuracyState
    >>> generator = BalancedAccuracyContentGenerator(
    ...     state=AccuracyState(
    ...         y_true=np.array([1, 0, 0, 1, 1]),
    ...         y_pred=np.array([1, 0, 0, 1, 1]),
    ...         y_true_name="target",
    ...         y_pred_name="pred",
    ...     )
    ... )
    >>> generator
    BalancedAccuracyContentGenerator(
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
        logger.info("Generating the balance accuracy content...")
        metrics = BalancedAccuracyEvaluator(self._state).evaluate()
        return Template(create_template()).render(
            {
                "balanced_accuracy": f"{metrics.get('balanced_accuracy', float('nan')):.4f}",
                "count": f"{metrics.get('count', 0):,}",
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
  <li><b>balanced accuracy</b>: {{balanced_accuracy}}</li>
  <li><b>number of samples</b>: {{count}}</li>
  <li><b>target label column</b>: {{y_true_name}}</li>
  <li><b>predicted label column</b>: {{y_pred_name}}</li>
</ul>
"""
