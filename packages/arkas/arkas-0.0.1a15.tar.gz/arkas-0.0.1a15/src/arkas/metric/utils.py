r"""Contain utility functions to compute metrics."""

from __future__ import annotations

__all__ = [
    "check_array_ndim",
    "check_label_type",
    "check_nan_policy",
    "check_nan_pred",
    "check_same_shape",
    "check_same_shape_pred",
    "check_same_shape_score",
    "contains_nan",
    "multi_isnan",
    "preprocess_pred",
    "preprocess_pred_multilabel",
    "preprocess_same_shape_arrays",
    "preprocess_score_binary",
    "preprocess_score_multiclass",
    "preprocess_score_multilabel",
]

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


def check_array_ndim(arr: np.ndarray, ndim: int) -> None:
    r"""Check if the number of array dimensions is matching the target
    number of dimensions.

    Args:
        arr: The array to check.
        ndim: The targeted number of array dimensions.

    Raises:
        ValueError: if the number of array dimensions does not match.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import check_array_ndim
    >>> check_array_ndim(np.ones((2, 3)), ndim=2)

    ```
    """
    if arr.ndim != ndim:
        msg = f"Incorrect number of array dimensions: {arr.ndim} (expected: {ndim})"
        raise ValueError(msg)


def check_label_type(label_type: str) -> None:
    r"""Check if the label type value is valid or not.

    Args:
        label_type: The type of labels.
            The valid values are ``'binary'``, ``'multiclass'``,
            ``'multilabel'``, and ``'auto'``.

    Raises:
        ValueError: if an invalid value is passed to ``label_type``.

    Example usage:

    ```pycon

    >>> from arkas.metric.utils import check_label_type
    >>> check_label_type(label_type="binary")

    ```
    """
    if label_type not in {"binary", "multiclass", "multilabel", "auto"}:
        msg = (
            f"Incorrect 'label_type': {label_type}. The supported label types are: "
            f"'binary', 'multiclass', 'multilabel', and 'auto'"
        )
        raise ValueError(msg)


def check_nan_policy(nan_policy: str) -> None:
    r"""Check the NaN policy.

    Args:
        nan_policy: The NaN policy.

    Raises:
        ValueError: if ``nan_policy`` is not ``'omit'``,
            ``'propagate'``, or ``'raise'``.

    Example usage:

    ```pycon

    >>> from arkas.metric.utils import check_nan_policy
    >>> check_nan_policy(nan_policy="omit")

    ```
    """
    if nan_policy not in {"omit", "propagate", "raise"}:
        msg = (
            f"Incorrect 'nan_policy': {nan_policy}. The valid values are: "
            f"'omit', 'propagate', 'raise'"
        )
        raise ValueError(msg)


