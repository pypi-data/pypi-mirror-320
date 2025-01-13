r"""Implement the average precision metrics."""

from __future__ import annotations

__all__ = [
    "average_precision",
    "binary_average_precision",
    "find_label_type",
    "multiclass_average_precision",
    "multilabel_average_precision",
]


import numpy as np
from sklearn import metrics

from arkas.metric.utils import (
    check_label_type,
    contains_nan,
    preprocess_score_binary,
    preprocess_score_multiclass,
    preprocess_score_multilabel,
)


def average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    label_type: str = "auto",
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the average precision metrics.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.
        label_type: The type of labels used to evaluate the metrics.
            The valid values are: ``'binary'``, ``'multiclass'``,
            and ``'multilabel'``. If ``'binary'`` or ``'multilabel'``,
            ``y_true`` values  must be ``0`` and ``1``.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric import average_precision
    >>> # auto
    >>> metrics = average_precision(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_score=np.array([2, -1, 0, 3, 1])
    ... )
    >>> metrics
    {'average_precision': 1.0, 'count': 5}
    >>> # binary
    >>> metrics = average_precision(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_score=np.array([2, -1, 0, 3, 1]),
    ...     label_type="binary",
    ... )
    >>> metrics
    {'average_precision': 1.0, 'count': 5}
    >>> # multiclass
    >>> metrics = average_precision(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_score=np.array(
    ...         [
    ...             [0.7, 0.2, 0.1],
    ...             [0.4, 0.3, 0.3],
    ...             [0.1, 0.8, 0.1],
    ...             [0.2, 0.3, 0.5],
    ...             [0.4, 0.4, 0.2],
    ...             [0.1, 0.2, 0.7],
    ...         ]
    ...     ),
    ...     label_type="multiclass",
    ... )
    >>> metrics
    {'average_precision': array([0.833..., 0.75 , 0.75 ]),
     'count': 6,
     'macro_average_precision': 0.777...,
     'micro_average_precision': 0.75,
     'weighted_average_precision': 0.777...}
    >>> # multilabel
    >>> metrics = average_precision(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_score=np.array([[2, -1, -1], [-1, 1, 2], [0, 2, 3], [3, -2, -4], [1, -3, -5]]),
    ...     label_type="multilabel",
    ... )
    >>> metrics
    {'average_precision': array([1. , 1. , 0.477...]),
     'count': 5,
     'macro_average_precision': 0.825...,
     'micro_average_precision': 0.588...,
     'weighted_average_precision': 0.804...}

    ```
    """
    check_label_type(label_type)
    if label_type == "auto":
        label_type = find_label_type(y_true=y_true, y_score=y_score)
    if label_type == "binary":
        return binary_average_precision(
            y_true=y_true, y_score=y_score, prefix=prefix, suffix=suffix, nan_policy=nan_policy
        )
    if label_type == "multilabel":
        return multilabel_average_precision(
            y_true=y_true, y_score=y_score, prefix=prefix, suffix=suffix, nan_policy=nan_policy
        )
    return multiclass_average_precision(
        y_true=y_true, y_score=y_score, prefix=prefix, suffix=suffix, nan_policy=nan_policy
    )


def binary_average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the average precision metrics for binary labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, *)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, *)``.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric import binary_average_precision
    >>> metrics = binary_average_precision(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_score=np.array([2, -1, 0, 3, 1])
    ... )
    >>> metrics
    {'average_precision': 1.0, 'count': 5}

    ```
    """
    y_true, y_score = preprocess_score_binary(
        y_true=y_true, y_score=y_score, drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_score_nan = contains_nan(arr=y_score, nan_policy=nan_policy, name="'y_score'")

    count = y_true.size
    ap = float("nan")
    if count > 0 and not y_true_nan and not y_score_nan:
        ap = float(metrics.average_precision_score(y_true=y_true, y_score=y_score))
    return {f"{prefix}average_precision{suffix}": ap, f"{prefix}count{suffix}": count}


def multiclass_average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the average precision metrics for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, n_classes)``.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric import multiclass_average_precision
    >>> metrics = multiclass_average_precision(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_score=np.array(
    ...         [
    ...             [0.7, 0.2, 0.1],
    ...             [0.4, 0.3, 0.3],
    ...             [0.1, 0.8, 0.1],
    ...             [0.2, 0.3, 0.5],
    ...             [0.4, 0.4, 0.2],
    ...             [0.1, 0.2, 0.7],
    ...         ]
    ...     ),
    ... )
    >>> metrics
    {'average_precision': array([0.833..., 0.75 , 0.75 ]),
     'count': 6,
     'macro_average_precision': 0.777...,
     'micro_average_precision': 0.75,
     'weighted_average_precision': 0.777...}

    ```
    """
    y_true, y_score = preprocess_score_multiclass(y_true, y_score, drop_nan=nan_policy == "omit")
    return _average_precision(
        y_true=y_true, y_score=y_score, prefix=prefix, suffix=suffix, nan_policy=nan_policy
    )


