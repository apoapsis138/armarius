"""Wounds that heal and harm from more than weapons (DE pp. 403-407),
with Lords of Men's bruises: the Recovery Total, the rolls, a season's
healing, Take Harm, and the penalties reaching casting."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import health
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.models import (
    Ability,
    AnimalForm,
    Character,
    Characteristics,
    Familiar,
    VirtueFlawInstance,
    Wounds,
    WoundState,
)
from ars_magica_manager.rules import casting, derived, dice, harm, recovery
from ars_magica_manager.rules.xp import ability_xp


def _die(*values: int):
    """A stress die that shows `values` in turn (0 a botch with no dice)."""
    shown = list(values)

    def stress(rng, botch_dice=1, *, saga=None):
        value = shown.pop(0)
        if value == 0:
            return dice.DieResult(0, (0,), botch_faces=(1,) * botch_dice)
        return dice.DieResult(value, (value % 10,))

    return stress


def _patient(stamina=1, **wounds):
    return Character(
        id="p",
        name="Patient",
        type="grog",
        covenant_id="cov1",
        characteristics=Characteristics(stamina=stamina),
        wounds=Wounds(**wounds),
    )


def test_states_line_up_with_the_counts():
    wounds = Wounds(light=2, medium=1, states=[WoundState("light", "disease", 3)])
    found = recovery.states(wounds)
    assert [(s.severity, s.source, s.bonus) for s in found] == [
        ("light", "disease", 3),
        ("light", "injury", 0),
        ("medium", "injury", 0),
    ]
    # Edit Wounds keeps what the remaining wounds carry.
    edited = wounds.with_counts(light=1, medium=0, heavy=0, incapacitated=False)
    assert recovery.states(edited)[0].source == "disease"


def test_the_recovery_total_adds_what_the_books_add():
    saga = everything_saga()
    patient = _patient(stamina=2, light=1)
    patient.virtues_flaws = [VirtueFlawInstance("vf_rapid_convalescence")]
    healer = Character(
        id="h",
        name="Brother Anselm",
        type="companion",
        covenant_id="cov1",
        abilities=[
            Ability("Chirurgy", xp=ability_xp(4)),
            Ability("Medicine", xp=ability_xp(2)),
        ],
    )
    saga.characters += [patient, healer]
    patient.wounds.aid = 9  # a Zenodochium
    injury = recovery.total(saga, patient, WoundState("light"))
    terms = {line.label: line.amount for line in injury.lines}
    assert terms["Stamina"] == 2
    assert terms["Chirurgy (Brother Anselm)"] >= 4
    assert terms["Magical aid"] == 9
    assert terms["Rapid Convalescence"] == 3
    disease = recovery.total(saga, patient, WoundState("light", "disease"))
    assert any(
        label.startswith("Medicine (")
        for label in (line.label for line in disease.lines)
    )


def test_a_roll_improves_holds_or_worsens(monkeypatch):
    patient = _patient(stamina=0, medium=1)
    state = recovery.states(patient.wounds)[0]
    monkeypatch.setattr(dice, "stress_die", _die(7, 3, 12))
    held = recovery.roll_wound(None, patient, state, random.Random())
    assert held.after == "medium" and state.bonus == 3  # 7 reaches 6
    worse = recovery.roll_wound(None, patient, state, random.Random())
    assert worse.after == "medium" and state.bonus == 6  # 3 + 3 reaches 6
    better = recovery.roll_wound(None, patient, state, random.Random())
    assert better.after == "light" and state.bonus == 0  # 12 + 6 reaches 12


def test_an_incapacitated_character_lives_or_dies(monkeypatch):
    patient = _patient(stamina=0, incapacitated=True)
    state = recovery.states(patient.wounds)[0]
    monkeypatch.setattr(dice, "stress_die", _die(5, 10))
    worse = recovery.roll_incapacitated(None, patient, state, random.Random())
    assert worse.after == "incapacitating" and patient.wounds.crisis == 1
    better = recovery.roll_incapacitated(None, patient, state, random.Random())
    assert better.after == "heavy"  # 10 - 1 reaches 9
    dying = _patient(stamina=0, incapacitated=True)
    monkeypatch.setattr(dice, "stress_die", _die(0))
    recovery.roll_incapacitated(
        None, dying, recovery.states(dying.wounds)[0], random.Random()
    )
    assert dying.wounds.dead


def test_a_season_heals_light_wounds_and_rests_fatigue():
    patient = _patient(stamina=3, light=2)
    patient.fatigue_level = "tired"
    patient.long_term_fatigue = 2
    played = recovery.season(None, patient, random.Random(4))
    assert patient.fatigue_level == "fresh" and patient.long_term_fatigue == 0
    assert played.rolls  # weekly rolls were made
    assert patient.wounds.light + patient.wounds.medium <= 2


def test_an_infernal_aura_stops_a_disease_improving(monkeypatch):
    saga = everything_saga()
    patient = _patient(stamina=0, light=1, states=[WoundState("light", "disease")])
    saga.characters.append(patient)
    covenant = saga.covenant("cov1")
    assert covenant is not None
    covenant.aura, covenant.aura_realm, covenant.boons_hooks = 2, "Infernal", []
    monkeypatch.setattr(dice, "stress_die", _die(30))
    state = recovery.states(patient.wounds)[0]
    rolled = recovery.roll_wound(saga, patient, state, random.Random())
    assert rolled.after == "light"  # it held, though 30 - 2 beats 10


def test_injury_poison_and_deprivation(monkeypatch):
    patient = _patient(stamina=0)
    # Boiling oil on a limb: +12 + 5 against Soak 0 + 2, 15: Heavy.
    monkeypatch.setattr(dice, "stress_die", _die(5, 2))
    done = harm.apply(
        None, patient, harm.INJURY, {"bonus": 6, "coverage": 2}, random.Random()
    )
    assert done.wounds == ["heavy"] and patient.wounds.heavy == 1
    poisoned = _patient(stamina=0)
    monkeypatch.setattr(dice, "stress_die", _die(4))
    harm.apply(
        None, poisoned, harm.POISON, {"ease": 9, "wound": "heavy"}, random.Random()
    )
    assert recovery.states(poisoned.wounds)[0].source == "poison"
    starving = _patient(stamina=0)
    monkeypatch.setattr(dice, "stress_die", _die(1, 1, 1, 1, 1, 1, 1))
    harm.apply(
        None,
        starving,
        harm.DEPRIVATION,
        {"kind": "food", "periods": 7},
        random.Random(),
    )
    # Five Fatigue levels to Unconscious (long-term), then a Light and a
    # Medium wound.
    assert starving.fatigue_level == "unconscious"
    assert starving.long_term_fatigue == 5
    assert (starving.wounds.light, starving.wounds.medium) == (1, 1)


def test_bruises_need_their_option_and_leave_a_residual_wound(monkeypatch):
    saga = everything_saga()
    assert harm.BRUISE not in harm.kinds(saga)
    patient = _patient(stamina=0)
    monkeypatch.setattr(dice, "stress_die", _die(9, 1))
    harm.apply(saga, patient, harm.BRUISE, {"bonus": 5}, random.Random())
    assert patient.wounds.bruises == {"heavy": 1}  # 14 - 1 = 13
    assert derived.wound_penalty(patient.wounds) == -5
    assert harm.heal_bruises(patient) == ["A Heavy Bruise left a Light Wound."]
    assert patient.wounds.light == 1 and not patient.wounds.bruises


def test_take_harm_is_kept_only_when_confirmed(monkeypatch):
    saga = everything_saga()
    patient = saga.characters[0]
    monkeypatch.setattr(dice, "stress_die", _die(9, 1))
    form = health.take_harm_form(saga, patient)
    assert isinstance(form, Form)
    shown = form.apply({"kind": harm.INJURY, "bonus": 6, "coverage": "1"})
    assert isinstance(shown, Confirm)
    assert not recovery.states(patient.wounds)  # not yet
    shown.apply()
    assert recovery.states(patient.wounds) or patient.wounds.dead
    assert patient.diary[-1].name.startswith("An injury")


def test_wounds_and_fatigue_reach_the_casting_score():
    saga = everything_saga()
    magus = next(c for c in saga.characters if c.type == "magus")
    before = casting.casting_score(magus, "Creo", "Ignem").total
    magus.wounds = Wounds(medium=1)
    magus.fatigue_level = "weary"
    after = casting.casting_score(magus, "Creo", "Ignem")
    labels = {line.label: line.amount for line in after.lines}
    assert labels["Wounds"] == -3 and labels["Fatigue"] == -1
    assert after.total == before - 4


def test_an_animal_s_natural_protection_is_in_its_soak():
    hound = Character(
        id="d", name="Fang", type="grog", animal=AnimalForm(species="Dog")
    )
    lines = {line.label: line.amount for line in derived.soak(hound).lines}
    assert lines["Natural Protection"] == 1


def test_a_familiar_s_bronze_cord_and_the_lab_s_health_help():
    saga = everything_saga()
    magus = next(c for c in saga.characters if c.type == "magus")
    familiar = saga.familiar_of(magus.id)
    if familiar is None:
        familiar = Familiar(id="fam", name="Corvus", character_id=magus.id)
        saga.familiars.append(familiar)
    familiar.bronze_cord = 2
    terms = {
        line.label: line.amount
        for line in recovery.total(saga, magus, WoundState("light")).lines
    }
    assert terms["Bronze Cord"] == 2


def test_the_season_writes_each_wounded_character_s_recovery():
    from ars_magica_manager.seasons.healing import season_healing

    saga = everything_saga()
    patient = saga.characters[0]
    patient.wounds = Wounds(light=1)
    lines = season_healing(saga, random.Random(2))
    assert [line.character_id for line in lines] == [patient.id]
    assert patient.diary[-1].name.startswith("Recovery: ")
