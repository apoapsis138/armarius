"""A player's seat on the desktop: the storyguide sits in a named player's
seat (Play as) and the window is drawn for them (seat.py)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from ars_magica_manager import players, seat, storage, viewing
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.widgets import ClickableCard, NewCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Character, Covenant, Player, Saga


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


@pytest.fixture(autouse=True)
def _empty_seat():
    yield
    seat.sign_out()


def _saga() -> Saga:
    ana = Player(id="p1", name="Ana", role=players.PLAYER)
    ben = Player(id="p2", name="Ben", role=players.PLAYER)
    mine = Character(id="pc1", name="Leandro", type="magus", covenant_id="home")
    mine.background.player_ids = [ana.id]
    theirs = Character(id="pc2", name="Bertrand", type="magus", covenant_id="home")
    theirs.background.player_ids = [ben.id]
    return Saga(
        id="seat_saga",
        name="Seat Saga",
        covenants=[Covenant(id="home", saga_id="seat_saga", name="Fengheld")],
        characters=[mine, theirs],
        players=[ana, ben],
    )


def _window(saga: Saga | None = None) -> MainWindow:
    saga = saga or _saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def test_the_seat_menu_is_offered_when_the_saga_has_players(app):
    window = _window()
    assert not window.seat_button.isHidden()
    assert window.seat_button.text().strip() == ""


def test_no_seat_menu_in_a_saga_without_players(app):
    saga = _saga()
    saga.players = []
    window = _window(saga)
    assert window.seat_button.isHidden()


def test_sitting_as_a_player_seats_them_and_back(app):
    window = _window()
    assert viewing.current().is_storyguide
    ana = window.saga.players[0]
    window.sit_as(ana)
    assert viewing.current().kind == viewing.PLAYER
    assert viewing.current().player is ana
    assert "Ana" in window.seat_button.text()
    assert window.view_button.isHidden()  # Player view is the storyguide's
    assert storage.guard is not None
    window.sit_as(None)
    assert viewing.current().is_storyguide
    assert storage.guard is None
    assert not window.view_button.isHidden()


def test_a_player_is_told_what_a_save_took_back(app):
    window = _window()
    told: list[tuple[str, str]] = []
    window.tell = lambda title, words: told.append((title, words))  # type: ignore[method-assign]
    window.sit_as(window.saga.players[0])
    assert storage.guard is not None
    storage.guard({"current_year": 1220}, {"current_year": 1221})
    assert told and "current_year" in told[0][1]


def _chapter(window: MainWindow):
    return window.page().codex.chapter(0)  # type: ignore[union-attr]


def _cards(window: MainWindow) -> list[str]:
    return [
        " ".join(label.text() for label in card.findChildren(QLabel))
        for card in _chapter(window).findChildren(ClickableCard)
    ]


def _labels(window: MainWindow) -> str:
    return " ".join(label.text() for label in _chapter(window).findChildren(QLabel))


def test_a_player_lands_on_their_characters_then_the_troupes(app):
    window = _window()
    words = _cards(window)
    assert any("Leandro" in w for w in words) and any("Bertrand" in w for w in words)
    window.sit_as(window.saga.players[0])  # Ana
    words = _cards(window)
    assert "Leandro" in words[0]  # hers first
    assert sum("Leandro" in w for w in words) == 1  # and not shown twice
    assert any("Bertrand" in w for w in words)  # the troupe's are seen too
    assert "Your Characters (1)" in _labels(window)
    assert "The Troupe's Characters (1)" in _labels(window)


def test_a_player_with_no_character_is_told(app):
    saga = _saga()
    saga.characters[0].background.player_ids = []
    saga.characters[0].background.player = ""
    window = _window(saga)
    window.sit_as(saga.players[0])
    assert "Your Characters (0)" in _labels(window)
    assert "Make one with New Character" in _labels(window)
    news = [c.words for c in _chapter(window).findChildren(NewCard)]
    assert news == ["New Character"]


def _verbs(window: MainWindow) -> set[str]:
    """The Add / Edit / Delete buttons on the page on show."""
    return {
        b.text().strip()
        for b in window.page().findChildren(QPushButton)  # type: ignore[union-attr]
        if b.text().strip() in ("Add", "Edit", "Delete") and not b.isHidden()
    }


def test_a_players_sheet_has_buttons_only_for_their_own_character(app):
    window = _window()
    window.show_character("pc2")
    assert _verbs(window)  # the storyguide's
    window.sit_as(window.saga.players[0])  # Ana
    window.show_character("pc2")  # Ben's character: read only
    assert _verbs(window) == set()
    window.show_character("pc1")  # her own
    assert {"Add", "Edit"} <= _verbs(window)


def test_a_player_has_no_advance_season(app):
    window = _window()
    window.show_character("pc1")
    assert window.season_panel is not None
    window.sit_as(window.saga.players[0])
    window.show_character("pc1")
    assert window.season_panel is None
    window.sit_as(None)
    window.show_character("pc1")
    assert window.season_panel is not None


def test_closing_the_saga_empties_the_seat(app):
    window = _window()
    window.sit_as(window.saga.players[0])
    window.player = None
    window.saga = None
    window._use_viewer()
    assert viewing.current().is_storyguide
    assert storage.guard is None
