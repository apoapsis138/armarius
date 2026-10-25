"""A character's supernatural powers from the Virtues that grant them (DE
Chapter Four: Focus Power p. 81, Greater Power p. 84, Lesser Power p. 90,
Personal Power p. 102, Ritual Power p. 106).

Each power is like a Hermetic spell of its level, with Penetration bought
level for level (0 otherwise). What each Virtue gives:

- **Greater Power** (Major): 50 levels a Virtue, by default one power
  each; Initiative Quickness - magnitude / 2; one Fatigue level up to
  level 50, two to 100.
- **Lesser Power** (Minor): 25 levels a Virtue, shared among powers;
  Initiative Quickness - 2 x magnitude; a Fatigue level for each 25
  levels or part.
- **Personal Power** (Minor): 25 levels a Virtue, for a power of Personal
  Range or a constant one; Initiative Quickness - magnitude / 2; one
  Fatigue level up to 50, two to 100.
- **Ritual Power** (Major): 25 levels a Virtue, a Ritual-like power;
  Initiative Quickness - 2 x magnitude; a Fatigue level for each 25
  levels or part, and a Confidence Point a magnitude.
- **Focus Power** (Major): a pool of 25 points a Virtue: 2 a level of its
  greatest effect, 1 a point of Penetration; any effect within its narrow
  field up to that level; Initiative Quickness - that magnitude; a
  Fatigue level up to 25, two to 50, three to 75.

The Virtues may be taken more than once and their levels pooled.

Pattern: the kinds are a table (a Strategy as data): each says how its
levels are counted, its Initiative and its Fatigue, so a power's figures
never branch on its kind elsewhere.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..models import LESSER, Character, CharacterPower
from .rounding import round_down, round_up

SOURCE = "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, pp. 81-106"


def magnitude(level: int) -> int:
    """A level's magnitude: a fifth, rounded up (a level under 5 counts as
    one)."""
    return max(1, round_up(level / 5)) if level > 0 else 0


def _per_25(level: int) -> int:
    return max(1, round_up(level / 25))


def _half_band(level: int) -> int:
    return 1 if level <= 50 else 2


@dataclass(frozen=True)
class PowerKind:
    """One power-granting Virtue: its name, its catalog id, the levels (or
    points) each instance gives, how a power's cost against them is
    counted, its Initiative modifier from the magnitude, and its Fatigue
    from the level."""

    name: str
    vf_id: str
    page: int
    budget: int
    cost: Callable[[CharacterPower], int]
    initiative: Callable[[int], int]
    fatigue: Callable[[int], int]


def _levels(power: CharacterPower) -> int:
    return max(0, power.level) + max(0, power.penetration)


def _focus_points(power: CharacterPower) -> int:
    return 2 * max(0, power.level) + max(0, power.penetration)


KINDS: dict[str, PowerKind] = {
    k.name: k
    for k in (
        PowerKind(
            "Greater Power",
            "vf_greater_power",
            84,
            50,
            _levels,
            lambda m: -round_down(m / 2),
            _half_band,
        ),
        PowerKind(
            "Lesser Power",
            "vf_lesser_power",
            90,
            25,
            _levels,
            lambda m: -2 * m,
            _per_25,
        ),
        PowerKind(
            "Personal Power",
            "vf_personal_power",
            102,
            25,
            _levels,
            lambda m: -round_down(m / 2),
            _half_band,
        ),
        PowerKind(
            "Ritual Power",
            "vf_ritual_power",
            106,
            25,
            _levels,
            lambda m: -2 * m,
            _per_25,
        ),
        PowerKind(
            "Focus Power",
            "vf_focus_power",
            81,
            25,
            _focus_points,
            lambda m: -m,
            _per_25,
        ),
    )
}


def kind_of(power: CharacterPower) -> PowerKind:
    return KINDS.get(power.virtue, KINDS["Lesser Power"])


def virtues_held(character: Character, kind: PowerKind) -> int:
    """How many times the character has the kind's Virtue."""
    return sum(1 for vf in character.virtues_flaws if vf.vf_id == kind.vf_id)


def initiative(character: Character, power: CharacterPower) -> int:
    """Quickness less what the power's magnitude costs it."""
    return character.characteristics.quickness + kind_of(power).initiative(
        magnitude(power.level)
    )


def fatigue(power: CharacterPower) -> int:
    """The Fatigue levels one use costs."""
    return kind_of(power).fatigue(max(0, power.level))


def confidence(power: CharacterPower) -> int:
    """A Ritual Power's Confidence Points, one a magnitude (none for the
    others)."""
    return magnitude(power.level) if power.virtue == "Ritual Power" else 0


