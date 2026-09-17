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

SEASONS: tuple[str, ...] = ("Spring", "Summer", "Autumn", "Winter")


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


@dataclass
class VirtueFlawDef:
    """A catalog entry (shared reference data, not per-saga)."""

    id: str
    name: str
    type: VirtueFlawType
    category: str
    cost: float
    parameters: list[str] = field(default_factory=list)
    modifiers: list[Modifier] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VirtueFlawDef:
        d = dict(data)
        d["modifiers"] = [Modifier(**m) for m in d.get("modifiers", [])]
        return cls(**d)


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
    score: int = 0
    specialty: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ability:
        return cls(**data)


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
class Laboratory:
    id: str
    covenant_id: str
    owner_id: str | None = None
    size: int = 0
    aura: int = 0
    features: list[str] = field(default_factory=list)
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Laboratory:
        d = dict(data)
        d["virtues_flaws"] = [
            VirtueFlawInstance(**vf) for vf in d.get("virtues_flaws", [])
        ]
        return cls(**d)


@dataclass
class Character:
    id: str
    name: str
    type: CharacterType
    covenant_id: str | None = None
    characteristics: Characteristics = field(default_factory=Characteristics)
    arts: dict[str, int] = field(default_factory=dict)
    abilities: list[Ability] = field(default_factory=list)
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    spells_known: list[str] = field(default_factory=list)  # Spell ids
    assigned_lab_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Character:
        d = dict(data)
        d["characteristics"] = Characteristics.from_dict(d.get("characteristics") or {})
        d["abilities"] = [Ability.from_dict(a) for a in d.get("abilities", [])]
        d["virtues_flaws"] = [
            VirtueFlawInstance(**vf) for vf in d.get("virtues_flaws", [])
        ]
        return cls(**d)


@dataclass
class Covenant:
    id: str
    saga_id: str
    name: str
    vis_stock: dict[str, int] = field(default_factory=dict)
    library_id: str | None = None
    notes: str = ""


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
