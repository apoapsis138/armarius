"""Where a mobile covenant has been and means to go: the dated stops it
has logged and the route it has planned. Each names a Place of The Region
and one of its levels. A ship apart from the fleet keeps a list of stops
of her own.

Which stop is in force is rules.mobile's.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import SEASONS, known_fields


@dataclass
class CovenantStop:
    """Where a covenant or a ship was from a season on: a Place and its
    level (0 for the surface), and a note."""

    year: int
    season: str
    place_id: str
    level: int = 0
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], owner: str) -> CovenantStop:
        d = known_fields(cls, data)
        what = f"A stop of {owner}"
        year = d.get("year")
        if isinstance(year, bool) or not isinstance(year, int):
            raise ValueError(f"{what}: the year should be a number, not {year!r}.")
        if d.get("season") not in SEASONS:
            raise ValueError(f"{what}: {d.get('season')!r} is not a season.")
        if not d.get("place_id"):
            raise ValueError(f"{what} names no Place.")
        d["place_id"] = str(d["place_id"])
        d["level"] = _whole(d.get("level", 0), f"{what}: its level")
        d["note"] = str(d.get("note") or "")
        return cls(**d)


@dataclass
class RouteStop:
    """One leg of a planned route: a Place and level, and the seasons
    meant to be spent there."""

    place_id: str
    level: int = 0
    seasons: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any], owner: str) -> RouteStop:
        d = known_fields(cls, data)
        what = f"A stop on the route of {owner}"
        if not d.get("place_id"):
            raise ValueError(f"{what} names no Place.")
        d["place_id"] = str(d["place_id"])
        d["level"] = _whole(d.get("level", 0), f"{what}: its level")
        d["seasons"] = _whole(d.get("seasons", 1), f"{what}: its seasons")
        if d["seasons"] < 1:
            raise ValueError(f"{what} should last a season at least.")
        return cls(**d)


def _whole(value: object, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{what} should be a whole number, not {value!r}.")
    return value


def stops_from(data: object, owner: str) -> list[CovenantStop]:
    """Saved stops, checked; `owner` names the covenant or ship."""
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError(f"{owner}'s stops should be a list, not {data!r}.")
    return [CovenantStop.from_dict(entry, owner) for entry in data]


def route_from(data: object, owner: str) -> list[RouteStop]:
    """A saved route, checked; `owner` names the covenant."""
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError(f"{owner}'s route should be a list, not {data!r}.")
    return [RouteStop.from_dict(entry, owner) for entry in data]
