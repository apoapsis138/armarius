"""Creation checks for the Characteristics step: 7 points on
the cost table (+1 = 1, +2 = 3, +3 = 6; negatives refund the same), range
-3..+3, Improved Characteristics adding 3 points a copy, Great and Poor
(Characteristic) taking a score past +3 or -3, and a child's age modifier.

A sheet's Characteristic is the score in play, so what was bought is the
score less its Great/Poor copies and the child modifier. Taking Great
(Characteristic) raises the score a point and is refused unless it is at
+3 or +4 (the second copy takes +4 to +5); Poor lowers it from -3 or -4
the same way. Removing one undoes its point while the score is past +3 or
-3. This step still warns when a score doesn't match its copies (a save
from before Great changed the score).

An animal grog has no child modifier, and its Size is added after the
points: twice to Strength, less from Quickness (rules.animal_grogs).

Rules: reference/rules-engine-reference.md §2 Characteristics; Child
characters; §5 Great (Characteristic), Improved Characteristics.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .. import sourcebooks
from ..markup import todo
from ..models import Character, Saga, VirtueFlawInstance
from . import animal_grogs
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import age
from .derived import size

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Characteristics, p. 48"
)
GREAT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, Great "
    "(Characteristic), p. 83"
)
CHILD_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Child Characters, p. 44"
)
GROGS_SOURCE = "Grogs, Chapter 5, Starting Characteristics, p. 65"

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
_ABBREVIATIONS = {"quickness": "Qik"}
BUDGET = 7
IMPROVED_POINTS = 3
BOUGHT_LIMIT = 3
#: Great or Poor (Characteristic) can take a score this far (+5 / -5).
VIRTUE_LIMIT = 5
GREAT = "vf_great_characteristic"
POOR = "vf_poor_characteristic"
IMPROVED = "vf_improved_characteristics"
WEAK = "vf_weak_characteristics"
#: The point a copy of Great or Poor (Characteristic) moves its score.
STEPS = {GREAT: 1, POOR: -1}


@dataclass(frozen=True)
class Heritage:
    """A free point a Virtue adds to one Characteristic, never taking it
    past `cap` (Sidhe Blood: +1 Presence, not above +3)."""

    key: str
    step: int
    cap: int


#: The kinds of Faerie Blood whose benefit is a Characteristic point.
BLOOD_CHARACTERISTICS: dict[str, str] = {
    "bloodcap": "strength",
    "ettin": "stamina",
    "nymph": "communication",
    "padfoot": "perception",
    "sidhe": "presence",
}
FAERIE_BLOODS = ("vf_faerie_blood", "vf_strong_faerie_blood")
BLOODCAP = "vf_faerie_blood_bloodcap"
#: Giant Blood: +1 Strength and +1 Stamina, which may reach +6 (DE p. 83).
GIANT_BLOOD = "vf_giant_blood"
GIANT_CAP = 6
#: Faerie Legacy lets a heritage point take the score one higher.
FAERIE_LEGACY = "vf_faerie_legacy"
HERITAGE_CAP = 3
UNINSPIRATIONAL = "vf_uninspirational"


def heritages(instance: VirtueFlawInstance) -> list[Heritage]:
    """The free Characteristic points this Virtue adds."""
    if instance.vf_id == BLOODCAP:
        return [Heritage("strength", 1, HERITAGE_CAP)]
    if instance.vf_id == GIANT_BLOOD:
        return [Heritage("strength", 1, GIANT_CAP), Heritage("stamina", 1, GIANT_CAP)]
    if instance.vf_id in FAERIE_BLOODS:
        key = BLOOD_CHARACTERISTICS.get(instance.params.get("blood", "").casefold())
        return [Heritage(key, 1, HERITAGE_CAP)] if key else []
    return []


def heritage_cap(character: Character, found: Heritage) -> int:
    """How high a heritage point can take its score: one more with Faerie
    Legacy."""
    legacy = any(vf.vf_id == FAERIE_LEGACY for vf in character.virtues_flaws)
    return found.cap + legacy


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


def age_modifier(saga: Saga, character: Character) -> int:
    """The child modifier for the character's age; none for an animal,
    whose kind is grown long before 14."""
    if animal_grogs.is_animal(character):
        return 0
    return child_modifier(age(saga, character))


def size_adjustment(character: Character, key: str) -> int:
    """What an animal's Size adds to Characteristic `key` after the points
    are spent (animal_grogs.size_adjustment); 0 for a person."""
    if not animal_grogs.is_animal(character):
        return 0
    return animal_grogs.size_adjustment(character, key, int(size(character).total))


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
    #: Free points from a heritage (Sidhe Blood's Presence).
    free: int = 0
    #: What an animal's Size adds, after the points.
    size: int = 0


def lines(
    saga: Saga, character: Character, scores: Mapping[str, int | None] | None = None
) -> list[CharacteristicLine]:
    """Each Characteristic's score and what it cost: the sheet's, or
    `scores` (a form being filled in; a blank counts as 0)."""
    modifier = age_modifier(saga, character)
    result = []
    for key, name in CHARACTERISTICS:
        score = (
            getattr(character.characteristics, key)
            if scores is None
            else scores.get(key) or 0
        )
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
        given = [
            found
            for vf in character.virtues_flaws
            for found in heritages(vf)
            if found.key == key
        ]
        virtue = great - poor
        sized = size_adjustment(character, key)
        base = score - modifier - sized
        # A heritage's free point is counted as given whenever the score
        # allows it (at its cap it may instead have been bought).
        cap = max((heritage_cap(character, h) for h in given), default=0)
        free = sum(h.step for h in given) if -BOUGHT_LIMIT <= base <= cap else 0
        base -= free
        # Great/Poor count only past +3/-3: a Great copy on a score not yet
        # at +3 is bought points still to find.
        if base > BOUGHT_LIMIT:
            bought = base - min(great, base - BOUGHT_LIMIT)
        elif base < -BOUGHT_LIMIT:
            bought = base + min(poor, -BOUGHT_LIMIT - base)
        else:
            bought = base
        result.append(
            CharacteristicLine(
                key, name, score, virtue, bought, cost(bought), free, sized
            )
        )
    return result


def _stepped(
    saga: Saga, character: Character, instance: VirtueFlawInstance
) -> tuple[str, str, int, int] | None:
    """(key, name, step, score less the child modifier) of the
    Characteristic a Great or Poor copy moves, or None for anything else."""
    step = STEPS.get(instance.vf_id)
    key = instance.params.get("characteristic", "")
    name = dict(CHARACTERISTICS).get(key)
    if step is None or name is None:
        return None
    base = (
        getattr(character.characteristics, key)
        - age_modifier(saga, character)
        - size_adjustment(character, key)
    )
    return key, name, step, base


def virtue_refusal(
    saga: Saga, character: Character, instance: VirtueFlawInstance
) -> str:
    """Why `character` can't take this Great or Poor copy ("" if it can):
    Great needs the Characteristic at +3 or +4, Poor at -3 or -4.
    Uninspirational needs Presence and Communication at 0 or less."""
    if instance.vf_id == UNINSPIRATIONAL:
        high = [
            f"{name} {getattr(character.characteristics, key):+d}"
            for key, name in CHARACTERISTICS
            if key in ("presence", "communication")
            and getattr(character.characteristics, key) > 0
        ]
        return (
            f"Uninspirational caps Presence and Communication at 0 ({', '.join(high)})."
            if high
            else ""
        )
    found = _stepped(saga, character, instance)
    if found is None:
        return ""
    _, name, step, base = found
    if step > 0 and base < BOUGHT_LIMIT:
        return f"Great {name} needs {name} at +3 first (it is {base:+d})."
    if step > 0 and base >= VIRTUE_LIMIT:
        return f"{name} is already {base:+d}, the most Great allows."
    if step < 0 and base > -BOUGHT_LIMIT:
        return f"Poor {name} needs {name} at -3 first (it is {base:+d})."
    if step < 0 and base <= -VIRTUE_LIMIT:
        return f"{name} is already {base:+d}, the most Poor allows."
    return ""


def apply_virtue(
    saga: Saga, character: Character, instance: VirtueFlawInstance
) -> None:
    """Move the Characteristic a newly taken Great or Poor copy names, or
    add a heritage's free point (not past its cap)."""
    if free_points := heritages(instance):
        for free in free_points:
            score = getattr(character.characteristics, free.key)
            if score - age_modifier(saga, character) < heritage_cap(character, free):
                setattr(character.characteristics, free.key, score + free.step)
        return
    found = _stepped(saga, character, instance)
    if found is not None:
        key, _, step, _ = found
        score = getattr(character.characteristics, key)
        setattr(character.characteristics, key, score + step)


