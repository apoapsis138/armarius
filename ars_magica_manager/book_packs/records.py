"""The records a pack's parts hand one another, by a short key: the
shape the Fourth Edition Tribunal packs share (the Levant keeps its own,
older one)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import Character, Covenant, Creature, Neighbour, Tribunal
from .builder import Builder

#: How widely a place is known, for `Builder.place`.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}


@dataclass
class Records:
    """`places` the regions, sites and regiones, `world` the other
    neighbours (lords, towns, churches, factions, threats), `creatures`
    the Bestiary, `covenants` and `magi` the Order's people (companions
    too)."""

    b: Builder
    tribunal: Tribunal | None = None
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    magi: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)
    creatures: dict[str, Creature] = field(default_factory=dict)
