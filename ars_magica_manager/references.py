"""References from one record to another, as a page shows them: a fact
that names another record (a neighbour's ruler, its liege, the place it
is in, who answers to it) carries a `Ref` to each record it names, so a
front-end can draw those names as links that open them.

Pattern: an id reference, resolved when shown (as a neighbour's
answers_to). A Ref holds the record's kind and id, and the name it had
when the page was drawn; each front-end maps a kind to the function that
opens such a record (Strategy, reduced to a dict).

A neighbour's ruler (Neighbour.ruler) is a record's id or a typed name,
as a favour's owed_by is: a name opens the one character, neighbour or
creature that has it, and none while two have it or none does."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import (
    Character,
    Covenant,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Tribunal,
)


@dataclass(frozen=True)
class Ref:
    """A record a page names: its kind (one of KINDS), its id, and its
    name as the page shows it."""

    kind: str
    id: str
    name: str


@dataclass(frozen=True)
class Fact:
    """One labelled value; `value` is plain text, "" when not set. `refs`
    are the records named in it, which a front-end can draw as links
    (references.segments)."""

    label: str
    value: str
    refs: tuple[Ref, ...] = ()

    @property
    def missing(self) -> bool:
        return not self.value


#: The kinds of record a Ref opens, as the saga lists them.
KINDS: dict[type, str] = {
    Character: "characters",
    Covenant: "covenants",
    Laboratory: "laboratories",
    Familiar: "familiars",
    Tribunal: "tribunals",
    Neighbour: "neighbours",
    Creature: "creatures",
}

#: A Link's kind (models.LINK_KINDS) as a Ref's, for the ones a page
#: can open: a place is a neighbour.
LINK_KINDS: dict[str, str] = {
    "characters": "characters",
    "covenants": "covenants",
    "familiars": "familiars",
    "places": "neighbours",
    "creatures": "creatures",
}

#: What a neighbour's ruler can be.
RULER_KINDS: tuple[str, ...] = ("characters", "neighbours", "creatures")


def find(saga: Saga, kind: str, record_id: str | None) -> Any | None:
    """The record of `kind` with `record_id`, or None if it is gone."""
    if not record_id or kind not in KINDS.values():
        return None
    return next((r for r in getattr(saga, kind) if r.id == record_id), None)


def ref(record: Any) -> Ref | None:
    """A Ref to `record`, or None for nothing or a record no page shows."""
    kind = KINDS.get(type(record))
    return Ref(kind, record.id, record.name) if kind is not None else None


def refs(*records: Any) -> tuple[Ref, ...]:
    """Refs to each of `records` a page can show (None is passed over)."""
    return tuple(r for r in map(ref, records) if r is not None)


def target(saga: Saga, found: Ref) -> Any | None:
    """The record `found` names, or None if it is gone."""
    return find(saga, found.kind, found.id)


# -- a neighbour's ruler --


def ruler(saga: Saga, neighbour: Neighbour) -> Any | None:
    """The record a neighbour's ruler names: the character, neighbour or
    creature with that id, else the only one with that name; None for a
    name no record has (or more than one has)."""
    value = neighbour.ruler.strip()
    if not value:
        return None
    for kind in RULER_KINDS:
        found = find(saga, kind, value)
        if found is not None and found is not neighbour:
            return found
    named = [
        r
        for kind in RULER_KINDS
        for r in getattr(saga, kind)
        if r.name == value and r is not neighbour
    ]
    return named[0] if len(named) == 1 else None


def ruler_name(saga: Saga, neighbour: Neighbour) -> str:
    """The ruler as a page shows them: the record's name, or the name
    typed."""
    found = ruler(saga, neighbour)
    return found.name if found is not None else neighbour.ruler


def ruled_by(saga: Saga, record: Any) -> list[Neighbour]:
    """The neighbours whose ruler or leader is `record`."""
    return [n for n in saga.neighbours if n.ruler and ruler(saga, n) is record]


def forget_ruler(saga: Saga, record: Any) -> None:
    """Before `record` is deleted: the neighbours it rules keep its name."""
    for neighbour in saga.neighbours:
        if neighbour.ruler and neighbour.ruler == record.id:
            neighbour.ruler = record.name


# -- drawing a value with its references --


def segments(value: str, found: tuple[Ref, ...]) -> list[tuple[str, Ref | None]]:
    """`value` cut into its plain stretches and the names of `found` in
    it, in order, each name with its Ref: what a front-end draws as text
    and links. A name not in the value (after the ones before it) isn't
    linked."""
    parts: list[tuple[str, Ref | None]] = []
    at = 0
    for each in found:
        start = value.find(each.name, at) if each.name else -1
        if start < 0:
            continue
        if start > at:
            parts.append((value[at:start], None))
        parts.append((each.name, each))
        at = start + len(each.name)
    if at < len(value):
        parts.append((value[at:], None))
    return parts
