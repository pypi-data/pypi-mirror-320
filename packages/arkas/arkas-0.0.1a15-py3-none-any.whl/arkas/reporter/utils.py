r"""Contain utility functions to generate HTML reports."""

from __future__ import annotations

__all__ = ["create_html_report"]

from coola.utils import str_indent


def create_html_report(toc: str, body: str) -> str:
    r"""Create a HTML report.

    Args:
        toc: The table of contents of the report.
        body: The body of the report

    Returns:
        The HTML report.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.reporter.utils import create_html_report
    >>> report = create_html_report(toc="", body="custom HTML with the content of the report")

    ```
    """
    return f"""
<!doctype html>
<html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous>"
    </head>
    <body style="margin: 1.5rem;">
    <div id="toc_container">
    <h2>Table of content</h2>
    {str_indent(toc, num_spaces=4)}
    </div>

    \t{str_indent(body, num_spaces=8)}
    </body>
</html>
"""
