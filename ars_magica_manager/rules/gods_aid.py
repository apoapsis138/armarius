"""Invoking God's aid, for oneself or for followers, and in war (Realms
of Power: The Divine, Invoking God's Aid, pp. 41-42). The roll and its
bonus table are rules.holy_influence's (aid_total, aid_bonus); this adds
who may ask, the group and war rules, and the odds.

- Anyone who can spend a Confidence Point may ask, or a Faith Point with
  True Faith; not a grog, nor one with Low Self-Esteem (p. 41). A short
  prayer aloud and the point spent: a stress die + Communication +
  Dominion Lore; 9 gives +1, 15 +2, 24 +3 (the most). A 0 rolls at least
  three botch dice: divine disfavour (struck dumb or blind, clumsy or
  slow) until penance.
- The bonus adds to every roll in the scene clearly made toward the aim
  asked for, spellcasting among them, until one of them fails or the
  scene ends (p. 41).
- One with spiritual authority may ask it for his followers, from two or
  three parishioners to an army: the same roll, and they and he gain the
  bonus. With the Ceremony Ability he adds it, and each participant's
  Communication + Dominion Lore (p. 42).
- In war (p. 42, sidebar): only against infidels or heretics as his faith
  sees them, or a supernatural menace not of the Divine (faeries, demons,
  magi). Both sides may be aided. A Trained Group adds a member's bonus to
  its combat bonus, beyond the usual three times the leader's Leadership,
  only the highest member's counting; lost when the group fails a roll or
  splits.

The errata have nothing on these pages; the Definitive Edition has no
rule for it."""

from __future__ import annotations

from functools import cache

from ..models import Character
from . import holy_influence as holy
from .scores import ability_level

SOURCE = "Realms of Power: The Divine, Invoking God's Aid, pp. 41-42"
BOOK = "RoP:D"
CEREMONY = "Ceremony"

#: Whom the aid is asked against in war (p. 42).
INFIDEL, OTHER_REALM, BELIEVER = "infidel", "other_realm", "believer"
FOES: dict[str, str] = {
    INFIDEL: "Infidels or heretics, as his faith sees them",
    OTHER_REALM: "A supernatural menace not of the Divine",
    BELIEVER: "Fellow believers of his own faith",
}


def may_ask(character: Character) -> str:
    """Why he can't ask God's aid ("" when he can)."""
    return holy.may_invoke_aid(character)


def point(character: Character) -> str:
    """The point he spends: "Faith" with True Faith, else "Confidence"."""
    return holy.point_to_spend(character) or "Confidence"


def group_problem(character: Character, *, for_group: bool, ceremony: bool) -> str:
    if for_group and not holy.has_standing(character):
        return (
            "Asking it for followers needs spiritual authority over them "
            "(p. 41): clergy, True Faith, Dominion Lore..."
        )
    if ceremony and ability_level(character, CEREMONY) <= 0:
        return "Only one with the Ceremony Ability leads the prayer with it (p. 42)."
    return ""


def war_problem(foe: str) -> str:
    if foe == BELIEVER:
        return (
            "In war God's aid is asked only against infidels, heretics or a "
            "supernatural menace not of the Divine (p. 42)."
        )
    return ""


def total(character: Character, *, ceremony: bool = False, others: int = 0) -> int:
    """Communication + Dominion Lore, and with Ceremony its score and each
    participant's Communication + Dominion Lore, before the die."""
    found = holy.aid_total(character)
    if ceremony:
        found += ability_level(character, CEREMONY) + max(0, others)
    return found


def bonus(rolled: int) -> int:
    return holy.aid_bonus(rolled)


# -- the odds of a stress die --


@cache
def _at_least(need: int, multiplier: int) -> float:
    """The chance a stress die already doubled to `multiplier` shows
    `need` or more (a 0 now counts 10, a 1 doubles again)."""
    if need <= multiplier:
        return 1.0
    found = sum(1 for face in range(2, 10) if face * multiplier >= need)
    found += 1 if 10 * multiplier >= need else 0
    return (found + _at_least(need, 2 * multiplier)) / 10


def stress_chance(modifiers: int, ease: int) -> float:
    """The chance `modifiers` + a stress die meets `ease` (a 0 counts 0,
    a botch or not)."""
    need = ease - modifiers
    if need <= 0:
        return 1.0
    plain = sum(1 for face in range(2, 10) if face >= need)
    return (plain + _at_least(need, 2)) / 10


#: How many doublings the odds follow; past this the chance is negligible.
_DEPTH = 8


@cache
def stress_distribution() -> tuple[tuple[int, float], ...]:
    """A stress die's values and their chances (a 0 counts 0)."""
    found: dict[int, float] = {0: 0.1}
    chance, multiplier = 0.1, 1
    for face in range(2, 10):
        found[face] = found.get(face, 0) + 0.1
    for _ in range(_DEPTH):
        multiplier *= 2
        for face in range(2, 11):
            value = face * multiplier
            found[value] = found.get(value, 0) + chance * 0.1
        chance *= 0.1
    return tuple(sorted(found.items()))


def opposed_chance(mine: int, theirs: int) -> float:
    """The chance `mine` + a stress die meets `theirs` + another."""
    dist = stress_distribution()
    return sum(p * q for x, p in dist for y, q in dist if mine + x >= theirs + y)


def chances(modifiers: int) -> list[tuple[int, float]]:
    """Each bonus and the chance of reaching it or more."""
    return [
        (value, stress_chance(modifiers, ease)) for ease, value in holy.INFLUENCE_TABLE
    ]
