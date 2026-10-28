"""Recreating a flawed creation (DE p. 274): the creations a magus may
recreate, the Magic Theory their record adds again, and what finishing the
recreation does."""

from test_lab_seasons import _design, _plan, _saga

from ars_magica_manager import seasons
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import advance
from ars_magica_manager.forms.lab_plan import LabPlanForm
from ars_magica_manager.models import (
    EnchantedDevice,
    ExperimentalEffect,
    InstilledEffect,
    KnownSpell,
    Spell,
)
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules import lab_seasons, recreating


def _flaw(season="Spring", year=1219, theory=4, result="major flaw"):
    return ExperimentalEffect(
        "side", result, year=year, season=season, magic_theory=theory
    )


def _with_flawed_spell(saga, *effects):
    magus = saga.character("m")
    spell = Spell(
        "ward-x",
        "Hot Ward",
        "Creo",
        "Ignem",
        level=4,
        base_level=4,
        range="Personal",
        duration="Momentary",
        target="Individual",
        experimental_effects=list(effects or [_flaw()]),
    )
    magus.invented_spells.append(spell)
    magus.spells_known.append(KnownSpell(spell_id=spell.id))
    return spell


def _recreatable(saga, activity=lab_seasons.INVENT, season="Spring", year=1220):
    return recreating.recreatable(saga, saga.character("m"), activity, year, season)


def test_a_flawed_spell_of_the_magus_can_be_recreated_with_its_result_shown():
    saga = _saga()
    _with_flawed_spell(saga)
    (found,) = _recreatable(saga)
    assert found.key == "spell:ward-x"
    assert found.theory == 4
    assert found.label == (
        "Hot Ward: Side effect: major flaw (Magic Theory 4, Spring 1219)"
    )


def test_a_spell_no_longer_known_or_never_flawed_is_not_offered():
    saga = _saga()
    spell = _with_flawed_spell(saga)
    saga.character("m").spells_known = []
    assert _recreatable(saga) == []
    saga.character("m").spells_known = [KnownSpell(spell_id=spell.id)]
    spell.experimental_effects = []
    assert _recreatable(saga) == []


def test_the_recreation_must_come_after_the_last_experimental_season():
    """A project over several seasons: its last season's Magic Theory, and
    only a season after that one (the app's call: DE doesn't say)."""
    saga = _saga()
    _with_flawed_spell(
        saga, _flaw("Summer", 1219, 3), _flaw("Winter", 1219, 5, "minor side effect")
    )
    assert _recreatable(saga, season="Winter", year=1219) == []
    (found,) = _recreatable(saga, season="Spring", year=1220)
    assert found.theory == 5
    assert (found.season, found.year) == ("Winter", 1219)


def test_only_the_maguss_own_item_effects_are_offered_to_instil_again():
    saga = _saga()
    mine = InstilledEffect(
        id="e1", name="Flame", instilled_by="m", experimental_effects=[_flaw()]
    )
    theirs = InstilledEffect(
        id="e2", name="Frost", instilled_by="other", experimental_effects=[_flaw()]
    )
    saga.enchanted_devices = [
        EnchantedDevice(id="d", name="Staff", effects=[mine, theirs])
    ]
    (found,) = _recreatable(saga, es.INSTIL)
    assert found.key == "effect:e1"
    assert found.name == "Staff: Flame"
    assert _recreatable(saga, lab_seasons.INVENT) == []


def test_a_longevity_ritual_is_recreated_only_for_its_own_subject():
    saga = _saga()
    magus = saga.character("m")
    magus.aging.longevity_by = magus.name
    magus.aging.longevity_effects = [_flaw()]
    (found,) = _recreatable(saga, lab_seasons.LONGEVITY)
    assert found.key == "longevity:m"
    plan = _plan(activity=lab_seasons.LONGEVITY, recreating="longevity:m")
    assert recreating.problem(magus, plan) is None
    plan.subject_id = "someone-else"
    assert recreating.problem(magus, plan) is not None


def _form(saga, existing=None):
    return LabPlanForm(
        saga,
        saga.character("m"),
        saga.laboratories[0],
        "Spring",
        1220,
        existing,
        activity=lab_seasons.INVENT,
    )


def test_choosing_the_flawed_spell_takes_the_magic_theory_from_its_record():
    saga = _saga()
    _with_flawed_spell(saga)
    form = _form(saga)
    keys = [f.key for f in form.fields()]
    assert "recreating_spell" in keys
    assert "recreating_theory" not in keys  # the record keeps the score
    plan = form.plan_of(
        {"activity": lab_seasons.INVENT, "recreating_spell": "spell:ward-x"}
    )
    assert (plan.recreating, plan.recreating_theory) == ("spell:ward-x", 4)
    chosen = _plan(
        "ward-x", recreating=plan.recreating, recreating_theory=plan.recreating_theory
    )
    why, work = lab_seasons.work(saga, saga.character("m"), chosen)
    assert work is not None, why
    assert any(
        line.amount == 4 and "Recreating" in line.label for line in work.lab_total.lines
    )


def test_a_record_without_magic_theory_asks_for_it():
    saga = _saga()
    _with_flawed_spell(saga, _flaw(theory=None))
    form = _form(saga)
    (typed,) = [f for f in form.fields() if f.key == "recreating_theory"]
    values = {"activity": lab_seasons.INVENT, "recreating_spell": "spell:ward-x"}
    assert typed.show_if is not None and typed.show_if(values)
    plan = form.plan_of(values | {"recreating_theory": 2})
    assert plan.recreating_theory == 2


def test_a_plan_from_before_the_choice_keeps_its_typed_score():
    saga = _saga()
    old = _plan("bolt", recreating_theory=3)
    seasons.set_plan(saga, old)
    form = _form(saga, old)
    plan = form.plan_of({"activity": lab_seasons.INVENT, "recreating_theory": 3})
    assert (plan.recreating, plan.recreating_theory) == ("", 3)


def _recreate(saga, retire: bool):
    design = _design(base_level=4, range="Personal", source_spell_id="ward-x")
    seasons.plan_lab_work(saga, _plan(design=design, recreating="spell:ward-x"))
    worked = seasons.resolve(saga)
    step = advance._retire_flawed(saga, worked, lambda: "next")
    assert isinstance(step, Form)
    assert step.title == "Retire Flawed Spells"
    assert step.apply({"retire_0": retire}) == "next"
    seasons.apply(saga, worked)
    return saga.character("m")


def test_a_recreated_spell_is_a_new_spell_and_both_stay_known():
    saga = _saga()
    _with_flawed_spell(saga)
    magus = _recreate(saga, retire=False)
    clean = magus.invented_spells[-1]
    assert clean.id != "ward-x"
    assert clean.experimental_effects == []
    assert {k.spell_id for k in magus.spells_known} == {"ward-x", clean.id}


def test_retiring_the_flawed_spell_takes_it_off_known_spells():
    saga = _saga()
    _with_flawed_spell(saga)
    magus = _recreate(saga, retire=True)
    clean = magus.invented_spells[-1]
    assert [k.spell_id for k in magus.spells_known] == [clean.id]
    # Its record and Lab Text are kept: only the knowing goes.
    assert any(s.id == "ward-x" for s in magus.invented_spells)


def test_nothing_to_retire_skips_the_step():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan("bolt"))
    worked = seasons.resolve(saga)
    assert advance._retire_flawed(saga, worked, lambda: "next") == "next"
