"""Planning seasons without a front-end: the character's This Season,
a grog's Yearly Update, the covenant's Seasons lists and the
laboratory's Planning list (season_forms, lab_plan_forms)."""

from __future__ import annotations

from typing import Any

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import commands, form_spec, seasons
from ars_magica_manager import lab_plan_forms as lpf
from ars_magica_manager import season_forms as sf
from ars_magica_manager.models import (
    Ability,
    Character,
    SeasonPlan,
    SpellDesign,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import lab_seasons


def _values(form: commands.Form, typed: dict[str, Any]) -> dict[str, Any]:
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    return form_spec.result(fields, lambda f: raw[f.key])


def _problem(form: commands.Form, typed: dict[str, Any]) -> str | None:
    assert form.validate is not None
    return form.validate(_values(form, typed))


def _saved(form: commands.Form, typed: dict[str, Any]) -> Any:
    values = _values(form, typed)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def _saga_with_grog():
    saga = _sample_saga_with_covenant()
    grog = Character(id="g", name="Hugo", type="grog", covenant_id="cov1")
    grog.abilities = [Ability("Single Weapon"), Ability("Brawl")]
    saga.characters.append(grog)
    return saga


# -- the character's This Season -----------------------------------------------


def test_a_season_is_planned_changed_and_cleared():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    ops = sf.character_season_ops(saga, magus)
    assert ops.add is not None and ops.rows() == []
    form = ops.add()
    assert isinstance(form, commands.Form)
    assert form.title == "Plan Leandro's Season (Spring 1220)"
    practice = {"activity": "practice", "subject_1": "ability:Magic Theory"}
    assert form.live is not None and "Magic Theory" in form.live(practice)
    _saved(form, practice)
    plan = seasons.plan_for(saga, magus)
    assert plan is not None and plan.activity == "practice"
    assert [a.subject for a in plan.allocations] == ["ability:Magic Theory"]
    # Planned: Edit and Clear act on the plan, its one row; no more Plan.
    ops = sf.character_season_ops(saga, magus)
    assert ops.add is None and ops.edit is not None and ops.remove is not None
    assert ops.rows() == [seasons.plan_summary(saga, magus, plan)]
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form)
    assert {f.key: f.value for f in edit.fields()}["activity"] == "practice"
    _saved(edit, {"activity": "other", "details": "Hunting"})
    changed = seasons.plan_for(saga, magus)
    assert changed is not None and changed.details == "Hunting"
    assert len(saga.season_plans) == 1  # replaced, not added
    clear = ops.remove(0)
    assert isinstance(clear, commands.Confirm)
    assert clear.question.startswith("Clear Leandro's plan (Other")
    assert clear.yes_label == "Clear"
    clear.apply()
    assert seasons.plan_for(saga, magus) is None


def test_the_plan_form_refuses_what_the_terminal_refuses():
    saga = _sample_saga_with_covenant()
    form = sf.plan_season(saga, saga.characters[0])
    assert (
        _problem(form, {"activity": "other"})
        == "Say in Notes what the season is spent on."
    )
    assert _problem(form, {"activity": "other", "details": "Hunting"}) is None
    # Cancelling (never applying) plans nothing.
    assert saga.season_plans == []


def test_nothing_to_clear_is_refused():
    saga = _sample_saga_with_covenant()
    refused = sf.clear_season(saga, saga.characters[0])
    assert isinstance(refused, commands.Refuse)
    assert refused.why == "Nothing is planned for Leandro this season."


def test_a_grog_plans_the_yearly_update():
    saga = _saga_with_grog()
    grog = saga.character("g")
    assert grog is not None
    ops = sf.character_season_ops(saga, grog)
    assert ops.edit is None and ops.remove is None
    assert sf.season_nouns(grog)[0] == "Yearly Update"
    assert ops.add is not None
    form = ops.add()
    assert isinstance(form, commands.Form)
    assert form.title == "Hugo's Yearly Update"
    _saved(form, {"vocational": "Single Weapon", "practice": "Brawl"})
    assert grog.grog_year is not None
    assert (grog.grog_year.vocational, grog.grog_year.practice) == (
        "Single Weapon",
        "Brawl",
    )
    assert grog.grog_year.vocational_xp == 7


def test_the_initiation_virtue_is_chosen_by_the_cores_list_or_the_terminals():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    by_key = {f.key: f for f in sf.season_plan_fields(saga, magus, None)}
    virtue = by_key["mystery_virtue"]
    assert virtue.kind == "picker" and virtue.picker is None
    assert virtue.choose is not None
    step = virtue.choose(None)
    assert isinstance(step, commands.Choose)
    affinity = next(c for c in step.choices() if c.value.id == "vf_affinity_with_art")
    form = step.apply(affinity.value)
    assert isinstance(form, commands.Form)
    chosen = form.apply({"art": "ignem"})
    assert chosen == commands.Picked(
        VirtueFlawInstance("vf_affinity_with_art", {"art": "ignem"})
    )
    # With the terminal's picker it is that picker field.
    picked = {
        f.key: f
        for f in sf.season_plan_fields(
            saga, magus, None, vf_picker=lambda *_args: lambda _current: None
        )
    }
    assert picked["mystery_virtue"].picker is not None
    # Choosing the plan's own Virtue again keeps what it names.
    existing = SeasonPlan(
        character_id=magus.id,
        year=1220,
        season="Spring",
        activity="undergo_initiation",
        effect_id="vf_affinity_with_art",
        effect_params={"art": "creo"},
    )
    values = {
        "activity": "undergo_initiation",
        "mystery_virtue": "vf_affinity_with_art",
    }
    plan = sf.season_plan_from(saga, magus, values, existing)
    assert (plan.effect_id, plan.effect_params) == (
        "vf_affinity_with_art",
        {"art": "creo"},
    )
    picked_instance = VirtueFlawInstance("vf_affinity_with_art", {"art": "ignem"})
    plan = sf.season_plan_from(
        saga, magus, values | {"mystery_virtue": picked_instance}, existing
    )
    assert plan.effect_params == {"art": "ignem"}


