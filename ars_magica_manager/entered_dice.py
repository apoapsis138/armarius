"""Entered dice (STORY-2459): a source of chance that gives out the
faces a person read off their own d10s, in order, instead of rolling.

When a rule throws a die the person hasn't entered yet, the source stops
the roll with `NeedDie`, saying which die is needed and why ("Bero's
Defence: a 1: roll again and double"). The form asks for that one face and
plays the roll again from the start with the faces so far; the rules work
out doublings and botches from the faces as they always do (rules.dice;
DE pp. 7-8).

Only d10s are asked for. A draw that is no die anyone throws (a tie
broken by chance) is settled at once, the same way every time.

Pattern: Strategy. A rule takes any source of chance; this one asks a
person where the usual one rolls. `RecordingDice` (a Decorator) wraps it
as it wraps any other, so the dice line sees entered dice like rolled ones.
"""

from __future__ import annotations

from collections.abc import Sequence

from .recorded_dice import DrawnDice


class NeedDie(Exception):
    """A roll stopped for a die not yet entered: `why` says which."""

    def __init__(self, why: str) -> None:
        super().__init__(why)
        self.why = why


class EnteringDice(DrawnDice):
    """The faces entered so far (0-9 each), given out in order."""

    def __init__(self, faces: Sequence[int] = ()) -> None:
        super().__init__()
        self._faces = list(faces)
        self._given = 0
        self._label = ""
        self._why = "a die"

    def rolling(self, label: str) -> None:
        """The roll the next dice are for (rules.dice.rolling)."""
        self._label = label

    def throwing(self, why: str) -> None:
        """The next throw's part in its die (rules.dice)."""
        self._why = why

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        if (start, stop, step) != (10, None, 1):
            return start if stop is not None else 0
        if self._given >= len(self._faces):
            why = f"{self._label}: {self._why}" if self._label else self._why
            raise NeedDie(why)
        face = self._faces[self._given]
        self._given += 1
        return face
