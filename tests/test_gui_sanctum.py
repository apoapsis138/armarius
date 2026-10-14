"""A magus and their sanctum one click apart: Sanctum on the magus's sheet,
the owner on the laboratory's, and the trail leads back each way."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import laboratory_sheet as ls
from ars_magica_manager import storage
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.laboratory import LaboratoryPage
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.gui.worksheet import WorksheetPage
from ars_magica_manager.models.saga import assign_laboratory_owner


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def test_the_core_finds_a_maguss_sanctum():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    assert ls.sanctum(saga, magus) is saga.laboratories[0]
    assign_laboratory_owner(saga, saga.laboratories[0], None)
    assert ls.sanctum(saga, magus) is None


def test_sanctum_opens_the_lab_below_the_magus_and_back(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    assert sheet.sanctum_button is not None
    assert sheet.sanctum_button.text().strip() == "Sanctum"
    sheet.sanctum_button.click()
    lab = window.page()
    assert isinstance(lab, LaboratoryPage)
    names = window.crumb_names()
    assert names[-2:] == ["Leandro", lab.lab.name]
    # The owner, on the laboratory, leads back up the trail.
    assert lab.owner_button is not None
    assert lab.owner_button.text().strip() == "Leandro"
    lab.owner_button.click()
    assert isinstance(window.page(), CharacterSheet)
    assert window.crumb_names() == names[:-1]


def test_the_owner_opens_below_a_laboratory_opened_from_its_covenant(app):
    window = _window(_sample_saga_with_covenant())
    window.open_laboratory("lab1")
    page = window.page()
    assert isinstance(page, LaboratoryPage) and page.owner_button is not None
    page.owner_button.click()
    assert isinstance(window.page(), CharacterSheet)
    assert window.crumb_names()[-2:] == [page.lab.name, "Leandro"]


def test_a_magus_with_no_sanctum_creates_one(app):
    saga = _sample_saga_with_covenant()
    assign_laboratory_owner(saga, saga.laboratories[0], None)
    window = _window(saga)
    window.show_character("char1")
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet) and sheet.sanctum_button is not None
    assert sheet.sanctum_button.text().strip() == "New Sanctum"
    asked = answering(window, {"name": "The Tower"})
    sheet.sanctum_button.click()
    assert asked[0].windowTitle() == "Create Leandro's Sanctum"
    saved = storage.load_saga(saga.id)
    made = next(lab for lab in saved.laboratories if lab.name == "The Tower")
    assert made.owner_id == "char1" and made.covenant_id == "cov1"
    # It opens on its worksheet, below the magus and the new lab.
    assert isinstance(window.page(), WorksheetPage)
    assert window.crumb_names()[-3:] == ["Leandro", "The Tower", "Creation Worksheet"]


def test_no_sanctum_for_a_companion_nor_owner_for_a_lab_with_none(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].type = "companion"
    assign_laboratory_owner(saga, saga.laboratories[0], None)
    window = _window(saga)
    window.show_character("char1")
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet) and sheet.sanctum_button is None
    window.open_laboratory("lab1")
    page = window.page()
    assert isinstance(page, LaboratoryPage) and page.owner_button is None
