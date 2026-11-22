"""A Remote seat's table for tests (at_table.Table): records what it is
asked, refuses nothing unless told, and opens form rolls through the
opener given."""

from __future__ import annotations

from collections.abc import Callable

from ars_magica_manager import (
    chronicle,
    handout_arrangement,
    handout_list,
    references,
    shows,
    table_rolls,
)


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
        self.shown: list[chronicle.ShowCall] = []
        self.opened: list[int] = []
        self.scenes_set: list[chronicle.SceneCall] = []
        self.scenes_ended = 0
        self.withdrawn: list[int] = []
        self.arranged: list[handout_arrangement.Arrange] = []

    def handouts(self, player_id: str) -> list[handout_list.Kept] | str:
        del player_id
        return self.refuse or []

    def open_handout(self, copy: handout_list.Copy) -> shows.Shown | str:
        return self.refuse or shows.Shown(copy.title, "Copy.")

    def search_handouts(self, player_id: str, words: str) -> set[str] | str:
        del player_id, words
        return self.refuse or set()

    def arrangement(self, player_id: str) -> handout_arrangement.Arrangement | str:
        del player_id
        return self.refuse or handout_arrangement.Arrangement()

    def arrange(self, player_id: str, call: handout_arrangement.Arrange) -> str | None:
        del player_id
        self.arranged.append(call)
        return self.refuse

    def withdraw(self, number: int) -> str | None:
        self.withdrawn.append(number)
        return self.refuse

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

    def show(self, call: chronicle.ShowCall) -> str | None:
        self.shown.append(call)
        return self.refuse

    def open_show(self, entry: chronicle.Entry) -> shows.Shown | str:
        self.opened.append(entry.number)
        return self.refuse or shows.Shown(str(entry.body.get("title", "")), "Copy.")

    def set_scene(self, call: chronicle.SceneCall) -> str | None:
        self.scenes_set.append(call)
        return self.refuse

    def end_scene(self) -> str | None:
        self.scenes_ended += 1
        return self.refuse

    def held(self) -> chronicle.HasEntries | None:
        return self._held
