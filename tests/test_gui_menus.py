"""The desktop sets out the terminal's New and More actions on the page
itself, where menu_forms.PLACES puts them, and has no New or More menu."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from screen_helpers import _saga_with_familiar, _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui import window as window_module
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.widgets import NewCard
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
        window_module.MainWindow,
        "tell",
        lambda _window, _title, words: said.append(words),
    )
    return said


def _menus(window: MainWindow) -> dict[str, QPushButton]:
    """Any New or More menu button in the window: there are none, as each
    action is set out on the page."""
    return {
        b.text().strip(): b
        for b in window.findChildren(QPushButton)
        if b.text().strip() in ("New", "More")
    }


def _new(window: MainWindow) -> dict[str, NewCard]:
    """The page's New cards on show, by their words."""
    page = window.page()
    assert page is not None
    return {c.words: c for c in page.findChildren(NewCard) if c.isVisibleTo(page)}


def _buttons(window: MainWindow) -> dict[str, QPushButton]:
    """The page's section buttons on show, by their words."""
    page = window.page()
    assert page is not None
    return {
        b.text().strip(): b
        for b in page.findChildren(QPushButton)
        if b.objectName() == "edit" and b.isVisibleTo(page)
    }


def _saga_chapter(window: MainWindow, chapter: str) -> None:
    page = window.page()
    assert page is not None
    page.codex.open_chapter(chapter)  # type: ignore[attr-defined]


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def test_the_saga_page_sets_out_its_actions_in_its_chapters(app):
    window = _window(_sample_saga_with_covenant())
    assert window.page().chapters() == [  # type: ignore[union-attr]
        "The World",
        "Seasons",
        "Rules and Content",
        "Saga Management",
    ]
    assert list(_new(window)) == [
        "New Covenant",
        "New Tribunal",
        "New Character",
        "New Laboratory",
    ]
    _saga_chapter(window, "Seasons")
    assert "Set Date" in _buttons(window)
    _saga_chapter(window, "Saga Management")
    assert {"Edit Saga", "Import"} <= set(_buttons(window))
    # Nothing is left for New and More; Bind Familiar is on a covenant
    # or a magus.
    assert _menus(window) == {}


def test_new_makes_a_record_and_opens_its_creation_worksheet(app):
    window = _window(_sample_saga_with_covenant())
    asked = answering(window, None)
    _new(window)["New Covenant"].on_click()
    assert asked[0].windowTitle() == "Create a New Covenant"
    assert [c.name for c in storage.load_saga("test_saga").covenants] == [
        "Test Covenant"
    ]
    answering(window, {"name": "Fengheld"})
    _new(window)["New Covenant"].on_click()
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
    assert list(_new(window)) == ["New Magus", "New Companion", "New Grog"]
    page.codex.open_chapter("Laboratories")
    assert list(_new(window)) == ["New Laboratory"]
    # Nothing is left for New: a familiar is bound on its magus or in
    # their laboratory.
    assert "New" not in _menus(window)
    answering(window, {"name": "Aelfric"})
    _new(window)["New Laboratory"].on_click()
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
    _new(window)["New Companion"].on_click()
    saga = window.saga
    assert saga is not None
    made = next(c for c in saga.characters if c.name == "Osric")
    assert (made.covenant_id, made.type) == ("cov1", "companion")
    assert window.crumb_names()[-2:] == ["Osric", "Creation Worksheet"]


def test_no_new_on_a_companion(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].type = "companion"
    window = _window(saga)
    window.show_character("char1")
    assert "New" not in _menus(window)


def test_the_saga_page_sets_its_date(app):
    window = _window(_sample_saga_with_covenant())
    _saga_chapter(window, "Seasons")
    answering(window, {"season": "Autumn", "year": "1225"})
    _buttons(window)["Set Date"].click()
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
    _saga_chapter(window, "Saga Management")
    asked = answering(window, "Books", str(csv), True, "Skip")
    _buttons(window)["Import"].click()
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
    assert list(_new(window)) == ["Bind Familiar"]
    answering(window, {"name": "Ashwing"})
    _new(window)["Bind Familiar"].on_click()
    saga = window.saga
    assert saga is not None
    assert [f.name for f in saga.familiars] == ["Ashwing"]
    assert window.crumb_names()[-1] == "Ashwing"
    window.show_character("char1")
    assert _new(window) == {}


def test_the_laboratorys_planning_binds_its_owners_familiar(app):
    window = _window(_sample_saga_with_covenant())
    window.open_laboratory("lab1")
    page = window.page()
    page.codex.open_chapter("Seasons")
    planning = section_buttons(page, "Planning")
    assert "Bind Familiar" in planning
    asked = answering(window, {"name": "Ashwing"})
    planning["Bind Familiar"].click()
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


def test_give_sits_on_each_raw_vis_section(app):
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    magus.raw_vis = {"vim": 3}
    saga.laboratories[0].raw_vis = {"ignem": 2}
    window = _window(saga)
    window.show_character("char1")
    window.page().codex.open_chapter("Inventory")
    asked = answering(window, {"count": 2, "to": "laboratory:lab1"})
    section_buttons(window.page(), "Raw Vis")["Give"].click()
    assert asked, "Give asks how much and to whom"
    assert storage.load_saga(saga.id).laboratories[0].raw_vis == {"ignem": 2, "vim": 2}
    window.open_laboratory("lab1")
    window.page().codex.open_chapter("Stores")
    assert "Give" in section_buttons(window.page(), "Raw Vis")
    assert "Move Vis" not in section_buttons(window.page(), "Raw Vis")


def test_a_covenants_library_imports_books(app):
    window = _window(_sample_saga_with_covenant())
    window.open_covenant("cov1")
    window.page().codex.open_chapter("Library")
    assert "Import" in section_buttons(window.page(), "Library")


def test_silver_shows_on_personal_gear_and_is_given_from_there(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].silver = 5
    wealth = saga.covenants[0].economics.wealth
    window = _window(saga)
    window.show_character("char1")
    window.page().codex.open_chapter("Inventory")
    buttons = section_buttons(window.page(), "Personal Gear")
    assert any(
        "5 pounds of silver" in label.text()
        for label in window.page().findChildren(QLabel)
    )
    answering(window, {"count": 3, "to": "covenant:cov1"})
    buttons["Give Silver"].click()
    saved = storage.load_saga(saga.id)
    assert saved.characters[0].silver == 2
    assert saved.covenants[0].economics.wealth == wealth + 3


def test_a_notice_is_drawn_on_paper_with_only_ok(app):
    from ars_magica_manager.gui.forms import NoticeDialog
    from ars_magica_manager.gui.themes import PALETTES

    notice = NoticeDialog("Give", "Gave [b]2 pawns[/] of Vim vis.", PALETTES[0])
    assert notice.words == "Gave 2 pawns of Vim vis."
    assert notice.save.text() == "OK" and notice.cancel.isHidden()
    # No system title bar: the paper is the whole window.
    assert notice.windowFlags() & Qt.WindowType.FramelessWindowHint


def test_a_verb_with_nothing_to_act_on_is_not_offered(app):
    window = _window(_sample_saga_with_covenant())
    window.show_character("char1")
    window.page().codex.open_chapter("Inventory")
    # No books: no Give; no gear: Add only, Edit and Delete hidden.
    assert section_buttons(window.page(), "Books")["Give"].isHidden()
    gear = section_buttons(window.page(), "Personal Gear")
    assert not gear["Add"].isHidden()
    assert gear["Edit"].isHidden() and gear["Delete"].isHidden()
