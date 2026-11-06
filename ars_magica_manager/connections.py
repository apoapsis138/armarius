"""A record's connections: the records that point at it, or that it sits
in, as its sheet's Connections section shows them, each name a link.

Pattern: a derived reverse index. Each link is stored once, on the record
that makes it (a faction's Links, a neighbour's ruler, a covenant's
place, a gild's members), and the way back is worked out when the sheet
is drawn, so editing or deleting one side can never leave the other
stale. The headings are a list of small query functions, each giving the
facts it finds for a record (none for a record it doesn't apply to), as
Ahead's list of functions; a new kind of connection is one more
function."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from . import (
    memberships,
    open_stories,
    places,
    references,
    story_chapters,
    world,
)
from .models import Character, Covenant, Creature, Familiar, Laboratory, Neighbour, Saga
from .references import Fact, Ref
from .rules import sites
from .tribunal_packages import rhine

#: The sheets that show a Connections section.
SHOWN_ON = (Character, Covenant, Laboratory)


def link_kind(record: Any) -> str | None:
    """The kind a Link to `record` has (models.LINK_KINDS), or None for
    a record no Link points at."""
    if isinstance(record, Neighbour):
        return "places" if sites.is_place(record) else None
    return {
        Character: "characters",
        Covenant: "covenants",
        Creature: "creatures",
        Familiar: "familiars",
    }.get(type(record))


def _named(label: str, found: list[tuple[Any, str]]) -> list[Fact]:
    """A fact naming each of `found` (a record and its note), each
    linked; none while there are none."""
    shown = [(r, note) for r, note in found if references.ref(r) is not None]
    if not shown:
        return []
    value = ", ".join(f"{r.name} ({note})" if note else r.name for r, note in shown)
    return [Fact(label, value, references.refs(*(r for r, _ in shown)))]


def _linking(saga: Saga, record: Any) -> list[tuple[Any, str]]:
    kind = link_kind(record)
    if kind is None:
        return []
    return [
        (other, link.note)
        for other, link in world.links_to(saga, kind, record.id)
        if other is not record
    ]


def member_of(saga: Saga, record: Any) -> list[Fact]:
    """The factions whose members include `record`, each with its role."""
    return _named("Member of", list(memberships.factions_of(saga, record)))


def linked_from(saga: Saga, record: Any) -> list[Fact]:
    """Every other record whose Links include `record`."""
    return _named("Linked from", _linking(saga, record))


def links_back(saga: Saga, record: Any) -> list[Fact]:
    """The factions `record` is a member of, then every other record
    whose Links include it: a neighbour's or creature's page."""
    return member_of(saga, record) + linked_from(saga, record)


def _covenant(saga: Saga, record: Any) -> list[Fact]:
    """A character's or laboratory's covenant."""
    if not isinstance(record, (Character, Laboratory)):
        return []
    found = saga.covenant(record.covenant_id)
    return [Fact("Covenant", found.name, references.refs(found))] if found else []


def where_fact(label: str, saga: Saga, at: tuple[Neighbour, int] | None) -> list[Fact]:
    """The place `at` (a place and its level), then each place around
    it, outward, each linked; none for nowhere."""
    if at is None:
        return []
    place, level = at
    chain = [place, *places.inside_of(saga, place)]
    value = ", inside ".join(
        [places.where_text(saga, place.id, level), *(p.name for p in chain[1:])]
    )
    return [Fact(label, value, references.refs(*chain))]


def _located_in(saga: Saga, record: Any) -> list[Fact]:
    """Where a covenant or laboratory is."""
    if isinstance(record, Covenant):
        return where_fact("Located in", saga, sites.covenant_place(saga, record))
    if isinstance(record, Laboratory):
        return where_fact("Located in", saga, sites.lab_place(saga, record))
    return []


def lands_fact(saga: Saga, record: Any) -> list[Fact]:
    """The Tribunal whose lands `record` lies in (places.lands_of), linked;
    for a covenant, whether it is a member of that Tribunal too."""
    if not isinstance(record, (Covenant, Character, Laboratory, Neighbour, Creature)):
        return []
    lands = places.lands_of(saga, record)
    if lands is None:
        return []
    value = lands.name
    if isinstance(record, Covenant) and record.tribunal_id != lands.id:
        value += " (not a member)"
    return [Fact("Tribunal's lands", value, references.refs(lands))]


def _gilds(saga: Saga, record: Any) -> list[Fact]:
    """The gilds a covenant belongs to (a Rhine custom), and the
    Tribunal that keeps them."""
    if not isinstance(record, Covenant):
        return []
    tribunal = saga.tribunal(record.tribunal_id)
    names = rhine.gilds_of(tribunal, record) if tribunal is not None else []
    if tribunal is None or not names:
        return []
    return [
        Fact(
            "Gilds",
            f"{', '.join(names)}, in {tribunal.name}",
            references.refs(tribunal),
        )
    ]


def rules_facts(saga: Saga, record: Any) -> list[Fact]:
    """The neighbours `record` rules or leads, each linked; none while it
    rules none."""
    ruled = references.ruled_by(saga, record)
    if not ruled:
        return []
    return [Fact("Rules", ", ".join(n.name for n in ruled), references.refs(*ruled))]


#: Each heading's query, in the order a sheet shows them.
QUERIES: tuple[Callable[[Saga, Any], list[Fact]], ...] = (
    _covenant,
    _located_in,
    lands_fact,
    _gilds,
    member_of,
    rules_facts,
    linked_from,
    open_stories.facts,
    story_chapters.facts,
)


def facts(saga: Saga, record: Any) -> list[Fact]:
    """`record`'s connections, a fact for each heading that has any."""
    return [fact for query in QUERIES for fact in query(saga, record)]


def refs(saga: Saga, record: Any) -> list[tuple[str, Ref]]:
    """Each record the connections name, with its heading."""
    return [(f.label, r) for f in facts(saga, record) for r in f.refs]
