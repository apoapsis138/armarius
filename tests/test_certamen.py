"""Certamen totals (STORY-812)."""

import pytest

from ars_magica_manager.models import Ability, ArtScore, Character, Characteristics
from ars_magica_manager.rules import certamen
from ars_magica_manager.rules.xp import ability_xp, art_xp


def test_certamen_totals():
    magus = Character(
        id="m",
        name="M",
        type="magus",
        characteristics=Characteristics(
            quickness=1, presence=2, perception=-1, intelligence=3, stamina=1
        ),
        arts={"perdo": ArtScore(xp=art_xp(9)), "ignem": ArtScore(xp=art_xp(6))},
        abilities=[
            Ability("Finesse", xp=ability_xp(2)),
            Ability("Penetration", xp=ability_xp(3)),
            Ability("Parma Magica", xp=ability_xp(4)),
        ],
        fatigue_level="weary",
    )
    totals = certamen.certamen_totals(magus, "Perdo", "Ignem")
    assert totals.initiative == 3
    assert (totals.attack_technique, totals.defence_form) == (2 + 9 - 1, -1 + 6 - 1)
    assert (totals.attack_form, totals.defence_technique) == (2 + 6 - 1, -1 + 9 - 1)
    assert totals.weakening_base == 6
    assert totals.resistance == 5  # Parma counts once, not x5
    assert certamen.max_vis(magus, "Perdo") == 9


@pytest.mark.parametrize(
    ("weakening", "resistance", "levels"),
    [(10, 10, 0), (11, 10, 1), (15, 10, 1), (16, 10, 2), (21, 5, 4)],
)
def test_fatigue_lost(weakening, resistance, levels):
    assert certamen.fatigue_lost(weakening, resistance) == levels


def test_a_tie_goes_to_the_defender():
    assert certamen.attack_advantage(12, 12) == 0
    assert certamen.attack_advantage(15, 12) == 3