@dataclass
class Budget:
    """A kind's levels (points, for Focus Power) given and used."""

    kind: PowerKind
    given: int
    used: int

    @property
    def over(self) -> int:
        return max(0, self.used - self.given)


def budgets(character: Character) -> list[Budget]:
    """Each power-granting Virtue the character has or uses, with its
    levels given (per instance) and used by its powers."""
    found: list[Budget] = []
    for kind in KINDS.values():
        held = virtues_held(character, kind)
        mine = [p for p in character.powers if kind_of(p) is kind]
        if held or mine:
            found.append(
                Budget(kind, kind.budget * held, sum(kind.cost(p) for p in mine))
            )
    return found


def problems(character: Character) -> list[str]:
    """What breaks the Virtues' rules: levels beyond what they give, a
    power with no Virtue for it, more Greater Powers than Greater Power
    Virtues, a Personal Power neither Personal Range nor constant (DE pp.
    81-106)."""
    found: list[str] = []
    for budget in budgets(character):
        name, unit = (
            budget.kind.name,
            ("points" if budget.kind.name == "Focus Power" else "levels"),
        )
        if not budget.given:
            found.append(f"No {name} Virtue for its powers (DE p. {budget.kind.page}).")
        elif budget.over:
            found.append(
                f"{name}: {budget.used} {unit} used of {budget.given} (DE p. "
                f"{budget.kind.page})."
            )
    greater = KINDS["Greater Power"]
    count = sum(1 for p in character.powers if p.virtue == greater.name)
    held = virtues_held(character, greater)
    if held and count > held:
        found.append(
            f"Greater Power: {count} powers for {held} Virtue(s); one each unless "
            "the troupe allows a strong link (DE p. 84)."
        )
    for p in character.powers:
        if p.virtue == "Personal Power" and not (
            p.constant or p.range.strip().casefold() == "personal"
        ):
            found.append(
                f"{p.name or 'A Personal Power'}: must be Range Personal or "
                "constant (DE p. 102)."
            )
    return found


# -- items a Virtue gives --

#: The Virtues that give a character enchanted items at creation, by the
#: name a device's "Had by a Virtue" uses (DE pp. 97-98, 105).
MINOR_ENCHANTMENTS, MASTERPIECE, REDCAP = "Minor Enchantments", "Masterpiece", "Redcap"
ITEM_VIRTUES = (MINOR_ENCHANTMENTS, MASTERPIECE, REDCAP)
_ITEM_VF = {
    MINOR_ENCHANTMENTS: "vf_minor_enchantments",
    MASTERPIECE: "vf_masterpiece",
    REDCAP: "vf_redcap",
}
MINOR_ENCHANTMENT_LEVELS, MINOR_ENCHANTMENT_MOST = 25, 30
REDCAP_LEVELS = 50


def item_problems(
    character: Character, devices: list[tuple[str, list[int], str]]
) -> list[str]:
    """What breaks the item Virtues' rules, from the character's devices
    as (granted_by, each effect's modified level, device type): Minor
    Enchantments' 25 levels a Virtue and no power over 30; one Masterpiece,
    a lesser enchantment; a Redcap's 50 levels; an item claimed by a
    Virtue the character hasn't (DE pp. 97-98, 105)."""
    found: list[str] = []
    held = {
        name: sum(1 for vf in character.virtues_flaws if vf.vf_id == vf_id)
        for name, vf_id in _ITEM_VF.items()
    }
    for name in ITEM_VIRTUES:
        mine = [d for d in devices if d[0] == name]
        if mine and not held[name]:
            found.append(f"No {name} Virtue for its items.")
    minor = [lv for g, levels, _ in devices if g == MINOR_ENCHANTMENTS for lv in levels]
    if minor and held[MINOR_ENCHANTMENTS]:
        allowed = MINOR_ENCHANTMENT_LEVELS * held[MINOR_ENCHANTMENTS]
        if sum(minor) > allowed:
            found.append(
                f"Minor Enchantments: {sum(minor)} levels of {allowed} (DE p. 98)."
            )
        if max(minor) > MINOR_ENCHANTMENT_MOST:
            found.append(
                f"Minor Enchantments: no power over level {MINOR_ENCHANTMENT_MOST} "
                f"({max(minor)}) (DE p. 98)."
            )
    master = [d for d in devices if d[0] == MASTERPIECE]
    if len(master) > 1 or any(t != LESSER for *_, t in master):
        found.append("Masterpiece: one lesser enchanted item (DE p. 97).")
    redcap = sum(lv for g, levels, _ in devices if g == REDCAP for lv in levels)
    if redcap > REDCAP_LEVELS:
        found.append(f"Redcap: {redcap} levels of {REDCAP_LEVELS} (DE p. 105).")
    return found
