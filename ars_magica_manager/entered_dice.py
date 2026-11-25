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

import copy
import random
from collections.abc import Callable, Sequence
from typing import Any

from . import viewing
from .commands import Form
from .form_spec import DialogField
from .markup import escape
from .models import Saga
from .recorded_dice import DrawnDice
from .rules import options


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


# -- a command whose dice may be entered --

#: The Dice choice: the app rolls, or the person enters the dice.
ROLL = "roll"
ENTER = "enter"


def dice_fields(saga: Saga, hint: str = "") -> list[DialogField]:
    """The Dice choice, while the saga allows entered dice (none else)."""
    if not options.is_on(saga, options.ENTERED_DICE_ALLOWED):
        return []
    return [
        DialogField(
            "dice",
            "Dice",
            "select",
            ROLL,
            options=[("Roll for me", ROLL), ("I'll roll it", ENTER)],
            hint=hint
            or "I'll roll it asks for each die in turn, saying whose roll it "
            "is and why.",
        )
    ]


def chosen(values: dict[str, Any]) -> bool:
    """Whether the form's Dice says I'll roll it."""
    return values.get("dice") == ENTER


def marked(said: str, entered: bool) -> str:
    """A dice line, marked with who entered its dice when they were."""
    if not (said and entered):
        return said
    viewer = viewing.current()
    who = viewer.player.name if viewer.player is not None else "the storyguide"
    return f"{said} (entered by {who})"


def place(records: Sequence[object], record: object) -> int:
    """Where `record` itself is in `records` (not an equal one): looked up
    afresh for each try, since the list may change while dice are entered."""
    return next(i for i, found in enumerate(records) if found is record)


def entered(
    saga: Saga,
    where: str,
    trial: Callable[[Saga, random.Random], object],
    play: Callable[[random.Random], Any],
    faces: tuple[int, ...] = (),
) -> Any:
    """Play with the dice a person enters (ADR 0032): `trial` is played on
    a copy of the saga with the faces so far, and each die it lacks is
    asked for in turn; once it needs none, `play` plays it for real with
    them. The saga changes only then, so stopping part way leaves it as it
    was. `where` (the fight, the siege) heads each prompt's hint."""
    try:
        trial(copy.deepcopy(saga), EnteringDice(faces))
    except NeedDie as need:
        return die_prompt(
            where,
            need.why,
            lambda face: entered(saga, where, trial, play, (*faces, face)),
        )
    return play(EnteringDice(faces))


def die_prompt(where: str, why: str, then: Callable[[int], Any]) -> Form:
    """Ask for one d10's face, as read (0 to 9), for `why` ("Bero's
    Defence: stress die"); `then` gets the face."""
    return Form(
        escape(why),
        lambda: [
            DialogField(
                "face",
                "Face",
                "select",
                None,
                options=[(str(n), str(n)) for n in range(10)],
                required=True,
                allow_blank=True,
                hint=f"{escape(where)}: the face your d10 shows, 0 to 9 "
                "(a 0 is a 0: it may call for botch dice).",
            )
        ],
        lambda values: then(int(values["face"])),
        save_label="Enter",
        help_id="entered-dice",
    )
