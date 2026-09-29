"""Activity Lab Totals (STORY-816)."""

import pytest

from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    LabSpecialtyEntry,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import lab
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _setup(*vf_ids: str):
    magus = Character(
        id="m",
        name="M",
        type="magus",
        characteristics=Characteristics(intelligence=3),
        arts={"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(6))},
        abilities=[Ability("Magic Theory", xp=ability_xp(5))],
        virtues_flaws=[VirtueFlawInstance(vf_id=v) for v in vf_ids],
    )
    laboratory = Laboratory(id="l", covenant_id="c", name="Lab")
    saga = Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="c", saga_id="s", name="C", aura=3)],
        characters=[magus],
        laboratories=[laboratory],
    )
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
