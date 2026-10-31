"""Legends of Hermes: five legendary magi of the Order's past and what
they left behind, as a pack of its own with no Tribunal, since the book's
stories move between Tribunals. Each chapter is a part: its sites as
places, its guardians as characters and creatures, its treasures in those
records, and its stories dormant until the storyguide begins them. A
location the book leaves open stays blank. The rest is a summary of the
book, not its words."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder

NAME = "Legends of Hermes"
SOURCE_BOOK = "LoH"
SOURCE = "Legends of Hermes, by Atlas Games; summarised, not quoted."
#: The parts, in the order they are built.
PARTS = ("conciatta", "fortunata", "herisson", "hermanus", "thomae")


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    import importlib

    b = Builder(NAME, source=SOURCE_BOOK)
    for name in PARTS:
        importlib.import_module(f"{__name__}.{name}").build(b)
    return b


def build() -> Saga:
    return assemble().saga


register(BookPack("legends_of_hermes", SOURCE_BOOK, NAME, assemble, SOURCE))
