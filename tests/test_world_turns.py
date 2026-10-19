"""The world turns: the yearly step's review, what applying it changes,
and deleting its entry to undo it."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import place_events, threats, towns, world, world_turns
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms import advance as advance_forms
from ars_magica_manager.models import CovenantDiaryEntry, TreasuryEntry


def _winter():
    saga = everything_saga()
    saga.current_season = "Winter"
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    saga.covenants[0].diary.append(
        CovenantDiaryEntry(
            1220, "Summer", name=f"{gottfried.name}'s reeve came about the mill rent"
        )
    )
    saga.tribunals[0].treasury.append(
        TreasuryEntry("loan", 5, who="Keep", due_year=1220)
    )
    return saga


def _review(saga):
    found = world_turns.proposals(saga, random.Random(1))
    return found, {f"{p.group}: {p.text}" for p in found}


def test_the_review_lists_what_the_year_brought():
    saga = _winter()
    found, texts = _review(saga)
    assert "Places: The Drachenfels: Level 2 opens" in texts
    assert "Threats: The Hollow Crown: The ford floods has come" in texts
    assert any(t.startswith("Neighbours: Soest fair: Keep's income") for t in texts)
    assert any(
        t.startswith("Tribunal treasury: Rhine: the loan to Keep") for t in texts
    )
    attitude = next(p for p in found if p.group == world_turns.ATTITUDES)
    assert attitude.covenant_id == "cov1" and attitude.events
    # The white stag comes every 7 years from 1218: not this year.
    assert not any("white stag" in t for t in texts)
    # A loan starts unticked; the others start ticked.
    loan = next(p for p in found if p.group == world_turns.TREASURY)
    assert not loan.ticked


def _apply(saga, found, **values):
    chosen = {f"tick_{i}": p.ticked for i, p in enumerate(found)}
    chosen.update(values)
    form = world_turns.review(saga, found, lambda: "played")
    assert form.validate is not None
    assert form.validate(chosen) is None
    assert form.apply(chosen) == "played"
    return saga.world_turns[-1]


def test_applying_writes_one_entry_and_deleting_it_undoes_it():
    saga = _winter()
    found, _texts = _review(saga)
    crown = saga.neighbour("crown")
    soest = saga.neighbour("soest")
    drachenfels = saga.neighbour("drachenfels")
    assert crown is not None and soest is not None and drachenfels is not None
    fair_before = dict(towns.fairs(soest)[0])
    diary_before = list(place_events.diary(drachenfels))
    attitude = next(i for i, p in enumerate(found) if p.group == world_turns.ATTITUDES)
    gottfried = saga.neighbour("gottfried")
    before = world.attitude_score(world.attitude_toward(gottfried, "cov1"))
    turn = _apply(
        saga,
        found,
        **{f"change_{attitude}": "-1", f"reason_{attitude}": "the mill rent unpaid"},
    )
    assert len(saga.world_turns) == 1
    assert world_turns.entry_title(turn) == "The world turns, Winter 1220"
    stage = next(s for s in threats.stages(crown) if s["title"] == "The ford floods")
    assert stage["outcome"] == "Happened"
    assert towns.fairs(soest)[0].get("last", "").startswith("1220:")
    assert len(place_events.diary(drachenfels)) == len(diary_before) + 1
    after = world.attitude_score(world.attitude_toward(gottfried, "cov1"))
    assert after == max(-3, before - 1)
    # The loan was left unticked: still unpaid.
    assert not saga.tribunals[0].treasury[-1].paid

    ops = world_turns.turn_ops(saga)
    assert ops.remove is not None
    confirm = ops.remove(0)
    assert isinstance(confirm, Confirm)
    assert confirm.apply() == []
    assert saga.world_turns == []
    assert stage.get("outcome") in (None, "Pending")
    assert towns.fairs(soest)[0] == fair_before
    assert place_events.diary(drachenfels) == diary_before
    assert world.attitude_score(world.attitude_toward(gottfried, "cov1")) == before


def test_a_change_made_since_is_left_alone_on_undo():
    saga = _winter()
    found, _texts = _review(saga)
    turn = _apply(saga, found)
    crown = saga.neighbour("crown")
    assert crown is not None
    stage = next(s for s in threats.stages(crown) if s["title"] == "The ford floods")
    stage["outcome"] = "Stopped"
    notes = world_turns.undo(saga, turn)
    assert notes and "left as they are" in notes[0]
    assert stage["outcome"] == "Stopped"


def test_an_attitude_change_needs_its_reason():
    saga = _winter()
    found, _texts = _review(saga)
    index = next(i for i, p in enumerate(found) if p.group == world_turns.ATTITUDES)
    form = world_turns.review(saga, found, lambda: None)
    assert form.validate is not None
    assert "reason" in (
        form.validate({f"change_{index}": "+1", f"reason_{index}": ""}) or ""
    )
    reason = next(f for f in form.fields() if f.key == f"reason_{index}")
    assert reason.show_if is not None and not reason.show_if({f"change_{index}": "0"})


def test_advance_season_asks_after_winter_only():
    saga = _winter()
    step = advance_forms.play_season(saga, rng=lambda: random.Random(2))
    while isinstance(step, Form) and step.title != world_turns.title(1220):
        step = step.apply({f.key: f.value for f in step.fields()})
    assert isinstance(step, Form) and step.title == world_turns.title(1220)
    played = step.apply({f.key: f.value for f in step.fields() if f.kind != "info"})
    assert isinstance(played, advance_forms.Played)
    assert (saga.current_season, saga.current_year) == ("Spring", 1221)
    assert len(saga.world_turns) == 1
    spring = everything_saga()
    step = advance_forms.play_season(spring, rng=lambda: random.Random(2))
    assert isinstance(step, advance_forms.Played) or (
        isinstance(step, Form) and step.title != world_turns.title(1220)
    )
