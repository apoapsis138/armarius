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

A threat moving by dates can be delayed (or hastened) by a number of
seasons held on the threat, which moves every stage still to come
without editing each one: the dates typed stay as they are. One moving
along a track can be tied to a place's trigger (place_events), whose
answer each time it comes moves the threat on or leaves it.

Either way its clock shows how far it has come: a segment for each
stage of a dated threat, filled as each comes, or one for each step of
a track up to its last stage, filled to its position.

A threat can be dormant: a story the storyguide hasn't begun (one left
unticked when its pack was imported). It has reached no stage, nothing
of it comes due, and Begin This Story starts it, its first stage due
next season at the soonest.

Kept in Neighbour.details: "antagonist", "moves", "position",
"delay" (seasons), "dormant", "diary" (as a place's) and "stages" (each {"title", "year", "season", "at", "clues",
"ignored", "stopped", "turned", "outcome"})."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Required, TypedDict, cast

from . import diaries, viewing, world
from .commands import Confirm, Form, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    CHAPTER,
    SEASONS,
    CovenantDiaryEntry,
    Neighbour,
    Saga,
    details_list,
    season_order,
)
from .neighbour_lists import KindList, KindTab, list_ops
from .references import Fact
from .sections import STAGES_SECTION

#: The neighbour kind, and the mark of a threat not yet begun.
THREAT = "threat"
DORMANT = "dormant"

#: How a threat moves from one stage to the next.
MOVES: tuple[str, ...] = ("Fixed dates", "A track", "An omen count")

#: What became of a stage: still to come, come, or kept from coming.
PENDING = "Pending"
OUTCOMES: tuple[str, ...] = (PENDING, "Happened", "Stopped", "Turned")


@dataclass(frozen=True)
class Reached:
    """The stage a threat has reached (None before its first) and the
    next one still to come (None after its last)."""

    current: Stage | None
    next: Stage | None


# -- the record --


def moves(neighbour: Neighbour) -> str:
    found = neighbour.details.get("moves")
    return found if found in MOVES else MOVES[0]


def by_date(neighbour: Neighbour) -> bool:
    return moves(neighbour) == MOVES[0]


def is_threat(record: object) -> bool:
    return isinstance(record, Neighbour) and record.kind == THREAT


def is_dormant(record: object) -> bool:
    """A threat not yet begun."""
    return (
        isinstance(record, Neighbour)
        and record.kind == THREAT
        and bool(record.details.get(DORMANT))
    )


def counts(saga: Saga) -> tuple[int, int]:
    """How many of the saga's threats are under way, and how many
    dormant."""
    found = [n for n in saga.neighbours if is_threat(n)]
    dormant = sum(1 for n in found if is_dormant(n))
    return len(found) - dormant, dormant


def stories_text(saga: Saga) -> str:
    """ "3 under way, 2 dormant": the Tribunal sheet's Stories."""
    active, dormant = counts(saga)
    return f"{active} under way, {dormant} dormant"


def begin(saga: Saga, neighbour: Neighbour) -> None:
    """Begin a dormant threat: dated stages move later together, so the
    first still to come is due next season at the soonest; a track or
    omen count starts where it stands."""
    neighbour.details.pop(DORMANT, None)
    if not by_date(neighbour):
        return
    pending = [
        when
        for s in stages(neighbour)
        if (s.get("outcome") or PENDING) == PENDING
        and (when := stage_when(neighbour, s)) is not None
    ]
    if not pending:
        return
    shift = max(0, _now(saga) + 1 - min(pending))
    if not shift:
        return
    for stage in stages(neighbour):
        when = stage_order(stage)
        if when is None:
            continue
        year, index = divmod(when + shift, len(SEASONS))
        if stage.get("season") in SEASONS:
            stage["year"], stage["season"] = year, SEASONS[index]
        else:
            # A stage dated by its year alone comes at the year's start.
            stage["year"] = year + (1 if index else 0)


