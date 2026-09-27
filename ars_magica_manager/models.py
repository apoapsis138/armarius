"""Data model for sagas, covenants, characters, laboratories, and books.

See DESIGN.md sections 4-6 for the entity relationships and the reasoning
behind the Virtue/Flaw modifier system.
"""

from __future__ import annotations

import math
import re
import uuid
from dataclasses import dataclass, field, fields
from typing import Any, Literal

from .arts import ART_BY_NAME, ARTS, TECHNIQUES
from .totals import validate_modifier_type

CharacterType = Literal["magus", "companion", "grog"]
VirtueFlawType = Literal["Virtue", "Flaw"]
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


def round_away_from_zero(value: float) -> int:
    """Round a fraction to a whole number by increasing its magnitude (2.4 ->
    3, -2.4 -> -3), per the user's "round up fractions" rule for covenant
    finances. A plain `math.ceil` would be wrong for a negative figure (Base
    Loyalty can be negative): `ceil(-2.4)` is -2, which softens the number
    instead of rounding it up."""
    return math.ceil(value) if value >= 0 else -math.ceil(-value)


def known_fields(cls: type, data: dict[str, Any]) -> dict[str, Any]:
    """`data` filtered down to keys that are still fields of `cls`, so
    `cls(**known_fields(cls, data))` tolerates a stale key from an older save
    (a field since removed) instead of raising a TypeError."""
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in names}


SEASONS: tuple[str, ...] = ("Spring", "Summer", "Autumn", "Winter")

#: The 8 "Laboratory Characteristics" (ArM5 Chapter 8) -- unlike human
#: Characteristics these start at 0 and are cheap to change. Each name here
#: doubles as a LabCharacteristics field name and a
#: LabVirtueFlawDef.characteristic_modifiers key.
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
)


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
    """A catalog entry (shared reference data, not per-saga)."""

    id: str
    name: str
    type: VirtueFlawType
    category: str
    tier: VirtueFlawTier
    cost: float
    parameters: list[str] = field(default_factory=list)
    modifiers: list[Modifier] = field(default_factory=list)
    description: str = ""

    def __post_init__(self) -> None:
        _validate_vf_tier_cost(self.id, self.tier, self.cost)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VirtueFlawDef:
        d = dict(data)
        d["modifiers"] = [Modifier(**m) for m in d.get("modifiers", [])]
        return cls(**d)


@dataclass
class LabVirtueFlawDef:
    """A catalog entry for a Laboratory Virtue/Flaw (ArM5 Chapter 8) --
    shared reference data, not per-saga. Distinct from VirtueFlawDef:
    labs have their own separate Virtues & Flaws list, not the character
    one (a lab and a magus are different "characters" with different
    catalogs, even though both use Free/Minor/Major tiers).

    `characteristic_modifiers` is the parsed numeric effect on one or more
    of LAB_CHARACTERISTICS (e.g. Superior Construction -> {"safety": 3}),
    used to auto-compute the virtue/flaw component of each Characteristic's
    manual + virtue_sum + flaw_sum = total (see
    laboratories.lab_characteristic_total).
    Any Specialization grant mentioned in the rules text is left as prose
    in `description` only: the user enters it as a LabSpecialtyEntry until
    the catalog carries the grants (STORY-804).

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
    characteristic_modifiers: dict[str, int] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        _validate_vf_tier_cost(self.id, self.tier, self.cost)
        for characteristic in self.characteristic_modifiers:
            if characteristic not in LAB_CHARACTERISTICS:
                raise ValueError(
                    f"Unknown Lab Characteristic {characteristic!r} for "
                    f"{self.id!r}; must be one of {LAB_CHARACTERISTICS}"
                )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabVirtueFlawDef:
        return cls(**data)


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
    stack) -- see covenants.covenant_modifiers().
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

    def __post_init__(self) -> None:
        _validate_vf_tier_cost(self.id, self.tier, self.cost)
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
        d["modifiers"] = [Modifier(**m) for m in d.get("modifiers", [])]
        return cls(**d)


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

    def __post_init__(self) -> None:
        if self.category not in ABILITY_CATEGORIES:
            raise ValueError(
                f"Unknown ability category {self.category!r}; "
                f"must be one of {ABILITY_CATEGORIES}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AbilityDef:
        return cls(**data)


@dataclass
class HouseDef:
    """A catalog entry for one of the 12 Hermetic Houses (shared reference
    data, not per-saga). No mechanical bonus is modeled yet -- see
    HermeticBackground's docstring."""

    id: str
    name: str
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HouseDef:
        return cls(**data)


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
        return cls(**data)


