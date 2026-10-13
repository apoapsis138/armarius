"""The desktop's switches: Show everything on a list to choose from (the
terminal's F3), turning a laboratory's Specialization off and on, and
giving several books one new owner, answered without showing the dialogs
(gui_steps.answering)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, everything, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog
from ars_magica_manager.gui.laboratory import LaboratoryPage
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import LabSpecialtyEntry


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    return MainWindow(saga_ids=[saga.id])


def test_show_everything_lists_a_spell_from_a_book_not_in_play(app):
    saga = _sample_saga_with_covenant()
    # Only the core book is in play: the catalog's other spells are hidden.
    saga.books_in_play = []
    window = _window(saga)
    window.show_character("char1")
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Hermetic Magic")
    seen: dict[str, object] = {}

    def look(dialog: ChooseDialog) -> None:
        offered = dialog.shown()
        dialog.everything.setChecked(True)
        seen["more"] = len(dialog.shown()) - len(offered)
        marked = next(s for s in dialog.shown() if s.endswith("(book not in play)"))
        seen["marked"] = marked
        dialog.choose(marked)

    answering(window, look)
    section_buttons(page, "Known Spells")["Add"].click()
    assert isinstance(seen["more"], int) and seen["more"] > 0
    known = storage.load_saga(saga.id).characters[0].spells_known
    assert len(known) == 2  # the magus's own, and the one out of play


def test_show_everything_lists_a_virtue_the_rules_refuse(app):
    saga = _sample_saga_with_covenant()
    window = _window(saga)
    window.show_character("char1")
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Virtues & Flaws")
    asked = answering(window, None)
    title = next(
        label.text()
        for label in page.findChildren(QLabel)
        if label.text().startswith("Virtues  ·")
    )
    section_buttons(page, title)["Add"].click()
    dialog = asked[0]
    assert isinstance(dialog, ChooseDialog)
    offered = dialog.shown()
    dialog.everything.setChecked(True)
    marked = [s for s in dialog.shown() if s not in offered]
    assert marked and all(s.endswith(")") for s in marked)
    dialog.everything.setChecked(False)
    assert dialog.shown() == offered
    # everything() ticks it and chooses in one answer.
    assert callable(everything(marked[0]))


def test_a_labs_specialization_is_turned_off_and_on(app):
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    lab.specialties = [LabSpecialtyEntry("Ignem", 2, "a fiery spring")]
    window = _window(saga)
    window.open_laboratory(lab.id)
    page = window.page()
    assert isinstance(page, LaboratoryPage)
    answering(window)
    section_buttons(page, "Art Specializations")["Turn Off/On"].click()
    saved = storage.load_saga(saga.id).laboratories[0]
    assert saved.dropped_specializations == ["Ignem"]
    page = window.page()
    assert isinstance(page, LaboratoryPage)
    section_buttons(page, "Art Specializations")["Turn Off/On"].click()
    assert storage.load_saga(saga.id).laboratories[0].dropped_specializations == []


def test_several_books_are_given_one_new_owner(app):
    saga = _sample_saga_with_covenant()
    window = _window(saga)
    window.open_covenant("cov1")
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("Library")
    asked = answering(
        window,
        {"owner": "character:char1", "book_0": True, "book_1": True},
        True,
    )
    section_buttons(page, "Library")["Change Owner"].click()
    assert isinstance(asked[1], ConfirmDialog)
    assert "2 books" in asked[1].question
    books = storage.load_saga(saga.id).books
    assert [(b.owner_kind, b.owner_id) for b in books] == [("character", "char1")] * 2
