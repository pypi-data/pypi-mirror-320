r"""Contain the base class to implement an output."""

from __future__ import annotations

__all__ = ["BaseOutput"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from coola.equality.comparators import BaseEqualityComparator
from coola.equality.handlers import EqualNanHandler, SameObjectHandler, SameTypeHandler
from coola.equality.testers import EqualityTester

if TYPE_CHECKING:
    from coola.equality import EqualityConfig

    from arkas.content.base import BaseContentGenerator
    from arkas.evaluator2.base import BaseEvaluator
    from arkas.plotter.base import BasePlotter


class BaseOutput(ABC):
    r"""Define the base class to implement an output.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.output import AccuracyOutput
    >>> from arkas.state import AccuracyState
    >>> output = AccuracyOutput(
    ...     AccuracyState(
    ...         y_true=np.array([1, 0, 0, 1, 1]),
    ...         y_pred=np.array([1, 0, 0, 1, 1]),
    ...         y_true_name="target",
    ...         y_pred_name="pred",
    ...     )
    ... )
    >>> output
    AccuracyOutput(
      (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
    )

    ```
    """

    @abstractmethod
    def compute(self) -> BaseOutput:
        r"""Compute the results and return a new ouptut.

        Returns:
            A new ouptut with the computed results.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.output import AccuracyOutput
        >>> from arkas.state import AccuracyState
        >>> output = AccuracyOutput(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> output
        AccuracyOutput(
          (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
        )
        >>> out = output.compute()
        >>> out
        Output(
          (content): ContentGenerator()
          (evaluator): Evaluator(count=5)
          (plotter): Plotter(count=0)
        )

        ```
        """

    @abstractmethod
    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two outputs are equal or not.

        Args:
            other: The other output to compare.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two outputs are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.output import AccuracyOutput
        >>> from arkas.state import AccuracyState
        >>> output1 = AccuracyOutput(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> output2 = AccuracyOutput(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> output3 = AccuracyOutput(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 0, 0]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> output1.equal(output2)
        True
        >>> output1.equal(output3)
        False

        ```
        """

    @abstractmethod
    def get_content_generator(self, lazy: bool = True) -> BaseContentGenerator:
        r"""Get the HTML content generator associated to the output.

        Args:
            lazy: If ``True``, it forces the computation of the
                content, otherwise it returns a content generator
                object that contains the logic to generate the content.

        Returns:
            The HTML content generator.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.output import AccuracyOutput
        >>> from arkas.state import AccuracyState
        >>> output = AccuracyOutput(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> output.get_content_generator()
        AccuracyContentGenerator(
          (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
        )

        ```
        """

    @abstractmethod
    def get_evaluator(self, lazy: bool = True) -> BaseEvaluator:
        r"""Get the evaluator associated to the output.

        Args:
            lazy: If ``True``, it forces the computation of the
                metrics, otherwise it returns an evaluator object
                that contains the logic to evaluate the metrics.

        Returns:
            The evaluator.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.output import AccuracyOutput
        >>> from arkas.state import AccuracyState
        >>> output = AccuracyOutput(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> output.get_evaluator()
        AccuracyEvaluator(
          (state): AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
        )

        ```
        """

    @abstractmethod
    def get_plotter(self, lazy: bool = True) -> BasePlotter:
        r"""Get the plotter associated to the output.

        Args:
            lazy: If ``True``, it forces the computation of the
                figures, otherwise it returns a plotter object
                that contains the logic to generate the figures.

        Returns:
            The plotter.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.output import AccuracyOutput
        >>> from arkas.state import AccuracyState
        >>> output = AccuracyOutput(
        ...     AccuracyState(
        ...         y_true=np.array([1, 0, 0, 1, 1]),
        ...         y_pred=np.array([1, 0, 0, 1, 1]),
        ...         y_true_name="target",
        ...         y_pred_name="pred",
        ...     )
        ... )
        >>> output.get_plotter()
        Plotter(count=0)

        ```
        """


class OutputEqualityComparator(BaseEqualityComparator[BaseOutput]):
    r"""Implement an equality comparator for ``BaseOutput`` objects."""

    def __init__(self) -> None:
        self._handler = SameObjectHandler()
        self._handler.chain(SameTypeHandler()).chain(EqualNanHandler())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def clone(self) -> OutputEqualityComparator:
        return self.__class__()

    def equal(self, actual: BaseOutput, expected: Any, config: EqualityConfig) -> bool:
        return self._handler.handle(actual, expected, config=config)


if not EqualityTester.has_comparator(BaseOutput):  # pragma: no cover
    EqualityTester.add_comparator(BaseOutput, OutputEqualityComparator())
