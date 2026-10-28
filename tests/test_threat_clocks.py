"""Threat clocks: a threat's clock, a delay that moves every stage still
to come, Delay or Hasten, and a place's trigger tied to a threat's track
that each season it comes asks whether the troupe failed it or kept it."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import place_events, threats, world_turns
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import advance as advance_forms
from ars_magica_manager.models import Neighbour


def _crown(saga):
    crown = saga.neighbour("crown")
    assert crown is not None
    return crown


def _hunt(saga) -> Neighbour:
    """A threat along a track: stages at 2 and 4, standing at 1."""
    hunt = Neighbour(
        id="hunt",
        name="The Wild Hunt",
        kind="threat",
        details={
            "moves": "A track",
            "position": 1,
            "stages": [
                {"title": "Hounds heard", "at": 2},
                {"title": "The Hunt rides", "at": 4},
            ],
        },
    )
    saga.neighbours.append(hunt)
    return hunt


def _tie(saga, hunt, season="Summer", steps=None):
    """Tie a yearly trigger at the Drachenfels to `hunt`."""
    place = saga.neighbour("drachenfels")
    assert place is not None
    trigger: place_events.Trigger = {
        "name": "Abnoba's due",
        "when": place_events.YEARLY,
        "season": season,
        "threat_id": hunt.id,
    }
    if steps is not None:
        trigger["steps"] = steps
    place_events.triggers(place).append(trigger)
    return place


# -- the clock --


def test_a_dated_threat_s_clock_counts_its_stages_come():
    saga = everything_saga()
    saga.current_season, saga.current_year = "Winter", 1220
    crown = _crown(saga)
    assert threats.clock(saga, crown) == (2, 3)
    assert threats.clock_text(saga, crown) == "■■□ 2 of 3"


def test_a_track_s_clock_runs_to_its_last_stage():
    saga = everything_saga()
    hunt = _hunt(saga)
    assert threats.clock_text(saga, hunt) == "■□□□ 1 of 4"
    hunt.details["position"] = 9
    assert threats.clock(saga, hunt) == (4, 4)
    facts = {f.label: f.value for f in threats.facts(saga, hunt)}
    assert facts["Clock"] == "■■■■ 4 of 4"


def test_no_clock_while_dormant_or_with_nothing_to_count():
    saga = everything_saga()
    hunt = _hunt(saga)
    hunt.details["dormant"] = True
    assert threats.clock(saga, hunt) is None
    empty = Neighbour(id="e", name="Empty", kind="threat", details={"moves": "A track"})
    assert threats.clock_text(saga, empty) == ""


# -- the delay --


def test_a_delay_moves_every_stage_still_to_come_but_not_the_settled():
    saga = everything_saga()
    saga.current_season, saga.current_year = "Autumn", 1220
    crown = _crown(saga)
    ford, crowning = threats.stages(crown)[1:]
    assert threats.when_text(crown, ford) == "Winter 1220"
    crown.details["delay"] = 2
    assert threats.when_text(crown, ford) == "Summer 1221"
    # A stage dated by its year alone comes at the year's start: Spring.
    assert threats.when_text(crown, crowning) == "Autumn 1222"
    # The dates typed stay as they are.
    assert (ford["year"], ford["season"]) == (1220, "Winter")
    assert threats.due(saga, crown) == (1221 * 4 + 1, "The Hollow Crown, Summer 1221")
    ford["outcome"] = "Stopped"
    assert threats.when_text(crown, ford) == "Winter 1220"


def test_a_delay_counts_when_a_stage_comes():
    saga = everything_saga()
    saga.current_season, saga.current_year = "Winter", 1220
    crown = _crown(saga)
    ford = threats.stages(crown)[1]
    assert threats.has_come(saga, crown, ford)
    crown.details["delay"] = 1
    assert not threats.has_come(saga, crown, ford)
    crown.details["delay"] = -1
    assert threats.has_come(saga, crown, ford)


def test_delay_or_hasten_on_a_dated_threat_writes_its_diary():
    saga = everything_saga()
    crown = _crown(saga)
    line = threats.move(saga, crown, 2, "the bridge was burned")
    assert threats.delay(crown) == 2
    assert line == "The Hollow Crown: Delayed 2 seasons: the bridge was burned."
    assert place_events.diary(crown)[-1]["text"] == (
        "The Hollow Crown: Delayed 2 seasons: the bridge was burned"
    )
    threats.move(saga, crown, -1, "the king's ally returned")
    assert threats.delay(crown) == 1
    assert "Hastened 1 season" in place_events.diary(crown)[-1]["text"]


def test_delay_or_hasten_on_a_track_moves_its_position():
    saga = everything_saga()
    hunt = _hunt(saga)
    hunt.details["position"] = 3
    threats.move(saga, hunt, 2, "the hounds were fed")
    assert threats.position(hunt) == 1
    assert "Moved back from 3 to 1" in place_events.diary(hunt)[-1]["text"]


def test_the_delay_form_asks_how_far_and_why():
    saga = everything_saga()
    hunt = _hunt(saga)
    form = threats.delay_form(saga, hunt)
    assert form.validate is not None
    assert "below 0" in (form.validate({"by": 2, "reason": "x"}) or "")
    assert form.validate({"by": 1, "reason": "x"}) is None
    assert form.apply({"by": 1, "reason": "fed"}) == [
        "The Wild Hunt: Moved back from 1 to 0: fed."
    ]


# -- a trigger tied to a threat --


def test_a_tied_trigger_is_asked_in_its_own_season_only():
    saga = everything_saga()
    hunt = _hunt(saga)
    _tie(saga, hunt, season="Summer")
    saga.current_season = "Spring"
    assert world_turns.season_proposals(saga, random.Random(1)) == []
    saga.current_season = "Summer"
    [clock] = world_turns.season_proposals(saga, random.Random(1))
    assert clock.group == world_turns.CLOCKS
    assert clock.text == "The Drachenfels: Abnoba's due (The Wild Hunt, ■□□□ 1 of 4)"
    # Nor is it among Winter's places.
    saga.current_season = "Winter"
    assert not any(
        "Abnoba" in p.text for p in world_turns.proposals(saga, random.Random(1))
    )


def test_failing_a_tied_trigger_moves_the_threat_and_deleting_the_entry_undoes_it():
    saga = everything_saga()
    hunt = _hunt(saga)
    place = _tie(saga, hunt, season="Summer", steps=2)
    saga.current_season = "Summer"
    found = world_turns.season_proposals(saga, random.Random(1))
    failed = found[0].answers[0]
    assert failed.label == "Failed: it moves to 3"
    assert failed.line == (
        "Abnoba's due failed: The Wild Hunt moves from 1 to 3, reaching Hounds heard"
    )
    form = world_turns.review(saga, found, lambda: "played")
    assert form.title == "The World This Season: Summer 1220"
    assert form.validate is not None
    assert "failed, kept" in (form.validate({}) or "")
    assert form.apply({"answer_0": world_turns.FAILED}) == "played"
    assert threats.position(hunt) == 3
    assert threats.reached(saga, hunt).current is not None
    assert place_events.diary(hunt)[-1]["text"].startswith(
        "The Drachenfels: Abnoba's due failed"
    )
    assert place_events.diary(place)[-1]["text"].startswith("Abnoba's due failed")
    [turn] = saga.world_turns
    assert world_turns.entry_title(turn) == "The world this season, Summer 1220"

    world_turns.undo(saga, turn)
    assert threats.position(hunt) == 1
    assert not any("Abnoba" in e["text"] for e in place_events.diary(hunt))


def test_keeping_it_writes_both_diaries_and_leaving_it_writes_nothing():
    saga = everything_saga()
    hunt = _hunt(saga)
    place = _tie(saga, hunt)
    saga.current_season = "Summer"
    found = world_turns.season_proposals(saga, random.Random(1))
    world_turns.review(saga, found, lambda: None).apply({"answer_0": world_turns.KEPT})
    assert threats.position(hunt) == 1
    assert place_events.diary(place)[-1]["text"] == (
        "Abnoba's due kept: The Wild Hunt stays at 1"
    )
    saga.world_turns.clear()
    world_turns.review(saga, found, lambda: None).apply(
        {"answer_0": world_turns.UNANSWERED}
    )
    assert saga.world_turns == []


def test_advance_season_asks_a_tied_trigger_outside_winter():
    saga = everything_saga()
    hunt = _hunt(saga)
    _tie(saga, hunt, season=saga.current_season)
    title = world_turns.title(saga.current_year, saga.current_season)
    step = advance_forms.play_season(saga, rng=lambda: random.Random(2))
    while isinstance(step, Form) and step.title != title:
        step = step.apply({f.key: f.value for f in step.fields()})
    assert isinstance(step, Form) and step.title == title
    played = step.apply({"answer_0": world_turns.FAILED})
    assert isinstance(played, advance_forms.Played)
    assert threats.position(hunt) == 2


def test_a_trigger_ties_only_to_a_track_and_needs_a_date():
    saga = everything_saga()
    hunt = _hunt(saga)
    place = saga.neighbour("drachenfels")
    assert place is not None
    [field] = [
        f
        for f in place_events.trigger_fields(saga, place, None)
        if f.key == "threat_id"
    ]
    assert field.options == [("The Wild Hunt", "hunt")]  # not the dated Crown
    problem = place_events._trigger_problem(
        {"name": "x", "when": place_events.WHENEVER, "what": "y", "threat_id": "hunt"}
    )
    assert problem and "needs a date" in problem
    # A threat that now moves by date no longer moves with the trigger.
    hunt.details["moves"] = "Fixed dates"
    assert place_events.threat_of(saga, {"name": "x", "threat_id": "hunt"}) is None


def test_the_trigger_list_says_what_failing_it_moves():
    saga = everything_saga()
    hunt = _hunt(saga)
    place = _tie(saga, hunt, steps=2)
    grid = place_events.triggers_grid(saga, place)
    assert grid.rows[-1][3] == "Failing it moves The Wild Hunt 2 steps"
