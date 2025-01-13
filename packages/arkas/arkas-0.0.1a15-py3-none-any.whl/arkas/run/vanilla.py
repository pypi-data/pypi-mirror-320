r"""Contain a simple implementation to represent a run."""

from __future__ import annotations

__all__ = ["Run"]

from typing import Any

from arkas.run.base import BaseRun


class Run(BaseRun):
    r"""Implement a simple run representation.

    Args:
        uri: The Uniform Resource Identifier (URI) of the run.
        metrics: The metrics associated to the run.
        data: The data associated to the run.
    """

    def __init__(self, uri: str, metrics: dict | None = None, data: dict | None = None) -> None:
        self._uri = uri
        self._metrics = metrics or {}
        self._data = data or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(uri={self.get_uri()})"

    def get_uri(self) -> str:
        return self._uri

    def get_data(self, name: str) -> Any:
        return self._data[name]

    def get_metrics(self) -> dict:
        return self._metrics
