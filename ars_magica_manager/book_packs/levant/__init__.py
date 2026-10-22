"""Blood and Sand: the Levant Tribunal, as of 1220, in paraphrase, with
the stat blocks of its free companion Secrets in Sand.
Built in parts: first the records shared with The Cradle and the
Crescent and The Sundered Eagle (book_packs.east: the Order of Suleiman,
the jinn, the Nizaris, the caliph and the Ayyubid princes, Georgia,
Iraq, the Fifth Crusade, the Sultan of Rum and the Emperor of Trebizond);
then the Tribunal itself, its Code, the Treaty of Baghdad and its
docket; the Levant's regions and places; the four major covenants and
their magi; the eight lesser covenants and theirs; the Latin states,
the Muslim powers, the churches, faiths and military orders; the
Bestiary; the saga's stories; the history; and last the eight magi
whose stat blocks are printed, converted from the Fourth Edition.

The book is a Fourth Edition one: its numbers are converted by the
Definitive Edition's appendix, and each judgement call the conversion
needed is on the pack's assumptions page.

Source: Blood and Sand: The Levant Tribunal and Secrets in Sand (Atlas
Games), content under CC-BY-SA 4.0; the text here is a summary of them,
not their words."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ...models import Character, Covenant, Creature, Neighbour, Saga, Tribunal
from ...places import PLACE
from .. import BookPack, east, register
from ..builder import Builder

NAME = "Blood and Sand: the Levant Tribunal"
SOURCE = (
    "Blood and Sand: The Levant Tribunal and its web supplement Secrets in "
    "Sand, by Atlas Games, content under the Creative Commons "
    "Attribution-ShareAlike 4.0 licence; summarised, not quoted."
)


@dataclass
class Levant:
    """The records the parts hand one another, by a short key.

    `places` holds place records (regions, sites, regiones), `world` the
    rest of the neighbours (lords, towns, churches, factions, threats),
    `creatures` the Bestiary, `covenants` and `magi` the Order's people.
    The shared records (book_packs.east) are put in these dicts under
    east.middle_east's keys before any part builds: places["iraq"],
    world["caliph"], creatures["al_khidr"] and so on."""

    b: Builder
    tribunal: Tribunal | None = None
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    magi: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)
    creatures: dict[str, Creature] = field(default_factory=dict)

    def covenant_named(self, name: str) -> Covenant:
        """The covenant of that name, made by any part."""
        found = next((c for c in self.b.saga.covenants if c.name == name), None)
        if found is None:
            raise KeyError(f"No covenant named {name!r} yet")
        return found

    def neighbour_named(self, name: str) -> Neighbour:
        """The place, lord, church, town, faction or threat of that name,
        made by any part."""
        found = next((n for n in self.b.saga.neighbours if n.name == name), None)
        if found is None:
            raise KeyError(f"No neighbour named {name!r} yet")
        return found

    def magus_named(self, name: str) -> Character:
        """The character of that name, made by any part."""
        found = next((c for c in self.b.saga.characters if c.name == name), None)
        if found is None:
            raise KeyError(f"No character named {name!r} yet")
        return found

    def creature_named(self, name: str) -> Creature:
        """The Bestiary entry of that name, made by any part."""
        found = next((c for c in self.b.saga.creatures if c.name == name), None)
        if found is None:
            raise KeyError(f"No creature named {name!r} yet")
        return found

    def find(self, key: str) -> Any:
        """The record another part keeps under `key` in any of the dicts,
        or None while that part is unwritten (so a finish step can skip
        what is not there yet)."""
        for found in (
            self.places,
            self.world,
            self.covenants,
            self.magi,
            self.creatures,
        ):
            if key in found:
                return found[key]
        return None


#: The parts, in the order they are built. The places come before the
#: covenants and lords that sit in them; the converted stat blocks are
#: entered last, in `stats`.
PARTS = (
    "tribunal",
    "places",
    "major_covenants",
    "other_covenants",
    "latin_states",
    "muslim_powers",
    "churches",
    "bestiary",
    "stories",
    "history",
    "stats_magi",
)


def _shared(levant: Levant) -> None:
    """The records shared with other packs, filed by kind."""
    for key, record in east.middle_east(levant.b).items():
        if isinstance(record, Creature):
            levant.creatures[key] = record
        elif record.kind == PLACE:
            levant.places[key] = record
        else:
            levant.world[key] = record


def assemble() -> Builder:
    import importlib

    parts = [importlib.import_module(f"{__name__}.{name}") for name in PARTS]
    levant = Levant(Builder(NAME, source="B&S"))
    _shared(levant)
    for part in parts:
        part.build(levant)
    for part in parts:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(levant)
    _covenant_auras(levant)
    for part in parts:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(levant)
    return levant.b


def _covenant_auras(levant: Levant) -> None:
    """A covenant whose part gave it no aura takes its site's: the regio
    level it stands on, or the place itself."""
    saga = levant.b.saga
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


register(BookPack("levant", "B&S", NAME, assemble, SOURCE))
