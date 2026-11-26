"""The desktop's Session page: opened by Open on a Sessions row, it shows
the Session's facts and its buttons (gui/session_page.py)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from ars_magica_manager import (
    chronicle,
    commands,
    players,
    seat,
    storage,
    virtual_tabletop,
)
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.session_page import SessionPage
from ars_magica_manager.gui.sessions_section import sessions_section
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import (
    AccountLine,
    Casting,
    Character,
    Player,
    Saga,
    Session,
)


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.sessions = [
        Session(
            "s1",
            real_date="2026-11-21",
            coming=["ana"],
            castings=[Casting("ana", "aelfric")],
        )
    ]
    return saga


def _window() -> MainWindow:
    storage.save_saga(_saga())
    window = MainWindow(saga_ids=["fengheld"])
    window.show()
    assert window.saga is not None
    return window


def _words(widget) -> str:
    return " ".join(label.text() for label in widget.findChildren(QLabel))


def _buttons(widget) -> dict[str, QPushButton]:
    return {b.text().strip(): b for b in widget.findChildren(QPushButton)}


@pytest.mark.usefixtures("app")
def test_open_on_a_sessions_row_opens_its_page() -> None:
    ran: list = []
    shown = sessions_section(_saga(), SCRIPTORUM, ran.append, lambda *_: None)
    _buttons(shown)["Open"].click()

    [step] = ran
    assert isinstance(step, commands.Act)
    went = step.apply()
    assert isinstance(went, commands.Go)
    assert (went.ref.kind, went.ref.id) == ("sessions", "s1")


@pytest.mark.usefixtures("app")
def test_the_window_shows_a_sessions_page_with_its_facts() -> None:
    window = _window()
    window.open_session("s1")
    page = window.page()

    assert isinstance(page, SessionPage)
    assert window.crumb_names()[-1] == "Session of 21 Nov 2026"
    words = _words(page)
    assert "Planned" in words
    assert "Ana as Aelfric" in words
    assert {"Edit", "Cast at a Glance", "Print the Cast"} <= set(_buttons(page))
    assert not {"Begin Session", "End Session", "Chronicle"} & set(_buttons(page))


@pytest.mark.usefixtures("app")
def test_a_player_still_reads_the_cast_at_a_glance() -> None:
    window = _window()
    saga = window.saga
    assert saga is not None
    saga.players[0].role = players.PLAYER
    window.sit_as(saga.players[0])
    try:
        window.open_session("s1")
        shown = {b for b, w in _buttons(window.page()).items() if not w.isHidden()}
        assert "Cast at a Glance" in shown
        assert "Edit" not in shown
    finally:
        seat.sign_out()


@pytest.mark.usefixtures("app")
def test_the_preview_adds_begin_to_the_page_and_edit_edits_its_session() -> None:
    virtual_tabletop.set_on(True)
    window = _window()
    ran: list = []
    window.run = lambda command, *a, **k: ran.append(command)  # type: ignore[method-assign]
    window.open_session("s1")
    page = window.page()
    buttons = _buttons(page)

    assert "Begin Session" in buttons
    assert "The evening" not in _words(page)  # planned: nothing yet
    buttons["Edit"].click()
    [step] = ran
    assert isinstance(step, commands.Form)
    assert step.title == "Edit the Session of 21 Nov 2026"


@pytest.mark.usefixtures("app")
def test_a_played_sessions_page_reads_the_evening_by_scene() -> None:
    saga = _saga()
    session = saga.sessions[0]
    session.played = True
    session.account = [
        AccountLine("roll", "Storyguide: Stress die 7, +0 = 7"),
        AccountLine(
            "scene set", "Scene: The ford, at A ford", scene="The ford", play=1
        ),
        AccountLine(
            "roll",
            "Aelfric: Stress die 2 [Blind]",
            chronicle.STORYGUIDE,
            [],
            "The ford",
            play=1,
        ),
    ]

    page = SessionPage(saga, session, SCRIPTORUM, lambda _command: None)
    scenes = [w.text() for w in page.findChildren(QLabel, "evening-scene")]
    lines = [w.text() for w in page.findChildren(QLabel, "evening-line")]

    assert "The evening" in _words(page)
    assert scenes == ["Before the first Scene", "The ford"]
    assert lines == [
        "Storyguide: Stress die 7, +0 = 7",
        "Scene: The ford, at A ford",
        "Aelfric: Stress die 2 [Blind]",  # the host is its storyguide
    ]
