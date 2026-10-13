"""Managing the sagas on the desktop's shelf: New Saga, a card's Delete
and Change Save Folder run the core's steps (saga_forms); answered
without showing the dialogs (gui_steps.answering)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, buttons
from PySide6.QtWidgets import QApplication
from support import everything_saga

from ars_magica_manager import paths, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import ConfirmDialog
from ars_magica_manager.gui.pages import SagaPage, SagaShelf
from ars_magica_manager.gui.window import SHELF, MainWindow, Place


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _shelf() -> MainWindow:
    saga = everything_saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.go([Place(SHELF)])
    assert isinstance(window.page(), SagaShelf)
    return window


def test_new_saga_creates_and_opens_it(app):
    window = _shelf()
    answering(
        window,
        {
            "name": "The Tremere Schism",
            "storyguide": "Hedda",
            "year": 1230,
            "description": "A covenant on the border.",
        },
    )
    window.page().new_saga.click()
    assert isinstance(window.page(), SagaPage)
    assert window.saga is not None
    assert window.saga.name == "The Tremere Schism"
    assert window.saga.current_year == 1230
    assert window.saga.id in storage.list_sagas()


def test_a_cards_delete_asks_then_deletes_the_saga(app):
    window = _shelf()
    saga_id = window.saga_ids[0]
    asked = answering(window, False)
    buttons(window.page(), "Delete")[0].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert "cannot be undone" in asked[0].question
    assert saga_id in storage.list_sagas()
    answering(window, True)
    buttons(window.page(), "Delete")[0].click()
    assert storage.list_sagas() == []
    page = window.page()
    assert isinstance(page, SagaShelf)
    assert buttons(page, "Delete") == []


def test_change_save_folder_moves_the_saves_there(app, tmp_path):
    # The saves start in the data folder, as the app keeps them.
    storage.use_data_dir(paths.data_dir())
    window = _shelf()
    saga_id = window.saga_ids[0]
    folder = tmp_path / "elsewhere"
    folder.mkdir()
    window.choose_folder = lambda _start: str(folder)
    answering(window, {"move": True})
    window.page().change_folder.click()
    assert paths.data_dir().resolve() == folder.resolve()
    assert storage.list_sagas() == [saga_id]
    assert (folder / paths.SAGAS).is_dir()
    assert window.told[0][0] == "Change Save Folder"
    assert "Moved" in window.told[0][1]
    assert isinstance(window.page(), SagaShelf)


def test_choosing_no_folder_changes_nothing(app):
    window = _shelf()
    before = paths.data_dir()
    window.choose_folder = lambda _start: ""
    answering(window)
    window.page().change_folder.click()
    assert paths.data_dir() == before
