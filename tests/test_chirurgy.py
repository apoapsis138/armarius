"""Art & Academe's chirurgy under its medicine option (pp. 59-62): first aid
and palliative care in the Wound Recovery Total, the First Aid roll,
surgery on a disease and surgical intervention, through Recovery Roll."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import health
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.models import (
    Ability,
    Background,
    Character,
    Characteristics,
    Disease,
    Wounds,
    WoundState,
)
from ars_magica_manager.rules import chirurgy, dice, disease, recovery
from ars_magica_manager.rules.xp import ability_xp


def _die(*values: int):
    """A stress die that shows `values` in turn (0 a botch)."""
    shown = list(values)

    def stress(rng, botch_dice=1, *, saga=None):
        value = shown.pop(0)
        if value == 0:
            return dice.DieResult(0, (0,), botch_faces=(0,) * max(botch_dice, 1))
        return dice.DieResult(value, (value % 10,))

    return stress


def _saga(on: bool = True):
    saga = everything_saga()
    saga.rule_options = {disease.OPTION: on}
    return saga


def _person(id: str, name: str, chirurgy_score: int = 0, specialty=None, **kw):
    abilities = (
        [Ability("Chirurgy", xp=ability_xp(chirurgy_score), specialty=specialty)]
        if chirurgy_score
        else []
    )
    return Character(
        id=id,
        name=name,
        type="companion",
        covenant_id="cov1",
        abilities=abilities,
        **kw,
    )


def _labels(total):
    return {line.label: line.amount for line in total.lines}


def test_half_rounds_up():
    assert [chirurgy.half(n) for n in (0, 1, 2, 3, 5)] == [0, 1, 1, 2, 3]


def test_without_the_option_the_medic_gives_his_whole_chirurgy():
    saga = _saga(on=False)
    patient = _person("p", "Halfgrim", wounds=Wounds(light=1))
    saga.characters += [patient, _person("m", "Medicus", 5)]
    found = _labels(recovery.total(saga, patient, WoundState("light")))
    assert found["Chirurgy (Medicus)"] == 5


def test_palliative_care_gives_half_and_first_aid_the_other_half_capped():
    saga = _saga()
    patient = _person("p", "Halfgrim", wounds=Wounds(light=1))
    saga.characters += [patient, _person("m", "Medicus", 5)]
    # Palliative care alone: half of 5, rounded up.
    found = _labels(recovery.total(saga, patient, WoundState("light")))
    assert found == {"Stamina": 0, "Palliative care (Medicus)": 3}
    # A grog's first aid (Chirurgy 2): +1 more, the book's example.
    found = _labels(recovery.total(saga, patient, WoundState("light", first_aid=2)))
    assert found["First aid"] == 1 and found["Palliative care (Medicus)"] == 3
    # The medicus's own first aid: +3 + 3 is capped at his Chirurgy, 5.
    found = _labels(recovery.total(saga, patient, WoundState("light", first_aid=5)))
    assert found["First aid"] + found["Palliative care (Medicus)"] == 5
    # A disease's wound still takes the physician's Medicine.
    assert "First aid" not in _labels(
        recovery.total(saga, patient, WoundState("light", "disease", first_aid=5))
    )


def test_a_specialty_counts_for_its_use():
    nurse = _person("n", "Nurse", 3, specialty="palliative care")
    assert chirurgy.chirurgy(nurse, chirurgy.PALLIATIVE) == 4
    assert chirurgy.chirurgy(nurse, chirurgy.SURGERY) == 3


def test_first_aid_through_recovery_roll(monkeypatch):
    saga = _saga()
    patient = _person("p", "Halfgrim", wounds=Wounds(light=1, medium=1))
    grog = _person("g", "Grog", 2, characteristics=Characteristics(dexterity=1))
    saga.characters += [patient, grog]
    monkeypatch.setattr(dice, "stress_die", _die(9))
    form = health.recovery_form(saga, patient)
    assert isinstance(form, Form)
    keys = [f.key for f in form.fields()]
    assert "chirurgeon" in keys and "intervene" in keys
    shown = form.apply({"which": "first aid", "chirurgeon": "g", "aid": 0})
    assert isinstance(shown, Confirm)
    # Dexterity 1 + Chirurgy 2 + 9 = 12 against the Medium's 12.
    assert "12 against 12, a success" in shown.question
    assert not any(s.first_aid for s in patient.wounds.states)  # not yet
    shown.apply()
    assert all(s.first_aid == 2 for s in recovery.states(patient.wounds))
    assert patient.diary[-1].name == "First aid"


def test_a_botched_first_aid_gives_no_bonus_and_an_immediate_roll(monkeypatch):
    saga = _saga()
    patient = _person("p", "Halfgrim", wounds=Wounds(light=1))
    saga.characters += [patient, _person("g", "Grog", 2)]
    monkeypatch.setattr(dice, "stress_die", _die(0, 0, 1))
    found = recovery.states(patient.wounds)
    rolled, _ = chirurgy.first_aid(
        saga, patient, saga.character("g"), 10, found, random.Random()
    )
    assert rolled is not None and rolled.botched
    assert not any(s.first_aid for s in found)
    shown = health.recovery_form(saga, patient).apply(
        {"which": "first aid", "chirurgeon": "g", "aid": 0}
    )
    assert "Light wound" in shown.question  # the Recovery roll it provoked


def test_surgery_on_a_disease(monkeypatch):
    saga = _saga()
    sick = Disease(
        "Anal Fistula",
        level="Serious",
        first_level="Minor",
        severity=5,
        stable=4,
        improve=10,
        interval="month",
    )
    patient = _person("p", "Patient", wounds=Wounds(diseases=[sick]))
    surgeon = _person("s", "Surgeon", 4, characteristics=Characteristics(dexterity=2))
    saga.characters += [patient, surgeon]
    form = health.recovery_form(saga, patient)
    values = {
        "which": "surgery",
        "chirurgeon": "s",
        "disease": "Anal Fistula",
        "procedure": "Phlebotomy",
        "aid": 0,
    }
    # Severity 8 now: too much for phlebotomy alone.
    assert "Severity 5 or less" in (form.validate(values) or "")
    values["procedure"] = "Removing a gall stone or fistula"
    assert form.validate(values) is None
    monkeypatch.setattr(dice, "stress_die", _die(3))
    shown = form.apply(values)
    shown.apply()
    record = patient.wounds.diseases[0]
    assert record.level == "Minor" and record.surgery == 3
    assert patient.wounds.medium == 1  # the surgery's own wound
    lines = _labels(disease.recovery_total(saga, patient, record, 0))
    assert lines["Surgery"] == 3
    monkeypatch.setattr(dice, "stress_die", _die(5))
    disease.roll(saga, patient, record, 0, random.Random())
    assert record.surgery == 0  # the next roll only


def test_a_failed_surgery_still_wounds_and_a_botch_wounds_worse(monkeypatch):
    saga = _saga()
    patient = _person(
        "p", "Patient", wounds=Wounds(diseases=[Disease("Quinsy", severity=6)])
    )
    saga.characters += [patient, _person("s", "Surgeon", 1)]
    record = patient.wounds.diseases[0]
    monkeypatch.setattr(dice, "stress_die", _die(2))
    done = chirurgy.surgery(
        saga,
        patient,
        saga.character("s"),
        record,
        "Removing a rotten tooth",
        random.Random(),
    )
    assert not done.rolled.success and done.wound == "light"
    monkeypatch.setattr(dice, "stress_die", _die(0))
    done = chirurgy.surgery(
        saga, patient, saga.character("s"), record, "Phlebotomy", random.Random()
    )
    assert done.rolled.botched and done.wound == "light"  # a Fatigue level, worse


def test_surgical_intervention_holds_a_failing_wound(monkeypatch):
    saga = _saga()
    patient = _person(
        "p", "Halfgrim", wounds=Wounds(medium=1), background=Background(year_born=1190)
    )
    surgeon = _person("s", "Surgeon", 5, characteristics=Characteristics(dexterity=2))
    saga.characters += [patient, surgeon]
    # The Recovery roll fails (Palliative +3, die 1: 4 < 6); the surgery
    # roll is 2 + 5 + 3 = 10 against 9.
    monkeypatch.setattr(dice, "stress_die", _die(1, 3))
    shown = health.recovery_form(saga, patient).apply(
        {"which": "all", "intervene": True, "location": "head", "chirurgeon": "s"}
    )
    assert "the wound holds instead" in shown.question
    assert "Two Aging Points" in shown.question
    shown.apply()
    found = recovery.states(patient.wounds)
    assert [(s.severity, s.bonus) for s in found] == [("medium", 3)]
    assert len(patient.aging.aging_due) == 2
    assert "(suggested: Intelligence)" in patient.aging.aging_due[0]


def test_a_botched_intervention_worsens_two_steps(monkeypatch):
    saga = _saga()
    patient = _person("p", "Halfgrim", wounds=Wounds(heavy=1))
    saga.characters += [patient, _person("s", "Surgeon", 1)]
    monkeypatch.setattr(dice, "stress_die", _die(1, 0))
    lines = recovery.roll_now(
        saga, patient, random.Random(), surgeon=chirurgy.Surgeon(saga.character("s"))
    )
    assert patient.wounds.dead
    assert "botched" in lines[-1] and "Minor Flaw" in lines[-1]


def test_a_light_wound_s_intervention_makes_an_aging_roll(monkeypatch):
    saga = _saga()
    patient = _person(
        "p", "Halfgrim", wounds=Wounds(light=1), background=Background(year_born=1190)
    )
    saga.characters += [patient, _person("s", "Surgeon", 5)]
    # Recovery botches (3 < 4), surgery 5 + 4 = 9, then the aging die.
    monkeypatch.setattr(dice, "stress_die", _die(0, 4, 1))
    shown = health.recovery_form(saga, patient).apply(
        {"which": "all", "intervene": True, "location": "limbs", "chirurgeon": "s"}
    )
    shown.apply()
    assert any(e.name.startswith("Aging (surgery)") for e in patient.diary)
