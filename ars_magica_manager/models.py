"""Data model for sagas, covenants, characters, laboratories, and books.

See DESIGN.md sections 4-6 for the entity relationships and the reasoning
behind the Virtue/Flaw modifier system.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, fields
from typing import Any, Literal

from .arts import ART_BY_NAME, ARTS, TECHNIQUES
from .rules import xp as xp_rules
from .totals import validate_modifier_type

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
    by one of the catalog entry's `parameters` (e.g. "{art}").

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


@dataclass
class VirtueFlawDef:
    """A character Virtue/Flaw catalog entry (shared reference data, not
    per-saga). The field-by-field reference, with every source book's
    version, is reference/virtues-and-flaws-reference.md.

    `category` is the first type the book prints (General, Hermetic,
    Supernatural...); `extra_categories` holds any others ("Supernatural,
    Tainted" is category Supernatural plus ["Tainted"]). An entry the book
    lets you take as Major or Minor is two entries, one per tier.

    `repeatable` marks entries whose text lets a character take them more
    than once; `max_count` is the most copies a character may hold, when
    the book gives one, and `max_per_parameter` the most copies that may
    share the same `params` (1: "a different Ability each time"; Great
    Characteristic allows 2; None: no limit, as when a power Virtue's
    levels pool into one power). Each copy is its own VirtueFlawInstance.

    `source` names the book(s) the entry comes from ("DE", "DE; RoP:F",
    "HoH:MC"), for attribution -- the text is CC-BY-SA -- and for choosing
    the books in play. `summary` is a one-line paraphrase for
    searching. `audience` restricts the entry to non-human characters or
    Mythic Companions (VIRTUE_FLAW_AUDIENCES); empty means anyone may take
    it. The picker hides what a character can't take (VirtueFlawChooser).
    """

    id: str
    name: str
    type: CharacterVirtueFlawType
    category: str
    tier: VirtueFlawTier
    cost: float
    parameters: list[str] = field(default_factory=list)
    modifiers: list[Modifier] = field(default_factory=list)
    description: str = ""
    extra_categories: list[str] = field(default_factory=list)
    repeatable: bool = False
    max_count: int | None = None
    max_per_parameter: int | None = 1
    source: str = ""
    summary: str = ""
    audience: list[str] = field(default_factory=list)
    #: What grants the entry by rule rather than purchase ("familiar_bond":
    #: binding a familiar gives both partners True Friend).
    granted_by: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_vf_tier_cost(self.id, self.tier, self.cost)
        if self.type not in VIRTUE_FLAW_SIDE:
            raise ValueError(f"Unknown type {self.type!r} for {self.id!r}")
        if (self.side == "Virtue" and self.cost < 0) or (
            self.side == "Flaw" and self.cost > 0
        ):
            raise ValueError(
                f"{self.id!r}: a {self.type} must have cost "
                f"{'>= 0' if self.side == 'Virtue' else '<= 0'}, not {self.cost!r}"
            )
        if self.max_count is not None and not self.repeatable:
            raise ValueError(f"{self.id!r}: max_count needs repeatable")
        if self.max_per_parameter is not None and self.max_per_parameter < 1:
            raise ValueError(f"{self.id!r}: max_per_parameter must be at least 1")
        for who in self.audience:
            if who not in VIRTUE_FLAW_AUDIENCES:
                raise ValueError(
                    f"Unknown audience {who!r} for {self.id!r}; "
                    f"must be one of {VIRTUE_FLAW_AUDIENCES}"
                )

    @property
    def side(self) -> VirtueFlawType:
        """ "Virtue" for a Virtue or Quality, "Flaw" for a Flaw or Inferiority."""
        return VIRTUE_FLAW_SIDE[self.type]

    @property
    def category_label(self) -> str:
        """Every printed type, as the book prints them: "Supernatural, Tainted"."""
        return ", ".join([self.category, *self.extra_categories])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VirtueFlawDef:
        d = dict(data)
        d["modifiers"] = [
            Modifier(**known_fields(Modifier, m)) for m in d.get("modifiers", [])
        ]
        return cls(**known_fields(cls, d))


@dataclass
class LabVirtueFlawDef:
    """A catalog entry for a Laboratory Virtue/Flaw (ArM5 Covenants, Chapter 9) --
    shared reference data, not per-saga. Distinct from VirtueFlawDef:
    labs have their own separate Virtues & Flaws list, not the character
    one (a lab and a magus are different "characters" with different
    catalogs, even though both use Free/Minor/Major tiers).

    `modifiers` carries its effects in the shared Modifier shape (DESIGN.md
    section 5.1): an effect on a Characteristic is a `lab_characteristic`
    modifier whose `target` names one of LAB_CHARACTERISTICS (Superior
    Construction: Safety +1, Aesthetics +1). They feed the virtue/flaw
    component of each Characteristic's manual + virtue_sum + flaw_sum =
    total (laboratories.lab_characteristic_total).
    A Specialization grant is a `lab_specialization` modifier:
    its `target` names the Specialization, or is "{specialization}" when the
    lab's owner picks it from `choices["specialization"]` as the Virtue is
    added (the pick is the instance's params). Grants the book leaves to
    distribute ("2 points on any Specialization(s)") stay prose, entered as
    LabSpecialtyEntry sources.

    `repeatable` marks the (asterisked in the book) entries a lab can hold
    more than once -- e.g. two Lesser Features -- so the picker shouldn't
    exclude them just because one's already attached.
    """

    id: str
    name: str
    type: VirtueFlawType
    category: str
    tier: VirtueFlawTier
    cost: float
    repeatable: bool = False
    modifiers: list[Modifier] = field(default_factory=list)
    #: A parameter the lab's owner chooses -> the values allowed.
    choices: dict[str, list[str]] = field(default_factory=dict)
    description: str = ""
    #: The book(s) it's from (sourcebooks); every entry so far is Covenants'.
    source: str = "Covenants"

    def __post_init__(self) -> None:
        _validate_vf_tier_cost(self.id, self.tier, self.cost)
        for options in self.choices.values():
            unknown = set(options) - set(LAB_SPECIALIZATIONS)
            if unknown:
                raise ValueError(f"Unknown Specializations {unknown} for {self.id!r}")
        for modifier in self.modifiers:
            if modifier.applies_to == "lab_specialization" and not (
                modifier.target in LAB_SPECIALIZATIONS
                or modifier.target == "{specialization}"
                and "specialization" in self.choices
            ):
                raise ValueError(
                    f"Unknown Specialization {modifier.target!r} for {self.id!r}"
                )
            if (
                modifier.applies_to == "lab_characteristic"
                and modifier.target not in LAB_CHARACTERISTICS
            ):
                raise ValueError(
                    f"Unknown Lab Characteristic {modifier.target!r} for "
                    f"{self.id!r}; must be one of {LAB_CHARACTERISTICS}"
                )

    @property
    def specialization_grants(self) -> list[tuple[str, float]]:
        """Its Specialization grants as (Specialization or "{specialization}"
        for a choice, points), in catalog order."""
        return [
            (m.target or "", m.amount or 0)
            for m in self.modifiers
            if m.applies_to == "lab_specialization"
        ]

    @property
    def characteristic_modifiers(self) -> dict[str, float]:
        """Its flat effects on the Characteristics, {characteristic: amount}
        in catalog order (read from `modifiers`)."""
        amounts: dict[str, float] = {}
        for modifier in self.modifiers:
            if modifier.applies_to == "lab_characteristic" and modifier.target:
                amounts[modifier.target] = amounts.get(modifier.target, 0) + (
                    modifier.amount or 0
                )
        return amounts

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabVirtueFlawDef:
        d = dict(data)
        # Older saves held the effects as a {characteristic: amount} map.
        legacy = d.pop("characteristic_modifiers", None) or {}
        d["modifiers"] = [
            Modifier(**known_fields(Modifier, m)) for m in d.get("modifiers", [])
        ] + [
            Modifier(applies_to="lab_characteristic", target=c, amount=amount)
            for c, amount in legacy.items()
        ]
        return cls(**known_fields(cls, d))


#: The "types" the Covenants book (Chapter Two: Boons & Hooks) sorts every
#: Boon and Hook into, in the order the book lists them.
COVENANT_BOON_HOOK_CATEGORIES: tuple[str, ...] = (
    "Site",
    "Fortifications",
    "Resources",
    "Residents",
    "External Relations",
    "Surroundings",
)


@dataclass
class CovenantBoonHookDef:
    """A catalog entry for a covenant Boon or Hook (ArM5 Chapter 6) --
    shared reference data, not per-saga. They work like Virtues & Flaws:
    Hooks are the Flaw-like story features and provide points (cost < 0),
    Boons are the Virtue-like advantages and spend them (cost > 0), in the
    same Free/Minor/Major tiers costing 0/1/3. The same name can appear as
    both a Boon and a Hook, and at both tiers (Regio, for one), so ids
    carry type and tier.

    `category` is the entry's type from the Covenants book (one of
    COVENANT_BOON_HOOK_CATEGORIES: Site, Fortifications, Resources, Residents,
    External Relations, Surroundings), or "" for the rare entry the book does
    not file under one (the Unknown Hook). The book's "Free Choices" -- options
    with no cost that don't count toward balancing -- are stored as Free-tier
    Boons (cost 0). One entry can carry only one category, so an entry the
    book lists under two (the Major Monster Hook) takes one of them.

    `requires` and `excludes` list other catalog ids (Shell Keep requires the
    Major Castle Hook; Seclusion excludes the Road and Urban Hooks). They are
    recorded for display and future use only -- nothing enforces them yet.

    `modifiers` are the entry's structured effects, in the same `Modifier`
    shape Virtues & Flaws use (DESIGN.md section 5): the Minor Aura Boon is
    `covenant_aura` +1, Shell Keep is `covenant_expense`/`buildings` +2.
    Everything else stays prose in `description`. `repeatable` marks entries
    that may be taken more than once; each instance's effects count (they
    stack) -- see covenants.covenant_modifiers(). `max_count` is the most
    times a repeatable entry may be taken, when the book gives one (Aura:
    seven). `requires_any` lists entries of which the covenant needs at
    least one (Magical Soldiers: any other kind of soldier), recorded like
    `requires`.

    `unknown` marks the Minor Hooks the book says "may be Unknown": an
    attached one can then be marked Unknown (BOON_HOOK_UNKNOWN) and counts
    3 points. `source` names the book(s) the entry comes from ("ArM5",
    "Covenants" or "ArM5; Covenants"), for attribution -- the text is
    CC-BY-SA. The field-by-field reference, with the rules text, is
    reference/covenants-boons-and-hooks-ref.md.
    """

    id: str
    name: str
    type: BoonHookType
    tier: VirtueFlawTier
    cost: float
    category: str = ""
    repeatable: bool = False
    requires: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)
    modifiers: list[Modifier] = field(default_factory=list)
    description: str = ""
    max_count: int | None = None
    requires_any: list[str] = field(default_factory=list)
    unknown: bool = False
    source: str = ""
    #: A "Style of Governance" Boon (Autocracy, Council...), listed on the
    #: Inhabitants tab.
    governance: bool = False

    def __post_init__(self) -> None:
        _validate_vf_tier_cost(self.id, self.tier, self.cost)
        if self.max_count is not None and not self.repeatable:
            raise ValueError(f"{self.id!r}: max_count needs repeatable")
        if self.category and self.category not in COVENANT_BOON_HOOK_CATEGORIES:
            raise ValueError(
                f"Unknown category {self.category!r} for {self.id!r}; "
                f"must be one of {COVENANT_BOON_HOOK_CATEGORIES} (or empty)"
            )
        if self.type not in ("Boon", "Hook"):
            raise ValueError(f"Unknown type {self.type!r} for {self.id!r}")
        if (self.type == "Boon" and self.cost < 0) or (
            self.type == "Hook" and self.cost > 0
        ):
            raise ValueError(
                f"{self.id!r}: Boons cost points (cost >= 0) and Hooks provide "
                f"them (cost <= 0), but this {self.type} has cost {self.cost!r}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CovenantBoonHookDef:
        d = dict(data)
        # Each Modifier checks its applies_to/activity against the registry
        # in totals.py, so a typo in the catalog fails at load time.
        d["modifiers"] = [
            Modifier(**known_fields(Modifier, m)) for m in d.get("modifiers", [])
        ]
        return cls(**known_fields(cls, d))


@dataclass
class CovenantSituationDef:
    """A Covenant Situation: one of the books' ready-made sets
    of Boons and Hooks for a new covenant. `entries` are the Boons, Hooks
    and Free Choices it adds: each a catalog id (`vf_id`), an optional
    `detail` ("Hall Keep") and a `count` when it's taken more than once.
    `notes` says where the book's own list was read differently (an entry
    it files on the wrong side, or one the catalog lacks)."""

    id: str
    name: str
    #: The book it's from (sourcebooks): "DE" or "Covenants".
    source: str = "ArM5"
    description: str = ""
    entries: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CovenantSituationDef:
        return cls(**known_fields(cls, data))


@dataclass
class AbilityDef:
    """A catalog entry for an Ability name (shared reference data, not per-saga).

    Some Abilities are really a family with a blank to fill in -- "Craft:
    {craft}", "Area Lore: {region}", "Language: {language}" -- named the
    same way Virtue/Flaw templating works. `parameters` lists which
    placeholders `name` contains; resolve them with resolve_ability_name()
    in catalog.py.
    """

    id: str
    name: str
    category: str
    parameters: list[str] = field(default_factory=list)
    description: str = ""
    #: The book(s) it's from (sourcebooks); every entry so far is the core
    #: book's.
    source: str = "ArM5"

    def __post_init__(self) -> None:
        if self.category not in ABILITY_CATEGORIES:
            raise ValueError(
                f"Unknown ability category {self.category!r}; "
                f"must be one of {ABILITY_CATEGORIES}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AbilityDef:
        return cls(**known_fields(cls, data))


@dataclass
class HouseDef:
    """A catalog entry for one of the 12 Hermetic Houses (shared reference
    data, not per-saga), with the benefit its members get at character
    creation."""

    id: str
    name: str
    description: str = ""
    #: The book it's from (sourcebooks): the core book.
    source: str = "ArM5"
    #: What membership gives at character creation, as the book's Hermetic
    #: Houses Summary words it.
    benefit: str = ""
    #: The free House Virtue: the Virtues a member takes one of (a
    #: VirtueFlawInstance's vf_id and params each). Empty when the benefit
    #: isn't a named Virtue (see `free`).
    virtues: list[dict[str, Any]] = field(default_factory=list)
    #: The Ability a Mystery Cult House's Virtue starts at a score of 1.
    ability: str = ""
    #: A benefit that isn't a named Virtue: "minor_virtue" (Jerbiton: any
    #: one Minor Virtue) or "ex_miscellanea" (a free Minor Hermetic Virtue,
    #: a free Major non-Hermetic Virtue and a compulsory Major Hermetic
    #: Flaw, all on top of the normal allowance).
    free: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HouseDef:
        return cls(**known_fields(cls, data))


@dataclass
class CharacterTemplateDef:
    """A ready-to-play character from the book's Character Templates
    (character_template_catalog.json), in the book's notation:
    scores, not xp. "{area}", "{second_area}" and "{language}" in an
    Ability name are asked for when the template is used."""

    id: str
    name: str
    type: CharacterType
    #: A magus's House (a house_catalog.json id).
    house: str | None = None
    characteristics: dict[str, int] = field(default_factory=dict)
    #: Aging Points per Characteristic (the book's "+1 (1)").
    aging_points: dict[str, int] = field(default_factory=dict)
    size: int = 0
    age: int = 0
    apparent_age: int = 0
    #: [score, points past it] for Decrepitude, Warping and Confidence.
    decrepitude: list[int] = field(default_factory=lambda: [0, 0])
    warping: list[int] = field(default_factory=lambda: [0, 0])
    confidence: list[int] = field(default_factory=lambda: [0, 0])
    #: Each {"vf_id", "params"}, plus the book's detail as "note" for an
    #: entry with no parameter for it, and "free" for a House's free Virtue.
    virtues_flaws: list[dict[str, Any]] = field(default_factory=list)
    #: [name, score] each.
    personality_traits: list[list[Any]] = field(default_factory=list)
    reputations: list[list[Any]] = field(default_factory=list)
    #: Each {"name", "score"}, with "xp" (toward the next score) and
    #: "specialty" when the book gives them. The score excludes a Puissant
    #: bonus, which comes from the Virtue.
    abilities: list[dict[str, Any]] = field(default_factory=list)
    #: Art -> {"score", "xp"?}, Arts at 0 left out.
    arts: dict[str, dict[str, int]] = field(default_factory=dict)
    #: Each {"spell_id"}, or a version of a catalog spell the catalog lacks:
    #: {"name", "level", "version_of"}.
    spells: list[dict[str, Any]] = field(default_factory=list)
    #: Each {"kind": "weapon"|"armor", "gear_id", "full"?} or
    #: {"kind": "item", "name"}.
    equipment: list[dict[str, Any]] = field(default_factory=list)
    #: The book's Customization Notes, condensed.
    notes: str = ""
    #: Where this entry differs from the page's text, and why.
    fixes: list[str] = field(default_factory=list)
    source: str = "ArM5"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CharacterTemplateDef:
        return cls(**known_fields(cls, data))


#: The book's weapon tables a WeaponDef comes from, in its order.
WEAPON_TABLES: tuple[str, ...] = ("melee", "missile", "natural")


@dataclass
class WeaponDef:
    """A catalog weapon (weapon_armor_catalog.json): one row of the book's
    Melee, Missile or Natural Weapons table (`table`, one of WEAPON_TABLES).
    The figures are the book's modifiers, None where it says n/a.
    `strength` is the minimum Strength to use it, `range` the range
    increment in paces (missile weapons) and `cost` one of GEAR_QUALITIES
    (None: it has none, e.g. a Fist or a natural weapon)."""

    id: str
    name: str
    table: str
    ability: str
    init: int
    attack: int | None
    defense: int
    damage: int | None
    strength: int | None = None
    load: int | None = None
    cost: str | None = None
    range: int | None = None
    description: str = ""
    source: str = ""

    def __post_init__(self) -> None:
        if self.table not in WEAPON_TABLES:
            raise ValueError(f"Unknown weapon table {self.table!r} for {self.id!r}")
        if self.cost is not None and self.cost not in GEAR_QUALITIES:
            raise ValueError(f"Unknown cost {self.cost!r} for {self.id!r}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WeaponDef:
        return cls(**known_fields(cls, data))


@dataclass
class ArmorDef:
    """A catalog armor Material (weapon_armor_catalog.json): its Protection
    (bonus to Soak) and Load as partial and as full armor -- full is None
    for a material that only comes partial -- and its cost (one of
    GEAR_QUALITIES)."""

    id: str
    name: str
    partial_protection: int
    partial_load: int
    full_protection: int | None
    full_load: int | None
    cost: str
    description: str = ""
    source: str = ""

    def __post_init__(self) -> None:
        if self.cost not in GEAR_QUALITIES:
            raise ValueError(f"Unknown cost {self.cost!r} for {self.id!r}")

    def figures(self, full: bool) -> tuple[int, int] | None:
        """(Protection, Load) as full or partial armor; None if the
        material doesn't come that way."""
        if not full:
            return self.partial_protection, self.partial_load
        if self.full_protection is None or self.full_load is None:
            return None
        return self.full_protection, self.full_load

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArmorDef:
        return cls(**known_fields(cls, data))


