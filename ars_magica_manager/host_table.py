"""The table on the host's own computer: each verb done in the Session's
Chronicle open here, by whoever uses this copy of the app.

Pattern: an Adapter at the Table's seam (at_table.Table); the seat's is
seat_session.SeatTable."""

from __future__ import annotations

from collections.abc import Callable

from . import (
    at_table,
    chronicle,
    handout_arrangement,
    handout_list,
    references,
    scene_play,
    shows,
    table_rolls,
    table_rules,
)
from .at_table import FormRoll, Opening, Table
from .models import Saga, Session

#: Why a record's Show can't be made from here: no copier was given.
NO_COPIER = "Show from the Session's page."


def _no_copier(_saga: Saga, _record: object, _ticked: tuple[int, ...]) -> str:
    raise ValueError(NO_COPIER)


class HostTable:
    """The table at the host: `who` acts in `session`'s Chronicle. A Show's
    copy is made by `copier` (show_copy.player_copy, which the forms that
    show give, from a layer above)."""

    def __init__(
        self,
        saga: Saga,
        session: Session,
        who: str,
        copier: shows.Copier | None = None,
    ) -> None:
        self.saga, self.session, self.who = saga, session, who
        self.copier = copier

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

    def show(self, call: chronicle.ShowCall) -> str | None:
        copier = self.copier or _no_copier
        return self._write(
            lambda book: shows.show(
                book, self.saga, self.session, call, by=self.who, copier=copier
            ),
            "The Show couldn't be saved.",
        )

    def open_show(self, entry: chronicle.Entry) -> shows.Shown | str:
        if not chronicle.sees(entry, self.who, self.session, self.saga):
            return "This Show isn't for you."
        if self.who != table_rules.storyguide_of(self.session, self.saga):
            # A player opens it only once the Chronicle says it is still out.
            book = self.held()
            if book is None:
                return shows.UNREAD_NOTE
            if entry.number in shows.withdrawn(book):
                return shows.WITHDRAWN_NOTE
        try:
            return shows.opened(self.saga.id, entry)
        except ValueError as problem:
            return str(problem)

    def handouts(self, player_id: str) -> list[handout_list.Kept] | str:
        if not handout_list.readable(self.saga, player_id, self.who):
            return handout_list.NOT_YOURS
        return handout_list.of_player(self.saga, player_id)

    def open_handout(self, copy: handout_list.Copy) -> shows.Shown | str:
        return handout_list.open_copy(self.saga, copy, self.who)

    def search_handouts(self, player_id: str, words: str) -> set[str] | str:
        if not handout_list.readable(self.saga, player_id, self.who):
            return handout_list.NOT_YOURS
        return handout_list.matching(self.saga, player_id, words)

    def arrangement(self, player_id: str) -> handout_arrangement.Arrangement | str:
        return handout_arrangement.arrangement_of(self.saga.id, player_id, self.who)

    def arrange(self, player_id: str, call: handout_arrangement.Arrange) -> str | None:
        return handout_arrangement.arrange(self.saga, player_id, call, by=self.who)

    def withdraw(self, number: int) -> str | None:
        return self._write(
            lambda book: shows.withdraw(
                book, self.saga, self.session, number, by=self.who
            ),
            "The Show couldn't be withdrawn just now.",
        )

    def set_scene(self, call: chronicle.SceneCall) -> str | None:
        return self._write(
            lambda book: scene_play.set_scene(
                book, self.saga, self.session, call, by=self.who
            ),
            "The Scene couldn't be saved.",
        )

    def end_scene(self) -> str | None:
        return self._write(
            lambda book: scene_play.end_scene(
                book, self.saga, self.session, by=self.who
            ),
            "The Scene's end couldn't be saved.",
        )

    def held(self) -> chronicle.HasEntries | None:
        try:
            return chronicle.read(self.saga, self.session)
        except OSError, ValueError:
            return None


def here(
    saga: Saga, session: Session, who: str, copier: shows.Copier | None = None
) -> Table:
    """The table as this copy acts at it: the Remote seat's, while one is
    attached, else the host's own Chronicle by `who` (Shows' copies made
    by `copier`)."""
    seat = at_table.seat()
    return seat if seat is not None else HostTable(saga, session, who, copier)
