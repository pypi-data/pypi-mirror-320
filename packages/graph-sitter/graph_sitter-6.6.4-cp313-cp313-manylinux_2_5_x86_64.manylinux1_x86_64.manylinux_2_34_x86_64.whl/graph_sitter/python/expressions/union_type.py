from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.utils.codemod.codemod_writer_decorators import py_apidoc
from graph_sitter.core.expressions.union_type import UnionType

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent")


@py_apidoc
class PyUnionType(UnionType["PyType", Parent], Generic[Parent]):
    """Union type

    Examples:
        str | int
    """

    pass
