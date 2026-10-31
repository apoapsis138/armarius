"""Antagonists: ten recurring opponents a troupe can set in any saga. The
pack holds no Tribunal, and their stories come in dormant. Each human or
magus is also a build template on New Character, read from the same
record: Prototype, so no stat block is kept twice. A summary of the book,
not its words."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder

NAME = "Antagonists"
SOURCE_BOOK = "Ant"
SOURCE = "Antagonists, by Atlas Games; summarised, not quoted."
#: The parts, in the order they are built.
PARTS = (
    "geoffroi",
    "giraud",
    "joseph",
    "orris",
    "galerius",
    "diabolist",
    "cult",
    "abbot",
    "queen",
    "waimie",
)


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    import importlib

    b = Builder(NAME, source=SOURCE_BOOK, known="In the region")
    for name in PARTS:
        importlib.import_module(f"{__name__}.{name}").build(b)
    return b


def build() -> Saga:
    return assemble().saga


register(BookPack("antagonists", SOURCE_BOOK, NAME, assemble, SOURCE))
