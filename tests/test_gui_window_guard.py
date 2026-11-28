"""Every window the desktop opens wears the app's frame: a test that fails,
naming it, for any dialog window in the desktop package that isn't a
Window (docs/adr/0033-every-window-wears-the-apps-frame.md, "Every window
wears the app's frame; only the system's file pickers stay native"). The
system's file picker, QFileDialog, is the one exception."""

from __future__ import annotations

import importlib
import os
import pkgutil

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QDialog, QFileDialog

from ars_magica_manager import gui
from ars_magica_manager.gui.window_frame import Window


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
        f"(gui/window_frame.py): {', '.join(unframed)}"
    )
