from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.utils.codemod.codemod_writer_decorators import apidoc, noapidoc
from graph_sitter.core.dataclasses.usage import UsageKind
from graph_sitter.core.expressions.expression import Expression
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.interfaces.has_name import HasName
from graph_sitter.extensions.autocommit import commiter

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent", bound="Editable")


@apidoc
class Value(Expression[Parent], Generic[Parent]):
    """Editable attribute on any given code objects that has a value.

    For example, function, classes, global variable, interfaces, expressions, parameters are all
    composed of a value.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.G.parser.log_unparsed(self.ts_node)

    @noapidoc
    @commiter
    def _compute_dependencies(self, usage_type: UsageKind, dest: HasName | None = None):
        for node in self.children:
            node._compute_dependencies(usage_type, dest=dest)
