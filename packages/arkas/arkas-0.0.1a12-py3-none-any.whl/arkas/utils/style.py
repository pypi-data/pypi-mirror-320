r"""Contain default styles."""

from __future__ import annotations

__all__ = ["get_tab_number_style"]


def get_tab_number_style() -> str:
    r"""Get the default style for numbers in a HTML table.

    Returns:
        The default style for numbers in a HTML table.

    Example usage:

    ```pycon

    >>> from arkas.utils.style import get_tab_number_style
    >>> style = get_tab_number_style()

    ```
    """
    return "text-align: right; font-variant-numeric: tabular-nums;"
