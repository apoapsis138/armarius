"""A player's private notes and goals: read by the character's players,
Steward and storyguide only (a goal shared, by the troupe too), never
sent to another seat, and a goal of a score opens Plan the Study Path
filled in."""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest
from support import everything_saga

from ars_magica_manager import players, seat, viewing
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import notes_goals
from ars_magica_manager.models import PlayerGoal, Saga
from ars_magica_manager.seat_view import seat_view


def _saga() -> tuple[Saga, players.Player, players.Player]:
    saga = everything_saga()
    magus = saga.characters[0]
    ana = players.add(saga, {"name": "Ana", "passcode": "x" * 14})
    bo = players.add(saga, {"name": "Bo", "passcode": "y" * 14})
    magus.background.player_ids = [ana.id]
    magus.private_notes = "SECRET-NOTE: I suspect the princeps."
    magus.arts.setdefault("creo", 0)
    magus.goals = [
        PlayerGoal("own", "SECRET-GOAL", subject="art:creo", score=15, by_year=1230),
        PlayerGoal("open", "Found a daughter covenant", shared=True),
    ]
    return saga, ana, bo


@pytest.fixture(autouse=True)
def _reset_viewer():
    yield
    viewing.use(viewing.STORYGUIDE_VIEWER)


def test_only_its_players_steward_and_storyguide_read_them():
    saga, ana, bo = _saga()
    magus = saga.characters[0]
    assert viewing.reads_private(viewing.viewer_for(ana), magus, saga)
    assert not viewing.reads_private(viewing.viewer_for(bo), magus, saga)
    assert not viewing.reads_private(viewing.TABLE_VIEWER, magus, saga)
    assert viewing.reads_private(viewing.STORYGUIDE_VIEWER, magus, saga)
    magus.background.player_ids = []
    magus.background.steward_id = bo.id
    assert viewing.reads_private(viewing.viewer_for(bo), magus, saga)


def test_another_players_seat_carries_neither_notes_nor_unshared_goals():
    saga, ana, bo = _saga()
    theirs = json.dumps(asdict(seat_view(saga, viewing.viewer_for(bo))))
    assert "SECRET-NOTE" not in theirs and "SECRET-GOAL" not in theirs
    assert "Found a daughter covenant" in theirs
    hers = json.dumps(asdict(seat_view(saga, viewing.viewer_for(ana))))
    assert "SECRET-NOTE" in hers and "SECRET-GOAL" in hers


def test_the_section_shows_only_what_the_reader_may_read():
    saga, ana, bo = _saga()
    magus = saga.characters[0]
    viewing.use(viewing.viewer_for(bo), saga)
    assert notes_goals.shown(saga, magus)  # one goal is shared
    assert "SECRET" not in notes_goals.text(saga, magus)
    assert [label for _i, label in notes_goals.rows(saga, magus)] == [
        label for _i, label in notes_goals.rows(saga, magus) if "daughter" in label
    ]
    magus.goals[1].shared = False
    assert not notes_goals.shown(saga, magus)
    viewing.use(viewing.viewer_for(ana), saga)
    assert notes_goals.rows(saga, magus)[0][1].count(notes_goals.NOTES_ROW) == 1


def test_edit_opens_the_notes_on_the_first_row_and_a_goal_after():
    saga, ana, _bo = _saga()
    magus = saga.characters[0]
    viewing.use(viewing.viewer_for(ana), saga)
    ops = notes_goals.ops(saga, magus)[notes_goals.SECTION]
    notes = ops.edit(0)
    assert isinstance(notes, Form)
    notes.apply({"notes": "changed"})
    assert magus.private_notes == "changed"
    goal = ops.edit(1)
    assert isinstance(goal, Form)
    goal.apply({"text": "Renamed", "shared": True, "subject": "", "score": 0})
    assert magus.goals[0].text == "Renamed" and magus.goals[0].shared
    assert magus.goals[0].subject == "" and magus.goals[0].by_year is None
    assert isinstance(ops.remove(0), Refuse)


def test_a_goal_of_a_score_needs_the_score():
    assert notes_goals.goal_problem({"subject": "art:creo", "score": 0})
    assert notes_goals.goal_problem({"subject": "", "score": 0}) is None


def test_plan_the_study_path_opens_filled_in_from_the_goal():
    saga, ana, _bo = _saga()
    magus = saga.characters[0]
    viewing.use(viewing.viewer_for(ana), saga)
    seat.sign_in(saga, ana)
    try:
        assert notes_goals.aim_text(magus.goals[0]) == "Creo 15 by 1230"
        assert notes_goals.plans(saga, magus, 1)
        assert not notes_goals.plans(saga, magus, 2)  # no score to reach
        form = notes_goals.plan_form(saga, magus, 1)
        assert isinstance(form, Form)
        values = {f.key: f.value for f in form.fields()}
        assert values == {"subject": "art:creo", "goal": 15, "by_year": 1230}
    finally:
        seat.sign_out()