def removal_changes(
    saga: Saga, character: Character, instance: VirtueFlawInstance
) -> list[tuple[str, str, int, int]]:
    """(key, name, before, after) of each Characteristic removing this Great
    or Poor copy or heritage moves back; none when it moves nothing: a score
    not past +3 or -3 never had a copy's point added, and a heritage's free
    point comes back off while the score is at its cap or below."""
    if free_points := heritages(instance):
        changes = []
        for free in free_points:
            score = getattr(character.characteristics, free.key)
            if score - age_modifier(saga, character) <= heritage_cap(character, free):
                changes.append(
                    (
                        free.key,
                        dict(CHARACTERISTICS)[free.key],
                        score,
                        score - free.step,
                    )
                )
        return changes
    found = _stepped(saga, character, instance)
    if found is None:
        return []
    key, name, step, base = found
    if (step > 0 and base <= BOUGHT_LIMIT) or (step < 0 and base >= -BOUGHT_LIMIT):
        return []
    score = getattr(character.characteristics, key)
    return [(key, name, score, score - step)]


def moves_text(changes: list[tuple[str, str, int, int]]) -> str:
    """ "Strength goes from +4 to +3 and Stamina from +2 to +1"."""
    return " and ".join(
        f"{name} goes from {before:+d} to {after:+d}"
        for _, name, before, after in changes
    )


