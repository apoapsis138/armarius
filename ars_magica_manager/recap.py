"""Previously On: a page to read aloud before the next Session, of what
happened since the last one: its chapters, the seasons played since, what
the world did (The World Turns), the threats' stages that came, and each
player character's What changed (what_changed.py).

It runs from the last played Session (the saga's date when it was marked
Played) to now; with no played Session, over the last four seasons. Read
as the Player view (`players`), it leaves out what the players may not
know: the World Turns' lines (they name neighbours the troupe may not
know of), unknown threats, and any non-player character's season.

Pattern: Ahead's pull registry run backwards: each part of the saga
answers "what happened between these two dates?", a list of functions
(Observer, reduced to a list) that `register` adds to."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from . import sessions, threats, viewing, what_changed, world
from .markup import escape
from .models import CHAPTER, SEASONS, Saga, Session, season_order
from .seasons.defaults import is_player_character

TITLE = "Previously On"
#: With no played Session, how many seasons back it looks.
FALLBACK_SEASONS = 4


@dataclass(frozen=True)
class Part:
    """One part of the recap: its heading and its lines (plain text)."""

    heading: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class Span:
    """What the recap covers: from `start` (a season order, inclusive) to
    now, the Session it starts from (None: the fallback), and whether it
    is read as the Player view."""

    start: int
    session: Session | None
    players: bool


Source = Callable[[Saga, Span], Part | None]

SOURCES: list[Source] = []


def register(source: Source) -> Source:
    SOURCES.append(source)
    return source


def _order(season: str, year: int) -> int:
    return season_order(season=season, year=year)


def span(saga: Saga, players: bool = False) -> Span:
    """From the last played Session marked with a date, else the last
    four seasons."""
    for session in sessions.played(saga):
        if session.played_year is not None:
            start = _order(session.played_season or SEASONS[0], session.played_year)
            return Span(start, session, players)
    now = _order(saga.current_season, saga.current_year)
    return Span(now - FALLBACK_SEASONS, None, players)


@register
def _chapters(saga: Saga, within: Span) -> Part | None:
    """The chapters played at the last Session, else those dated since."""
    lines = []
    for covenant in world.player_covenants(saga):
        for entry in covenant.diary:
            if entry.category != CHAPTER:
                continue
            at_session = within.session is not None and (
                entry.session_id == within.session.id
            )
            dated = _order(entry.season, entry.year) >= within.start
            if at_session or (within.session is None and dated):
                went = [
                    c.name for i in entry.cast if (c := saga.character(i)) is not None
                ]
                who = f" ({', '.join(went)})" if went else ""
                lines.append(f"{entry.name}: {entry.details.strip()}{who}")
    return Part("The last Session's chapters", tuple(lines)) if lines else None


@register
def _seasons(saga: Saga, within: Span) -> Part | None:
    """The seasons played since: each player character's line (every
    line, read by the storyguide)."""
    lines = []
    played = {c.id for c in saga.characters if is_player_character(c)}
    for record in saga.season_records:
        if _order(record.season, record.year) < within.start:
            continue
        shown = [
            f"{line.name}: {line.activity or 'nothing planned'}"
            + (f", {line.result}" if line.result else "")
            for line in record.lines
            if not within.players or line.character_id in played
        ]
        if shown:
            lines.append(f"{record.season} {record.year}: " + "; ".join(shown))
    return Part("The seasons since", tuple(lines)) if lines else None


@register
def _world(saga: Saga, within: Span) -> Part | None:
    """What the world did each year (The World Turns): the storyguide's
    only."""
    if within.players:
        return None
    lines = [
        f"{turn.season} {turn.year}: {line}"
        for turn in saga.world_turns
        if _order(turn.season or SEASONS[-1], turn.year) >= within.start
        for line in turn.lines
    ]
    return Part("What the world did", tuple(lines)) if lines else None


@register
def _threats(saga: Saga, within: Span) -> Part | None:
    """The threats' dated stages that came (or were stopped or turned)."""
    lines = []
    for neighbour in saga.neighbours:
        if not threats.is_threat(neighbour):
            continue
        if (within.players and not viewing.is_known(neighbour)) or not (
            viewing.readable(viewing.current(), neighbour, saga)
        ):
            continue
        for stage in threats.stages(neighbour):
            order = threats.stage_order(stage)
            outcome = stage.get("outcome") or threats.PENDING
            if order is None or order < within.start or outcome == threats.PENDING:
                continue
            lines.append(
                f"{neighbour.name}: {stage.get('title', '')} ({outcome.lower()}, "
                f"{stage.get('season', '')} {stage.get('year', '')})"
            )
    return Part("The threats", tuple(lines)) if lines else None


@register
def _changed(saga: Saga, within: Span) -> Part | None:
    """Each player character's What changed since the last Session."""
    if within.session is None or not within.session.kept:
        return None
    lines = []
    for character in saga.characters:
        before = within.session.kept.get(character.id)
        if before is None:
            continue
        changed = what_changed.changes(saga, before, character)
        if changed:
            lines.append(f"{character.name}: {'; '.join(changed)}.")
    return Part("What changed", tuple(lines)) if lines else None


def parts(saga: Saga, players: bool = False) -> list[Part]:
    within = span(saga, players)
    found = (source(saga, within) for source in SOURCES)
    return [part for part in found if part is not None]


def lead(saga: Saga, players: bool = False) -> str:
    within = span(saga, players)
    if within.session is None:
        return f"The last {FALLBACK_SEASONS} seasons, to {saga.current_season} {saga.current_year}."
    return (
        f"Since the Session of {sessions.when(within.session)}, to "
        f"{saga.current_season} {saga.current_year}."
    )


def text(saga: Saga, players: bool = False) -> str:
    """The recap for a window (markup)."""
    found = parts(saga, players)
    lines = [f"[i]{escape(lead(saga, players))}[/]"]
    if not found:
        lines.append("Nothing recorded since.")
    for part in found:
        lines.append(f"\n[b]{escape(part.heading)}[/]")
        lines += [escape(line) for line in part.lines]
    return "\n".join(lines)
