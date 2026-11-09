"""A saga as one reader may have it: what leaves the host for a Remote seat,
and what a player's export carries.

The pages hide a great deal from a player as they are drawn (viewing.py):
records the players don't know of, Secrets not revealed, a threat's stages
still to come and its clock, a place's Roll Tables, Diary lines about
unknown records, secret pins, a hidden research target. That is enough
while the copy a player reads runs on the storyguide's computer. A Remote
seat is handed data, and a player who controls their own copy could read
whatever is only hidden on screen, so `seat_view` takes it out of the data
itself, by the same rules (viewing.py's functions, asked with the reader as
the viewer): one rule for the screen and the data, not two.

What it keeps, it keeps whole: drawn as the same reader, the copy shows
exactly what the full saga shows (tests/test_seat_view.py draws every sheet
both ways). The Players stay as names and roles only, so "Played by" still
reads; their passcode hashes never leave.

Pattern: Protection Proxy, at the data's edge rather than the page's.
"""

from __future__ import annotations

import copy
from collections.abc import Iterator
from contextlib import contextmanager

from . import memberships, threats, viewing, world
from .models import Pin, Player, Saga
from .place_events import diary as place_diary
from .place_events import tables as place_tables
from .references import Ref

#: The record lists a Secret can sit on.
_WITH_SECRETS = ("characters", "covenants", "neighbours", "creatures", "tribunals")
#: The record lists with links to other records.
_WITH_LINKS = ("characters", "covenants", "neighbours", "creatures")


@contextmanager
def looking_as(viewer: viewing.Viewer, saga: Saga) -> Iterator[None]:
    """Ask viewing.py's questions as `viewer` reading `saga`, then put
    back whoever was looking."""
    before, before_saga = viewing.current(), viewing.in_use_saga()
    viewing.use(viewer, saga)
    try:
        yield
    finally:
        viewing.use(before, before_saga)


def seat_view(saga: Saga, viewer: viewing.Viewer) -> Saga:
    """A copy of `saga` holding only what `viewer` may read. The
    storyguide's is the whole saga, less the passcode hashes; among
    several storyguides, a record another runs is as the players have it
    (ADR 0015)."""
    view = copy.deepcopy(saga)
    view.players = [_name_only(p) for p in saga.players]
    if viewing.reads_everything(viewer, view):
        return view
    with looking_as(viewer, view):
        held = _held(view, viewer)
        _hide_lines(view, viewer)
        _hide_threat_futures(view, held)
        _hide_secrets(view, held)
        _hide_tables_and_targets(view, held)
        _hide_private(view, viewer)
        _hide_unknown(view, viewer)
    return view


def _hide_private(view: Saga, viewer: viewing.Viewer) -> None:
    """A character's private notes and unshared goals, for anyone but its
    players, Steward and storyguide: not even that they exist."""
    for character in view.characters:
        if not viewing.reads_private(viewer, character, view):
            character.private_notes = ""
            character.goals = [g for g in character.goals if g.shared]


def _held(view: Saga, viewer: viewing.Viewer) -> set[int]:
    """The records `viewer` reads whole, by identity, asked once before
    any is changed."""
    return {
        id(record)
        for kind in _WITH_SECRETS
        for record in getattr(view, kind)
        if viewing.holds(viewer, record, view)
    }


def _name_only(player: Player) -> Player:
    return Player(id=player.id, name=player.name, role=player.role)


def _hide_lines(view: Saga, viewer: viewing.Viewer) -> None:
    """Diary lines, links and members that name a record the reader
    doesn't know of. Asked before those records go, while they can still
    be found."""
    for covenant in view.covenants:
        covenant.diary = [
            e for e in covenant.diary if viewing.diary_readable(view, e, viewer)
        ]
    for neighbour in view.neighbours:
        lines = place_diary(neighbour)
        lines[:] = [
            line for line in lines if viewing.line_readable(view, dict(line), viewer)
        ]
        if "roster" in neighbour.details:
            roster = memberships.roster(neighbour)
            roster[:] = [
                m
                for m in roster
                if (found := memberships.record_of(view, m)) is None
                or viewing.may_read(viewer, found)
            ]
    for kind in _WITH_LINKS:
        for record in getattr(view, kind):
            record.links = [
                link
                for link in record.links
                if (target := world.link_target(view, link)) is None
                or viewing.may_read(viewer, target)
            ]

    def pin_kept(pin: Pin) -> bool:
        found = Ref(pin.kind, pin.record_id, "")
        if viewing.ref_held(view, found, viewer):
            return True
        return not pin.secret and not pin.hidden and viewing.ref_known(view, found)

    view.pins = [pin for pin in view.pins if pin_kept(pin)]


def _hide_threat_futures(view: Saga, held: set[int]) -> None:
    """A threat as the players learn of it: the stages that have come or
    been marked, never its antagonist, clock or what is still to come."""
    for neighbour in view.neighbours:
        if neighbour.kind != threats.THREAT or id(neighbour) in held:
            continue
        stages = threats.stages(neighbour)
        stages[:] = [s for s in stages if threats.shows_stage(view, neighbour, s)]
        details = neighbour.details
        details.pop("antagonist", None)
        if not threats.by_date(neighbour):
            # Its position up to the last stage shown, so what has come
            # still has, and no further.
            reached = [s.get("at") or 0 for s in stages]
            details["position"] = min(
                threats.position(neighbour), max(reached, default=0)
            )


def _hide_secrets(view: Saga, held: set[int]) -> None:
    for kind in _WITH_SECRETS:
        for record in getattr(view, kind):
            if id(record) not in held:
                record.secrets = [
                    s for s in record.secrets if s.revealed_year is not None
                ]


def _hide_tables_and_targets(view: Saga, held: set[int]) -> None:
    """A place's Roll Tables are the storyguide's; so is a research
    target kept hidden until it is reached."""
    for neighbour in view.neighbours:
        if "tables" in neighbour.details and id(neighbour) not in held:
            place_tables(neighbour).clear()
    for character in view.characters:
        if id(character) in held:
            continue
        for goal in character.breakthroughs:
            if goal.hidden_target and not goal.reached:
                goal.target = 0


def _hide_unknown(view: Saga, viewer: viewing.Viewer) -> None:
    """The records the reader doesn't know of, gone."""

    def kept(record: object) -> bool:
        return viewing.readable(viewer, record, view)

    view.characters = [c for c in view.characters if kept(c)]
    view.covenants = [c for c in view.covenants if kept(c)]
    view.neighbours = [n for n in view.neighbours if kept(n)]
    view.creatures = [c for c in view.creatures if kept(c)]
