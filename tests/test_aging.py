"""Aging and Decrepitude: the Winter aging roll."""

import random

from ars_magica_manager import aging_due, seasons
from ars_magica_manager.models import (
    Aging,
    Character,
    Characteristics,
    Covenant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import aging, hybrid_magic, warping


class _Dice(random.Random):
    """A Random whose d10s come out as given (a stress die reads 0 as 10
    unless it's the first face)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5

    def randint(self, a, b):
        return self.faces.pop(0) if self.faces else 5


def _saga(age: int = 50, **aging_kw) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep", living_conditions_magi=1)
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(stamina=1, quickness=-1, intelligence=3)
    magus.background.year_born = 1220 - age
    magus.aging = Aging(**aging_kw)
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[magus])
    saga.current_season = "Winter"
    return saga


def test_decrepitude_advances_like_an_ability():
    assert [aging.decrepitude_score(p) for p in (0, 4, 5, 17, 30, 75)] == [
        0,
        0,
        1,
        2,
        3,
        5,
    ]


def test_a_typed_decrepitude_becomes_points():
    assert Aging.from_dict({"decrepitude": 2}).decrepitude_points == 15


def test_no_roll_before_35_without_a_ritual():
    saga = _saga(age=30)
    assert seasons.year_end_aging(saga, _Dice(9)) == []
    saga = _saga(age=30, longevity_modifier=3)
    assert len(seasons.year_end_aging(saga, _Dice(9))) == 1


def test_the_table_gives_aging_points_and_lowers_characteristics():
    saga = _saga(age=50)
    # Die 8 + 5 (age / 10) - 1 (Living Conditions) = 12: 1 Aging Point in
    # any Characteristic, for the player to place (the highest suggested);
    # its Decrepitude counts at once.
    lines = seasons.year_end_aging(saga, _Dice(8))
    magus = saga.character("m")
    assert magus.aging.aging_points == {}
    assert magus.aging.decrepitude_points == 1
    assert magus.aging.aging_due == [
        "Aging roll, Winter 1220: any Characteristic (suggested: Intelligence)"
    ]
    aging_due.place(saga, [magus], {})
    assert magus.aging.aging_points == {"intelligence": 1}
    assert magus.aging.decrepitude_points == 1 and magus.aging.aging_due == []
    assert magus.aging.apparent_age == 50
    assert lines[0].result == "apparent age +1, 1 Aging Point(s)"
    assert magus.diary[-1].activity == "Aging"


def test_a_characteristic_falls_when_its_points_exceed_it():
    saga = _saga(age=50)
    # Faces 1, 8: a doubled 8 = 16; 16 + 5 - 1 = 20: Communication and
    # Presence, both 0, fall on their first point.
    seasons.year_end_aging(saga, _Dice(1, 8))
    magus = saga.character("m")
    stats = magus.characteristics
    assert (stats.communication, stats.presence) == (-1, -1)
    assert magus.aging.aging_points == {"communication": 0, "presence": 0}
    assert magus.aging.decrepitude_points == 2


def test_a_crisis_ends_the_longevity_ritual_and_takes_the_next_season():
    saga = _saga(age=60, longevity_modifier=2)
    # Faces 1, 5: a doubled 5 = 10; 10 + 6 - 1 - 2 = 13: to the next
    # Decrepitude score, and a Crisis (simple die 3).
    seasons.year_end_aging(saga, _Dice(1, 5, 3))
    magus = saga.character("m")
    assert magus.aging.decrepitude == 1 and magus.aging.decrepitude_points == 5
    assert magus.aging.longevity_modifier == 0
    assert magus.aging.recovering == "Spring 1221"
    assert "Longevity Ritual sees the character through" in magus.diary[-1].details


def test_age_quickly_ages_by_an_effective_age_with_two_rolls():
    saga = _saga(age=20)  # effective age 40: past 35
    magus = saga.characters[0]
    assert seasons.year_end_aging(saga, _Dice(9)) == []
    magus.virtues_flaws = [VirtueFlawInstance("vf_age_quickly")]
    assert aging.effective_age(magus, 20) == 40
    assert len(seasons.year_end_aging(saga, _Dice(0, 0))) == 2


def test_no_aging_in_twilight():
    saga = _saga(age=50, twilight_until="Spring 1221")
    assert seasons.year_end_aging(saga, _Dice(9)) == []


def test_a_longevity_ritual_stored_negated_loads_as_its_bonus():
    assert Aging.from_dict({"longevity_modifier": -8}).longevity_modifier == 8


def test_time_in_the_aura_sets_its_yearly_warping():
    # DE p. 390: half the time, frequent visits, or away.
    assert warping.aura_points(9) == 4
    assert warping.aura_points(9, warping.HALF) == 2
    assert warping.aura_points(9, warping.FREQUENT) == 1
    assert warping.aura_points(7, warping.HALF, 1222) == 1
    assert warping.aura_points(7, warping.HALF, 1223) == 0
    assert warping.aura_points(10, warping.AWAY) == 0


def test_age_quickly_from_the_year_it_began():
    # DE p. 119: two years a year, from the curse rather than from birth.
    cursed = Character(
        id="c",
        name="C",
        type="companion",
        virtues_flaws=[VirtueFlawInstance("vf_age_quickly", {"since": "1210"})],
    )
    cursed.background.year_born = 1180  # 30 when it began
    assert aging.effective_age(cursed, 40) == 50
    assert aging.effective_age(cursed, 25) == 25
    assert aging.rolls_per_year(cursed, 28) == 1
    assert aging.rolls_per_year(cursed, 40) == 2
    cursed.virtues_flaws = [VirtueFlawInstance("vf_age_quickly")]
    assert aging.effective_age(cursed, 40) == 80  # from birth


def test_a_botch_can_step_into_final_twilight():
    # DE p. 228: Warping 8 and two zeros land on row 10.
    time, _ = warping._twilight_time(10, 8, random.Random(1), None)
    assert "Final Twilight" in time


def test_might_virtues_are_immune_and_faerie_virtues_at_home_in_faerie_auras():
    # DE pp. 109-110, 389; RoP: Faerie p. 111.
    angel = Character(
        id="a",
        name="A",
        type="companion",
        virtues_flaws=[VirtueFlawInstance("vf_strong_angelic_heritage")],
    )
    assert warping.immune(angel)
    fey = Character(
        id="f",
        name="F",
        type="companion",
        virtues_flaws=[VirtueFlawInstance("vf_faerie_blood")],
    )
    assert not hybrid_magic.warps_from_aura(fey, "Faerie")
    assert hybrid_magic.warps_from_aura(fey, "Infernal")
