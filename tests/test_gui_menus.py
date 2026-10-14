"""The desktop window's New and More menus, beside the trail, and the
page's own buttons for what it sets out itself (menu_forms.PLACES)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QPushButton
from screen_helpers import _saga_with_familiar, _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui import window as window_module
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.widgets import GiltButton
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


def _gilt(window: MainWindow) -> dict[str, GiltButton]:
    """The page's own buttons on show, by their words."""
    page = window.page()
    assert page is not None
    return {b.text(): b for b in page.findChildren(GiltButton) if b.isVisibleTo(page)}


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def test_the_saga_page_sets_out_its_actions_as_buttons(app):
    window = _window(_sample_saga_with_covenant())
    assert list(_gilt(window)) == [
        "Edit Saga",
        "Import",
        "Set Date",
        "New Covenant",
        "New Character",
        "New Laboratory",
    ]
    # Nothing is left for New and More; Bind Familiar is on a covenant
    # or a magus.
    assert _menus(window) == {}


def test_new_makes_a_record_and_opens_its_creation_worksheet(app):
    window = _window(_sample_saga_with_covenant())
    asked = answering(window, None)
    _gilt(window)["New Covenant"].click()
    assert asked[0].windowTitle() == "Create a New Covenant"
    assert [c.name for c in storage.load_saga("test_saga").covenants] == [
        "Test Covenant"
    ]
    answering(window, {"name": "Fengheld"})
    _gilt(window)["New Covenant"].click()
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


def test_a_covenants_people_and_laboratories_open_with_new(app):
    window = _window(_sample_saga_with_covenant())
    window.open_covenant("cov1")
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("People")
    assert list(_gilt(window)) == ["New Character"]
    page.codex.open_chapter("Laboratories")
    assert list(_gilt(window)) == ["New Laboratory"]
    # Nothing is left for New: a familiar is bound on its magus or in
    # their laboratory.
    assert "New" not in _menus(window)
    answering(window, {"name": "Aelfric"})
    _gilt(window)["New Laboratory"].click()
    saga = window.saga
    assert saga is not None
    lab = next(lab for lab in saga.laboratories if lab.name == "Aelfric")
    assert lab.covenant_id == "cov1"


def test_new_character_on_a_covenant_belongs_to_it(app):
    window = _window(_sample_saga_with_covenant())
    window.open_covenant("cov1")
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("People")
    answering(window, {"name": "Osric"})
    _gilt(window)["New Character"].click()
    saga = window.saga
    assert saga is not None
    made = next(c for c in saga.characters if c.name == "Osric")
    assert made.covenant_id == "cov1"
    assert window.crumb_names()[-2:] == ["Osric", "Creation Worksheet"]


def test_no_new_on_a_companion(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].type = "companion"
    window = _window(saga)
    window.show_character("char1")
    assert "New" not in _menus(window)


def test_the_saga_page_sets_its_date(app):
    window = _window(_sample_saga_with_covenant())
    answering(window, {"season": "Autumn", "year": "1225"})
    _gilt(window)["Set Date"].click()
    assert [words for _title, words in window.told] == ["Date set to Autumn 1225."]
    saved = storage.load_saga("test_saga")
    assert (saved.current_season, saved.current_year) == ("Autumn", 1225)


def test_more_on_a_record_leaves_out_what_its_page_offers(app):
    """Export, Update from a File and Delete are in the record's Manage
    chapter, the mode and the worksheet in its header (test_gui_manage),
    and the rest in their sections."""
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    assert isinstance(window.page(), CharacterSheet)
    # Lab Texts Read is beside the Lab Texts too: nothing is left.
    assert _menus(window) == {}
    window = _window(_saga_with_familiar())
    window.open_familiar("fam1")
    assert _menus(window) == {}


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
    _gilt(window)["Import"].click()
    assert asked[1].windowTitle() == "Import books (as unassigned books)"
    assert "Import 2 books from books.csv" in asked[2].question
    assert asked[3].windowTitle().startswith("A book named On the Theory of Magic")
    books = storage.load_saga("test_saga").books
    assert [b.name for b in books[before:]] == ["Notes on Flame"]
    assert window.told == [
        ("Import Data", "Imported 1 book as unassigned books; skipped 1 duplicate.")
    ]


def test_a_magus_binds_a_familiar_where_it_would_be_shown(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    assert list(_gilt(window)) == ["Bind Familiar"]
    answering(window, {"name": "Ashwing"})
    _gilt(window)["Bind Familiar"].click()
    saga = window.saga
    assert saga is not None
    assert [f.name for f in saga.familiars] == ["Ashwing"]
    assert window.crumb_names()[-1] == "Ashwing"
    window.show_character("char1")
    assert _gilt(window) == {}


def test_the_laboratorys_seasons_bind_its_owners_familiar(app):
    window = _window(_sample_saga_with_covenant())
    window.open_laboratory("lab1")
    page = window.page()
    page.codex.open_chapter("Seasons")
    assert list(_gilt(window)) == ["Bind Familiar"]
    asked = answering(window, {"name": "Ashwing"})
    _gilt(window)["Bind Familiar"].click()
    assert asked[0].windowTitle() == "Bind a New Familiar"
    saga = window.saga
    assert saga is not None
    assert [(f.name, f.character_id) for f in saga.familiars] == [("Ashwing", "char1")]


def test_texts_read_sits_beside_the_lab_texts(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    asked = answering(window, None)
    section_buttons(window.page(), "Hermetic Background")["Texts Read"].click()
    assert asked[0].windowTitle().startswith("Lab Texts")
    window.open_laboratory("lab1")
    window.page().codex.open_chapter("Stores")
    asked = answering(window, None)
    section_buttons(window.page(), "Lab Texts")["Texts Read"].click()
    assert asked[0].windowTitle().startswith("Lab Texts")
