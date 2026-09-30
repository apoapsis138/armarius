"""Aging and Decrepitude (STORY-904): the Winter aging roll."""

import random

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Aging,
    Character,
    Characteristics,
    Covenant,
    Saga,
)
from ars_magica_manager.rules import aging


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
    # Die 8 + 5 (age / 10) - 1 (Living Conditions) = 12: 1 Aging Point, on
    # the highest Characteristic.
    lines = seasons.year_end_aging(saga, _Dice(8))
    magus = saga.character("m")
    assert magus.aging.aging_points == {"intelligence": 1}
    assert magus.aging.decrepitude_points == 1
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