@dataclass
class VirtueFlawInstance:
    """A catalog Virtue/Flaw as attached to a specific Character or Laboratory.

    `id` tells apart two instances of the same Virtue (a lab's two Lesser
    Features), so a LabFeature can point at its own. A laboratory's
    instances always have one (given at load and when added); a character's
    are left "". It isn't compared: two instances of the same Virtue with
    the same params are equal."""

    vf_id: str
    params: dict[str, str] = field(default_factory=dict)
    id: str = field(default="", compare=False)


def new_instance_id() -> str:
    """A fresh id for a VirtueFlawInstance or LabFeature."""
    return uuid.uuid4().hex[:12]


@dataclass
class Characteristics:
    intelligence: int = 0
    perception: int = 0
    strength: int = 0
    stamina: int = 0
    presence: int = 0
    communication: int = 0
    dexterity: int = 0
    quickness: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Characteristics:
        return cls(**known_fields(cls, data))


@dataclass
class Ability:
    """An Ability: its total xp is stored and its score derived from it
    (rules.xp)."""

    name: str
    category: str = "General"
    xp: int = 0
    specialty: str | None = None

    @property
    def level(self) -> int:
        """The score the xp buys."""
        return xp_rules.score_from_xp(self.xp, xp_rules.ABILITY_FACTOR)

    @property
    def progress(self) -> xp_rules.Progress:
        return xp_rules.progress(self.xp, xp_rules.ABILITY_FACTOR)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ability:
        d = dict(data)
        if "score" in d and "level" not in d:
            # Pre-Phase-1b saves used "score".
            d["level"] = d.pop("score")
        d.pop("xp_to_next", None)  # typed by hand in older saves
        if "level" in d:
            # Older saves typed the score beside the xp.
            d["xp"], _ = xp_rules.migrate_level_xp(
                d.pop("level"), d.get("xp", 0), xp_rules.ABILITY_FACTOR
            )
        return cls(**known_fields(cls, d))


@dataclass
class Spell:
    """A Hermetic spell. The shared catalog (data/spell_catalog.json) holds the
    published ones; `Saga.spells` holds the saga's own (added by hand or
    imported); a magus's `Character.invented_spells` holds theirs. All share
    one id namespace -- spells.find_spell() resolves an id from any of them.

    `level` is None for a General-level spell (the Aegis of the Hearth, the
    Wards), which is cast at any level. Range/Duration/Target are plain
    strings: the core values (SPELL_RANGES etc.) or a supplement's own.
    `requisites` are extra Arts (Techniques or Forms) the spell also needs.
    Magnitude, the "CrIg 20" shorthand and a Ritual's vis cost and casting time
    are worked out in spells.py, never stored."""

    id: str
    name: str
    technique: str
    form: str
    level: int | None = None
    description: str = ""
    requisites: list[str] = field(default_factory=list)
    range: str = ""
    duration: str = ""
    target: str = ""
    ritual: bool = False
    #: The guideline level before Range/Duration/Target (None if not given).
    base_level: int | None = None
    #: Where it's published: a sourcebooks.SOURCEBOOKS abbreviation, or free
    #: text for the saga's own spells.
    source: str = "ArM5"
    #: The page of `source` it's printed on ("" if not known).
    page: str = ""
    #: Side effects and modified effects from the experiment that invented
    #: it: anyone who learns it learns them too.
    experimental_effects: list[str] = field(default_factory=list)
    #: A catalog entry listed without its details (the source page lacks them).
    details_missing: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Spell:
        return cls(**known_fields(cls, data))


@dataclass
class MasteryAbility:
    """One Mastery Ability a magus has bought on a known spell (Fast
    Casting, Penetration, ...) -- its own name/level/xp, since some (e.g.
    Multiple Casting) carry a score that matters. No catalog or rules
    validation yet (see DESIGN.md's "tracker, not rules engine" stance)."""

    name: str
    level: int = 0
    xp: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MasteryAbility:
        return cls(**known_fields(cls, data))


@dataclass
class KnownSpell:
    """One spell a character knows, plus their Spell Mastery in it (ArM5
    Chapter Seven): a score/xp track and the Mastery Abilities bought with
    it. `spell_id` resolves through spells.find_spell() like any other
    spell reference (catalog, saga's own, or the magus's invented spells)."""

    spell_id: str
    mastery_score: int = 0
    mastery_xp: int = 0
    mastery_abilities: list[MasteryAbility] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnownSpell:
        d = dict(data)
        d["mastery_abilities"] = [
            MasteryAbility.from_dict(m) for m in d.get("mastery_abilities", [])
        ]
        return cls(**known_fields(cls, d))


#: Standard Hermetic Ranges, Durations and Targets (ArM5 Chapter Nine), in the
#: book's order. Supplements add their own (Road, Bargain...), kept as typed.
SPELL_RANGES: tuple[str, ...] = (
    "Personal",
    "Touch",
    "Eye",
    "Voice",
    "Sight",
    "Arcane Connection",
)
SPELL_DURATIONS: tuple[str, ...] = (
    "Momentary",
    "Concentration",
    "Diameter",
    "Sun",
    "Ring",
    "Moon",
    "Year",
)
SPELL_TARGETS: tuple[str, ...] = (
    "Individual",
    "Circle",
    "Part",
    "Group",
    "Room",
    "Structure",
    "Boundary",
    "Taste",
    "Touch",
    "Smell",
    "Hearing",
    "Vision",
)
#: The kinds of book a library holds (reference/Libraries.md).
BOOK_TYPES: tuple[str, ...] = (
    "Art Summa",
    "Ability Summa",
    "Tractatus",
    "Lab Text",
    "Casting Tablet",
    "Other",
)
#: What a Lab Text records (`Book.text_kind`): a spell, an
#: enchanted device's effect, a Longevity Ritual, or anything else (a tamed
#: creature, a Discovery, a familiar's bond power).
TEXT_SPELL = "Spell"
TEXT_ENCHANTMENT = "Enchantment"
TEXT_LONGEVITY = "Longevity Ritual"
TEXT_OTHER = "Other"
LAB_TEXT_KINDS: tuple[str, ...] = (
    TEXT_SPELL,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_OTHER,
)
#: What a Tractatus is written on.
TRACTATUS_SUBJECTS: tuple[str, ...] = ("Art", "Ability")
#: Who can own a book (`Book.owner_kind`). A book with no owner is unassigned
#: and files under the saga.
BOOK_OWNER_KINDS: tuple[str, ...] = ("covenant", "laboratory", "character")


