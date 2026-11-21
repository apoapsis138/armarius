"""What can be done at the table while a Session is under way, as one
interface: roll, spend Confidence, answer a Roll request, send a Message,
open a form's roll, Show something and open a Show's copy, and set and
end a Scene. The host's own window does each in its Chronicle
(host_table.HostTable); a Remote seat asks its host (seat_session's
SeatTable). The pane, the sheet's Roll and the Table roll forms take a
Table and never ask which one they have.

At a Remote seat the window hands its seat's Table here (`use_seat`)
while the seat's Chronicle pane is attached, for the forms opened from a
sheet, which have no pane to ask.

Pattern: Remote Proxy, as the saga store (ADR 0011): one interface, an
adapter at the host and one at a seat."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from . import chronicle, references, shows


@dataclass(frozen=True)
class Opening:
    """What a form roll is, as the host is told before its first die: the
    form's name, the character (none: the storyguide's own) and who sees
    it."""

    form: str
    character_id: str
    visibility: str


class FormRoll(Protocol):
    """One form roll being saved: where its dice come from, and how it
    ends. `finish` writes it with the form's result lines (the reason it
    couldn't be, or None); `cancel` writes the dice drawn so far as
    cancelled."""

    @property
    def dice(self) -> random.Random: ...

    def finish(self, lines: list[str]) -> str | None: ...

    def cancel(self) -> None: ...


class Table(Protocol):
    """The table, as whoever sits here acts at it. Each verb gives None
    once its entry is in the Chronicle, else the reason it wasn't (refused,
    or couldn't be saved or sent)."""

    def roll(self, request: chronicle.RollRequest) -> str | None: ...

    def spend(self, number: int, points: int) -> str | None: ...

    def answer(self, number: int, character_id: str, specialty: bool) -> str | None: ...

    def say(
        self, words: str, to: tuple[str, ...], links: tuple[references.Ref, ...]
    ) -> str | None: ...

    def open_form_roll(self, opening: Opening) -> FormRoll:
        """A form's roll opened at the table; ValueError says why it
        can't be made."""
        ...

    def show(self, call: chronicle.ShowCall) -> str | None: ...

    def open_show(self, entry: chronicle.Entry) -> shows.Shown | str:
        """The copy Show `entry` names, as this person may open it, or why
        it can't be opened."""
        ...

    def set_scene(self, call: chronicle.SceneCall) -> str | None: ...

    def end_scene(self) -> str | None: ...

    def held(self) -> chronicle.HasEntries | None:
        """The Chronicle as this copy holds it (None: it can't be read)."""
        ...


_seat: Table | None = None


def use_seat(table: Table | None) -> None:
    """Act at the table through `table` (a Remote seat's), or at the host's
    own Chronicle (None)."""
    global _seat
    _seat = table


def seat() -> Table | None:
    """The Remote seat's Table, while its pane is attached; None on the
    host's own computer."""
    return _seat
