from typing import TYPE_CHECKING, Generic, TypeVar

from codegen.utils.codemod.codemod_writer_decorators import ts_apidoc
from graph_sitter.core.expressions.union_type import UnionType

if TYPE_CHECKING:
    pass


Parent = TypeVar("Parent")


@ts_apidoc
class TSUnionType(UnionType["TSType", Parent], Generic[Parent]):
    """Union type

    Examples:
        string | number
    """

    pass
