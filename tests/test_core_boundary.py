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


def test_no_core_module_imports_a_ui():
    bad = sorted(
        f"{_module_name(path)} imports {module}"
        for path in _files(None)
        for module in set(_imports(path))
        if _breaks_the_boundary(module)
    )
    assert not bad, "; ".join(bad)


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
    assert _breaks_the_boundary(f"{PACKAGE}.gui.style.paper", "tui")
    assert _breaks_the_boundary(f"{PACKAGE}.tui.style")
    assert not _breaks_the_boundary(f"{PACKAGE}.style.palettes")


# -- the core's layers --

#: The core's layers, lowest first: a module may import its own layer or
#: one below it, never one above. The package itself (`ROOT`, `DATA_DIR`,
#: the version) is in the lowest.
LAYERS: tuple[tuple[str, frozenset[str]], ...] = (
    (
        "models",
        frozenset({"", "arts", "markup", "models", "paths", "totals", "rules.xp"}),
    ),
    # The catalogs and the books they come from: data the rules look up.
    ("data", frozenset({"book_kinds", "catalog", "sourcebooks"})),
    # The rules, and the top-level modules that are rules too (a covenant's
    # Boons and Hooks, what a book is worth, raw vis): they keep to the
    # layers below.
    ("rules", frozenset({"rules", "book_value", "covenants", "vis"})),
    ("app", frozenset()),  # every other top-level module and package
    # What a page shows and does: the sheets and forms, and the pages
    # built from them (the hall and the meeting held in it, Ahead, the
    # saga overview, the creation worksheet, the printed sheets, each
    # section's verbs).
    (
        "sheets",
        frozenset(
            {
                "acta",
                "actions",
                "ahead",
                "forms",
                "hall",
                "hibernia_meeting",
                "meeting",
                "print_layout",
                "rhine_meeting",
                "ruins",
                "saga_overview",
                "section_verbs",
                "sheets",
                "theban_meeting",
                "troupe",
                "worksheet",
                "worksheet_feedback",
                # Transylvania's meeting steps.
                "transylvania_meeting",
                # Normandy's Library and Provence's residency steps.
                "normandy_meeting",
                "provence_meeting",
            }
        ),
    ),
    ("front-ends", frozenset(FRONT_ENDS)),
)
APP = next(i for i, (name, _) in enumerate(LAYERS) if name == "app")


def _layer(module: str) -> int:
    """The layer of `module`: its own entry in LAYERS (`rules.xp`), else
    its top-level module's or package's."""
    parts = module.split(".")[1:]
    for name in (".".join(parts[:2]), parts[0] if parts else ""):
        for i, (_, tops) in enumerate(LAYERS):
            if name in tops:
                return i
    return APP


def _runs_code(path: Path) -> bool:
    """Whether a package's `__init__` imports anything (a docstring alone
    doesn't tie its importer to the package's layer)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))


def _upward_imports(root: Path = ROOT) -> set[str]:
    """Every import of a module in a higher layer than the importer's.
    `from package import module` counts the package only when its
    `__init__` imports something."""
    paths = {_module_name(path, root): path for path in root.rglob("*.py")}
    found = set()
    for name, path in paths.items():
        targets = set(_imports(path, root)) & set(paths)
        for target in targets:
            inside = [t for t in targets if t.startswith(target + ".")]
            empty = paths[target].name == "__init__.py" and not _runs_code(
                paths[target]
            )
            if inside and empty:
                continue
            if _layer(target) > _layer(name):
                found.add(f"{name} -> {target}")
    return found


def test_no_import_points_up_a_layer():
    found = sorted(_upward_imports())
    assert not found, (
        "These import a module in a higher layer (see LAYERS): "
        + "; ".join(found)
        + ". Move what is needed down a layer, or pass it in as an argument."
    )


def test_the_layer_check_catches_an_upward_import(tmp_path):
    root = tmp_path / PACKAGE
    (root / "models").mkdir(parents=True)
    (root / "rules").mkdir()
    (root / "__init__.py").write_text("")
    (root / "catalog.py").write_text("")
    (root / "rules" / "__init__.py").write_text("")
    (root / "rules" / "xp.py").write_text("from .. import catalog\n")
    (root / "models" / "__init__.py").write_text(
        "def f():\n    from ..rules import xp\n"
    )
    (root / "rules" / "lab.py").write_text("")
    (root / "models" / "laboratory.py").write_text("from ..rules import lab\n")
    # rules.xp is in the lowest layer, with models; rules.lab is not, and
    # the rules package's empty __init__ isn't counted.
    assert _upward_imports(root) == {
        f"{PACKAGE}.models.laboratory -> {PACKAGE}.rules.lab",
        f"{PACKAGE}.rules.xp -> {PACKAGE}.catalog",
    }
