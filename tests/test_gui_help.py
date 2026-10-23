"""Help on the desktop: ? or F1 or the top bar's Help opens the same help
pages as the terminal's, on the page on show, with a filter and links."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import help_text as ht
from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.help import HelpPage
from ars_magica_manager.gui.window import _HELP_IDS, MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window() -> MainWindow:
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    return MainWindow(saga_ids=[saga.id])


def _help(window: MainWindow) -> HelpPage:
    page = window.page()
    assert isinstance(page, HelpPage)
    return page


def test_help_opens_on_the_chapter_on_show_and_goes_back(app):
    window = _window()
    window.show_character("char1")
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    sheet.open_chapter("Hermetic Magic")
    window.help.click()
    page = _help(window)
    assert window.crumb_names()[-2:] == ["Leandro", "Help"]
    entries = page.entries()
    assert entries[:3] == ["THIS SCREEN", "Hermetic Magic tab", "Character sheet"]
    assert page.topic_id == "tab-hermetic"
    assert "Hermetic Magic tab" in page.shown_text()
    # The trail leads back to the sheet.
    window.go(window.trail[:-1])
    assert isinstance(window.page(), CharacterSheet)


def test_the_filter_lists_what_matches_and_links_show_their_topic(app):
    window = _window()
    window.open_help()
    page = _help(window)
    assert "HOW-TO GUIDES" in page.entries()
    page.filter.setText("vis")
    assert page.entries()[0].startswith("FOUND (")
    assert page.topic_id == ht.book(ht.GUI).search("vis")[0].id
    page._link(QUrl("help:advance-season"))
    assert page.topic_id == "advance-season"
    assert "Advance" in page.shown_text()


def test_about_and_whats_new_come_from_the_core(app):
    window = _window()
    window.open_help()
    page = _help(window)
    page.show_topic(ht.WHATS_NEW)
    assert page.shown_text().startswith("What's New")
    page.show_topic(ht.ABOUT)
    assert "Armarius v" in page.shown_text()


def test_every_desktop_page_has_help_written_for_the_desktop():
    """Each page opens Help on a page the desktop's help has, and none
    of it is the terminal's own."""
    book = ht.book(ht.GUI)
    for kind, ids in _HELP_IDS.items():
        assert ids[0] in book.pages, kind
    assert not [t.id for t in book.topics.values() if t.front_end == ht.TUI]


def test_help_on_the_saga_shows_the_desktop_workspace(app):
    window = _window()
    window.open_help()
    page = _help(window)
    page.show_topic("workspace")
    assert "navigation tree" not in page.shown_text()


def test_a_chapter_named_otherwise_opens_help_on_its_tab(app):
    window = _window()
    window.open_covenant(window.saga.covenants[0].id)
    window.page().codex.rail.setCurrentRow(0)  # Charter
    window.help.click()
    assert _help(window).topic_id == "tab-cov-attributes"


def test_go_there_turns_back_to_the_chapter_the_topic_describes(app):
    window = _window()
    window.show_character("char1")
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    sheet.open_chapter("Hermetic Magic")
    window.help.click()
    page = _help(window)
    assert page.go_there.isEnabled()  # the Hermetic Magic tab
    page.show_topic("tab-vf")
    page.go_there.click()
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    assert sheet.codex.rail.currentItem().text() == "Virtues & Flaws"


def test_go_there_says_where_a_place_on_another_page_is(app):
    window = _window()
    window.show_character("char1")
    window.help.click()
    page = _help(window)
    page.show_topic("tab-lab-totals")
    assert not page.go_there.isEnabled()
    page._link(QUrl("go:tab-lab-totals"))
    assert isinstance(window.page(), HelpPage)
    assert page.note.text().endswith("It is on the Laboratory sheet.")
