"""The Grogs Aging Chart: an older grog's pre-play aging taken a decade
at a time, instead of one aging roll a year.

- The chart gives the Aging Points (and crises) expected in a decade at
  each Aging Score, for mild, average and harsh aging. The Aging Score is
  the Aging Total without the stress die: age / 10 (rounded up) - Living
  Conditions - the Longevity Ritual's modifier. A decade spent partly at
  one score and partly at another uses the higher; a part of a decade
  takes that share of the chart's numbers, rounded up.
- Apparent age: a simple die for each decade; at or under the decade's
  Aging Points it advances the whole decade, otherwise by the die.
- Crises are the storyguide's choice. Taken, they give a Decrepitude score
  of the number of crises (with the points that score needs) and the
  chart's points divided by one more than the crises, rounded up.
- The chart's points (not a crisis's) fall about as the Aging table
  spreads them: just under half on any Characteristic, of the rest about
  half on Quickness or Stamina, 30 percent on Perception or Presence, 15
  percent on Strength or Dexterity and the remainder on Intelligence or
  Communication.
- Harsh aging may let a new character start with Abilities 1 higher than
  the age cap, mild aging 1 lower; Mild Aging requires mild aging, Poor
  Living Conditions harsh.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Literal

from ..models import Character, Saga
from . import aging, dice, effects, sites
from .rounding import round_up
from .scores import character_source

SOURCE = (
    "Grogs, Chapter 5: Creating & Maintaining Grogs, Aging, the Easy Way, "
    "pp. 65-66 (https://www.redcap.org/page/Grogs_Chapter_Five:_Creating_"
    "%26_Maintaining_Grogs#Aging.2C_the_Easy_Way)"
)

Kind = Literal["mild", "average", "harsh"]
KINDS: tuple[Kind, ...] = ("mild", "average", "harsh")
YEARS_A_DECADE = 10

#: The Aging Chart: Aging Score -> (Aging Points, crises) a decade, for
#: mild, average and harsh aging. The points leave out a crisis's own.
CHART: dict[int, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = {
    1: ((1, 0), (2, 0), (3, 0)),
    2: ((2, 0), (3, 0), (4, 0)),
    3: ((3, 0), (4, 0), (5, 0)),
    4: ((3, 0), (4, 1), (5, 2)),
    5: ((4, 1), (5, 1), (6, 2)),
    6: ((5, 1), (6, 1), (7, 2)),
    7: ((6, 1), (7, 1), (8, 2)),
    8: ((7, 1), (8, 1), (9, 2)),
    9: ((7, 1), (9, 1), (10, 2)),
    10: ((9, 1), (11, 1), (12, 2)),
}
LOWEST_SCORE = min(CHART)
HIGHEST_SCORE = max(CHART)

#: What each kind of aging does to the Ability cap at creation.
CAP_CHANGE: dict[str, int] = {"mild": -1, "average": 0, "harsh": 1}
#: The Virtues and Flaws that require one kind of aging.
REQUIRED: dict[str, Kind] = {
    "vf_mild_aging": "mild",
    "vf_poor_living_conditions": "harsh",
}

#: How the chart's points fall on the Characteristics, in 400ths:
#: just under half (45%) on any, then of the other 55%, half on
#: Quickness or Stamina, 30% Perception or Presence, 15% Strength or
#: Dexterity, the remainder (5%) Intelligence or Communication.
ANY = "any"
SHARES: tuple[tuple[str, tuple[str, ...], int], ...] = (
    (ANY, (), 180),
    ("quickness or stamina", ("quickness", "stamina"), 110),
    ("perception or presence", ("perception", "presence"), 66),
    ("strength or dexterity", ("strength", "dexterity"), 33),
    ("intelligence or communication", ("intelligence", "communication"), 11),
)
_WHOLE = sum(share for _, _, share in SHARES)


def chart(score: int, kind: Kind) -> tuple[int, int]:
    """The chart's (Aging Points, crises) for a decade at `score`; a score
    off the chart reads its nearest row."""
    row = CHART[max(LOWEST_SCORE, min(score, HIGHEST_SCORE))]
    return row[KINDS.index(kind)]


def kinds_allowed(character: Character) -> tuple[Kind, ...]:
    """The kinds of aging the character may take: only the one a Virtue or
    Flaw requires, or any."""
    required = {
        REQUIRED[vf.vf_id] for vf in character.virtues_flaws if vf.vf_id in REQUIRED
    }
    return tuple(k for k in KINDS if k in required) or KINDS


def aging_score(
    character: Character, age: int, living: int, saga: Saga | None = None
) -> int:
    """The Aging Total without its stress die at `age`, for base Living
    Conditions `living`: age / 10 (rounded up) - Living Conditions (with
    the character's Virtues) - the Longevity Ritual, plus the Virtues and
    places that change aging rolls."""
    found = effects.collect([character_source(character.virtues_flaws)], "aging_roll")
    if saga is not None:
        found += sites.character_effects(saga, character, "aging_roll")
    return (
        round_up(age / 10)
        - aging.living_conditions(character, living)
        - character.aging.longevity_modifier
        + int(effects.amount_total(found))
    )


@dataclass(frozen=True)
class Decade:
    """A decade (or the part of one) of aging: the ages it covers, its
    Aging Score and what the chart gives for it."""

    first: int
    last: int
    score: int
    points: int
    crises: int

    @property
    def years(self) -> int:
        return self.last - self.first + 1


def decades(
    first: int, end: int, score_at: Callable[[int], int], kind: Kind
) -> list[Decade]:
    """The decades from age `first` up to (not including) `end`, ten years
    each from `first` (the last may be shorter), each at its highest Aging
    Score; a shorter one takes its share of the chart, rounded up."""
    found = []
    for start in range(first, end, YEARS_A_DECADE):
        last = min(start + YEARS_A_DECADE, end) - 1
        score = max(score_at(age) for age in range(start, last + 1))
        points, crises = chart(score, kind)
        years = last - start + 1
        found.append(
            Decade(
                start,
                last,
                score,
                round_up(points * years / YEARS_A_DECADE),
                round_up(crises * years / YEARS_A_DECADE),
            )
        )
    return found


@dataclass(frozen=True)
class ChartTotal:
    """What the chart gives over every decade: the chart's own points
    after any crises, the crises taken, and the points those crises add to
    reach their Decrepitude score."""

    chart_points: int
    crises: int
    crisis_points: int
    decrepitude: int

    @property
    def points(self) -> int:
        return self.chart_points + self.crisis_points


def total(
    found: Sequence[Decade], decrepitude_points: int, take_crises: bool
) -> ChartTotal:
    """The Aging Points the decades give a character who has
    `decrepitude_points` already. Without crises, the chart's points. With
    them, the Decrepitude score rises by one a crisis (the points that
    score needs), plus the chart's points divided by one more than the
    crises, rounded up."""
    points = sum(d.points for d in found)
    before = aging.decrepitude_score(decrepitude_points)
    crises = sum(d.crises for d in found) if take_crises else 0
    if not crises:
        return ChartTotal(points, 0, 0, before)
    score = min(before + crises, len(aging.DECREPITUDE_POINTS) - 1)
    reach = max(0, aging.points_for_score(score) - decrepitude_points)
    return ChartTotal(round_up(points / (crises + 1)), crises, reach, score)


def shares(points: int) -> list[tuple[str, tuple[str, ...], int]]:
    """The chart's `points` split by SHARES: (group, its Characteristics,
    points). Each point in turn goes to the group furthest below its share
    of the points so far (a tie to the larger share), so one more point
    never takes a point from another group."""
    given = [0] * len(SHARES)
    for k in range(1, points + 1):
        behind = [
            share * k - given[i] * _WHOLE for i, (_, _, share) in enumerate(SHARES)
        ]
        given[behind.index(max(behind))] += 1
    return [(name, chars, n) for (name, chars, _), n in zip(SHARES, given, strict=True)]


def placements(points: int, crisis_points: int, scores: dict[str, int]) -> list[str]:
    """Which Characteristic each Aging Point goes to, in order: a crisis's
    spread over the Characteristics highest first (as a yearly roll's), then
    each pair's points alternating between its two (the first named
    first), then the points on any Characteristic ("any": the highest at
    the time, as the yearly roll takes)."""
    order = sorted(aging.CHARACTERISTICS, key=lambda c: -scores[c])
    placed = [order[i % len(order)] for i in range(crisis_points)]
    any_points = 0
    for name, chars, n in shares(points):
        if name == ANY:
            any_points = n
        else:
            placed += [chars[i % len(chars)] for i in range(n)]
    return placed + [ANY] * any_points


@dataclass
class Applied:
    """The points placed: each Characteristic's Aging Points gained, and
    the notes of the Characteristics that fell."""

    gained: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def place_points(
    placed: Sequence[str],
    scores: dict[str, int],
    aging_points: dict[str, int],
    unaging: bool,
) -> Applied:
    """Put each point of `placed` on its Characteristic, changing `scores`
    and `aging_points`: a Characteristic with more Aging Points than its
    score (ignoring the sign) falls by 1 and starts again (never when
    unaging)."""
    applied = Applied()
    for where in placed:
        name = (
            max(aging.CHARACTERISTICS, key=lambda c: scores[c])
            if where == ANY
            else where
        )
        applied.gained[name] = applied.gained.get(name, 0) + 1
        aging_points[name] = aging_points.get(name, 0) + 1
        if aging_points[name] > abs(scores[name]) and not unaging:
            scores[name] -= 1
            aging_points[name] = 0
            applied.notes.append(f"{name.title()} falls to {scores[name]:+d}.")
    return applied


def apparent_years(decade: Decade, die: int) -> int:
    """How far a decade moves the apparent age, for a simple die `die`: the
    whole decade at or under its Aging Points, otherwise the die's years
    (a shorter decade's share, rounded up)."""
    if die <= decade.points:
        return decade.years
    return min(decade.years, round_up(die * decade.years / YEARS_A_DECADE))


def roll_apparent(found: Sequence[Decade], rng: random.Random) -> list[tuple[int, int]]:
    """Each decade's (die, years the apparent age moves)."""
    rolled = []
    for decade in found:
        die = dice.simple_die(rng)
        rolled.append((die, apparent_years(decade, die)))
    return rolled


def decade_text(decade: Decade) -> str:
    crises = f", {decade.crises} crisis" if decade.crises == 1 else ""
    if decade.crises > 1:
        crises = f", {decade.crises} crises"
    return (
        f"Ages {decade.first}-{decade.last} ({decade.years} years) at Aging "
        f"Score {decade.score}: {decade.points} Aging Point(s){crises}"
    )


def cap_change(character: Character) -> int:
    """How far the chart's harsh or mild aging moved the Ability cap at
    creation (0 when the chart wasn't used, or the cap left alone)."""
    return character.creation_conditions.aging_chart_cap
