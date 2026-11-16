"""The records beside one on the desktop's trail: the other people of a
character's covenant, the other laboratories of a laboratory's, and the
saga's other covenants, for the last crumb's switcher.

Pattern: Iterator. `siblings` walks the records at one level of the trail
one at a time, group by group, so the switcher lists them without knowing
where each kind is kept or how it is grouped. It yields only what whoever
is looking may read (viewing.reads: Player view and a player's seat).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from . import viewing, world
from .models import Saga
from .saga_overview import people_groups

#: The kinds of record that have siblings: the trail's own place kinds.
CHARACTER, LABORATORY, COVENANT = "character", "laboratory", "covenant"
KINDS = (CHARACTER, LABORATORY, COVENANT)

#: The groups the saga's covenants are listed in, troupe covenants first.
TROUPE, REGION = "The Troupe's", "The Region's"


@dataclass(frozen=True)
class Sibling:
    """One record at the level asked about: the group it is listed under
    ("" when the list has none), its id and its name."""

    group: str
    id: str
    name: str


def siblings(saga: Saga, kind: str, record_id: str | None) -> Iterator[Sibling]:
    """The records at the level of `record_id`, a record of `kind` (KINDS),
    in the order the pages list them, itself among them: a character's
    covenant's people by Magi, Companions and Grogs (the saga's unassigned
    people for one of no covenant); a laboratory's covenant's laboratories;
    the saga's covenants, the troupe's then the Region's. Nothing for a
    record that is gone or a kind with no siblings."""
    if kind == CHARACTER:
        character = saga.character(record_id)
        if character is None:
            return
        for group, people in people_groups(saga, character.covenant_id):
            for person in people:
                if viewing.reads(person):
                    yield Sibling(group, person.id, person.name or "(unnamed)")
    elif kind == LABORATORY:
        lab = saga.laboratory(record_id)
        if lab is None:
            return
        for other in saga.laboratories:
            if other.covenant_id == lab.covenant_id and viewing.reads(other):
                yield Sibling("", other.id, other.name or "(unnamed)")
    elif kind == COVENANT:
        readable = [c for c in saga.covenants if viewing.reads(c)]
        for covenant in world.troupe_first(readable):
            group = TROUPE if covenant.played else REGION
            yield Sibling(group, covenant.id, covenant.name or "(unnamed)")
