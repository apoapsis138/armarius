"""Ahead: what is coming in the next seasons, asked of every part of
the saga rather than kept as a list.

Each source is a function that returns its upcoming entries between two
seasons; Ahead calls them all and sorts the answers by season. The
Tribunals give their next meetings, the seasons notice of a case is
due and the terms of their rulings ending; the towns their fairs; the places their dated triggers; the threats
their dated stages; the characters the year their aging rolls begin and
the season they come back from Twilight; each Winter the world turns
(the yearly step); and the storyguide's own entries (Saga.calendar)
come once, each year, or every so many years.

How far it looks is the saga's ahead_span: a number of years, or to the
next Tribunal (0).

Pattern: Observer, reduced to a list of functions (SOURCES) that each
answer the same question; register() adds one."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass

from . import place_events, threats, tribunal_terms
from .grids import Grid
from .markup import escape
from .models import (
    EVERY,
    FULL,
    SEASONS,
    YEARLY,
    CalendarEntry,
    Covenant,
    Saga,
    season_order,
)
from .references import Fact
from .rules import aging
from .sheets import tribunal as tribunal_sheet

#: How each source is shown in the filter, in order.
EVERYTHING = "Everything"
TRIBUNAL = "Tribunal"
NEIGHBOURS = "Neighbours"
PLACES = "Places"
THREATS = "Threats"
CHARACTERS = "Characters"
INCOME = "Income"
CALENDAR = "Calendar"
SHOWS: tuple[str, ...] = (
    EVERYTHING,
    TRIBUNAL,
    NEIGHBOURS,
    PLACES,
    THREATS,
    CHARACTERS,
    INCOME,
    CALENDAR,
)

#: The spans offered, in years (0: to the next Tribunal).
SPANS: tuple[int, ...] = (1, 2, 3, 5, 0)
DEFAULT_SPAN = 2


@dataclass(frozen=True)
class Entry:
    """One thing coming: its season, what it is, the filter it shows
    under, where it comes from (a name), and the covenant it concerns,
    if one. `calendar` is the index of the storyguide's entry it comes
    from (None for one worked out)."""

    year: int
    season: str
    title: str
    show: str
    source: str = ""
    covenant_id: str | None = None
    calendar: int | None = None
    tribunal_id: str | None = None

    @property
    def when(self) -> int:
        return season_order(season=self.season, year=self.year)


def _from_order(value: int) -> tuple[int, str]:
    return value // len(SEASONS), SEASONS[value % len(SEASONS)]


Source = Callable[[Saga, int, int], list[Entry]]

#: Every source Ahead asks, in the order registered.
SOURCES: list[Source] = []


def register(source: Source) -> Source:
    SOURCES.append(source)
    return source


# -- the span --


def now(saga: Saga) -> int:
    return season_order(season=saga.current_season, year=saga.current_year)


def _next_tribunal(saga: Saga) -> int | None:
    meetings = [
        season_order(season=t.next_season, year=t.next_year)
        for t in saga.tribunals
        if t.next_year is not None
        and season_order(season=t.next_season, year=t.next_year) >= now(saga)
    ]
    return min(meetings) if meetings else None


def end(saga: Saga) -> int:
    """The last season Ahead looks at: the span's years from now, or the
    next Tribunal's (two years with none set)."""
    span = saga.ahead_span
    if span <= 0:
        found = _next_tribunal(saga)
        if found is not None:
            return found
        span = DEFAULT_SPAN
    return now(saga) + span * len(SEASONS) - 1


def span_text(saga: Saga) -> str:
    """ "2 years (to Winter 1221)", or "To the next Tribunal (Summer
    1228)"."""
    year, season = _from_order(end(saga))
    if saga.ahead_span <= 0:
        return f"To the next Tribunal ({season} {year})"
    span = saga.ahead_span
    return f"{span} year{'' if span == 1 else 's'} (to {season} {year})"


