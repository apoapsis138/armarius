"""The Sundered Eagle: the Theban Tribunal, as of 1220, in paraphrase.
Built in parts: the Tribunal itself, its Code, docket and ruined
covenants; then each region's land, covenants, magi, libraries, vis and
mundane world (Greece, the Islands, Constantinople, Anatolia); the
places of the four realms; the Bestiary; the saga's stories; the
history; and last the generated stats.

Source: The Sundered Eagle: The Theban Tribunal (Atlas Games), content
under CC-BY-SA 4.0; the text here is a summary of it, not its words."""

from __future__ import annotations

from dataclasses import dataclass, field

from ...models import Character, Covenant, Neighbour, Saga, Tribunal
from .. import BookPack, register
from ..builder import Builder

NAME = "The Sundered Eagle: the Theban Tribunal"
SOURCE = (
    "The Sundered Eagle: The Theban Tribunal, by Atlas Games, content under "
    "the Creative Commons Attribution-ShareAlike 4.0 licence; summarised, "
    "not quoted."
)


@dataclass
class Theban:
    """The records the parts hand one another, by a short key."""

    b: Builder
    tribunal: Tribunal | None = None
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    magi: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)

    def covenant_named(self, name: str) -> Covenant:
        """The covenant of that name, made by any part."""
        found = next((c for c in self.b.saga.covenants if c.name == name), None)
        if found is None:
            raise KeyError(f"No covenant named {name!r} yet")
        return found


#: The parts, in the order they are built.
PARTS = (
    "tribunal",
    "greece",
    "islands",
    "constantinople",
    "anatolia",
    "realms",
    "stories",
    "history",
    "bestiary",
)


def assemble() -> Builder:
    import importlib

    parts = [importlib.import_module(f"{__name__}.{name}") for name in PARTS]
    theban = Theban(Builder(NAME, source="TSE"))
    for part in parts:
        part.build(theban)
    for part in parts:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(theban)
    _covenant_auras(theban)
    for part in parts:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(theban)
    return theban.b


def _covenant_auras(theban: Theban) -> None:
    """A covenant whose part gave it no aura takes its site's: the regio
    level it stands on, or the place itself."""
    saga = theban.b.saga
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


register(BookPack("theban", "TSE", NAME, assemble, SOURCE))
