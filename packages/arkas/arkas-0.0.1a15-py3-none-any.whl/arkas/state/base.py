r"""Contain the base class to implement a state."""

from __future__ import annotations

__all__ = ["BaseState"]

import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from coola.equality.comparators import BaseEqualityComparator
from coola.equality.handlers import EqualNanHandler, SameObjectHandler, SameTypeHandler
from coola.equality.testers import EqualityTester

if TYPE_CHECKING:
    from coola.equality import EqualityConfig

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )


class BaseState(ABC):
    r"""Define the base class to implement a state.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.state import AccuracyState
    >>> state = AccuracyState(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_pred=np.array([1, 0, 0, 1, 1]),
    ...     y_true_name="target",
    ...     y_pred_name="pred",
    ... )
    >>> state
    AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')

    ```
    """

    @abstractmethod
    def clone(self, deep: bool = True) -> Self:
        r"""Return a copy of the state.

        Args:
            deep: If ``True``, it returns a deep copy of the state,
                otherwise it returns a shallow copy.

        Returns:
            A copy of the state.

         Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.state import AccuracyState
        >>> state = AccuracyState(
        ...     y_true=np.array([1, 0, 0, 1, 1]),
        ...     y_pred=np.array([1, 0, 0, 1, 1]),
        ...     y_true_name="target",
        ...     y_pred_name="pred",
        ... )
        ... cloned_state = state.clone()

        ```
        """

    @abstractmethod
    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two states are equal or not.

        Args:
            other: The other state to compare.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two states are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.state import AccuracyState
        >>> state1 = AccuracyState(
        ...     y_true=np.array([1, 0, 0, 1, 1]),
        ...     y_pred=np.array([1, 0, 0, 1, 1]),
        ...     y_true_name="target",
        ...     y_pred_name="pred",
        ... )
        >>> state2 = AccuracyState(
        ...     y_true=np.array([1, 0, 0, 1, 1]),
        ...     y_pred=np.array([1, 0, 0, 1, 1]),
        ...     y_true_name="target",
        ...     y_pred_name="pred",
        ... )
        >>> state3 = AccuracyState(
        ...     y_true=np.array([1, 0, 0, 0, 0]),
        ...     y_pred=np.array([1, 0, 0, 1, 1]),
        ...     y_true_name="target",
        ...     y_pred_name="pred",
        ... )
        >>> state1.equal(state2)
        True
        >>> state1.equal(state3)
        False

        ```
        """


class StateEqualityComparator(BaseEqualityComparator[BaseState]):
    r"""Implement an equality comparator for ``BaseState`` objects."""

    def __init__(self) -> None:
        self._handler = SameObjectHandler()
        self._handler.chain(SameTypeHandler()).chain(EqualNanHandler())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def clone(self) -> StateEqualityComparator:
        return self.__class__()

    def equal(self, actual: BaseState, expected: Any, config: EqualityConfig) -> bool:
        return self._handler.handle(actual, expected, config=config)


if not EqualityTester.has_comparator(BaseState):  # pragma: no cover
    EqualityTester.add_comparator(BaseState, StateEqualityComparator())
