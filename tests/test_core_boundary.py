"""The shared core never imports a UI library.

The rules, models, seasons, storage, catalogs, form specs and actions are
shared by every front-end; only the front-ends (the Textual screens, the
app shell, its themes and the hosting that serves it) may import a UI
library. A core module that imported one, or imported a front-end module,
would tie the core to that UI and break the other front-end. Read from the
source, so an import inside a function or under TYPE_CHECKING counts too."""

import ast
from pathlib import Path

import pytest

PACKAGE = "ars_magica_manager"
ROOT = Path(__file__).resolve().parent.parent / PACKAGE

#: The front-end: the Textual screens, and the top-level modules that run
#: or serve them.
FRONT_END_PACKAGES = frozenset({"screens"})
FRONT_END_MODULES = frozenset({"app", "themes", "hosting"})

#: UI libraries and the libraries only a UI front-end uses.
UI_LIBRARIES = frozenset(
    {"textual", "textual_serve", "rich", "asyncssh", "PySide6", "shiboken6"}
)


def _module_name(path: Path, root: Path = ROOT) -> str:
    parts = path.relative_to(root.parent).with_suffix("").parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _is_front_end(module: str) -> bool:
    parts = module.split(".")
    if parts[0] != PACKAGE or len(parts) < 2:
        return False
    return parts[1] in FRONT_END_PACKAGES or parts[1] in FRONT_END_MODULES


def _core_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.py") if not _is_front_end(_module_name(path))
    )


def _resolve(path: Path, node: ast.ImportFrom, root: Path) -> str:
    """The absolute module a `from ... import` names."""
    if node.level == 0:
        return node.module or ""
    package = _module_name(path, root).split(".")
    if path.name != "__init__.py":
        package = package[:-1]
    base = package[: len(package) - (node.level - 1)]
    return ".".join(base + ([node.module] if node.module else []))


def _imports(path: Path, root: Path = ROOT) -> list[str]:
    """Every module `path` imports, absolute, with `from x import y`
    counted as both x and x.y (y may be a submodule)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = _resolve(path, node, root)
            found.append(module)
            found += [f"{module}.{alias.name}" for alias in node.names]
    return found


def _breaks_the_boundary(module: str) -> bool:
    return module.split(".")[0] in UI_LIBRARIES or _is_front_end(module)


def test_the_core_is_most_of_the_package():
    # A guard against the walk finding nothing (a moved package).
    assert len(_core_files()) > 50


@pytest.mark.parametrize("path", _core_files(), ids=lambda path: _module_name(path))
def test_core_module_imports_no_ui(path):
    bad = sorted({m for m in _imports(path) if _breaks_the_boundary(m)})
    assert not bad, f"{_module_name(path)} imports {', '.join(bad)}"


def test_the_check_catches_a_ui_import(tmp_path):
    root = tmp_path / PACKAGE
    (root / "rules").mkdir(parents=True)
    module = root / "rules" / "leaky.py"
    module.write_text(
        "from textual.widgets import Static\n"
        "def f():\n"
        "    from ..screens import fields\n"
        "    from .. import hosting\n"
    )
    bad = {m for m in _imports(module, root) if _breaks_the_boundary(m)}
    assert {"textual.widgets", f"{PACKAGE}.screens", f"{PACKAGE}.hosting"} <= bad
