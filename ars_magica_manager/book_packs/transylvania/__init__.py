"""Against the Dark: the Transylvanian Tribunal, as of 1220, in
paraphrase. Built in parts: the Tribunal itself, its Code, docket and
ruins; then each region's land, oppida, magi, libraries, vis and
mundane world (Hungary, Bulgaria, the Slav lands, Transylvania's border
peoples); Coeris; the hidden fortresses and the zenodochia; the hedge
traditions; the saga's stories; the history; the Bestiary; and last the
generated stats.

The book's oppida, where its magi live, are the app's covenants; the
five legal covenants are privileges each magus holds, kept by the
Transylvania package with the oppida's aediles.

Source: Against the Dark: The Transylvanian Tribunal (Atlas Games),
content under CC-BY-SA 4.0; the text here is a summary of it, not its
words."""

from __future__ import annotations

from dataclasses import dataclass, field

from ...models import Character, Covenant, Neighbour, Saga, Tribunal
from .. import BookPack, register
from ..builder import Builder, fill_boons_hooks

NAME = "Against the Dark: the Transylvanian Tribunal"
SOURCE = (
    "Against the Dark: The Transylvanian Tribunal, by Atlas Games, content "
    "under the Creative Commons Attribution-ShareAlike 4.0 licence; "
    "summarised, not quoted."
)


@dataclass
class Transylvania:
    """The records the parts hand one another, by a short key."""

    b: Builder
    tribunal: Tribunal | None = None
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    magi: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)
    #: Each named magus's privilege (a key of the Transylvania package's
    #: PRIVILEGES) and any office besides Praeco, Presiding Quaesitor and
    #: aedile, by the magus's key; the Tribunal part writes them into the
    #: package's members.
    privileges: dict[str, tuple[str, str]] = field(default_factory=dict)
    #: Each oppidum's aediles, by the oppidum's key: one or two magus keys.
    aediles: dict[str, list[str]] = field(default_factory=dict)

    def covenant_named(self, name: str) -> Covenant:
        """The covenant of that name, made by any part."""
        found = next((c for c in self.b.saga.covenants if c.name == name), None)
        if found is None:
            raise KeyError(f"No covenant named {name!r} yet")
        return found


#: The parts, in the order they are built.
PARTS = (
    "tribunal",
    "hungary",
    "bulgaria",
    "slavs",
    "borders",
    "coeris",
    "fortresses",
    "traditions",
    "stories",
    "history",
    "bestiary",
    "auras",
)


def assemble() -> Builder:
    import importlib

    parts = [importlib.import_module(f"{__name__}.{name}") for name in PARTS]
    transylvania = Transylvania(Builder(NAME, source="AtD"))
    for part in parts:
        part.build(transylvania)
    for part in parts:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(transylvania)
    _covenant_auras(transylvania)
    fill_boons_hooks(transylvania.b.saga)
    for part in parts:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(transylvania)
    return transylvania.b


def _covenant_auras(transylvania: Transylvania) -> None:
    """A covenant whose part gave it no aura takes its site's: the regio
    level it stands on, or the place itself."""
    saga = transylvania.b.saga
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


register(BookPack("transylvania", "AtD", NAME, assemble, SOURCE))