@dataclass
class Book:
    """One book. Fields a type doesn't use stay blank: `art` is for Art Summae
    and Art Tractatus, `ability` for Ability Summae and Ability Tractatus,
    `spell_id`/`spell_name` for Lab Texts and Casting Tablets. The Build Point
    cost is always calculated (books.cost)."""

    id: str
    name: str
    type: str  # one of BOOK_TYPES
    language: str = "Latin"
    author: str = ""
    owner_kind: str | None = None  # one of BOOK_OWNER_KINDS, or None
    owner_id: str | None = None
    year_published: int | None = None
    description: str = ""
    subject_kind: str = ""  # a Tractatus's TRACTATUS_SUBJECTS entry
    art: str = ""
    ability: str = ""
    level: int | None = None
    quality: int | None = None
    spell_name: str = ""
    #: A Lab Text's / Casting Tablet's spell (any spell id; see Spell). Its
    #: Level comes from the spell, unless the spell is General-level, when
    #: `level` is the book's own. `spell_name` stays as typed (imported books
    #: link by it until a spell is chosen).
    spell_id: str | None = None
    #: A Lab Text written raw by its author: only he, and whoever
    #: decoded his texts or learned his abbreviations, can use it until he
    #: rewrites it for general use. `author_id`: the author, when a
    #: character of the saga.
    raw: bool = False
    author_id: str | None = None
    #: A Lab Text's kind (one of LAB_TEXT_KINDS; "" for any other book),
    #: and what it records of an effect with no spell to take it from:
    #: its Technique and Form (a spell's text takes both, and
    #: its level, from the spell), and a snapshot taken when it was written
    #: -- an enchantment's Range / Duration / Target, kind of device and
    #: shape and material, or a Longevity Ritual's subject (not `subject`:
    #: that key marks a pre-Library-tab save, see from_dict).
    text_kind: str = ""
    technique: str = ""
    form: str = ""
    effect_rdt: str = ""
    device_type: str = ""
    shape_material: str = ""
    ritual_subject: str = ""
    #: A Longevity Ritual's extra vis: the pawns beyond age / 5 it was first
    #: made with, which must be spent again each time it is performed.
    ritual_extra_vis: int = 0
    #: The codex the book is bound in with other books (a Codex id); None:
    #: bound on its own.
    codex_id: str | None = None

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], spell_names: dict[str, str] | None = None
    ) -> Book:
        d = dict(data)
        if d.get("type") == "Lab Text" and not d.get("text_kind"):
            # In older saves a Lab Text has no kind.
            d["text_kind"] = (
                TEXT_SPELL if d.get("spell_id") or d.get("spell_name") else TEXT_OTHER
            )
        if "subject" in d:
            # The pre-Library-tab stub: Summa/Tractatus/Lab Text on one `subject`.
            subject = str(d.pop("subject") or "")
            art = ART_BY_NAME.get(subject.lower())
            old_type = d.get("type")
            if old_type == "Summa":
                d["type"] = "Art Summa" if art else "Ability Summa"
            if old_type in ("Summa", "Tractatus"):
                if art:
                    d["art"] = art
                else:
                    d["ability"] = subject
            if old_type == "Tractatus":
                d["subject_kind"] = "Art" if art else "Ability"
            if old_type == "Lab Text":
                d["spell_name"] = (spell_names or {}).get(d.get("spell_id") or "", "")
            d.setdefault("name", d.get("spell_name") or subject)
            if d.get("notes"):
                d.setdefault("description", d["notes"])
        return cls(**known_fields(cls, d))


@dataclass
class Codex:
    """One physical tome binding several books together (Covenants,
    Varieties of Manuscript). Each book in it is still studied on its own,
    but only one reader can use the codex in a season, and its books are
    always kept together: they share one owner. The books point to it by
    `Book.codex_id`; a book with none is a codex of its own.

    A palimpsest is a codex whose first text was scraped away and written
    over: both texts can be read, each at -3 Quality."""

    id: str
    name: str
    palimpsest: bool = False
    #: An encyclopedia: a series of tractatus, each studied on its own, that
    #: also aids research like a library of its own (+1 per tractatus on
    #: the subject; Art & Academe, Encyclopedias).
    encyclopedia: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Codex:
        return cls(**known_fields(cls, data))


@dataclass
class LabCharacteristics:
    """The 8 Laboratory Characteristics' manual (base) component only.

    Each Characteristic's effective total is manual + virtue_sum +
    flaw_sum (see laboratories.lab_characteristic_total) -- virtue_sum and
    flaw_sum are derived from the lab's attached Virtues/Flaws, never stored
    here.
    """

    size: int = 0
    refinement: int = 0
    general_quality: int = 0
    upkeep: int = 0
    safety: int = 0
    warping: int = 0
    health: int = 0
    aesthetics: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabCharacteristics:
        return cls(**known_fields(cls, data))


@dataclass
class NamedDescription:
    """A name + a free-text description -- shared shape for a Laboratory's
    Rooms and its Inventory "items that influence the lab"."""

    name: str
    description: str = ""


@dataclass
class ArcaneConnection:
    """An Arcane Connection kept in a laboratory: what it
    connects to, and whether it has been fixed (made permanent by a season
    of lab work and a pawn of Vim) or lasts only a while."""

    id: str
    #: Whom or what it connects to ("a lock of Banna's hair").
    to: str
    fixed: bool = False
    #: A temporary one: how long it lasts, as typed ("until Summer 1222").
    lasts: str = ""
    #: Where it came from.
    source: str = ""
    description: str = ""
    #: When it was fixed, if the app fixed it.
    fixed_year: int | None = None
    fixed_season: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArcaneConnection:
        return cls(**known_fields(cls, data))


#: What a laboratory Diary entry can record, for its Activity Type: the lab
#: activities of reference/lab-sheet-design-doc.md, then the rest of a
#: season's lab work, and Other. A Diary entry's `activity` is one of these
#: or "" (not set -- every entry written before Activity Type existed).
LAB_ACTIVITIES: tuple[str, ...] = (
    "Invent Spell",
    "Learn Spell from Teacher",
    "Extract Vis",
    "Fix Arcane Connection",
    "Open Item for Enchantment",
    "Instill Effect (Invested Device)",
    "Lesser Enchantment",
    "Charged Item",
    "Longevity Ritual",
    "Bind Familiar",
    "Empower Familiar Bond",
    "Train Apprentice",
    "Translate Lab Text",
    "Arcane Experimentation",
    "Original Research",
    "Study",
    "Refine Laboratory",
    "Build/Modify Laboratory",
    "Other",
)


#: The 8 Activity Specializations a laboratory can have (ArM5 p.115 and
#: reference/laboratory-features-reference.md); with the 15 Arts they make
#: every Specialization.
LAB_ACTIVITY_SPECIALIZATIONS: tuple[str, ...] = (
    "Experimentation",
    "Familiar",
    "Items",
    "Longevity Rituals",
    "Spells",
    "Teaching",
    "Texts",
    "Vis Extraction",
)
LAB_SPECIALIZATIONS: tuple[str, ...] = (*LAB_ACTIVITY_SPECIALIZATIONS, *ARTS)


#: The lab Virtues a Feature is built on, and the points each gives it
#: (reference/laboratory-features-reference.md).
FEATURE_VIRTUE_POINTS: dict[str, int] = {
    "labvf_lesser_feature": 1,
    "labvf_greater_feature": 3,
}
#: The Focus Flaws, each with the Feature Virtue it goes with and the extra
#: points it gives that Feature.
FOCUS_FLAWS: dict[str, tuple[str, int]] = {
    "labvf_lesser_focus": ("labvf_lesser_feature", 2),
    "labvf_greater_focus": ("labvf_greater_feature", 4),
}


@dataclass
class LabFeatureDef:
    """A catalog Laboratory Feature (Altar, Cauldron...): what it is and the
    Specializations its points may go to. "Any Technique" in the source is
    stored as the five Techniques."""

    id: str
    name: str
    description: str
    specializations: tuple[str, ...]
    #: The book(s) it's from (sourcebooks); every entry so far is Covenants'.
    source: str = "Covenants"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabFeatureDef:
        specializations: list[str] = []
        for name in data["specializations"]:
            specializations += TECHNIQUES if name == "Any Technique" else [name]
        unknown = set(specializations) - set(LAB_SPECIALIZATIONS)
        if unknown:
            raise ValueError(f"Unknown Specializations {unknown} for {data['id']!r}")
        return cls(
            data["id"],
            data["name"],
            data["description"],
            tuple(specializations),
            data.get("source", "Covenants"),
        )


@dataclass
class LabSpecialtyGrant:
    """Points a Feature (or its Focus) puts into one Specialization."""

    specialization: str
    points: int


@dataclass
class LabFeature:
    """A Feature installed in a laboratory, built on one of its Lesser or
    Greater Feature Virtues (`virtue_id`, a VirtueFlawInstance.id; None when
    it has none yet, e.g. converted from old notes). `feature_id` is the
    catalog Feature, None for a custom one; `name` is the user's own label
    ("Large Brass Cauldron"). `allocations` spend the Virtue's points; with
    `focus` (the lab's Focus Flaw is built around it) `focus_allocations`
    spend the Focus's."""

    id: str
    name: str
    feature_id: str | None = None
    virtue_id: str | None = None
    allocations: list[LabSpecialtyGrant] = field(default_factory=list)
    focus: bool = False
    focus_allocations: list[LabSpecialtyGrant] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabFeature:
        d = dict(data)
        d["allocations"] = [
            LabSpecialtyGrant(**known_fields(LabSpecialtyGrant, g))
            for g in d.get("allocations", [])
        ]
        d["focus_allocations"] = [
            LabSpecialtyGrant(**known_fields(LabSpecialtyGrant, g))
            for g in d.get("focus_allocations", [])
        ]
        return cls(**known_fields(cls, d))


def _feature_from_old_text(
    text: str, feature_names: dict[str, str] | None = None, *, id: str = ""
) -> LabFeature:
    """An older save's free-text Feature as a LabFeature named with the text,
    of the catalog Feature named in it (by whole word, a plural too: "Big
    windows" is a Window), else custom. `feature_names` maps catalog names
    to ids (loaded from the catalog when not given)."""
    if feature_names is None:
        from .catalog import load_lab_feature_catalog

        feature_names = {f.name: f.id for f in load_lab_feature_catalog()}
    feature_id = None
    for name in sorted(feature_names, key=len, reverse=True):
        if re.search(rf"\b{re.escape(name)}s?\b", text, re.IGNORECASE):
            feature_id = feature_names[name]
            break
    return LabFeature(id=id or new_instance_id(), name=text, feature_id=feature_id)


def link_unlinked_features(lab: Laboratory) -> None:
    """Give each Feature without a Virtue the first Lesser/Greater Feature
    Virtue no other Feature has (old notes carry no link)."""
    taken = {f.virtue_id for f in lab.features if f.virtue_id}
    free = [
        vf.id
        for vf in lab.virtues_flaws
        if vf.vf_id in FEATURE_VIRTUE_POINTS and vf.id not in taken
    ]
    for feature in lab.features:
        if feature.virtue_id is None and free:
            feature.virtue_id = free.pop(0)


@dataclass
class LabSpecialtyEntry:
    """Points in one Specialization from a source the app doesn't work out
    itself (a Virtue/Flaw such as Subterranean, a magical effect...), typed
    in by the user. `specialization` is one of LAB_SPECIALIZATIONS, or ""
    for old free text that named none (the text is kept in `source`)."""

    specialization: str
    points: int = 1
    source: str = ""


def _parse_old_specialty(text: str) -> LabSpecialtyEntry:
    """An older save's free-text Specialty ("Terram +1") as an entry: the
    Specialization it names, its number (1 when there isn't one), the source
    "(from old notes)". Text that names no Specialization becomes a 0-point
    entry keeping the text, for the user to fix."""
    words = text.split()
    points = 1
    if words and re.fullmatch(r"[+-]?\d+", words[-1]):
        points = int(words.pop())
    name = " ".join(words).casefold()
    for specialization in LAB_SPECIALIZATIONS:
        if specialization.casefold() == name:
            return LabSpecialtyEntry(specialization, points, "(from old notes)")
    return LabSpecialtyEntry("", 0, text)


@dataclass
class DiaryEntry:
    """One entry of a laboratory's or a character's Diary."""

    year: int
    season: str = "Spring"  # one of SEASONS
    name: str = ""
    details: str = ""
    #: A lab Diary: one of LAB_ACTIVITIES. A character's Diary: the season
    #: activity's label (rules.activities.ACTIVITIES). "" when not set.
    activity: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DiaryEntry:
        return cls(**known_fields(cls, data))


@dataclass
class Laboratory:
    id: str
    #: None while the lab isn't assigned to a covenant (a legal state).
    covenant_id: str | None
    name: str
    owner_id: str | None = None
    location: str = ""
    #: Manual adjustment on top of the covenant's aura this lab inherits
    #: (e.g. from Virtues) -- see laboratories.lab_aura_total().
    aura_modifier: int = 0
    characteristics: LabCharacteristics = field(default_factory=LabCharacteristics)
    features: list[LabFeature] = field(default_factory=list)
    #: Specialization points from sources entered by hand (see
    #: laboratories.lab_specializations for the totals).
    specialties: list[LabSpecialtyEntry] = field(default_factory=list)
    #: Specializations the user turned off (or that arrived over a cap);
    #: they keep their points but don't count.
    dropped_specializations: list[str] = field(default_factory=list)
    #: Whether the sanctum's boundary is marked (Code of Hermes).
    sanctum_marked: bool = False
    rooms: list[NamedDescription] = field(default_factory=list)
    inventory_items: list[NamedDescription] = field(default_factory=list)
    raw_vis: dict[str, int] = field(default_factory=dict)  # Art -> pawns
    diary: list[DiaryEntry] = field(default_factory=list)
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    arcane_connections: list[ArcaneConnection] = field(default_factory=list)
    #: Moving it by mundane means: the seasons done so far (0: not
    #: moving; pack, then two reassembling).
    move_seasons: int = 0
    #: One of its covenant's starting laboratories: its Build
    #: Points count against the covenant's at creation.
    starting: bool = False
    #: Being created by the book: the creation checks run and
    #: the Creation Worksheet is offered. New records start In Creation;
    #: older saves load In Play (False).
    in_creation: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Laboratory:
        d = dict(data)
        d.pop("aura", None)  # moved to Covenant.aura -- discard the old per-lab value
        legacy_size = d.pop("size", None)
        if "characteristics" not in d:
            d["characteristics"] = LabCharacteristics(size=legacy_size or 0)
        else:
            d["characteristics"] = LabCharacteristics.from_dict(d["characteristics"])
        d["rooms"] = [
            NamedDescription(**known_fields(NamedDescription, r))
            for r in d.get("rooms", [])
        ]
        d["inventory_items"] = [
            NamedDescription(**known_fields(NamedDescription, i))
            for i in d.get("inventory_items", [])
        ]
        d["arcane_connections"] = [
            ArcaneConnection.from_dict(c) for c in d.get("arcane_connections", [])
        ]
        d["diary"] = [DiaryEntry.from_dict(entry) for entry in d.get("diary", [])]
        d["virtues_flaws"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, vf))
            for vf in d.get("virtues_flaws", [])
        ]
        # Ids given at load are the same every time (not new_instance_id):
        # a hosted saga's saves compare the file as loaded.
        for i, vf in enumerate(d["virtues_flaws"]):
            vf.id = vf.id or f"{d.get('id', '')}-vf{i}"
        old_features = [f for f in d.get("features", []) if isinstance(f, str)]
        d["features"] = [
            _feature_from_old_text(f, id=f"{d.get('id', '')}-feature{i}")
            if isinstance(f, str)  # older saves' free text
            else LabFeature.from_dict(f)
            for i, f in enumerate(d.get("features", []))
        ]
        d["specialties"] = [
            _parse_old_specialty(s)
            if isinstance(s, str)  # older saves' free text
            else LabSpecialtyEntry(**known_fields(LabSpecialtyEntry, s))
            for s in d.get("specialties", [])
        ]
        lab = cls(**known_fields(cls, d))
        if old_features:
            link_unlinked_features(lab)
        return lab