# -- the covenant's Seasons lists ------------------------------------------------


def test_the_covenant_lists_plan_and_clear_the_person_chosen():
    saga = _saga_with_grog()
    covenant = saga.covenants[0]
    magi = sf.covenant_season_ops(saga, covenant, "magus")
    assert magi.add is None and magi.edit is not None and magi.remove is not None
    assert magi.rows() == ["Leandro"]
    _saved(magi.edit(0), {"activity": "other", "details": "Hunting"})
    assert seasons.plan_for(saga, saga.characters[0]) is not None
    confirm = magi.remove(0)
    assert isinstance(confirm, commands.Confirm)
    confirm.apply()
    assert saga.season_plans == []
    grogs = sf.covenant_season_ops(saga, covenant, "grog")
    assert grogs.remove is None and grogs.rows() == ["Hugo"]
    assert grogs.edit is not None
    form = grogs.edit(0)
    assert isinstance(form, commands.Form) and form.title == "Hugo's Yearly Update"


# -- the laboratory's Planning list ---------------------------------------------


def test_lab_work_is_planned_and_cleared():
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    ops = lpf.planning_ops(saga, lab)
    assert ops.rows() == ["Spring 1220  nothing planned"]
    assert ops.edit is not None and ops.remove is not None
    form = ops.edit(0)
    assert isinstance(form, commands.Form)
    assert form.title == "Lab Work: Leandro in Leandro's Sanctum, Spring 1220"
    assert form.save_label == "Schedule"
    assert _problem(form, {}) == "Choose the lab work."
    assert form.live is not None
    assert "pawn(s) of Vim vis" in form.live({"activity": lab_seasons.EXTRACT})
    assert _saved(form, {"activity": lab_seasons.EXTRACT, "vis_to": "covenant"}) == []
    plan = seasons.plan_for(saga, saga.characters[0])
    assert plan is not None and plan.lab_id == lab.id
    assert (plan.activity, plan.vis_from) == (lab_seasons.EXTRACT, "covenant")
    assert ops.rows()[0].startswith("Spring 1220  Extract")
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form)
    assert {f.key: f.value for f in edit.fields()}["vis_to"] == "covenant"
    clear = ops.remove(0)
    assert isinstance(clear, commands.Confirm)
    assert clear.question.startswith("Clear Leandro's plan for Spring 1220 (")
    clear.apply()
    assert saga.season_plans == []
    refused = ops.remove(0)
    assert isinstance(refused, commands.Refuse)
    assert refused.why == "Nothing is planned for Spring 1220."


def test_a_new_spell_starts_from_a_spell_or_a_blank_design():
    saga = _sample_saga_with_covenant()
    saga.characters[0].spells_known = []
    lab = saga.laboratories[0]
    ops = lpf.planning_ops(saga, lab, lambda: 0)
    assert ops.add is not None
    choose = ops.add()
    assert isinstance(choose, commands.Choose)
    choices = choose.choices()
    assert choices[0].value is None
    assert "spell1" in [c.value for c in choices]
    form = choose.apply("spell1")
    assert isinstance(form, commands.Form)
    shown = {f.key: f.value for f in form.fields()}
    assert (shown["activity"], shown["name"]) == (
        lab_seasons.INVENT,
        "Ball of Abysmal Flame",
    )
    blank = choose.apply(None)
    assert isinstance(blank, commands.Form)
    typed = {
        "name": "Spark",
        "technique": "Creo",
        "form": "Ignem",
        "base_level": "5",
    }
    assert blank.live is not None and "Level 5" in blank.live(_values(blank, typed))
    _saved(blank, typed)
    plan = seasons.plan_for(saga, saga.characters[0])
    assert plan is not None and isinstance(plan.design, SpellDesign)
    assert (plan.design.name, plan.design.base_level) == ("Spark", 5)


def test_a_long_invention_is_scheduled_over_more_seasons():
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    form = lpf.plan_lab_season(saga, lab, None)
    assert isinstance(form, commands.Form)
    typed = {
        "activity": lab_seasons.INVENT,
        "name": "Big Flame",
        "technique": "Creo",
        "form": "Ignem",
        "base_level": "20",
    }
    told = _saved(form, typed)
    assert told and told[0].startswith("Planned through ")
    assert len(saga.season_plans) > 1
    assert len(lpf.planning_ops(saga, lab).rows()) >= 2


def test_lab_work_needs_a_magus_owner():
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    lab.owner_id = None
    ops = lpf.planning_ops(saga, lab)
    assert ops.add is not None and ops.edit is not None
    for step in (ops.add(), ops.edit(0)):
        assert isinstance(step, commands.Refuse)
        assert step.why == lpf.NO_OWNER
