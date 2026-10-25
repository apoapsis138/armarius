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

No screen uses wound_for() yet: it is a rule for a screen still to come, and
only the tests call it.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..models import Character, Possession, VirtueFlawInstance, Wounds
from . import effects, equipment
from .breakdown import Breakdown, Line
from .rounding import round_up
from .scores import character_source

#: The Magic Resistance the Divine gives the ordained and anointed, by
#: office; their wives share their husbands' (DE p. 420; Commanding Aura,
#: p. 74). Soak gains a fifth of it.
OFFICE_RESISTANCE: dict[str, int] = {
    "Archbishop": 10,
    "King (crowned)": 10,
    "Queen (a crowned king's wife)": 10,
    "Legatus missus": 15,
    "Cardinal or legatus a latere": 20,
    "Pope": 25,
}
OFFICE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 12: Church Officers and Sovereigns, p. 420"
)

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Combat Scores, Damage "
    "Table, Wounds, Fatigue and Encumbrance, pp. 393, 403-406"
)
ANIMAL_SOURCE = "Grogs, Chapter Seven: Horses & Hounds, p. 137"
SIZE_SOURCE = "Ars Magica Definitive Edition, Chapter Three: Characters, Size, p. 26"

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


#: A disease's Disease Penalty by its stage (Art & Academe p. 46); a
#: Critical one allows no action at all.
DISEASE_PENALTIES = {"Minor": -1, "Serious": -3, "Major": -5, "Critical": -5}


def disease_penalty(wounds: Wounds) -> int:
    """The diseases' Disease Penalties together (none for one that gives
    Flaws instead)."""
    return sum(DISEASE_PENALTIES.get(d.level, 0) for d in wounds.diseases if d.penalty)


def wound_penalty(
    wounds: Wounds,
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
    *,
    diseases: bool = True,
) -> int:
    """The Wound Penalty, with bruises' and (unless `diseases` is False)
    Disease Penalties, which work as a wound's (Lords of Men p. 132; Art &
    Academe p. 46)."""
    bruises = wounds.bruises
    return _adjusted(
        wounds.light * WOUND_PENALTIES["light"]
        + wounds.medium * WOUND_PENALTIES["medium"]
        + wounds.heavy * WOUND_PENALTIES["heavy"]
        + sum(bruises.get(k, 0) * p for k, p in WOUND_PENALTIES.items())
        + (disease_penalty(wounds) if diseases else 0),
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
    """The Load the character carries: the armour worn and the weapons
    carried, times how many of each (DE p. 403). Other suits of armour,
    and weapons not carried, are kept elsewhere."""
    worn = worn_armour(inventory)
    return sum(
        item.load * max(item.quantity, 1)
        for item in inventory
        if (item.kind == "weapon" and item.carried) or item is worn
    )


def walking_pace(character: Character) -> int:
    """Paces a combat round at a walk: 10 + Quickness - Encumbrance (a
    hurry twice that, a run four times) (DE p. 395)."""
    load = carried_load(character.inventory)
    enc = encumbrance(load, character.characteristics.strength)
    return max(0, 10 + character.characteristics.quickness - enc)


def worn_armour(inventory: Sequence[Possession]) -> Possession | None:
    """The armour that protects best (a character wears one suit)."""
    armour = [item for item in inventory if item.kind == "armor"]
    return max(armour, key=lambda item: item.armor_protection, default=None)


def primitive_armour(character: Character, armour: Possession) -> bool:
    """Primitive Equipment in armour that isn't Inexpensive: -1 to its
    Protection (and to Initiative, rules.combat)."""
    if not any(vf.vf_id == "vf_primitive_equipment" for vf in character.virtues_flaws):
        return False
    from .. import catalog

    definition = catalog.load_armor_catalog_by_id().get(armour.gear_id or "")
    cost = definition.cost if definition is not None else armour.gear_quality
    return cost != "Inexpensive"


def soak(character: Character) -> Breakdown:
    """Stamina + armour Protection + Soak Virtues + the typed adjustment."""
    lines = [Line("Stamina", amount=character.characteristics.stamina, source=SOURCE)]
    total = character.characteristics.stamina
    if character.animal is not None and character.animal.protection:
        lines.append(
            Line(
                "Natural Protection",
                amount=character.animal.protection,
                source=ANIMAL_SOURCE,
            )
        )
        total += character.animal.protection
    armour = worn_armour(character.inventory)
    if armour is not None and armour.armor_protection:
        lines.append(Line(armour.name, amount=armour.armor_protection, source=SOURCE))
        total += armour.armor_protection
        made = equipment.quality_bonus(armour)
        if made:
            lines.append(
                Line(
                    f"{armour.make} armour",
                    amount=made,
                    source=equipment.QUALITY_SOURCE,
                )
            )
            total += made
        if primitive_armour(character, armour):
            lines.append(
                Line("Primitive Equipment (armour)", amount=-1, source="character")
            )
            total -= 1
    for effect in effects.collect([character_source(character.virtues_flaws)], "soak"):
        amount = effect.amount or 0
        lines.append(Line(effect.entry.name, amount=amount, source="character"))
        total += amount
    if any(vf.vf_id == "vf_guardian_angel" for vf in character.virtues_flaws):
        # The angel's +5, while the character does God's will (DE p. 84).
        lines.append(Line("Guardian Angel", amount=5, source=SOURCE))
        total += 5
    office = OFFICE_RESISTANCE.get(character.background.church_rank, 0) // 5
    if office:
        lines.append(
            Line(character.background.church_rank, amount=office, source=OFFICE_SOURCE)
        )
        total += office
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


def form_bonus(character: Character, form: str) -> int:
    """A magus's Form Bonus: the Form's score / 5, rounded up (DE p. 206).
    It adds to Soak against harm of that Form and, for Vim, to avoiding
    Twilight."""
    art = character.arts.get(form.lower())
    return round_up(art.level / 5) if art is not None and art.level > 0 else 0
