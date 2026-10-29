"""The Dragon and the Bear: the Novgorod Tribunal, as of 1220, in
paraphrase.

Built in parts: the Tribunal itself, its Code, its history and its docket
for 1221; the Russian and Polish lands and the places of Slavic legend;
the four covenants the book describes, with their magi; the princes,
dukes, Church, towns, crusaders and pagans; the Bestiary of Slavic
faeries; the stories, with the Mongols' stages added to the shared
record; and last the nine printed magi, converted from the Fourth
Edition, with everyone else's generated stats.

The book is a Fourth Edition one: its numbers are converted by the
Definitive Edition's appendix as book_packs.fourth reads it, its faerie
powers by Realms of Power: Faerie, and each judgement call is on the
pack's assumptions page. No Fifth Edition book describes these covenants
or magi; where one touches the Tribunal it wins (the Gathering of the
Twelve Years in 1227, Guardians of the Forests).

Source: The Dragon and the Bear: The Novgorod Tribunal (Atlas Games),
content under CC-BY-SA 4.0; the text here is a summary of it, not its
words."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder
from ..records import Records
from . import bestiary, covenants, places, stats_magi, stories, tribunal, world

NAME = "The Dragon and the Bear: the Novgorod Tribunal"
SOURCE = (
    "The Dragon and the Bear: The Novgorod Tribunal, by Atlas Games, content "
    "under the Creative Commons Attribution-ShareAlike 4.0 licence; "
    "summarised, not quoted."
)

#: The parts, in the order they are built: the places before the
#: covenants and lords that sit in them; the stats go in last.
PARTS = (tribunal, places, covenants, world, bestiary, stories, stats_magi)


def assemble() -> Builder:
    records = Records(Builder(NAME, source="D&B"))
    for step in ("build", "finish", "stats"):
        for part in PARTS:
            run = getattr(part, step, None)
            if run is not None:
                run(records)
    return records.b


def build() -> Saga:
    return assemble().saga


register(BookPack("novgorod", "D&B", NAME, assemble, SOURCE))
