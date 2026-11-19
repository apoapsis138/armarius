"""A Remote seat's table for tests (at_table.Table): records what it is
asked, refuses nothing unless told, and opens form rolls through the
opener given."""

from __future__ import annotations

from collections.abc import Callable

from ars_magica_manager import chronicle, references, table_rolls


class FakeTable:
    def __init__(
        self,
        opener: Callable[[table_rolls.Opening], table_rolls.FormRoll] | None = None,
        *,
        refuse: str | None = None,
        held: chronicle.HasEntries | None = None,
    ) -> None:
        self.opener = opener
        self.refuse = refuse
        self._held = held
        self.rolled: list[chronicle.RollRequest] = []
        self.spent: list[tuple[int, int]] = []
        self.answered: list[tuple[int, str, bool]] = []
        self.said: list[tuple[str, tuple[str, ...]]] = []

    def roll(self, request: chronicle.RollRequest) -> str | None:
        self.rolled.append(request)
        return self.refuse

    def spend(self, number: int, points: int) -> str | None:
        self.spent.append((number, points))
        return self.refuse

    def answer(self, number: int, character_id: str, specialty: bool) -> str | None:
        self.answered.append((number, character_id, specialty))
        return self.refuse

    def say(
        self, words: str, to: tuple[str, ...], links: tuple[references.Ref, ...]
    ) -> str | None:
        del links
        self.said.append((words, to))
        return self.refuse

    def open_form_roll(self, opening: table_rolls.Opening) -> table_rolls.FormRoll:
        if self.opener is None:
            raise ValueError("This table opens no form rolls.")
        return self.opener(opening)

    def held(self) -> chronicle.HasEntries | None:
        return self._held
