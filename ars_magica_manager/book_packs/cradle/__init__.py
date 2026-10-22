"""The Cradle and the Crescent: Arabia, Mesopotamia, Persia and the Silk
Road as of 1220, in paraphrase. A region pack: the lands lie east of the
Levant and outside every Hermetic Tribunal, so the pack holds no
Tribunal, no Peripheral Code and no docket.

Built in parts: first the records shared with Blood and Sand and The
Sundered Eagle (book_packs.east: the Order of Suleiman with its Stone
and River families, the jinn, the Nizaris, the caliph and the Ayyubid
princes, Georgia, Iraq, the Fifth Crusade, the Mongols, the Sultan of
Rum and the Emperor of Trebizond); then the four regions with their
places, rulers, towns and factions; the jinn's lands and courts; the
Mazdeans and their fire temples; the Order of Suleiman's own records,
its families, its houses of wisdom (the app's covenants) and their
sahirs; the Bestiary; the stories; and the history, which with no
Tribunal Diary goes in the Dar al-Hikma's covenant Diary and the saga's
calendar. Last, the one sahir whose stat block is printed.

Every sahir is a companion of the Sahirs tradition (trad_sahirs), not a
Hermetic magus; the app's word for a house of wisdom (bayt al-hikma) is
a covenant, with no Tribunal.

Source: The Cradle and the Crescent (Atlas Games), content under
CC-BY-SA 4.0; the text here is a summary of it, not its words."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ...models import Character, Covenant, Creature, Neighbour, Saga
from ...places import PLACE
from .. import BookPack, east, register
from ..builder import Builder

NAME = "The Cradle and the Crescent"
SOURCE = (
    "The Cradle and the Crescent, by Atlas Games, content under the "
    "Creative Commons Attribution-ShareAlike 4.0 licence; summarised, not "
    "quoted."
)
#: How widely a place is known when a part does not say: there is no
#: Tribunal to be known in.
KNOWN = "In the region"


@dataclass
class Cradle:
    """The records the parts hand one another, by a short key.

    `places` holds place records (regions, provinces, sites, regiones),
    `world` the rest of the neighbours (lords, towns, factions, threats),
    `creatures` the Bestiary, `covenants` the houses of wisdom and
    `people` every character (sahirs and the one Hermetic magus). The
    shared records (book_packs.east) are put in these dicts under
    east.middle_east's keys before any part builds: places["iraq"],
    world["baghdad"], world["order"], creatures["al_khidr"] and so on."""

    b: Builder
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    people: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)
    creatures: dict[str, Creature] = field(default_factory=dict)

    def covenant_named(self, name: str) -> Covenant:
        """The covenant of that name, made by any part."""
        found = next((c for c in self.b.saga.covenants if c.name == name), None)
        if found is None:
            raise KeyError(f"No covenant named {name!r} yet")
        return found

    def neighbour_named(self, name: str) -> Neighbour:
        """The place, lord, town, faction or threat of that name, made by
        any part."""
        found = next((n for n in self.b.saga.neighbours if n.name == name), None)
        if found is None:
            raise KeyError(f"No neighbour named {name!r} yet")
        return found

    def person_named(self, name: str) -> Character:
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
        or None while that part is unwritten (so a part can skip what is
        not there yet)."""
        for found in (
            self.places,
            self.world,
            self.covenants,
            self.people,
            self.creatures,
        ):
            if key in found:
                return found[key]
        return None


#: The parts, in the order they are built. The regions come first, so
#: the temples, houses of wisdom and creatures after them can sit in
#: their places; the printed stat block is entered last, in `stats`.
PARTS = (
    "arabia",
    "mesopotamia",
    "persia",
    "silk_road",
    "jinn",
    "zoroastrians",
    "order",
    "bestiary",
    "stories",
    "history",
)


def _shared(cradle: Cradle) -> None:
    """The records shared with other packs, filed by kind."""
    for key, record in east.middle_east(cradle.b).items():
        if isinstance(record, Creature):
            cradle.creatures[key] = record
        elif record.kind == PLACE:
            cradle.places[key] = record
        else:
            cradle.world[key] = record


def assemble() -> Builder:
    import importlib

    parts = [importlib.import_module(f"{__name__}.{name}") for name in PARTS]
    cradle = Cradle(Builder(NAME, source="TC&TC", known=KNOWN))
    _shared(cradle)
    for part in parts:
        part.build(cradle)
    for part in parts:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(cradle)
    _covenant_auras(cradle)
    for part in parts:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(cradle)
    return cradle.b


def _covenant_auras(cradle: Cradle) -> None:
    """A covenant whose part gave it no aura takes its site's: the regio
    level it stands on, or the place itself."""
    saga = cradle.b.saga
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


register(BookPack("cradle", "TC&TC", NAME, assemble, SOURCE))
