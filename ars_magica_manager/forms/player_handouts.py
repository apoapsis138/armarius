"""A Player's Handouts, to read (handout_list.py): a player's own, opened
from the page of any character they play; any Player's for the
storyguide, from that Player's row in Saga Management's Players. Choose a
Handout, then, when it was shown more than once, which copy; its copy
opens as a Show's does.

Where the list comes from: a Remote seat asks its host (Remote Proxy), the
host's own copy works it out from its Chronicles.

Pattern: Command steps (Choose, then the copy's Form), the same on both
front-ends; viewing decides whose list a reader may read (Protection
Proxy, handout_list.readable)."""

from __future__ import annotations

from typing import Any, Protocol

from .. import at_table, chronicle, handout_list, shows, virtual_tabletop
from ..commands import Choice, Choose, Command, Refuse
from ..markup import escape
from ..models import Character, Saga
from . import show as show_forms

TITLE = "Handouts"
HELP_ID = "handouts"


class Reads(Protocol):
    """Where a Player's Handouts are read: the seat's Table, or the
    host's own Chronicles."""

    def handouts(self, player_id: str) -> list[handout_list.Kept] | str: ...

    def open_handout(self, copy: handout_list.Copy) -> shows.Shown | str: ...


class HostReads:
    """The host's own copy: each list worked out from its Chronicles, as
    `who` may read it."""

    def __init__(self, saga: Saga, who: str) -> None:
        self.saga, self.who = saga, who

    def handouts(self, player_id: str) -> list[handout_list.Kept] | str:
        if not handout_list.readable(self.saga, player_id, self.who):
            return handout_list.NOT_YOURS
        return handout_list.of_player(self.saga, player_id)

    def open_handout(self, copy: handout_list.Copy) -> shows.Shown | str:
        return handout_list.open_copy(self.saga, copy, self.who)


def here(saga: Saga) -> Reads:
    """Where whoever uses this copy reads Handouts: through the Remote
    seat while one is attached, else this computer's Chronicles."""
    seat = at_table.seat()
    return seat if seat is not None else HostReads(saga, chronicle.here())


def _date(time: str) -> str:
    return time[:10]


def _open(reads: Reads, copy: handout_list.Copy) -> Command:
    found = reads.open_handout(copy)
    if isinstance(found, str):
        return Refuse(TITLE, escape(found))
    return show_forms.copy_form(found)


def _copies(reads: Reads, kept: handout_list.Kept) -> Command:
    """One Handout: its copy, or, shown more than once, which copy."""
    if len(kept.copies) == 1:
        return _open(reads, kept.copies[0])
    return Choose(
        escape(kept.title),
        lambda: [
            Choice(escape(f"{_date(c.time)}: {c.title}"), index)
            for index, c in enumerate(kept.copies)
        ],
        lambda index: _open(reads, kept.copies[index]),
        help_id=HELP_ID,
    )


def handouts(reads: Reads, player_id: str, whose: str = "") -> Command:
    """Player `player_id`'s Handouts, newest first, read through `reads`;
    `whose` names them in the title (none: the reader's own)."""
    found = reads.handouts(player_id)
    if isinstance(found, str):
        return Refuse(TITLE, escape(found))

    def label(kept: handout_list.Kept) -> str:
        shown = len(kept.copies)
        when = f"shown {shown} times, last {_date(kept.copies[0].time)}"
        return f"{kept.title} ({when if shown > 1 else _date(kept.copies[0].time)})"

    return Choose(
        f"{escape(whose)}'s {TITLE}" if whose else TITLE,
        lambda: [Choice(escape(label(k)), index) for index, k in enumerate(found)],
        lambda index: _copies(reads, found[index]),
        empty="Nothing has been shown to them yet."
        if whose
        else ("Nothing has been shown to you yet."),
        help_id=HELP_ID,
    )


def plays(character: Character, who: str) -> bool:
    """Whether `who` plays `character` (a shared one: any Player)."""
    b = character.background
    return bool(who) and (who in b.player_ids or b.everyone_plays)


def offered_on(saga: Saga, record: Any) -> bool:
    """Handouts, on the page of a character whoever uses this copy plays,
    while the Virtual Tabletop (Preview) is on."""
    del saga
    return (
        virtual_tabletop.on()
        and isinstance(record, Character)
        and plays(record, chronicle.here())
    )


def mine(saga: Saga, record: Any) -> Command:
    """The Handouts of whoever uses this copy, opened from the page of a
    character they play."""
    if not offered_on(saga, record):
        return Refuse(TITLE, "Handouts are opened from a character you play.")
    return handouts(here(saga), chronicle.here())


def of_player(saga: Saga, row: int | None) -> Command:
    """The Handouts of the Player chosen in Players, for the storyguide."""
    if row is None or not 0 <= row < len(saga.players):
        return Refuse(TITLE, "Choose a Player first.")
    player = saga.players[row]
    return handouts(here(saga), player.id, player.name)
