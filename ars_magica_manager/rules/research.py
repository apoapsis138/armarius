"""Arcane Discovery as a process: where a goal stands, the odds of an
experiment's chart roll, and the Research log each season adds to.

A goal's stage is worked out from the goal, never stored, so it can't
disagree with the points, Discovery and insights it is read from.

Rules: rules.experiment (Ars Magica Definitive Edition, Chapter 8,
Experimentation and Arcane Discovery).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..models import Breakthrough, ResearchAttempt
from . import experiment

SOURCE = experiment.SOURCE


class Stage(Enum):
    """Where a research goal stands, as its next step names it."""

    NOT_STARTED = "Not started"
    SEEKING = "Seeking a Discovery"
    INSIGHT = "Insight to invent"
    DISCOVERY = "Discovery to stabilize"
    STABILIZING = "Stabilizing"
    RETRY = "Stabilization to retry"
    REACHED = "Breakthrough reached"


#: The steps of the process, in order, as the sheet's step tracker shows
#: them.
STEPS: tuple[str, ...] = (
    "Goal agreed",
    "Seek",
    "Discovery",
    "Stabilize",
    "Breakthrough",
    "Spread",
)


def stage(goal: Breakthrough) -> Stage:
    if goal.reached:
        return Stage.REACHED
    if goal.pending_magnitude:
        if goal.retry_season:
            return Stage.RETRY
        if goal.stabilizing_seasons:
            return Stage.STABILIZING
        return Stage.DISCOVERY
    if goal.insights:
        return Stage.INSIGHT
    if goal.points or goal.log:
        return Stage.SEEKING
    return Stage.NOT_STARTED


def step(goal: Breakthrough) -> int:
    """The index into STEPS of the step the goal is on."""
    return {
        Stage.NOT_STARTED: 1,
        Stage.SEEKING: 1,
        Stage.INSIGHT: 1,
        Stage.DISCOVERY: 3,
        Stage.STABILIZING: 3,
        Stage.RETRY: 3,
        Stage.REACHED: 5,
    }[stage(goal)]


def target_text(goal: Breakthrough) -> str:
    """The goal's points, with its target unless the storyguide keeps it."""
    if goal.hidden_target and not goal.reached:
        return f"{goal.points} points (target kept by the storyguide)"
    return f"{goal.points}/{goal.target} points"


# -- the odds of a chart roll ---------------------------------------------


def stress_values(simple: bool = False, depth: int = 6) -> dict[int, float]:
    """The chance of each value of a stress die that didn't botch (a 0 on
    the first throw is left out: see `zero_chance`). With `simple`, a
    simple die (1-10)."""
    if simple:
        return {v: 0.1 for v in range(1, 11)}
    found: dict[int, float] = {}

    def explode(multiplier: int, chance: float, left: int) -> None:
        # A re-roll after a 1: 2-9 and 0 (as 10) stop; another 1 doubles.
        for face in (2, 3, 4, 5, 6, 7, 8, 9, 10):
            value = face * multiplier
            found[value] = found.get(value, 0.0) + chance * 0.1
        if left:
            explode(multiplier * 2, chance * 0.1, left - 1)

    for face in range(2, 10):
        found[face] = found.get(face, 0.0) + 0.1
    explode(2, 0.1, depth)
    return found


def zero_chance(simple: bool = False) -> float:
    """The chance a stress die's first throw is 0."""
    return 0.0 if simple else 0.1


@dataclass(frozen=True)
class Odds:
    """A season's chances on the Extraordinary Results chart: a Discovery
    (seeking) or a stabilization (stabilizing), a harmful result (No
    Benefit or Complete Failure), and a Disaster."""

    risk: int
    botch_dice: int
    success: float
    harmful: float
    disaster: float


def seeking_odds(risk: int, botch_dice: int, *, simple: bool = False) -> Odds:
    """Seeking a Discovery: a roll (die + risk) within the risk of 10 can be
    moved there, unless the roll itself wastes the season (8)."""
    values = stress_values(simple)
    success = sum(
        p for v, p in values.items() if abs(v + risk - 10) <= risk and v + risk != 8
    )
    zero = zero_chance(simple)
    disaster = zero * (1 - 0.9 ** max(botch_dice, 0))
    # A die of 0 that doesn't botch reads 0 + risk.
    landed = dict(values)
    landed[0] = landed.get(0, 0.0) + zero - disaster
    harmful = sum(p for v, p in landed.items() if v + risk in (7, 8))
    return Odds(risk, botch_dice, success, harmful, disaster)


def stabilizing_odds(
    risk: int, move: int, botch_dice: int, *, simple: bool = False
) -> Odds:
    """Stabilizing: the roll (die + risk), moved as before, must not land
    on a harmful result."""
    values = stress_values(simple)
    zero = zero_chance(simple)
    disaster = zero * (1 - 0.9 ** max(botch_dice, 0))
    landed = dict(values)
    landed[0] = landed.get(0, 0.0) + zero - disaster
    harmful = sum(p for v, p in landed.items() if v + risk + move in (7, 8))
    return Odds(risk, botch_dice, 1 - harmful - disaster, harmful, disaster)


def risk_table(magic_theory: int, aura: int, *, simple: bool = False) -> list[Odds]:
    """Seeking a Discovery's odds at each risk Magic Theory allows."""
    return [
        seeking_odds(risk, 1 + risk + max(0, aura), simple=simple)
        for risk in range(1, experiment.max_risk(magic_theory) + 1)
    ]


# -- the chart, as bands --------------------------------------------------


@dataclass(frozen=True)
class Band:
    """A stretch of the chart: its lowest and highest roll (None: no top)
    and what it gives."""

    low: int
    high: int | None
    label: str
    #: "none", "side", "harm", "story", "discovery", "modified", "twice".
    tone: str

    def holds(self, roll: int) -> bool:
        return roll >= self.low and (self.high is None or roll <= self.high)


BANDS: tuple[Band, ...] = (
    Band(0, 4, "no effect", "none"),
    Band(5, 6, "side effect", "side"),
    Band(7, 7, "no benefit", "harm"),
    Band(8, 8, "complete failure", "harm"),
    Band(9, 9, "story event", "story"),
    Band(10, 10, "Discovery", "discovery"),
    Band(11, 11, "modified effect", "modified"),
    Band(12, None, "roll twice", "twice"),
)


def band_of(roll: int) -> Band:
    return next(b for b in BANDS if b.holds(max(roll, 0)))


# -- the Research log -----------------------------------------------------


def record(goal: Breakthrough, attempt: ResearchAttempt) -> None:
    goal.log.append(attempt)
