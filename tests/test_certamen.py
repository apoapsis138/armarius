"""Certamen totals, and the duel's choice of Art."""

import random

import pytest

from ars_magica_manager.models import Ability, ArtScore, Character, Characteristics
from ars_magica_manager.rules import certamen
from ars_magica_manager.rules import certamen_duel as cd
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


class _Fives(random.Random):
    """Every die a 5: no botches, and both Arts' totals compared fairly."""

    def randrange(self, *_a, **_k) -> int:  # type: ignore[override]
        return 5


def _duelist(cid: str, name: str, rego: int, ignem: int, pre: int, per: int):
    magus = Character(id=cid, name=name, type="magus")
    magus.characteristics = Characteristics(presence=pre, perception=per, stamina=3)
    magus.arts = {
        "rego": ArtScore(xp=art_xp(rego)),
        "ignem": ArtScore(xp=art_xp(ignem)),
    }
    return magus


def _first_attack(duel: cd.Duel, name: str) -> str:
    return next(line for line in duel.lines if f": {name} attacks with" in line)


def test_whichever_art_is_better_weighs_the_rivals_defence():
    """Guide 13: Adelheid (Attack +5 Rego or +17 Ignem; Defense +18 Ignem or
    +6 Rego) against Rudolf of Tremere (his Ignem 6 counts double: Attack
    +11 Rego or +13 Ignem; Defense +13 Ignem or +11 Rego). Her Ignem attack
    beats his Rego defence by 6, while her Rego attack falls 8 short of his
    Ignem defence, so she attacks with Ignem; he too, by 13 - 6 against
    11 - 18 (DE p. 231)."""
    adelheid = _duelist("a", "Adelheid", 3, 15, 2, 3)
    rudolf = _duelist("r", "Rudolf", 10, 6, 1, 1)
    rudolf.hermetic.house = certamen.TREMERE
    duel = cd.play(None, cd.Plan(adelheid), cd.Plan(rudolf), "Rego", "Ignem", _Fives())
    assert "Adelheid attacks with Ignem" in _first_attack(duel, "Adelheid")
    assert "Rudolf attacks with Ignem" in _first_attack(duel, "Rudolf")


def test_whichever_art_is_better_counts_vis_and_ties_to_the_technique():
    """Even Arts tie, and the tie goes to the Technique; a pawn of the
    Form's vis to spend on attack tips it to the Form."""
    one = _duelist("a", "Una", 5, 5, 0, 0)
    two = _duelist("b", "Duo", 5, 5, 0, 0)
    duel = cd.play(None, cd.Plan(one), cd.Plan(two), "Rego", "Ignem", _Fives())
    assert "Una attacks with Rego" in _first_attack(duel, "Una")
    one.raw_vis = {"ignem": 3}
    duel = cd.play(
        None, cd.Plan(one, attack_vis=1), cd.Plan(two), "Rego", "Ignem", _Fives()
    )
    assert "Una attacks with Ignem" in _first_attack(duel, "Una")


def test_a_tie_goes_to_the_defender():
    assert certamen.attack_advantage(12, 12) == 0
    assert certamen.attack_advantage(15, 12) == 3
