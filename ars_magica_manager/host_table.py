"""The table on the host's own computer: each verb done in the Session's
Chronicle open here, by whoever uses this copy of the app.

Pattern: an Adapter at the Table's seam (at_table.Table); the seat's is
seat_session.SeatTable."""

from __future__ import annotations

from collections.abc import Callable

from . import at_table, chronicle, references, table_rolls
from .at_table import FormRoll, Opening, Table
from .models import Saga, Session


class HostTable:
    """The table at the host: `who` acts in `session`'s Chronicle."""

    def __init__(self, saga: Saga, session: Session, who: str) -> None:
        self.saga, self.session, self.who = saga, session, who

    def _write(
        self, act: Callable[[chronicle.Chronicle], object], saved: str
    ) -> str | None:
        """Do `act` in the Chronicle: None, or why it wasn't done."""
        try:
            act(chronicle.read(self.saga, self.session))
        except ValueError as problem:
            return str(problem)
        except OSError:
            return saved
        return None

    def roll(self, request: chronicle.RollRequest) -> str | None:
        return self._write(
            lambda book: chronicle.free_roll(
                book, self.saga, self.session, request, by=self.who
            ),
            "The roll couldn't be saved.",
        )

    def spend(self, number: int, points: int) -> str | None:
        return self._write(
            lambda book: chronicle.spend_confidence(
                book, self.saga, self.session, number, points, by=self.who
            ),
            "The Chronicle couldn't be saved.",
        )

    def answer(self, number: int, character_id: str, specialty: bool) -> str | None:
        return self._write(
            lambda book: chronicle.answer(
                book,
                self.saga,
                self.session,
                number,
                character_id,
                by=self.who,
                specialty=specialty,
            ),
            "The roll couldn't be saved.",
        )

    def say(
        self, words: str, to: tuple[str, ...], links: tuple[references.Ref, ...]
    ) -> str | None:
        return self._write(
            lambda book: chronicle.message(
                book, self.saga, self.session, words, to=to, links=links, by=self.who
            ),
            "The Message couldn't be saved.",
        )

    def open_form_roll(self, opening: Opening) -> FormRoll:
        return table_rolls.HostRoll(self.saga, self.session, opening, by=self.who)

    def held(self) -> chronicle.HasEntries | None:
        try:
            return chronicle.read(self.saga, self.session)
        except OSError, ValueError:
            return None


def here(saga: Saga, session: Session, who: str) -> Table:
    """The table as this copy acts at it: the Remote seat's, while one is
    attached, else the host's own Chronicle by `who`."""
    seat = at_table.seat()
    return seat if seat is not None else HostTable(saga, session, who)
