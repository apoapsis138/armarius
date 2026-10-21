"""Paired plans: Be taught plans the teacher's Teach, Be trained the
master's season, Teach with a student the student's Be taught, and lab
work naming an assistant the assistant's Assist; a clash refuses Save,
and clearing one side clears the other."""

from __future__ import annotations

from test_lab_seasons import _plan as _lab_plan
from test_lab_seasons import _saga as _lab_saga

from ars_magica_manager import seasons
from ars_magica_manager.commands import Confirm
from ars_magica_manager.forms import lab_plan as lab_plan_forms
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import laboratory_seasons as ls
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons import pairs


def _saga() -> tuple[Saga, Character, Character]:
    teacher = Character(id="t", name="Tiberius", type="magus")
    teacher.characteristics = Characteristics(communication=2)
    teacher.abilities = [
        Ability("Latin", xp=ability_xp(5)),
        Ability("Teaching", xp=ability_xp(2)),
    ]
    student = Character(id="s", name="Bertram", type="companion")
    student.abilities = [Ability("Latin", xp=ability_xp(1))]
    saga = Saga(
        id="test_saga",
        name="Pairs",
        current_year=1220,
        current_season="Spring",
        characters=[teacher, student],
    )
    return saga, teacher, student


TAUGHT = {"activity": rules.TAUGHT, "teacher_id": "t", "subject_1": "ability:Latin"}


def _theirs(saga, character) -> SeasonPlan | None:
    return seasons.plan_for(saga, character)


def test_being_taught_plans_the_teachers_teach():
    saga, teacher, student = _saga()
    form = season_forms.plan_season(saga, student)
    assert form.validate is not None and form.validate(TAUGHT) is None
    assert form.live is not None and "Also plans Tiberius's season" in form.live(TAUGHT)
    season_forms.save_season(saga, student, TAUGHT)
    teach = _theirs(saga, teacher)
    assert teach is not None and teach.activity == rules.TEACH
    assert teach.partner_id == student.id
    assert rules.outcome(student, _theirs(saga, student), saga).ok


def test_a_teacher_already_teaching_is_left_as_it_is():
    saga, teacher, student = _saga()
    mine = SeasonPlan(teacher.id, 1220, "Spring", rules.TEACH)
    seasons.set_plan(saga, mine)
    season_forms.save_season(saga, student, TAUGHT)
    assert _theirs(saga, teacher) is mine


def test_a_teacher_planned_for_something_else_refuses_save():
    saga, teacher, student = _saga()
    seasons.set_plan(saga, SeasonPlan(teacher.id, 1220, "Spring", rules.PRACTICE))
    form = season_forms.plan_season(saga, student)
    assert form.validate is not None
    why = form.validate(TAUGHT) or ""
    assert "Tiberius already has Practice" in why and "change or clear" in why


def test_being_trained_plans_the_masters_season_at_the_ability():
    saga, teacher, student = _saga()
    values = {**TAUGHT, "activity": rules.TRAINED}
    season_forms.save_season(saga, student, values)
    work = _theirs(saga, teacher)
    assert work is not None and work.activity == rules.EXPOSURE
    assert work.allocations[0].subject == "ability:Latin"
    assert "Training Bertram" in work.details


def test_a_busy_master_is_not_refused():
    saga, teacher, student = _saga()
    seasons.set_plan(saga, SeasonPlan(teacher.id, 1220, "Spring", rules.PRACTICE))
    form = season_forms.plan_season(saga, student)
    assert form.validate is not None
    assert pairs.pair_problem(saga, student, season_forms.season_plan_from(
        saga, student, {**TAUGHT, "activity": rules.TRAINED}
    )) is None  # fmt: skip
    season_forms.save_season(saga, student, {**TAUGHT, "activity": rules.TRAINED})
    kept = _theirs(saga, teacher)
    assert kept is not None and kept.activity == rules.PRACTICE


