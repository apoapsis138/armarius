"""Sessions: the evenings of play, their order, who played whom, Stewards
and the Needs You line for an Away Player's character."""

from dataclasses import asdict

from ars_magica_manager import attention, commands, deletion, sessions
from ars_magica_manager import players as pl
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.forms import sessions as session_forms
from ars_magica_manager.models import (
    STORY_EVENT,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Player,
    Saga,
    SeasonPlan,
    Session,
)


def _troupe() -> Saga:
    """Ana plays Aelfric, Ana and Ben share Brother Tam, and everyone plays
    the grog Gus."""
    saga = Saga(id="s", name="Saga")
    saga.players = [
        Player("ana", "Ana"),
        Player("ben", "Ben"),
        Player("sg", "Sue", "storyguide"),
    ]
    saga.covenants = [Covenant(id="c", saga_id="s", name="Fengheld", played=True)]
    aelfric = Character(id="aelfric", name="Aelfric", type="magus", covenant_id="c")
    aelfric.background.player_ids = ["ana"]
    tam = Character(id="tam", name="Brother Tam", type="companion", covenant_id="c")
    tam.background.player_ids = ["ana", "ben"]
    gus = Character(id="gus", name="Gus", type="grog", covenant_id="c")
    gus.background.everyone_plays = True
    saga.characters = [aelfric, tam, gus]
    return saga


def _answer(step: object, values: dict) -> object:
    assert isinstance(step, commands.Form)
    fields = {f.key: f.value for f in step.fields()}
    fields.update(values)
    problem = step.validate(fields) if step.validate else None
    assert problem is None, problem
    return step.apply(fields)


def test_planned_come_soonest_first_then_played_newest_first():
    saga = _troupe()
    saga.sessions = [
        Session("a", real_date="2026-12-01"),
        Session("b"),
        Session("c", real_date="2026-11-14"),
        Session("d", real_date="2026-10-01", played=True),
        Session("e", real_date="2026-10-20", played=True),
    ]
    assert [s.id for s in sessions.in_order(saga)] == ["c", "a", "b", "e", "d"]
    assert sessions.next_planned(saga).id == "c"


def test_a_saga_with_no_one_in_the_player_role_is_solo():
    saga = _troupe()
    assert not sessions.is_solo(saga)
    saga.players = [p for p in saga.players if p.role == pl.STORYGUIDE]
    assert sessions.is_solo(saga)


def test_who_played_whom_is_prefilled_and_a_shared_character_left_to_choose():
    saga = _troupe()
    form = session_forms.session_ops(saga).add()
    second = _answer(form, {"real_date": "2026-11-14", "attend_ben": "away"})
    assert isinstance(second, commands.Form)
    prefill = {f.key: f.value for f in second.fields()}
    # Ana alone of Tam's Players comes: Tam is hers tonight. Gus is
    # everyone's, and only Ana comes, so he is hers too.
    assert prefill["played_by_aelfric"] == "ana"
    assert prefill["played_by_tam"] == "ana"
    _answer(second, {})
    [session] = saga.sessions
    assert session.coming == ["ana"] and session.away == ["ben"]
    assert {(c.player_id, c.character_id) for c in session.castings} == {
        ("ana", "aelfric"),
        ("ana", "tam"),
        ("ana", "gus"),
    }


def test_two_coming_players_leave_their_shared_character_unpaired():
    saga = _troupe()
    second = _answer(session_forms.session_ops(saga).add(), {})
    prefill = {f.key: f.value for f in second.fields()}
    assert prefill["played_by_tam"] == ""
    assert prefill["played_by_gus"] == ""
    # A character has one person at most: one choice per character.
    keys = [f.key for f in second.fields()]
    assert len(keys) == len(set(keys))


def test_a_solo_session_asks_no_attendance_and_shows_not_recorded_later():
    saga = _troupe()
    table = saga.players
    saga.players = []
    done = _answer(session_forms.session_ops(saga).add(), {"real_date": ""})
    assert done == []
    [session] = saga.sessions
    assert session.solo and session.castings == []
    assert sessions.attendance_line(saga, session) == ""
    saga.players = table
    assert sessions.attendance_line(saga, session) == sessions.NOT_RECORDED


def test_a_bad_date_is_refused():
    saga = _troupe()
    form = session_forms.session_ops(saga).add()
    assert isinstance(form, commands.Form)
    assert form.validate({"real_date": "14 Nov"}) is not None


def test_removing_a_player_cuts_planned_sessions_and_stewards_but_keeps_played():
    saga = _troupe()
    saga.characters[2].background.steward_id = "ben"
    planned = Session("p", coming=["ben"], storyguide_id="ben")
    played = Session("q", played=True, coming=["ben"], names={"ben": "Ben"})
    saga.sessions = [planned, played]
    pl.remove(saga, saga.players[1])
    assert planned.coming == [] and planned.storyguide_id == ""
    assert played.coming == ["ben"]
    assert sessions.player_name(saga, played, "ben") == "Ben"
    assert saga.characters[2].background.steward_id == ""


def test_deleting_a_character_takes_it_out_of_planned_castings():
    saga = _troupe()
    _answer(_answer(session_forms.session_ops(saga).add(), {"attend_ben": "away"}), {})
    deletion.delete_character(saga, saga.characters[0])
    assert all(c.character_id != "aelfric" for c in saga.sessions[0].castings)


def test_a_steward_is_set_only_where_no_player_is_named():
    saga = _troupe()
    gus, aelfric = saga.characters[2], saga.characters[0]
    character_forms.apply_biographical(gus, {"steward_id": "ben"})
    assert sessions.steward(saga, gus).id == "ben"
    assert sessions.stewarded(saga, saga.players[1]) == [gus]
    character_forms.apply_biographical(aelfric, {"steward_id": "ben"})
    assert aelfric.background.steward_id == ""


def test_a_steward_may_change_the_characters_season_plans_only():
    saga = _troupe()
    gus = saga.characters[2]
    gus.background.everyone_plays = False
    gus.background.steward_id = "ben"
    ben = saga.players[1]
    assert pl.may_plan(saga, ben, gus) and not pl.may_change(saga, ben, gus)
    before = asdict(saga)
    saga.season_plans.append(SeasonPlan("gus", 1220, "Spring", "exposure"))
    gus.name = "Gus the Bold"
    kept, refused = pl.guard_changes(ben, before, asdict(saga))
    assert [p["character_id"] for p in kept["season_plans"]] == ["gus"]
    assert "characters[gus]" in refused


def test_needs_you_names_a_story_whose_characters_players_are_all_away():
    saga = _troupe()
    covenant = saga.covenants[0]
    covenant.diary = [
        CovenantDiaryEntry(
            1220,
            name="The Black Tower",
            category=STORY_EVENT,
            status="Open",
            concerns="characters:aelfric",
        ),
        CovenantDiaryEntry(
            1220,
            name="The Abbot",
            category=STORY_EVENT,
            status="Open",
            concerns="characters:tam",
        ),
    ]
    saga.sessions = [Session("n", coming=["ben"], away=["ana"])]
    away = [i for i in attention.items(saga) if i.need == attention.AWAY]
    # Tam's Ben is coming; Aelfric's only Player is Away.
    assert [i.title for i in away] == ["Aelfric: The Black Tower"]
    saga.sessions = [Session("n")]
    assert not [i for i in attention.items(saga) if i.need == attention.AWAY]
