r"""Contain some functions to validate variables."""

from __future__ import annotations

__all__ = ["check_positive"]


def check_positive(name: str, value: float) -> None:
    r"""Check the value is positive (>=0).

    Args:
        name: The name of the variable.
        value: The value to check.

    Raises:
        ValueError: if the value is not positive.

    Example usage:

    ```pycon

    >>> from arkas.utils.validation import check_positive
    >>> check_positive("var", 1)

    ```
    """
    if value < 0:
        msg = f"Incorrect {name!r}: {value}. The value must be positive"
        raise ValueError(msg)
