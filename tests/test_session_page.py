"""A Session's own page: the core both front-ends draw it from (where.py,
sheets/session.py, the More registry on a Session page)."""

from __future__ import annotations

import pytest

from ars_magica_manager import commands, section_verbs, virtual_tabletop
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import more
from ars_magica_manager.forms import page as page_forms
from ars_magica_manager.models import Casting, Character, Player, Saga, Session
from ars_magica_manager.sections import SESSION_INFO_SECTION, SESSIONS_SECTION
from ars_magica_manager.sheets import session as session_sheet
from ars_magica_manager.where import Where

VERBS = ("begin_session", "close_session", "read_chronicle", "cast_glance")


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.sessions = [
        Session(
            "s1",
            real_date="2026-11-21",
            season="Spring",
            year=1221,
            coming=["ana"],
            away=["ben"],
            castings=[Casting("ana", "aelfric")],
            notes="Bring the map.",
        ),
        Session("s2"),
    ]
    return saga


def _page(saga: Saga, session_id: str = "s1") -> page_forms.Page:
    return page_forms.page_at(
        saga, Where(NodeKind.SESSION, session_id), section=SESSION_INFO_SECTION
    )


@pytest.fixture
def preview() -> None:
    virtual_tabletop.set_on(True)


def test_a_session_page_shows_its_session_and_is_named_by_its_date() -> None:
    saga = _saga()
    where = Where.of(saga.sessions[0])

    assert where == Where(NodeKind.SESSION, "s1")
    assert where.shows_record
    assert where.session(saga) is saga.sessions[0]
    assert where.name(saga) == "Session of 21 Nov 2026"
    assert Where(NodeKind.SESSION, "s2").name(saga) == "Session (no date yet)"


def test_a_deleted_session_page_is_gone() -> None:
    saga = _saga()
    where = Where.of(saga.sessions[0])
    saga.sessions.pop(0)

    assert where.gone(saga)
    assert where.session(saga) is None


def test_the_page_says_when_who_storyguides_who_comes_and_who_plays_whom() -> None:
    saga = _saga()
    session = saga.sessions[0]

    assert session_sheet.title(session) == "Session of 21 Nov 2026"
    assert session_sheet.subtitle(session) == "Planned  ·  Spring 1221"
    facts = {f.label: f.value for f in session_sheet.facts(saga, session)}
    assert facts["Storyguide"] == "The saga's storyguide"
    assert facts["Coming"] == "Ana"
    assert facts["Away"] == "Ben"
    assert facts["Who plays whom"] == "Ana as Aelfric"
    assert facts["Notes"] == "Bring the map."


def test_edit_on_the_page_edits_its_session() -> None:
    saga = _saga()
    ops = section_verbs.ops_of(saga, saga.sessions[0])[SESSION_INFO_SECTION]

    assert ops.add is None and ops.remove is None
    assert ops.edit is not None
    step = ops.edit(0)
    assert isinstance(step, commands.Form)
    assert {f.key: f.value for f in step.fields()}["real_date"] == "2026-11-21"


def _offered(saga: Saga, session_id: str = "s1") -> set[str]:
    page = _page(saga, session_id)
    return {a for a in VERBS if more.available(a, page)}


def test_the_page_offers_nothing_of_the_chronicle_with_the_preview_off() -> None:
    assert _offered(_saga()) == {"cast_glance"}


@pytest.mark.usefixtures("preview")
def test_the_page_offers_begin_then_end_and_the_chronicle_for_its_session() -> None:
    saga = _saga()

    assert _offered(saga) == {"begin_session", "cast_glance"}
    step = menu_forms._COMMANDS["begin_session"](_page(saga))
    assert isinstance(step, commands.Confirm)
    step.apply()

    assert saga.sessions[0].under_way
    assert _offered(saga) == {"close_session", "read_chronicle", "cast_glance"}
    # One Session under way at a time: the other's page can't begin.
    assert _offered(saga, "s2") == {"cast_glance"}


def test_open_session_is_offered_on_a_sessions_row_and_opens_its_page() -> None:
    saga = _saga()
    on_row = page_forms.Page(saga, NodeKind.SAGA, section=SESSIONS_SECTION, row=0)

    assert more.available("open_session", on_row)
    assert not more.available("open_session", _page(saga))
    step = menu_forms._COMMANDS["open_session"](on_row)
    assert isinstance(step, commands.Act)
    went = step.apply()
    assert isinstance(went, commands.Go)
    assert (went.ref.kind, went.ref.id) == ("sessions", "s1")


@pytest.mark.usefixtures("preview")
def test_cast_at_a_glance_on_the_page_is_its_sessions() -> None:
    saga = _saga()
    step = menu_forms._COMMANDS["cast_glance"](_page(saga, "s2"))

    assert isinstance(step, commands.Form)
    assert "No date yet" in step.title
