"""The Contested Isle: the Hibernian Tribunal, as of 1220, in paraphrase.
Built in parts: the Tribunal itself, its Code, treaties, docket,
ambassadors and ruins; then each province's land, covenants, magi,
libraries, vis and mundane world (Munster, Leinster, Meath with the
English lordship, Ulster, Connacht); the magical and faerie landscape
(the Coill Trí and their túatha, the bards, the elder races and the High
Roads); the two churches and the Infernal; the saga's stories; the
history; the Bestiary with the saints; and last the generated stats.

Each covenant's cathach, the Tribunal's ambassadors and treaties and the
Coill Trí's túatha are kept by the Hibernia package, which only the
Tribunal part writes; the other parts hand it what they find through the
`Hibernia` record.

Source: The Contested Isle: The Hibernian Tribunal (Atlas Games),
content under CC-BY-SA 4.0; the text here is a summary of it, not its
words."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ...models import Character, Covenant, Neighbour, Saga, Tribunal
from .. import BookPack, register
from ..builder import Builder

NAME = "The Contested Isle: the Hibernian Tribunal"
SOURCE = (
    "The Contested Isle: The Hibernian Tribunal, by Atlas Games, content "
    "under the Creative Commons Attribution-ShareAlike 4.0 licence; "
    "summarised, not quoted."
)


@dataclass
class Hibernia:
    """The records the parts hand one another, by a short key."""

    b: Builder
    tribunal: Tribunal | None = None
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    magi: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)
    #: Each covenant's cathach, by the covenant's key: {"cathach" (what it
    #: is), and "taken_by" and "taken_year" if another holds it}.
    cathaigh: dict[str, dict[str, Any]] = field(default_factory=dict)
    #: The Coill Trí's seven túatha, in order: (name, ceannaire or "").
    tuatha: list[tuple[str, str]] = field(default_factory=list)

    def covenant_named(self, name: str) -> Covenant:
        """The covenant of that name, made by any part."""
        found = next((c for c in self.b.saga.covenants if c.name == name), None)
        if found is None:
            raise KeyError(f"No covenant named {name!r} yet")
        return found

    def neighbour_named(self, name: str) -> Neighbour:
        """The place, lord, church, town or faction of that name, made by
        any part."""
        found = next((n for n in self.b.saga.neighbours if n.name == name), None)
        if found is None:
            raise KeyError(f"No neighbour named {name!r} yet")
        return found


#: The parts, in the order they are built.
PARTS = (
    "tribunal",
    "munster",
    "leinster",
    "meath",
    "ulster",
    "connacht",
    "otherworld",
    "church",
    "stories",
    "history",
    "bestiary",
)


def assemble() -> Builder:
    import importlib

    parts = [importlib.import_module(f"{__name__}.{name}") for name in PARTS]
    hibernia = Hibernia(Builder(NAME, source="TCI"))
    for part in parts:
        part.build(hibernia)
    for part in parts:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(hibernia)
    _covenant_auras(hibernia)
    for part in parts:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(hibernia)
    return hibernia.b


def _covenant_auras(hibernia: Hibernia) -> None:
    """A covenant whose part gave it no aura takes its site's: the regio
    level it stands on, or the place itself."""
    saga = hibernia.b.saga
    for covenant in saga.covenants:
        place = saga.neighbour(covenant.place_id) if covenant.place_id else None
        if covenant.aura or place is None:
            continue
        levels = place.details.get("levels") or []
        if 0 < covenant.place_level <= len(levels):
            level = levels[covenant.place_level - 1]
            covenant.aura, covenant.aura_realm = level["aura"], level["realm"]
        elif place.details.get("aura"):
            covenant.aura = place.details["aura"]
            covenant.aura_realm = place.realm or covenant.aura_realm


def build() -> Saga:
    return assemble().saga


register(BookPack("hibernia", "TCI", NAME, assemble, SOURCE))
