"""Dice: simple and stress dice, botch dice, and rolls against
an Ease Factor. Every function takes the random number generator, so a
caller (or a test) decides the source of chance.

- Simple die: 1d10, a 0 reads as 10. Never botches or explodes.
- Stress die: 2-9 at face value; a 1 re-rolls and doubles (each further 1
  doubles again, and a re-rolled 0 reads as 10); a 0 on the first throw is
  0, and the botch dice are rolled: any 0 among them is a botch.
- A botched roll totals min(0, modifiers): the Characteristic, Ability and
  positive modifiers are cancelled.

With the saga's "Simple dice only" option on (rules.options), every stress
die is rolled as a simple die.

No screen uses botch_chance(), ease_factor_label() yet: they are the rules
for screens still to come, and only the tests call them.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import Saga
from . import options

SOURCE = (
    "Ars Magica Definitive Edition, Chapter One: Introduction, Simple Die, "
    "Stress Die and Botch Dice "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_One:"
    "_Introduction#Stress_Die)"
)

#: The Ease Factor labels (DE Chapter One, Ease Factors).
EASE_FACTORS: tuple[tuple[int, str], ...] = (
    (0, "Trivial"),
    (3, "Simple"),
    (6, "Easy"),
    (9, "Average"),
    (12, "Hard"),
    (15, "Very Hard"),
    (18, "Impressive"),
    (21, "Remarkable"),
    (24, "Almost impossible"),
)


def _d10(rng: random.Random) -> int:
    """One throw of a d10, as its face: 0-9."""
    return rng.randrange(10)


def simple_die(rng: random.Random) -> int:
    """1-10 (a 0 reads as 10)."""
    return _d10(rng) or 10


@dataclass(frozen=True)
class DieResult:
    """A die's value, the faces thrown for it, and for a stress die that
    showed 0, the botch dice and how many of them came up 0."""

    value: int
    faces: tuple[int, ...]
    stress: bool = True
    botch_faces: tuple[int, ...] = ()

    @property
    def botches(self) -> int:
        """How many botch dice showed 0: 0 is no botch, 1 bad, 2 worse, 3+
        about as bad as it gets."""
        return self.botch_faces.count(0)

    @property
    def botched(self) -> bool:
        return self.botches > 0

    @property
    def doublings(self) -> int:
        """How many 1s the stress die exploded on."""
        return self.faces[:-1].count(1) if self.stress else 0


def stress_die(
    rng: random.Random, botch_dice: int = 1, *, saga: Saga | None = None
) -> DieResult:
    """A stress die with `botch_dice` botch dice (0 when disaster can't be
    the outcome). A simple die instead when the saga rolls simple dice only."""
    if options.is_on(saga, "simple_dice_only"):
        value = simple_die(rng)
        return DieResult(value=value, faces=(value % 10,), stress=False)
    first = _d10(rng)
    if first == 0:
        botch_faces = tuple(_d10(rng) for _ in range(max(botch_dice, 0)))
        return DieResult(value=0, faces=(0,), botch_faces=botch_faces)
    faces = [first]
    multiplier = 1
    while faces[-1] == 1:
        multiplier *= 2
        faces.append(_d10(rng))
    last = faces[-1] if len(faces) == 1 else (faces[-1] or 10)
    return DieResult(value=last * multiplier, faces=tuple(faces))


def simple_roll(rng: random.Random) -> DieResult:
    value = simple_die(rng)
    return DieResult(value=value, faces=(value % 10,), stress=False)


@dataclass(frozen=True)
class Roll:
    """A roll: its modifiers (Characteristic + Ability + the rest), the die,
    and the total, compared with an Ease Factor when there is one."""

    modifiers: int
    die: DieResult
    ease_factor: int | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        if self.die.botched:
            return min(0, self.modifiers)
        return self.modifiers + self.die.value

    @property
    def succeeded(self) -> bool | None:
        """Total >= Ease Factor (None with no Ease Factor); a botch fails."""
        if self.ease_factor is None:
            return None
        return not self.die.botched and self.total >= self.ease_factor

    @property
    def margin(self) -> int | None:
        """How far the total beat (or missed) the Ease Factor."""
        return None if self.ease_factor is None else self.total - self.ease_factor


def roll(
    rng: random.Random,
    modifiers: int,
    *,
    ease_factor: int | None = None,
    stress: bool = True,
    botch_dice: int = 1,
    saga: Saga | None = None,
) -> Roll:
    """Roll `modifiers` + a die, against `ease_factor` if given."""
    die = stress_die(rng, botch_dice, saga=saga) if stress else simple_roll(rng)
    return Roll(modifiers=modifiers, die=die, ease_factor=ease_factor)


def botch_chance(botch_dice: int) -> float:
    """The chance a stress roll botches with this many botch dice: the die
    must first show 0 (1 in 10), then at least one botch die a 0."""
    if botch_dice <= 0:
        return 0.0
    return 0.1 * (1 - 0.9**botch_dice)


def ease_factor_label(ease_factor: int) -> str:
    """The book's word for an Ease Factor: the highest band it reaches."""
    label = EASE_FACTORS[0][1]
    for threshold, name in EASE_FACTORS:
        if ease_factor >= threshold:
            label = name
    return label
