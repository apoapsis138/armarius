"""Repeating a plan: Plan Season's For (this season, until it's done, or
a number of seasons), the seasons each kind of work needs, clearing the
seasons after the first, and Advance Season's Interruptions step, after
which the seasons the work still needs are worked out again."""

from __future__ import annotations

import random

from screen_helpers import _sample_saga_with_covenant
from test_lab_seasons import _plan as _lab_plan
from test_lab_seasons import _saga as _lab_saga

from ars_magica_manager import seasons
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms import advance as advance_forms
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import SeasonPlan
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.seasons import repeat

READ_UNTIL_DONE = {
    "activity": rules.READ,
    "book_id": "book1",  # Magic Theory summa, L8 Q6
    repeat.FOR: repeat.UNTIL_DONE,
}


def _reader():
    saga = _sample_saga_with_covenant()
    return saga, saga.characters[0]  # Leandro, Magic Theory 5 (75 xp)


def _when(plans: list[SeasonPlan]) -> list[str]:
    return [f"{p.season} {p.year}" for p in plans]


def _advance(saga, answers=None) -> tuple[list[str], advance_forms.Played]:
    """Advance a season, answering Interruptions with `answers`; the
    titles of the steps asked."""
    asked: list[str] = []
    step = advance_forms.play_season(saga, rng=lambda: random.Random(1))
    while isinstance(step, Form):
        asked.append(step.title)
        values = {f.key: f.value for f in step.fields() if f.kind != "info"}
        if step.title == "Interruptions":
            values.update(answers or {})
        step = step.apply(values)
    assert isinstance(step, advance_forms.Played)
    return asked, step


def test_each_kind_of_work_says_the_seasons_it_needs():
    saga, magus = _reader()
    plan = SeasonPlan(magus.id, 1220, "Spring", rules.READ, book_id="book1")
    # Magic Theory L8 needs 180 xp (from 75): 105 at 6 a season.
    assert repeat.seasons_needed(saga, magus, plan) == 18
    assert (
        repeat.seasons_needed(
            saga, magus, SeasonPlan(magus.id, 1220, "Spring", rules.PRACTICE)
        )
        is None
    )
    assert repeat.can_run_until_done(bs.WRITE_SUMMA)
    assert not repeat.can_run_until_done(rules.EXPOSURE)
    lab = _lab_saga()
    tiberius = lab.characters[0]
    # Bolt: Lab Total 15 against level 15... two seasons (seasons_left 1).
    assert repeat.seasons_needed(lab, tiberius, _lab_plan("bolt")) == 2


def test_until_done_plans_the_seasons_straight_after():
    saga, magus = _reader()
    form = season_forms.plan_season(saga, magus)
    assert form.validate is not None and form.validate(READ_UNTIL_DONE) is None
    assert form.live is not None
    assert "Until it's done: 18 seasons" in form.live(READ_UNTIL_DONE)
    added = season_forms.save_season(saga, magus, READ_UNTIL_DONE)
    assert len(added) == 17 and _when(added)[-1] == "Summer 1224"
    first = seasons.plan_for(saga, magus)
    assert first is not None and first.until_done and first.series
    assert {p.series for p in saga.season_plans} == {first.series}
    assert "Season 1 of 18, until it's done (to Summer 1224)" in seasons.plan_text(
        saga, magus
    )


def test_a_season_already_planned_stops_it_and_the_last_says_so():
    saga, magus = _reader()
    seasons.set_plan(saga, SeasonPlan(magus.id, 1220, "Autumn", rules.PRACTICE))
    added = season_forms.save_season(saga, magus, READ_UNTIL_DONE)
    assert _when(added) == ["Summer 1220"]
    assert added[-1].more_needed == 16
    rows = [text for _, text in seasons.ahead_rows(saga, magus)]
    assert rows[0].endswith("(needs more seasons)")


def test_a_number_of_seasons_repeats_any_plan():
    saga, magus = _reader()
    values = {
        "activity": rules.EXPOSURE,
        "subject_1": "ability:Magic Theory",
        repeat.FOR: "3",
    }
    added = season_forms.save_season(saga, magus, values)
    assert _when(added) == ["Summer 1220", "Autumn 1220"]
    assert not any(p.until_done for p in saga.season_plans)


def test_until_done_is_refused_for_work_with_no_end():
    saga, magus = _reader()
    form = season_forms.plan_season(saga, magus)
    values = {
        "activity": rules.EXPOSURE,
        "subject_1": "ability:Magic Theory",
        repeat.FOR: repeat.UNTIL_DONE,
    }
    assert form.validate is not None
    assert "choose a number of seasons" in (form.validate(values) or "")


