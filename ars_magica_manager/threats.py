"""A threat in detail (the core rules, Dies Irae): a story that grows if
it is left alone. It has an antagonist, a way of moving and an ordered
list of stages, each with when it comes, the clues that warn of it, and
what happens if it is ignored, stopped or turned; and the stage it has
reached is worked out from the date.

A threat moves by fixed dates (each stage has its season and year), or
along a track or an omen count (each stage comes at a number, and the
storyguide moves the threat's position). A stage the troupe stopped or
turned no longer comes; one marked as happened has come whatever the
date.

Kept in Neighbour.details: "antagonist", "moves", "position" and
"stages" (each {"title", "year", "season", "at", "clues", "ignored",
"stopped", "turned", "outcome"})."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .character_sheet import Fact
from .commands import SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .models import SEASONS, Neighbour, Saga
from .neighbour_lists import KindList, KindTab, details_list, list_ops
from .sections import STAGES_SECTION

#: How a threat moves from one stage to the next.
MOVES: tuple[str, ...] = ("Fixed dates", "A track", "An omen count")

#: What became of a stage: still to come, come, or kept from coming.
PENDING = "Pending"
OUTCOMES: tuple[str, ...] = (PENDING, "Happened", "Stopped", "Turned")


@dataclass(frozen=True)
class Reached:
    """The stage a threat has reached (None before its first) and the
    next one still to come (None after its last)."""

    current: dict[str, Any] | None
    next: dict[str, Any] | None


# -- the record --


def moves(neighbour: Neighbour) -> str:
    found = neighbour.details.get("moves")
    return found if found in MOVES else MOVES[0]


def by_date(neighbour: Neighbour) -> bool:
    return moves(neighbour) == MOVES[0]


def position(neighbour: Neighbour) -> int:
    return int(neighbour.details.get("position") or 0)


def stages(neighbour: Neighbour) -> list[dict[str, Any]]:
    return details_list(neighbour, "stages")


# -- worked out --


def _when(stage: dict[str, Any]) -> int | None:
    """A dated stage's season, as a number that sorts by date."""
    year = stage.get("year")
    if year is None:
        return None
    season = stage.get("season")
    return year * len(SEASONS) + (SEASONS.index(season) if season in SEASONS else 0)


def _now(saga: Saga) -> int:
    season = saga.current_season
    return saga.current_year * len(SEASONS) + (
        SEASONS.index(season) if season in SEASONS else 0
    )


def has_come(saga: Saga, neighbour: Neighbour, stage: dict[str, Any]) -> bool:
    """Whether `stage` has come: marked as happened, or (still pending)
    its date or its place on the track reached."""
    outcome = stage.get("outcome") or PENDING
    if outcome != PENDING:
        return outcome == "Happened"
    if by_date(neighbour):
        when = _when(stage)
        return when is not None and when <= _now(saga)
    at = stage.get("at")
    return at is not None and at <= position(neighbour)


def reached(saga: Saga, neighbour: Neighbour) -> Reached:
    """The last stage that has come, and the first still to come."""
    current = None
    upcoming = None
    for stage in stages(neighbour):
        if has_come(saga, neighbour, stage):
            current = stage
        elif upcoming is None and (stage.get("outcome") or PENDING) == PENDING:
            upcoming = stage
    return Reached(current, upcoming)


def when_text(neighbour: Neighbour, stage: dict[str, Any]) -> str:
    """ "Winter 1220", or "at 3" on a track; "" when not set."""
    if by_date(neighbour):
        year = stage.get("year")
        if year is None:
            return ""
        season = stage.get("season")
        return f"{season} {year}" if season else str(year)
    at = stage.get("at")
    return "" if at is None else f"at {at}"


