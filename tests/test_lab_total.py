"""The Lab Total (STORY-801)."""

import pytest

from ars_magica_manager import lab_planning
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Familiar,
    Laboratory,
    LabSpecialtyEntry,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import lab
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga(realm: str = "Magic", aura: int = 3):
    magus = Character(
        id="m",
        name="Magus",
        type="magus",
        characteristics=Characteristics(intelligence=3),
        arts={"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(6))},
        abilities=[Ability("Magic Theory", xp=ability_xp(5))],
    )
    laboratory = Laboratory(id="l", covenant_id="c", name="Lab", owner_id="m")
    covenant = Covenant(id="c", saga_id="s", name="C", aura=aura, aura_realm=realm)
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus],
        laboratories=[laboratory],
    )
    return saga, magus, laboratory


def _terms(total) -> dict[str, float]:
    return {line.label: line.amount for line in total.lines if line.amount is not None}


def test_the_generic_lab_total():
    saga, magus, laboratory = _saga()
    total = lab.lab_total(saga, magus, "Creo", "Ignem", laboratory)
    # 10 + 6 + Int 3 + Magic Theory 5 + aura 3
    assert total.total == 27
    assert _terms(total) == {
        "Creo": 10,
        "Ignem": 6,
        "Intelligence": 3,
        "Magic Theory": 5,
        "Aura (Magic 3)": 3,
    }


def test_a_divine_aura_hinders_hermetic_lab_work():
    saga, magus, laboratory = _saga(realm="Divine", aura=2)
    assert lab.lab_total(saga, magus, "Creo", "Ignem", laboratory).total == 24 - 6


def test_general_quality_and_the_specializations_that_apply():
    saga, magus, laboratory = _saga()
    laboratory.characteristics.general_quality = 2
    laboratory.specialties = [
        LabSpecialtyEntry("Ignem", 2, "notes"),
        LabSpecialtyEntry("Vim", 3, "notes"),
        LabSpecialtyEntry("Spells", 1, "notes"),
    ]
    plain = lab.lab_total(saga, magus, "Creo", "Ignem", laboratory)
    assert plain.total == 27 + 2 + 2  # Vim and Spells don't apply
    inventing = lab.lab_total(
        saga, magus, "Creo", "Ignem", laboratory, activity="invent_spells"
    )
    assert inventing.total == 27 + 2 + 2 + 1


def test_puissant_and_deficient_arts():
    saga, magus, laboratory = _saga()
    magus.virtues_flaws = [
        VirtueFlawInstance(vf_id="vf_puissant_art", params={"art": "creo"}),
        VirtueFlawInstance(vf_id="vf_deficient_form", params={"form": "ignem"}),
    ]
    # (13 + 6 + 3 + 5 + 3) halved, rounded down; Creo Vim isn't halved.
    assert lab.lab_total(saga, magus, "Creo", "Ignem", laboratory).total == 15
    assert lab.lab_total(saga, magus, "Creo", "Vim", laboratory).total == 24


def test_assistants_and_a_familiar_add_intelligence_and_magic_theory():
    saga, magus, laboratory = _saga()
    helper = Character(
        id="a",
        name="Apprentice",
        type="magus",
        characteristics=Characteristics(intelligence=1),
        abilities=[Ability("Magic Theory", xp=ability_xp(2))],
    )
    familiar = Familiar(
        id="f",
        name="Corax",
        character_id="m",
        characteristics=Characteristics(intelligence=-1),
        abilities=[Ability("Magic Theory", xp=ability_xp(1))],
    )
    total = lab.lab_total(
        saga, magus, "Creo", "Ignem", laboratory, assistants=[helper], familiar=familiar
    )
    assert total.total == 27 + 3 + 0
    assert not total.notes
    too_many = lab.lab_total(
        saga, magus, "Creo", "Ignem", laboratory, assistants=[helper, helper]
    )
    assert "Leadership allows 1" in too_many.notes[0]


@pytest.mark.parametrize(
    ("days", "penalty"), [(0, 0), (10, 0), (11, -12), (20, -30), (21, None)]
)
def test_distractions(days, penalty):
    assert lab.distraction_penalty(days) == penalty


def test_the_planning_text_shows_the_grid():
    saga, magus, laboratory = _saga()
    text = lab_planning.lab_totals_text(saga, laboratory, magus)
    assert "Lab Totals for Magus" in text
    creo = next(line for line in text.splitlines() if line.startswith("Creo"))
    assert creo.split()[1 + 5] == "27"  # the Ignem column
    assert "no Lab Totals" in lab_planning.lab_totals_text(
        saga, laboratory, Character(id="g", name="Grog", type="grog")
    )
    assert "give the laboratory an owner" in lab_planning.lab_totals_text(
        saga, laboratory, None
    )
