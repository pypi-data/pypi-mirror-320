import ast
import importlib.metadata
from typing import (
    Any,
    Generator,
    Type,
)

from .visitors import DefaultMatchCaseVisitor


class Plugin:
    name = 'flake8-spm'
    version = importlib.metadata.version('flake8-spm')

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Generator[tuple[int, int, str, Type[Any]], None, None]:
        visitors = [
            DefaultMatchCaseVisitor(),
        ]
        for visitor in visitors:
            visitor.visit(self._tree)
            for line, col in visitor.problems:
                yield line, col, visitor.error_message, type(self)
