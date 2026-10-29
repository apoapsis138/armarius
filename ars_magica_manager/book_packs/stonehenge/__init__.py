"""Heirs to Merlin: the Stonehenge Tribunal, as of 1220, in paraphrase.

Built in parts: the Tribunal itself, its customs, its one printed ruling
and its history with the twenty fallen covenants; the nine covenants,
their magi, the Redcaps and natural magicians, Mercer House and the
known ruins; the places of legend; the king, the triumvirate, the
nobles, the Church, the towns and universities; the stories; and last
every magus's generated stats.

The book is a Fourth Edition one that prints no statistics at all (p. 5),
so nothing is converted: every magus is generated from the book's
paragraph, and each judgement call is on the pack's assumptions page.
Where a Fifth Edition book describes the same thing it wins: Ebroin as
Primus of Ex Miscellanea, Immanola's Final Twilight in 1216, Gwrhyr and
Cad Gadu (DE p. 22; Houses of Hermes: Societates pp. 101-103, 110-112).

Source: Heirs to Merlin: The Stonehenge Tribunal (Atlas Games), content
under CC-BY-SA 4.0; the text here is a summary of it, not its words."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder
from ..records import Records
from . import covenants, places, stats, stories, tribunal, world

NAME = "Heirs to Merlin: the Stonehenge Tribunal"
SOURCE = (
    "Heirs to Merlin: The Stonehenge Tribunal, by Atlas Games, content under "
    "the Creative Commons Attribution-ShareAlike 4.0 licence; summarised, "
    "not quoted."
)

#: The parts, in the order they are built: the covenants make the lands
#: the places and lords sit in; the generated stats go in last.
PARTS = (tribunal, covenants, places, world, stories, stats)


def assemble() -> Builder:
    records = Records(Builder(NAME, source="HtM"))
    for step in ("build", "finish", "stats"):
        for part in PARTS:
            run = getattr(part, step, None)
            if run is not None:
                run(records)
    return records.b


def build() -> Saga:
    return assemble().saga


register(BookPack("stonehenge", "HtM", NAME, assemble, SOURCE))
