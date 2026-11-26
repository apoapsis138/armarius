"""The desktop Creation Worksheet's Review Interests step: Restore the
defaults, beside Edit Interests, answered without showing the dialogs
(gui_steps.answering)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtWidgets import QApplication, QPushButton
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import creation, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.gui.worksheet import WorksheetPage


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _buttons(page: WorksheetPage) -> dict[str, QPushButton]:
    """The step on show's buttons, by their words, in order."""
    chapter = page.codex.pages.currentWidget()
    assert chapter is not None
    return {b.text().strip(): b for b in chapter.findChildren(QPushButton)}


def test_restore_the_defaults_sits_beside_edit_interests_and_restores_them(
    app: QApplication,
):
    saga = _sample_saga_with_covenant()
    character = creation.add_character(saga, "Brother Anselm", "companion", "cov1")
    character.interests_chosen = True
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_worksheet(character.id)
    page = window.page()
    assert isinstance(page, WorksheetPage)
    page.open_step("interests")
    words = list(_buttons(page))
    assert words[words.index("Edit Interests") + 1] == "Restore the defaults"
    answering(window)
    _buttons(page)["Restore the defaults"].click()
    saved = storage.load_saga(saga.id).character(character.id)
    assert saved is not None and not saved.interests_chosen
    # answering() keeps the notes in the window's `told`.
    assert vars(window)["told"] == [
        ("Interests", "Brother Anselm is back to the defaults: Religion.")
    ]