def check_nan_pred(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    r"""Check if any array elements in ``y_true`` or ``y_pred`` arrays is
    a NaN value.

    Args:
        y_true: The ground truth target labels.
        y_pred: The predicted labels.

    Raises:
        RuntimeError: ``'y_true'`` or ``'y_pred'`` has a NaN value.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import check_nan_pred
    >>> y_true = np.array([1, 0, 0, 1])
    >>> y_pred = np.array([0, 1, 0, 1])
    >>> check_nan_pred(y_true, y_pred)

    ```
    """
    if np.isnan(y_true).any():
        msg = "'y_true' contains at least one NaN value"
        raise RuntimeError(msg)
    if np.isnan(y_pred).any():
        msg = "'y_pred' contains at least one NaN value"
        raise RuntimeError(msg)


def check_same_shape(arrays: Iterable[np.ndarray]) -> None:
    r"""Check if arrays have the same shape.

    Args:
        arrays: The arrays to check.

    Raises:
        RuntimeError: if the arrays have different shapes.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import check_same_shape
    >>> check_same_shape([np.array([1, 0, 0, 1]), np.array([0, 1, 0, 1])])

    ```
    """
    shapes = {arr.shape for arr in arrays}
    if len(shapes) > 1:
        msg = f"arrays have different shapes: {shapes}"
        raise RuntimeError(msg)


def check_same_shape_pred(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    r"""Check if ``y_true`` and ``y_pred`` arrays have the same shape.

    Args:
        y_true: The ground truth target labels.
        y_pred: The predicted labels.

    Raises:
        RuntimeError: ``'y_true'`` and ``'y_pred'`` have different
            shapes.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import check_same_shape_pred
    >>> y_true = np.array([1, 0, 0, 1])
    >>> y_pred = np.array([0, 1, 0, 1])
    >>> check_same_shape_pred(y_true, y_pred)

    ```
    """
    if y_true.shape != y_pred.shape:
        msg = f"'y_true' and 'y_pred' have different shapes: {y_true.shape} vs {y_pred.shape}"
        raise RuntimeError(msg)


def check_same_shape_score(y_true: np.ndarray, y_score: np.ndarray) -> None:
    r"""Check if ``y_true`` and ``y_score`` arrays have the same shape.

    Args:
        y_true: The ground truth target labels.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions.

    Raises:
        RuntimeError: ``'y_true'`` and ``'y_score'`` have different
            shapes.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import check_same_shape_score
    >>> y_true = np.array([1, 0, 0, 1])
    >>> y_score = np.array([0, 1, 0, 1])
    >>> check_same_shape_score(y_true, y_score)

    ```
    """
    if y_true.shape != y_score.shape:
        msg = f"'y_true' and 'y_score' have different shapes: {y_true.shape} vs {y_score.shape}"
        raise RuntimeError(msg)


def contains_nan(arr: np.ndarray, nan_policy: str = "propagate", name: str = "input array") -> bool:
    r"""Indicate if the given array contains at least one NaN value.

    Args:
        arr: The array to check.
        nan_policy: The NaN policy. The valid values are ``'omit'``,
            ``'propagate'``, or ``'raise'``.
        name: An optional name to be more precise about the array when
            the exception is raised.

    Returns:
        ``True`` if the array contains at least one NaN value.

    Raises:
        ValueError: if the array contains at least one NaN value and
            ``nan_policy`` is ``'raise'``.
    """
    check_nan_policy(nan_policy)
    isnan = np.any(np.isnan(arr))
    if isnan and nan_policy == "raise":
        msg = f"{name} contains at least one NaN value"
        raise ValueError(msg)
    return isnan


def multi_isnan(arrays: Sequence[np.ndarray]) -> np.ndarray:
    r"""Test element-wise for NaN for all input arrays and return result
    as a boolean array.

    Args:
        arrays: The input arrays to test. All the arrays must have the
            same shape.

    Returns:
        A boolean array. ``True`` where any array is NaN,
            ``False`` otherwise.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import multi_isnan
    >>> mask = multi_isnan(
    ...     [np.array([1, 0, 0, 1, float("nan")]), np.array([1, float("nan"), 0, 1, 1])]
    ... )
    >>> mask
    array([False,  True, False, False,  True])

    ```
    """
    if len(arrays) == 0:
        msg = "'arrays' cannot be empty"
        raise RuntimeError(msg)
    mask = np.isnan(arrays[0])
    for arr in arrays[1:]:
        mask = np.logical_or(mask, np.isnan(arr))
    return mask


def preprocess_pred(
    y_true: np.ndarray, y_pred: np.ndarray, drop_nan: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    r"""Preprocess ``y_true`` and ``y_pred`` arrays.

    Args:
        y_true: The ground truth target labels.
        y_pred: The predicted labels.
        drop_nan: If ``True``, the NaN values are removed,
            otherwise they are kept.

    Returns:
        A tuple with the preprocessed ``y_true`` and ``y_pred``
            arrays.

    Raises:
        RuntimeError: if an invalid value is passed to ``nan``.
        RuntimeError: ``'y_true'`` and ``'y_pred'`` have different
            shapes.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import preprocess_pred
    >>> y_true = np.array([1, 0, 0, 1, 1, float("nan")])
    >>> y_pred = np.array([0, 1, 0, 1, float("nan"), 1])
    >>> preprocess_pred(y_true, y_pred)
    (array([ 1.,  0.,  0.,  1.,  1., nan]), array([ 0.,  1.,  0.,  1., nan,  1.]))
    >>> preprocess_pred(y_true, y_pred, drop_nan=True)
    (array([1., 0., 0., 1.]), array([0., 1., 0., 1.]))

    ```
    """
    check_same_shape_pred(y_true, y_pred)
    if not drop_nan:
        return y_true, y_pred
    mask = np.logical_not(multi_isnan([y_true, y_pred]))
    return y_true[mask], y_pred[mask]


def preprocess_pred_multilabel(
    y_true: np.ndarray, y_pred: np.ndarray, drop_nan: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    r"""Preprocess ``y_true`` and ``y_pred`` arrays.

    Args:
        y_true: The ground truth target labels.
        y_pred: The predicted labels.
        drop_nan: If ``True``, the NaN values are removed,
            otherwise they are kept.

    Returns:
        A tuple with the preprocessed ``y_true`` and ``y_pred``
            arrays.

    Raises:
        RuntimeError: if an invalid value is passed to ``nan``.
        RuntimeError: ``'y_true'`` and ``'y_pred'`` have different
            shapes.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import preprocess_pred_multilabel
    >>> y_true = np.array([[1, float("nan"), 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]])
    >>> y_pred = np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, float("nan")]])
    >>> preprocess_pred_multilabel(y_true, y_pred)
    (array([[ 1., nan,  1.],
            [ 0.,  1.,  0.],
            [ 0.,  1.,  0.],
            [ 1.,  0.,  1.],
            [ 1.,  0.,  1.]]),
     array([[ 1.,  0.,  1.],
            [ 0.,  1.,  0.],
            [ 0.,  1.,  0.],
            [ 1.,  0.,  1.],
            [ 1.,  0., nan]]))
    >>> preprocess_pred_multilabel(y_true, y_pred, drop_nan=True)
    (array([[0., 1., 0.],
            [0., 1., 0.],
            [1., 0., 1.]]),
     array([[0., 1., 0.],
            [0., 1., 0.],
            [1., 0., 1.]]))

    ```
    """
    if y_true.size == 0 and y_pred.size == 0:
        return np.array([]), np.array([])

    if y_true.ndim == 1:
        y_true = y_true.reshape((-1, 1))
    if y_true.ndim != 2:
        msg = f"'y_true' must be a 1d or 2d array but received an array of shape: {y_true.shape}"
        raise RuntimeError(msg)
    if y_pred.ndim == 1:
        y_pred = y_pred.reshape((-1, 1))
    check_same_shape_pred(y_true, y_pred)
    if not drop_nan:
        return y_true, y_pred

    mask = np.logical_not(np.logical_or(np.isnan(y_true).any(axis=1), np.isnan(y_pred).any(axis=1)))
    return y_true[mask], y_pred[mask]


def preprocess_same_shape_arrays(
    arrays: Sequence[np.ndarray], drop_nan: bool = False
) -> tuple[np.ndarray, ...]:
    r"""Preprocess a sequence of same shape arrays.

    Args:
        arrays: The arrays to preprocess.
        drop_nan: If ``True``, the NaN values are removed,
            otherwise they are kept.

    Returns:
        A tuple with the preprocessed ``y_true`` and ``y_pred``
            arrays.

    Raises:
        RuntimeError: if the arrays have different shapes.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import preprocess_same_shape_arrays
    >>> arrays = [
    ...     np.array([1, 0, 0, 1, 1, float("nan")]),
    ...     np.array([0, 1, 0, 1, float("nan"), 1]),
    ... ]
    >>> preprocess_same_shape_arrays(arrays)
    (array([ 1.,  0.,  0.,  1.,  1., nan]), array([ 0.,  1.,  0.,  1., nan,  1.]))
    >>> preprocess_same_shape_arrays(arrays, drop_nan=True)
    (array([1., 0., 0., 1.]), array([0., 1., 0., 1.]))

    ```
    """
    check_same_shape(arrays)
    if not drop_nan:
        return tuple(arrays)
    mask = np.logical_not(multi_isnan(arrays))
    return tuple(arr[mask] for arr in arrays)


def preprocess_score_binary(
    y_true: np.ndarray, y_score: np.ndarray, drop_nan: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    r"""Preprocess ``y_true`` and ``y_score`` arrays for the binary
    classification case.

    Args:
        y_true: The ground truth target labels. This input must be an
            array of shape ``(n_samples, *)``.
        y_score: The predicted labels. This input must be an
            array of shape ``(n_samples, *)``.
        drop_nan: If ``True``, the NaN values are removed,
            otherwise they are kept.

    Returns:
        A tuple with the preprocessed ``y_true`` and ``y_score``
            arrays.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import preprocess_score_binary
    >>> y_true = np.array([1, 0, 0, 1, 1, float("nan")])
    >>> y_score = np.array([0, 1, 0, 1, float("nan"), 1])
    >>> preprocess_score_binary(y_true, y_score)
    (array([ 1.,  0.,  0.,  1.,  1., nan]), array([ 0.,  1.,  0.,  1., nan,  1.]))
    >>> preprocess_score_binary(y_true, y_score, drop_nan=True)
    (array([1., 0., 0., 1.]), array([0., 1., 0., 1.]))

    ```
    """
    y_true, y_score = y_true.ravel(), y_score.ravel()
    if y_true.size == 0 and y_score.size == 0:
        return y_true, y_score

    check_same_shape_score(y_true, y_score)
    if not drop_nan:
        return y_true, y_score

    # Remove NaN values
    mask = np.logical_not(multi_isnan([y_true, y_score]))
    return y_true[mask], y_score[mask]


def preprocess_score_multiclass(
    y_true: np.ndarray, y_score: np.ndarray, drop_nan: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    r"""Preprocess ``y_true`` and ``y_score`` arrays for the multiclass
    classification case.

    Args:
        y_true: The ground truth target labels. This input must be an
            array of shape ``(n_samples,)`` or ``(n_samples, 1)``.
        y_score: The predicted labels. This input must be an
            array of shape ``(n_samples, n_classes)``.
        drop_nan: If ``True``, the NaN values are removed,
            otherwise they are kept.

    Returns:
        A tuple with the preprocessed ``y_true`` and ``y_score``
            arrays.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import preprocess_score_multiclass
    >>> y_true = np.array([0, 0, 1, 1, 2, float("nan")])
    >>> y_score = np.array(
    ...     [
    ...         [0.7, 0.2, 0.1],
    ...         [0.4, 0.3, 0.3],
    ...         [0.1, 0.8, float("nan")],
    ...         [0.2, 0.3, 0.5],
    ...         [0.4, 0.4, 0.2],
    ...         [0.1, 0.2, 0.7],
    ...     ]
    ... )
    >>> preprocess_score_multiclass(y_true, y_score)
    (array([ 0.,  0.,  1.,  1.,  2., nan]),
     array([[0.7, 0.2, 0.1],
            [0.4, 0.3, 0.3],
            [0.1, 0.8, nan],
            [0.2, 0.3, 0.5],
            [0.4, 0.4, 0.2],
            [0.1, 0.2, 0.7]]))
    >>> preprocess_score_multiclass(y_true, y_score, drop_nan=True)
    (array([0., 0., 1., 2.]),
     array([[0.7, 0.2, 0.1],
            [0.4, 0.3, 0.3],
            [0.2, 0.3, 0.5],
            [0.4, 0.4, 0.2]]))

    ```
    """
    if y_true.size == 0 and y_score.size == 0:
        return np.array([]), np.array([])

    if y_true.size != y_true.shape[0]:
        msg = (
            f"'y_true' must be a an array of shape (n_samples,) or (n_samples, 1) but received: "
            f"{y_true.shape}"
        )
        raise RuntimeError(msg)
    y_true = y_true.ravel()
    if y_true.shape[0] != y_score.shape[0]:
        msg = (
            f"'y_true' and 'y_score' have different first dimension: {y_true.shape} vs "
            f"{y_score.shape}"
        )
        raise RuntimeError(msg)

    if y_score.ndim != 2:
        msg = f"'y_score' must be a 2d array but received an array of shape: {y_score.shape}"
        raise RuntimeError(msg)

    if not drop_nan:
        return y_true, y_score

    # Remove NaN values
    mask = np.logical_not(np.logical_or(np.isnan(y_true), np.isnan(y_score).any(axis=1)))
    return y_true[mask], y_score[mask]


def preprocess_score_multilabel(
    y_true: np.ndarray, y_score: np.ndarray, drop_nan: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    r"""Preprocess ``y_true`` and ``y_score`` arrays for the multilabel
    classification case.

    Args:
        y_true: The ground truth target labels. This input must be an
            array of shape ``(n_samples, n_classes)`` or
            ``(n_samples,)``.
        y_score: The predicted labels. This input must be an
            array of shape ``(n_samples, n_classes)`` or
            ``(n_samples,)``.
        drop_nan: If ``True``, the NaN values are removed,
            otherwise they are kept.

    Returns:
        A tuple with the preprocessed ``y_true`` and ``y_score``
            arrays.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.utils import preprocess_score_multilabel
    >>> y_true = np.array([[1, float("nan"), 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]])
    >>> y_score = np.array(
    ...     [[2, -1, -1], [-1, 1, 2], [0, 2, 3], [3, -2, -4], [1, float("nan"), -5]]
    ... )
    >>> preprocess_score_multilabel(y_true, y_score)
    (array([[ 1., nan,  1.],
            [ 0.,  1.,  0.],
            [ 0.,  1.,  0.],
            [ 1.,  0.,  1.],
            [ 1.,  0.,  1.]]),
     array([[ 2., -1., -1.],
            [-1.,  1.,  2.],
            [ 0.,  2.,  3.],
            [ 3., -2., -4.],
            [ 1., nan, -5.]]))
    >>> preprocess_score_multilabel(y_true, y_score, drop_nan=True)
    (array([[0., 1., 0.],
            [0., 1., 0.],
            [1., 0., 1.]]),
     array([[-1.,  1.,  2.],
            [ 0.,  2.,  3.],
            [ 3., -2., -4.]]))

    ```
    """
    if y_true.size == 0 and y_score.size == 0:
        return np.array([]), np.array([])

    if y_true.ndim == 1:
        y_true = y_true.reshape((-1, 1))
    if y_true.ndim != 2:
        msg = f"'y_true' must be a 1d or 2d array but received an array of shape: {y_true.shape}"
        raise RuntimeError(msg)
    if y_score.ndim == 1:
        y_score = y_score.reshape((-1, 1))
    check_same_shape_score(y_true, y_score)

    if not drop_nan:
        return y_true, y_score

    # Remove NaN values
    mask = np.logical_not(
        np.logical_or(np.isnan(y_true).any(axis=1), np.isnan(y_score).any(axis=1))
    )
    return y_true[mask], y_score[mask]
