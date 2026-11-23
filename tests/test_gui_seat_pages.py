"""Every kind of desktop page in a player's seat: it opens, offers nothing
that changes a record the player doesn't play, and keeps the buttons that
only read (Print to PDF, Cast at a Glance). DESIGN.md, "Who a button is
hidden from", says which code hides what."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from support import everything_saga

from ars_magica_manager import players, seat, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.window import SAGA, MainWindow
from ars_magica_manager.models import Player, Saga, Session

#: Words that open a button changing a record, or playing a fight or siege.
#: Travel, The Hunt and Area Lore stay: anyone works out a journey.
CHANGING = (
    "Add",
    "Edit",
    "Delete",
    "Characteristics",
    "Next ",
    "Battle Event",
    "Begin Project",
    "Choose",
)

#: Each kind of page: how to open it, and a button on it that only reads.
PAGES: dict[str, tuple[Callable[[MainWindow, Saga], None], str | None]] = {
    "saga": (lambda w, _s: w.go(w._up_to(SAGA)), "Previously On"),
    "covenant": (lambda w, s: w.open_covenant(s.covenants[0].id), "Print to PDF"),
    "character": (lambda w, s: w.show_character(s.characters[0].id), "Print to PDF"),
    "laboratory": (
        lambda w, s: w.open_laboratory(s.laboratories[0].id),
        "Print to PDF",
    ),
    "familiar": (lambda w, s: w.open_familiar(s.familiars[0].id), "Print to PDF"),
    "tribunal": (lambda w, s: w.open_tribunal(s.tribunals[0].id), "Print to PDF"),
    "neighbour": (lambda w, s: w.open_neighbour(s.neighbours[0].id), "Print to PDF"),
    "creature": (lambda w, s: w.open_creature(s.creatures[0].id), "Print to PDF"),
    "fight": (lambda w, s: w.open_fight(s.fights[0].id), None),
    "siege": (lambda w, s: w.open_siege(s.sieges[0].id), None),
    "session": (lambda w, s: w.open_session(s.sessions[0].id), "Cast at a Glance"),
    "store": (lambda w, _s: w.open_store("armarium"), None),
    "seasons": (lambda w, _s: w.open_seasons(), "Calendar"),
}


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


@pytest.fixture
def window(app: QApplication) -> Iterator[MainWindow]:
    """The sample saga in the seat of Ana, a player who plays none of it."""
    saga = everything_saga()
    saga.players = [Player(id="ana", name="Ana", role=players.PLAYER)]
    saga.sessions = [Session("s1", real_date="2026-11-21")]
    storage.save_saga(saga)
    shown = MainWindow(saga_ids=[saga.id])
    shown.show()
    assert shown.saga is not None
    shown.sit_as(shown.saga.players[0])
    yield shown
    seat.sign_out()
    shown.close()
    shown.deleteLater()
    QApplication.processEvents()


def _shown(window: MainWindow) -> set[str]:
    page = window.page()
    assert page is not None
    return {
        b.text().strip()
        for b in page.findChildren(QPushButton)
        if b.text().strip() and not b.isHidden()
    }


@pytest.mark.parametrize("kind", list(PAGES))
def test_a_player_reads_every_page_and_changes_nothing(
    window: MainWindow, kind: str
) -> None:
    open_page, reads = PAGES[kind]
    assert window.saga is not None
    open_page(window, window.saga)
    assert not isinstance(window.page(), QLabel), "a page, not a stand-in label"
    shown = _shown(window)
    assert not {b for b in shown if b.startswith(CHANGING)}, kind
    if reads is not None:
        assert reads in shown
