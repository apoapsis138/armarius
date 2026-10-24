"""The Research tab's text: a magus's research goals, every season's work
toward them, and the chosen goal or season in detail.

Markup strings, so both front-ends show the same words: the goal's
stage, steps and odds are worked out here from rules.research, and the
tab only draws them.
"""

from __future__ import annotations

from collections.abc import Sequence

from . import experiment_text
from .markup import escape
from .models import Breakthrough, Character, Laboratory, ResearchAttempt, Saga
from .models.common import SEASONS
from .rules import experiment, research
from .rules.experiment import Extraordinary
from .rules.lab import ability_score, botch_conditions
from .tables import Table

#: The Research Log's columns, as its header shows them.
LOG_HEADER = (
    f"  {'Season':<11} {'Goal':<16} {'Work':<20} {'Die':>3} {'Roll':>4} "
    f"{'Move':>4}  Result"
)

_KINDS = {
    "seek": "Seek",
    "stabilize": "Stabilize",
    "insight": "Insight",
    "invent insight": "Invent",
}


def _clip(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def _when(attempt: ResearchAttempt) -> tuple[int, int]:
    season = SEASONS.index(attempt.season) if attempt.season in SEASONS else 0
    return attempt.year, season


def log_entries(
    character: Character, goals: Sequence[Breakthrough] | None = None
) -> list[tuple[Breakthrough, ResearchAttempt]]:
    """Every season's work toward any goal (or only `goals`), newest
    first."""
    chosen = character.breakthroughs if goals is None else goals
    entries = [(goal, a) for goal in chosen for a in goal.log]
    entries.sort(key=lambda e: _when(e[1]), reverse=True)
    return entries


def landed(attempt: ResearchAttempt) -> int | None:
    """Where the chart roll ended up: the die + risk, moved."""
    roll = attempt.roll
    return None if roll is None else roll + attempt.move


def outcome(attempt: ResearchAttempt) -> str:
    """A season's result in a word or two (markup)."""
    if attempt.zeroes:
        return "[$text-error]Disaster[/]"
    if attempt.kind == "insight":
        return "[$text-success]insight[/]" if attempt.insight else "no insight"
    if attempt.discovery:
        return "[$text-success]Discovery[/]"
    if attempt.points:
        return f"[$text-success]+{attempt.points} pts[/]"
    spot = landed(attempt)
    if spot is None:
        return ""
    band = research.band_of(spot)
    label = SHORT_LABELS.get(band.label, band.label)
    if band.tone == "harm":
        return f"[$text-error]{label}[/]"
    return label


def under_way(saga: Saga, lab: Laboratory) -> list[Breakthrough]:
    """The research the laboratory's owner has under way: their goals
    begun and not yet reached."""
    owner = saga.character(lab.owner_id)
    if owner is None:
        return []
    return [
        goal
        for goal in owner.breakthroughs
        if not goal.reached and research.stage(goal) is not research.Stage.NOT_STARTED
    ]


def log_rows(
    character: Character, goals: Sequence[Breakthrough] | None = None
) -> list[tuple[int | None, str]]:
    """The Research Log's rows, newest first; each row's data is its place
    in log_entries."""
    rows: list[tuple[int | None, str]] = []
    for index, (goal, attempt) in enumerate(log_entries(character, goals)):
        work = f"{_KINDS.get(attempt.kind, attempt.kind)} {attempt.work}".strip()
        die = "" if attempt.die is None else str(attempt.die)
        roll = "" if attempt.roll is None else str(attempt.roll)
        move = f"{attempt.move:+d}" if attempt.move else ""
        rows.append(
            (
                index,
                f"{attempt.season + ' ' + str(attempt.year):<11} "
                f"{escape(_clip(goal.name, 16)):<16} "
                f"{escape(_clip(work, 20)):<20} {die:>3} {roll:>4} {move:>4}  "
                + outcome(attempt),
            )
        )
    return rows


def log_table(
    character: Character, goals: Sequence[Breakthrough] | None = None
) -> Table:
    """The Research Log as a table: the same seasons as log_rows, keyed
    by their place in log_entries."""
    rows = []
    for goal, attempt in log_entries(character, goals):
        rows.append(
            [
                f"{attempt.season} {attempt.year}",
                escape(goal.name),
                escape(f"{_KINDS.get(attempt.kind, attempt.kind)} {attempt.work}"),
                "" if attempt.die is None else str(attempt.die),
                "" if attempt.roll is None else str(attempt.roll),
                f"{attempt.move:+d}" if attempt.move else "",
                outcome(attempt),
            ]
        )
    return Table(
        ["Season", "Goal", "Work", "Die", "Roll", "Move", "Result"],
        rows,
        markup=True,
        stretch=2,
    )


def goal_line(goal: Breakthrough) -> str:
    """A goal's kind, points and stage, under its name on a card."""
    return f"{goal.kind} · {research.target_text(goal)} · {research.stage(goal).value}"


def steps_line(goal: Breakthrough) -> str:
    """The process, step by step, with the goal's own step marked."""
    current = research.step(goal)
    parts = []
    for index, name in enumerate(research.STEPS):
        if index < current or goal.reached and index <= current:
            parts.append(f"[$text-success]✓ {name}[/]")
        elif index == current:
            parts.append(f"[b]▶ {name}[/]")
        else:
            parts.append(f"[dim]· {name}[/]")
    return "  ".join(parts)


#: The chart's bands, shortened for the one-line strip.
SHORT_LABELS = {
    "no effect": "none",
    "side effect": "side",
    "complete failure": "failure",
    "story event": "story",
    "modified effect": "modified",
    "roll twice": "twice",
}


def band_strip(roll: int | None, *, plain: bool = False) -> str:
    """The chart's bands in one line, the roll's own marked; `plain`
    leaves out the colours, for a form's note (plain text)."""
    parts = []
    for band in research.BANDS:
        span = (
            f"{band.low}+"
            if band.high is None
            else str(band.low)
            if band.high == band.low
            else f"{band.low}-{band.high}"
        )
        text = f"{span} {SHORT_LABELS.get(band.label, band.label)}"
        if plain:
            landed = roll is not None and band.holds(max(roll, 0))
            parts.append(f"▸ {text} ◂" if landed else text)
            continue
        if roll is not None and band.holds(max(roll, 0)):
            text = f"[b $text-primary]▸ {text} ◂[/]"
        elif band.tone == "harm":
            text = f"[$text-error]{text}[/]"
        elif band.tone == "discovery":
            text = f"[$text-success]{text}[/]"
        parts.append(text)
    return " · ".join(parts)


def _pct(chance: float) -> str:
    return f"{chance * 100:.1f}%" if 0 < chance < 0.1 else f"{chance * 100:.0f}%"


def odds_lines(saga: Saga, character: Character, goal: Breakthrough) -> list[str]:
    """The chances of the goal's next season at the chart."""
    aura, safety = botch_conditions(saga, character)
    if research.stage(goal) in (
        research.Stage.DISCOVERY,
        research.Stage.STABILIZING,
        research.Stage.RETRY,
    ):
        risk = goal.discovery_risk
        odds = research.stabilizing_odds(
            risk,
            goal.discovery_shift,
            experiment.botch_dice(character, risk, aura, safety),
        )
        return [
            f"[b]Odds of stabilizing[/] (risk +{risk}, move "
            f"{goal.discovery_shift:+d}, aura {aura}): stabilized "
            f"{_pct(odds.success)} · harmful {_pct(odds.harmful)} · "
            f"disaster {_pct(odds.disaster)}",
        ]
    if goal.reached:
        return []
    score, bonus = ability_score(character, "Magic Theory")
    lines = [
        f"[b]Odds of a Discovery[/] by risk (Magic Theory {score + bonus}, "
        f"aura {aura}):"
    ]
    for odds in research.risk_table(
        score + bonus, aura, character=character, safety=safety
    ):
        lines.append(
            f"  +{odds.risk}: Discovery {_pct(odds.success)} · harmful "
            f"{_pct(odds.harmful)} · disaster {_pct(odds.disaster)}"
        )
    return lines


def goal_panel(saga: Saga, character: Character, goal: Breakthrough) -> str:
    """A goal's details: where it stands, step by step, and the odds of its
    next season, then what it grants and what waits on it."""
    from .sheet_text import goal_text

    title, *rest = goal_text(goal).split("\n")
    lines = [title, steps_line(goal), *odds_lines(saga, character, goal), *rest]
    return "\n".join(lines)


def attempt_panel(
    goal: Breakthrough, attempt: ResearchAttempt, *, strip: bool = True
) -> str:
    """One season's work in detail: the roll, where it landed and why;
    with `strip`, the chart's bands as a line of text (a front-end that
    draws the chart leaves it out)."""
    kind = _KINDS.get(attempt.kind, attempt.kind)
    lines = [
        f"[b]{attempt.season} {attempt.year}: {kind}[/] toward {escape(goal.name)}",
    ]
    if attempt.work:
        lines.append(
            f"Work: {escape(attempt.work)}"
            + (f" (magnitude {attempt.magnitude})" if attempt.magnitude else "")
            + (f", Lab Total {attempt.lab_total}" if attempt.lab_total else "")
        )
    if attempt.die is not None:
        roll = attempt.die + attempt.risk
        text = f"Roll: die {attempt.die} + risk {attempt.risk} = {roll}"
        if attempt.move:
            text += f", moved {attempt.move:+d} = {roll + attempt.move}"
        lines.append(text)
        if strip:
            lines += ["", band_strip(roll + attempt.move), ""]
        if attempt.die == 0:
            lines.append(
                f"A 0: {attempt.botch_dice} botch dice, {attempt.zeroes} zero(es)."
            )
    if attempt.result:
        lines.append(escape(attempt.result))
    if attempt.points:
        lines.append(f"Breakthrough points: +{attempt.points}.")
    if attempt.warping:
        lines.append(f"Warping Points: {attempt.warping}.")
    lines += experiment_text.effect_lines(attempt.effects, "Left on the work")
    return "\n".join(lines)


def move_card(
    saga: Saga,
    character: Character,
    goal: str,
    risk: int,
    chart: Extraordinary,
) -> str:
    """Advance Season's question when an experiment's roll can be moved
    onto 10: the roll and where it landed, the chart with it marked, what
    the move gives, and the odds a stabilization at that move then has.
    Plain text: it is a form's note."""
    shift = chart.discovery_shift or 0
    roll = chart.die + risk
    band = research.band_of(roll)
    aura, safety = botch_conditions(saga, character)
    odds = research.stabilizing_odds(
        risk, shift, experiment.botch_dice(character, risk, aura, safety)
    )
    return "\n".join(
        [
            f"{character.name}'s experiment toward {goal}",
            f"Roll: die {chart.die} + risk {risk} = {roll}: {band.label}.",
            band_strip(roll, plain=True),
            f"Moving it {shift:+d} reaches 10: a Discovery as well (within the "
            "risk modifier); the roll's own result stands either way.",
            "The same move is then made every season of this project and when "
            f"stabilizing: at risk +{risk} and move {shift:+d}, a stabilization "
            f"succeeds {_pct(odds.success)} of the time.",
        ]
    )
