"""Penetration and Magic Resistance."""

from ars_magica_manager import sheet_text
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Background,
    Character,
    Saga,
)
from ars_magica_manager.rules import penetration as pen
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(penetration: int = 3, parma: int = 2) -> Character:
    return Character(
        id="m",
        name="M",
        type="magus",
        arts={"ignem": ArtScore(xp=art_xp(8))},
        abilities=[
            Ability("Penetration", xp=ability_xp(penetration)),
            Ability("Parma Magica", xp=ability_xp(parma)),
        ],
    )


def test_the_books_worked_example():
    # Penetration 3 + specialty 1, Penetration Mastery 1; fixed Arcane
    # Connection (+4) and today's horoscope (+1): (4 + 1) x 6 = 30.
    bonus = pen.penetration_bonus(
        _magus(),
        arcane_connection="Indefinitely",
        sympathies=[pen.Sympathy("Target's horoscope for today", 1)],
        mastery=1,
        specialty=True,
    )
    assert bonus.total == 30


def test_sympathy_needs_an_arcane_connection_and_is_capped():
    no_connection = pen.penetration_bonus(
        _magus(), sympathies=[pen.Sympathy("Target's signature", 1)]
    )
    assert no_connection.total == 3
    capped = pen.penetration_bonus(
        _magus(),
        arcane_connection="Hours or days",
        sympathies=[pen.Sympathy("A big one", 5)],
    )
    assert capped.total == 3 * (1 + 1 + 2)


def test_penetration_must_beat_magic_resistance():
    assert pen.penetration_total(30, 6, 20) == 16
    assert pen.penetrates(16, 15)
    assert not pen.penetrates(15, 15)
    assert not pen.penetrates(0, 0)
    assert pen.penetrates(-5, None)  # no Magic Resistance at all


def test_hermetic_magic_resistance():
    magus = _magus()
    assert pen.magic_resistance(magus, "Ignem").total == 8 + 10
    assert pen.magic_resistance(magus, "Ignem", parma_raised=False).total == 8
    assert pen.magic_resistance(magus, "Ignem", aura=3).total == 21
    assert pen.magic_resistance(magus, "Vim", aura=2, aura_realm="Divine").total == 4
    assert pen.magic_resistance(magus, "Vim", sharing=True).total == 0  # Parma 2


def test_true_faith_and_the_dominion_option():
    faithful = Character(
        id="f", name="F", type="companion", background=Background(true_faith_score=1)
    )
    assert pen.faith_magic_resistance(faithful) == 10
    assert sheet_text.faith_score_text(faithful) == "1 (Magic Resistance 10)"
    plain = Character(id="p", name="P", type="grog")
    saga = Saga(id="s", name="S", rule_options={"dominion_magic_resistance": True})
    assert pen.faith_magic_resistance(plain, dominion_aura=3) == 0
    assert pen.faith_magic_resistance(plain, saga, dominion_aura=3) == 15


def test_the_aegis_hinders_foreign_casting_inside():
    assert pen.aegis_penalty(25) == -12
