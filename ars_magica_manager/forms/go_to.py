"""Go To: the records a page names, to open one, for either front-end.
The terminal offers it in More; the desktop draws each name as a link
instead, and gives a Links row an Open button (open_link).

What a page names comes from its facts' references (references.Ref):
a neighbour's ruler, liege and place, who answers to it, and what its
kind works out (a place's claimant and what is found there); a
character's, covenant's or laboratory's Connections; then its Links.
Choosing one ends the steps with a commands.Go, which the front-end
follows."""

from __future__ import annotations

from typing import Any

from .. import connections, neighbours, references
from ..commands import Act, Choice, Choose, Command, Go, Refuse
from ..markup import escape
from ..models import Creature, Neighbour, Saga
from ..references import Ref
from ..sheets import creature as creature_sheet
from ..sheets import region as region_sheet
from ..sheets.character import Fact

#: A Link's kind as Go To heads it.
_LINK_HEADING = "Links"


def _facts(saga: Saga, record: Any) -> list[Fact]:
    """The facts `record`'s page shows that can name other records."""
    if isinstance(record, Creature):
        return creature_sheet.facts(saga, record)
    if isinstance(record, connections.SHOWN_ON):
        return connections.facts(saga, record)
    if not isinstance(record, Neighbour):
        return []
    facts = region_sheet.neighbour_facts(saga, record)
    worked_out = neighbours.kind_of(record).facts
    if worked_out is not None:
        facts += worked_out(saga, record)
    return facts


def _fact_targets(saga: Saga, record: Any) -> list[tuple[str, Ref]]:
    facts = _facts(saga, record)
    return [(fact.label, found) for fact in facts for found in fact.refs]


def link_ref(saga: Saga, link: Any) -> Ref | None:
    """A Ref to what a Link points at, or None for one no page shows (a
    book, a possession) or one gone."""
    kind = references.LINK_KINDS.get(link.kind)
    found = references.find(saga, kind, link.target_id) if kind else None
    return references.ref(found)


def targets(saga: Saga, record: Any) -> list[tuple[str, Ref]]:
    """What `record`'s page names that a page can show, each once, with
    the label it is named under: its facts', then its links'."""
    found = _fact_targets(saga, record)
    for link in getattr(record, "links", []):
        linked = link_ref(saga, link)
        if linked is not None:
            found.append((_LINK_HEADING, linked))
    seen: set[tuple[str, str]] = {(record_kind(record), getattr(record, "id", ""))}
    shown: list[tuple[str, Ref]] = []
    for label, each in found:
        key = (each.kind, each.id)
        if key not in seen and references.target(saga, each) is not None:
            seen.add(key)
            shown.append((label, each))
    return shown


def record_kind(record: Any) -> str:
    return references.KINDS.get(type(record), "")


def go_to(saga: Saga, record: Any) -> Command:
    """Go To: choose one of the records `record`'s page names, and open
    it."""
    named = targets(saga, record)
    if not named:
        return Refuse("Go To", "This page names no other record.")
    return Choose(
        "Go To",
        lambda: [
            Choice(
                escape(each.name),
                each,
                f"[$label]{escape(label)}[/]",
                facets=(("Named as", label),),
            )
            for label, each in named
        ],
        Go,
        filters=("Named as",),
        help_id="go-to",
    )


def open_link(saga: Saga, record: Any, row: int) -> Command:
    """A Links row's Open: the record it points at."""
    links = getattr(record, "links", [])
    found = link_ref(saga, links[row]) if row < len(links) else None
    if found is None:
        return Refuse("Open", "That link points at nothing a page shows.")
    return Act(lambda: Go(found))


def opens(saga: Saga, record: Any, row: int) -> bool:
    """Whether a Links row's Open has a page to go to."""
    links = getattr(record, "links", [])
    return row < len(links) and link_ref(saga, links[row]) is not None


def has_targets(saga: Saga, record: Any) -> bool:
    return bool(targets(saga, record))
