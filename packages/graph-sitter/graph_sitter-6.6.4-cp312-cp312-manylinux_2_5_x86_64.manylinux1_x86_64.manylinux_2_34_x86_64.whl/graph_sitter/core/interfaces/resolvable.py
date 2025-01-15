from abc import abstractmethod
from typing import TYPE_CHECKING, Generic

from typing_extensions import TypeVar

from codegen.utils.codemod.codemod_writer_decorators import noapidoc
from graph_sitter.core.autocommit import writer
from graph_sitter.core.interfaces.chainable import Chainable
from graph_sitter.core.interfaces.editable import Editable

if TYPE_CHECKING:
    pass
Parent = TypeVar("Parent", bound=Editable)


class Resolvable(Chainable[Parent], Generic[Parent]):
    """Represents a class resolved to another symbol during the compute dependencies step."""

    @abstractmethod
    @noapidoc
    @writer
    def rename_if_matching(self, old: str, new: str) -> None: ...
