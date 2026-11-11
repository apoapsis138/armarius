"""No `except` catches TypeError or AttributeError.

Those are what a renamed field or a wrong argument raise, so catching them
turns a bug into a silent no-op (CONTRIBUTING.md, "Catch only the error you
expect"). Data from outside (a file, another computer) is checked for
shape where it comes in (shapes.py) and refused with a ValueError naming
the field instead.

A tuple of exceptions named for catching later counts too.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "ars_magica_manager"
BROAD = {"TypeError", "AttributeError"}


def _names(node: ast.expr) -> list[ast.expr]:
    return list(node.elts) if isinstance(node, ast.Tuple) else [node]


def _broad(node: ast.expr) -> bool:
    return any(isinstance(n, ast.Name) and n.id in BROAD for n in _names(node))


def test_no_catch_of_type_or_attribute_errors():
    found = []
    for path in sorted(ROOT.rglob("*.py")):
        where = path.relative_to(ROOT).as_posix()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            caught = (
                node.type
                if isinstance(node, ast.ExceptHandler) and node.type is not None
                else node.value
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Tuple)
                else None
            )
            if caught is not None and _broad(caught):
                found.append(f"{where}:{node.lineno}")
    assert not found, (
        "catches TypeError or AttributeError (check the data's shape where it "
        "comes in instead, shapes.py): " + "; ".join(found)
    )
