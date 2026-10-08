"""Catalog definitions loaded from data/: Virtues and Flaws, spells,
equipment and the rest."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import (
    ABILITY_CATEGORIES,
    LAB_CHARACTERISTICS,
    VIRTUE_FLAW_AUDIENCES,
    VIRTUE_FLAW_SIDE,
    BoonHookType,
    CharacterType,
    CharacterVirtueFlawType,
    Modifier,
    VirtueFlawTier,
    VirtueFlawType,
    _validate_vf_tier_cost,
    known_fields,
)
from .holdings import GEAR_QUALITIES
from .laboratory import LAB_SPECIALIZATIONS


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
