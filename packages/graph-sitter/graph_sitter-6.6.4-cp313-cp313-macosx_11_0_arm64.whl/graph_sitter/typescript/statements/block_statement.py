from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.utils.codemod.codemod_writer_decorators import apidoc
from graph_sitter.core.statements.block_statement import BlockStatement
from graph_sitter.typescript.detached_symbols.code_block import TSCodeBlock
from graph_sitter.typescript.interfaces.has_block import TSHasBlock

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent", bound="TSCodeBlock")


@apidoc
class TSBlockStatement(BlockStatement[Parent], TSHasBlock, Generic[Parent]):
    """Statement which contains a block."""