def span_label(years: int) -> str:
    if years <= 0:
        return "To the next Tribunal"
    return f"{years} year{'' if years == 1 else 's'}"


# -- repeating --


def repeats(
    first: int, step: int | None, start: int, stop: int
) -> Iterator[tuple[int, str]]:
    """The seasons from `first`, every `step` seasons (None: once), that
    fall between `start` and `stop` (inclusive)."""
    when = first
    if step:
        while when < start:
            when += step
    while start <= when <= stop:
        yield _from_order(when)
        if not step:
            return
        when += step


# -- the sources --


@register
def _tribunals(saga: Saga, start: int, stop: int) -> list[Entry]:
    found = []
    for tribunal in saga.tribunals:
        if tribunal.next_year is None:
            continue
        meeting = season_order(season=tribunal.next_season, year=tribunal.next_year)
        if start <= meeting <= stop:
            found.append(
                Entry(
                    tribunal.next_year,
                    tribunal.next_season,
                    f"The {tribunal.name} Tribunal meets",
                    TRIBUNAL,
                    tribunal.name,
                    tribunal_id=tribunal.id,
                )
            )
        if any(not c.notice_given for c in tribunal_sheet.open_cases(tribunal)):
            due = tribunal_sheet.notice_due(tribunal)
            season, _, year = due.partition(" ")
            if year and start <= season_order(season=season, year=int(year)) <= stop:
                found.append(
                    Entry(
                        int(year),
                        season,
                        f"Notice due for the {tribunal.name} Tribunal's cases",
                        TRIBUNAL,
                        tribunal.name,
                        tribunal_id=tribunal.id,
                    )
                )
    return found


@register
def _terms(saga: Saga, start: int, stop: int) -> list[Entry]:
    """A ruling made for a term: the season before it ends, and the season
    it ends and goes back on the docket."""
    found = []
    for tribunal, case in tribunal_terms.termed(saga):
        if case.term_docketed:
            continue
        end = tribunal_terms.ends(case)
        for when, words in (
            (end - 1, "ends next season"),
            (end, "ends: back on the docket"),
        ):
            if start <= when <= stop:
                year, season = _from_order(when)
                found.append(
                    Entry(
                        year,
                        season,
                        f"The term of {case.title} {words}",
                        TRIBUNAL,
                        tribunal.name,
                        tribunal_id=tribunal.id,
                    )
                )
    return found


@register
def _fairs(saga: Saga, start: int, stop: int) -> list[Entry]:
    found = []
    for town in saga.neighbours:
        if town.kind != "town":
            continue
        for fair in town.details.get("fairs") or []:
            season = fair.get("season")
            if season not in SEASONS:
                continue
            trading = fair.get("covenant_id")
            title = f"{town.name}: {fair.get('name', 'the fair')}"
            if trading:
                title += " (income roll)"
            for year, when in repeats(
                season_order(season=season, year=saga.current_year),
                len(SEASONS),
                start,
                stop,
            ):
                found.append(
                    Entry(
                        year,
                        when,
                        title,
                        INCOME if trading else NEIGHBOURS,
                        town.name,
                        trading,
                    )
                )
    return found


@register
def _places(saga: Saga, start: int, stop: int) -> list[Entry]:
    found = []
    for place in saga.neighbours:
        if place.kind != "place":
            continue
        for trigger in place_events.triggers(place):
            date = place_events.next_date(saga, trigger)
            if date is None:
                continue
            when = trigger.get("when")
            step = (
                len(SEASONS)
                if when == place_events.YEARLY
                else len(SEASONS) * max(1, int(trigger.get("every") or 1))
                if when == place_events.EVERY
                else None
            )
            for year, season in repeats(
                season_order(season=date[1], year=date[0]), step, start, stop
            ):
                found.append(
                    Entry(
                        year,
                        season,
                        f"{place.name}: {trigger['name']}",
                        PLACES,
                        place.name,
                    )
                )
    return found


