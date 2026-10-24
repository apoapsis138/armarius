"""Warping and Wizard's Twilight."""

import random

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Aging,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import warping
from ars_magica_manager.rules.xp import art_xp


class _Dice(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5


def _saga(kind="magus", realm="Magic", aura=3, **aging_kw) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep", aura_realm=realm)
    covenant.aura = aura
    person = Character(id="p", name="Tiberius", type=kind, covenant_id="cov")
    person.characteristics = Characteristics(stamina=1, intelligence=2)
    person.background.year_born = 1180
    person.aging = Aging(**aging_kw)
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[person])
    saga.current_season = "Winter"
    return saga


def test_the_score_advances_like_an_ability():
    assert [warping.score_for(p) for p in (4, 5, 14, 15, 30, 75)] == [0, 1, 1, 2, 3, 5]
    person = _saga().characters[0]
    warping.set_total(person, 18)
    assert (person.aging.warping_score, person.aging.warping_points) == (2, 3)


def test_a_longevity_ritual_warps_a_point_a_year():
    saga = _saga(longevity_modifier=3)
    seasons.year_end_aging(saga, _Dice(0))  # die 0: no apparent aging
    assert warping.total_points(saga.characters[0]) == 1


def test_a_strong_aura_of_another_realm_warps_its_residents():
    saga = _saga(kind="companion", realm="Faerie", aura=8)
    seasons.year_end_aging(saga, _Dice(0))
    assert warping.total_points(saga.characters[0]) == 2
    magus = _saga(kind="magus", realm="Magic", aura=8)
    seasons.year_end_aging(magus, _Dice(0))
    assert warping.total_points(magus.characters[0]) == 0


def test_two_points_at_once_can_bring_on_twilight():
    saga = _saga(warping_score=6)
    # Avoidance: Stamina 1 + die 2 = 3 against 6 + 2 + aura + 5: fails.
    # Twilight adds a simple die (4); comprehension Int 2 + 3 against 6 + 3
    # fails: the base time.
    notes = seasons.gain_warping(saga, saga.characters[0], 2, _Dice(2, 5, 4, 3, 3))
    person = saga.characters[0]
    assert "Twilight: not comprehended" in notes[2]
    assert "lasts a season" in notes[2]
    assert person.aging.twilight_until == "Winter 1220"
    assert warping.total_points(person) == warping.points_for(6) + 2 + 4
    found = rules.problems(person, SeasonPlan("p", 1220, "Winter", rules.OTHER), saga)
    assert found == ["Tiberius is lost in Wizard's Twilight until Winter 1220."]


def test_resisting_twilight():
    saga = _saga()
    notes = seasons.gain_warping(saga, saga.characters[0], 2, _Dice(9, 0))
    assert notes[-1] == "The magus regains control in two minutes."
    assert saga.characters[0].aging.twilight_until == ""


def test_comprehending_twilight_shortens_it():
    # Warping Score 7 (a year), comprehended by two points: two steps
    # shorter, a Moon (DE p. 228).
    saga = _saga(warping_score=7)
    person = saga.characters[0]
    # Avoidance fails; comprehension Int 2 + 9 = 11 against 7 + 2 = 9.
    notes = seasons.gain_warping(saga, person, 2, _Dice(2, 5, 4, 9, 2))
    assert "Twilight: comprehended" in notes[2]
    assert "lasts a Moon" in notes[2]
    assert person.aging.twilight_until == ""


def test_the_vim_form_bonus_helps_avoid_twilight():
    saga = _saga()
    person = saga.characters[0]
    person.arts["vim"] = ArtScore(xp=art_xp(10))  # Form Bonus +2
    # Stamina 1 + Vim 2 + die 6 = 9 against 0 + 2 + aura 3 + 4 = 9.
    notes = seasons.gain_warping(saga, person, 2, _Dice(6, 4))
    assert notes[-1] == "The magus regains control in two minutes."


def test_twilights_effects_are_sized_by_its_points():
    saga = _saga(warping_score=6)
    notes = seasons.gain_warping(saga, saga.characters[0], 3, _Dice(2, 5, 4, 3, 3))
    # 3 + the simple die 4 = 7 points: 14 xp, a Minor Flaw.
    assert (
        "14 xp lost" in notes[3] and "a Minor Hermetic or Supernatural Flaw" in notes[3]
    )


def test_demonic_blood_is_immune_to_warping():
    saga = _saga(kind="companion", realm="Faerie", aura=8)
    person = saga.characters[0]
    person.virtues_flaws = [VirtueFlawInstance("vf_demonic_blood")]
    seasons.year_end_aging(saga, _Dice(0))
    assert warping.total_points(person) == 0


def test_a_non_magus_warping_score_brings_flaws_and_a_virtue():
    assert warping.mundane_effects(0, 1) == [
        "Warping Score 1: a Minor Flaw from the main source of the Warping."
    ]
    assert len(warping.mundane_effects(4, 7)) == 3  # 5, 6 and 7
