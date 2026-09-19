"""Data model for sagas, covenants, characters, laboratories, and libraries.

See DESIGN.md sections 4-6 for the entity relationships and the reasoning
behind the Virtue/Flaw modifier system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from .totals import validate_modifier_type

CharacterType = Literal["magus", "companion", "grog"]
BookType = Literal["Summa", "Tractatus", "Lab Text"]
VirtueFlawType = Literal["Virtue", "Flaw"]
VirtueFlawTier = Literal["Free", "Minor", "Major"]
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

TECHNIQUES: tuple[str, ...] = ("Creo", "Intellego", "Muto", "Perdo", "Rego")
FORMS: tuple[str, ...] = (
    "Animal",
    "Aquam",
    "Auram",
    "Corpus",
    "Herbam",
    "Ignem",
    "Imaginem",
    "Mentem",
    "Terram",
    "Vim",
)
ART_ABBREVIATIONS: dict[str, str] = {
    "Creo": "Cr",
    "Intellego": "In",
    "Muto": "Mu",
    "Perdo": "Pe",
    "Rego": "Re",
    "Animal": "An",
    "Aquam": "Aq",
    "Auram": "Au",
    "Corpus": "Co",
    "Herbam": "He",
    "Ignem": "Ig",
    "Imaginem": "Im",
    "Mentem": "Me",
    "Terram": "Te",
    "Vim": "Vi",
}


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
    manual + virtue_sum + flaw_sum = total (see lab_characteristic_total).
    Any Specialization grant mentioned in the rules text is left as prose
    in `description` only -- Lab Specialties are freeform for now, not a
    structured/auto-applied catalog concept yet.

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
    """A catalog Virtue/Flaw as attached to a specific Character or Laboratory."""

    vf_id: str
    params: dict[str, str] = field(default_factory=dict)


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
    id: str
    name: str
    technique: str
    form: str
    level: int
    description: str = ""


@dataclass
class Book:
    id: str
    type: BookType
    subject: str
    quality: int = 0
    level: int | None = None  # Summa and Lab Texts have a level; Tractatus does not
    author: str = ""
    spell_id: str | None = None  # set when type == "Lab Text"
    notes: str = ""


@dataclass
class Library:
    id: str
    covenant_id: str
    books: list[str] = field(default_factory=list)  # Book ids


@dataclass
class LabCharacteristics:
    """The 8 Laboratory Characteristics' manual (base) component only.

    Each Characteristic's effective total is manual + virtue_sum +
    flaw_sum (see lab_characteristic_total) -- virtue_sum/flaw_sum are
    derived from the lab's attached Virtues/Flaws, never stored here.
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


@dataclass
class DiaryEntry:
    year: int
    season: str = "Spring"  # one of SEASONS
    name: str = ""
    details: str = ""


@dataclass
class Laboratory:
    id: str
    covenant_id: str
    name: str
    owner_id: str | None = None
    location: str = ""
    build_points: int = 0
    characteristics: LabCharacteristics = field(default_factory=LabCharacteristics)
    features: list[str] = field(default_factory=list)
    specialties: list[str] = field(default_factory=list)
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
        return cls(**d)


def lab_net_vf_points(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """Current Virtue points minus Flaw points attached to the lab."""
    return sum(
        catalog_by_id[vf.vf_id].cost
        for vf in lab.virtues_flaws
        if vf.vf_id in catalog_by_id
    )


def lab_occupied_size(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """OCCUPIED SIZE: current Virtue points - Flaw points - Refinement."""
    return lab_net_vf_points(lab, catalog_by_id) - lab.characteristics.refinement


def lab_free_virtues(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """How many more points of Virtues (minus Flaws) the lab has room for:
    (Size + Refinement) - current Virtue points minus Flaw points."""
    limit = lab.characteristics.size + lab.characteristics.refinement
    return limit - lab_net_vf_points(lab, catalog_by_id)


def lab_base_safety(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """BASE SAFETY OF LAB: Refinement - occupied Size (if positive)."""
    occupied = lab_occupied_size(lab, catalog_by_id)
    return lab.characteristics.refinement - max(occupied, 0)


def lab_characteristic_total(
    lab: Laboratory,
    catalog_by_id: dict[str, LabVirtueFlawDef],
    characteristic: str,
) -> tuple[int, int, int, int]:
    """(manual, virtue_sum, flaw_sum, total) for one of LAB_CHARACTERISTICS.

    manual + virtue_sum + flaw_sum = total, per the user's explicit
    formula: the manual component is a free player adjustment on top of
    whatever the lab's attached Virtues/Flaws contribute.
    """
    manual = getattr(lab.characteristics, characteristic)
    virtue_sum = 0
    flaw_sum = 0
    for vf in lab.virtues_flaws:
        entry = catalog_by_id.get(vf.vf_id)
        if entry is None:
            continue
        amount = entry.characteristic_modifiers.get(characteristic, 0)
        if entry.type == "Virtue":
            virtue_sum += amount
        else:
            flaw_sum += amount
    return manual, virtue_sum, flaw_sum, manual + virtue_sum + flaw_sum


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
    confidence: int = 0
    birth_name: str = ""
    year_born: int | None = None
    race_nationality: str = ""
    place_of_origin: str = ""
    religion: str = ""
    title_profession: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Background:
        return cls(**data)


@dataclass
class Description:
    height: float | None = None
    weight: float | None = None
    hair: str = ""
    eyes: str = ""
    handedness: Handedness = "right"
    physical_description: str = ""

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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Wounds:
        return cls(**data)


@dataclass
class ScoredTrait:
    """A name + integer score. Shared shape for Personality Traits and
    Reputations -- both are just a label and a score on the character sheet."""

    name: str
    score: int


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
    spells_known: list[str] = field(default_factory=list)  # Spell ids
    inventory: list[str] = field(default_factory=list)  # freeform item descriptions
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
        return cls(**d)


def character_age(year_born: int | None, current_year: int) -> int | None:
    """The character's age this saga-year, or None if Year Born isn't set.

    Not a Character property -- Character has no back-reference to the Saga
    that holds `current_year`, so this takes it explicitly instead, the same
    way an XP-to-Level formula would (see ArtScore's docstring).
    """
    return None if year_born is None else current_year - year_born


@dataclass
class Covenant:
    id: str
    saga_id: str
    name: str
    vis_stock: dict[str, int] = field(default_factory=dict)
    library_id: str | None = None
    notes: str = ""
    aura: int = 0  # inherited by all of the covenant's laboratories


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
    libraries: list[Library] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    spells: list[Spell] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Saga:
        d = dict(data)
        d["covenants"] = [Covenant(**c) for c in d.get("covenants", [])]
        d["characters"] = [Character.from_dict(c) for c in d.get("characters", [])]
        d["laboratories"] = [
            Laboratory.from_dict(lab) for lab in d.get("laboratories", [])
        ]
        d["libraries"] = [Library(**lib) for lib in d.get("libraries", [])]
        d["books"] = [Book(**b) for b in d.get("books", [])]
        d["spells"] = [Spell(**s) for s in d.get("spells", [])]
        return cls(**d)
