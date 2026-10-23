"""Virtues and Flaws in working seasons and the year: Labor Points
(Perfect Eye for Commodity, Bigamist, Necessary Realm Aura, Independent
Craftsman), Artes Liberales by subject (Academic Concentration,
Aristotelian Training) and a year's Warping (Raised from the Dead,
Immortality of the Forest, Susceptibility to Warping)."""

import random

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Covenant,
    DiaryEntry,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import debate, lab_virtues, warping
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.xp import ability_xp


def _vf(vf_id: str, **params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, params=params)


def _saga(*virtues: VirtueFlawInstance, realm="Magic", aura=3) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep", aura_realm=realm)
    covenant.aura = aura
    smith = Character(id="c", name="Wulf", type="companion", covenant_id="cov")
    smith.characteristics = Characteristics(dexterity=2, intelligence=1)
    smith.abilities = [
        Ability("Craft: Smith", xp=ability_xp(6)),
        Ability("Artes Liberales", xp=ability_xp(2)),
    ]
    smith.background.year_born = 1200
    smith.virtues_flaws = list(virtues)
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[smith])
    saga.current_season = "Winter"
    return saga


def _labor(saga: Saga, activity="working_season", **kw) -> sw.SupplementWork:
    plan = SeasonPlan(
        "c", 1220, "Spring", activity, [XpAllocation("ability:Craft: Smith")], **kw
    )
    return sw.work(saga, saga.characters[0], plan, None)


def test_perfect_eye_and_bigamist_change_the_business_year():
    saga = _saga(_vf("vf_perfect_eye_for_commodity", commodity="iron"))
    wulf = saga.characters[0]
    wulf.labor_points = 100
    seasons.year_end_business(saga)
    assert wulf.labor_points == 100 - 36 + 9  # 3 x average 3
    assert "Perfect Eye for iron +9" in wulf.diary[-1].details
    wulf.virtues_flaws = [_vf("vf_bigamist")]
    seasons.year_end_business(saga)
    assert wulf.labor_points == 73 - 36 - 18
    wulf.virtues_flaws = [_vf("vf_bigamist", status="lower")]
    seasons.year_end_business(saga)
    assert wulf.labor_points == 19 - 36 - 9


def test_necessary_realm_aura_lowers_its_ability_outside_the_aura():
    flaw = _vf(
        "vf_necessary_realm_aura_for_ability", realm="Dominion", ability="Craft: Smith"
    )
    away = _labor(_saga(flaw))
    assert away.labor_points == (2 + 6 - 3) * 3
    assert "-3 (Necessary Realm Aura)" in away.notes[0]
    home = _labor(_saga(flaw, realm="Divine"))
    assert home.labor_points == (2 + 6) * 3
    workshop = _labor(_saga(flaw), "workshop_production")
    assert workshop.notes[0].startswith("Workshop Total 5 against Craft Level 6")


def test_independent_craftsman_is_a_note_on_the_workshop():
    work = _labor(_saga(_vf("vf_independent_craftsman")), "workshop_production")
    assert any(
        n.startswith("Independent Craftsman: Craft: Smith counts 3") for n in work.notes
    )
    assert not any(
        "Independent" in n for n in _labor(_saga(), "workshop_production").notes
    )


def test_artes_liberales_by_subject_in_a_horoscope_and_a_debate():
    wulf = _saga().characters[0]
    assert lab_virtues.horoscope_score(wulf) == 1 + 2
    wulf.virtues_flaws = [_vf("vf_academic_concentration_subject", subject="Astronomy")]
    assert lab_virtues.horoscope_score(wulf) == 1 + 2 + 3
    assert debate.debater("Wulf", wulf).attacks["Artes Liberales"] == 2 - 1
    wulf.virtues_flaws.append(_vf("vf_aristotelian_training"))
    assert debate.debater("Wulf", wulf).attacks["Artes Liberales"] == 2 - 1 + 1
    wulf.virtues_flaws[0] = _vf("vf_academic_concentration_subject", subject="rhetoric")
    assert debate.debater("Wulf", wulf).attacks["Artes Liberales"] == 2 + 3 + 1


def test_raised_from_the_dead_and_susceptibility_add_yearly_warping():
    saga = _saga(_vf("vf_raised_from_the_dead"))
    seasons.year_end_aging(saga, random.Random(1))
    assert warping.total_points(saga.characters[0]) == 1
    saga.characters[0].virtues_flaws.append(_vf("vf_susceptibility_to_warping"))
    seasons.year_end_aging(saga, random.Random(1))
    assert warping.total_points(saga.characters[0]) == 1 + 2


def test_susceptibility_counts_a_year_that_warped_by_an_event():
    saga = _saga(_vf("vf_susceptibility_to_warping"))
    wulf = saga.characters[0]
    seasons.year_end_aging(saga, random.Random(1))
    assert warping.total_points(wulf) == 0  # nothing warped this year
    wulf.diary.append(
        DiaryEntry(year=saga.current_year, season="Summer", name="Warping +1")
    )
    seasons.year_end_aging(saga, random.Random(1))
    assert warping.total_points(wulf) == 1  # the extra point only


def test_immortality_of_the_forest_warps_instead_of_aging():
    saga = _saga(_vf("vf_immortality_of_the_forest"))
    saga.current_year = 1260  # aged 60: a roll is due
    assert seasons.year_end_aging(saga, random.Random(1)) == []
    wulf = saga.characters[0]
    assert warping.total_points(wulf) == 1
    assert not wulf.aging.aging_points
