"""The Atlas's records: a map (a picture of a region, kept on its
Tribunal, or on the saga when it belongs to none) and a pin (a record
placed on a map, kept on the saga).

The maps belong to the Tribunal and the pins to the saga: a pack brings
its Tribunal's map and base pins, and the troupe adds, moves and hides
pins of its own. A pin's position is a fraction of the map's width and
height, so a new export of the same map at another size keeps every pin.
Which pins a map shows is atlas.py's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields


@dataclass
class AtlasMap:
    """A map: its name, its picture (the copy's file name in the maps
    folder, "" for none yet) and the picture's size in pixels, and the
    credit line it is shown with. Its scale, once set, is the two ends of
    its scale bar (fractions of its width and height: x1, y1, x2, y2) and
    how many miles the bar stands for."""

    id: str
    name: str
    picture: str = ""
    width: int = 0
    height: int = 0
    credit: str = ""
    scale_bar: list[float] = field(default_factory=list)
    scale_miles: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AtlasMap:
        d = known_fields(cls, data)
        if not d.get("id") or not d.get("name"):
            raise ValueError(f"A map needs an id and a name: {data!r}.")
        for key in ("width", "height"):
            if not isinstance(d.get(key, 0), int):
                raise ValueError(f"The map {d['name']}'s {key} should be a number.")
        bar = d.get("scale_bar") or []
        if len(bar) not in (0, 4) or not all(
            isinstance(n, int | float) and not isinstance(n, bool) for n in bar
        ):
            raise ValueError(f"The map {d['name']}'s scale bar should be four numbers.")
        d["scale_bar"] = [float(n) for n in bar]
        miles = d.get("scale_miles", 0.0)
        if isinstance(miles, bool) or not isinstance(miles, int | float) or miles < 0:
            raise ValueError(
                f"The map {d['name']}'s scale should be a number of miles."
            )
        d["scale_miles"] = float(miles)
        return cls(**d)


@dataclass
class Pin:
    """A record on a map: the map's id, the record's kind (a Ref's:
    references.KINDS) and id, and where it is, as fractions of the map's
    width and height from its top left. A pack's pin (`from_pack`) is
    hidden from the saga rather than deleted, so importing the pack again
    doesn't bring it back; a secret one is left off the Table view."""

    map_id: str
    kind: str
    record_id: str
    x: float
    y: float
    from_pack: bool = False
    hidden: bool = False
    secret: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Pin:
        d = known_fields(cls, data)
        for key in ("map_id", "kind", "record_id"):
            if not isinstance(d.get(key), str) or not d[key]:
                raise ValueError(f"A pin needs a {key}: {data!r}.")
        for key in ("x", "y"):
            value = d.get(key)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise ValueError(f"A pin's {key} should be a number: {data!r}.")
            d[key] = min(1.0, max(0.0, float(value)))
        return cls(**d)
