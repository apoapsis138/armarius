"""The desktop window's New and More menus, beside the trail."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QPushButton
from screen_helpers import _saga_with_familiar, _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui import window as window_module
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.gui.worksheet import WorksheetPage


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


@pytest.fixture(autouse=True)
def told(monkeypatch) -> list[str]:
    """What the window tells the user (its notes), without showing it."""
    said: list[str] = []
    monkeypatch.setattr(
        window_module.QMessageBox,
        "information",
        lambda _parent, _title, words: said.append(words),
    )
    return said


def _menus(window: MainWindow) -> dict[str, QPushButton]:
    found = {}
    for i in range(window.menus.count()):
        item = window.menus.itemAt(i)
        button = item.widget() if item is not None else None
        if isinstance(button, QPushButton):
            found[button.text().strip()] = button
    return found


def _entries(window: MainWindow, menu: str) -> dict[str, QAction]:
    found = _menus(window)[menu].menu()
    assert found is not None
    return {a.text(): a for a in found.actions() if not a.isSeparator()}


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def test_new_makes_a_record_and_opens_its_creation_worksheet(app):
    window = _window(_sample_saga_with_covenant())
    assert set(_menus(window)) == {"New", "More"}
    assert list(_entries(window, "More")) == ["Edit Saga", "Import", "Set Date"]
    asked = answering(window, None)
    _entries(window, "New")["New Covenant"].trigger()
    assert asked[0].windowTitle() == "Create a New Covenant"
    assert [c.name for c in storage.load_saga("test_saga").covenants] == [
        "Test Covenant"
    ]
    answering(window, {"name": "Fengheld"})
    _entries(window, "New")["New Covenant"].trigger()
    # A new record is In Creation: it opens on its worksheet, below its page.
    assert window.crumb_names() == [
        "Sagas",
        "Test Saga",
        "Fengheld",
        "Creation Worksheet",
    ]
    assert isinstance(window.page(), WorksheetPage)
    window.go(window.trail[:-1])
    assert isinstance(window.page(), CovenantPage)
    saved = storage.load_saga("test_saga")
    assert [c.name for c in saved.covenants] == ["Test Covenant", "Fengheld"]


def test_more_on_the_saga_sets_its_date(app):
    window = _window(_sample_saga_with_covenant())
    answering(window, {"season": "Autumn", "year": "1225"})
    _entries(window, "More")["Set Date"].trigger()
    assert [words for _title, words in window.told] == ["Date set to Autumn 1225."]
    saved = storage.load_saga("test_saga")
    assert (saved.current_season, saved.current_year) == ("Autumn", 1225)


def test_deleting_a_character_from_their_sheet(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    assert isinstance(window.page(), CharacterSheet)
    more = _entries(window, "More")
    assert list(more) == [
        "Lab Texts Read",
        "Export",
        "In Creation / In Play",
        "Delete Leandro",
    ]
    asked = answering(window, False)
    more["Delete Leandro"].trigger()
    assert asked[0].question.startswith("Delete Leandro?")
    assert storage.load_saga("test_saga").characters
    answering(window, True)
    _entries(window, "More")["Delete Leandro"].trigger()
    assert storage.load_saga("test_saga").characters == []
    # The page above the deleted one: their covenant's.
    assert window.crumb_names() == ["Sagas", "Test Saga", "Test Covenant"]


def test_a_familiars_page_only_deletes_it(app):
    window = _window(_saga_with_familiar())
    window.open_familiar("fam1")
    assert set(_menus(window)) == {"More"}
    assert list(_entries(window, "More")) == ["Delete Ashwing"]
    answering(window, True)
    _entries(window, "More")["Delete Ashwing"].trigger()
    assert storage.load_saga("test_saga").familiars == []
    assert window.crumb_names()[-1] == "Leandro"


def test_more_import_reads_a_file_chosen_in_the_open_window(app, tmp_path):
    window = _window(_sample_saga_with_covenant())
    csv = tmp_path / "books.csv"
    csv.write_text(
        "name,type,ability,quality,level\n"
        "On the Theory of Magic,Ability Summa,Magic Theory,5,3\n"
        "Notes on Flame,Ability Summa,Magic Theory,5,3\n",
        encoding="utf-8",
    )
    before = len(storage.load_saga("test_saga").books)
    asked = answering(window, "Books", str(csv), True, "Skip")
    _entries(window, "More")["Import"].trigger()
    assert asked[1].windowTitle() == "Import books (as unassigned books)"
    assert "Import 2 books from books.csv" in asked[2].question
    assert asked[3].windowTitle().startswith("A book named On the Theory of Magic")
    books = storage.load_saga("test_saga").books
    assert [b.name for b in books[before:]] == ["Notes on Flame"]
    assert window.told == [
        ("Import Data", "Imported 1 book as unassigned books; skipped 1 duplicate.")
    ]