@dataclass
class ArtScore:
    """A magus's score in one Art: the total xp spent is stored, the score
    derived from it (rules.xp)."""

    xp: int = 0

    @property
    def level(self) -> int:
        """The score the xp buys."""
        return xp_rules.score_from_xp(self.xp, xp_rules.ART_FACTOR)

    @property
    def progress(self) -> xp_rules.Progress:
        return xp_rules.progress(self.xp, xp_rules.ART_FACTOR)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtScore:
        d = dict(data)
        if "level" in d:
            # Older saves typed the score beside the xp.
            d["xp"], _ = xp_rules.migrate_level_xp(
                d.pop("level"), d.get("xp", 0), xp_rules.ART_FACTOR
            )
        return cls(**known_fields(cls, d))


@dataclass
class Background:
    """Character-sheet page 1's biographical block (not the paper sheet's
    "Description" box -- see Description below for that)."""

    player: str = ""
    #: The saga Player who plays this character (players.py):
    #: when they sign in to a hosted saga, they may change it. None: no one
    #: but the storyguide.
    player_id: str | None = None
    setting: str = ""
    size: int = 0
    confidence_score: int = 0
    confidence_points: int = 0
    #: True Faith (faith.py): a Score only with the True Faith Virtue;
    #: anyone may hold Faith Points.
    true_faith_score: int = 0
    faith_points: int = 0
    birth_name: str = ""
    year_born: int | None = None
    race_nationality: str = ""
    place_of_origin: str = ""
    religion: str = ""
    title_profession: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Background:
        d = dict(data)
        if "confidence" in d and "confidence_score" not in d:
            # Older saves used a single "confidence"; migrate on load
            # so existing characters don't become unreadable over the split.
            d["confidence_score"] = d.pop("confidence")
        return cls(**known_fields(cls, d))


@dataclass
class Description:
    height: float | None = None
    weight: float | None = None
    hair: str = ""
    eyes: str = ""
    handedness: Handedness = "right"
    physical_description: str = ""
    #: Free-text biography, distinct from physical_description (the paper
    #: sheet's short free-text box), shown in the Biographical
    #: Detail section.
    biography: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Description:
        return cls(**known_fields(cls, data))


@dataclass
class Aging:
    """Decrepitude and Warping. Warping is tracked as Score/Points; both are
    typed for now (deriving the Score is Phase 4)."""

    decrepitude: int = 0
    effects: str = ""
    warping_score: int = 0
    warping_points: int = 0
    #: A Longevity Ritual: its modifier to aging rolls (0: none),
    #: the year it was made and who made it.
    longevity_modifier: int = 0
    longevity_year: int | None = None
    longevity_by: str = ""
    #: Aging: Decrepitude points (the score is worked out from
    #: them and kept in `decrepitude`), Aging Points per Characteristic, the
    #: apparent age (None: the actual age), and the season spent recovering
    #: from an Aging Crisis ("Spring 1221").
    decrepitude_points: int = 0
    aging_points: dict[str, int] = field(default_factory=dict)
    apparent_age: int | None = None
    recovering: str = ""
    #: Wizard's Twilight: the last season it takes ("Winter
    #: 1224"); no activity can be planned until after it.
    twilight_until: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Aging:
        aging = cls(**known_fields(cls, data))
        if aging.decrepitude and "decrepitude_points" not in data:
            # A typed Decrepitude score: the points that give it.
            thresholds = (0, 5, 15, 30, 50, 75)
            aging.decrepitude_points = thresholds[max(0, min(aging.decrepitude, 5))]
        return aging


@dataclass
class Wounds:
    """Simple per-severity counts, not individual wound records -- matches
    checking boxes on the paper sheet, not the calculated Wound Penalty."""

    light: int = 0
    medium: int = 0
    heavy: int = 0
    incapacitated: bool = False
    dead: bool = False
    #: A character's typed adjustment on top of the Soak worked out from
    #: Stamina, armour and Virtues (rules.derived.soak); a
    #: familiar's wounds leave it 0 (a familiar has base_soak).
    soak: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Wounds:
        return cls(**known_fields(cls, data))


@dataclass
class ScoredTrait:
    """A name + integer score. Shared shape for Personality Traits and
    Reputations -- both are just a label and a score on the character sheet."""

    name: str
    score: int
    #: Covenant Reputations only: whether the covenant is aware of this
    #: reputation (an unknown bad Reputation can't yet hurt Loyalty -- see
    #: inhabitants.reputation_loyalty_penalty). Always True and never edited
    #: for a Character's own Personality Traits/Reputations.
    known: bool = True


@dataclass
class HermeticBackground:
    """Magus-only Hermetic lineage block. `house` is a house_catalog.json id;
    no mechanical bonus is modeled for it yet, same as an unencoded
    Virtue/Flaw -- see VirtueFlawDef.modifiers."""

    house: str | None = None
    domus_magna: str = ""
    primus: str = ""
    parens: str = ""
    covenant_of_apprenticeship: str = ""
    #: Blank/unset means unknown, same convention as Background.year_born.
    age_of_apprenticeship: int | None = None
    wizards_sigil: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HermeticBackground:
        return cls(**known_fields(cls, data))


@dataclass
class Progress:
    """Progress carried from season to season on something a character is
    working at: an excellent item, a pilgrimage, taming
    an animal, a work of art, a formula, years at university."""

    kind: str
    name: str
    target: int = 0
    points: int = 0
    done: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Progress:
        return cls(**known_fields(cls, data))


@dataclass
class GrogYear:
    """A grog's yearly update (Grogs Ch. 5), applied in Winter:
    the vocational training (7 xp, or the teacher's Source Quality), 4 xp of
    practice and two 2 xp of exposure, less a season for each story award
    this year."""

    vocational: str = ""
    vocational_xp: int = 7
    practice: str = ""
    exposure: str = ""
    exposure_2: str = ""
    story_awards: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrogYear:
        return cls(**known_fields(cls, data))


@dataclass
class Breakthrough:
    """A magus's original research goal: what it is, its kind and
    target (the storyguide may type a secret one), the points gained, what
    reaching it grants, a Discovery waiting to be stabilized, and insights
    waiting to be invented."""

    name: str
    kind: str = "Minor"  # Minor / Major / Hermetic
    target: int = 30
    points: int = 0
    description: str = ""
    #: What reaching it grants: "Ability" (the points become its xp),
    #: "Virtue" (a catalog id in `grant`), "Parameter" or "" (the troupe's).
    grant_kind: str = ""
    grant: str = ""
    #: The Discovery to stabilize: its magnitude, the seasons, Lab Total,
    #: risk and vis of the experiment that made it, and the move of the chart
    #: roll (repeated when stabilizing).
    pending_magnitude: int = 0
    discovery_seasons: int = 1
    discovery_lab_total: int = 0
    discovery_risk: int = 0
    discovery_vis: int = 0
    discovery_vis_art: str = ""
    discovery_shift: int = 0
    #: The Technique and Form of that experiment (its Lab Text's).
    discovery_technique: str = ""
    discovery_form: str = ""
    #: Stabilizing: the seasons done of the current attempt.
    stabilizing_seasons: int = 0
    #: Insights gained and not yet invented.
    insights: int = 0
    reached: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Breakthrough:
        return cls(**known_fields(cls, data))


@dataclass
class CreationXp:
    """xp spent at a creation step, already added to
    the Ability or Art it names: the Creation Worksheet's record of where a
    character's starting xp came from, checked against each step's budget."""

    #: The worksheet step: "childhood", "later_life", "virtue", "free",
    #: "apprenticeship" or "gauntlet".
    step: str
    #: An Ability's name ("Area Lore: Rhine") or an Art ("Creo").
    target: str
    xp: int
    #: "native" for the childhood Native Language; the Virtue (vf_id) whose
    #: xp a "virtue" entry spends; the package a "package" entry comes from.
    note: str = ""
    #: The xp actually added to the Ability or Art (an Affinity adds half
    #: again); None: `xp`.
    applied: int | None = None


@dataclass
class CreationConditions:
    """A magus's years past Gauntlet at creation: the seasons
    that went to lab work, the working conditions the storyguide set (used
    for lab work and pre-play aging), and the age pre-play aging has been
    rolled up to (None: not yet)."""

    lab_seasons: int = 0
    aura: int = 3
    lab_quality: int = 0
    living_conditions: int = 1
    aged_to: int | None = None


@dataclass
class LabTextAccess:
    """How far a magus can read one author's raw Lab Texts: up to `level`, and how that
    was gained -- "decoded", "taught" (the author's abbreviations) or "" (not
    recorded)."""

    level: int = 0
    via: str = ""


@dataclass
class Character:
    id: str
    name: str
    type: CharacterType
    covenant_id: str | None = None
    characteristics: Characteristics = field(default_factory=Characteristics)
    arts: dict[str, ArtScore] = field(default_factory=dict)
    abilities: list[Ability] = field(default_factory=list)
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    #: Spells known, each with its own Spell Mastery.
    spells_known: list[KnownSpell] = field(default_factory=list)
    #: Spells this magus invented: they live with the magus, not the catalog
    #: (see Spell). Invention itself comes with the lab activities.
    invented_spells: list[Spell] = field(default_factory=list)
    #: Personal gear -- Possession records scoped to kind in
    #: {"weapon", "armor", "item"} (a character-scale subset of what the
    #: covenant Possessions tab holds; no sanctums/vis on a character sheet).
    inventory: list[Possession] = field(default_factory=list)
    assigned_lab_id: str | None = None
    background: Background = field(default_factory=Background)
    description: Description = field(default_factory=Description)
    aging: Aging = field(default_factory=Aging)
    wounds: Wounds = field(default_factory=Wounds)
    fatigue_level: FatigueLevel = "fresh"
    personality_traits: list[ScoredTrait] = field(default_factory=list)
    reputations: list[ScoredTrait] = field(default_factory=list)
    raw_vis: dict[str, int] = field(default_factory=dict)  # Art -> pawns
    hermetic: HermeticBackground = field(default_factory=HermeticBackground)
    #: What the character did season by season: written when a season is
    #: applied, and editable like a laboratory's Diary.
    diary: list[DiaryEntry] = field(default_factory=list)
    #: Tractatus already studied (book ids): each gives its xp only once
    #: (DE Ch. 10, Studying Tractatus).
    tractatus_read: list[str] = field(default_factory=list)
    #: Whose raw Lab Texts this magus can read, and up to what level
    #: (decoded, or taught the author's abbreviations), by the
    #: author's character id -- or name, for an author outside the saga
    #: (rules.book_seasons.author_key).
    lab_text_access: dict[str, LabTextAccess] = field(default_factory=dict)
    #: Original research goals.
    breakthroughs: list[Breakthrough] = field(default_factory=list)
    #: A grog's yearly update; None until set up.
    grog_year: GrogYear | None = None
    #: The supplements' sub-systems: Labor Points and a
    #: workshop's scores (City & Guild), progress records, experimental
    #: philosophy formulas known, and the last Ordeal (its size, and the
    #: Initiations since).
    labor_points: int = 0
    workshop_innovation: int = 0
    workshop_raw_materials: int = 0
    progress: list[Progress] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)
    ordeal: str = ""
    initiations_since_ordeal: int = 0
    #: Being created by the book: the creation checks run and
    #: the Creation Worksheet is offered. New records start In Creation;
    #: older saves load In Play (False).
    in_creation: bool = False
    #: Where the starting xp went, step by step.
    creation_xp: list[CreationXp] = field(default_factory=list)
    #: Years past Gauntlet and pre-play aging.
    creation_conditions: CreationConditions = field(default_factory=CreationConditions)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Character:
        d = dict(data)
        d["characteristics"] = Characteristics.from_dict(d.get("characteristics") or {})
        d["arts"] = {
            art: ArtScore.from_dict(score) for art, score in d.get("arts", {}).items()
        }
        d["abilities"] = [Ability.from_dict(a) for a in d.get("abilities", [])]
        d["virtues_flaws"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, vf))
            for vf in d.get("virtues_flaws", [])
        ]
        d["background"] = Background.from_dict(d.get("background") or {})
        d["description"] = Description.from_dict(d.get("description") or {})
        d["aging"] = Aging.from_dict(d.get("aging") or {})
        d["wounds"] = Wounds.from_dict(d.get("wounds") or {})
        d["personality_traits"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("personality_traits", [])
        ]
        d["reputations"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("reputations", [])
        ]
        d["hermetic"] = HermeticBackground.from_dict(d.get("hermetic") or {})
        d["invented_spells"] = [
            Spell.from_dict(sp) for sp in d.get("invented_spells", [])
        ]
        d["inventory"] = [
            # Older saves held plain description strings.
            Possession(id=f"{data['id']}-inv-{i}", kind="item", name=item)
            if isinstance(item, str)
            else Possession(**known_fields(Possession, item))
            for i, item in enumerate(d.get("inventory", []))
        ]
        d["spells_known"] = [
            # Older saves held bare spell ids.
            KnownSpell(spell_id=entry)
            if isinstance(entry, str)
            else KnownSpell.from_dict(entry)
            for entry in d.get("spells_known", [])
        ]
        d["diary"] = [DiaryEntry.from_dict(e) for e in d.get("diary", [])]
        d["breakthroughs"] = [
            Breakthrough.from_dict(b) for b in d.get("breakthroughs", [])
        ]
        if d.get("grog_year") is not None:
            d["grog_year"] = GrogYear.from_dict(d["grog_year"])
        d["progress"] = [Progress.from_dict(p) for p in d.get("progress", [])]
        d["creation_conditions"] = CreationConditions(
            **known_fields(CreationConditions, d.get("creation_conditions") or {})
        )
        d["creation_xp"] = [
            CreationXp(**known_fields(CreationXp, x)) for x in d.get("creation_xp", [])
        ]
        d["lab_text_access"] = {
            # In older saves an author's entry was just the level.
            author: (
                LabTextAccess(level=int(entry))
                if isinstance(entry, int)
                else LabTextAccess(**known_fields(LabTextAccess, entry))
            )
            for author, entry in (d.get("lab_text_access") or {}).items()
        }
        return cls(**known_fields(cls, d))


