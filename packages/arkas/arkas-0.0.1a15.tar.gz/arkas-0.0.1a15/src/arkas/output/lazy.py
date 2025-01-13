r"""Contain a base class that partially implements the lazy computation
logic."""

from __future__ import annotations

__all__ = ["BaseLazyOutput"]

from abc import abstractmethod
from typing import TYPE_CHECKING

from arkas.output.base import BaseOutput

if TYPE_CHECKING:
    from arkas.content.base import BaseContentGenerator
    from arkas.evaluator2.base import BaseEvaluator
    from arkas.output.vanilla import Output


class BaseLazyOutput(BaseOutput):
    r"""Define a base class that partially implements the lazy
    computation logic."""

    def compute(self) -> Output:
        from arkas.output.vanilla import Output

        return Output(
            content=self.get_content_generator().compute(),
            evaluator=self.get_evaluator().compute(),
        )

    def get_content_generator(self, lazy: bool = True) -> BaseContentGenerator:
        content = self._get_content_generator()
        if not lazy:
            content = content.compute()
        return content

    def get_evaluator(self, lazy: bool = True) -> BaseEvaluator:
        evaluator = self._get_evaluator()
        if not lazy:
            evaluator = evaluator.compute()
        return evaluator

    @abstractmethod
    def _get_content_generator(self) -> BaseContentGenerator:
        r"""Get the content generator associated to the output.

        Returns:
            The content generator.
        """

    @abstractmethod
    def _get_evaluator(self) -> BaseEvaluator:
        r"""Get the evaluator associated to the output.

        Returns:
            The evaluator.
        """
