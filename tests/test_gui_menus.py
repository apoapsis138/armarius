"""The desktop sets out the terminal's New and More actions on the page
itself, where menu_forms.PLACES puts them, and has no New or More menu."""

from __future__ import annotations

import os
from dataclasses import replace

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, buttons, section_buttons
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from screen_helpers import _saga_with_familiar, _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui import window as window_module
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.forms import TALLEST_WINDOW, FieldsDialog
from ars_magica_manager.gui.region import NeighbourPage
from ars_magica_manager.gui.tribunal import TribunalPage
from ars_magica_manager.gui.widgets import NewCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.gui.worksheet import WorksheetPage
from ars_magica_manager.models import Neighbour, Tribunal, VirtueFlawInstance


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
        "The Troupe",
        "The World",
        "The Region",
        "The Bestiary",
        "Conflicts",
        "Seasons",
        "Rules and Content",
        "Saga Management",
    ]
    # The Troupe gathers what is already made, so it makes nothing.
    assert list(_new(window)) == []
    _saga_chapter(window, "The World")
    assert list(_new(window)) == [
        "New Covenant",
        "New Tribunal",
        "New Character",
        "New Laboratory",
    ]
    _saga_chapter(window, "The Region")
    assert list(_new(window)) == ["New Neighbour"]
    _saga_chapter(window, "The Bestiary")
    assert list(_new(window)) == ["New Creature"]
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
    _saga_chapter(window, "The World")
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


def test_new_grog_from_a_grogs_template_asks_its_choices_first(app):
    """The Animal Trainer's Madoc: the choices form opens after New Grog,
    a grog's limits refuse an extra Virtue, and saving the book's own set
    makes him In Creation, on his worksheet."""
    window = _window(_sample_saga_with_covenant())
    window.open_covenant("cov1")
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("People")
    errors: list[str] = []

    def extra_virtue(dialog, key):
        dialog.set_value(key, VirtueFlawInstance("vf_tough"))
        dialog.try_save()
        errors.append(dialog.error.text())
        dialog.set_value(key, None)

    asked = answering(
        window,
        {"name": "Madoc", "template_grog": "gt_animal_trainer"},
        {"virtue_0": extra_virtue},
    )
    _new(window)["New Grog"].on_click()
    assert asked[1].windowTitle() == "Animal Trainer template"
    assert "Flaw points" in errors[0]
    saga = window.saga
    assert saga is not None
    made = next(c for c in saga.characters if c.name == "Madoc")
    assert made.in_creation and made.creation_xp
    assert window.crumb_names()[-2:] == ["Madoc", "Creation Worksheet"]


def test_new_companion_from_a_quick_recipe_asks_its_choices_first(app):
    """The Definitive Edition's quick Martial companion: the choices form
    opens after New Companion, and using it makes her In Creation with the
    recipe's Virtues and Flaws, on her worksheet."""
    window = _window(_sample_saga_with_covenant())
    window.open_covenant("cov1")
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("People")
    asked = answering(
        window,
        {"name": "Hild", "template_companion": "ct_quick_martial"},
        {"slot_0_1": "bows", "flaw": "vf_dark_secret"},
    )
    _new(window)["New Companion"].on_click()
    assert asked[1].windowTitle() == "Martial companion (DE quick)"
    saga = window.saga
    assert saga is not None
    made = next(c for c in saga.characters if c.name == "Hild")
    assert made.in_creation and made.type == "companion"
    assert VirtueFlawInstance("vf_puissant_ability", {"ability": "bows"}) in (
        made.virtues_flaws
    )
    assert window.crumb_names()[-2:] == ["Hild", "Creation Worksheet"]


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


def test_a_second_new_character_waits_for_the_one_open(app):
    """While New Magus is open, New Magus, New Companion and New Grog
    open no second New Character: the open one is brought forward."""
    window = _window(_sample_saga_with_covenant())
    window.open_covenant("cov1")
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("People")
    window.ask = window._present  # the real one, not a test's
    cards = _new(window)
    before = len(storage.load_saga("test_saga").characters)
    seen: dict[str, object] = {}

    def click_again() -> None:
        first = next(d for d in window.findChildren(FieldsDialog) if d.isVisible())
        for words in ("New Magus", "New Companion", "New Grog"):
            cards[words].on_click()
        shown = [d for d in window.findChildren(FieldsDialog) if d.isVisible()]
        seen["open"] = shown == [first]
        first.reject()

    QTimer.singleShot(0, click_again)
    cards["New Magus"].on_click()
    assert seen == {"open": True}
    assert window._open is None
    assert len(storage.load_saga("test_saga").characters) == before
    window.close()


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


def test_a_long_form_from_saga_management_scrolls_in_its_window(app):
    """Export Pack, with a tick for each of many covenants, opens in a
    window no taller than the screen allows, its ticks scrolling inside it
    above its Export button; the chapter's buttons stay where they are."""
    saga = _sample_saga_with_covenant()
    first = saga.covenants[0]
    saga.covenants += [
        replace(first, id=f"more{i}", name=f"Covenant {i}") for i in range(30)
    ]
    window = _window(saga)
    window.resize(1200, 800)
    _saga_chapter(window, "Saga Management")
    window.ask = window._present  # the real one, not a test's
    seen: dict[str, object] = {}

    def look() -> None:
        form = next(d for d in window.findChildren(FieldsDialog) if d.isVisible())
        seen["window"] = form.isWindow()
        seen["fits"] = form.height() <= TALLEST_WINDOW
        seen["scrolls"] = form.area.verticalScrollBar().maximum() > 0
        seen["export shown"] = form.save.isVisible()
        seen["buttons stay"] = "Export Saga" in _buttons(window)
        form.reject()

    QTimer.singleShot(0, look)
    _buttons(window)["Export Pack"].click()
    assert seen == {
        "window": True,
        "fits": True,
        "scrolls": True,
        "export shown": True,
        "buttons stay": True,
    }
    window.close()


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
    # In A Season's Work, the lab work besides the plan.
    assert "Bind Familiar" not in section_buttons(page, "Planning")
    (bind,) = buttons(page, "Bind Familiar")
    asked = answering(window, {"name": "Ashwing"})
    bind.click()
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


def test_the_tribunal_and_neighbour_pages_edit_from_their_header(app):
    saga = _sample_saga_with_covenant()
    saga.tribunals.append(Tribunal(id="rhine", name="Rhine"))
    saga.neighbours.append(Neighbour(id="mark", name="Count of Mark", kind="lord"))
    window = _window(saga)
    window.open_tribunal("rhine")
    page = window.page()
    assert isinstance(page, TribunalPage)
    assert page.edit_tribunal.toolTip() == "Edit Tribunal"
    assert not buttons(page, "Edit Tribunal")
    window.open_neighbour("mark")
    page = window.page()
    assert isinstance(page, NeighbourPage)
    assert page.edit_neighbour.toolTip() == "Edit Neighbour"
    assert not buttons(page, "Edit Neighbour")