def character_age(year_born: int | None, current_year: int) -> int | None:
    """The character's age this saga-year, or None if Year Born isn't set.

    Not a Character property -- Character has no back-reference to the Saga
    that holds `current_year`, so this takes it explicitly instead, the same
    way an XP-to-Level formula would (see ArtScore's docstring).
    """
    return None if year_born is None else current_year - year_born


#: A Cord's score (0-5) -> its point cost from the binding Lab Total, per the
#: Familiar rules (see familiars.py). An exact table, not a formula.
CORD_SCORE_COSTS: dict[int, int] = {0: 0, 1: 5, 2: 15, 3: 30, 4: 50, 5: 75}


@dataclass
class BondPower:
    """One Empowered Bond Power (invested effect) on a Familiar -- typed in,
    no Lab Total formula computed (see DESIGN.md's "tracker, not rules
    engine" stance)."""

    id: str
    name: str = ""
    level: int = 0
    technique: str = ""  # one of TECHNIQUES, or ""
    form: str = ""  # one of FORMS, or ""
    #: e.g. "Magus (controlled by Familiar)" -- free text, not a fixed enum.
    target_controller: str = ""
    uses_per_day: int = 0
    penetration: int = 0
    vis_spent: int = 0
    cosmetic_trait: str = ""
    #: Points instilled so far while it is being instilled as lab work;
    #: None when finished.
    instilling_progress: int | None = None


@dataclass
class Familiar:
    """A magus's bound familiar (ArM5 Familiars). One per magus at a time,
    nested under its magus in the nav tree, but its own top-level entity
    (own sheet) rather than a field on Character.

    `character_id` is the magus who bound it: required, set once at
    creation, and never reassigned to a different magus.

    Built in slices, all now landed onto this one dataclass, the
    same way Character grew over many stories.

    `virtues_flaws`/`personality_traits` reuse Character's own shapes
    (VirtueFlawInstance/ScoredTrait) -- True Friend and Loyal (Partner) +3
    are added automatically (to both partners) when the Familiar is
    created, not left for the user to type in.

    The three Cords (golden/silver/bronze) are typed-in scores 0-5; their
    point cost is looked up from CORD_SCORE_COSTS, not stored separately.
    """

    id: str
    character_id: str
    name: str = ""
    #: The sheet's single "Species / Description" free-text line.
    species: str = ""
    season_bound: str = ""  # one of SEASONS, or "" if unset
    year_bound: int | None = None
    magic_might: int = 0
    might_pool: int | None = None  # None = not yet tracked, like year_born
    size: int = 0
    wound_multiplier: int = 1
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    personality_traits: list[ScoredTrait] = field(default_factory=list)
    reputations: list[ScoredTrait] = field(default_factory=list)
    #: Binding details -- typed in, no Lab Total formula computed.
    binding_technique: str = ""  # one of TECHNIQUES, or ""
    binding_form: str = ""  # one of FORMS, or ""
    binding_lab_total: int = 0
    target_binding_level: int = 0
    vis_spent_binding: int = 0
    golden_cord: int = 0  # 0-5
    silver_cord: int = 0  # 0-5
    bronze_cord: int = 0  # 0-5
    characteristics: Characteristics = field(default_factory=Characteristics)
    #: Both typed in, no formula computed -- same "tracker, not rules engine"
    #: treatment as Wounds.soak (see DESIGN.md).
    base_soak: int = 0
    magic_resistance: int = 0
    wounds: Wounds = field(default_factory=Wounds)
    fatigue_level: FatigueLevel = "fresh"
    #: Bite/Claws/Dodge etc. -- a free list of weapon-kind Possessions (same
    #: shape as Character.inventory's weapons), not a fixed
    #: 3-row table.
    natural_weapons: list[Possession] = field(default_factory=list)
    #: Same shape/catalog as Character.abilities -- Languages are just
    #: ordinary Abilities here too (per the rules, a familiar shares its
    #: magus's Language scores automatically, so none need typing in
    #: unless the user wants to note an exception).
    abilities: list[Ability] = field(default_factory=list)
    bond_powers: list[BondPower] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Familiar:
        d = dict(data)
        d["virtues_flaws"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, vf))
            for vf in d.get("virtues_flaws", [])
        ]
        d["personality_traits"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("personality_traits", [])
        ]
        d["reputations"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("reputations", [])
        ]
        d["characteristics"] = Characteristics.from_dict(d.get("characteristics") or {})
        d["wounds"] = Wounds.from_dict(d.get("wounds") or {})
        d["natural_weapons"] = [
            Possession(**known_fields(Possession, w))
            for w in d.get("natural_weapons", [])
        ]
        d["abilities"] = [Ability.from_dict(a) for a in d.get("abilities", [])]
        d["bond_powers"] = [
            BondPower(**known_fields(BondPower, p)) for p in d.get("bond_powers", [])
        ]
        return cls(**known_fields(cls, d))


# -- Enchanted Devices & Talismans (DE ch. 8, Enchantments) --

#: The three kinds of enchanted item. A Talisman is an Invested Device with
#: `EnchantedDevice.talisman` set (DE ch. 8, Talisman Attunement).
INVESTED = "Invested Device"
LESSER = "Lesser Enchantment"
CHARGED = "Charged Item"
DEVICE_TYPES: tuple[str, ...] = (INVESTED, LESSER, CHARGED)
#: Who can hold an enchanted device (`EnchantedDevice.holder_kind`).
DEVICE_HOLDER_KINDS: tuple[str, ...] = ("character", "laboratory", "covenant")

#: DE ch. 8, Material and Size Tables: each material's base points, and each
#: size's multiplier; capacity (the pawns of Vim vis to open it) is their
#: product.
ENCHANT_MATERIALS: dict[str, int] = {
    "cloth": 1,
    "glass": 1,
    "wood": 2,
    "leather": 2,
    "bone": 3,
    "soft stone": 3,
    "hard stone": 4,
    "base metal": 5,
    "silver": 6,
    "gold": 10,
    "semi-precious gem": 12,
    "precious gem": 15,
    "priceless gem": 20,
}
ENCHANT_SIZES: dict[str, int] = {
    "tiny": 1,
    "small": 2,
    "medium": 3,
    "large": 4,
    "huge": 5,
}
#: Where the Material and Size tables come from.
MATERIAL_SIZE_CITATION = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Material and Size Tables"
)

#: How a compound invested item's opening is paid (DE ch. 8, Preparation for
#: Enchantment): the sum of its components, or only the highest one.
PAY_SUM = "Sum of components"
PAY_HIGHEST = "Highest component"
DEVICE_PAYMENTS: tuple[str, ...] = (PAY_SUM, PAY_HIGHEST)

#: Uses per day -> the level added (DE ch. 8, Effect Frequency Table).
EFFECT_FREQUENCIES: dict[str, int] = {
    "1": 0,
    "2": 1,
    "3": 2,
    "6": 3,
    "12": 4,
    "24": 5,
    "50": 6,
    "Unlimited": 10,
}
#: Effect Expiry (invested items only; DE ch. 8, Effect Modifications) ->
#: how many years the effect lasts from its first use (None: it doesn't
#: expire).
EFFECT_EXPIRIES: dict[str, int | None] = {
    "None": None,
    "1 year": 1,
    "7 years": 7,
    "70 years": 70,
}


@dataclass(frozen=True)
class ShapeMaterialDef:
    """A catalog row (shape_material_catalog.json): one shape or material of
    DE's Shape and Material Bonuses Table, its (bonus, effect) pairs, and
    where it comes from. A row with no bonuses keeps the book's text as its
    `note`."""

    id: str
    name: str
    bonuses: tuple[tuple[int, str], ...] = ()
    note: str = ""
    source: str = ""
    citation: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShapeMaterialDef:
        d = dict(data)
        d["bonuses"] = tuple((b["bonus"], b["effect"]) for b in d.get("bonuses", []))
        return cls(**known_fields(cls, d))


@dataclass
class DeviceComponent:
    """One part of an enchanted item: what it is, and the Material and Size
    its capacity comes from (ENCHANT_MATERIALS, ENCHANT_SIZES)."""

    description: str = ""
    material: str = "wood"
    size: str = "small"


@dataclass
class ShapeMaterialBonus:
    """A Shape & Material bonus a device gives its effects, or (with a year
    and season) one of a talisman's attunements: the bonus, what it applies
    to, and the shape or material giving it (from the catalog or typed)."""

    bonus: int = 0
    applies_to: str = ""
    shape: str = ""
    #: Attunements only: when it was gained.
    year: int | None = None
    season: str = ""


@dataclass
class InstilledEffect:
    """One effect instilled in an enchanted device (the idea of a Familiar's
    Bond Powers). The level is typed; the modified level, vis and charges
    are worked out (enchanted_devices), each overridable."""

    id: str
    name: str = ""
    technique: str = ""  # one of TECHNIQUES, or ""
    form: str = ""  # one of FORMS, or ""
    requisites: str = ""
    range: str = ""
    duration: str = ""
    target: str = ""
    #: The spell-equivalent level.
    level: int = 0
    description: str = ""
    #: A key of EFFECT_FREQUENCIES (not used on a Charged Item).
    uses_per_day: str = "1"
    penetration: int = 0
    maintains_concentration: bool = False
    restricted_use: bool = False
    restricted_to: str = ""
    environmental_trigger: bool = False
    fast_trigger: bool = False
    linked_trigger: bool = False
    #: The id of the effect on the same device that triggers this one.
    linked_to: str = ""
    #: The word, gesture or condition that triggers it.
    trigger: str = ""
    #: A key of EFFECT_EXPIRIES (invested devices only), and the year of its
    #: first use, from which the expiry counts.
    expiry: str = "None"
    first_use_year: int | None = None
    #: False for a power not yet found by Investigation.
    known: bool = True
    #: Invested devices: points accumulated so far; None when finished.
    instilling_progress: int | None = None
    #: Typed figures replacing the worked-out ones (None: worked out).
    modified_level_override: int | None = None
    vis_override: int | None = None


