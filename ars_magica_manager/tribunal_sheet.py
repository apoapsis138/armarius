"""What a Tribunal's sheet says, for either front-end: the facts under
its name and its roster of covenants. Worked out from the covenants and
characters that belong to it (tribunals.py)."""

from __future__ import annotations

from . import tribunals, world
from .character_sheet import Fact
from .markup import escape
from .models import Saga, Tribunal
from .tables import Table


def next_meeting(tribunal: Tribunal) -> str:
    """When and where the Tribunal next meets, or "(not set)"."""
    if tribunal.next_year is None:
        return "(not set)"
    when = f"{tribunal.next_season} {tribunal.next_year}"
    place = tribunal.meeting_place.strip()
    return f"{when}, at {place}" if place else when


def _officer(saga: Saga, character_id: str | None) -> str:
    character = saga.character(character_id)
    return character.name if character is not None else "(not chosen)"


def _of_total(recorded: int, total: int | None) -> str:
    return f"{recorded} recorded of {total}" if total is not None else str(recorded)


def your_votes(saga: Saga, tribunal: Tribunal) -> int:
    """The player covenants' votes at `tribunal`."""
    return sum(
        world.votes(saga, c) for c in tribunals.covenants_of(saga, tribunal) if c.played
    )


def facts(saga: Saga, tribunal: Tribunal) -> list[Fact]:
    """The Tribunal's facts under its name."""
    members = tribunals.covenants_of(saga, tribunal)
    magi = sum(world.votes(saga, c) for c in members)
    return [
        Fact("Meets every", f"{tribunal.meets_every} years"),
        Fact(
            "Next meeting",
            "(not set)"
            if tribunal.next_year is None
            else f"{tribunal.next_season} {tribunal.next_year}",
        ),
        Fact("Meeting place", tribunal.meeting_place.strip() or "(not set)"),
        Fact("Praeco", _officer(saga, tribunal.praeco_id)),
        Fact("Presiding Quaesitor", _officer(saga, tribunal.quaesitor_id)),
        Fact("Covenants", _of_total(len(members), tribunal.covenants_total)),
        Fact("Magi", _of_total(magi, tribunal.magi_total)),
        Fact("Your votes", str(your_votes(saga, tribunal))),
    ]


def roster_rows(saga: Saga, tribunal: Tribunal) -> list[tuple[str, str, str, str]]:
    """Each covenant of the Tribunal: its name, whether the troupe plays
    it, its detail and its votes."""
    return [
        (
            c.name,
            "yours" if c.played else "",
            c.detail,
            str(world.votes(saga, c)),
        )
        for c in tribunals.covenants_of(saga, tribunal)
    ]


def roster_table(saga: Saga, tribunal: Tribunal) -> Table:
    """The roster as a table, a row for each covenant in roster order."""
    return Table(
        ["Covenant", "", "Detail", "Votes"],
        [list(row) for row in roster_rows(saga, tribunal)],
    )


def roster_lines(saga: Saga, tribunal: Tribunal) -> list[str]:
    """The roster as lines of markup for a list."""
    rows = roster_rows(saga, tribunal)
    if not rows:
        return []
    width = max(len(name) for name, *_ in rows)
    return [
        f"{escape(name.ljust(width))}  {played:<5}  {detail:<6}  "
        f"{votes} vote{'' if votes == '1' else 's'}"
        for name, played, detail, votes in rows
    ]
