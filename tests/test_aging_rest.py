"""Aging, the rest: Unaging's harmless Crises, Leprosy's Heavy Wound at
every Crisis (DE pp. 114, 135), and what Decrepitude 4 and 5 mean (DE p.
392)."""

import random

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Aging,
    Character,
    Characteristics,
    Covenant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import aging


class _Dice(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5

    def randint(self, a, b):
        return self.faces.pop(0) if self.faces else 5


def _saga(*vf_ids: str) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep", living_conditions_magi=1)
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(stamina=1, intelligence=3)
    magus.background.year_born = 1160
    magus.aging = Aging(longevity_modifier=2)
    magus.virtues_flaws = [VirtueFlawInstance(v) for v in vf_ids]
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[magus])
    saga.current_season = "Winter"
    return saga


# Faces 1, 5: a doubled 5 = 10; 10 + 6 - 1 - 2 = 13, a Crisis; its simple
# die 3 + 6 + Decrepitude 1 = 10: bedridden a month.
_CRISIS = (1, 5, 3)


def test_a_crisis_takes_the_next_season():
    saga = _saga()
    seasons.year_end_aging(saga, _Dice(*_CRISIS))
    assert saga.character("m").aging.recovering == "Spring 1221"


def test_the_unaging_take_no_harm_from_a_crisis_that_cant_kill():
    saga = _saga("vf_unaging")
    seasons.year_end_aging(saga, _Dice(*_CRISIS))
    magus = saga.character("m")
    assert magus.aging.recovering == ""
    assert "Unaging" in magus.diary[-1].details


def test_a_crisis_that_can_kill_is_fatal():
    assert aging.fatal_crisis("Aging Crisis: 15 (die 5): Minor illness.")
    assert not aging.fatal_crisis("Aging Crisis: 10 (die 3): Bedridden a month.")


def test_a_leper_takes_a_heavy_wound_with_each_crisis():
    saga = _saga("vf_leprosy")
    # Leprosy's Living Conditions -2: a doubled 4 = 8; 8 + 6 + 1 - 2 = 13.
    seasons.year_end_aging(saga, _Dice(1, 4, 3))
    magus = saga.character("m")
    assert magus.wounds.heavy == 1
    assert "Leprosy" in magus.diary[-1].details


def test_decrepitude_4_and_5_are_flagged():
    magus = Character(id="m", name="Tiberius", type="magus")
    assert aging.frailty(magus) == ""
    magus.aging.decrepitude = 4
    assert aging.frailty(magus).startswith("Decrepitude 4: extremely frail")
    magus.virtues_flaws = [VirtueFlawInstance("vf_unaging")]
    assert aging.frailty(magus) == ""
    magus.aging.decrepitude = 5
    assert aging.frailty(magus).startswith("Decrepitude 5: bedridden")
