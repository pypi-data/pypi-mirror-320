r"""Contain the base class to implement an evaluator."""

from __future__ import annotations

__all__ = ["BaseEvaluator"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from coola.equality.comparators import BaseEqualityComparator
from coola.equality.handlers import EqualNanHandler, SameObjectHandler, SameTypeHandler
from coola.equality.testers import EqualityTester

if TYPE_CHECKING:
    from coola.equality import EqualityConfig


class BaseEvaluator(ABC):
    r"""Define the base class to implement an evaluator.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.evaluator2 import AccuracyEvaluator
    >>> from arkas.state import AccuracyState
    >>> evaluator = AccuracyEvaluator(
    ...     AccuracyState(
    ...         y_true=np.array([1, 0, 0, 1, 1]),
    ...         y_pred=np.array([1, 0, 0, 1, 1]),
    ...         y_true_name="target",
    ...         y_pred_name="pred",
    ...     )
    ... )
    >>> evaluator
    AccuracyEvaluator(
      (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
    )

    ```
    """

    @abstractmethod
    def compute(self) -> BaseEvaluator:
        r"""Compute the metrics and return a new evaluator.

        Returns:
            A new evaluator with the computed metrics.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.evaluator2 import AccuracyEvaluator
        >>> from arkas.state import AccuracyState
        >>> evaluator = AccuracyEvaluator(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> evaluator2 = evaluator.compute()
        >>> evaluator2
        Evaluator(count=5)

        ```
        """

    @abstractmethod
    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two evaluators are equal or not.

        Args:
            other: The other evaluator to compare.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two evaluators are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.evaluator2 import AccuracyEvaluator
        >>> from arkas.state import AccuracyState
        >>> evaluator1 = AccuracyEvaluator(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> evaluator2 = AccuracyEvaluator(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> evaluator3 = AccuracyEvaluator(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 0, 0]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> evaluator1.equal(evaluator2)
        True
        >>> evaluator1.equal(evaluator3)
        False

        ```
        """

    @abstractmethod
    def evaluate(self, prefix: str = "", suffix: str = "") -> dict:
        r"""Evaluate the metrics.

        Args:
            prefix: The key prefix in the returned dictionary.
            suffix: The key suffix in the returned dictionary.

        Returns:
            The metrics.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.evaluator2 import AccuracyEvaluator
        >>> from arkas.state import AccuracyState
        >>> evaluator = AccuracyEvaluator(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> evaluator.evaluate()
        {'accuracy': 1.0, 'count_correct': 5, 'count_incorrect': 0, 'count': 5, 'error': 0.0}

        ```
        """


class EvaluatorEqualityComparator(BaseEqualityComparator[BaseEvaluator]):
    r"""Implement an equality comparator for ``BaseEvaluator``
    objects."""

    def __init__(self) -> None:
        self._handler = SameObjectHandler()
        self._handler.chain(SameTypeHandler()).chain(EqualNanHandler())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def clone(self) -> EvaluatorEqualityComparator:
        return self.__class__()

    def equal(self, actual: BaseEvaluator, expected: Any, config: EqualityConfig) -> bool:
        return self._handler.handle(actual, expected, config=config)


if not EqualityTester.has_comparator(BaseEvaluator):  # pragma: no cover
    EqualityTester.add_comparator(BaseEvaluator, EvaluatorEqualityComparator())
