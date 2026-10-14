"""A record's Manage chapter (Export, Update from a File, Delete) and the
In Creation / In Play toggle in its header, with the palette each mode
is drawn in (gui/manage.py)."""

from __future__ import annotations

import os

import pytest
import shiboken6

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtCore import QEvent
from PySide6.QtGui import QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QWidget
from screen_helpers import _saga_with_familiar, _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.manage import ModeToggle, fade_from
from ars_magica_manager.gui.paper import Paper
from ars_magica_manager.gui.themes import DRAFTING, PALETTES
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.gui.worksheet import WorksheetPage


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def _manage(window: MainWindow) -> dict[str, QPushButton]:
    """The page's Manage chapter, opened: its buttons by their words."""
    page = window.page()
    codex = getattr(page, "codex", None)
    assert codex is not None and codex.chapters()[-1] == "Manage"
    codex.open_chapter("Manage")
    chapter = codex.pages.currentWidget()
    assert isinstance(chapter, QWidget)
    return {b.text().strip(): b for b in chapter.findChildren(QPushButton)}


def test_a_characters_manage_chapter_exports_updates_and_deletes(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    assert list(_manage(window)) == ["Export", "Update from a File", "Delete Leandro"]


def test_a_familiar_can_only_be_deleted(app):
    window = _window(_saga_with_familiar())
    window.open_familiar("fam1")
    buttons = _manage(window)
    assert list(buttons) == ["Delete Ashwing"]
    answering(window, True)
    buttons["Delete Ashwing"].click()
    assert storage.load_saga("test_saga").familiars == []
    assert window.crumb_names()[-1] == "Leandro"


def test_delete_asks_first_then_leaves_for_the_page_above(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    asked = answering(window, False)
    _manage(window)["Delete Leandro"].click()
    assert asked[0].question.startswith("Delete Leandro?")
    assert storage.load_saga("test_saga").characters
    answering(window, True)
    _manage(window)["Delete Leandro"].click()
    assert storage.load_saga("test_saga").characters == []
    assert window.crumb_names() == ["Sagas", "Test Saga", "Test Covenant"]


def test_an_export_updates_the_character_it_came_from(app, tmp_path):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    target = tmp_path / "leandro.amm.json"
    answering(window, {"file": str(target)})
    _manage(window)["Export"].click()
    assert target.is_file()
    # Changed here since: the file puts it back.
    saga = window.saga
    assert saga is not None
    magus = saga.character("char1")
    assert magus is not None
    magus.name = "Leandro the Younger"
    storage.save_saga(saga)
    window.redraw()
    asked = answering(window, str(target), True)
    _manage(window)["Update from a File"].click()
    assert "Name: Leandro the Younger → Leandro" in asked[1].question
    saved = storage.load_saga("test_saga")
    assert [c.name for c in saved.characters] == ["Leandro"]
    assert window.told[-1][1] == "Updated Leandro from leandro.amm.json."
    # Nothing differs now.
    answering(window, str(target))
    _manage(window)["Update from a File"].click()
    assert "Nothing in leandro.amm.json differs" in window.told[-1][1]


def test_the_mode_toggle_changes_the_palette_and_opens_the_worksheet(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    toggle = window.page().findChild(ModeToggle)
    assert toggle is not None and toggle.worksheet is None
    assert toggle.switch.text().strip() == "In Play"
    assert window.palette_ is PALETTES[0]
    answering(window, True)
    toggle.switch.click()
    saga = window.saga
    assert saga is not None and saga.character("char1").in_creation
    assert isinstance(window.page(), WorksheetPage)
    # Drafting vellum, ruled, while it is In Creation.
    assert window.palette_ is DRAFTING and DRAFTING.ruled
    body = window.stack.widget(0)
    assert isinstance(body, Paper) and body.p is DRAFTING
    window.go(window.trail[:-1])
    assert isinstance(window.page(), CharacterSheet)
    toggle = window.page().findChild(ModeToggle)
    assert toggle is not None and toggle.worksheet is not None
    assert toggle.switch.text().strip() == "In Creation"
    answering(window, True)
    toggle.switch.click()
    assert not saga.character("char1").in_creation
    assert window.palette_ is PALETTES[0]
    assert isinstance(window.page(), CharacterSheet)


def test_the_fade_goes_away_when_it_ends(app):
    host = QWidget()
    host.resize(100, 80)
    cover = fade_from(host, QPixmap(100, 80), ms=10)
    assert cover.geometry() == host.rect()
    for _ in range(100):
        QTest.qWait(20)
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        if not shiboken6.isValid(cover):
            break
    assert not shiboken6.isValid(cover)
