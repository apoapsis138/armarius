"""Sanctuary of Ice: the Greater Alps Tribunal, as of 1220, in paraphrase.

Built in parts: the Tribunal itself, its chairs, ostracism and Peripheral
Code, its Hermetic year and its meetings; the Alps' regions and places;
the six covenants the book describes, with their chapters and magi; the
lords, bishops, abbeys and towns; the Bestiary; the stories; and last the
four magi and the Redcap whose stat blocks are printed, converted from
the Fourth Edition, with everyone else's generated stats.

The book is a Fourth Edition one: its numbers are converted by the
Definitive Edition's appendix as book_packs.fourth reads it, and each
judgement call is on the pack's assumptions page. Where a Fifth Edition
book describes the same thing it wins: Muscaria as Prima of Criamon (DE
p. 21; Houses of Hermes: Mystery Cults pp. 44, 55-57), and Andru,
Carmine and Valnastium (Houses of Hermes: Societates pp. 51-53).

Source: Sanctuary of Ice: The Greater Alps Tribunal (Atlas Games),
content under CC-BY-SA 4.0; the text here is a summary of it, not its
words."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder
from . import bestiary, covenants, places, stats_magi, stories, tribunal, world
from .state import Alps

NAME = "Sanctuary of Ice: the Greater Alps Tribunal"
SOURCE = (
    "Sanctuary of Ice: The Greater Alps Tribunal, by Atlas Games, content "
    "under the Creative Commons Attribution-ShareAlike 4.0 licence; "
    "summarised, not quoted."
)

#: The parts, in the order they are built: the places before the
#: covenants and lords that sit in them, the converted and generated
#: stats last, in `stats`.
PARTS = (tribunal, places, covenants, world, bestiary, stories, stats_magi)


def assemble() -> Builder:
    alps = Alps(Builder(NAME, source="SoI"))
    for part in PARTS:
        part.build(alps)
    for part in PARTS:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(alps)
    for part in PARTS:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(alps)
    return alps.b


def build() -> Saga:
    return assemble().saga


register(BookPack("alps", "SoI", NAME, assemble, SOURCE))