@dataclass
class EnchantedDevice:
    """An enchanted item (DE ch. 8, Enchantments): an Invested Device (a
    Talisman when `talisman`), a Lesser Enchantment or a Charged Item. Held
    by a character, laboratory or covenant (the Book owner pattern); giving
    it away changes only the holder. Its maker is a character (`maker_id`)
    or a typed name, or neither (found or bought)."""

    id: str
    name: str
    type: str = INVESTED  # one of DEVICE_TYPES
    description: str = ""
    talisman: bool = False
    holder_kind: str | None = None  # one of DEVICE_HOLDER_KINDS, or None
    holder_id: str | None = None
    maker_id: str | None = None
    maker_name: str = ""
    components: list[DeviceComponent] = field(default_factory=list)
    #: A compound invested item's one-time choice (DEVICE_PAYMENTS).
    payment: str = PAY_SUM
    capacity_override: int | None = None
    #: Invested devices: the pawns of Vim vis opened so far.
    pawns_opened: int = 0
    bonuses: list[ShapeMaterialBonus] = field(default_factory=list)
    #: Charged Items: the Lab Total they were made with, the charges made
    #: (None: the most that Lab Total gives) and left (None: all of them),
    #: and how many identical objects share the charges.
    lab_total: int | None = None
    charges_made: int | None = None
    charges_left: int | None = None
    objects: int = 1
    #: Talismans: the attunements gained, each with its year and season.
    attunements: list[ShapeMaterialBonus] = field(default_factory=list)
    effects: list[InstilledEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EnchantedDevice:
        d = dict(data)
        d["components"] = [
            DeviceComponent(**known_fields(DeviceComponent, c))
            for c in d.get("components", [])
        ]
        for key in ("bonuses", "attunements"):
            d[key] = [
                ShapeMaterialBonus(**known_fields(ShapeMaterialBonus, b))
                for b in d.get(key, [])
            ]
        d["effects"] = [
            InstilledEffect(**known_fields(InstilledEffect, e))
            for e in d.get("effects", [])
        ]
        return cls(**known_fields(cls, d))


#: The kinds of covenant inhabitant, in the order the Inhabitants tab lists them.
INHABITANT_KINDS: tuple[str, ...] = (
    "magus",
    "companion",
    "specialist",
    "craftsperson",
    "turb",
    "inhabitant",
    "horse",
    "livestock",
)

#: The Covenant Role choices for a Companion or Specialist. Steward,
#: Chamberlain, Turb Captain and Autocrat each earn the covenant a Loyalty
#: bonus (Presence + a specific Ability) -- see
#: inhabitants.ROLE_ABILITY_MAP / specialists_loyalty().
COVENANT_ROLES: tuple[str, ...] = (
    "Teacher",
    "Steward",
    "Chamberlain",
    "Turb Captain",
    "Autocrat",
    "Other",
)

#: A magus's Gift, for the manual (not sheet-linked) case -- see
#: inhabitants.InhabitantEntry.gift / base_loyalty(). "" means not yet set
#: (base_loyalty() then assumes "Normal", the default expectation for a
#: magus); "None" is a deliberate choice that the magus has no Gift at all,
#: distinct from leaving it blank.
GIFT_CHOICES: tuple[str, ...] = ("Gentle", "Normal", "Blatant", "None")

#: The Covenant Role choices for the "inhabitant" kind (Other Covenfolk),
#: distinct from COVENANT_ROLES (Companions/Specialists): which of the book's
#: covenfolk categories this entry belongs to. Required -- unlike
#: COVENANT_ROLES it has no blank/"Other" option -- and feeds the
#: Teamsters/Servants/Laborers counts on the Inhabitants summary (see
#: inhabitants.other_covenfolk_count).
OTHER_COVENFOLK_ROLES: tuple[str, ...] = ("Laborer", "Servant", "Teamster", "Dependent")

#: The field of work of a Craftsperson. Each field but None and Books saves
#: money in one category of the covenant's yearly expenditure (see
#: economics.CRAFT_SAVINGS); Books (binders, illuminators) saves nothing.
CRAFT_FIELDS: tuple[str, ...] = (
    "None",
    "Building",
    "Consumables",
    "Laboratories",
    "Provisions",
    "Weapons and Armor",
    "Writing Materials",
    "Books",
)

#: Loyalty situational-modifier choices (Equipment, Money), default first noted.
LOYALTY_EQUIPMENT: tuple[str, ...] = (
    "Only inexpensive",
    "Standard",
    "Standard + 1 expensive piece",
    "Anything they need",
)
LOYALTY_EQUIPMENT_DEFAULT = "Standard"
LOYALTY_MONEY: tuple[str, ...] = (
    "No salary",
    "Half salary",
    "Standard salary",
    "Generous salary",
    "Lavish salary",
)
LOYALTY_MONEY_DEFAULT = "Standard salary"


#: The kinds of covenant possession, in the order the Possessions tab lists them.
POSSESSION_KINDS: tuple[str, ...] = (
    "property",
    "sanctum",
    "weapon",
    "armor",
    "vis_source",
    "vis_store",
    "item",
)

#: How heavily a sanctum's laboratory is used (default: Standard).
SANCTUM_USAGES: tuple[str, ...] = (
    "Light (1 Season or Less)",
    "Standard (2 Seasons)",
    "Heavy (3+ Seasons)",
)
SANCTUM_USAGE_DEFAULT = "Standard (2 Seasons)"

#: Points of a Weapon or Armor entry (ArM5 "Points of Weapons and Armor"):
#: type -> quality -> points each. Siege engines only come Expensive.
GEAR_QUALITIES: tuple[str, ...] = ("Inexpensive", "Standard", "Expensive")
GEAR_QUALITY_DEFAULT = "Standard"
GEAR_POINTS: dict[str, dict[str, int]] = {
    "Weapon or shield": {"Inexpensive": 1, "Standard": 4, "Expensive": 16},
    "Partial armor": {"Inexpensive": 2, "Standard": 8, "Expensive": 32},
    "Full armor": {"Inexpensive": 4, "Standard": 16, "Expensive": 64},
    "Ballista or light catapult": {"Expensive": 16},
    "Heavy catapult or trebuchet": {"Expensive": 32},
}
#: Which types each list offers (a shield is a weapon; armor is worn).
GEAR_TYPES_BY_KIND: dict[str, tuple[str, ...]] = {
    "weapon": (
        "Weapon or shield",
        "Ballista or light catapult",
        "Heavy catapult or trebuchet",
    ),
    "armor": ("Partial armor", "Full armor"),
}

#: The kinds of covenant income source and the yearly income (pounds) each
#: typically provides -- the default for a source's Current Income.
INCOME_TYPES: tuple[str, ...] = ("None", "Lesser", "Typical", "Greater", "Legendary")
INCOME_TYPE_DEFAULTS: dict[str, int] = {
    "None": 0,
    "Lesser": 40,
    "Typical": 100,
    "Greater": 250,
    "Legendary": 1000,
}

#: Income Modification (the book's yearly random-event table): the Effect a
#: storyguide picks for a source of income, and the multiplier it applies to
#: that year's income -- see economics.projected_income() / the covenant
#: Economics tab's "Improve" action (a manual stand-in for the yearly/
#: automated advancement the book describes; not run automatically here).
INCOME_EFFECTS: tuple[str, ...] = (
    "Slump",
    "Contraction",
    "Stagnation",
    "Status Quo",
    "Growth",
    "Expansion",
    "Boom",
)
INCOME_EFFECT_MULTIPLIERS: dict[str, float] = {
    "Slump": 0.5,
    "Contraction": 0.8,
    "Stagnation": 0.95,
    "Status Quo": 1.0,
    "Growth": 1.05,
    "Expansion": 1.2,
    "Boom": 1.5,
}


@dataclass
class Possession:
    """One stored entry on a covenant's Possessions tab.

    A single flat record for every kind (see POSSESSION_KINDS); each kind only
    uses the fields that suit it:

    * property: name, location, dimensions, inhabitants (free text), description.
    * sanctum: name, owner (text), location, quality, upkeep, build_points,
      usage, description. The covenant's laboratories are listed as sanctums
      automatically; a record with `lab_id` only holds the covenant-side extras
      (quality, upkeep, usage, description) for that laboratory, while a record
      without one is a manually-added sanctum.
    * weapon / armor: name, quantity, gear_type, gear_quality (they give its
      points, which feed the covenant's finances), load, description, and gear_id: the
      weapon_armor_catalog entry its figures were filled from (None: typed in). weapon
      only: weapon_init/weapon_attack/ weapon_defense/weapon_damage (combat figures,
      typed in or filled from the catalog and then editable, no formula -- see
      DESIGN.md; a None Attack or Damage is the book's n/a). armor only:
      armor_protection (its bonus to Soak).
    * item: name, quantity, description.
    * vis_source: name, art, pawns, season (when it is harvested), location,
      physical_form, description.
    * vis_store (Raw Vis Stores): name, art, pawns, physical_form, where it
      is kept -- location_kind/location_id: the covenant, one of its
      laboratories or one of its characters (none set means the
      covenant) -- and location, a free-text note on where exactly.

    `description` is user-written text that supports inline emphasis.
    """

    id: str
    kind: str
    name: str = ""
    lab_id: str | None = None
    description: str = ""
    location: str = ""
    #: vis_store: who keeps it -- "covenant", "laboratory" or "character"
    #: and that record's id ("" / None: the covenant that owns it).
    location_kind: str = ""
    location_id: str | None = None
    quantity: int = 1
    dimensions: str = ""
    inhabitants: str = ""
    owner: str = ""
    quality: int | None = None
    upkeep: int | None = None
    build_points: int | None = None
    usage: str = SANCTUM_USAGE_DEFAULT
    gear_type: str = ""  # weapon / armor: a key of GEAR_POINTS ("" = not set)
    gear_quality: str = GEAR_QUALITY_DEFAULT  # weapon / armor: one of GEAR_QUALITIES
    gear_id: str | None = None  # weapon / armor: a WeaponDef/ArmorDef id
    load: int = 0  # weapon / armor
    weapon_init: int = 0  # weapon only
    weapon_attack: int | None = 0  # weapon only; None = n/a
    weapon_defense: int = 0  # weapon only
    weapon_damage: int | None = 0  # weapon only; None = n/a
    armor_protection: int = 0  # armor only
    art: str = ""
    pawns: int = 0
    season: str = ""  # one of SEASONS
    physical_form: str = ""
    #: vis_source: covered by a Contested (or Indiscreet)
    #: Resource Hook, secured through this year (one story secures it for
    #: five); and by a Dwindling Resource Hook (-10% of its first value a year).
    contested: bool = False
    secured_until: int | None = None
    dwindling: bool = False
    #: A Dwindling Resource's value when it began to dwindle, and the years
    #: it has dwindled since (seasons.dwindle); None until its first year end.
    dwindling_from: int | None = None
    dwindled_years: int = 0

    def __post_init__(self) -> None:
        if self.kind not in POSSESSION_KINDS:
            raise ValueError(
                f"Unknown possession kind {self.kind!r}; must be one of {POSSESSION_KINDS}"
            )


@dataclass
class Inhabitant:
    """One stored entry on a covenant's Inhabitants tab.

    A single flat record for every kind (see INHABITANT_KINDS); each kind only
    uses the fields that make sense for it. `character_id` links it to a
    character sheet:

    * For a grog assigned to Specialists/Craftspeople/Turb/Inhabitants it is the
      grog it came from (name and year born were copied in when it was added and
      can be edited; the link is kept so the grog counts as assigned and its
      Abilities can be picked from).
    * For Magi/Companions, characters of that type in the covenant are listed
      automatically from their sheets; a record with their `character_id` only
      holds the covenant-side extras (description, responsibility, role),
      or, once `departed`, records that they are no longer counted.
    * With no `character_id` it is a manually-added person or animal (e.g. an NPC
      magus without a character sheet).

    `description` is user-written text that supports inline emphasis.
    """

    id: str
    kind: str
    name: str = ""
    character_id: str | None = None
    year_born: int | None = None
    house: str | None = None  # NPC magus: a house_catalog.json id
    gift: str = ""  # manual (non-sheet) magus: one of GIFT_CHOICES, or ""
    quantity: int = 1
    responsibility: str = ""
    role: str = ""  # one of COVENANT_ROLES, or ""
    #: Craftsperson: value of the crafting skill, unless linked_ability
    #: resolves one from a sheet. Steward/Chamberlain/Turb Captain/Autocrat:
    #: the manual Ability portion of the role's Loyalty bonus, unless the
    #: entry is tied to a character sheet (see inhabitants.ROLE_ABILITY_MAP).
    skill_value: int = 0
    field_of_work: str = "None"  # Craftsperson: one of CRAFT_FIELDS
    rare: bool = False  # Craftsperson
    linked_ability: str = ""  # Craftsperson: the Ability name they use
    #: Steward/Chamberlain/Turb Captain/Autocrat: the manual Presence portion
    #: of the role's Loyalty bonus, unless tied to a character sheet.
    presence: int = 0
    description: str = ""
    #: Magi/Companions only: the character is still in the covenant on their
    #: sheet but no longer counts as an inhabitant (died, left...). A departed
    #: record just marks that; it is not listed and not counted.
    departed: bool = False
    #: A specialist bought with Build Points at covenant creation:
    #: the score in the Ability used for the covenant
    #: (`linked_ability`); a teacher also has Communication and Teaching
    #: (None: not a teacher). None score: not bought.
    specialist_score: int | None = None
    teacher_communication: int | None = None
    teacher_teaching: int | None = None

    def __post_init__(self) -> None:
        if self.kind not in INHABITANT_KINDS:
            raise ValueError(
                f"Unknown inhabitant kind {self.kind!r}; must be one of {INHABITANT_KINDS}"
            )


@dataclass
class Loyalty:
    """The covenant's Loyalty block. Base Loyalty, Total Modifiers, Current
    Loyalty Points and Prevailing Loyalty Score are all calculated (see
    inhabitants.py) from the fields below plus data read from elsewhere on the
    sheet (magi's Gift, Equipment/Money's own point tables, the covenant's
    Living Conditions (Mundane), Specialists' role bonuses, Reputations).
    Familiarity and Magical Influence stay free-form. Actions and Events
    also adds the covenant Diary's Loyalty points (covenant_diary.py);
    `actions_and_events` is the manual adjustment on top."""

    governance: str = ""  # Type of Governance; only used if no governance Boon
    equipment: str = LOYALTY_EQUIPMENT_DEFAULT
    money: str = LOYALTY_MONEY_DEFAULT
    #: The covenant provides a pension (half Wages until death) to retirees:
    #: +10 Loyalty points on top of the Money selection's own points.
    pension: bool = False
    familiarity: int = 0
    actions_and_events: int = 0
    magical_influence: int = 0


@dataclass
class Population:
    """The Inhabitants summary block and the Miscellaneous block. The
    covenant's Total Inhabitants, the minimum Servants/Teamsters needed, and
    the actual Teamsters/Servants/Laborers counts are all calculated from the
    Other Covenfolk list (see inhabitants.total_inhabitants /
    minimum_servants / minimum_teamsters / other_covenfolk_count), not
    stored; `other_people` is the one figure left with no list behind it, so
    it stays manual."""

    other_people: int = 0
    aging_magi: int = 0
    aging_mundane: int = 0
    magic_laborers: int = 0
    magic_servants: int = 0
    magic_teamsters: int = 0
    magic_turbula: int = 0


@dataclass
class IncomeSource:
    """One of a covenant's sources of income. `income` is the Current Income in
    pounds per year; None means "follow the type" (INCOME_TYPE_DEFAULTS), an
    int is a value the user typed over it."""

    id: str
    name: str = ""
    type: str = "Typical"  # one of INCOME_TYPES
    income: int | None = None
    description: str = ""  # supports inline emphasis
    #: A record of the last "Improve" action taken on this source (see
    #: economics.improvement_note); plain text, replaced wholesale each time,
    #: not user-editable directly.
    note: str = ""
    #: Covered by a Contested (or Indiscreet) Resource Hook,
    #: secured through this year (no income until it is); and a Dwindling
    #: Resource Hook (-10% of its first value a year).
    contested: bool = False
    secured_until: int | None = None
    dwindling: bool = False
    #: A Dwindling Resource's value when it began to dwindle, and the years
    #: it has dwindled since (seasons.dwindle); None until its first year end.
    dwindling_from: int | None = None
    dwindled_years: int = 0

    def __post_init__(self) -> None:
        if self.type not in INCOME_TYPES:
            raise ValueError(
                f"Unknown income type {self.type!r}; must be one of {INCOME_TYPES}"
            )

    @property
    def current_income(self) -> int:
        if self.income is not None:
            return self.income
        return INCOME_TYPE_DEFAULTS[self.type]


@dataclass
class Economics:
    """What is stored for the covenant's Economics tab. Every figure that can be
    worked out from the rest of the sheet (points, costs, savings, totals) is
    calculated on demand (see economics.py), not stored: only what the user
    types is kept here."""

    income_sources: list[IncomeSource] = field(default_factory=list)
    wealth: int = 0  # the covenant's stores, in pounds
    tithes: int = 0
    inflation: int = 0
    #: There's a cost of at least 1 pound of sundries every year.
    sundry: int = 1
    #: Cost-saving rows the book gives no formula for, so the user works the
    #: figure out and types the pounds saved directly.
    magic_savings: int = 0
    emergency_savings: int = 0
    #: Free-text notes by row key ("buildings", "laborers"...).
    notes: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Economics:
        d = known_fields(cls, data)
        d["income_sources"] = [
            IncomeSource(**known_fields(IncomeSource, s))
            for s in d.get("income_sources", [])
        ]
        return cls(**known_fields(cls, d))


#: A Covenant Diary entry's categories, in the spec's order.
COVENANT_DIARY_CATEGORIES: tuple[str, ...] = (
    "Improvements",
    "Purchases & Sales",
    "Vis",
    "Library",
    "Inhabitants",
    "Membership",
    "Council",
    "Laboratories",
    "Loyalty Event",
    "Year-end Accounts",
    "Defence & Magic",
    "Politics",
    "Favours",
    "Covenant Season",
    "Story Event",
)
#: The category whose entries have a Status, a linked Boon/Hook and a
#: Revisit year.
STORY_EVENT = "Story Event"
#: A Story Event's Status.
STORY_EVENT_STATUSES: tuple[str, ...] = ("Open", "Resolved")


@dataclass
class CovenantDiaryEntry:
    """One entry on the covenant's Diary tab: what happened and
    when, with optional amounts. Only `loyalty` changes the sheet (it adds
    into the Loyalty block's Actions and Events); pounds and vis are a
    record. `status`, `boon_hook_id` (a VirtueFlawInstance.id among the
    covenant's Boons/Hooks) and `revisit_year` are for Story Events."""

    year: int
    season: str = "Spring"  # one of SEASONS
    name: str = ""
    details: str = ""
    category: str = ""  # one of COVENANT_DIARY_CATEGORIES, or ""
    pounds: float | None = None  # + received, - spent
    vis_pawns: int | None = None  # + gained, - spent
    vis_art: str = ""  # one of ARTS, or ""
    loyalty: int | None = None
    status: str = ""  # Story Events: one of STORY_EVENT_STATUSES
    boon_hook_id: str | None = None
    revisit_year: int | None = None


@dataclass
class Covenant:
    id: str
    saga_id: str
    name: str
    notes: str = ""
    aura: int = 0  # inherited by all of the covenant's laboratories
    #: Which realm the aura belongs to (REALMS); older saves load as Magic.
    aura_realm: str = "Magic"
    tribunal: str = ""
    year_founded: int | None = None
    aegis_of_the_hearth: int = 0
    aegis_penetration: int = 0
    living_conditions_magi: int = 0
    living_conditions_mundane: int = 0
    #: The covenant's life stage (ArM5 Chapter 6, "Covenant Seasons") -- one
    #: of SEASONS. Not the calendar season, which lives on the Saga.
    covenant_season: str = "Spring"
    #: The book's base covenant it was started from (covenant_templates
    #: BASE_BY_KEY: "weak", "medium", "powerful"), or "".
    base_covenant: str = ""
    #: Pounds its unspent Build Points became on moving to In Play
    #: (creation_covenant.convert_remaining), so they stay spent if it moves
    #: back to In Creation.
    converted_pounds: int = 0
    #: Boons and Hooks attached to this covenant, resolved against the
    #: covenant Boon/Hook catalog (vf_id holds the catalog id).
    #: An optional free-text descriptor lives in `params["detail"]` (which
    #: Edifice, which resource...), blank by default -- see BOON_HOOK_DETAIL.
    boons_hooks: list[VirtueFlawInstance] = field(default_factory=list)
    #: Covenant Reputations: a name and a score from -3 to +3 (the range is
    #: enforced by the edit dialog, not here).
    reputations: list[ScoredTrait] = field(default_factory=list)
    #: The Inhabitants tab (see Inhabitant, Loyalty and Population).
    inhabitants: list[Inhabitant] = field(default_factory=list)
    loyalty: Loyalty = field(default_factory=Loyalty)
    population: Population = field(default_factory=Population)
    #: The Possessions tab (see Possession).
    possessions: list[Possession] = field(default_factory=list)
    #: The Economics tab (see Economics).
    economics: Economics = field(default_factory=Economics)
    #: The Diary tab (see CovenantDiaryEntry), in the order entered.
    diary: list[CovenantDiaryEntry] = field(default_factory=list)
    #: The Power Level chosen at creation: one of POWER_LEVELS,
    #: or "" before one is chosen.
    power_level: str = ""
    #: The Build Points the storyguide gives it, within the Power Level's
    #: range: what its starting resources are bought with (None: not set).
    build_points_budget: int | None = None
    #: Magi who go without a laboratory at creation, each refunding 50
    #: Build Points. Only this refunds: a magus whose lab
    #: isn't entered still has the free one.
    magi_without_lab: int = 0
    #: What its Build Points were spent on when it moved to In Play, by
    #: Build-tab row; None for a covenant still In Creation,
    #: or one in play since before this was recorded.
    initial_build_points: dict[str, int] | None = None
    #: Being created by the book: the creation checks run and
    #: the Creation Worksheet is offered. New records start In Creation;
    #: older saves load In Play (False).
    in_creation: bool = False
    #: The library's research bonus per subject (an Art or Ability name ->
    #: 1-5, book_value.RESEARCH_LEVELS), as the troupe judges its
    #: collection; a subject not listed has none.
    library_research: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Covenant:
        d = dict(data)
        d["economics"] = Economics.from_dict(d.get("economics") or {})
        d["boons_hooks"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, bh))
            for bh in d.get("boons_hooks", [])
        ]
        # Diary Story Events link to a Boon/Hook by its instance id.
        # The same ids every load, like a laboratory's Virtues.
        for i, bh in enumerate(d["boons_hooks"]):
            bh.id = bh.id or f"{d.get('id', '')}-bh{i}"
        d["diary"] = [
            CovenantDiaryEntry(**known_fields(CovenantDiaryEntry, e))
            for e in d.get("diary", [])
        ]
        d["reputations"] = [
            ScoredTrait(**known_fields(ScoredTrait, r))
            for r in d.get("reputations", [])
        ]
        d["inhabitants"] = [
            Inhabitant(**known_fields(Inhabitant, i)) for i in d.get("inhabitants", [])
        ]
        d["loyalty"] = Loyalty(**known_fields(Loyalty, d.get("loyalty") or {}))
        d["population"] = Population(
            **known_fields(Population, d.get("population") or {})
        )
        d["possessions"] = [
            Possession(**known_fields(Possession, p)) for p in d.get("possessions", [])
        ]
        # Older saves kept a bare Art -> pawns `vis_stock`; those are now Raw Vis
        # stores on the Possessions tab (and the key is no longer saved).
        stock = d.pop("vis_stock", None) or {}
        if stock:
            for art, pawns in stock.items():
                art_name = ART_BY_NAME.get(str(art).lower(), str(art))
                d["possessions"].append(
                    Possession(
                        id=f"vis_store_{art_name.lower()}",
                        kind="vis_store",
                        name=f"{art_name} Vis",
                        art=art_name,
                        pawns=int(pawns),
                    )
                )
        return cls(**known_fields(cls, d))  # drops the retired `library_id`