def unapply_virtue(
    saga: Saga, character: Character, instance: VirtueFlawInstance
) -> None:
    """Take back the point of a Great or Poor copy, or a heritage's free
    point, being removed."""
    for key, _, _, after in removal_changes(saga, character, instance):
        setattr(character.characteristics, key, after)


def budget(character: Character) -> int:
    """The points to buy Characteristics with: 7, +3 for each Improved
    Characteristics, -3 for each Weak Characteristics (two leave one;
    DE pp. 86, 152)."""
    improved = sum(1 for vf in character.virtues_flaws if vf.vf_id == IMPROVED)
    weak = sum(1 for vf in character.virtues_flaws if vf.vf_id == WEAK)
    return BUDGET + IMPROVED_POINTS * (improved - weak)


def points_text(
    saga: Saga, character: Character, scores: Mapping[str, int | None]
) -> str:
    """The points a Characteristics form's `scores` spend, as it is typed
    (markup): spent of the budget and what's left, each score's
    cost, and any score bought past -3..+3."""
    found = lines(saga, character, scores)
    spent = sum(line.cost for line in found)
    points = budget(character)
    if spent > points:
        total = f"[$text-error]{spent} of {points} spent, {spent - points} too many[/]"
    elif spent == points:
        total = f"[$text-success]{spent} of {points} spent[/]"
    else:
        total = f"{spent} of {points} spent, {points - spent} left"
    # In the form's own order (the order of `scores`).
    order = list(scores)
    costs = "  ".join(
        f"{_ABBREVIATIONS.get(line.key, line.name[:3])} "
        + (f"{line.cost:+d}" if line.cost else "0")
        for line in sorted(found, key=lambda line: order.index(line.key))
    )
    text = [f"[b]Points:[/] {total}", f"[b]Cost:[/] {costs}"]
    sized = [line for line in found if line.size]
    if sized:
        text.append(
            "[b]Size:[/] "
            + ", ".join(f"{line.name} {line.size:+d}" for line in sized)
            + " added after the points"
        )
    past = [line.name for line in found if abs(line.bought) > BOUGHT_LIMIT]
    if past:
        text.append(
            todo(
                f"{', '.join(past)}: bought from -3 to +3 (Great or "
                "Poor adds 1 a copy past that)."
            )
        )
    return "\n".join(text)


def _check(
    label: str, ok: bool, detail: str, source: str = SOURCE, *, advice: bool = False
):
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
            base = line.score - age_modifier(saga, character) - line.size
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
            base = line.score - age_modifier(saga, character) - line.size
            found.append(
                _check(
                    f"Poor {line.name}: {line.name} at -3, then -1 a copy",
                    base == wanted,
                    f"{base:+d}, should be {wanted:+d}",
                    GREAT_SOURCE,
                )
            )
    modifier = age_modifier(saga, character)
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
