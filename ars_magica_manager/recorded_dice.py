"""A source of chance that keeps the dice it gives out (STORY-2291,
STORY-2348): every face in order, and each whole die `rules.dice` makes
(its doublings and botch dice) kept together, for the dice line
(dice_text) to say. Table rolls record a form's dice with it
(table_rolls).

Pattern: Decorator. `RecordingDice` wraps any source of chance and adds
recording, so every rule that takes an `rng` takes it unchanged.
"""

from __future__ import annotations

import random
import secrets
from typing import Any

from .rules import dice as dice_rules

#: The most bits one draw asks for: a larger draw is made of several.
_CHUNK = 30


class DrawnDice(random.Random):
    """A source of chance whose every draw is a `randrange`: a choice, a
    shuffle or a float is made of dice too, so a source that records or
    fetches its dice (the host's, a seat's) sees all of them."""

    def random(self) -> float:
        return self.getrandbits(_CHUNK) / (1 << _CHUNK)

    def getrandbits(self, k: int, /) -> int:
        bits = 0
        while k > 0:
            take = min(k, _CHUNK)
            bits = (bits << take) | self.randrange(1 << take)
            k -= take
        return bits


#: A die as a form roll's entry keeps it: a whole die
#: (`{"stress", "faces", "botch_faces"}`, as `rules.dice.DieResult` has
#: them) or a face drawn outside the die helpers (`{"face"}`).
Die = dict[str, Any]


class RecordingDice(DrawnDice):
    """A source of chance that keeps every face it gives out, in order:
    `source`'s own (the host's `secrets.SystemRandom` unless given). A die
    (`randrange`, `randint`) is kept as its face; any other draw (a choice,
    a shuffle) goes through `randrange` too, so it is kept the same way.

    `dice` keeps the same faces grouped: each whole die `rules.dice`
    makes (it tells the source through `die_made`) with its doublings and
    botch dice, and each face drawn some other way on its own."""

    def __init__(self, source: random.Random | None = None) -> None:
        super().__init__()
        self._source = source if source is not None else secrets.SystemRandom()
        self.faces: list[int] = []
        #: How many of `faces` are already in a whole die of `_whole`.
        self._grouped = 0
        self._whole: list[Die] = []

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        face = self._source.randrange(start, stop, step)
        self.faces.append(face)
        return face

    def randint(self, a: int, b: int) -> int:
        face = self._source.randint(a, b)
        self.faces.append(face)
        return face

    def note(self, face: int) -> None:
        """Keep a face drawn from some other source (a watch's)."""
        self.faces.append(face)

    def die_made(self, die: dice_rules.DieResult) -> None:
        """`die`, just made from the last of the loose faces: kept whole
        (loose faces before it stay loose). A die whose faces aren't the
        last ones drawn is left as loose faces."""
        listener = getattr(self._source, "die_made", None)
        if callable(listener):  # a recording source under this one
            listener(die)
        thrown = [*die.faces, *die.botch_faces]
        loose = self.faces[self._grouped :]
        if not thrown or loose[len(loose) - len(thrown) :] != thrown:
            return
        before = len(self.faces) - len(thrown)
        self._whole.extend({"face": f} for f in self.faces[self._grouped : before])
        self._whole.append(
            {
                "stress": die.stress,
                "faces": list(die.faces),
                "botch_faces": list(die.botch_faces),
            }
        )
        self._grouped = len(self.faces)

    @property
    def dice(self) -> list[Die]:
        """Every face drawn, as whole dice and loose faces, in order."""
        return [*self._whole, *({"face": f} for f in self.faces[self._grouped :])]
