from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, Self, TypeVar, override

from codegen.utils.codemod.codemod_writer_decorators import noapidoc
from graph_sitter.codebase.resolution_stack import ResolutionStack
from graph_sitter.core.expressions import Name
from graph_sitter.extensions.autocommit import reader

if TYPE_CHECKING:
    from graph_sitter.core.symbol import Symbol


Parent = TypeVar("Parent", bound="Symbol")


class DefinedName(Name[Parent], Generic[Parent]):
    """A name that defines a symbol.

    Does not reference any other names
    """

    @reader
    @noapidoc
    @override
    def _resolved_types(self) -> Generator[ResolutionStack[Self], None, None]:
        yield ResolutionStack(self)
