"""Every window the desktop opens wears the app's frame: a test that fails,
naming it, for any dialog window in the desktop package that isn't a
Window (docs/adr/0033-every-window-wears-the-apps-frame.md, "Every window
wears the app's frame; only the system's file pickers stay native"): a
QDialog subclass that isn't one, a bare QDialog made in place, or one of
Qt's stock dialogs (QMessageBox, QInputDialog and the rest). The system's
file picker, QFileDialog, is the one exception."""

from __future__ import annotations

import ast
import importlib
import os
import pkgutil
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtPrintSupport, QtWidgets
from PySide6.QtWidgets import QDialog, QFileDialog

from ars_magica_manager import gui
from ars_magica_manager.gui.style.window_frame import Window

#: Qt's own dialogs, which draw the system's title bar: every QDialog
#: subclass Qt ships, but the file picker.
STOCK_DIALOGS = frozenset(
    name
    for module in (QtWidgets, QtPrintSupport)
    for name in dir(module)
    if isinstance(found := getattr(module, name), type)
    and issubclass(found, QDialog)
    and found not in (QDialog, QFileDialog)
)


def _desktop_dialogs() -> list[type[QDialog]]:
    for info in pkgutil.walk_packages(gui.__path__, prefix=f"{gui.__name__}."):
        importlib.import_module(info.name)
    found: list[type[QDialog]] = []
    to_visit: list[type[QDialog]] = [QDialog]
    while to_visit:
        cls = to_visit.pop()
        to_visit.extend(cls.__subclasses__())
        module = cls.__module__
        if module == gui.__name__ or module.startswith(f"{gui.__name__}."):
            found.append(cls)
    return found


def _name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _unframed_uses(source: str) -> list[str]:
    """The lines of `source` that make a bare QDialog or use a stock one,
    as "line: what"."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and _name(node.func) == "QDialog":
            found.append(f"{node.lineno}: QDialog(")
        elif isinstance(node, ast.ImportFrom):
            found.extend(
                f"{node.lineno}: {alias.name}"
                for alias in node.names
                if alias.name in STOCK_DIALOGS
            )
        elif _name(node) in STOCK_DIALOGS:
            found.append(f"{node.lineno}: {_name(node)}")
    return sorted(set(found), key=lambda line: int(line.split(":")[0]))


def test_qt_s_stock_dialogs_are_known() -> None:
    assert {"QMessageBox", "QInputDialog", "QColorDialog"} <= STOCK_DIALOGS
    assert "QFileDialog" not in STOCK_DIALOGS


@pytest.mark.parametrize(
    "source",
    [
        "from PySide6.QtWidgets import QMessageBox\n",
        "QMessageBox.warning(None, 'A', 'B')\n",
        "QtWidgets.QInputDialog.getText(None, 'A', 'B')\n",
        "window = QDialog(parent)\n",
        "window = QtWidgets.QDialog()\n",
    ],
)
def test_a_bare_or_stock_dialog_is_caught(source: str) -> None:
    assert _unframed_uses(source)


@pytest.mark.parametrize(
    "source",
    [
        "from PySide6.QtWidgets import QDialog, QFileDialog\n",
        "QFileDialog.getOpenFileName(None, 'Open')\n",
        "class Form(QDialog):\n    pass\n",
        "result = QDialog.DialogCode.Accepted\n",
    ],
)
def test_the_file_picker_and_subclassing_are_not(source: str) -> None:
    assert _unframed_uses(source) == []


def test_every_desktop_window_is_a_window() -> None:
    dialogs = _desktop_dialogs()
    assert Window in dialogs, "The walk found no Window: did a gui module fail?"
    unframed = sorted(
        f"{cls.__module__}.{cls.__qualname__}"
        for cls in dialogs
        if not issubclass(cls, (Window, QFileDialog))
    )
    assert unframed == [], (
        "These windows don't wear the app's frame; build them on Window "
        f"(gui/style/window_frame.py): {', '.join(unframed)}"
    )


def test_no_desktop_source_makes_a_bare_or_stock_dialog() -> None:
    package = Path(gui.__file__).parent
    found = [
        f"{path.relative_to(package).as_posix()}:{use}"
        for path in sorted(package.rglob("*.py"))
        for use in _unframed_uses(path.read_text(encoding="utf-8"))
    ]
    assert found == [], (
        "These open a window without the app's frame; build it on Window "
        f"(gui/style/window_frame.py): {', '.join(found)}"
    )