@dataclass
class Ability:
    name: str
    category: str = "General"
    level: int = 0
    xp: int = 0
    #: XP needed for the next level, typed by hand -- a placeholder, not a
    #: computed formula (see DESIGN.md's "tracker, not rules engine" stance).
    xp_to_next: int = 0
    specialty: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ability:
        d = dict(data)
        if "score" in d and "level" not in d:
            # Pre-Phase-1b saves used "score"; migrate on load so existing
            # characters don't become unreadable over a field rename.
            d["level"] = d.pop("score")
        return cls(**d)


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
    #: Where it's published: one of SPELL_SOURCES, or free text.
    source: str = "ArM5"
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
#: Where spells are published: the Definitive Edition core rules, then the
#: supplements the Grand Grimoire collects.
SPELL_SOURCES: dict[str, str] = {
    "ArM5": "Ars Magica Definitive Edition",
    "HoHTL": "Houses of Hermes: True Lineages",
    "HoHMC": "Houses of Hermes: Mystery Cults",
    "HoHS": "Houses of Hermes: Societates",
    "TMRE": "The Mysteries Revised Edition",
    "A&A": "Art & Academe",
}


#: The kinds of book a library holds (reference/Libraries.md).
BOOK_TYPES: tuple[str, ...] = (
    "Art Summa",
    "Ability Summa",
    "Tractatus",
    "Lab Text",
    "Casting Tablet",
    "Other",
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

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], spell_names: dict[str, str] | None = None
    ) -> Book:
        d = dict(data)
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
        return cls(**data)


