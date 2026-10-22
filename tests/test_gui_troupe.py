"""The Troupe on the desktop: the saga page's first chapter, holding the
player characters, the troupe's covenants and what the reader starred;
the Star at the top of a record's page; and a page reopening on the
chapter it was left at."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

from ars_magica_manager import storage, troupe
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.bookmark import Ribbon
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.pages import SagaPage
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Character, Covenant, Neighbour, Saga


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _saga() -> Saga:
    """The troupe's covenant with a player's magus and a grog nobody plays,
    and one neighbour."""
    magus = Character(id="pc1", name="Leandro", type="magus", covenant_id="home")
    magus.background.player = "Hedda"
    return Saga(
        id="troupe_saga",
        name="Troupe Saga",
        covenants=[Covenant(id="home", saga_id="troupe_saga", name="Fengheld")],
        characters=[
            magus,
            Character(id="npc", name="Gunther", type="grog", covenant_id="home"),
        ],
        neighbours=[Neighbour(id="n1", name="The Bishop")],
    )


def _window() -> MainWindow:
    saga = _saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def _words(widget) -> str:
    return " ".join(label.text() for label in widget.findChildren(QLabel))


def _troupe_cards(window: MainWindow) -> list[ClickableCard]:
    page = window.page()
    assert isinstance(page, SagaPage)
    assert page.codex.rail.currentItem().text() == "The Troupe"
    return page.codex.chapter(0).findChildren(ClickableCard)


def test_the_saga_opens_on_the_troupe_a_click_from_each_player(app):
    window = _window()
    cards = _troupe_cards(window)
    words = [_words(c) for c in cards]
    assert any("Leandro" in w for w in words)
    assert any("Fengheld" in w for w in words)  # the troupe's covenant
    assert not any("Gunther" in w for w in words)  # nobody plays him
    [leandro] = [c for c in cards if "Leandro" in _words(c)]
    leandro.clicked()
    assert isinstance(window.page(), CharacterSheet)
    assert window.crumb_names()[-1] == "Leandro"


def _ribbon(window: MainWindow) -> Ribbon:
    [ribbon] = window.page().findChildren(Ribbon)  # type: ignore[union-attr]
    return ribbon


def test_the_ribbon_bookmarks_a_page_into_the_troupe(app):
    window = _window()
    assert window.page().findChildren(Ribbon) == []  # type: ignore[union-attr]
    window.open_neighbour("n1")
    assert not _ribbon(window).isChecked()
    _ribbon(window).click()
    assert troupe.is_bookmarked("troupe_saga", "neighbour", "n1")
    window.go(window.trail[:2])
    assert any("The Bishop" in _words(c) for c in _troupe_cards(window))
    window.open_neighbour("n1")
    assert _ribbon(window).isChecked()
    _ribbon(window).click()
    window.go(window.trail[:2])
    assert not any("The Bishop" in _words(c) for c in _troupe_cards(window))


def test_every_record_page_has_its_ribbon(app):
    window = _window()
    window.open_covenant("home")
    assert _ribbon(window).kind == "covenant"
    window.show_character("npc")
    assert _ribbon(window).record_id == "npc"
    window.open_covenant(None)  # the characters of no covenant: no record
    assert window.page().findChildren(Ribbon) == []  # type: ignore[union-attr]


def test_a_page_reopens_on_the_chapter_it_was_left_at(app):
    window = _window()
    window.open_covenant("home")
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("People")
    window.show_character("pc1")
    window.back()
    page = window.page()
    assert isinstance(page, CovenantPage)
    assert page.codex.rail.currentItem().text() == "People"
