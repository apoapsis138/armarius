"""The desktop Saga Content page's Add, Edit and Delete buttons."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import house_rules as hr
from ars_magica_manager import saga_content as sc
from ars_magica_manager import spells as spl
from ars_magica_manager import storage, traditions
from ars_magica_manager.forms import saga_content as scf
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.markup_html import plain
from ars_magica_manager.gui.saga_content import SagaContentPage
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.widgets import ClickableCard, ToggleSwitch
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.sheets import saga_content as scs


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _content(chapter: str) -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_content()
    _page(window).codex.open_chapter(chapter)
    return window, saga.id


def _page(window: MainWindow) -> SagaContentPage:
    page = window.page()
    assert isinstance(page, SagaContentPage)
    return page


def test_a_saga_source_is_added_edited_and_refused_while_cited(app):
    window, saga_id = _content("Books")
    asked = answering(window, {"abbreviation": "HR", "title": "Ours"})
    controls = section_buttons(_page(window), "Saga Sources")
    assert not controls["Edit"].isEnabled()
    controls["Add"].click()
    assert asked[0].windowTitle() == "Add a Saga Source"
    assert [s.abbreviation for s in storage.load_saga(saga_id).sources] == ["HR"]
    # The page is drawn again at the same chapter, the one row chosen.
    assert _page(window).codex.rail.currentItem().text() == "Books"
    answering(window, {"title": "Our rules"})
    section_buttons(_page(window), "Saga Sources")["Edit"].click()
    assert storage.load_saga(saga_id).sources[0].title == "Our rules"
    saga = window.saga
    assert saga is not None
    hr.add(
        saga,
        hr.CHARACTER,
        {"name": "X", "type": "Virtue", "tier": "Minor", "source": "HR"},
    )
    answering(window)
    section_buttons(_page(window), "Saga Sources")["Delete"].click()
    assert [why for _title, why in window.told] == [
        "HR is cited by X: change them first."
    ]
    assert saga.sources


def test_a_saga_spell_is_added_and_deleted(app):
    window, saga_id = _content("Spells")
    answering(
        window,
        {
            "name": "Spark",
            "technique": "Creo",
            "form": "Ignem",
            "level": "5",
            "range": "Touch",
            "duration": "Momentary",
            "target": "Individual",
        },
    )
    section_buttons(_page(window), "Spells")["Add"].click()
    before = [s.name for s in storage.load_saga(saga_id).spells]
    assert "Spark" in before
    page = _page(window)
    page.spell_source.setCurrentIndex(page.spell_source.findData(spl.OWN_SOURCE))
    page.spell_search.setText("Spark")
    controls = section_buttons(page, "Spells")
    assert controls["Delete"].isEnabled()  # the only spell shown
    asked = answering(window, True)
    controls["Delete"].click()
    assert asked[0].question == "Delete Spark?"  # type: ignore[attr-defined]
    after = [s.name for s in storage.load_saga(saga_id).spells]
    assert after == [name for name in before if name != "Spark"]


def test_a_catalog_entry_is_hidden_by_catalog_then_entry(app):
    window, saga_id = _content("Catalogs")
    entry = scf.hideable(window.saga, "abilities")[0]
    label = plain(scf.entry_choice(entry).label)
    answering(window, {"catalog": "abilities"}, label)
    section_buttons(_page(window), "Hidden Entries")["Hide"].click()
    assert storage.load_saga(saga_id).hidden_entries == {"abilities": [entry.id]}
    asked = answering(window, True)
    section_buttons(_page(window), "Hidden Entries")["Offer again"].click()
    assert len(asked) == 1
    assert storage.load_saga(saga_id).hidden_entries == {}


def test_a_cult_its_degree_and_its_script_are_added(app):
    """The Mystery Cults chapter: Add a cult, a degree of it, then the
    degree's Script (Add on its Script, while it has none); Experiment on a
    Script is offered only for a degree with no Script."""
    window, saga_id = _content("Mystery Cults")
    answering(window, {"name": "The Thread", "lore": "Thread Lore"})
    section_buttons(_page(window), "The Saga's Mystery Cults")["Add"].click()
    assert [c.name for c in storage.load_saga(saga_id).custom_cults] == ["The Thread"]
    assert _page(window).codex.rail.currentItem().text() == "Mystery Cults"

    answering(window, {"name": "Spinner", "virtue_id": "vf_second_sight"})
    section_buttons(_page(window), "Degrees")["Add"].click()
    degrees = storage.load_saga(saga_id).custom_cults[0].degrees
    assert [(d.name, d.virtue_id) for d in degrees] == [("Spinner", "vf_second_sight")]
    # A Mystagogue's experiment is on her own Deeds chapter, not here.
    controls = section_buttons(_page(window), "Degrees")
    assert "Experiment on a Script" not in controls

    answering(window, {"name": "The Silk Hall", "place": True, "quests": 1})
    section_buttons(_page(window), "Spinner: no Script yet")["Add"].click()
    script = storage.load_saga(saga_id).custom_cults[0].degrees[0].script
    assert script is not None and (script.name, script.bonus) == ("The Silk Hall", 6)
    assert "The Silk Hall: +6" in [
        label.text() for label in _page(window).findChildren(QLabel)
    ]


def _chip(page: SagaContentPage, book: str) -> QWidget:
    """The in-play chip on `book`'s card (a button for a supplement, a
    label for the core book)."""
    badge = next(label for label in page.findChildren(QLabel) if label.text() == book)
    card = badge.parentWidget()
    assert card is not None
    return next(
        w
        for w in card.findChildren(QWidget)
        if w.objectName() == "chip" or (isinstance(w, QLabel) and w.text() == "Always")
    )


def _books_title(page: SagaContentPage) -> str:
    return next(
        label.text()
        for label in page.findChildren(QLabel)
        if label.text().startswith("Books in Play (")
    )


def test_a_books_chip_puts_it_in_or_out_of_play(app):
    window, saga_id = _content("Books")
    saga = window.saga
    assert saga is not None
    sc.set_books_in_play(saga, ["Covenants"])
    storage.save_saga(saga)
    window.redraw()
    page = _page(window)
    every = len(sc.every_book(saga))
    assert _books_title(page) == f"Books in Play (2 of {every})"
    core = _chip(page, "DE")
    assert not isinstance(core, QPushButton)
    assert "always in play" in core.toolTip()
    chip = _chip(page, "RoP:F")
    assert isinstance(chip, QPushButton) and chip.text() == "Not in play"
    chip.click()
    assert storage.load_saga(saga_id).books_in_play == ["Covenants", "RoP:F"]
    page = _page(window)
    assert page.codex.rail.currentItem().text() == "Books"
    assert _books_title(page) == f"Books in Play (3 of {every})"
    chip = _chip(page, "RoP:F")
    assert chip.text() == "In play"
    chip.click()
    assert storage.load_saga(saga_id).books_in_play == ["Covenants"]


#: Widgets the Books chapter builds for the sample saga (47 book cards
#: and their group headings, and the sources); the traditions are
#: drawn on their own chapter. Raise a budget only deliberately.
BOOKS_WIDGET_BUDGET = 310


def test_the_books_chapter_stays_within_its_widget_budget(app):
    page = SagaContentPage(_sample_saga_with_covenant(), SCRIPTORUM)
    built = len(page._books().findChildren(QWidget))
    assert built <= BOOKS_WIDGET_BUDGET, built


def _tradition_card(page: SagaContentPage, name: str) -> ClickableCard:
    return next(
        card
        for card in page.findChildren(ClickableCard)
        if any(label.text() == name for label in card.findChildren(QLabel))
    )


def test_traditions_are_cards_offered_by_book_or_one_by_one(app):
    window, saga_id = _content("Traditions")
    saga = window.saga
    assert saga is not None
    sc.set_books_in_play(saga, ["HMRE"])
    storage.save_saga(saga)
    window.redraw()
    page = _page(window)
    assert page.codex.rail.currentItem().text() == "Traditions"
    # No Edit beside the section: the switches are its controls.
    with pytest.raises(AssertionError, match="with buttons"):
        section_buttons(page, "Traditions Offered")
    hedge = [
        t.id for t in traditions.listed(saga) if traditions.book_of(t, saga) == "HMRE"
    ]
    # The headings' switches come first in each group, in tradition_groups'
    # order: Hedge Magic's offers all of them, so clicking it offers none.
    groups = scs.tradition_groups(saga)
    headings = [
        s
        for s in page.findChildren(ToggleSwitch)
        if "of them" in s.toolTip() or "its traditions" in s.toolTip()
    ]
    headings[[g.book for g in groups].index("HMRE")].click()
    assert storage.load_saga(saga_id).traditions_off == hedge
    page = _page(window)
    card = _tradition_card(page, "Vitkir")
    # Two lines: the name and its switch, then its kind.
    assert [lb.text() for lb in card.findChildren(QLabel)] == [
        "Vitkir",
        "Hedge Tradition",
    ]
    card.findChild(ToggleSwitch).click()
    assert "trad_vitkir" not in storage.load_saga(saga_id).traditions_off
    # A book out of play: its cards greyed out, their switches dead.
    page = _page(window)
    assert not _tradition_card(page, "Ascetics").findChild(ToggleSwitch).isEnabled()


def test_a_traditions_inspector_shows_it_with_a_switch_of_its_own(app):
    window, saga_id = _content("Traditions")
    page = _page(window)
    card = _tradition_card(page, "Vitkir")
    card.clicked()
    inspector = page.codex.inspector
    assert inspector.title.text() == "Vitkir"
    assert inspector.subtitle.text() == "Hedge Tradition"
    assert "Adds:" in plain(inspector.body.text()) or "Adds" in inspector.body.text()
    switch = inspector.action
    assert isinstance(switch, ToggleSwitch) and switch.isChecked()
    switch.click()
    assert storage.load_saga(saga_id).traditions_off == ["trad_vitkir"]
    # The page is drawn again with the tradition still in the inspector.
    page = _page(window)
    assert page.codex.inspector.title.text() == "Vitkir"
    action = page.codex.inspector.action
    assert isinstance(action, ToggleSwitch) and not action.isChecked()


def test_the_traditions_are_drawn_only_when_turned_to(app):
    page = SagaContentPage(_sample_saga_with_covenant(), SCRIPTORUM)
    assert not page.findChildren(ToggleSwitch)
    page.codex.open_chapter("Traditions")
    assert page.findChildren(ToggleSwitch)