@dataclass
class NamedDescription:
    """A name + a free-text description -- shared shape for a Laboratory's
    Rooms and its Inventory "items that influence the lab"."""

    name: str
    description: str = ""


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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabFeatureDef:
        specializations: list[str] = []
        for name in data["specializations"]:
            specializations += TECHNIQUES if name == "Any Technique" else [name]
        unknown = set(specializations) - set(LAB_SPECIALIZATIONS)
        if unknown:
            raise ValueError(f"Unknown Specializations {unknown} for {data['id']!r}")
        return cls(
            data["id"], data["name"], data["description"], tuple(specializations)
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
        d["allocations"] = [LabSpecialtyGrant(**g) for g in d.get("allocations", [])]
        d["focus_allocations"] = [
            LabSpecialtyGrant(**g) for g in d.get("focus_allocations", [])
        ]
        return cls(**known_fields(cls, d))


def _feature_from_old_text(
    text: str, feature_names: dict[str, str] | None = None
) -> LabFeature:
    """A pre-STORY-308 free-text Feature as a LabFeature named with the text,
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
    return LabFeature(id=new_instance_id(), name=text, feature_id=feature_id)


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
    """A pre-STORY-307 free-text Specialty ("Terram +1") as an entry: the
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
    year: int
    season: str = "Spring"  # one of SEASONS
    name: str = ""
    details: str = ""
    #: One of LAB_ACTIVITIES, or "" when not set.
    activity: str = ""


@dataclass
class Laboratory:
    id: str
    #: None while the lab isn't assigned to a covenant (a legal state).
    covenant_id: str | None
    name: str
    owner_id: str | None = None
    location: str = ""
    build_points: int = 0
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Laboratory:
        d = dict(data)
        d.pop("aura", None)  # moved to Covenant.aura -- discard the old per-lab value
        legacy_size = d.pop("size", None)
        if "characteristics" not in d:
            d["characteristics"] = LabCharacteristics(size=legacy_size or 0)
        else:
            d["characteristics"] = LabCharacteristics.from_dict(d["characteristics"])
        d["rooms"] = [NamedDescription(**r) for r in d.get("rooms", [])]
        d["inventory_items"] = [
            NamedDescription(**i) for i in d.get("inventory_items", [])
        ]
        d["diary"] = [DiaryEntry(**entry) for entry in d.get("diary", [])]
        d["virtues_flaws"] = [
            VirtueFlawInstance(**vf) for vf in d.get("virtues_flaws", [])
        ]
        for vf in d["virtues_flaws"]:
            vf.id = vf.id or new_instance_id()
        old_features = [f for f in d.get("features", []) if isinstance(f, str)]
        d["features"] = [
            _feature_from_old_text(f)  # pre-STORY-308 free text
            if isinstance(f, str)
            else LabFeature.from_dict(f)
            for f in d.get("features", [])
        ]
        d["specialties"] = [
            _parse_old_specialty(s)
            if isinstance(s, str)  # pre-STORY-307 free text
            else LabSpecialtyEntry(**s)
            for s in d.get("specialties", [])
        ]
        lab = cls(**known_fields(cls, d))
        if old_features:
            link_unlinked_features(lab)
        return lab


@dataclass
class ArtScore:
    """A magus's score in one Art: the working Level, and total XP spent.

    These are stored independently rather than deriving Level from XP --
    v1 is a tracker, not a rules engine (see DESIGN.md section 2), so
    there's no XP-to-Level formula applied here yet.
    """

    level: int = 0
    xp: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtScore:
        return cls(**data)


@dataclass
class Background:
    """Character-sheet page 1's biographical block (not the paper sheet's
    "Description" box -- see Description below for that)."""

    player: str = ""
    setting: str = ""
    size: int = 0
    confidence_score: int = 0
    confidence_points: int = 0
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
            # Pre-STORY-208 saves used a single "confidence"; migrate on load
            # so existing characters don't become unreadable over the split.
            d["confidence_score"] = d.pop("confidence")
        return cls(**d)


@dataclass
class Description:
    height: float | None = None
    weight: float | None = None
    hair: str = ""
    eyes: str = ""
    handedness: Handedness = "right"
    physical_description: str = ""
    #: Free-text biography, distinct from physical_description (the paper
    #: sheet's short free-text box) -- added for STORY-207's Biographical
    #: Detail section.
    biography: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Description:
        return cls(**data)


@dataclass
class Aging:
    """Decrepitude and Warping. Warping is tracked as Score/Points, the same
    shape as an Ability's Level/XP -- but nothing derives one from the other
    yet; both are plain stored values (see ArtScore's docstring for why)."""

    decrepitude: int = 0
    effects: str = ""
    warping_score: int = 0
    warping_points: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Aging:
        return cls(**data)


@dataclass
class Wounds:
    """Simple per-severity counts, not individual wound records -- matches
    checking boxes on the paper sheet, not the calculated Wound Penalty."""

    light: int = 0
    medium: int = 0
    heavy: int = 0
    incapacitated: bool = False
    dead: bool = False
    #: Typed in, not derived from Stamina/armor/Virtues -- same "tracker, not
    #: rules engine" treatment as everything else (see DESIGN.md, STORY-205).
    soak: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Wounds:
        return cls(**data)


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
        return cls(**data)


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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Character:
        d = dict(data)
        d["characteristics"] = Characteristics.from_dict(d.get("characteristics") or {})
        d["arts"] = {
            art: ArtScore.from_dict(score) for art, score in d.get("arts", {}).items()
        }
        d["abilities"] = [Ability.from_dict(a) for a in d.get("abilities", [])]
        d["virtues_flaws"] = [
            VirtueFlawInstance(**vf) for vf in d.get("virtues_flaws", [])
        ]
        d["background"] = Background.from_dict(d.get("background") or {})
        d["description"] = Description.from_dict(d.get("description") or {})
        d["aging"] = Aging.from_dict(d.get("aging") or {})
        d["wounds"] = Wounds.from_dict(d.get("wounds") or {})
        d["personality_traits"] = [
            ScoredTrait(**t) for t in d.get("personality_traits", [])
        ]
        d["reputations"] = [ScoredTrait(**t) for t in d.get("reputations", [])]
        d["hermetic"] = HermeticBackground.from_dict(d.get("hermetic") or {})
        d["invented_spells"] = [
            Spell.from_dict(sp) for sp in d.get("invented_spells", [])
        ]
        d["inventory"] = [
            # Pre-STORY-203 saves held plain description strings.
            Possession(id=f"{data['id']}-inv-{i}", kind="item", name=item)
            if isinstance(item, str)
            else Possession(**known_fields(Possession, item))
            for i, item in enumerate(d.get("inventory", []))
        ]
        d["spells_known"] = [
            # Pre-STORY-203 saves held bare spell ids.
            KnownSpell(spell_id=entry)
            if isinstance(entry, str)
            else KnownSpell.from_dict(entry)
            for entry in d.get("spells_known", [])
        ]
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
    engine" stance and STORY-206 Slice 5)."""

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


@dataclass
class Familiar:
    """A magus's bound familiar (ArM5 Familiars). One per magus at a time,
    nested under its magus in the nav tree, but its own top-level entity
    (own sheet) rather than a field on Character -- see kanban STORY-206.

    `character_id` is the magus who bound it: required, set once at
    creation, and never reassigned to a different magus.

    Built in slices (STORY-206), all now landed onto this one dataclass, the
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
    #: treatment as Wounds.soak (see DESIGN.md, STORY-205/206 Slice 2).
    base_soak: int = 0
    magic_resistance: int = 0
    wounds: Wounds = field(default_factory=Wounds)
    fatigue_level: FatigueLevel = "fresh"
    #: Bite/Claws/Dodge etc. -- a free list of weapon-kind Possessions (same
    #: shape as Character.inventory's weapons, see STORY-205), not a fixed
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
            VirtueFlawInstance(**vf) for vf in d.get("virtues_flaws", [])
        ]
        d["personality_traits"] = [
            ScoredTrait(**t) for t in d.get("personality_traits", [])
        ]
        d["reputations"] = [ScoredTrait(**t) for t in d.get("reputations", [])]
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

#: Catalog ids of the covenant Boons that are a "Style of Governance" (Free
#: Choices under Residents). The Loyalty section's Type of Governance follows
#: whichever of these the covenant has.
GOVERNANCE_STYLE_IDS: tuple[str, ...] = (
    "covbh_boon_free_autocracy",
    "covbh_boon_free_council",
    "covbh_boon_free_democracy",
    "covbh_boon_free_faux_feudalism",
    "covbh_boon_free_gerontocracy",
    "covbh_boon_free_militocracy",
    "covbh_boon_free_theocracy",
)


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
      points, which feed the covenant's finances), description. weapon only:
      weapon_init/weapon_attack/weapon_defense/weapon_damage (typed-in combat
      figures, no formula -- see DESIGN.md, STORY-205).
    * item: name, quantity, description.
    * vis_source: name, art, pawns, season (when it is harvested), location,
      physical_form, description.
    * vis_store (Raw Vis Stores): name, art, pawns, location, physical_form.

    `description` is user-written text that supports inline emphasis.
    """

    id: str
    kind: str
    name: str = ""
    lab_id: str | None = None
    description: str = ""
    location: str = ""
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
    weapon_init: int = 0  # weapon only
    weapon_attack: int = 0  # weapon only
    weapon_defense: int = 0  # weapon only
    weapon_damage: int = 0  # weapon only
    art: str = ""
    pawns: int = 0
    season: str = ""  # one of SEASONS
    physical_form: str = ""

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
    Familiarity, Actions and Events, and Magical Influence stay free-form
    (meant to come from Diary entries once that tab exists)."""

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
        return cls(**d)


@dataclass
class Covenant:
    id: str
    saga_id: str
    name: str
    notes: str = ""
    aura: int = 0  # inherited by all of the covenant's laboratories
    tribunal: str = ""
    year_founded: int | None = None
    aegis_of_the_hearth: int = 0
    aegis_penetration: int = 0
    living_conditions_magi: int = 0
    living_conditions_mundane: int = 0
    #: The covenant's life stage (ArM5 Chapter 6, "Covenant Seasons") -- one
    #: of SEASONS. Not the calendar season, which lives on the Saga.
    covenant_season: str = "Spring"
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Covenant:
        d = dict(data)
        d["economics"] = Economics.from_dict(d.get("economics") or {})
        d["boons_hooks"] = [VirtueFlawInstance(**bh) for bh in d.get("boons_hooks", [])]
        d["reputations"] = [ScoredTrait(**r) for r in d.get("reputations", [])]
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


def next_season(season: str, year: int) -> tuple[str, int]:
    """The season after (season, year). The ArM5 year begins in Spring, so
    Winter rolls over into Spring of the following year."""
    index = SEASONS.index(season)
    if index == len(SEASONS) - 1:
        return SEASONS[0], year + 1
    return SEASONS[index + 1], year


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
    spells: list[Spell] = field(default_factory=list)
    familiars: list[Familiar] = field(default_factory=list)
    #: The app version that last saved this saga (storage.save_saga sets it;
    #: "" for a save older than versioning), for upgrading old saves later.
    app_version: str = ""

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
        d["spells"] = [Spell.from_dict(s) for s in d.get("spells", [])]
        spell_names = {s.id: s.name for s in d["spells"]}
        d["books"] = [Book.from_dict(b, spell_names) for b in d.get("books", [])]
        # Older saves kept a Library record per covenant listing its book ids;
        # ownership now lives on the book itself.
        for library in d.pop("libraries", None) or []:
            ids = set(library.get("books") or [])
            for book in d["books"]:
                if book.id in ids and book.owner_kind is None:
                    book.owner_kind = "covenant"
                    book.owner_id = library.get("covenant_id")
        return cls(**known_fields(cls, d))


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
    detail: str, description: str, base: dict[str, str] | None = None
) -> dict[str, str]:
    """The `params` of a covenant Boon/Hook: `base` (any keys we don't own)
    plus the detail and description, each stored only when non-empty."""
    params = {
        k: v
        for k, v in (base or {}).items()
        if k not in (BOON_HOOK_DETAIL, BOON_HOOK_DESCRIPTION)
    }
    if detail.strip():
        params[BOON_HOOK_DETAIL] = detail.strip()
    if description.strip():
        params[BOON_HOOK_DESCRIPTION] = description.strip()
    return params