@register
def _threats(saga: Saga, start: int, stop: int) -> list[Entry]:
    found = []
    for threat in saga.neighbours:
        if (
            threat.kind != "threat"
            or not threats.by_date(threat)
            or threats.is_dormant(threat)
        ):
            continue
        for stage in threats.stages(threat):
            if (stage.get("outcome") or threats.PENDING) != threats.PENDING:
                continue
            year = stage.get("year")
            if year is None:
                continue
            season = stage.get("season") or SEASONS[-1]
            if start <= season_order(season=season, year=year) <= stop:
                found.append(
                    Entry(
                        year,
                        season,
                        f"{threat.name}: {stage['title']}",
                        THREATS,
                        threat.name,
                    )
                )
    return found


@register
def _characters(saga: Saga, start: int, stop: int) -> list[Entry]:
    found = []
    for character in saga.characters:
        born = character.background.year_born
        if born is not None and character.detail == FULL:
            year = born + aging.start_age(character)
            if (
                start <= season_order(season="Winter", year=year) <= stop
                and year > saga.current_year - 1
            ):
                found.append(
                    Entry(
                        year,
                        "Winter",
                        f"{character.name}'s aging rolls begin",
                        CHARACTERS,
                        character.name,
                        character.covenant_id,
                    )
                )
        until = character.aging.twilight_until
        season, _, year_text = until.partition(" ")
        if year_text.isdigit() and season in SEASONS:
            back = season_order(season=season, year=int(year_text)) + 1
            if start <= back <= stop:
                year, when = _from_order(back)
                found.append(
                    Entry(
                        year,
                        when,
                        f"{character.name} back from Twilight",
                        CHARACTERS,
                        character.name,
                        character.covenant_id,
                    )
                )
    return found


@register
def _world_turns(saga: Saga, start: int, stop: int) -> list[Entry]:
    first = season_order(season="Winter", year=saga.current_year)
    return [
        Entry(year, season, "The world turns: the yearly step", EVERYTHING, "the saga")
        for year, season in repeats(first, len(SEASONS), start, stop)
    ]


def calendar_step(entry: CalendarEntry) -> int | None:
    if entry.repeats == YEARLY:
        return len(SEASONS)
    if entry.repeats == EVERY:
        return len(SEASONS) * max(1, entry.every or 1)
    return None


@register
def _calendar(saga: Saga, start: int, stop: int) -> list[Entry]:
    found = []
    for index, entry in enumerate(saga.calendar):
        first = season_order(season=entry.season, year=entry.year)
        for year, season in repeats(first, calendar_step(entry), start, stop):
            found.append(
                Entry(
                    year,
                    season,
                    entry.title,
                    CALENDAR,
                    "",
                    entry.covenant_id,
                    calendar=index,
                )
            )
    return found


# -- asking --


def concerns(saga: Saga, entry: Entry, covenant: Covenant) -> bool:
    """Whether `entry` concerns `covenant`: it names the covenant, or
    is its Tribunal's, a threat or place of the region, or the
    storyguide's own for the whole saga."""
    if entry.covenant_id is not None:
        return entry.covenant_id == covenant.id
    if entry.show == TRIBUNAL:
        return entry.tribunal_id == covenant.tribunal_id
    return entry.show in (THREATS, PLACES, CALENDAR)


def entries(
    saga: Saga, show: str = EVERYTHING, covenant: Covenant | None = None
) -> list[Entry]:
    """Everything coming from this season to the span's end, soonest
    first: only what shows under `show` (Everything: all), and (given a
    covenant) only what concerns it."""
    start, stop = now(saga), end(saga)
    found = [e for source in SOURCES for e in source(saga, start, stop)]
    if show in SHOWS and show != EVERYTHING:
        found = [e for e in found if e.show == show]
    if covenant is not None:
        found = [e for e in found if concerns(saga, e, covenant)]
    return sorted(found, key=lambda e: e.when)


