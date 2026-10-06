"""The Lab Total."""

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
    text = lab_planning.lab_totals_grid_text(saga, laboratory, magus)
    assert "Magus working here" in text
    creo = next(line for line in text.splitlines() if line.startswith("[b]Creo"))
    assert creo.split()[2 + 5] == "27"  # the Ignem column, after "[b]Creo [/]"
    base = lab_planning.base_lab_total_text(saga, laboratory, magus)
    assert base.splitlines()[0].startswith("Int ")
    activities = lab_planning.activity_totals_text(saga, laboratory, magus)
    assert "[b]Experimenting[/]" in activities
    assert "no Lab Totals" in lab_planning.lab_totals_grid_text(
        saga, laboratory, Character(id="g", name="Grog", type="grog")
    )
    assert "give the laboratory an owner" in lab_planning.lab_totals_grid_text(
        saga, laboratory, None
    )


def test_signed_amounts_are_coloured_by_theme():
    # + in $text-success, - in $text-error, zero plain; '+' kept.
    assert lab_planning.signed(3) == "[$text-success]+3[/]"
    assert lab_planning.signed(-2) == "[$text-error]-2[/]"
    assert lab_planning.signed(0) == "+0"


# -- Activity Lab Totals --


def _setup(*vf_ids: str):
    """_saga()'s magus, holding the Virtues/Flaws `vf_ids`."""
    saga, magus, laboratory = _saga()
    magus.virtues_flaws = [VirtueFlawInstance(vf_id=v) for v in vf_ids]
    return saga, magus, laboratory


def _total(saga, magus, laboratory, **kw) -> float:
    return lab.lab_total(saga, magus, "Creo", "Ignem", laboratory, **kw).total


BASE = 27  # 10 + 6 + Int 3 + Magic Theory 5 + aura 3


def test_activity_bonuses_apply_only_to_their_activity():
    saga, magus, laboratory = _setup("vf_inventive_genius")
    assert _total(saga, magus, laboratory) == BASE
    assert _total(saga, magus, laboratory, activity="invent_spells") == BASE + 3
    assert _total(saga, magus, laboratory, activity="learn_from_lab_text") == BASE


def test_experimenting_replaces_inventive_genius_rather_than_adding():
    saga, magus, laboratory = _setup("vf_inventive_genius")
    laboratory.specialties = [LabSpecialtyEntry("Experimentation", 2, "x")]
    total = _total(
        saga, magus, laboratory, activity="invent_spells", experimenting=True
    )
    assert total == BASE + 6 + 2


@pytest.mark.parametrize(
    ("vf_id", "activity", "total"),
    [
        ("vf_adept_laboratory_student", "learn_from_lab_text", BASE + 6),
        ("vf_weak_scholar", "learn_from_lab_text", BASE - 6),
        ("vf_creative_block", "invent_spells", BASE - 3),
        ("vf_creative_block", "learn_from_lab_text", BASE),
        ("vf_weak_enchanter", "enchant_items", BASE // 2),
        ("vf_weak_enchanter", "invent_spells", BASE),
    ],
)
def test_lab_virtues_and_flaws(vf_id, activity, total):
    saga, magus, laboratory = _setup(vf_id)
    assert _total(saga, magus, laboratory, activity=activity) == total


def test_activity_specializations():
    saga, magus, laboratory = _setup()
    laboratory.specialties = [
        LabSpecialtyEntry("Texts", 2, "x"),
        LabSpecialtyEntry("Familiar", 1, "x"),
    ]
    assert _total(saga, magus, laboratory, activity="learn_from_lab_text") == BASE + 2
    assert _total(saga, magus, laboratory, activity="bind_familiar") == BASE + 1


def test_similar_spell_and_shape_and_material():
    saga, magus, laboratory = _setup()
    assert (
        _total(
            saga, magus, laboratory, activity="invent_spells", similar_spell_level=15
        )
        == BASE + 3
    )
    # Shape and material capped at Magic Theory (5).
    assert (
        _total(saga, magus, laboratory, activity="enchant_items", shape_material=9)
        == BASE + 5
    )
    assert _total(saga, magus, laboratory, shape_material=9) == BASE  # not enchanting


@pytest.mark.parametrize(
    ("lab_total", "level", "points", "seasons"),
    [(25, 20, 5, 4), (25, 12, 13, 1), (25, 13, 12, 2), (20, 20, 0, None)],
)
def test_inventing_takes_seasons(lab_total, level, points, seasons):
    assert lab.points_per_season(lab_total, level) == points
    assert lab.seasons_to_invent(lab_total, level) == seasons


def test_the_other_activity_rules():
    assert lab.lab_text_usable(20, 20)
    assert lab.longevity_modifier(23) == 5
    assert lab.longevity_modifier(23, mundane=True) == 3
    assert lab.vis_extracted(23) == 3
    assert lab.vis_extracted(3) == 1
    _, magus, _ = _setup()
    assert lab.vis_limit(magus) == 10
    assert lab.lowest_total([22, 19, 25]) == 19
