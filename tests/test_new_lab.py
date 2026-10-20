"""Setting up a laboratory where a magus has none: planned on the
character sheet, it makes the laboratory in their covenant with the Basic
Flaw, and Advance Season asks whether the second season finishes it."""

from __future__ import annotations

import random

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager.commands import Form
from ars_magica_manager.forms import advance as advance_forms
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import Character, SeasonPlan, next_season
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import activity_groups as groups
from ars_magica_manager.rules import laboratory_seasons as ls
from ars_magica_manager.seasons.plans import plan_for, set_plan


def _planned(name: str = ""):
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    saga.laboratories = []
    plan = SeasonPlan(
        magus.id, saga.current_year, saga.current_season, ls.NEW, title=name
    )
    set_plan(saga, plan)
    return saga, magus, plan


def _advance(saga, finish: bool | None = True):
    """Advance the season, answering each question with its defaults and
    the new laboratory's with `finish`; the questions asked."""
    asked: list[str] = []
    step = advance_forms.play_season(saga, rng=lambda: random.Random(1))
    while isinstance(step, Form):
        asked.append(step.title)
        values = {f.key: f.value for f in step.fields() if f.kind != "info"}
        if step.title == "A New Laboratory" and finish is not None:
            values = {k: finish for k in values}
        step = step.apply(values)
    assert isinstance(step, advance_forms.Played)
    return asked, step


def test_it_is_offered_on_the_character_sheet_under_order_and_covenant():
    _, magus, _ = _planned()
    activity = rules.ACTIVITIES[ls.NEW]
    assert not activity.lab
    assert activity.group == groups.ORDER
    assert activity in rules.activities_for(magus)
    companion = Character(id="c", name="Bertram", type="companion")
    assert activity not in rules.activities_for(companion)


def test_it_needs_magic_theory_3_and_a_covenant():
    saga, magus, plan = _planned()
    assert rules.outcome(magus, plan, saga).ok
    magus.covenant_id = None
    assert "no covenant" in rules.outcome(magus, plan, saga).problems[0]
    magus.covenant_id = "cov1"
    magus.abilities = [a for a in magus.abilities if a.name != "Magic Theory"]
    assert "Magic Theory 3" in rules.outcome(magus, plan, saga).problems[0]


def test_the_form_names_the_laboratory():
    saga, magus, _ = _planned()
    fields = season_forms.season_plan_fields(saga, magus, None)
    named = next(f for f in fields if f.key == "lab_name")
    assert named.show_if is not None and named.show_if({"activity": ls.NEW})
    assert not named.show_if({"activity": rules.PRACTICE})
    plan = season_forms.season_plan_from(
        saga, magus, {"activity": ls.NEW, "lab_name": "The Tower"}
    )
    assert plan.title == "The Tower"
    assert ls.new_lab_name(magus, plan) == "The Tower"
    assert ls.new_lab_name(magus, SeasonPlan(magus.id, 1220, "Spring", ls.NEW)) == (
        "Leandro's laboratory"
    )


def test_applying_it_makes_the_lab_and_plans_the_second_season():
    saga, magus, _ = _planned("The Tower")
    year, season = saga.current_year, saga.current_season
    asked, played = _advance(saga, finish=True)
    assert "A New Laboratory" in asked
    lab = next(lab for lab in saga.laboratories if lab.name == "The Tower")
    assert (lab.covenant_id, lab.owner_id) == ("cov1", magus.id)
    assert ls.has_vf(lab, ls.BASIC)
    assert lab.diary and lab.diary[-1].name == "Set up a new laboratory"
    assert magus.diary[-1].activity == "Set up a new laboratory"
    assert (magus.diary[-1].year, magus.diary[-1].season) == (year, season)
    second = plan_for(saga, magus)
    assert second is not None
    assert (second.activity, second.lab_id) == (ls.BUILD, lab.id)
    assert "finishes The Tower" in played.message

    # The second season removes the Basic Flaw.
    asked, _ = _advance(saga)
    assert "A New Laboratory" not in asked
    assert not ls.has_vf(lab, ls.BASIC)


def test_declining_leaves_the_next_season_unplanned():
    saga, magus, _ = _planned()
    _, played = _advance(saga, finish=False)
    lab = next(lab for lab in saga.laboratories if lab.owner_id == magus.id)
    assert ls.has_vf(lab, ls.BASIC)
    assert plan_for(saga, magus) is None
    assert "finishes" not in played.message


def test_a_season_already_planned_is_kept():
    saga, magus, plan = _planned()
    season, year = next_season(plan.season, plan.year)
    set_plan(saga, SeasonPlan(magus.id, year, season, rules.PRACTICE))
    _advance(saga, finish=True)
    kept = plan_for(saga, magus)
    assert kept is not None and kept.activity == rules.PRACTICE


def test_a_plan_that_cant_be_carried_out_asks_nothing():
    saga, magus, _ = _planned()
    magus.covenant_id = None
    asked, _ = _advance(saga)
    assert "A New Laboratory" not in asked
    assert saga.laboratories == []