def by_season(found: list[Entry]) -> list[tuple[int, str, list[Entry]]]:
    """The entries as (year, season, entries), a season at a time."""
    grouped: dict[int, list[Entry]] = {}
    for entry in found:
        grouped.setdefault(entry.when, []).append(entry)
    return [(*_from_order(when), grouped[when]) for when in sorted(grouped)]


def due_now(saga: Saga) -> int:
    """How many entries come this season."""
    return sum(1 for e in entries(saga) if e.when == now(saga))


def next_tribunal_text(saga: Saga) -> str:
    found = _next_tribunal(saga)
    if found is None:
        return "not set"
    year, season = _from_order(found)
    return f"{season} {year}"


def season_text(saga: Saga, year: int, season: str) -> str:
    """ "Summer 1220", with " · now" for the current season."""
    shown = f"{season} {year}"
    return (
        f"{shown} · now"
        if season_order(season=season, year=year) == now(saga)
        else shown
    )


def shown(saga: Saga, covenant: Covenant | None = None) -> list[Entry]:
    """What the Ahead list shows: the saga's filter, or (for a
    covenant) everything that concerns it."""
    if covenant is not None:
        return entries(saga, EVERYTHING, covenant)
    return entries(saga, saga.ahead_show)


def title(saga: Saga, covenant: Covenant | None = None) -> str:
    """ "Looking Ahead: 2 years", or "Ahead for Keep: 2 years"."""
    span = span_label(saga.ahead_span)
    if covenant is not None:
        return f"Ahead for {covenant.name}: {span}"
    show = "" if saga.ahead_show == EVERYTHING else f" · {saga.ahead_show}"
    return f"Looking Ahead: {span}{show}"


def grid(saga: Saga, covenant: Covenant | None = None) -> Grid:
    """Each entry under its season (named on the season's first row),
    with where it comes from; the current season is marked."""
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    for year, season, found in by_season(shown(saga, covenant)):
        for index, entry in enumerate(found):
            row = len(rows)
            if index == 0:
                styles[(row, 0)] = (
                    "$text-warning"
                    if season_order(season=season, year=year) == now(saga)
                    else "b"
                )
            if entry.calendar is not None:
                styles[(row, 2)] = "i"
            rows.append(
                [
                    season_text(saga, year, season) if index == 0 else "",
                    entry.title,
                    entry.source or "your calendar",
                ]
            )
    return Grid(
        ["Season", "What", "From"],
        rows,
        list(range(len(rows))),
        "Nothing coming in this span: add your own with a.",
        styles,
        caps=[17, 36, 14],
        stretch=1,
    )


def facts(saga: Saga) -> list[Fact]:
    """The Seasons top panel: the date, the span, the next Tribunal and
    what comes this season."""
    return [
        Fact("Now", f"{saga.current_season} {saga.current_year}"),
        Fact("Ahead", span_text(saga)),
        Fact("Next Tribunal", next_tribunal_text(saga)),
        Fact("Due this season", str(due_now(saga))),
    ]


def detail_text(saga: Saga, entry: Entry) -> str:
    """An entry in detail (markup): where it comes from, and for one of
    the storyguide's own, how often it comes and its note."""
    lines = [f"[b]{escape(entry.title)}[/]", f"{entry.season} {entry.year}"]
    if entry.calendar is None:
        lines.append(
            f"[$label]Worked out from {escape(entry.source or 'the saga')}: "
            "change it there.[/]"
        )
        return "\n".join(lines)
    written = saga.calendar[entry.calendar]
    comes = (
        f"every {written.every or 1} years"
        if written.repeats == EVERY
        else written.repeats.lower()
    )
    covenant = saga.covenant(written.covenant_id)
    lines.append(
        f"Comes {comes}, for {escape(covenant.name if covenant else 'the whole saga')}."
    )
    if written.note:
        lines.append(escape(written.note))
    lines.append("[$label]Your own entry: Edit or Delete changes it.[/]")
    return "\n".join(lines)
