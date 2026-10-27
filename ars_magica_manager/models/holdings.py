"""What a covenant holds: inhabitants, possessions and sources of
income."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from .common import known_fields
from .ships import Ship

#: The kinds of covenant inhabitant, in the order the Inhabitants tab lists them.
INHABITANT_KINDS: tuple[str, ...] = (
    "magus",
    "companion",
    "specialist",
    "craftsperson",
    "turb",
    "inhabitant",
    "horse",
    "hound",
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
#: rules.covenfolk.InhabitantEntry.gift / base_loyalty(). "" means not yet set
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
    # A covenant's ships (Hermetic Projects; City & Guild): first, as the
    # approved Possessions preview has them.
    "ship",
    "property",
    "sanctum",
    "weapon",
    "armor",
    "vis_source",
    "vis_store",
    "item",
)

#: The kinds of raw vis a Vis Source or Raw Vis Store may hold beyond the
#: ordinary ("", the default): Realms of Power: Magic's extraordinary and
#: dedicated vis and Things of Virtue (pp. 119-128), and Realms of Power:
#: Faerie's faerie vis (pp. 18-19). What each does is rules.vis_kinds'.
VIS_KINDS: tuple[str, ...] = (
    "",
    "lesser_enchantment",
    "spell_like",
    "dedicated",
    "herb_of_virtue",
    "object_of_virtue",
    "encased",
    "anchor",
    "accrued",
    "sleeping",
    "abstract",
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
    * vis_store (Raw Vis Stores): name, art, pawns, physical_form, infernal
      (Infernal vis), its kind of vis (vis_kind and the fields that go
      with it; a vis_source has them too), where it
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
    #: Armour worn as one piece of an outfit (models.arms.ARMOR_SLOTS:
    #: "Body", "Surcoat", "Greaves", "Helmet"; Lords of Men p. 140), whose
    #: Protection and Load add to the other pieces'; "" for a whole suit.
    armor_slot: str = ""
    #: Weapons and armour: how well made (rules.equipment.MAKES: "" for
    #: standard, "Shoddy", "Superior", "Excellent"), and an Excellent
    #: item's bonus (+2 or more).
    make: str = ""
    make_bonus: int = 0
    #: Weapons: carried, so its Load counts (a spare left at home doesn't).
    carried: bool = True
    #: Gear: the Ability (and specialty) it helps, and how much ("Minor" or
    #: "Major": 1 or 3 off the Ease Factor).
    assists: str = ""
    assistance: str = ""
    art: str = ""
    pawns: int = 0
    season: str = ""  # one of SEASONS
    physical_form: str = ""
    #: vis_store / vis_source: Infernal vis, tainted by Hell (RoP: The
    #: Infernal pp. 18-19): more botch dice in casting (rules.casting).
    infernal: bool = False
    #: vis_store / vis_source: the kind of vis (one of VIS_KINDS; "" is
    #: ordinary vis); a dedicated pawn's other Art (its Technique or Form
    #: with `art`); a Thing of Virtue's entry in rules.vis_kinds'
    #: THINGS_OF_VIRTUE ("" for one not listed); and an extraordinary
    #: pawn's power's level (None: not known).
    vis_kind: str = ""
    paired_art: str = ""
    virtue_thing: str = ""
    effect_level: int | None = None
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
    #: ship: her figures (models.ships.Ship); None for every other kind.
    ship: Ship | None = None

    def __post_init__(self) -> None:
        if self.kind not in POSSESSION_KINDS:
            raise ValueError(
                f"Unknown possession kind {self.kind!r}; must be one of {POSSESSION_KINDS}"
            )
        # A saved ship comes back as a dict; a new one starts with defaults.
        saved: object = self.ship
        if isinstance(saved, dict):
            self.ship = Ship.from_dict(
                cast(dict[str, Any], saved), self.name or self.id
            )
        elif self.kind == "ship" and self.ship is None:
            self.ship = Ship()
        if self.vis_kind not in VIS_KINDS:
            raise ValueError(
                f"{self.name or self.id}: unknown kind of vis {self.vis_kind!r}; "
                f"must be one of {VIS_KINDS}"
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
    #: Retirees the pension keeps: half Wages each (DE p. 186).
    pensioners: int = 0
    #: Familiarity is worked out from the years since the covenant's
    #: founding (inhabitants.familiarity); this adjusts it (new covenfolk
    #: dilute it, Covenants p. 40).
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


#: Grain made by magic (Transforming Mythic Europe pp. 120-121): how its
#: store is kept (a twentieth or a tenth lost a year at best, a fifth when
#: only covered), and the share of the provisions that is bread.
GRAIN_CARE: tuple[str, ...] = ("Protected well", "Protected", "Covered only")
BREAD_SHARES: tuple[str, ...] = ("Half", "Three quarters")


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
    #: Pennies paid daily to professional soldiers: a pound of Wages each
    #: (DE p. 193).
    soldier_pay: int = 0
    #: Last year's total expenditure, for inflation's growth (None: not
    #: recorded yet).
    last_expenditure: int | None = None
    #: Free-text notes by row key ("buildings", "laborers"...).
    notes: dict[str, str] = field(default_factory=dict)
    # Technological savings (Transforming Mythic Europe pp. 120-121): the
    # covenant's enchanted devices doing covenfolk's work (device ids),
    # the magnitudes of Ritual spells cast for it this year, and a store of
    # grain made by magic (bushels), how it is kept and how much of the
    # provisions is bread.
    saving_devices: list[str] = field(default_factory=list)
    ritual_magnitudes: int = 0
    magic_grain: int = 0
    grain_care: str = GRAIN_CARE[-1]
    bread_share: str = BREAD_SHARES[0]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Economics:
        d = known_fields(cls, data)
        d["income_sources"] = [
            IncomeSource(**known_fields(IncomeSource, s))
            for s in d.get("income_sources", [])
        ]
        for key, allowed in (("grain_care", GRAIN_CARE), ("bread_share", BREAD_SHARES)):
            if key in d and d[key] not in allowed:
                raise ValueError(
                    f"Economics: unknown {key} {d[key]!r}; must be one of {allowed}"
                )
        for key in ("ritual_magnitudes", "magic_grain"):
            if key in d and (not isinstance(d[key], int) or d[key] < 0):
                raise ValueError(
                    f"Economics: {key} must be a whole number of at least 0, "
                    f"not {d[key]!r}"
                )
        return cls(**known_fields(cls, d))