def test_teach_with_a_student_plans_their_be_taught():
    saga, teacher, student = _saga()
    values = {
        "activity": rules.TEACH,
        "subject_1": "ability:Teaching",
        "student_id": "s",
        "student_subject": "ability:Latin",
    }
    fields = {f.key: f for f in season_forms.season_plan_fields(saga, teacher, None)}
    assert fields["student_subject"].show_if is not None
    assert fields["student_subject"].show_if(values)
    form = season_forms.plan_season(saga, teacher)
    assert form.validate is not None and form.validate(values) is None
    season_forms.save_season(saga, teacher, values)
    taught = _theirs(saga, student)
    assert taught is not None and taught.activity == rules.TAUGHT
    assert taught.teacher_id == teacher.id
    assert taught.allocations[0].subject == "ability:Latin"


def test_changing_the_plan_takes_its_pair_away():
    saga, teacher, student = _saga()
    season_forms.save_season(saga, student, TAUGHT)
    existing = _theirs(saga, student)
    season_forms.save_season(
        saga, student, {"activity": rules.EXPOSURE, "subject_1": "ability:Latin"},
        existing,
    )  # fmt: skip
    assert _theirs(saga, teacher) is None


def test_clearing_either_side_clears_both_after_one_question():
    saga, teacher, student = _saga()
    season_forms.save_season(saga, student, TAUGHT)
    step = season_forms.clear_season(saga, teacher)
    assert isinstance(step, Confirm)
    assert "Bertram's plan for Spring 1220 is cleared with it" in step.question
    step.apply()
    assert saga.season_plans == []
    season_forms.save_season(saga, student, TAUGHT)
    step = season_forms.clear_season(saga, student)
    assert isinstance(step, Confirm) and "Tiberius's plan" in step.question
    step.apply()
    assert saga.season_plans == []


def test_a_teach_another_student_needs_is_kept():
    saga, teacher, student = _saga()
    other = Character(id="o", name="Odo", type="companion")
    other.abilities = [Ability("Latin", xp=ability_xp(1))]
    saga.characters.append(other)
    season_forms.save_season(saga, student, TAUGHT)
    season_forms.save_season(saga, other, TAUGHT)
    step = season_forms.clear_season(saga, student)
    assert isinstance(step, Confirm) and "cleared with it" not in step.question
    step.apply()
    assert _theirs(saga, teacher) is not None
    assert _theirs(saga, other) is not None


def _with_helper():
    saga = _lab_saga()
    helper = Character(id="h", name="Celsus", type="magus", covenant_id="cov")
    helper.characteristics = Characteristics(intelligence=3)
    helper.abilities = [Ability("Magic Theory", xp=ability_xp(3))]
    saga.characters.append(helper)
    return saga, saga.characters[0], helper


def test_lab_work_naming_an_assistant_plans_their_assist():
    saga, magus, helper = _with_helper()
    form = lab_plan_forms.LabPlanForm(
        saga, magus, saga.laboratories[0], "Spring", 1220, None,
        activity="invent",
    )  # fmt: skip
    assert ("Celsus", "h") in form.helpers()
    plan = _lab_plan("bolt", assistant_ids=["h"])
    added = seasons.plan_lab_work(saga, plan)
    assist = seasons.plan_for(saga, helper)
    assert assist is not None and assist.activity == ls.ASSIST
    assert assist.teacher_id == magus.id
    # The helper's Intelligence + Magic Theory (+6) finish it in one season.
    assert added == []


def test_clearing_an_assist_leaves_the_lab_work():
    saga, magus, helper = _with_helper()
    seasons.plan_lab_work(saga, _lab_plan("bolt", assistant_ids=["h"]))
    step = season_forms.clear_season(saga, helper)
    assert isinstance(step, Confirm)
    step.apply()
    lead = seasons.plan_for(saga, magus)
    assert lead is not None and lead.assistant_ids == []
    assert seasons.plan_for(saga, helper) is None


def test_clearing_lab_work_clears_its_assistants():
    saga, _magus, _helper = _with_helper()
    seasons.plan_lab_work(saga, _lab_plan("bolt", assistant_ids=["h"]))
    step = lab_plan_forms.clear_lab_season(saga, saga.laboratories[0], 0)
    assert isinstance(step, Confirm) and "Celsus's plans" in step.question
    step.apply()
    assert saga.season_plans == []