def begin_command(saga: Saga, neighbour: Neighbour) -> Confirm:
    """More's Begin This Story on a dormant threat."""

    def apply() -> list[str]:
        begin(saga, neighbour)
        upcoming = reached(saga, neighbour).next
        line = f"{neighbour.name} has begun."
        if upcoming is not None and (when := when_text(neighbour, upcoming)):
            line = f"{neighbour.name} has begun: {upcoming['title']} comes {when}."
        return notes(escape(line))

    return Confirm(
        f"Begin {escape(neighbour.name)}? Its stages start to come: a dated "
        "first stage already past moves to next season, and the rest move "
        "with it.",
        apply,
        yes_label="Begin",
        title="Begin This Story",
    )


DELAY_TITLE = "Delay or Hasten"


def delay_form(saga: Saga, neighbour: Neighbour) -> Form:
    """More's Delay or Hasten on a threat under way: something the troupe
    did (or failed to do) pushes it later or brings it sooner. A dated
    threat's stages still to come move by the seasons given; a track's
    position moves back or on by the steps given. The reason goes into
    the threat's Diary."""
    dated = by_date(neighbour)
    unit = "Seasons" if dated else "Steps"

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "_now",
                "",
                "info",
                f"Delayed {delay_text(delay(neighbour))} so far."
                if dated and delay(neighbour)
                else f"At {position(neighbour)} on its track."
                if not dated
                else "Not delayed so far.",
            ),
            DialogField(
                "by",
                f"{unit} later" if dated else f"{unit} back",
                "int",
                1,
                required=True,
                hint="Every stage still to come moves this many seasons later "
                "(below 0: sooner)."
                if dated
                else "The threat moves back this many steps (below 0: on).",
            ),
            DialogField(
                "reason",
                "Why",
                "text",
                "",
                required=True,
                placeholder="e.g. the bridge was burned",
            ),
        ]

    def problem(values: dict[str, Any]) -> str | None:
        if not values.get("by"):
            return f"Say how many {unit.lower()} it moves."
        if not dated and position(neighbour) - (values.get("by") or 0) < 0:
            return "Its position can't go below 0."
        return None

    def apply(values: dict[str, Any]) -> list[str]:
        line = move(saga, neighbour, int(values["by"]), values["reason"].strip())
        return notes(escape(line))

    return Form(
        DELAY_TITLE,
        fields,
        apply,
        validate=problem,
        save_label="Apply",
        help_id="threat-delay",
    )


def move(saga: Saga, neighbour: Neighbour, by: int, reason: str) -> str:
    """Push a threat later by `by` (seasons on its dates, or steps back on
    its track; below 0 sooner, or on), with a line in its Diary saying
    why. Returns the line."""
    if by_date(neighbour):
        neighbour.details["delay"] = delay(neighbour) + by
        count = abs(by)
        what = f"{'Delayed' if by > 0 else 'Hastened'} {count} season" + (
            "" if count == 1 else "s"
        )
    else:
        before = position(neighbour)
        neighbour.details["position"] = before - by
        what = f"Moved {'back' if by > 0 else 'on'} from {before} to {before - by}"
    text = f"{what}: {reason}" if reason else what
    diaries.write(
        saga.current_year,
        saga.current_season,
        neighbour.name,
        text,
        neighbours=[neighbour],
    )
    return f"{neighbour.name}: {text}."


def position(neighbour: Neighbour) -> int:
    return int(neighbour.details.get("position") or 0)


def delay(neighbour: Neighbour) -> int:
    """The seasons a dated threat's stages still to come are pushed later
    (below 0: brought sooner)."""
    return int(neighbour.details.get("delay") or 0)


def tied(neighbour: Neighbour) -> bool:
    """Whether a place's trigger can move the threat: one moving along a
    track or an omen count."""
    return is_threat(neighbour) and not by_date(neighbour)


class Stage(TypedDict, total=False):
    """A stage of a threat's plan: its title, the clues it leaves, what
    happens if it is ignored, stopped or turned, how it came out, and
    when it comes (a date, or the threat's position it is reached at).
    `chapter` is the form's word on what the troupe did, written as a
    chapter and never kept on the stage."""

    title: Required[str]
    clues: str
    ignored: str
    stopped: str
    turned: str
    outcome: str
    year: int | None
    season: str
    at: int | None
    chapter: str


