"""A covenant's ship: the figures kept on a Ships entry of its
Possessions (a Possession of kind "ship" holds one). What they mean --
damage levels, crews, stress checks, combat -- is rules.ships'.

Hermetic Projects pp. 53-54 (ship damage, the Ship Sizes and Capacity
table) and City & Guild pp. 77, 84-87 (damaged goods, crews, costs, ship
combat).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import known_fields

#: How well a ship is made (C&G p. 77; HP p. 53): its base damage levels
#: and its stress-check modifier follow from it. Supernatural is City &
#: Guild's wondrous item.
SHIP_QUALITIES: tuple[str, ...] = (
    "Shoddy",
    "Standard",
    "Superior",
    "Excellent",
    "Supernatural",
)
SHIP_QUALITY_DEFAULT = "Standard"


@dataclass
class Ship:
    """The ship-only figures of a Ships entry; the Possession around it
    keeps her name and description.

    `ship_type` is the line of Hermetic Projects' table (rules.ships.
    SHIP_TYPES) the form's Like filled her from ("" typed in), `kind_name`
    what she is called ("Knarr"). `crew` is the square-rigged crew;
    `lateen` adds half as many again. `damage_lost` counts the damage
    levels she has lost; `repaired` marks a ship mended before (-1 to
    stress checks). `magnitudes` are the invested effects' total, added to
    her stress checks. `fighters_tons` is cargo space given to fighting
    men, at 8 a ton on a long voyage or 16 a quarter ton close to home.
    """

    ship_type: str = ""
    kind_name: str = ""
    size: int = 5
    tons: int = 20
    crew: int = 8
    lateen: bool = False
    galley: bool = False
    quality: str = SHIP_QUALITY_DEFAULT
    #: An Excellent ship's bonus (HP p. 63's example: +2).
    excellent_bonus: int = 2
    damage_lost: int = 0
    repaired: bool = False
    magnitudes: int = 0
    #: A saga character's id (None: no captain named).
    captain_id: str | None = None
    ballistae: int = 0
    catapults: int = 0
    fighters_tons: float = 0.0
    close_to_home: bool = False
    home_port: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], name: str) -> Ship:
        """A saved ship, checked: `name` is the entry's, for the message."""
        d = known_fields(cls, data)
        quality = d.get("quality", SHIP_QUALITY_DEFAULT)
        if quality not in SHIP_QUALITIES:
            raise ValueError(
                f"Ship {name}: unknown quality {quality!r}; must be one of "
                f"{SHIP_QUALITIES}"
            )
        for key in (
            "size",
            "tons",
            "crew",
            "excellent_bonus",
            "damage_lost",
            "magnitudes",
            "ballistae",
            "catapults",
        ):
            value = d.get(key, 0)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"Ship {name}: {key} must be a whole number")
            if value < 0 and key != "size":
                raise ValueError(f"Ship {name}: {key} can't be negative")
        fighters = d.get("fighters_tons", 0.0)
        if isinstance(fighters, bool) or not isinstance(fighters, int | float):
            raise ValueError(f"Ship {name}: fighters_tons must be a number")
        d["fighters_tons"] = float(fighters)
        return cls(**d)
