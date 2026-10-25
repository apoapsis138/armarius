"""New and overlapping Initiation Scripts, unGifted and hedge Initiations,
and a failed Initiation that spends no Ordeal step (The Mysteries Revised
Edition pp. 12-18; Legends of Hermes pp. 50-51; Hedge Magic Revised
Edition pp. 13-14; DE pp. 386-389)."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import seasons
from ars_magica_manager.forms import season as sf
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Ordeal,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import dice, mysteries
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.xp import ability_xp

FOLK = "trad_folk_witches"
FLIGHT = f"{FOLK}/Unbound by Land"  # Ease 15, +6, gains Flight (Minor)
MATHEMATICI = "trad_learned_magicians"  # no self-initiation


def _saga() -> Saga:
    """Wulf, an unGifted companion; Mira, a magus Mystagogue; Agnes, an
    unGifted folk witch with Flight."""
    wulf = Character(id="c", name="Wulf", type="companion")
    wulf.characteristics = Characteristics(presence=2, intelligence=1)
    wulf.abilities = [Ability("Mercere Lore", xp=ability_xp(5))]
    mira = Character(id="m", name="Mira", type="magus")
    mira.characteristics = Characteristics(presence=2, intelligence=2)
    mira.abilities = [Ability("Mercere Lore", xp=ability_xp(6))]
    agnes = Character(id="w", name="Agnes", type="companion")
    agnes.characteristics = Characteristics(presence=3, intelligence=1)
    agnes.traditions = [FOLK]
    agnes.abilities = [Ability("Folk Witch Magic Theory", xp=ability_xp(4))]
    agnes.virtues_flaws = [VirtueFlawInstance("vf_flight")]
    return Saga(id="s", name="S", characters=[wulf, mira, agnes])


def _plan(character_id: str = "c", **kw) -> SeasonPlan:
    base = {
        "title": "Mercere Lore",
        "effect_id": "vf_puissant_ability",
        "effect_params": {"ability": "Brawl"},
    }
    return SeasonPlan(
        character_id, 1220, "Spring", "undergo_initiation", [], **(base | kw)
    )


def _minor_ordeal() -> dict:
    return {"ordeal_kind": "gain", "device_id": "vf_arthritis"}


def _problems(saga: Saga, plan: SeasonPlan, who: str = "c") -> list[str]:
    person = saga.character(who)
    assert person is not None
    return sw.problems(saga, person, plan)


def _work(saga: Saga, plan: SeasonPlan, rng: random.Random | None = None):
    wulf = saga.character("c")
    assert wulf is not None
    assert sw.problems(saga, wulf, plan) == []
    return sw.work(saga, wulf, plan, rng)


def _run(saga: Saga, plan: SeasonPlan) -> Character:
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, random.Random(1)))
    found = saga.character(plan.character_id)
    assert found is not None
    return found


# -- a failed Initiation spends no Ordeal step (DE p. 388) ----------------------


def test_a_failed_initiation_spends_no_step_of_a_past_ordeal():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    wulf.type = "magus"  # Gifted: his past Ordeals count
    wulf.ordeals = [Ordeal("Major", 0)]
    plan = _plan(teacher_id="m", other_modifier=0)
    # Mira's Presence 2 + Lore 6 = 8 against 18 - 9 = 9: not initiated.
    wulf = _run(saga, plan)
    assert wulf.ordeals == [Ordeal("Major", 0)]
    plan = _plan(teacher_id="m", other_modifier=1)
    wulf = _run(saga, plan)
    assert wulf.ordeals == [Ordeal("Major", 1)]


def test_a_distracted_failure_records_its_ordeal_but_spends_no_step():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    wulf.type = "magus"
    wulf.ordeals = [Ordeal("Minor", 1)]
    # 2 + 6 + 10 = 18 against 18 - 2, less a third for a month lost.
    plan = _plan(teacher_id="m", other_modifier=10, months_lost=1, **_minor_ordeal())
    wulf = _run(saga, plan)
    assert wulf.ordeals == [Ordeal("Minor", 1), Ordeal("Minor", 0)]


# -- unGifted Initiations (HMRE p. 14) ------------------------------------------


def test_an_ungifted_initiate_needs_an_ordeal():
    saga = _saga()
    assert _problems(saga, _plan(teacher_id="m")) == [
        "Wulf is unGifted: the Initiation must include an Ordeal (Hedge Magic "
        "Revised Edition p. 14)."
    ]
    assert _problems(saga, _plan(teacher_id="m", **_minor_ordeal())) == []


def test_an_ungifted_initiate_can_t_initiate_himself():
    saga = _saga()
    assert _problems(saga, _plan(**_minor_ordeal())) == [
        "Wulf can't Initiate himself: an unGifted Mystagogue must know the power "
        "(Hedge Magic Revised Edition p. 14)."
    ]


def test_an_ungifted_mystagogue_must_know_the_power():
    saga = _saga()
    agnes = saga.character("w")
    assert agnes is not None
    agnes.abilities.append(Ability("Mercere Lore", xp=ability_xp(3)))
    plan = _plan(teacher_id="w", **_minor_ordeal())
    assert "Agnes can't be the Mystagogue" in _problems(saga, plan)[0]
    plan.knows_power = True
    assert _problems(saga, plan) == []


def test_an_ungifted_initiate_s_past_ordeals_lower_nothing():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    wulf.ordeals = [Ordeal("Major", 0)]
    plan = _plan(teacher_id="m", **_minor_ordeal())
    assert sw.ordeal_reduction(wulf) == 0
    assert sw.initiation_target(saga, wulf, plan) == 18
    wulf.type = "magus"
    assert sw.initiation_target(saga, wulf, plan) == 9


# -- hedge Scripts (HMRE p. 13) --------------------------------------------------


def test_a_hedge_script_s_target_rises_when_the_power_is_unknown():
    assert mysteries.hedge_target(15, "Minor", True).total == 15
    assert mysteries.hedge_target(15, "Minor", False).total == 18
    assert mysteries.hedge_target(21, "Major", False).total == 30
    # A past Ordeal lowers it, never below 9, nor a low Ease Factor at all.
    assert mysteries.hedge_target(21, "Major", True, reduction=9).total == 12
    assert mysteries.hedge_target(15, "Minor", True, reduction=9).total == 9
    assert mysteries.hedge_target(6, "Minor", True, reduction=3).total == 6


def test_a_script_s_tier_when_no_virtue_names_it():
    assert mysteries.script_tier(21, "Give 1") == "Major"
    assert mysteries.script_tier(15, "Curse 1") == "Minor"
    assert mysteries.script_tier(18, "Elysian Ecstasy (Minor)") == "Minor"
    assert mysteries.script_tier(15, "Cursing (Major)") == "Major"


def test_the_saga_s_traditions_offer_their_scripts():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    keys = [key for _, key in ts.script_options(saga, wulf)]
    assert FLIGHT in keys
    assert all(key.startswith(FOLK + "/") for key in keys)
    found = ts.hedge_script(FLIGHT)
    assert found is not None and found[1].ease_factor == 15
    assert ts.hedge_script("trad_folk_witches/No such rite") is None


def test_a_folk_witch_initiates_flight_by_her_script():
    saga = _saga()
    plan = _plan(
        teacher_id="w",
        title="",
        effect_id="vf_flight",
        effect_params={},
        hedge_script=FLIGHT,
        ordeal_kind="gain",
        device_id="vf_arthritis",
    )
    # Agnes knows Flight: Ease 15. Presence 3 + Folk Witch Magic Theory 4
    # + Script 6 = 13: short.
    wulf = saga.character("c")
    assert wulf is not None
    assert sw.initiation_target(saga, wulf, plan) == 15
    done = _work(saga, plan)
    assert done.notes[-1].startswith(
        "Initiation Total 13 (Presence + Folk Witch Magic Theory + Script 6)"
    )
    assert not done.initiated
    plan.other_modifier = 2  # a Quest the troupe adds
    done = _work(saga, plan)
    assert done.initiated
    assert [vf.vf_id for vf in done.add_vfs] == ["vf_flight", "vf_arthritis"]


def test_a_hedge_mystagogue_who_lacks_the_power_faces_plus_three():
    saga = _saga()
    agnes = saga.character("w")
    assert agnes is not None
    agnes.virtues_flaws = []
    wulf = saga.character("c")
    assert wulf is not None
    plan = _plan(teacher_id="w", title="", hedge_script=FLIGHT, **_minor_ordeal())
    plan.effect_id, plan.effect_params = "vf_flight", {}
    assert sw.initiation_target(saga, wulf, plan) == 18
    # And unGifted, she can't lead it at all until she knows the power.
    assert "Agnes can't be the Mystagogue" in _problems(saga, plan)[0]
    plan.knows_power = True
    assert sw.initiation_target(saga, wulf, plan) == 15
    assert _problems(saga, plan) == []


def test_a_hedge_initiation_needs_no_virtue_but_says_what_it_gives():
    saga = _saga()
    plan = _plan(
        teacher_id="w",
        title="",
        effect_id=None,
        effect_params={},
        hedge_script=FLIGHT,
        knows_power=True,
        other_modifier=5,
        **_minor_ordeal(),
    )
    done = _work(saga, plan)
    assert done.initiated
    assert [vf.vf_id for vf in done.add_vfs] == ["vf_arthritis"]
    assert done.notes[-1].endswith("Add what it gives by hand: Flight (Minor).")


def test_what_stops_a_hedge_initiation():
    saga = _saga()
    plan = _plan(teacher_id="m", title="", hedge_script=FLIGHT, **_minor_ordeal())
    assert _problems(saga, plan) == [
        "Mira isn't one of the Folk Witches: the Mystagogue must be."
    ]
    agnes = saga.character("w")
    assert agnes is not None
    agnes.traditions.append(MATHEMATICI)
    agnes.abilities.append(Ability("Organization Lore: Mathematici", xp=ability_xp(3)))
    agnes.virtues_flaws.append(VirtueFlawInstance("vf_the_gift"))
    tueor = _plan(
        character_id="w",
        title="",
        effect_id=None,
        hedge_script=f"{MATHEMATICI}/Tueor",
        **_minor_ordeal(),
    )
    assert _problems(saga, tueor, "w") == [
        "The Learned Magicians can't Initiate themselves: choose a Mystagogue."
    ]
    plan.hedge_script = "trad_folk_witches/No such rite"
    assert _problems(saga, plan) == [
        "That hedge Script is no longer in the catalog: choose another."
    ]


def test_a_script_fails_an_initiate_short_of_its_scores():
    # The master tests Philosophiae 2 (HMRE p. 88).
    tueor = ts.hedge_script(f"{MATHEMATICI}/Tueor")
    assert tueor is not None and dict(tueor[1].requires) == {"Philosophiae": 2}
    # Every Ikhwan Script: Artes Liberales, Philosophiae, Theology (Islam)
    # 4 and Arabic 5 (pp. 30-31); Tulab Ibn Sina's by Script (p. 31).
    blood = ts.hedge_script("trad_elementalists/Ikhwan: Blood Oath")
    assert blood is not None
    assert dict(blood[1].requires)["Living Language: Arabic"] == 5
    humor = ts.hedge_script(
        "trad_elementalists/Tulab: Discovering the Physician's Humor"
    )
    assert humor is not None and dict(humor[1].requires) == {
        "Medicine": 4,
        "Chirurgy": 4,
    }
    saga = _saga()
    wulf, agnes = saga.character("c"), saga.character("w")
    assert wulf is not None and agnes is not None
    agnes.traditions.append(MATHEMATICI)
    agnes.abilities.append(Ability("Organization Lore: Mathematici", xp=ability_xp(3)))
    found = sw._hedge_problem(wulf, agnes, *tueor)
    assert "always fails for an Initiate without Philosophiae 2" in found
    wulf.abilities.append(Ability("Philosophiae", xp=ability_xp(2)))
    assert sw._hedge_problem(wulf, agnes, *tueor) == ""


def test_a_gruagach_initiating_himself_faces_the_harder_ease():
    # 15, or 18 self-initiated (HMRE p. 61).
    fetch = ts.hedge_script("trad_gruagachan/Calling the Fetch")
    assert fetch is not None
    assert (fetch[1].ease_factor, fetch[1].self_ease_factor) == (15, 18)


# -- overlapping Scripts (Legends of Hermes pp. 50-51) -----------------------------


def test_an_overlapping_script_may_replace_a_component_at_15():
    assert mysteries.VARY_EASE[mysteries.REPLACE] == 15
    assert mysteries.VARY_LABELS[mysteries.REPLACE] == "Replace a component (15)"


# -- experimental Scripts (TMRE p. 18) --------------------------------------------


def test_the_validity_roll_s_ease_factor():
    assert mysteries.validity_ease(6, on_self=True) == 15
    assert mysteries.validity_ease(6, on_self=False) == 21


@pytest.mark.parametrize(
    ("roll", "side", "no_virtue", "risk_counts", "words"),
    [
        (3, 1, False, True, "no extraordinary effects"),
        (5, 2, False, True, "Personality Trait"),
        (5, 7, False, True, "extra Ordeal Flaw"),
        (6, 9, False, True, "a second Minor Virtue"),
        (6, 10, True, True, "fatal flaw"),
        (7, 1, False, False, "no benefit"),
        (8, 1, True, True, "complete failure"),
        (10, 1, False, True, "Discovery"),
        (11, 1, False, True, "a different Virtue"),
    ],
)
def test_the_chart_read_for_a_rite(
    monkeypatch, roll, side, no_virtue, risk_counts, words
):
    monkeypatch.setattr(dice, "simple_die", lambda _rng: side)
    rite = mysteries.ExperimentalRite()
    mysteries._read_rite(rite, roll, random.Random(0), 0)
    assert (rite.no_virtue, rite.risk_counts) == (no_virtue, risk_counts)
    assert words in rite.notes[0]


def test_an_experimental_script_is_rolled_when_played():
    saga = _saga()
    plan = _plan(teacher_id="m", experimental_script=True, risk=1, **_minor_ordeal())
    assert _work(saga, plan).notes == [
        "An experimental Script's dice are rolled when the season is played."
    ]


def test_an_experimental_script_adds_its_risk_and_sympathy_or_fails():
    saga = _saga()
    mira = saga.character("m")
    assert mira is not None
    mira.abilities = [Ability("Mercere Lore", xp=ability_xp(9))]
    plan = _plan(
        teacher_id="m",
        experimental_script=True,
        risk=2,
        script_sympathy=1,
        other_modifier=4,
        **_minor_ordeal(),
    )
    rolled = [_work(saga, plan, random.Random(seed)) for seed in range(40)]
    worked = [w for w in rolled if w.initiated]
    failed = [w for w in rolled if not w.initiated]
    assert worked and failed
    # Mira: Presence 2 + Lore 9 + Script 4 + sympathy 1 + risk 2 = 18,
    # against 18 (she lacks the Virtue).
    assert any("Initiation Total 18" in w.notes[-1] for w in worked)
    # A failed rite, like a fatal flaw, still costs its Ordeal.
    for w in failed:
        if "the rite failed" in w.notes[-1]:
            assert [vf.vf_id for vf in w.add_vfs] == ["vf_arthritis"]
            assert w.ordeal == "Minor"
    assert all(
        "against 19" in n
        for w in rolled
        for n in w.notes
        if n.startswith("The rite's validity")
    )


def test_an_experimental_script_isn_t_also_varied_nor_over_3_risk():
    saga = _saga()
    plan = _plan(
        teacher_id="m",
        experimental_script=True,
        script_variation="add",
        **_minor_ordeal(),
    )
    assert _problems(saga, plan) == [
        "An experimental Script isn't also varied: choose one or the other."
    ]
    plan.script_variation, plan.risk = "", 4
    assert _problems(saga, plan) == ["An experimental Script's risk is 0 to +3."]


# -- the season form ---------------------------------------------------------------


def test_the_season_form_saves_the_script_choices():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    values = {
        "activity": "undergo_initiation",
        "mystery_virtue": VirtueFlawInstance("vf_flight"),
        "hedge_script": FLIGHT,
        "knows_power": True,
        "experimental_script": True,
        "script_risk": 2,
        "script_sympathy": 1,
    }
    plan = sf.season_plan_from(saga, wulf, values)
    assert (plan.hedge_script, plan.knows_power) == (FLIGHT, True)
    assert (plan.experimental_script, plan.risk, plan.script_sympathy) == (True, 2, 1)
    plan = sf.season_plan_from(saga, wulf, values | {"experimental_script": False})
    assert (plan.risk, plan.script_sympathy) == (0, 0)
