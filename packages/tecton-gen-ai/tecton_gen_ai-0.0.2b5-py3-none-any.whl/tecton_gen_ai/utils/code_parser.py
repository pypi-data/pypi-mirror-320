import ast
import inspect
from typing import Any
from textwrap import dedent


def get_declaration(obj: Any) -> str:
    """
    Get the function or class declaration with docstring.

    Args:

        obj: The object

    Returns:

        str: The object declaration with docstring
    """
    if inspect.isclass(obj) or inspect.isfunction(obj):
        src = dedent(inspect.getsource(obj))
        tree = ast.parse(src)
        tree = _traverse(tree)
        return ast.unparse(tree)
    raise ValueError(f"{obj} is not a class or function")


def _traverse(node: Any):
    if isinstance(node, ast.FunctionDef):
        name = node.name
        if name == "__init__" or not name.startswith("_"):
            nb = node.body
            if (
                len(nb) > 0
                and isinstance(nb[0], ast.Expr)
                and isinstance(nb[0].value, ast.Constant)
            ):
                nb = [nb[0], ast.Pass()]
            else:
                nb = [ast.Pass()]
            node.body = nb
            return node
        else:
            return None
    elif hasattr(node, "body"):
        body = []
        for x in node.body:
            xx = _traverse(x)
            if xx is not None:
                body.append(xx)
        node.body = body
        return node
    else:
        return node
