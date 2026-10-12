"""Shared types, constants and the Modifier record every model uses."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Literal

from ..totals import validate_modifier_type

#: A Mythic Companion is a companion with a Free Mythic Companion Virtue
#: (DE ch. 4): it counts as a companion except where Virtues and Flaws are
#: chosen (see COMPANION_TYPES).
CharacterType = Literal["magus", "companion", "mythic companion", "grog"]
#: The character types that count as a companion (Covenant Inhabitants).
COMPANION_TYPES: tuple[str, ...] = ("companion", "mythic companion")
VirtueFlawType = Literal["Virtue", "Flaw"]
#: A character catalog entry's type: Qualities and Inferiorities are the
#: non-human counterparts of Virtues and Flaws (RoP:Magic magic characters,
#: HoH:Mystery Cults animals and heartbeasts).
CharacterVirtueFlawType = Literal["Virtue", "Flaw", "Quality", "Inferiority"]
VirtueFlawTier = Literal["Free", "Minor", "Major"]
BoonHookType = Literal["Boon", "Hook"]
Handedness = Literal["right", "left", "ambidextrous"]
FatigueLevel = Literal["fresh", "winded", "weary", "tired", "dazed", "unconscious"]

#: Display order for the Fatigue Levels track on the character sheet, from
#: least to most fatigued -- Fresh -> Winded -> Weary -> Tired -> Dazed ->
#: Unconscious. Not enforced anywhere (see FatigueLevel), just the order a
#: picker or display should list them in.
FATIGUE_LEVELS: tuple[FatigueLevel, ...] = (
    "fresh",
    "winded",
    "weary",
    "tired",
    "dazed",
    "unconscious",
)

# Point magnitude for each tier, per the core rules: Major Virtues cost, and
# Major Flaws grant, three points; Minor is one point; Free is zero either
# way. A catalog entry's `cost` sign follows `type` (positive for a Virtue's
# cost, negative for a Flaw's grant) but must match this magnitude for its
# `tier` -- enforced in VirtueFlawDef.__post_init__ so a typo in the catalog
# JSON fails loudly at load time instead of silently giving a wrong total.
VIRTUE_FLAW_TIER_COST: dict[str, int] = {"Free": 0, "Minor": 1, "Major": 3}

#: The side of the ledger each character catalog type falls on: a Quality
#: is bought like a Virtue and listed with them, an Inferiority with Flaws.
VIRTUE_FLAW_SIDE: dict[str, VirtueFlawType] = {
    "Virtue": "Virtue",
    "Quality": "Virtue",
    "Flaw": "Flaw",
    "Inferiority": "Flaw",
}

#: The kinds of character a Virtue/Flaw can be restricted to
#: (VirtueFlawDef.audience); an entry with no audience is for anyone. All
#: but the last are non-human; "mythic companion" marks the Free Virtues
#: that make a character a Mythic Companion (Devil Child, Nephilim...).
VIRTUE_FLAW_AUDIENCES: tuple[str, ...] = (
    "faerie",
    "magic being",
    "corrupted beast",
    "animal",
    "mythic companion",
)


def known_fields(cls: type, data: dict[str, Any]) -> dict[str, Any]:
    """`data` filtered down to keys that are still fields of `cls`, so
    `cls(**known_fields(cls, data))` tolerates a stale key from an older save
    (a field since removed) instead of raising a TypeError."""
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in names}


SEASONS: tuple[str, ...] = ("Spring", "Summer", "Autumn", "Winter")

#: The four realms an aura or a power can belong to (DE Chapter Twelve).
REALMS: tuple[str, ...] = ("Magic", "Divine", "Faerie", "Infernal")

#: The 8 "Laboratory Characteristics" (ArM5 Covenants, Chapter 9) -- unlike human
#: Characteristics these start at 0 and are cheap to change. Each name here
#: doubles as a LabCharacteristics field name and a `lab_characteristic`
#: Modifier's target.
LAB_CHARACTERISTICS: tuple[str, ...] = (
    "size",
    "refinement",
    "general_quality",
    "upkeep",
    "safety",
    "warping",
    "health",
    "aesthetics",
)
ABILITY_CATEGORIES: tuple[str, ...] = (
    "General",
    "Academic",
    "Martial",
    "Arcane",
    "Supernatural",
    # A hedge tradition's Arts (Hedge Magic): learned like Supernatural
    # Abilities, advanced on the Ability xp table.
    "Hedge Art",
)
#: The Ability categories that are supernatural powers: a Virtue grants
#: them, and they mark their holder as more than mundane.
SUPERNATURAL_CATEGORIES: tuple[str, ...] = ("Supernatural", "Hedge Art")


@dataclass
class Modifier:
    """A structured effect a Virtue/Flaw has on a Total or resource flow.

    `applies_to` names a modifier type from totals.MODIFIER_TYPES (e.g.
    "lab_total", "casting_total", "study_total", "aging_roll", "art_xp_gain").
    `target` optionally narrows the modifier to a specific Art/Ability named
    by one of the catalog entry's `parameters` (e.g. "{art}"); a target
    ending in "*" covers every name it begins ("Craft: *").

    `activity` optionally narrows it further to one specific activity within
    that type -- e.g. two modifiers both applying to "lab_total" but one
    scoped to "invent_spells" and the other to "extract_vis", each with its
    own amount. A single Virtue/Flaw can carry several such modifiers (it's
    a list on VirtueFlawDef), so different amounts for different activities
    from the same source are just multiple Modifier entries, disambiguated
    by `activity`. See totals.ACTIVITIES_BY_TYPE for the valid activities
    per type; both fields are validated against that registry so a typo or
    an unmodeled type/activity fails loudly at load time rather than
    silently disappearing from a future totals calculation.
    """

    applies_to: str
    amount: float | None = None
    multiplier: float | None = None
    target: str | None = None
    activity: str | None = None
    #: Applies only when the instance's parameters have these values
    #: ({"realm": "divine"}): an entry whose effect depends on a choice
    #: (Student of (Realm), a Faerie Blood's heritage) carries one modifier
    #: per choice.
    when: dict[str, str] | None = None

    def __post_init__(self) -> None:
        validate_modifier_type(self.applies_to, self.activity)


def _validate_vf_tier_cost(id_: str, tier: str, cost: float) -> None:
    """Shared by VirtueFlawDef and LabVirtueFlawDef: cost's magnitude must
    match VIRTUE_FLAW_TIER_COST[tier] (0/1/3 for Free/Minor/Major)."""
    if tier not in VIRTUE_FLAW_TIER_COST:
        raise ValueError(
            f"Unknown tier {tier!r} for {id_!r}; "
            f"must be one of {sorted(VIRTUE_FLAW_TIER_COST)}"
        )
    expected_magnitude = VIRTUE_FLAW_TIER_COST[tier]
    if abs(cost) != expected_magnitude:
        raise ValueError(
            f"{id_!r} is {tier!r} tier (should cost "
            f"{expected_magnitude} points) but has cost {cost!r}"
        )
