"""A question or notice window is tall enough for every line of its text:
a wrapped label doesn't make its window grow by itself, and a window that
cut off its last paragraph went unnoticed until a screen was drawn."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog

from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import ConfirmDialog, NoticeDialog
from ars_magica_manager.gui.themes import PALETTES

LONG = (
    "Delete the covenant Fengheld?\n\n"
    "Its laboratories and the characters who live there are kept, with no "
    "covenant. Its books, vis and wealth go with it, and its Diary too.\n\n"
    "This cannot be undone, and the players' copies change at once."
)


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application  # pyright: ignore[reportReturnType]


def _fits(dialog: QDialog) -> None:
    dialog.show()
    QApplication.processEvents()
    layout = dialog.layout()
    assert layout is not None
    needed = layout.totalHeightForWidth(dialog.width())
    assert dialog.height() >= needed, (
        f"{type(dialog).__name__} is {dialog.height()} tall; its text needs {needed}"
    )


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize("kind", ["confirm", "notice"])
def test_a_long_question_or_notice_fits_its_window(kind: str) -> None:
    p = PALETTES[0]
    dialog = (
        ConfirmDialog(LONG, p, yes_label="Delete")
        if kind == "confirm"
        else NoticeDialog("Deleted", LONG, p)
    )
    _fits(dialog)
