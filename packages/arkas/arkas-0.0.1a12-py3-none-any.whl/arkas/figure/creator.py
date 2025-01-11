r"""Contain the definition of a figure creator and a registry."""

from __future__ import annotations

__all__ = ["FigureCreatorRegistry"]

from typing import Any, Generic, TypeVar

from coola import objects_are_equal
from coola.utils import str_indent, str_mapping

T = TypeVar("T")


class FigureCreatorRegistry(Generic[T]):
    """Implement figure creator registry.

    Args:
        registry: The initial registry with the figure creators.
    """

    def __init__(self, registry: dict[str, T] | None = None) -> None:
        self._registry = registry or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(\n  {str_indent(str_mapping(self._registry))}\n)"

    def add_creator(self, backend: str, creator: T, exist_ok: bool = False) -> None:
        r"""Add a figure creator for a given backend.

        Args:
            backend: The backend for this test.
            creator: The creator used to test the figure
                of the specified type.
            exist_ok: If ``False``, ``RuntimeError`` is raised if the
                backend already exists. This parameter should be
                set to ``True`` to overwrite the creator for a type.

        Raises:
            RuntimeError: if an creator is already registered for the
                backend and ``exist_ok=False``.

        Example usage:

        ```pycon

        >>> from arkas.figure.creator import FigureCreatorRegistry
        >>> registry = FigureCreatorRegistry()

        ```
        """
        if backend in self._registry and not exist_ok:
            msg = (
                f"A figure creator ({self._registry[backend]}) is already registered for the "
                f"backend {backend!r}. Please use `exist_ok=True` if you want to overwrite the "
                "creator for this backend"
            )
            raise RuntimeError(msg)
        self._registry[backend] = creator

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two registries are equal or not.

        Args:
            other: The other object to compare with.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two objects are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from arkas.figure.creator import FigureCreatorRegistry
        >>> registry = FigureCreatorRegistry()

        ```
        """
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._registry, other._registry, equal_nan=equal_nan)

    def has_creator(self, backend: str) -> bool:
        r"""Indicate if a figure creator is registered for the given
        backend.

        Args:
            backend: The backend to check.

        Returns:
            ``True`` if a figure creator is registered,
                otherwise ``False``.

        Example usage:

        ```pycon

        >>> from arkas.figure.creator import FigureCreatorRegistry
        >>> registry = FigureCreatorRegistry()
        >>> registry.has_creator("missing")
        False

        ```
        """
        return backend in self._registry

    def find_creator(self, backend: str) -> T:
        r"""Find the figure creator associated to a backend.

        Args:
            backend: The backend.

        Returns:
            The figure creator associated to the backend.

        Raises:
            ValueError: if the backend is missing.

        Example usage:

        ```pycon

        >>> from arkas.figure.creator import FigureCreatorRegistry
        >>> registry = FigureCreatorRegistry()

        ```
        """
        creator = self._registry.get(backend, None)
        if creator is not None:
            return creator
        msg = f"Incorrect backend: {backend!r}"
        raise ValueError(msg)