def stages(neighbour: Neighbour) -> list[Stage]:
    return cast(list[Stage], details_list(neighbour, "stages"))


# -- worked out --


def stage_order(stage: Stage) -> int | None:
    """A dated stage's season, as a number that sorts by date."""
    year = stage.get("year")
    if year is None:
        return None
    return season_order(season=stage.get("season"), year=year)


def stage_when(neighbour: Neighbour, stage: Stage) -> int | None:
    """When a dated stage comes, its threat's delay counted: a stage
    still to come moves with the delay, one already settled stays."""
    when = stage_order(stage)
    if when is None or (stage.get("outcome") or PENDING) != PENDING:
        return when
    return when + delay(neighbour)


def comes(neighbour: Neighbour, stage: Stage) -> int | None:
    """The season a dated stage comes, as a number that sorts by date:
    stage_when, with a stage given only a year coming in its Winter
    unless the delay has moved it."""
    when = stage_when(neighbour, stage)
    if when is None or delay(neighbour):
        return when
    season = stage.get("season") or SEASONS[-1]
    return season_order(season=season, year=when // len(SEASONS))


def _now(saga: Saga) -> int:
    return season_order(season=saga.current_season, year=saga.current_year)


def has_come(saga: Saga, neighbour: Neighbour, stage: Stage) -> bool:
    """Whether `stage` has come: marked as happened, or (still pending)
    its date or its place on the track reached."""
    outcome = stage.get("outcome") or PENDING
    if outcome != PENDING:
        return outcome == "Happened"
    if is_dormant(neighbour):
        return False
    if by_date(neighbour):
        when = stage_when(neighbour, stage)
        return when is not None and when <= _now(saga)
    at = stage.get("at")
    return at is not None and at <= position(neighbour)


def reached(saga: Saga, neighbour: Neighbour) -> Reached:
    """The last stage that has come, and the first still to come; none
    of either while it is dormant."""
    if is_dormant(neighbour):
        return Reached(None, None)
    current = None
    upcoming = None
    for stage in stages(neighbour):
        if has_come(saga, neighbour, stage):
            current = stage
        elif upcoming is None and (stage.get("outcome") or PENDING) == PENDING:
            upcoming = stage
    return Reached(current, upcoming)


def when_text(neighbour: Neighbour, stage: Stage) -> str:
    """ "Winter 1220", or "at 3" on a track; "" when not set."""
    if by_date(neighbour):
        year = stage.get("year")
        if year is None:
            return ""
        when = stage_when(neighbour, stage)
        if when is not None and when != stage_order(stage):
            year, index = divmod(when, len(SEASONS))
            return f"{SEASONS[index]} {year}"
        season = stage.get("season")
        return f"{season} {year}" if season else str(year)
    at = stage.get("at")
    return "" if at is None else f"at {at}"


def due(saga: Saga, neighbour: Neighbour) -> tuple[int, str] | None:
    """The next dated stage's date (sortable) and "Title, Winter 1220",
    for the Region's Threat due; None if no dated stage is to come, and
    for the players, who never see what is still to come."""
    if not viewing.storyguide_reads(neighbour):
        return None
    upcoming = reached(saga, neighbour).next
    if upcoming is None or not by_date(neighbour):
        return None
    when = stage_when(neighbour, upcoming)
    if when is None:
        return None
    return when, f"{neighbour.name}, {when_text(neighbour, upcoming)}"


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    at = reached(saga, neighbour)
    if not viewing.storyguide_reads(neighbour):
        # The players learn of a threat's stages as they come, never of
        # its clock or what is still to come (viewing.py).
        return [
            Fact(
                "Stage reached",
                "none yet" if at.current is None else at.current["title"],
            )
        ]
    found = [
        Fact("Antagonist", neighbour.details.get("antagonist", "")),
        Fact("Moves by", moves(neighbour).lower()),
    ]
    if is_dormant(neighbour):
        return [*found, Fact("Dormant", "not begun: More, Begin This Story")]
    if not by_date(neighbour):
        found.append(Fact("Position", str(position(neighbour))))
    elif delay(neighbour):
        found.append(Fact("Delayed", delay_text(delay(neighbour))))
    if words := clock_text(saga, neighbour):
        found.append(Fact("Clock", words))
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


def delay_text(seasons: int) -> str:
    """ "2 seasons later", "1 season sooner"."""
    count = abs(seasons)
    return f"{count} season{'' if count == 1 else 's'} " + (
        "later" if seasons > 0 else "sooner"
    )


#: A clock's segments, filled and empty.
FILLED, EMPTY = "■", "□"


def clock(saga: Saga, neighbour: Neighbour) -> tuple[int, int] | None:
    """How far the threat has come, as (filled, segments): a dated
    threat's stages come, or a track's position up to its last stage.
    None while it is dormant or has nothing to count, and for the
    players, who never see a threat's clock (viewing.py)."""
    if is_dormant(neighbour) or not viewing.storyguide_reads(neighbour):
        return None
    every = stages(neighbour)
    if by_date(neighbour):
        total = len(every)
        filled = sum(1 for s in every if has_come(saga, neighbour, s))
    else:
        total = max((s.get("at") or 0 for s in every), default=0)
        filled = min(max(position(neighbour), 0), total)
    if total <= 0:
        return None
    return filled, total


def clock_squares(saga: Saga, neighbour: Neighbour) -> str:
    """ "■■□□", the clock alone, for a line with little room
    (Ahead); "" with no clock."""
    found = clock(saga, neighbour)
    if found is None:
        return ""
    filled, total = found
    return FILLED * filled + EMPTY * (total - filled)


def clock_text(saga: Saga, neighbour: Neighbour) -> str:
    """ "■■□□ 2 of 4"; "" with no clock."""
    found = clock(saga, neighbour)
    if found is None:
        return ""
    filled, total = found
    return f"{FILLED * filled}{EMPTY * (total - filled)} {filled} of {total}"


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
        DialogField(
            "delay",
            "Delayed by (seasons)",
            "int",
            d.get("delay", 0),
            hint="For fixed dates: how many seasons later every stage still to "
            "come arrives (below 0: sooner). The dates typed stay as they are.",
            show_if=lambda v: v.get("moves") == MOVES[0],
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("position") or 0) < 0:
        return "Its position can't be below 0."
    return None


# -- the stages --


def shows_stage(saga: Saga, neighbour: Neighbour, stage: Stage) -> bool:
    """Whether whoever is looking may read `stage`: the storyguide any; the
    players one once it has come or been marked (viewing.py)."""
    return viewing.storyguide_reads(neighbour) or (
        (stage.get("outcome") or PENDING) != PENDING or has_come(saga, neighbour, stage)
    )


def stages_title(saga: Saga, neighbour: Neighbour) -> str:
    shown = [s for s in stages(neighbour) if shows_stage(saga, neighbour, s)]
    return f"Stages ({len(shown)})"


def state_text(saga: Saga, neighbour: Neighbour, stage: Stage) -> str:
    """What became of `stage`: its outcome, or for one still pending
    whether it has been reached."""
    outcome = stage.get("outcome") or PENDING
    if outcome != PENDING:
        return outcome
    return "Reached" if has_come(saga, neighbour, stage) else "To come"


def stages_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    """Each stage in order: when it comes, what became of it, and what
    happens if it is ignored. The stage reached is marked."""
    at = reached(saga, neighbour)
    rows = []
    indices: list[int | None] = []
    styles: dict[tuple[int, int], str] = {}
    for index, stage in enumerate(stages(neighbour)):
        if not shows_stage(saga, neighbour, stage):
            continue
        indices.append(index)
        index = len(rows)
        if stage is at.current:
            styles[(index, 0)] = "b"
            styles[(index, 2)] = "$text-warning"
        rows.append(
            [
                stage["title"],
                when_text(neighbour, stage),
                state_text(saga, neighbour, stage),
                stage.get("ignored", ""),
            ]
        )
    return Grid(
        ["Stage", "When", "Now", "If ignored"],
        rows,
        indices,
        "No stages yet: add each step the threat takes, in order.",
        styles,
        caps=[24, 12, 9, 0],
        stretch=3,
    )


#: A stage's words, by key, as the inspector titles them.
STAGE_WORDS: tuple[tuple[str, str], ...] = (
    ("clues", "Clues"),
    ("ignored", "If ignored"),
    ("stopped", "If stopped"),
    ("turned", "If turned"),
)


def stage_text(saga: Saga, neighbour: Neighbour, index: int) -> str:
    """The stage at `index` in full, for the desktop's inspector: when it
    comes and what became of it, then its clues and what happens if it
    is ignored, stopped or turned, each it has; "" for no such stage."""
    every = stages(neighbour)
    if not 0 <= index < len(every):
        return ""
    stage = every[index]
    lines = [
        f"[$label]When:[/] {escape(when_text(neighbour, stage) or 'not set')}",
        f"[$label]Now:[/] {escape(state_text(saga, neighbour, stage))}",
    ]
    lines += [
        f"[$label]{title}:[/] {escape(words)}"
        for key, title in STAGE_WORDS
        if (words := (stage.get(key) or "").strip())
    ]
    return "\n".join(lines)


def stage_fields(
    _saga: Saga, neighbour: Neighbour, stage: Stage | None
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
        DialogField(
            "chapter",
            "What the troupe did",
            "area",
            "",
            hint="Optional: written in its Diary and the troupe's as a chapter "
            "of the tale.",
        ),
    ]
    return found


#: What a stage's outcome makes of it: the field saying what follows.
CONSEQUENCES: dict[str, str] = {
    "Happened": "ignored",
    "Stopped": "stopped",
    "Turned": "turned",
}


def stage_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    before = {id(s): s.get("outcome") or PENDING for s in stages(neighbour)}

    def after() -> None:
        for stage in stages(neighbour):
            words = (stage.pop("chapter", "") or "").strip()
            if words:
                write_chapter(
                    saga,
                    neighbour,
                    saga.current_year,
                    saga.current_season,
                    f"{stage['title']}: {words}",
                )
            outcome = stage.get("outcome") or PENDING
            if outcome != PENDING and before.get(id(stage), PENDING) == PENDING:
                record_outcome(saga, neighbour, stage)

    return list_ops(
        saga,
        neighbour,
        "stages",
        "Stage",
        stage_fields,
        lambda s: s["title"],
        after=after,
    )


def record_outcome(saga: Saga, neighbour: Neighbour, stage: Stage) -> str:
    """What a stage marked as come (or kept from coming) does: its
    consequence, as the stage says it, written in the threat's Diary and
    each troupe covenant's, so the troupe sees what follows. Returns it."""
    outcome = stage.get("outcome") or PENDING
    key = CONSEQUENCES.get(outcome)
    words = str(stage.get(key) or "").strip() if key else ""
    if not words:
        return ""
    text = f"{stage['title']} ({outcome.lower()}): {words}"
    diaries.write(
        saga.current_year,
        saga.current_season,
        neighbour.name,
        text,
        covenants=world.player_covenants(saga),
        neighbours=[neighbour],
    )
    return text


def write_chapter(
    saga: Saga, neighbour: Neighbour, year: int, season: str, words: str
) -> None:
    """A chapter of the threat's tale, what the troupe did: in its Diary,
    marked a chapter, and each troupe covenant's as a Chapter naming it."""
    details_list(neighbour, "diary").append(
        {"year": year, "season": season, "text": words, "chapter": True}
    )
    for covenant in world.player_covenants(saga):
        covenant.diary.append(
            CovenantDiaryEntry(
                year,
                season,
                neighbour.name,
                words,
                category=CHAPTER,
                threat_id=neighbour.id,
            )
        )


TAB = KindTab(
    "Stages",
    "tab-nb-threat",
    (KindList(STAGES_SECTION, stages_title, stages_grid, stage_ops, stage_text),),
)