#: The `VirtueFlawInstance.params` key holding a covenant Boon/Hook's
#: optional descriptor.
BOON_HOOK_DETAIL = "detail"

#: The `params` key holding the user's own multi-line description of an
#: attached Boon/Hook (what the Hidden Resources actually contain...), shown
#: in the details panel ahead of the official rules text.
BOON_HOOK_DESCRIPTION = "description"

#: The `params` key marking an attached Minor Hook as Unknown ("yes"): one
#: player storyguides it without the others knowing, and it counts as a
#: Major Hook for balancing (Covenants). Only honoured for catalog entries
#: marked `unknown` -- see covenants.boon_hook_is_unknown().
BOON_HOOK_UNKNOWN = "unknown"

#: The `params` key holding the id of the vis or income source a Contested,
#: Indiscreet or Dwindling Resource Hook is about (see
#: covenants.RESOURCE_HOOKS).
BOON_HOOK_RESOURCE = "resource"

#: The `params` key holding the id of the Covenant Situation a Boon/Hook
#: came with (covenants.situation_instances), so choosing another
#: Situation can replace it.
BOON_HOOK_SITUATION = "situation"


def next_season(season: str, year: int) -> tuple[str, int]:
    """The season after (season, year). The ArM5 year begins in Spring, so
    Winter rolls over into Spring of the following year."""
    index = SEASONS.index(season)
    if index == len(SEASONS) - 1:
        return SEASONS[0], year + 1
    return SEASONS[index + 1], year


@dataclass
class XpAllocation:
    """Where some of a season's Source Quality goes: `subject` is
    "ability:<name>", "art:<art>" or "mastery:<spell id>" (see
    rules.activities.subject_label), `points` its share (Adventure splits its
    Source Quality, Exposure may split its 2 points)."""

    subject: str
    points: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> XpAllocation:
        return cls(**known_fields(cls, data))


@dataclass
class SpellDesign:
    """A spell being invented: started from a spell or from
    nothing, and edited freely. It lives on the plan until the spell is
    invented; only then is it added to the magus's spells."""

    #: Identifies the design across the seasons it takes (its project).
    key: str
    name: str = ""
    technique: str = ""
    form: str = ""
    requisites: list[str] = field(default_factory=list)
    base_level: int | None = None
    range: str = "Personal"
    duration: str = "Momentary"
    target: str = "Individual"
    #: Magnitudes of a Range/Duration/Target the app doesn't know (a
    #: breakthrough, a troupe ruling), by "range"/"duration"/"target".
    custom_steps: dict[str, int] = field(default_factory=dict)
    #: Size, complexity and requisite magnitudes on top.
    extra_magnitudes: int = 0
    ritual: bool = False
    description: str = ""
    base_effect: str = ""
    #: The spell it was started from, if any.
    source_spell_id: str | None = None
    #: The level as printed, for a spell started from one with no base
    #: level recorded (None: worked out from the base level).
    printed_level: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpellDesign:
        return cls(**known_fields(cls, data))


