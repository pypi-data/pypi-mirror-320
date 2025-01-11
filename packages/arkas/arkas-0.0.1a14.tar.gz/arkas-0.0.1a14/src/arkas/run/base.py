r"""Contain the base class to represent a run."""

from __future__ import annotations

__all__ = ["BaseRun"]

from abc import abstractmethod
from typing import Any


class BaseRun:
    r"""Define the base class to represent a run."""

    @abstractmethod
    def get_uri(self) -> str:
        r"""Get the Uniform Resource Identifier (URI) of the run.

        Returns:
            The Uniform Resource Identifier (URI).
        """

    @abstractmethod
    def get_data(self, name: str) -> Any:
        r"""Get data.

        Args:
            name: The name of the data to get.

        Returns:
            The data associated to the name.
        """

    @abstractmethod
    def get_metrics(self) -> dict:
        r"""Get the metric values.

        Returns:
            The metric values.
        """
