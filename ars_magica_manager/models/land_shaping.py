"""A covenant's work of shaping the land by magic: an island raised from
the sea in the way Transforming Mythic Europe's Island of the Magicians
describes (a stone wall jacketing an infill of earth, then its surface
life and its wards). Only the design is kept; the Rituals it needs, their
levels and vis, and what the land is worth are rules.land_shaping's, and
the Rituals cast so far are the magi's Progress records (kind
LAND_KIND, named for the project).

Transforming Mythic Europe pp. 54-67, 71-77.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields

#: The Progress records a season of shaping the land keeps: one Ritual of
#: the project cast is a point.
LAND_KIND = "land_shaping"

#: The outer wall's shapes (TME pp. 55-56). A tall cylinder is the open
#: cylinder with a higher wall.
RING = "Open-ended cylinder"
SQUARE = "Open-ended rectangular prism"
SOLID = "Solid stone cylinder"
SHAPES: tuple[str, ...] = (RING, SQUARE, SOLID)

#: What the wall is made of (TME pp. 58-59): wood and animal bone are as
#: hard to make as stone, human bone as base metal.
STONE = "Stone"
BASE_METAL = "Base metal"
PRECIOUS_METAL = "Precious metal"
WOOD = "Wood"
ANIMAL_BONE = "Animal bone"
HUMAN_BONE = "Human bone"
WALL_MATERIALS: tuple[str, ...] = (
    STONE,
    BASE_METAL,
    PRECIOUS_METAL,
    WOOD,
    ANIMAL_BONE,
    HUMAN_BONE,
)

#: What fills the space the wall encloses (TME p. 59): soil (topsoil over
#: rubbish) or clay, both as easy as dirt, or stone.
SOIL = "Soil or clay"
STONE_FILL = "Stone"
FILLS: tuple[str, ...] = (SOIL, STONE_FILL)

#: The wall's ornaments and defences, by key (TME pp. 56-57): what each
#: adds is rules.land_shaping.WALL_FEATURES'.
FEATURE_KEYS: tuple[str, ...] = (
    "crenellations",
    "fire_step",
    "machicolations",
    "hoardings",
    "sea_gate",
    "statuary",
)


def _whole(value: Any, what: str, least: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < least:
        raise ValueError(f"{what} should be a whole number of at least {least}.")
    return value


def _one_of(value: Any, allowed: tuple[str, ...], what: str) -> str:
    text = str(value)
    if text not in allowed:
        raise ValueError(f"{what}: {text!r} is not one of {', '.join(allowed)}.")
    return text


@dataclass
class LandProject:
    """One work of shaping the land: the island's shape and size (its
    diameter, or a square's side, in miles), its wall, its fill, its
    surface life (grassland over all of it, a forest of so many trees), its
    wards (an Aegis of the Hearth of the level chosen, and the island-wide
    Boundary spells by name), whether its land is highly fertile, and the
    manors already settled on it."""

    id: str
    name: str
    shape: str = RING
    across_miles: float = 3.0
    wall_height: int = 30
    wall_thickness: int = 2
    wall_material: str = STONE
    #: FEATURE_KEYS chosen for the wall.
    features: list[str] = field(default_factory=list)
    #: A Muto requisite gives the wall an unnatural property (TME p. 58).
    unnatural: bool = False
    #: The troupe's option capping complexity at three magnitudes (p. 56).
    cap_complexity: bool = False
    fill: str = SOIL
    #: Several kinds of stone in a stone fill (+1 magnitude, p. 60).
    mixed_stone: bool = False
    #: An ablative slope of earth at the wall's foot (p. 56).
    slope: bool = True
    grassland: bool = True
    forest_trees: int = 0
    #: The Aegis of the Hearth's level before the island's size (0: none).
    aegis: int = 0
    #: The Boundary spells of pp. 71-77 cast over the island, by name.
    boundary_spells: list[str] = field(default_factory=list)
    fertile: bool = False
    manors_settled: int = 0
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LandProject:
        if not isinstance(data, dict):
            raise ValueError(f"A land project should be a mapping, not {data!r}.")
        d = dict(data)
        what = f"The land project {d.get('name')!r}"
        if not d.get("id") or not str(d.get("name") or "").strip():
            raise ValueError(f"{what} needs an id and a name.")
        d["name"] = str(d["name"])
        if "shape" in d:
            d["shape"] = _one_of(d["shape"], SHAPES, f"{what}'s shape")
        if "wall_material" in d:
            d["wall_material"] = _one_of(
                d["wall_material"], WALL_MATERIALS, f"{what}'s wall"
            )
        if "fill" in d:
            d["fill"] = _one_of(d["fill"], FILLS, f"{what}'s fill")
        across = d.get("across_miles", 3.0)
        if isinstance(across, bool) or not isinstance(across, (int, float)):
            raise ValueError(f"{what}'s size should be a number of miles.")
        if across <= 0:
            raise ValueError(f"{what}'s size should be more than nothing.")
        d["across_miles"] = float(across)
        for key, least in (
            ("wall_height", 1),
            ("wall_thickness", 1),
            ("forest_trees", 0),
            ("aegis", 0),
            ("manors_settled", 0),
        ):
            if key in d:
                d[key] = _whole(d[key], f"{what}'s {key.replace('_', ' ')}", least)
        features = d.get("features") or []
        if not isinstance(features, list):
            raise ValueError(f"{what}'s wall features should be a list.")
        d["features"] = [_one_of(f, FEATURE_KEYS, f"{what}'s wall") for f in features]
        spells = d.get("boundary_spells") or []
        if not isinstance(spells, list):
            raise ValueError(f"{what}'s Boundary spells should be a list.")
        d["boundary_spells"] = [str(s) for s in spells]
        return cls(**known_fields(cls, d))
