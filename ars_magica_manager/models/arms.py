"""Lords of Men's armour outfittings (Expanded Armor Table, Lords of Men
p. 140): armour worn as separate pieces -- body armour, a surcoat, greaves
and a helmet -- whose Protection and Load add together, fractions kept
until the end and then rounded up."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import known_fields
from .holdings import GEAR_QUALITIES

#: Where a piece is worn: one of each at a time. A Possession's
#: `armor_slot` is one of these, or "" for a whole suit (the Definitive
#: Edition's partial or full armour).
BODY = "Body"
SURCOAT = "Surcoat"
GREAVES = "Greaves"
HELMET = "Helmet"
ARMOR_SLOTS: tuple[str, ...] = (BODY, SURCOAT, GREAVES, HELMET)


@dataclass(frozen=True)
class ArmorPieceDef:
    """A catalog piece of armour (weapon_armor_catalog.json's
    "armor_pieces"): one cell of Lords of Men's Expanded Armor Table.
    `protection` and `load` may be fractions (+2.5, 1.5). `full` marks full
    body armour, which already includes greaves; `perception` is a helmet's
    Perception penalty; `cost` one of GEAR_QUALITIES."""

    id: str
    name: str
    slot: str
    protection: float
    load: float
    cost: str
    full: bool = False
    perception: int = 0
    description: str = ""
    source: str = ""

    def __post_init__(self) -> None:
        if self.slot not in ARMOR_SLOTS:
            raise ValueError(f"Unknown armour slot {self.slot!r} for {self.id!r}")
        if self.cost not in GEAR_QUALITIES:
            raise ValueError(f"Unknown cost {self.cost!r} for {self.id!r}")
        if self.full and self.slot != BODY:
            raise ValueError(f"Only body armour is full, not {self.id!r}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArmorPieceDef:
        return cls(**known_fields(cls, data))
