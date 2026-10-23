"""Advance Season's Experiment Results step: the storyguide's word on each
experiment, and what it does to the season and the creation."""

from test_experiment import _Dice, _plan, _saga

from ars_magica_manager import catalog, seasons
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import experiment_results as er
from ars_magica_manager.models import (
    STORY_EVENT,
    ArtScore,
    BondPower,
    DiaryEntry,
    ExperimentalEffect,
    InstilledEffect,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules import experiment as ex
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules.xp import art_xp


def _resolve(*faces: int, **plan):
    saga = _saga()
    seasons.set_plan(saga, _plan(**plan))
    return saga, seasons.resolve(saga, _Dice(*faces))


def _form(saga, worked) -> Form:
    form = er.experiment_results(saga, worked, lambda: "done", lambda: _Dice())
    assert isinstance(form, Form)
    return form


def _values(form: Form, **answers):
    values = {f.key: f.value for f in form.fields() if not f.key.startswith("_")}
    return values | answers


def _bolt(saga):
    (known,) = saga.character("m").spells_known
    return catalog.find_spell(saga, known.spell_id)


def test_nothing_to_decide_asks_nothing():
    # Die 5; chart 3 + 1 = 4: no extraordinary effects.
    saga, worked = _resolve(5, 3)
    assert er.experiment_results(saga, worked, lambda: "done", lambda: _Dice()) == (
        "done"
    )


def test_a_side_effect_is_described_and_stays_with_the_spell():
    # Die 5; chart 4 + 1 = 5: a side effect (simple die 3: minor flaw).
    saga, worked = _resolve(5, 4, 3)
    form = _form(saga, worked)
    assert form.title == "Experiment Results: Tiberius"
    assert form.help_id == "advance-experiment-results"
    done = form.apply(_values(form, a_e0_description="it smells of cinnamon"))
    assert done == "done"
    seasons.apply(saga, worked)
    (effect,) = _bolt(saga).experimental_effects
    assert (effect.kind, effect.result, effect.description) == (
        "side",
        "minor flaw",
        "it smells of cinnamon",
    )
    assert (effect.year, effect.season, effect.magic_theory) == (1220, "Spring", 6)


def test_a_modified_effect_changes_the_range_but_never_the_level():
    # Die 5; chart 10 + 1 = 11: a modified effect (9 + 1: increased).
    saga, worked = _resolve(5, 10, 9)
    form = _form(saga, worked)
    form.apply(_values(form, a_e0_parameter="range", a_e0_range="Voice"))
    seasons.apply(saga, worked)
    spell = _bolt(saga)
    assert (spell.range, spell.level) == ("Voice", 10)
    (effect,) = spell.experimental_effects
    assert (effect.kind, effect.range, effect.potency) == ("modified", "Voice", 0)
    assert "[Range Voice; level kept]" in ex.describe(effect)


def test_the_storyguide_chooses_which_of_two_rolls_stands():
    saga = _saga()
    saga.character("m").virtues_flaws = [VirtueFlawInstance("vf_creative_block")]
    seasons.set_plan(saga, _plan())
    # Die 5; first roll 3 + 1 = 4 (nothing), second 4 + 1 = 5 (side effect,
    # rolled twice: 3 and 6).
    worked = seasons.resolve(saga, _Dice(5, 3, 4, 3, 6))
    form = _form(saga, worked)
    roll = next(f for f in form.fields() if f.key == "roll")
    assert [value for _label, value in roll.options] == ["a", "b"]
    form.apply(_values(form, roll="b", b_e0_result=ex.SIDE_EFFECTS[6]))
    seasons.apply(saga, worked)
    (effect,) = _bolt(saga).experimental_effects
    assert effect.result == ex.SIDE_EFFECTS[6]


def test_a_story_event_is_an_open_line_in_the_covenants_diary():
    # Die 5; chart 8 + 1 = 9: a special result.
    saga, worked = _resolve(5, 8)
    form = _form(saga, worked)
    form.apply(_values(form, a_s0_kind="story", a_s0_text="A salamander visits"))
    seasons.apply(saga, worked)
    entry = saga.covenants[0].diary[-1]
    assert (entry.category, entry.status, entry.details) == (
        STORY_EVENT,
        "Open",
        "A salamander visits",
    )


def test_extra_vis_is_paid_or_the_season_is_a_complete_failure():
    saga, worked = _resolve(5, 8)
    form = _form(saga, worked)
    form.apply(_values(form, a_s0_kind="vis"))
    work = worked[0].lab_work
    assert work.experiment.wasted and work.experiment.failure

    saga, worked = _resolve(5, 8)
    saga.character("m").raw_vis = {"creo": 5}
    form = _form(saga, worked)
    form.apply(_values(form, a_s0_kind="vis"))
    # Level 10 is magnitude 2, plus risk 1.
    assert worked[0].lab_work.experiment.extra_vis == {"Creo": 3}
    seasons.apply(saga, worked)
    assert saga.character("m").raw_vis == {"creo": 2}


def test_a_bonus_spell_opens_the_spell_form_and_is_learned():
    saga, worked = _resolve(5, 8)
    form = _form(saga, worked)
    spell_form = form.apply(_values(form, a_s0_kind="spell"))
    assert isinstance(spell_form, Form)
    values = _values(
        spell_form,
        name="Spark",
        level=40,
        range="Touch",
        duration="Momentary",
        target="Individual",
    )
    assert "at most 17" in (spell_form.validate(values) or "")
    assert spell_form.apply(values | {"level": 5}) == "done"
    seasons.apply(saga, worked)
    names = {
        catalog.find_spell(saga, k.spell_id).name
        for k in saga.character("m").spells_known
    }
    assert names == {"Bolt", "Spark"}
    assert any(b.name.endswith("Spark") for b in saga.books)


def _disaster(**answers):
    # Risk +3 in an aura of 1: five botch dice. Die 5; the chart's stress
    # die 0, then all five botch dice 0.
    saga = _saga()
    saga.covenants[0].aura = 1
    seasons.set_plan(saga, _plan(risk=3))
    worked = seasons.resolve(saga, _Dice(5, 0, 0, 0, 0, 0, 0))
    assert worked[0].lab_work.experiment.zeroes == 5
    form = _form(saga, worked)
    form.apply(_values(form, **answers))
    seasons.apply(saga, worked)
    return saga


def test_a_disaster_of_five_zeroes_can_threaten_the_covenant_instead():
    saga = _disaster(a_disaster="covenant")
    assert not saga.character("m").wounds.incapacitated
    assert saga.covenants[0].diary[-1].category == STORY_EVENT
    # The laboratory destroyed, by default.
    saga = _disaster()
    assert saga.character("m").wounds.incapacitated
    flaws = {vf.vf_id for vf in saga.laboratories[0].virtues_flaws}
    assert {"labvf_deformed", "labvf_unstable"} <= flaws


def test_older_saves_keep_their_experimental_effects_as_records():
    spell = Spell.from_dict(
        {
            "id": "x",
            "name": "X",
            "technique": "Creo",
            "form": "Ignem",
            "experimental_effects": ["Side effect: minor flaw", "a strange glow"],
        }
    )
    assert [(e.kind, e.result) for e in spell.experimental_effects] == [
        ("side", "minor flaw"),
        ("special", "a strange glow"),
    ]
    effect = InstilledEffect.from_dict(
        {"id": "e", "name": "Glow", "description": "Light.\nExperimental: odd hue"}
    )
    assert effect.description == "Light."
    assert [e.result for e in effect.experimental_effects] == ["odd hue"]
    power = BondPower.from_dict(
        {
            "id": "p",
            "name": "Sight",
            "cosmetic_trait": "Bright eyes (Side effect: minor flaw)",
        }
    )
    assert power.cosmetic_trait == "Bright eyes"
    assert power.experimental_effects == [ExperimentalEffect("side", "minor flaw")]


def test_a_less_potent_longevity_ritual_protects_less():
    saga = _saga()
    magus = saga.character("m")
    magus.arts["corpus"] = ArtScore(xp=art_xp(5))
    magus.background.year_born = 1195
    magus.raw_vis = {"creo": 8}
    seasons.set_plan(
        saga,
        SeasonPlan(
            "m",
            1220,
            "Spring",
            lab_seasons.LONGEVITY,
            lab_id="lab",
            vis_art="Creo",
            experimenting=True,
            risk=1,
        ),
    )
    # Die 5; chart 10 + 1 = 11: a modified effect (1 + 1: reduced).
    worked = seasons.resolve(saga, _Dice(5, 10, 1))
    work = worked[0].lab_work
    assert [e.result for e in work.experiment.effects] == [ex.REDUCED]
    form = _form(saga, worked)
    potency = next(f for f in form.fields() if f.key == "a_e0_potency")
    assert potency.value == -1
    form.apply(_values(form))
    seasons.apply(saga, worked)
    assert magus.aging.longevity_modifier == work.longevity - 1
    (effect,) = magus.aging.longevity_effects
    assert effect.potency == -1


def test_an_experiment_too_low_for_its_work_still_rolls_the_chart():
    saga = _saga()
    saga.spells[0].level = 40
    magus = saga.character("m")
    # Without experimenting it is refused; experimenting, the plan says so.
    assert lab_seasons.work(saga, magus, _plan(experimenting=False))[1] is None
    found, work = lab_seasons.work(saga, magus, _plan())
    assert found == [] and "can't be invented yet" in work.too_low
    seasons.set_plan(saga, _plan())
    # Die 5: 28 + 5 + 1 = 34, still not above 40; the chart 4 + 1 = 5.
    worked = seasons.resolve(saga, _Dice(5, 4, 3))
    (outcome,) = worked
    assert outcome.lab_work.points_gained == 0 and not outcome.lab_work.finished
    assert any("the season goes ahead all the same" in n for n in outcome.notes)
    assert [e.result for e in outcome.lab_work.experiment.effects] == ["minor flaw"]
    seasons.apply(saga, worked)
    assert magus.spells_known == []


def _investigation(protected: bool):
    import test_enchant_seasons as te

    saga = te._saga()
    plan = te._plan(
        es.INVESTIGATE,
        device_id="box",
        die=3,
        experimenting=True,
        risk=1,
        experiment_die=5,
    )
    seasons.set_plan(saga, plan)
    # The chart's stress die 0, then both botch dice 0: a Disaster of two.
    worked = seasons.resolve(saga, _Dice(0, 0, 0))
    chart = worked[0].lab_work.experiment
    assert chart.zeroes == 2 and chart.item_at_risk
    form = _form(saga, worked)
    form.apply(_values(form, a_protected=protected))
    seasons.apply(saga, worked)
    return saga


def test_an_experiment_can_destroy_the_item_investigated_unless_it_is_protected():
    assert "box" not in {d.id for d in _investigation(False).enchanted_devices}
    assert "box" in {d.id for d in _investigation(True).enchanted_devices}


def test_a_lab_diary_entry_of_original_research_is_now_arcane_discovery():
    entry = DiaryEntry.from_dict(
        {"year": 1220, "season": "Spring", "name": "x", "activity": "Original Research"}
    )
    assert entry.activity == "Arcane Discovery"