def test_changing_one_season_keeps_the_rest_and_replanning_replaces_them():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, READ_UNTIL_DONE)
    first = seasons.plan_for(saga, magus)
    season_forms.save_season(
        saga, magus, {**READ_UNTIL_DONE, repeat.FOR: repeat.ONCE}, first
    )
    kept = seasons.plan_for(saga, magus)
    assert kept is not None and kept.series == first.series
    assert len(saga.season_plans) == 18
    season_forms.save_season(saga, magus, {**READ_UNTIL_DONE, repeat.FOR: "2"}, kept)
    assert len(saga.season_plans) == 2


def test_clearing_the_first_season_offers_to_clear_the_rest():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, {**READ_UNTIL_DONE, repeat.FOR: "3"})
    step = season_forms.clear_season(saga, magus)
    assert isinstance(step, Form)
    rest = next(f for f in step.fields() if f.key == "rest")
    assert "to Autumn 1220" in rest.label and rest.value is True
    step.apply({"rest": False})
    assert _when(saga.season_plans) == ["Summer 1220", "Autumn 1220"]
    step = season_forms.clear_season(saga, magus, ("Summer", 1220))
    assert isinstance(step, Form)
    step.apply({"rest": True})
    assert saga.season_plans == []


def test_a_single_season_clears_with_a_plain_confirmation():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, {**READ_UNTIL_DONE, repeat.FOR: "once"})
    assert isinstance(season_forms.clear_season(saga, magus), Confirm)


def test_months_lost_set_the_reading_back_a_season():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, READ_UNTIL_DONE)
    asked, played = _advance(saga, {"months_0": 3})
    assert "Interruptions" in asked
    assert _when(saga.season_plans)[-1] == "Autumn 1224"  # one more season
    assert "now runs to Autumn 1224" in played.message


def test_a_season_lost_is_not_played_and_is_planned_again():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, READ_UNTIL_DONE)
    diary = len(magus.diary)
    _, played = _advance(saga, {"lost_0": True})
    assert len(magus.diary) == diary
    assert "season of Read a book" in played.message and "was lost" in played.message
    assert len(saga.season_plans) == 18


def test_an_uninterrupted_season_changes_nothing():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, READ_UNTIL_DONE)
    _, played = _advance(saga)
    assert len(saga.season_plans) == 17
    assert "worked out again" not in played.message


def test_a_plan_for_one_season_asks_nothing():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, {**READ_UNTIL_DONE, repeat.FOR: "2"})
    asked, _ = _advance(saga)
    assert "Interruptions" not in asked


def test_lab_work_interrupted_runs_a_season_longer():
    saga = _lab_saga()
    seasons.plan_lab_work(saga, _lab_plan("bolt"))
    assert _when(sorted(saga.season_plans, key=lambda p: p.year)) == [
        "Spring 1220",
        "Summer 1220",
    ]
    step = advance_forms.play_season(saga, rng=lambda: random.Random(1))
    assert isinstance(step, Form) and step.title == "Interruptions"
    assert "Days away from the laboratory" in [f.label for f in step.fields()]
    _, played = _advance(saga, {"days_0": 21})  # no lab work this season
    assert _when(saga.season_plans) == ["Summer 1220", "Autumn 1220"]
    assert "now runs to Autumn 1220" in played.message


def test_work_finished_early_clears_the_seasons_left():
    saga, magus = _reader()
    season_forms.save_season(saga, magus, {**READ_UNTIL_DONE})
    mt = next(a for a in magus.abilities if a.name == "Magic Theory")
    mt.xp = 175  # 6 xp short of score 8
    _, played = _advance(saga)
    assert saga.season_plans == []
    assert "is done" in played.message


async def test_the_terminal_clear_offers_the_later_seasons():
    from support import wait_until
    from test_list_flows import _open, _press
    from test_seasons_ahead import AHEAD
    from textual.widgets import Button, Checkbox

    from ars_magica_manager import storage
    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens import FieldsDialog

    saga, magus = _reader()
    magus.id = "mag1"
    seasons.set_plan(saga, SeasonPlan("mag1", 1220, "Spring", rules.PRACTICE))
    values = {**READ_UNTIL_DONE, repeat.FOR: "3", "when": "Summer 1220"}
    season_forms.save_season(saga, magus, values)
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, _ = await _open(pilot, app, AHEAD)
        await _press(pilot, app, "d", FieldsDialog)
        assert app.screen.query_one("#fld-rest", Checkbox).value is True
        app.screen.query_one("#btn-save", Button).press()
        assert await wait_until(
            pilot,
            lambda: (
                [p.activity for p in storage.load_saga("test_saga").season_plans]
                == [rules.PRACTICE]
            ),
        )
        assert app.screen is workspace
