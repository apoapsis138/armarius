"""Begin Session, End Session and the Chronicle on the Sessions list:
offered only with the Virtual Tabletop (Preview) on, and only to the
Session's storyguide (forms/sessions.py, through the More registry of
ADR 0006, so the terminal and the desktop do the same)."""

from __future__ import annotations

import pytest

from ars_magica_manager import actions, chronicle, commands, virtual_tabletop
from ars_magica_manager import sessions as ss
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import menu_refresh
from ars_magica_manager.models import Player, Saga, Session
from ars_magica_manager.sections import SESSIONS_SECTION

VERBS = ("begin_session", "close_session", "read_chronicle")


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana")]
    saga.sessions = [Session("s1", real_date="2026-11-20"), Session("s2")]
    return saga


def _page(saga: Saga, row: int | None = 0) -> menu_forms.Page:
    return menu_forms.Page(saga, NodeKind.SAGA, section=SESSIONS_SECTION, row=row)


def _offered(saga: Saga, row: int | None = 0) -> set[str]:
    page = _page(saga, row)
    return {
        item.action
        for item in actions.MORE_MENU
        if item.action in VERBS
        and actions.MORE_SECTIONS.get(item.action) == SESSIONS_SECTION
        and actions.available(item.action, page)
    }


def _run(saga: Saga, action: str, row: int = 0) -> object:
    return menu_forms._COMMANDS[action](_page(saga, row))


def _words(step: object) -> str:
    """What a read-only Form shows."""
    assert isinstance(step, commands.Form)
    return str(step.fields()[0].value)


@pytest.fixture
def preview() -> None:
    virtual_tabletop.set_on(True)


def test_nothing_of_the_chronicle_is_offered_with_the_preview_off() -> None:
    saga = _saga()

    assert _offered(saga) == set()


@pytest.mark.usefixtures("preview")
def test_a_planned_session_offers_begin() -> None:
    saga = _saga()

    assert _offered(saga) == {"begin_session"}
    assert _offered(saga, None) == set()


@pytest.mark.usefixtures("preview")
def test_begin_session_puts_it_under_way_and_offers_end_and_the_chronicle() -> None:
    saga = _saga()

    step = _run(saga, "begin_session")
    assert isinstance(step, commands.Confirm)
    step.apply()

    session = ss.in_order(saga)[0]
    assert session.under_way
    assert _offered(saga) == {"close_session", "read_chronicle"}
    assert _offered(saga, 1) == set()  # one Session under way at a time


@pytest.mark.usefixtures("preview")
def test_another_players_session_is_not_theirs_to_begin() -> None:
    saga = _saga()
    ss.in_order(saga)[0].storyguide_id = "ana"

    assert _offered(saga) == set()


@pytest.mark.usefixtures("preview")
def test_end_session_marks_it_played_and_its_chronicle_stays_readable() -> None:
    saga = _saga()
    _begin = _run(saga, "begin_session")
    assert isinstance(_begin, commands.Confirm)
    _begin.apply()

    step = _run(saga, "close_session")
    assert isinstance(step, commands.Confirm)
    step.apply()

    session = next(s for s in saga.sessions if s.id == "s1")
    assert session.played and not session.under_way
    row = ss.in_order(saga).index(session)
    assert _offered(saga, row) == {"read_chronicle"}
    words = _words(_run(saga, "read_chronicle", row))
    assert "Session begun." in words and "Session ended." in words


@pytest.mark.usefixtures("preview")
def test_a_session_never_begun_has_no_chronicle_to_read() -> None:
    saga = _saga()

    assert "read_chronicle" not in _offered(saga)


@pytest.mark.usefixtures("preview")
def test_the_chronicle_shows_only_what_its_reader_may_see() -> None:
    """The host's own view goes through the audience filter: a Private roll
    of Ana's is not shown to the host when Ana's storyguide is another."""
    saga = _saga()
    session = ss.in_order(saga)[0]
    book = chronicle.begin(saga, session, by=chronicle.storyguide_of(session))
    book.add(
        chronicle.ROLL,
        "ana",
        chronicle.chosen("ana"),
        {"secret": "MARKER"},
    )
    session.storyguide_id = "ana"

    assert "MARKER" not in _words(_run(saga, "read_chronicle"))


def test_the_verbs_change_the_sessions_list_and_reading_saves_nothing() -> None:
    assert menu_refresh.REFRESH["begin_session"].sections == (SESSIONS_SECTION,)
    assert menu_refresh.REFRESH["close_session"].sections == (SESSIONS_SECTION,)
    assert menu_refresh.REFRESH["read_chronicle"].saves is False
