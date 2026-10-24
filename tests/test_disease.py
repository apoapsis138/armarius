"""Art & Academe's diseases as a saga option (A&A pp. 45-58)."""

import random

from ars_magica_manager import aging_due, health
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import advance as advance_forms
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Covenant,
    Disease,
    Saga,
    Wounds,
)
from ars_magica_manager.rules import derived, disease, harm, recovery
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons.healing import season_healing


def _saga(*characters: Character) -> Saga:
    saga = Saga(
        id="s",
        name="S",
        characters=list(characters),
        covenants=[Covenant(id="cov", saga_id="s", name="C")],
    )
    saga.books_in_play = ["A&A"]
    saga.rule_options = {disease.OPTION: True}
    return saga


def _person(cid: str = "p", stamina: int = 0, **kw) -> Character:
    return Character(
        id=cid,
        name=cid.title(),
        type="companion",
        covenant_id="cov",
        characteristics=Characteristics(stamina=stamina, intelligence=2),
        **kw,
    )


def test_severity_from_its_parts_and_its_stage():
    # Erysipelas: Minor 6, Month +1, Stable 6 +0, Improve 10 -1 = 6 (p. 47).
    assert disease.severity_of("Minor", "month", 6, 10) == 6
    garotillo = disease.from_def(disease.CATALOG_BY_NAME["Garotillo"])
    garotillo.level = "Major"
    assert disease.severity(garotillo) == 12  # Serious 9, a stage worse
    assert disease.penalty(garotillo) == -5


def test_disease_penalties_add_to_the_wound_penalty_but_not_to_its_own_rolls():
    wounds = Wounds(light=1, diseases=[Disease("Coryza", "Minor")])
    assert derived.wound_penalty(wounds) == -2
    assert derived.wound_penalty(wounds, diseases=False) == -1


def test_the_option_makes_take_harm_catch_a_disease_record():
    patient = _person(stamina=-5)
    saga = _saga(patient)
    done = harm.apply(
        saga, patient, harm.DISEASE, {"aa_disease": "Bloody Flux"}, random.Random(1)
    )
    assert "Disease Avoidance" in done.lines[0]
    assert [d.name for d in patient.wounds.diseases] == ["Bloody Flux"]
    assert patient.wounds.light == 0  # not a wound


def test_medicine_helps_only_when_the_prognosis_beats_the_severity():
    doctor = _person("d")
    doctor.abilities.append(Ability("Medicine", xp=ability_xp(4)))
    patient = _person()
    saga = _saga(doctor, patient)
    flux = disease.from_def(disease.CATALOG_BY_NAME["Bloody Flux"])  # Severity 9
    # Int 2 + Medicine 4 + diet 0 = 6: not over 9.
    assert disease.prognosis(saga, patient, 0).total == 6
    assert "Medicine (D)" not in [
        line.label for line in disease.recovery_total(saga, patient, flux, 0).lines
    ]
    doctor.abilities[0] = Ability("Medicine", xp=ability_xp(8))
    assert "Medicine (D)" in [
        line.label for line in disease.recovery_total(saga, patient, flux, 0).lines
    ]


def test_recovery_modifiers_and_their_botch_dice():
    patient = _person()
    patient.wounds.conditions = ["noble_diet", "active", "no_herbs"]
    saga = _saga(patient)
    amounts = [line.amount for line in disease.condition_lines(saga, patient)]
    assert amounts == [1, -1, -3]
    assert disease.botch_dice(patient) == 4


def test_a_crisis_ends_in_a_stage_or_a_death():
    patient = _person(stamina=3)
    saga = _saga(patient)
    apoplexy = disease.from_def(disease.CATALOG_BY_NAME["Apoplexy"])
    patient.wounds.diseases = [apoplexy]
    lines = disease.season(saga, patient, 0, random.Random(3))
    assert lines
    assert (
        patient.wounds.dead or apoplexy.level != disease.CRITICAL or "still" in lines[0]
    )


def test_a_season_rolls_a_disease_at_its_interval_and_cures_it():
    patient = _person(stamina=5)
    patient.wounds.diseases = [disease.from_def(disease.CATALOG_BY_NAME["Coryza"])]
    saga = _saga(patient)
    season_healing(saga, random.Random(2))
    assert not patient.wounds.diseases  # weekly rolls at Stamina 5 cure a cold
    assert patient.diary[-1].name == "Recovery: healed"


def test_edit_wounds_sets_conditions_and_cures_a_disease():
    wounds = Wounds(diseases=[Disease("Coryza")])
    names = [f.key for f in character_forms.wounds_fields(wounds, academe=True)]
    assert "condition_noble_diet" in names and "cured_0" in names
    result = {
        "soak": 0,
        "light": 0,
        "medium": 0,
        "heavy": 0,
        "incapacitated": False,
        "dead": False,
        "condition_noble_diet": True,
        "cured_0": True,
    }
    after = character_forms.apply_wounds(wounds, result)
    assert (after.conditions, after.diseases) == (["noble_diet"], [])


def test_the_disease_penalty_slows_wound_healing():
    patient = _person()
    patient.wounds = Wounds(light=1, diseases=[Disease("Coryza")])
    state = recovery.states(patient.wounds)[0]
    labels = [
        line.label for line in recovery.total(_saga(patient), patient, state).lines
    ]
    assert "Disease Penalty" in labels


def test_take_harm_offers_the_books_diseases_with_the_option():
    keys = [f.key for f in health.harm_fields(_saga())]
    assert "aa_disease" in keys


def test_avoidance_meets_or_beats_the_stable_ease_factor():
    # DE p. 7's equals-or-exceeds, over A&A p. 46's "exceed".
    flux = disease.from_def(disease.CATALOG_BY_NAME["Bloody Flux"])  # Stable 6
    assert disease.avoids(6, flux) and not disease.avoids(5, flux)


def test_a_crisis_survived_leaves_an_aging_point_to_place():
    # A&A p. 47: one Aging Point, the storyguide's choice of Characteristic.
    patient = _person(stamina=3)
    saga = _saga(patient)
    patient.aging.aging_due = ["Survived Apoplexy's Crisis"]
    form = advance_forms.play_season(saga)
    assert isinstance(form, Form) and form.title == aging_due.TITLE
    lines = aging_due.place(saga, [patient], {"point_p_0": "stamina"})
    assert patient.aging.aging_points["stamina"] == 1
    assert patient.aging.aging_due == [] and "Stamina" in lines[0]
