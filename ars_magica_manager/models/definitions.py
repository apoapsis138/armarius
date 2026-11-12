"""Catalog definitions loaded from data/: Virtues and Flaws, spells,
equipment and the rest."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import (
    ABILITY_CATEGORIES,
    LAB_CHARACTERISTICS,
    LAB_VF_PARAMETERS,
    REALMS,
    VIRTUE_FLAW_AUDIENCES,
    VIRTUE_FLAW_SIDE,
    XP_TABLES,
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


@dataclass(frozen=True)
class VirtueFlawDef:
    """A character Virtue/Flaw catalog entry (shared reference data, not
    per-saga).

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
    it. The picker hides what a character can't take (rules.vf_eligibility).
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


@dataclass(frozen=True)
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
    total (rules.lab_stats.lab_characteristic_total).
    A Specialization grant is a `lab_specialization` modifier:
    its `target` names the Specialization, or is "{specialization}" when the
    lab's owner picks it from `choices["specialization"]` as the Virtue is
    added (the pick is the instance's params). Grants the book leaves to
    distribute ("2 points on any Specialization(s)") stay prose, entered as
    LabSpecialtyEntry sources.

    `repeatable` marks the (asterisked in the book) entries a lab can hold
    more than once -- e.g. two Lesser Features -- so the picker shouldn't
    exclude them just because one's already attached.

    `parameters` are what the owner enters as the Virtue is added, from
    LAB_VF_PARAMETERS: "intelligence" (a whole number) and "servant" (a
    grog's id, whose Intelligence is used instead) and "illusory" (the
    name of the lab's Virtue an Illusion negates) and "cost" (what an Empty
    lab pays, Upkeep or Health). A modifier reads one
    with `amount_param` (Servant: Safety +half the servant's Intelligence).
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
    parameters: list[str] = field(default_factory=list)
    description: str = ""
    #: The book(s) it's from (sourcebooks); every entry so far is Covenants'.
    source: str = "Covenants"

    def __post_init__(self) -> None:
        _validate_vf_tier_cost(self.id, self.tier, self.cost)
        for options in self.choices.values():
            unknown = set(options) - set(LAB_SPECIALIZATIONS)
            if unknown:
                raise ValueError(f"Unknown Specializations {unknown} for {self.id!r}")
        unknown_params = set(self.parameters) - set(LAB_VF_PARAMETERS)
        if unknown_params:
            raise ValueError(f"Unknown parameters {unknown_params} for {self.id!r}")
        for modifier in self.modifiers:
            if (
                modifier.amount_param is not None
                and modifier.amount_param not in self.parameters
            ):
                raise ValueError(
                    f"{self.id!r} reads {modifier.amount_param!r}, "
                    "which isn't one of its parameters"
                )
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
        in catalog order (read from `modifiers`); one read from a parameter
        is in `characteristic_readings` instead."""
        amounts: dict[str, float] = {}
        for modifier in self.modifiers:
            if (
                modifier.applies_to == "lab_characteristic"
                and modifier.target
                and modifier.amount_param is None
            ):
                amounts[modifier.target] = amounts.get(modifier.target, 0) + (
                    modifier.amount or 0
                )
        return amounts

    @property
    def characteristic_readings(self) -> list[Modifier]:
        """Its effects on the Characteristics that are read from a
        parameter (Servant's Safety), in catalog order."""
        return [
            m
            for m in self.modifiers
            if m.applies_to == "lab_characteristic" and m.amount_param is not None
        ]

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


@dataclass(frozen=True)
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

    `parameters` lists what the entry names when it is taken, as a
    Virtue's do ("{form}" in "Vis Source ({form})"): none of the books'
    entries has any, but a saga's own may. Each is stored in the instance's
    params beside its detail and description.

    `unknown` marks the Minor Hooks the book says "may be Unknown": an
    attached one can then be marked Unknown (BOON_HOOK_UNKNOWN) and counts
    3 points. `source` names the book(s) the entry comes from ("ArM5",
    "Covenants" or "ArM5; Covenants"), for attribution -- the text is
    CC-BY-SA.
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
    parameters: list[str] = field(default_factory=list)

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


@dataclass(frozen=True)
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


#: The eight Characteristics, as an Ability's roll names them.
ROLL_CHARACTERISTICS: tuple[str, ...] = (
    "Intelligence",
    "Perception",
    "Strength",
    "Stamina",
    "Presence",
    "Communication",
    "Dexterity",
    "Quickness",
)


@dataclass(frozen=True)
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
    #: A hedge Art's part in its tradition's magic ("Technique", "Form",
    #: "Method", "Power", "Rune", "Practice", "Foe"); "" for any other
    #: Ability.
    role: str = ""
    #: The xp table it advances on (XP_TABLES): "ability", or "art" for an
    #: Accelerated Ability or a hedge Art that isn't Difficult.
    xp_table: str = "ability"
    #: A saga's own Supernatural Ability: the realm it is affiliated with
    #: ("" for none given), and the Characteristic its rolls add (""
    #: when it varies), as Houses of Hermes: Societates p. 104 designs one.
    realm: str = ""
    characteristic: str = ""

    def __post_init__(self) -> None:
        if self.category not in ABILITY_CATEGORIES:
            raise ValueError(
                f"Unknown ability category {self.category!r}; "
                f"must be one of {ABILITY_CATEGORIES}"
            )
        if self.xp_table not in XP_TABLES:
            raise ValueError(
                f"Unknown xp table {self.xp_table!r}; must be one of {XP_TABLES}"
            )
        if self.realm and self.realm not in REALMS:
            raise ValueError(
                f"Ability {self.name!r}: unknown realm {self.realm!r}; "
                f"must be one of {REALMS}"
            )
        if self.characteristic and self.characteristic not in ROLL_CHARACTERISTICS:
            raise ValueError(
                f"Ability {self.name!r}: unknown Characteristic "
                f"{self.characteristic!r}; must be one of {ROLL_CHARACTERISTICS}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AbilityDef:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
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


HEDGE_TRADITION = "Hedge Tradition"
MYSTERY_CULT = "Mystery Cult"
#: What kind of tradition one is, cutting across the books. Each term is
#: the books' own: House Ex Miscellanea's traditions (HoH:S), Mystery Cults
#: (TMRE, HoH:MC), hedge traditions (HMRE), faerie wizardry (RoP:F pp.
#: 135-136), holy traditions (RoP:D p. 47), infernal traditions (RoP:I),
#: rival traditions (RM pp. 6, 8) and ancient magic (AM).
TRADITION_CATEGORIES: tuple[str, ...] = (
    "Ex Miscellanea Tradition",
    MYSTERY_CULT,
    HEDGE_TRADITION,
    "Faerie Tradition",
    "Holy Tradition",
    "Infernal Tradition",
    "Rival Tradition",
    "Ancient Tradition",
)

#: The realms a non-Hermetic tradition's magic can belong to.
TRADITION_REALMS: tuple[str, ...] = ("Magic", "Faerie", "Divine", "Infernal")
#: Whether a tradition's members have The Gift: all, some or none.
TRADITION_GIFT: tuple[str, ...] = ("required", "optional", "never")


@dataclass(frozen=True)
class TraditionTraining:
    """How a tradition makes a new member at creation: the apprenticeship
    its book gives (Gifted and unGifted), the scores it leaves, and what
    a Gifted member's Opening gives. Names are Ability catalog names (a
    family filled in, "Craft: Runes"); Virtues are catalog ids."""

    gift: str = "optional"
    #: A Gifted member's apprenticeship: xp on the tradition's Arts and
    #: Abilities, and levels of its spells or scripts.
    xp: int = 0
    levels: int = 0
    #: An unGifted member's.
    ungifted_xp: int = 0
    ungifted_levels: int = 0
    #: Virtues that change the apprenticeship: id -> [xp, levels] each.
    modifiers: dict[str, list[int]] = field(default_factory=dict)
    #: The scores a Gifted member leaves apprenticeship with, at least.
    minimums: dict[str, int] = field(default_factory=dict)
    #: The Arts and Abilities a Gifted member's Opening gives, at 0.
    opening: list[str] = field(default_factory=list)
    #: Virtues the Opening gives free, outside the Virtue/Flaw balance.
    opening_virtues: list[str] = field(default_factory=list)
    #: Free Minor Virtues of `free_category` a Gifted member takes from
    #: the master, outside the balance.
    free_minor_virtues: int = 0
    free_category: str = "Supernatural"
    #: The highest score an Art on the Art table may have at creation;
    #: 0 for the usual rules.
    art_cap: int = 0
    #: The least of the apprenticeship xp spent on the tradition's Arts.
    arts_xp: int = 0
    #: The age the apprenticeship usually starts and the years it lasts;
    #: Later Life leaves those years out, as a magus's apprenticeship
    #: does (0: the book sets none).
    starts: int = 0
    years: int = 0
    #: What the worksheet can't yet apply, as the book words it.
    notes: str = ""

    def __post_init__(self) -> None:
        if self.gift not in TRADITION_GIFT:
            raise ValueError(
                f"Unknown gift rule {self.gift!r}; must be one of {TRADITION_GIFT}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraditionTraining:
        return cls(**known_fields(cls, data))


#: How a casting kind finds its scores (rules.hedge_casting.KINDS): a
#: Technique and a Form; one Ability; the lowest of the runes a script uses.
CASTING_KINDS: tuple[str, ...] = ("art_pair", "ability", "rune", "song")
#: The die a casting total adds.
CASTING_DICE: tuple[str, ...] = ("stress", "simple", "none")
#: How many pawns of vis a casting may use: each Art's score (the Hermetic
#: rule), the Ability or rune used, or the sum of the tradition's Forms.
VIS_CAPS: tuple[str, ...] = ("arts", "score", "forms", "none")
#: How a casting's botch dice are counted (CastingRule.botch).
BOTCH_RULES: tuple[str, ...] = ("hermetic", "magnitude", "none")
#: Hedge Magic's Magical Defenses (Hedge Magic RE, Ch. 1).
DEFENSE_KINDS: tuple[str, ...] = (
    "Accelerated Expiry",
    "Alacritous Fortune",
    "Confounding Magics",
    "Immovable Object",
    "Magical Fortitude",
    "Strength of Form",
)


@dataclass(frozen=True)
class CastingRule:
    """One way a tradition's members work magic, as data: which scores
    the total adds, the die, what it is divided by, and what happens when
    it falls short. A season's Lab Total (`lab`) adds no die."""

    name: str
    kind: str = "art_pair"
    #: The Characteristic every total adds; `characteristics` names one
    #: per Art or Ability instead (Animal Ken: Communication).
    characteristic: str = ""
    characteristics: dict[str, str] = field(default_factory=dict)
    #: The Arts or Abilities it uses: the Techniques and Forms of an
    #: art_pair, the Abilities of an ability kind, the runes. Empty: the
    #: tradition's Arts of that role.
    techniques: list[str] = field(default_factory=list)
    forms: list[str] = field(default_factory=list)
    scores: list[str] = field(default_factory=list)
    #: Abilities the total also adds (Rune Magic), and ones of which it
    #: adds the best (Refining's Medicine, Philosophiae or a realm Lore).
    adds: list[str] = field(default_factory=list)
    best_of: list[str] = field(default_factory=list)
    #: An Ability no score the rule uses may count above (Galdor Wisdom
    #: caps a Song Talent, Land of Fire & Ice p. 46).
    capped_by: str = ""
    die: str = "stress"
    divisor: int = 1
    #: The division rounds up instead of down (storm wizards' ice
    #: harvesting, Against the Dark p. 130).
    rounds_up: bool = False
    #: How far short a total may fall and still work, at a Fatigue cost;
    #: 0 when it must reach the level or Ease Factor.
    failure_margin: int = 0
    #: What the total is rolled against: a "level" or an "Ease Factor".
    against: str = "level"
    #: True when the effect's magnitude is the score used (5 x score is its
    #: level), as for Supernatural Abilities.
    magnitude_is_score: bool = False
    fatigue: str = ""
    vis_per_pawn: int = 2
    vis_cap: str = "arts"
    #: Which vis it may use, as the book words it.
    vis: str = ""
    #: Whether an unGifted member may boost it with vis.
    ungifted_vis: bool = True
    lab: bool = False
    penetrates: bool = True
    #: A roll the target makes even after Penetration (Poetic Justice).
    resistance: str = ""
    #: How many botch dice a stressed casting rolls (BOTCH_RULES):
    #: "hermetic", one, one a pawn of vis and a foreign aura's points;
    #: "magnitude", the effect's magnitude + the aura (an Amazon rite);
    #: "none". `botch_extra` adds to them (Wildfire's two), and
    #: `botch_notes` says what else does, as the book words it.
    botch: str = "hermetic"
    botch_extra: int = 0
    botch_notes: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        for value, allowed, what in (
            (self.kind, CASTING_KINDS, "casting kind"),
            (self.die, CASTING_DICE, "die"),
            (self.vis_cap, VIS_CAPS, "vis cap"),
            (self.botch, BOTCH_RULES, "botch rule"),
        ):
            if value not in allowed:
                raise ValueError(f"Unknown {what} {value!r}; must be one of {allowed}")
        if self.divisor < 1:
            raise ValueError("A casting divisor is at least 1")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CastingRule:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class MagicalDefense:
    """The Magical Defense one of a tradition's Arts or Abilities gives,
    and the effects it works against (its specialty)."""

    kind: str
    against: str

    def __post_init__(self) -> None:
        if self.kind not in DEFENSE_KINDS:
            raise ValueError(
                f"Unknown Magical Defense {self.kind!r}; must be one of {DEFENSE_KINDS}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MagicalDefense:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class DispelRule:
    """An active dispelling: a casting that ends another effect when its
    total reaches `multiple` x the effect's level (a Supernatural
    Ability's effect counting as 5 x its score)."""

    name: str
    #: The Art pair or Ability that casts it ("Take Curse").
    uses: str
    multiple: int = 1
    #: "level" (the dispelling effect's level + a stress die) or "total"
    #: (the caster's Casting Total).
    total: str = "level"
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DispelRule:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class GroupCasting:
    """How several members work one effect together: `helper` is what
    each helper adds ("Ceremony": Characteristic + the score used, as
    RoP: The Divine's Ceremony; a number: that bonus each), up to `most`
    helpers ("aura": the aura's strength; "Ceremony": the leader's
    Ceremony; a number), to the totals named in `applies_to`."""

    name: str
    helper: str = "Ceremony"
    most: str = "Ceremony"
    applies_to: list[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupCasting:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class OpeningRule:
    """How a Gifted master of the tradition Opens a Gifted student's Gift
    to it: the Opening Total's terms (a Characteristic, Abilities added,
    the highest and the lowest of some, the aura), and the Flaw a student
    takes for each of the tradition's Arts the master has below 2."""

    characteristic: str = "Intelligence"
    adds: list[str] = field(default_factory=list)
    highest_of: list[str] = field(default_factory=list)
    lowest_of: list[str] = field(default_factory=list)
    aura: bool = True
    #: The Flaw a flawed Opening gives (a catalog id), and the parameter
    #: that names the Art; "" when the troupe picks the Flaw.
    flaw: str = ""
    flaw_param: str = ""
    #: The Opening Total's bands, as multiples of the Opening Ease Factor:
    #: at least `opens_at` Opens the student; more than `keeps_over` keeps
    #: their Supernatural Abilities, or (when set) at least `keeps_at`.
    opens_at: int = 1
    keeps_over: int = 2
    keeps_at: int | None = None
    #: The Opening loses the Arts of any other tradition the student had.
    loses_other_arts: bool = False
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OpeningRule:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class InitiationScript:
    """One of the tradition's printed Initiation Scripts."""

    name: str
    ease_factor: int
    bonus: int
    #: What it gives, and the Ordeal, as the book names them.
    gains: str = ""
    ordeal: str = ""
    #: "gifted", "ungifted" or "" (either).
    who: str = ""
    notes: str = ""
    #: The Initiate's least scores, by Ability, below which the Script
    #: always fails (an Ability named without its subject, "Theology",
    #: counts the best of its kind).
    requires: tuple[tuple[str, int], ...] = ()
    #: The harder Ease Factor of a self-initiation, when the book gives
    #: one (the gruagachan's 18 and 30, HMRE p. 61); 0: the same.
    self_ease_factor: int = 0
    #: The Script's components as the book gives them, (what, bonus) in
    #: order (rules.mysteries.printed_components_note); () when the book
    #: gives only the total.
    components: tuple[tuple[str, int], ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InitiationScript:
        d = known_fields(cls, data)
        d["requires"] = tuple(
            (str(k), int(v)) for k, v in dict(d.get("requires") or {}).items()
        )
        d["components"] = tuple(
            (str(name), int(bonus)) for name, bonus in d.get("components") or ()
        )
        return cls(**d)


@dataclass(frozen=True)
class InitiationRule:
    """The tradition's Initiation Total (the Mystagogue's Characteristic +
    Lore + the Script's bonus) and its scripts. `roll_less`: the Forest
    Paths' kind, which gives its Flaw then its Virtue with no roll."""

    characteristic: str = "Presence"
    lore: str = ""
    self_initiation: bool = True
    roll_less: bool = False
    scripts: list[InitiationScript] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InitiationRule:
        d = known_fields(cls, data)
        d["scripts"] = [InitiationScript.from_dict(x) for x in d.get("scripts") or []]
        return cls(**d)


@dataclass(frozen=True)
class Advancement:
    """How the tradition's Arts advance besides the usual sources: whether
    they may be practised, and whether studied from vis."""

    practice_arts: bool = True
    vis_study: bool = False
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Advancement:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class TraditionActivity:
    """A season of the tradition's own work (Refining, brewing, inventing
    scripts...): Exposure in its Arts, with the Lab Total of the casting
    rule `lab_rule` (TraditionDef.casting) when it has one."""

    key: str
    label: str
    summary: str
    lab_rule: str = ""
    gifted_only: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraditionActivity:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class PoolDef:
    """A store of points the tradition's members keep (sparks, Prophecy
    Points, reagents...): what fills it each year, what spends it, and
    its cap, as the book words them."""

    name: str
    income: str = ""
    costs: str = ""
    cap: str = ""
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PoolDef:
        return cls(**known_fields(cls, data))


#: How a tradition's Warping is shown: the book's words only, or worked
#: out (an elementalist's elemental Personality Traits).
WARPING_KINDS = ("note", "elemental_traits")


@dataclass(frozen=True)
class WarpingRule:
    """What the tradition's members suffer in place of (or beside) the
    Hermetic Warping and Twilight: its name, what sets it off, and
    whether the app works it out."""

    name: str
    kind: str = "note"
    replaces_twilight: bool = False
    trigger: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if self.kind not in WARPING_KINDS:
            raise ValueError(
                f"Unknown kind {self.kind!r}; must be one of {WARPING_KINDS}"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WarpingRule:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class BondRule:
    """A being the tradition's members bind (a familiar, a fetch, a
    spirit, a golem): how it is bound and what it adds to its master."""

    name: str
    how: str = ""
    feeds: str = ""
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BondRule:
        return cls(**known_fields(cls, data))


#: How a guideline's base level grows with the magnitudes an effect adds
#: (rules.hedge_effects): "hermetic", 5 levels a magnitude and 1 below
#: level 5; "three", 3 levels a magnitude (Soqotran levels, the Augustan
#: and utiseta Ease Factors); "none", the guideline's level is the
#: effect's (a rune's level, an Ease Factor table's row).
LEVEL_STEPS: tuple[str, ...] = ("hermetic", "three", "none")
#: The parameters an effect names.
EFFECT_PARAMETER_KINDS: tuple[str, ...] = ("range", "duration", "target")


@dataclass(frozen=True)
class Guideline:
    """One of a tradition's guidelines: the Art pair, Ability, rune or
    incense it is for, its base level (or Ease Factor; 0 for a General
    guideline, whose level the effect sets), a short label and a one-line
    summary in the app's words, and its printed page."""

    name: str
    arts: list[str] = field(default_factory=list)
    level: int = 0
    summary: str = ""
    page: int = 0

    @property
    def general(self) -> bool:
        return self.level == 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Guideline:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class EffectParameter:
    """A Range, Duration or Target an effect of the tradition may have,
    and the magnitudes it adds. `arts`: only for effects using one of
    these Arts (a gruagach's Conversation costs nothing for Blessing and
    Curse, a magnitude for Shape and Vision); `items`: "items" or
    "effects" when it is only for one of them (a learned magician's
    amulets and charms), "" for both."""

    kind: str
    name: str
    magnitudes: int = 0
    arts: list[str] = field(default_factory=list)
    items: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if self.kind not in EFFECT_PARAMETER_KINDS:
            raise ValueError(
                f"Unknown parameter kind {self.kind!r}; must be one of "
                f"{EFFECT_PARAMETER_KINDS}"
            )
        if self.items not in ("", "items", "effects"):
            raise ValueError(f"Unknown items {self.items!r}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EffectParameter:
        return cls(**known_fields(cls, data))


@dataclass(frozen=True)
class TraditionDef:
    """A catalog entry for a non-Hermetic magical tradition (shared
    reference data, not per-saga): what its members learn, how they
    advance, and the chapter of the sheet that shows them. A character
    names the traditions they belong to; the tradition's Abilities are
    ordinary Ability catalog entries, which several traditions may share.
    """

    id: str
    name: str
    #: The book(s) it's from (sourcebooks), as on the other catalogs.
    source: str = "HMRE"
    realm: str = "Magic"
    #: The realm its magic reads an aura as outside a Magic aura, when not
    #: `realm`: the landvaettir's Faerie (Land of Fire & Ice p. 33).
    outside_magic: str = ""
    #: What kind of tradition it is (TRADITION_CATEGORIES), cutting across
    #: the books; set by hand from them, not worked out from its rules.
    category: str = HEDGE_TRADITION
    #: Other realms its magic can belong to, by version or practitioner
    #: (`realm` is the usual one, which the rules read), and why.
    other_realms: list[str] = field(default_factory=list)
    realm_note: str = ""
    description: str = ""
    #: The sheet chapter's title; the tradition's name when blank.
    chapter: str = ""
    #: Its Arts and Abilities (Ability catalog names), in the order the
    #: chapter lists them.
    abilities: list[str] = field(default_factory=list)
    #: The Abilities its members learn as favored ones.
    favored: list[str] = field(default_factory=list)
    #: The Virtues (catalog ids) membership requires or gives free.
    virtues: list[str] = field(default_factory=list)
    #: Seasons a year its members spend on their own work, and the xp
    #: they get from that work; 0 when the book sets none.
    working_seasons: int = 0
    working_xp: int = 0
    #: The free Social Status Virtue, if the tradition gives one.
    social_status: str = ""
    #: Its place in the Order of Hermes: "house" for a tradition of House
    #: Ex Miscellanea, whose magi take its Virtues as the House's free ones;
    #: "societas" for a Hermetic society any magus may join; "" for neither.
    hermetic: str = ""
    #: Rules the sheet can't yet apply, as the book words them.
    notes: str = ""
    #: How a new member is made at creation.
    training: TraditionTraining = field(default_factory=TraditionTraining)
    #: How its members cast (rules.hedge_casting), the Magical Defense each
    #: of its Arts or Abilities gives (by name), its active dispellings,
    #: and its group castings.
    casting: list[CastingRule] = field(default_factory=list)
    defenses: dict[str, MagicalDefense] = field(default_factory=dict)
    dispels: list[DispelRule] = field(default_factory=list)
    groups: list[GroupCasting] = field(default_factory=list)
    #: How a master Opens a student's Gift (None: the tradition doesn't),
    #: its initiations, how its Arts advance, and its own seasons' work.
    opening: OpeningRule | None = None
    initiation: InitiationRule | None = None
    advancement: Advancement = field(default_factory=Advancement)
    activities: list[TraditionActivity] = field(default_factory=list)
    #: The beings its members bind, the pools they keep, and the
    #: tradition's own Warping (None: the Hermetic rules).
    bonds: list[BondRule] = field(default_factory=list)
    pools: list[PoolDef] = field(default_factory=list)
    warping: WarpingRule | None = None
    #: Its guideline table, the Ranges, Durations and Targets its effects
    #: may have (none listed: the Hermetic ones), the parameters an Art's
    #: guidelines already include (Art -> kind -> name: a utiseta's base
    #: Range, an Amazon Consonant's), so only the steps from them cost;
    #: `bases_either_way` when a step down costs as a step up does (the
    #: Amazons'), how magnitudes add to a level (LEVEL_STEPS), and the book
    #: and pages of the table.
    guidelines: list[Guideline] = field(default_factory=list)
    effect_parameters: list[EffectParameter] = field(default_factory=list)
    parameter_bases: dict[str, dict[str, str]] = field(default_factory=dict)
    bases_either_way: bool = False
    level_steps: str = "hermetic"
    guideline_source: str = ""

    def __post_init__(self) -> None:
        if self.level_steps not in LEVEL_STEPS:
            raise ValueError(
                f"Unknown level steps {self.level_steps!r}; must be one of "
                f"{LEVEL_STEPS}"
            )
        if self.realm not in TRADITION_REALMS:
            raise ValueError(
                f"Unknown realm {self.realm!r}; must be one of {TRADITION_REALMS}"
            )
        if self.category not in TRADITION_CATEGORIES:
            raise ValueError(
                f"Unknown category {self.category!r}; must be one of "
                f"{TRADITION_CATEGORIES}"
            )

    @property
    def title(self) -> str:
        """The chapter's title."""
        return self.chapter or self.name

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraditionDef:
        d = known_fields(cls, data)
        d["training"] = TraditionTraining.from_dict(d.get("training") or {})
        d["casting"] = [CastingRule.from_dict(c) for c in d.get("casting") or []]
        d["defenses"] = {
            name: MagicalDefense.from_dict(v)
            for name, v in (d.get("defenses") or {}).items()
        }
        d["dispels"] = [DispelRule.from_dict(v) for v in d.get("dispels") or []]
        d["groups"] = [GroupCasting.from_dict(v) for v in d.get("groups") or []]
        if d.get("opening") is not None:
            d["opening"] = OpeningRule.from_dict(d["opening"])
        if d.get("initiation") is not None:
            d["initiation"] = InitiationRule.from_dict(d["initiation"])
        d["advancement"] = Advancement.from_dict(d.get("advancement") or {})
        d["activities"] = [
            TraditionActivity.from_dict(v) for v in d.get("activities") or []
        ]
        d["bonds"] = [BondRule.from_dict(v) for v in d.get("bonds") or []]
        d["pools"] = [PoolDef.from_dict(v) for v in d.get("pools") or []]
        if d.get("warping") is not None:
            d["warping"] = WarpingRule.from_dict(d["warping"])
        d["guidelines"] = [Guideline.from_dict(v) for v in d.get("guidelines") or []]
        d["effect_parameters"] = [
            EffectParameter.from_dict(v) for v in d.get("effect_parameters") or []
        ]
        return cls(**d)


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class GrogTemplateDef:
    """One of Grogs' Chapter 7 Grog Templates (grog_template_catalog.json):
    the book's guidance for a kind of grog, which the player fills in by
    choosing from it. Ability lists are in the book's notation (scores,
    with "xp" toward the next), each list for one age; "{area}" and the
    like in a name are asked for when the template is used.

    `virtues_flaws` are the book's own set, taken unless unticked; `pool`
    the ones it suggests, each {"vf_id", "params", "note"?} or a single
    pick {"label", "one_of": [...]}. `variants` (each a dict with "name"
    and any of "statuses", "virtues_flaws", "ages", "renames" and
    "flaw_hint", replacing the template's own) are the book's versions
    of the template to choose between, under `variant_label`."""

    id: str
    name: str
    page: int
    concept: str = ""
    #: Social Status Virtues or Flaws (vf_ids) to choose from, the first
    #: offered first.
    statuses: list[str] = field(default_factory=list)
    virtues_flaws: list[dict[str, Any]] = field(default_factory=list)
    pool: list[dict[str, Any]] = field(default_factory=list)
    variant_label: str = ""
    variants: list[dict[str, Any]] = field(default_factory=list)
    #: The book's Characteristics, when it gives figures, and its advice.
    characteristics: dict[str, int] = field(default_factory=dict)
    characteristics_advice: str = ""
    #: [name, score] each, and single picks {"score", "options"}.
    traits: list[list[Any]] = field(default_factory=list)
    trait_choices: list[dict[str, Any]] = field(default_factory=list)
    reputations: list[list[Any]] = field(default_factory=list)
    #: Each {"age", "label"?, "native", "abilities"}; "native" names the
    #: Ability that is the Native Language.
    ages: list[dict[str, Any]] = field(default_factory=list)
    #: Shown with the extra Flaw fields: what the book suggests instead of
    #: a Flaw left out.
    flaw_hint: str = ""
    packages: str = ""
    notes: str = ""
    #: Where this entry differs from the page's text, and why.
    fixes: list[str] = field(default_factory=list)
    #: An animal grog's sample (animal_template_catalog.json): its "kind",
    #: "species", "language" and "size"; empty for a person.
    animal: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrogTemplateDef:
        return cls(**known_fields(cls, data))


#: The book's weapon tables a WeaponDef comes from, in its order.
WEAPON_TABLES: tuple[str, ...] = ("melee", "missile", "natural")


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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
