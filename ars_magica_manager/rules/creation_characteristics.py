"""Creation checks for the Characteristics step (STORY-1305): 7 points on
the cost table (+1 = 1, +2 = 3, +3 = 6; negatives refund the same), range
-3..+3, Improved Characteristics adding 3 points a copy, Great and Poor
(Characteristic) taking a score past +3 or -3, and a child's age modifier.

A sheet's Characteristic is the score in play, so what was bought is the
score less its Great/Poor copies and the child modifier. Virtues come
before Characteristics, so Great (Characteristic) is never refused: this
step warns until the Characteristic is at +3 with its Great copies on top.

Rules: reference/rules-engine-reference.md §2 Characteristics; Child
characters; §5 Great (Characteristic), Improved Characteristics.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import sourcebooks
from ..models import Character, Saga
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import age

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Characteristics "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Three:"
    "_Characters#Characteristics_2)"
)
GREAT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, Great "
    "(Characteristic) (https://www.redcap.org/page/Ars_Magica_Definitive_"
    "Edition,_Chapter_Four:_Virtues_and_Flaws#Great_(Characteristic))"
)
CHILD_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Child "
    "Characters (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Three:_Characters#Child_Characters)"
)
GROGS_SOURCE = (
    "Grogs, Chapter 5, Starting Characteristics (https://www.redcap.org/page/"
    "Grogs_Chapter_Five:_Creating_%26_Maintaining_Grogs#Starting_Characteristics)"
)

CHARACTERISTICS: tuple[tuple[str, str], ...] = (
    ("intelligence", "Intelligence"),
    ("perception", "Perception"),
    ("strength", "Strength"),
    ("stamina", "Stamina"),
    ("presence", "Presence"),
    ("communication", "Communication"),
    ("dexterity", "Dexterity"),
    ("quickness", "Quickness"),
)
BUDGET = 7
IMPROVED_POINTS = 3
BOUGHT_LIMIT = 3
#: Great or Poor (Characteristic) can take a score this far (+5 / -5).
VIRTUE_LIMIT = 5
GREAT = "vf_great_characteristic"
POOR = "vf_poor_characteristic"
IMPROVED = "vf_improved_characteristics"

#: The Grogs book's pre-bought arrays, each spending the standard 7 points.
GROG_ARRAYS: tuple[tuple[int, ...], ...] = (
    (2, 2, 2, 2, 1, 1, -1, -3),
    (3, 2, 2, 1, 1, 0, -1, -3),
    (3, 3, 1, 1, 0, -1, -2, -2),
    (3, 2, 2, 1, -1, -1, -1, -2),
    (2, 2, 2, 2, 1, 0, -2, -2),
    (3, 3, 0, 0, 0, -1, -1, -2),
    (2, 2, 2, 1, 0, 0, 0, -2),
    (3, 1, 1, 0, 0, 0, 0, -1),
)


def cost(score: int) -> int:
    """What a bought score costs: n(n+1)/2, a negative refunding the same."""
    n = abs(score)
    return (n * (n + 1) // 2) * (1 if score >= 0 else -1)


def child_modifier(years: int | None) -> int:
    """The age modifier on every Characteristic for a child under 14."""
    if years is None or years >= 14:
        return 0
    if years >= 12:
        return -1
    if years >= 10:
        return -2
    if years >= 8:
        return -3
    return -4


@dataclass(frozen=True)
class CharacteristicLine:
    key: str
    name: str
    score: int
    #: Copies of Great (positive) or Poor (negative) for it.
    virtue: int
    #: The score bought with points.
    bought: int
    cost: int


def lines(saga: Saga, character: Character) -> list[CharacteristicLine]:
    modifier = child_modifier(age(saga, character))
    result = []
    for key, name in CHARACTERISTICS:
        score = getattr(character.characteristics, key)
        great = sum(
            1
            for vf in character.virtues_flaws
            if vf.vf_id == GREAT and vf.params.get("characteristic") == key
        )
        poor = sum(
            1
            for vf in character.virtues_flaws
            if vf.vf_id == POOR and vf.params.get("characteristic") == key
        )
        virtue = great - poor
        base = score - modifier
        # Great/Poor count only past +3/-3: a Great copy on a score not yet
        # at +3 is bought points still to find.
        if base > BOUGHT_LIMIT:
            bought = base - min(great, base - BOUGHT_LIMIT)
        elif base < -BOUGHT_LIMIT:
            bought = base + min(poor, -BOUGHT_LIMIT - base)
        else:
            bought = base
        result.append(
            CharacteristicLine(key, name, score, virtue, bought, cost(bought))
        )
    return result


def budget(character: Character) -> int:
    improved = sum(1 for vf in character.virtues_flaws if vf.vf_id == IMPROVED)
    return BUDGET + IMPROVED_POINTS * improved


def _check(label: str, ok: bool, detail: str, source: str = SOURCE, *, advice=False):
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check("characteristics", label, status, detail, source)


@check("characteristics", CHARACTER_CHECKS)
def characteristic_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    found_lines = lines(saga, character)
    spent = sum(line.cost for line in found_lines)
    points = budget(character)
    found = [
        _check(
            f"Characteristics cost at most {points} points",
            spent <= points,
            f"{spent} spent"
            + (f", {spent - points} too many" if spent > points else ""),
        )
    ]
    if spent < points:
        found.append(
            _check(
                "Characteristic points spent",
                False,
                f"{points - spent} unspent",
                advice=True,
            )
        )
    for line in found_lines:
        if abs(line.bought) > BOUGHT_LIMIT:
            found.append(
                _check(
                    f"{line.name} is bought from -3 to +3",
                    False,
                    f"{line.bought:+d} bought",
                )
            )
        if line.virtue > 0:
            # Great (Characteristic): +1 a copy on top of +3, at most +5.
            wanted = min(BOUGHT_LIMIT + line.virtue, VIRTUE_LIMIT)
            base = line.score - child_modifier(age(saga, character))
            found.append(
                _check(
                    f"Great {line.name}: {line.name} at +3, then +1 a copy",
                    base == wanted,
                    f"{base:+d}, should be {wanted:+d}",
                    GREAT_SOURCE,
                )
            )
        elif line.virtue < 0:
            wanted = max(-BOUGHT_LIMIT + line.virtue, -VIRTUE_LIMIT)
            base = line.score - child_modifier(age(saga, character))
            found.append(
                _check(
                    f"Poor {line.name}: {line.name} at -3, then -1 a copy",
                    base == wanted,
                    f"{base:+d}, should be {wanted:+d}",
                    GREAT_SOURCE,
                )
            )
    modifier = child_modifier(age(saga, character))
    if modifier:
        found.append(
            _check(
                "A child's Characteristics carry the age modifier",
                True,
                f"{modifier:+d} on each (under 14)",
                CHILD_SOURCE,
            )
        )
    return found


def grog_arrays_offered(saga: Saga, character: Character) -> bool:
    """A grog may take a pre-bought array when the Grogs book is in play."""
    return character.type == "grog" and sourcebooks.in_play(
        "Grogs", sourcebooks.saga_books(saga)
    )
