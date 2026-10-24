"""Enchanted devices and their effects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import ExperimentalEffect, experimental_effects, known_fields

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
    #: The character who instilled it, as lab work recorded it ("": not
    #: known -- typed in, or from an older save). A talisman's effects must
    #: all be its magus's own.
    instilled_by: str = ""
    #: Uses of it since the day began (Use an Effect counts them against
    #: its uses per day; a new day sets them back to 0).
    uses_today: int = 0
    #: Typed figures replacing the worked-out ones (None: worked out).
    modified_level_override: int | None = None
    vis_override: int | None = None
    #: What the experiments that instilled it left on it.
    experimental_effects: list[ExperimentalEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InstilledEffect:
        d = dict(data)
        effects = experimental_effects(d.get("experimental_effects"))
        # Older saves wrote them into the description, after "Experimental:".
        description, marker, old = str(d.get("description", "")).partition(
            "\nExperimental: "
        )
        if not marker and description.startswith("Experimental: "):
            description, old = "", description.removeprefix("Experimental: ")
        if old:
            d["description"] = description.rstrip()
            effects += experimental_effects(old.split("; "))
        d["experimental_effects"] = effects
        return cls(**known_fields(cls, d))


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
    #: Verditius Magic: its maker crafted it from raw materials in its
    #: first season (Verditius Runes), with this Craft Ability ("" when he
    #: shaped it by magic alone).
    verditius_runes: bool = False
    verditius_craft: str = ""
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
        d["effects"] = [InstilledEffect.from_dict(e) for e in d.get("effects", [])]
        return cls(**known_fields(cls, d))
