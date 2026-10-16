"""Derived character values: Size, the Damage Table's wound
ranges, Wound and Fatigue penalties, Encumbrance and Soak.

- Size: the typed base (0 for an adult human) plus Virtues and Flaws such as
  Large (+1), Giant Blood (+2), Small Frame (-1) and Dwarf (-2).
- Wound ranges: each band is max(1, 5 + Size) wide (Size 0: Light 1-5,
  Medium 6-10, Heavy 11-15, Incapacitating 16-20, Dead 21+).
- Wound Penalty: -1 per Light, -3 per Medium, -5 per Heavy wound, summed.
  Fatigue: Fresh 0, Winded 0, Weary -1, Tired -3, Dazed -5. Both apply to
  every roll (not Soak) and add together; Enduring Constitution makes each
  1 better (not past 0), Low Tolerance 1 worse.
- Encumbrance: Burden is the highest n whose n(n+1)/2 the total Load
  reaches; Encumbrance is Burden less a positive Strength (never below 0).
- Soak: Stamina + armour Protection (+ Virtues such as Tough), plus the
  adjustment typed on the sheet. A magus's Form bonus adds only against harm
  of that Form, so it is not part of the standing figure.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..models import Character, Possession, VirtueFlawInstance, Wounds
from . import effects
from .breakdown import Breakdown, Line
from .scores import character_source

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Combat Scores, "
    "Damage Table, Wounds, Fatigue and Encumbrance "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eleven:"
    "_Obstacles#Combat_Scores)"
)
SIZE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Size "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Three:"
    "_Characters#Size)"
)

WOUND_PENALTIES: dict[str, int] = {"light": -1, "medium": -3, "heavy": -5}
FATIGUE_PENALTIES: dict[str, int] = {
    "fresh": 0,
    "winded": 0,
    "weary": -1,
    "tired": -3,
    "dazed": -5,
    "unconscious": 0,  # no actions at all, rather than a penalty
}
WOUND_BANDS: tuple[str, ...] = ("Light", "Medium", "Heavy", "Incapacitating")


def size(character: Character) -> Breakdown:
    """The character's Size: the typed base plus Size Virtues and Flaws."""
    found = effects.collect([character_source(character.virtues_flaws)], "size")
    return effects.combine(
        character.background.size,
        found,
        base_label="Base Size",
        base_source=SIZE_SOURCE,
    )


def wound_ranges(size: int) -> list[tuple[str, int, int | None]]:
    """The Damage Table for a Size: (wound, lowest, highest) for each band,
    the last (Dead) open-ended."""
    width = max(1, 5 + size)
    bands = [
        (name, width * i + 1, width * (i + 1)) for i, name in enumerate(WOUND_BANDS)
    ]
    return [*bands, ("Dead", width * len(WOUND_BANDS) + 1, None)]


def wound_for(excess: int, size: int) -> str | None:
    """The wound a blow that beats Soak by `excess` deals (None for none)."""
    if excess <= 0:
        return None
    for name, _low, high in wound_ranges(size):
        if high is None or excess <= high:
            return name
    return "Dead"  # pragma: no cover - the last band is open-ended


def _adjusted(
    penalty: int, virtues_flaws: Sequence[VirtueFlawInstance], applies_to: str
) -> int:
    """A penalty made better (Enduring Constitution) or worse (Low
    Tolerance) by the character's Virtues and Flaws; only a penalty there
    is changes, and a better one stops at 0."""
    if not penalty:
        return 0
    found = effects.collect([character_source(virtues_flaws)], applies_to)
    return min(0, penalty + int(effects.amount_total(found)))


def wound_penalty(
    wounds: Wounds, virtues_flaws: Sequence[VirtueFlawInstance] = ()
) -> int:
    return _adjusted(
        wounds.light * WOUND_PENALTIES["light"]
        + wounds.medium * WOUND_PENALTIES["medium"]
        + wounds.heavy * WOUND_PENALTIES["heavy"],
        virtues_flaws,
        "wound_penalty",
    )


def fatigue_penalty(
    level: str, virtues_flaws: Sequence[VirtueFlawInstance] = ()
) -> int:
    return _adjusted(FATIGUE_PENALTIES.get(level, 0), virtues_flaws, "fatigue_penalty")


def burden(load: int) -> int:
    """The highest n with Load >= n(n+1)/2."""
    n = 0
    while (n + 1) * (n + 2) // 2 <= load:
        n += 1
    return n


def encumbrance(load: int, strength: int) -> int:
    """Burden, less Strength when it's positive (spare Strength is no bonus)."""
    return max(0, burden(load) - max(strength, 0))


def carried_load(inventory: Sequence[Possession]) -> int:
    """The Load of the weapons and armour the character has, times how many
    of each (everything on a character's sheet counts as carried)."""
    return sum(
        item.load * max(item.quantity, 1)
        for item in inventory
        if item.kind in ("weapon", "armor")
    )


def worn_armour(inventory: Sequence[Possession]) -> Possession | None:
    """The armour that protects best (a character wears one suit)."""
    armour = [item for item in inventory if item.kind == "armor"]
    return max(armour, key=lambda item: item.armor_protection, default=None)


def soak(character: Character) -> Breakdown:
    """Stamina + armour Protection + Soak Virtues + the typed adjustment."""
    lines = [Line("Stamina", amount=character.characteristics.stamina, source=SOURCE)]
    total = character.characteristics.stamina
    armour = worn_armour(character.inventory)
    if armour is not None and armour.armor_protection:
        lines.append(Line(armour.name, amount=armour.armor_protection, source=SOURCE))
        total += armour.armor_protection
    for effect in effects.collect([character_source(character.virtues_flaws)], "soak"):
        amount = effect.amount or 0
        lines.append(Line(effect.entry.name, amount=amount, source="character"))
        total += amount
    if character.wounds.soak:
        lines.append(Line("Adjustment", amount=character.wounds.soak))
        total += character.wounds.soak
    return Breakdown(total=total, lines=lines)


def terms(breakdown: Breakdown, *, skip_first_zero: bool = False) -> str:
    """A breakdown's terms in words: "Stamina +1, Tough +3"."""
    parts = []
    for i, line in enumerate(breakdown.lines):
        if line.amount is None:
            continue
        if skip_first_zero and i == 0 and not line.amount:
            continue
        parts.append(f"{line.label} {line.amount:+g}")
    return ", ".join(parts)