def multilabel_average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the average precision metrics for multilabel labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, n_classes)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, n_classes)``.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric import multilabel_average_precision
    >>> metrics = multilabel_average_precision(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_score=np.array([[2, -1, -1], [-1, 1, 2], [0, 2, 3], [3, -2, -4], [1, -3, -5]]),
    ... )
    >>> metrics
    {'average_precision': array([1. , 1. , 0.477...]),
     'count': 5,
     'macro_average_precision': 0.825...,
     'micro_average_precision': 0.588...,
     'weighted_average_precision': 0.804...}

    ```
    """
    y_true, y_score = preprocess_score_multilabel(y_true, y_score, drop_nan=nan_policy == "omit")
    return _average_precision(
        y_true=y_true, y_score=y_score, prefix=prefix, suffix=suffix, nan_policy=nan_policy
    )


def _average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the average precision metrics for multilabel or multiclass
    labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, n_classes)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, n_classes)``.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.
    """
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_score_nan = contains_nan(arr=y_score, nan_policy=nan_policy, name="'y_score'")

    n_samples = y_true.shape[0]
    macro, micro, weighted = float("nan"), float("nan"), float("nan")
    ap = np.array([])
    if n_samples > 0 and not y_true_nan and not y_score_nan:
        macro = metrics.average_precision_score(y_true=y_true, y_score=y_score, average="macro")
        micro = metrics.average_precision_score(y_true=y_true, y_score=y_score, average="micro")
        weighted = metrics.average_precision_score(
            y_true=y_true, y_score=y_score, average="weighted"
        )
        ap = np.asarray(
            metrics.average_precision_score(y_true=y_true, y_score=y_score, average=None)
        ).ravel()

    return {
        f"{prefix}average_precision{suffix}": ap,
        f"{prefix}count{suffix}": n_samples,
        f"{prefix}macro_average_precision{suffix}": float(macro),
        f"{prefix}micro_average_precision{suffix}": float(micro),
        f"{prefix}weighted_average_precision{suffix}": float(weighted),
    }


def find_label_type(y_true: np.ndarray, y_score: np.ndarray) -> str:
    r"""Try to find the label type automatically based on the arrays'
    shape.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.

    Returns:
        The label type.

    Raises:
        RuntimeError: if the label type cannot be found automatically.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.classification.ap import find_label_type
    >>> # binary
    >>> label_type = find_label_type(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_score=np.array([2, -1, 0, 3, 1]),
    ... )
    >>> label_type
    'binary'

    ```
    """
    if y_true.ndim == 1 and y_score.ndim == 2:
        return "multiclass"
    if y_true.ndim == 2 and y_score.ndim == 2:
        return "multilabel"
    if y_true.ndim == 1 and y_score.ndim == 1:
        return "binary"
    msg = "Could not find the label type"
    raise RuntimeError(msg)
