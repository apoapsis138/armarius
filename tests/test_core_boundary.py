"""The shared core never imports a UI library.

The rules, models, seasons, storage, catalogs, form specs and actions are
shared by every front-end; only the front-ends, tui/ (Textual) and gui/
(PySide6), may import a UI library. A core module that imported one, or
imported a front-end module, would tie the core to that UI and break the
other front-end; and neither front-end imports the other or the other's
libraries. Read from the source, so an import inside a function or under
TYPE_CHECKING counts too."""

import ast
from pathlib import Path

import pytest

PACKAGE = "ars_magica_manager"
ROOT = Path(__file__).resolve().parent.parent / PACKAGE

#: Each front-end package, with the UI libraries (and the libraries only
#: that front-end uses) that it alone may import.
FRONT_ENDS = {
    "tui": frozenset({"textual", "textual_serve", "rich", "asyncssh"}),
    "gui": frozenset({"PySide6", "shiboken6"}),
}
UI_LIBRARIES = frozenset().union(*FRONT_ENDS.values())


def _module_name(path: Path, root: Path = ROOT) -> str:
    parts = path.relative_to(root.parent).with_suffix("").parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _front_end(module: str) -> str | None:
    """The front-end package `module` belongs to, or None for the core."""
    parts = module.split(".")
    if parts[0] != PACKAGE or len(parts) < 2 or parts[1] not in FRONT_ENDS:
        return None
    return parts[1]


def _files(front_end: str | None) -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.py")
        if _front_end(_module_name(path)) == front_end
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


def _breaks_the_boundary(module: str, front_end: str | None = None) -> bool:
    """Whether code in `front_end` (None: the core) may not import `module`."""
    allowed = FRONT_ENDS.get(front_end or "", frozenset())
    library = module.split(".")[0]
    if library in UI_LIBRARIES and library not in allowed:
        return True
    return _front_end(module) not in (None, front_end)


def test_the_core_is_most_of_the_package():
    # A guard against the walk finding nothing (a moved package).
    assert len(_files(None)) > 50
    assert len(_files("tui")) > 30


@pytest.mark.parametrize("path", _files(None), ids=lambda path: _module_name(path))
def test_core_module_imports_no_ui(path):
    bad = sorted({m for m in _imports(path) if _breaks_the_boundary(m)})
    assert not bad, f"{_module_name(path)} imports {', '.join(bad)}"


@pytest.mark.parametrize("front_end", sorted(FRONT_ENDS))
def test_a_front_end_imports_only_the_core_and_its_own_libraries(front_end):
    bad = sorted(
        f"{_module_name(path)} imports {module}"
        for path in _files(front_end)
        for module in _imports(path)
        if _breaks_the_boundary(module, front_end)
    )
    assert not bad, "; ".join(bad)


def test_the_check_catches_a_ui_import(tmp_path):
    root = tmp_path / PACKAGE
    (root / "rules").mkdir(parents=True)
    module = root / "rules" / "leaky.py"
    module.write_text(
        "from textual.widgets import Static\n"
        "def f():\n"
        "    from ..tui.screens import fields\n"
        "    from ..tui import hosting\n"
    )
    bad = {m for m in _imports(module, root) if _breaks_the_boundary(m)}
    assert {
        "textual.widgets",
        f"{PACKAGE}.tui.screens",
        f"{PACKAGE}.tui.hosting",
    } <= bad


def test_the_check_catches_one_front_end_importing_the_other():
    assert _breaks_the_boundary("PySide6.QtWidgets", "tui")
    assert _breaks_the_boundary(f"{PACKAGE}.tui.screens", "gui")
    assert _breaks_the_boundary("textual.app", "gui")
    assert not _breaks_the_boundary("textual.app", "tui")
    assert not _breaks_the_boundary(f"{PACKAGE}.form_spec", "gui")
