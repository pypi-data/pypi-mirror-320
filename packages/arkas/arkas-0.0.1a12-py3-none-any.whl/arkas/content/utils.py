r"""Contain utility functions."""

from __future__ import annotations

__all__ = ["float_to_str", "to_str"]

from typing import Any


def to_str(value: Any) -> str:
    r"""Return a string representation of the input value.

    Args:
        value: The value to encode.

    Returns:
        The string representation of the input value.

    Example usage:

    ```pycon

    >>> from arkas.content.utils import to_str
    >>> to_str(42)
    42

    ```
    """
    if isinstance(value, (int, float)):
        return float_to_str(value)
    return str(value)


def float_to_str(value: float) -> str:
    r"""Return a string representation of the input value.

    Args:
        value: The value to encode.

    Returns:
        The string representation of the input value.

    Example usage:

    ```pycon

    >>> from arkas.content.utils import float_to_str
    >>> float_to_str(42)
    42

    ```
    """
    return f"{value:.4g}"
