"""The desktop covenant page's Add, Edit and Delete buttons: one flow per
kind of section (a single-record Edit, a catalog choice then a form, a
table, an empty section, the library's shelves and the Diary's cards).
Each saves the saga, so the saved copy is checked."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QPushButton
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.figures import BookSpine
from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog, FieldsDialog
from ars_magica_manager.gui.markup_html import plain
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import CovenantDiaryEntry, IncomeSource


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga=None) -> MainWindow:
    saga = saga or _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant(saga.covenants[0].id)
    return window


def _page(window: MainWindow) -> CovenantPage:
    page = window.page()
    assert isinstance(page, CovenantPage)
    return page


def _saved(window: MainWindow):
    assert window.saga is not None
    return storage.load_saga(window.saga.id).covenants[0]


def test_edit_covenant_and_its_description(app):
    window = _window()
    asked = answering(window, {"name": "Fengheld"}, {"notes": "Windswept."})
    # Edit Covenant is the header's Edit, beside the covenant's season.
    header_edit = next(
        b
        for b in _page(window).findChildren(QPushButton)
        if b.toolTip() == "Edit Covenant"
    )
    header_edit.click()
    assert asked[0].windowTitle() == "Edit Covenant"
    assert "Edit Covenant" not in section_buttons(_page(window), "The Covenant")
    assert _saved(window).name == "Fengheld"
    section_buttons(_page(window), "The Covenant")["Edit Description"].click()
    assert _saved(window).notes == "Windswept."


def test_adding_a_boon_chooses_it_from_the_catalog_then_names_it(app):
    window = _window()
    assert window.saga is not None
    wealth = next(
        plain(c.label)
        for c in covenant_forms.boon_hook_choices(
            window.saga, window.saga.covenants[0], "Boon"
        )
        if c.value.id == "covbh_boon_major_wealth"
    )
    asked = answering(window, wealth, {"detail": "a silver mine"})
    section_buttons(_page(window), "Boons")["Add"].click()
    assert isinstance(asked[0], ChooseDialog) and isinstance(asked[1], FieldsDialog)
    assert asked[1].windowTitle() == "Boon: Wealth"
    # A covenant's steps open as windows over the page, one after another.
    assert not any(getattr(d, "inline", True) for d in asked)
    saved = _saved(window)
    assert [bh.vf_id for bh in saved.boons_hooks] == ["covbh_boon_major_wealth"]
    # Its card is the only Boon, so Delete acts on it; No keeps it.
    answering(window, False)
    section_buttons(_page(window), "Boons")["Delete"].click()
    assert _saved(window).boons_hooks
    asked = answering(window, True)
    section_buttons(_page(window), "Boons")["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog) and not asked[0].inline
    assert asked[0].question == "Delete Wealth - a silver mine?"
    assert _saved(window).boons_hooks == []


def test_an_empty_inhabitant_section_adds_and_its_table_row_is_edited(app):
    window = _window()
    controls = section_buttons(_page(window), "Turb")
    assert not controls["Edit"].isEnabled()
    answering(window, {"name": "The watch", "quantity": "6"})
    controls["Add"].click()
    assert [i.name for i in _saved(window).inhabitants] == ["The watch"]
    page = _page(window)
    table = page.tables["turb"]
    table.setCurrentIndex(table.model().index(0, 0))
    asked = answering(window, {"responsibility": "Walls"})
    section_buttons(page, "Turb")["Edit"].click()
    assert asked[0].windowTitle() == "Edit The watch"
    assert _saved(window).inhabitants[0].responsibility == "Walls"


def test_editing_loyalty_and_a_source_of_income(app):
    saga = _sample_saga_with_covenant()
    saga.covenants[0].economics.income_sources = [
        IncomeSource("s1", "Mill", income=40),
        IncomeSource("s2", "Tolls", income=10),
    ]
    window = _window(saga)
    asked = answering(window, {"familiarity": "2"})
    section_buttons(_page(window), "Loyalty")["Edit"].click()
    assert _saved(window).loyalty.familiarity == 2
    # Its window is wide enough for its long labels and the fields beside
    # them, and tall enough that the fields need no scrolling.
    loyalty = asked[0]
    assert isinstance(loyalty, FieldsDialog) and loyalty.width() > 700
    loyalty.show()
    QApplication.processEvents()
    assert loyalty.body.sizeHint().width() <= loyalty.area.viewport().width()
    assert loyalty.height() < 820
    assert loyalty.area.verticalScrollBar().maximum() == 0
    loyalty.close()
    page = _page(window)
    controls = section_buttons(page, "Sources of Income")
    assert not controls["Edit"].isEnabled()  # two rows, none chosen
    table = page.tables["income"]
    table.setCurrentIndex(table.model().index(1, 0))
    assert controls["Edit"].isEnabled()
    asked = answering(window, {"income": "15"})
    controls["Edit"].click()
    assert asked[0].windowTitle() == "Edit Tolls"
    assert [s.income for s in _saved(window).economics.income_sources] == [40, 15]


def test_a_book_is_added_to_the_library_and_a_chosen_one_deleted(app):
    window = _window()
    answering(
        window,
        {
            "name": "De Igne",
            "type": "Tractatus",
            "subject_kind": "Art",
            "art": "Ignem",
            "quality": "7",
        },
    )
    section_buttons(_page(window), "Library")["Add"].click()
    assert window.saga is not None
    saved = storage.load_saga(window.saga.id)
    assert [b.name for b in saved.books][-1] == "De Igne"
    page = _page(window)
    spine = next(
        s for s in page.findChildren(BookSpine) if s.spine.book.name == "De Igne"
    )
    spine.clicked()
    asked = answering(window, True)
    section_buttons(page, "Library")["Delete"].click()
    assert asked[0].question == "Delete De Igne?"
    saved = storage.load_saga(window.saga.id)
    assert "De Igne" not in [b.name for b in saved.books]


def test_a_diary_entry_is_added_and_its_card_edited(app):
    saga = _sample_saga_with_covenant()
    saga.covenants[0].diary = [
        CovenantDiaryEntry(year=1219, season="Spring", name="Founded"),
    ]
    window = _window(saga)
    answering(window, {"name": "Bought a mill", "pounds": "-12"})
    section_buttons(_page(window), "Diary")["Add"].click()
    diary = _saved(window).diary
    assert [e.name for e in diary] == ["Founded", "Bought a mill"]
    page = _page(window)
    founded = next(
        card
        for card in page.findChildren(ClickableCard)
        if any(
            "Founded" in label.text()
            for label in card.findChildren(type(page.inspector.title))
        )
    )
    founded.clicked()
    asked = answering(window, {"details": "In the hills."})
    section_buttons(page, "Diary")["Edit"].click()
    assert asked[0].windowTitle() == "Edit a Diary Entry"
    assert _saved(window).diary[0].details == "In the hills."


def test_improve_acts_on_the_source_of_income_chosen(app):
    saga = _sample_saga_with_covenant()
    saga.covenants[0].economics.income_sources = [
        IncomeSource("s1", "Mill", income=40),
        IncomeSource("s2", "Tolls", income=10),
    ]
    window = _window(saga)
    page = _page(window)
    page.codex.open_chapter("Treasury")
    controls = section_buttons(page, "Sources of Income")
    assert not controls["Improve"].isEnabled()
    table = page.tables["income"]
    table.setCurrentIndex(table.model().index(1, 0))
    asked = answering(window, {"effect": "Status Quo"}, True)
    controls["Improve"].click()
    assert asked[0].windowTitle() == "Improve Tolls"


def test_add_on_the_magi_takes_in_a_magus_of_the_saga(app):
    from ars_magica_manager.models import Character, Covenant

    saga = _sample_saga_with_covenant()
    saga.covenants.append(Covenant(id="cov2", saga_id=saga.id, name="Elsewhere"))
    saga.characters.append(
        Character(id="mag2", name="Far Away", type="magus", covenant_id="cov2")
    )
    window = _window(saga)
    page = _page(window)
    page.codex.open_chapter("Covenfolk")
    chapter = page.codex.pages.currentWidget()
    assert chapter is not None
    asked = answering(window, "Far Away  (of Elsewhere)", True)
    section_buttons(chapter, "Magi")["Add"].click()
    assert asked[1].question.startswith("Move Far Away from Elsewhere")
    assert window.saga is not None
    saved = storage.load_saga(window.saga.id)
    assert saved.character("mag2").covenant_id == "cov1"