@dataclass
class SeasonPlan:
    """What a character will do in one season: typed by the user,
    locked in until the season is applied. Its outcome is always worked out
    (rules.activities.outcome), never stored."""

    character_id: str
    year: int
    season: str  # one of SEASONS
    activity: str  # a rules.activities.ACTIVITIES key
    allocations: list[XpAllocation] = field(default_factory=list)
    #: Practice / Adventure: the Source Quality when it isn't the rule's
    #: default (None: the default).
    source_quality: int | None = None
    #: Full months of the season lost to distractions (0-3).
    months_lost: int = 0
    #: Free text: what "Other" was, or notes kept with the Diary entry.
    details: str = ""
    #: Reading: the book studied.
    book_id: str | None = None
    #: Being taught / trained: the teacher or master.
    teacher_id: str | None = None
    #: Vis study: whose raw vis is used ("character" or "laboratory").
    vis_from: str = ""
    #: Vis study: the stress die as rolled at the table (None: the app
    #: rolls it when the season is applied).
    die: int | None = None
    #: Lab work: the laboratory it is done in. A plan with a
    #: laboratory is made on the lab's Planning tab.
    lab_id: str | None = None
    #: Inventing: the spell invented (a Lab Text's spell when working from one).
    spell_id: str | None = None
    #: Inventing: a similar spell the magus knows (adds its magnitude).
    similar_spell_id: str | None = None
    #: Lab work: days away from the laboratory (a short adventure, travel...);
    #: 11-20 lower the Lab Total, more rule lab work out.
    days_away: int = 0
    #: Inventing: the spell being designed (the Invent Spell screen).
    design: SpellDesign | None = None
    #: Lab work: the magus's Magical Focus applies (the lower Art counts
    #: twice), their Magic Theory Specialty applies (+1), and any other
    #: modifier the troupe allows.
    focus: bool = False
    theory_specialty: bool = False
    other_modifier: int = 0
    #: Longevity Ritual: who it is for (the magus when None), the
    #: Art of the vis paid with, and extra pawns (+1 Lab Total each). Being
    #: its subject: the magus making it.
    subject_id: str | None = None
    vis_art: str = ""
    extra_vis: int = 0
    #: Fixing an Arcane Connection: the laboratory's connection fixed.
    connection_id: str | None = None
    #: Enchanting: the enchanted device worked on, the effect
    #: instilled (or made), and the shape and material bonus that applies.
    device_id: str | None = None
    effect_id: str | None = None
    shape_bonus: int = 0
    #: Binding a familiar: the Technique and Form used, and the
    #: cords the Lab Total buys (0-5 each).
    technique: str = ""
    form: str = ""
    golden_cord: int = 0
    silver_cord: int = 0
    bronze_cord: int = 0
    #: Writing, copying and translating books: the title, the
    #: summa's Level (None: the most the author can), the language written
    #: or translated into, and a quick copy.
    title: str = ""
    book_level: int | None = None
    language: str = ""
    quick: bool = False
    #: Moving a laboratory: by spell (one season, a roll) rather
    #: than mundane means, and where to.
    by_spell: bool = False
    #: Supplement seasons: the Characteristic a total uses.
    characteristic: str = ""
    #: Experimentation: whether the season experiments, its
    #: risk modifier, the simple die added to the Lab Total (None: rolled
    #: when played), and the research goal it seeks a Discovery for.
    experimenting: bool = False
    risk: int = 0
    experiment_die: int | None = None
    research: str = ""
    research_kind: str = "Minor"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonPlan:
        d = dict(data)
        d["allocations"] = [XpAllocation.from_dict(a) for a in d.get("allocations", [])]
        if d.get("design") is not None:
            d["design"] = SpellDesign.from_dict(d["design"])
        return cls(**known_fields(cls, d))


@dataclass
class LabProject:
    """Lab work that runs over several seasons: the points a
    magus has put into inventing a spell so far."""

    character_id: str
    spell_id: str
    points: int = 0
    #: Experimental side effects and modified effects so far.
    effects: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabProject:
        return cls(**known_fields(cls, data))


@dataclass
class SeasonRecordLine:
    """One person's line in a season's record: kept as the text
    it showed, so it still reads right after the character is renamed or
    deleted."""

    character_id: str
    name: str
    covenant_id: str | None = None
    #: The activity's label; "" when nothing was planned.
    activity: str = ""
    #: What it was on ("Latin", Other's notes...).
    what: str = ""
    #: The result ("Latin +4 xp"), or why the plan wasn't carried out.
    result: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonRecordLine:
        return cls(**known_fields(cls, data))


@dataclass
class SeasonRecord:
    """What happened in one season, saved when it is applied if the saga
    keeps season records."""

    year: int
    season: str
    lines: list[SeasonRecordLine] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonRecord:
        d = dict(data)
        d["lines"] = [SeasonRecordLine.from_dict(line) for line in d.get("lines", [])]
        return cls(**known_fields(cls, d))


@dataclass
class Player:
    """Someone who can sign in to the saga from a browser: a
    name, a role (players.PLAYER or players.STORYGUIDE) and the passcode,
    kept only as a salted hash (players.hash_passcode)."""

    id: str
    name: str
    role: str = "player"
    passcode_hash: str = ""
    #: Whether this player may also change the covenants; a
    #: storyguide always may.
    covenant_rights: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Player:
        return cls(**known_fields(cls, data))


@dataclass
class Saga:
    id: str
    name: str
    storyguide: str = ""
    description: str = ""
    current_year: int = 1220
    current_season: str = "Spring"
    covenants: list[Covenant] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    laboratories: list[Laboratory] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    #: The codices binding several books together (see Codex).
    codices: list[Codex] = field(default_factory=list)
    spells: list[Spell] = field(default_factory=list)
    familiars: list[Familiar] = field(default_factory=list)
    #: Every enchanted item in the saga, each shown on its holder's sheet.
    enchanted_devices: list[EnchantedDevice] = field(default_factory=list)
    #: The supplements in play (sourcebooks.SUPPLEMENTS abbreviations); None,
    #: the default and what older saves load as, means every book. The core
    #: book is always in play. See sourcebooks.
    books_in_play: list[str] | None = None
    #: The optional rules the troupe has turned on (rules.options keys);
    #: an option not listed is off, its default.
    rule_options: dict[str, bool] = field(default_factory=dict)
    #: Season plans not yet applied; a plan is removed when its
    #: season is applied.
    season_plans: list[SeasonPlan] = field(default_factory=list)
    #: Whether a record of each applied season is kept.
    keep_season_records: bool = True
    #: Those records, oldest first.
    season_records: list[SeasonRecord] = field(default_factory=list)
    #: Lab work in progress over several seasons.
    lab_projects: list[LabProject] = field(default_factory=list)
    #: User-made catalog entries: house rules and entries from
    #: books the shared catalogs don't carry -- character Virtues & Flaws,
    #: laboratory Virtues & Flaws, covenant Boons & Hooks. Text only: no
    #: effects the rules engine applies. See house_rules.py.
    custom_virtues_flaws: list[VirtueFlawDef] = field(default_factory=list)
    custom_lab_virtues_flaws: list[LabVirtueFlawDef] = field(default_factory=list)
    custom_boons_hooks: list[CovenantBoonHookDef] = field(default_factory=list)
    #: Who can sign in to the saga from a browser when it is hosted;
    #: the storyguide's own window needs no sign-in.
    players: list[Player] = field(default_factory=list)
    #: The app version that last saved this saga (storage.save_saga sets it;
    #: "" for a save older than versioning), for upgrading old saves later.
    app_version: str = ""
    #: Who last saved the saga (storage.save_saga sets it, from
    #: storage.saved_by): a signed-in player's name, else "" for the
    #: storyguide. Shown when another copy picks up the change.
    saved_by: str = ""

    def covenant(self, covenant_id: str | None) -> Covenant | None:
        """The covenant with this id, if there is one."""
        return next((c for c in self.covenants if c.id == covenant_id), None)

    def character(self, character_id: str | None) -> Character | None:
        """The character with this id, if there is one."""
        return next((c for c in self.characters if c.id == character_id), None)

    def laboratory(self, laboratory_id: str | None) -> Laboratory | None:
        """The laboratory with this id, if there is one."""
        return next((lab for lab in self.laboratories if lab.id == laboratory_id), None)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Saga:
        d = dict(data)
        d["covenants"] = [Covenant.from_dict(c) for c in d.get("covenants", [])]
        d["characters"] = [Character.from_dict(c) for c in d.get("characters", [])]
        d["laboratories"] = [
            Laboratory.from_dict(lab) for lab in d.get("laboratories", [])
        ]
        d["familiars"] = [Familiar.from_dict(f) for f in d.get("familiars", [])]
        d["enchanted_devices"] = [
            EnchantedDevice.from_dict(e) for e in d.get("enchanted_devices", [])
        ]
        d["spells"] = [Spell.from_dict(s) for s in d.get("spells", [])]
        d["season_plans"] = [SeasonPlan.from_dict(p) for p in d.get("season_plans", [])]
        d["season_records"] = [
            SeasonRecord.from_dict(r) for r in d.get("season_records", [])
        ]
        d["lab_projects"] = [LabProject.from_dict(p) for p in d.get("lab_projects", [])]
        d["custom_virtues_flaws"] = [
            VirtueFlawDef.from_dict(e) for e in d.get("custom_virtues_flaws", [])
        ]
        d["custom_lab_virtues_flaws"] = [
            LabVirtueFlawDef.from_dict(e) for e in d.get("custom_lab_virtues_flaws", [])
        ]
        d["custom_boons_hooks"] = [
            CovenantBoonHookDef.from_dict(e) for e in d.get("custom_boons_hooks", [])
        ]
        d["players"] = [Player.from_dict(p) for p in d.get("players", [])]
        spell_names = {s.id: s.name for s in d["spells"]}
        d["books"] = [Book.from_dict(b, spell_names) for b in d.get("books", [])]
        d["codices"] = [Codex.from_dict(c) for c in d.get("codices", [])]
        # Older saves kept a Library record per covenant listing its book ids;
        # ownership now lives on the book itself.
        for library in d.pop("libraries", None) or []:
            ids = set(library.get("books") or [])
            for book in d["books"]:
                if book.id in ids and book.owner_kind is None:
                    book.owner_kind = "covenant"
                    book.owner_id = library.get("covenant_id")
        saga = cls(**known_fields(cls, d))
        _link_vis_store_locations(saga)
        _key_lab_text_access_by_author(saga)
        return saga


def _key_lab_text_access_by_author(saga: Saga) -> None:
    """Key who can read whose Lab Texts by the author's character id, not
    name (older saves used the name, which a rename broke): an
    entry, or a decoding under way, naming exactly one character of the
    saga moves to that character's id. Any other name stays as typed."""
    ids = {c.id for c in saga.characters}
    by_name: dict[str, list[str]] = {}
    for character in saga.characters:
        by_name.setdefault(character.name, []).append(character.id)

    def key(author: str) -> str:
        found = by_name.get(author, [])
        return found[0] if author not in ids and len(found) == 1 else author

    for character in saga.characters:
        moved: dict[str, LabTextAccess] = {}
        for author, access in character.lab_text_access.items():
            kept = moved.get(key(author))
            if kept is None or access.level > kept.level:
                moved[key(author)] = access
        character.lab_text_access = moved
    for project in saga.lab_projects:
        # A decoding under way: "decode:<reader id>:<author>".
        prefix, _, author = project.spell_id.rpartition(":")
        if prefix.startswith("decode:") and author:
            project.spell_id = f"{prefix}:{key(author)}"


def _link_vis_store_locations(saga: Saga) -> None:
    """Give every covenant Raw Vis Store a real place it is kept
    (older saves only had free text): the laboratory or character
    of the covenant that the text names, else the covenant itself, with the
    text left as the store's note on where exactly."""
    for covenant in saga.covenants:
        places: list[tuple[str, str, str]] = [
            ("laboratory", lab.id, lab.name)
            for lab in saga.laboratories
            if lab.covenant_id == covenant.id
        ] + [
            ("character", c.id, c.name)
            for c in saga.characters
            if c.covenant_id == covenant.id
        ]
        for store in covenant.possessions:
            if store.kind != "vis_store" or store.location_kind:
                continue
            text = store.location.strip().lower()
            match = next(
                (p for p in places if text and p[2].strip().lower() == text), None
            )
            if match is not None:
                store.location_kind, store.location_id = match[0], match[1]
                store.location = ""
            else:
                store.location_kind, store.location_id = "covenant", covenant.id


def assign_laboratory(saga: Saga, character: Character, new_lab_id: str | None) -> None:
    """Give `character` the laboratory `new_lab_id` (or none), keeping
    Character.assigned_lab_id and Laboratory.owner_id in sync from both
    directions: the character's old lab (if any) is freed, and if the new lab
    already had a different owner, that character is unassigned too, so a lab
    never has an owner who doesn't point back at it or vice versa."""
    old_lab = saga.laboratory(character.assigned_lab_id)
    if old_lab is not None:
        old_lab.owner_id = None

    character.assigned_lab_id = new_lab_id
    if new_lab_id is None:
        return

    new_lab = next(lab for lab in saga.laboratories if lab.id == new_lab_id)
    previous_owner = saga.character(new_lab.owner_id)
    if previous_owner is not None:
        previous_owner.assigned_lab_id = None
    new_lab.owner_id = character.id


def assign_laboratory_owner(
    saga: Saga, lab: Laboratory, new_owner_id: str | None
) -> None:
    """Owner reassignment from the laboratory's side -- the inverse of
    assign_laboratory(), with the same two-way sync."""
    if new_owner_id is None:
        if lab.owner_id is not None:
            old_owner = saga.character(lab.owner_id)
            if old_owner is not None:
                old_owner.assigned_lab_id = None
            lab.owner_id = None
        return
    new_owner = next(c for c in saga.characters if c.id == new_owner_id)
    assign_laboratory(saga, new_owner, lab.id)


def add_raw_vis(pool: dict[str, int], art: str, pawns: int) -> None:
    """Add `pawns` of `art` to a Raw Vis pool (merging with any already held)."""
    pool[art] = pool.get(art, 0) + pawns


def replace_raw_vis(pool: dict[str, int], old_art: str, art: str, pawns: int) -> None:
    """Replace the `old_art` entry of a Raw Vis pool with `pawns` of `art`;
    re-pointing it at an Art already held merges the pawns into it."""
    del pool[old_art]
    add_raw_vis(pool, art, pawns)


def boon_hook_params(
    detail: str,
    description: str,
    base: dict[str, str] | None = None,
    *,
    unknown: bool = False,
) -> dict[str, str]:
    """The `params` of a covenant Boon/Hook: `base` (any keys we don't own)
    plus the detail and description, each stored only when non-empty, and
    the Unknown mark when `unknown`."""
    params = {
        k: v
        for k, v in (base or {}).items()
        if k not in (BOON_HOOK_DETAIL, BOON_HOOK_DESCRIPTION, BOON_HOOK_UNKNOWN)
    }
    if detail.strip():
        params[BOON_HOOK_DETAIL] = detail.strip()
    if description.strip():
        params[BOON_HOOK_DESCRIPTION] = description.strip()
    if unknown:
        params[BOON_HOOK_UNKNOWN] = "yes"
    return params