def due(saga: Saga, neighbour: Neighbour) -> tuple[int, str] | None:
    """The next dated stage's date (sortable) and "Title, Winter 1220",
    for the Region's Threat due; None if no dated stage is to come."""
    upcoming = reached(saga, neighbour).next
    if upcoming is None or not by_date(neighbour):
        return None
    when = _when(upcoming)
    if when is None:
        return None
    return when, f"{neighbour.name}, {when_text(neighbour, upcoming)}"


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    at = reached(saga, neighbour)
    found = [
        Fact("Antagonist", neighbour.details.get("antagonist", "")),
        Fact("Moves by", moves(neighbour).lower()),
    ]
    if not by_date(neighbour):
        found.append(Fact("Position", str(position(neighbour))))
    found += [
        Fact(
            "Stage reached",
            "none yet" if at.current is None else at.current["title"],
        ),
        Fact(
            "Next",
            "none to come"
            if at.next is None
            else f"{at.next['title']}, {when_text(neighbour, at.next)}".rstrip(", "),
        ),
    ]
    return found


# -- the form --


def fields(_saga: Saga, neighbour: Neighbour | None) -> list[DialogField]:
    """What New Threat and Edit add to the common fields."""
    d = neighbour.details if neighbour is not None else {}
    return [
        DialogField(
            "antagonist",
            "Antagonist",
            "text",
            d.get("antagonist", ""),
            placeholder="e.g. The Hollow Crown",
        ),
        DialogField(
            "moves",
            "Moves by",
            "select",
            d.get("moves", MOVES[0]),
            options=pairs(MOVES),
            required=True,
            hint="Each stage on its date, or at a number on a track or an omen count.",
        ),
        DialogField(
            "position",
            "Position on its track",
            "int",
            d.get("position", 0),
            hint="For a track or an omen count: where it stands now.",
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("position") or 0) < 0:
        return "Its position can't be below 0."
    return None


# -- the stages --


def stages_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Stages ({len(stages(neighbour))})"


def stages_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    """Each stage in order: when it comes, what became of it, and what
    happens if it is ignored. The stage reached is marked."""
    at = reached(saga, neighbour)
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, stage in enumerate(stages(neighbour)):
        outcome = stage.get("outcome") or PENDING
        state = outcome
        if outcome == PENDING:
            state = "Reached" if has_come(saga, neighbour, stage) else "To come"
        if stage is at.current:
            styles[(index, 0)] = "b"
            styles[(index, 2)] = "$text-warning"
        rows.append(
            [
                stage["title"],
                when_text(neighbour, stage),
                state,
                stage.get("ignored", ""),
            ]
        )
    return Grid(
        ["Stage", "When", "Now", "If ignored"],
        rows,
        list(range(len(rows))),
        "No stages yet: add each step the threat takes, in order.",
        styles,
        caps=[24, 12, 9, 0],
        stretch=3,
    )


def stage_fields(
    _saga: Saga, neighbour: Neighbour, stage: dict[str, Any] | None
) -> list[DialogField]:
    s = stage or {}
    found = [
        DialogField("title", "Stage", "text", s.get("title", ""), required=True),
    ]
    if by_date(neighbour):
        found += [
            DialogField("year", "Year", "optint", s.get("year")),
            DialogField(
                "season",
                "Season",
                "select",
                s.get("season") or None,
                options=pairs(SEASONS),
                allow_blank=True,
                placeholder="(any)",
            ),
        ]
    else:
        found.append(
            DialogField(
                "at",
                "Comes at",
                "optint",
                s.get("at"),
                hint="The place on the track, or the omen count, it comes at.",
            )
        )
    found += [
        DialogField("clues", "Clues", "text", s.get("clues", "")),
        DialogField("ignored", "If ignored", "text", s.get("ignored", "")),
        DialogField("stopped", "If stopped", "text", s.get("stopped", "")),
        DialogField("turned", "If turned", "text", s.get("turned", "")),
        DialogField(
            "outcome",
            "What became of it",
            "select",
            s.get("outcome") or PENDING,
            options=pairs(OUTCOMES),
            required=True,
            hint="Pending comes on its date; the others say it came or was "
            "kept from coming.",
        ),
    ]
    return found


def stage_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "stages",
        "Stage",
        stage_fields,
        lambda s: s["title"],
    )


TAB = KindTab(
    "Stages",
    "tab-nb-threat",
    (KindList(STAGES_SECTION, stages_title, stages_grid, stage_ops),),
)
