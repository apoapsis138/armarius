"""Downtime runs: several seasons at once (DE p. 528), each kept as it is
played, Winter's World Turns review kept for the end, and a player
character whose plans run out stopping the run with their plan form."""

from typing import Any

from ars_magica_manager import commands, world_turns
from ars_magica_manager.forms import downtime
from ars_magica_manager.models import Character, Saga


def _answer(asked: list[str]) -> Any:
    def ask(question: commands.Question) -> object:
        asked.append(getattr(question, "title", ""))
        if isinstance(question, commands.Form):
            return {f.key: f.value for f in question.fields()}
        return True

    return ask


def _run(saga: Saga, values: dict, asked: list[str]) -> object:
    form = downtime.downtime_form(saga)
    filled = {f.key: f.value for f in form.fields()} | values
    assert form.validate is not None and form.validate(filled) is None
    step: Any = form.apply(filled)
    outcome = commands.drive(step, _answer(asked))
    kept = 0
    while isinstance(outcome, commands.Then):
        kept += 1
        outcome = commands.drive(outcome.step, _answer(asked))
    return outcome


def test_a_run_plays_each_season_to_the_one_chosen():
    saga = Saga(id="s", name="Saga", current_year=1220, current_season="Spring")
    asked: list[str] = []
    outcome = _run(saga, {"season": "Spring", "year": 1221}, asked)
    assert (saga.current_season, saga.current_year) == ("Spring", 1221)
    assert isinstance(outcome, commands.Finished)
    assert "4 seasons played" in str(outcome.end)


def test_winters_review_waits_for_the_end_dated_its_year(monkeypatch):
    saga = Saga(id="s", name="Saga", current_year=1220, current_season="Autumn")

    def proposals(saga: Saga, _rng: object) -> list[world_turns.Proposal]:
        if saga.current_season == "Winter":
            return [
                world_turns.Proposal(world_turns.NEIGHBOURS, "The fair at Hildesheim")
            ]
        return []

    monkeypatch.setattr(world_turns, "season_proposals", proposals)
    asked: list[str] = []
    _run(saga, {"season": "Summer", "year": 1221}, asked)
    # The review is asked once, after the seasons, titled with its year.
    reviews = [a for a in asked if "1220" in a]
    assert len(reviews) == 1 and asked[-1] == reviews[0]


def test_a_player_character_whose_plans_ran_out_stops_the_run_with_a_plan_form():
    saga = Saga(id="s", name="Saga", current_year=1220, current_season="Spring")
    magus = Character(id="m", name="Aelfric", type="magus")
    magus.background.player_ids = ["ana"]
    saga.characters = [magus]
    form = downtime.downtime_form(saga)
    filled = {f.key: f.value for f in form.fields()} | {"year": 1221}
    step = form.apply(filled)
    assert isinstance(step, commands.Form)
    assert "plans have run out" in step.title


def test_a_run_must_end_after_now():
    saga = Saga(id="s", name="Saga", current_year=1220, current_season="Summer")
    assert downtime.problem(saga, {"to": "season", "season": "Spring", "year": 1220})
