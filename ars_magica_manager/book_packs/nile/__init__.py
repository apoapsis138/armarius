"""Lands of the Nile: Egypt, Nubia and Ethiopia as of 1220. The pack holds no Tribunal: these lands lie outside every
Hermetic Tribunal. Built in parts: the records shared with the other
African pack (book_packs.hunger), then peoples, monuments, egypt_nubia, ethiopia. A summary of the book,
not its words."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, hunger, register
from ..builder import Builder

NAME = "Lands of the Nile"
SOURCE_BOOK = "LotN"
SOURCE = "Lands of the Nile, by Atlas Games; summarised, not quoted."
#: The parts, in the order they are built.
PARTS = ("peoples", "monuments", "egypt_nubia", "ethiopia")


#: Places two parts each made: (the one kept, the one merged into it).
SAME_PLACES = (
    ("The Danakil Desert", "The Danakil Desert"),
    ("The Gizeh Necropolis", "The Necropolis of Gizeh"),
    ("The Gizeh Necropolis", "Abu 'l-Ahwa, the Father of Dread"),
)
#: Factions two parts each made, the same way round.
SAME_FACTIONS = (("The Hirranian Sabeans", "The Sabeans"),)


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    import importlib

    b = Builder(NAME, source=SOURCE_BOOK, known="In the region")
    hunger.build(b)
    for name in PARTS:
        importlib.import_module(f"{__name__}.{name}").build(b)
    for keep, drop in SAME_PLACES:
        b.absorb(keep, drop)
    for keep, drop in SAME_FACTIONS:
        b.absorb(keep, drop, kind="faction")
    return b


def build() -> Saga:
    return assemble().saga


register(BookPack("nile", SOURCE_BOOK, NAME, assemble, SOURCE))
