"""The covenant's side of a season: dwindling and lapsed resources, its
vis and income, and the covenant's Seasons tab."""

from __future__ import annotations

from collections.abc import Callable, Collection

from .. import vis_harvest
from ..covenants import contested_now, settle_resource
from ..grids import Grid
from ..markup import escape
from ..models import (
    SEASONS,
    Character,
    Covenant,
    CovenantDiaryEntry,
    IncomeSource,
    Possession,
    Saga,
    SeasonRecordLine,
)
from ..rules import activities as rules
from ..rules.covenfolk import character_kind
from ..rules.rounding import round_away_from_zero, round_down
from ..tables import Table
from ..world import takes_part_in_play
from .plans import (
    is_departed,
    plan_for,
    plan_summary,
    plan_text,
    planning_year,
    seasons_ahead,
    working_seasons_done,
)

DWINDLING_SOURCE = (
    "Covenants, Chapter Two: Boons & Hooks, Minor Resources Hooks, Dwindling Resource, "
    "p. 16"
)


#: A Dwindling Resource loses 1 / DWINDLING_YEARS of its original value each
#: year, so it is gone after DWINDLING_YEARS years (DWINDLING_SOURCE).
DWINDLING_YEARS = 10


def dwindle(
    resource: IncomeSource | Possession,
    value: int,
    rounding: Callable[[float], int],
) -> int:
    """`resource`'s value (now `value`) after a year's end. A Dwindling
    Resource loses a tenth of its original value: the value when it began
    to dwindle, taken as its value at its first year end (so an older
    save starts from its value then). Income rounds away from
    zero (covenant finances), vis pawns down. A resource no longer dwindling
    forgets its original value, so ticking it again starts afresh."""
    if not resource.dwindling:
        resource.dwindling_from = None
        resource.dwindled_years = 0
        return value
    if resource.dwindling_from is None:
        resource.dwindling_from = value
        resource.dwindled_years = 0
    resource.dwindled_years = min(DWINDLING_YEARS, resource.dwindled_years + 1)
    left = DWINDLING_YEARS - resource.dwindled_years
    return rounding(resource.dwindling_from * left / DWINDLING_YEARS)


def _vis_sources(covenant: Covenant) -> list:
    return [p for p in covenant.possessions if p.kind == "vis_source"]


def lapsed_resources(saga: Saga) -> list[tuple[str, str]]:
    """The contested resources to ask about before advancing: (id, label)
    for vis sources harvested this season and, in Winter, income sources,
    whose security has lapsed."""
    year = saga.current_year
    found: list[tuple[str, str]] = []
    for covenant in filter(takes_part_in_play, saga.covenants):
        for source in _vis_sources(covenant):
            if contested_now(source, year) and source.season == saga.current_season:
                found.append(
                    (source.id, f"{covenant.name}'s {source.name or 'vis source'}")
                )
        if saga.current_season == SEASONS[-1]:
            for income in covenant.economics.income_sources:
                if contested_now(income, year):
                    found.append(
                        (
                            income.id,
                            f"{covenant.name}'s {income.name or 'income source'}",
                        )
                    )
    return found


def available(resource: Possession | IncomeSource, year: int) -> bool:
    """Whether a vis or income source gives anything this year: not contested,
    or secured through it: an unaddressed contested resource isn't
    available until it is addressed."""
    return not contested_now(resource, year)


def waiting_sources(
    saga: Saga, secured: dict[str, bool]
) -> list[tuple[Covenant, Possession]]:
    """With Harvest Vis by Hand on, the vis sources still waiting to be
    gathered as the season is advanced, with their covenants: those that
    could be harvested now (vis_harvest), a lapsed one counting as settled
    when `secured` says it was secured this season."""
    return [
        (covenant, source)
        for covenant in filter(takes_part_in_play, saga.covenants)
        for source in _vis_sources(covenant)
        if vis_harvest.harvestable(saga, source, settling=secured.get(source.id, False))
    ]


def covenant_season(
    saga: Saga, secured: dict[str, bool], gathered: Collection[str] = ()
) -> list[SeasonRecordLine]:
    """What the season does for each covenant: its vis sources
    harvested into its vis stores, and in Winter, Dwindling Resources shrink
    by a tenth. A contested resource gives nothing until it is addressed:
    `secured` answers "Was it secured this season?" for each lapsed one
    (yes: secured for five years), and a year that ends with it unaddressed
    is written in the covenant Diary. With Harvest Vis by Hand on, a source
    is gathered by hand during its season (vis_harvest), counted here; one
    still waiting is gathered by the covenfolk now if `gathered` names it
    (by id), and otherwise lost for the year. Returns record lines."""
    season, year = saga.current_season, saga.current_year
    lines: list[SeasonRecordLine] = []
    for covenant in filter(takes_part_in_play, saga.covenants):
        resources = [*_vis_sources(covenant), *covenant.economics.income_sources]
        for resource in resources:
            if secured.get(resource.id):
                settle_resource(resource, year)
        harvested = [
            f"{entry.vis_pawns} {entry.vis_art}"
            for entry in vis_harvest.harvested_this_season(saga, covenant)
        ]
        for source in _vis_sources(covenant):
            if source.season != season or not source.art or source.pawns <= 0:
                continue
            if source.harvested_year == year:
                continue  # gathered by hand this season, and counted above
            if not available(source, year):
                covenant.diary.append(
                    CovenantDiaryEntry(
                        year,
                        season,
                        f"{source.name or 'A vis source'} not harvested",
                        "A contested resource not yet secured: no harvest.",
                        category="Covenant Season",
                    )
                )
                continue
            if saga.harvest_vis_by_hand and source.id in gathered:
                vis_harvest.harvest(saga, covenant, source, source.pawns)
                harvested.append(f"{source.pawns} {source.art}")
                continue
            if saga.harvest_vis_by_hand:
                covenant.diary.append(
                    CovenantDiaryEntry(
                        year,
                        season,
                        f"{source.name or 'A vis source'} not harvested",
                        "Nobody gathered it this season: its vis is lost for the year.",
                        category="Covenant Season",
                    )
                )
                continue
            vis_harvest.add_vis(covenant, source, source.pawns)
            source.harvested_year = year
            harvested.append(f"{source.pawns} {source.art}")
            covenant.diary.append(
                CovenantDiaryEntry(
                    year,
                    season,
                    f"Vis harvested: {source.name or source.art}",
                    f"{source.pawns} pawn(s) of {source.art} vis into the vis stores.",
                    category="Covenant Season",
                    vis_pawns=source.pawns,
                    vis_art=source.art,
                )
            )
        if season == SEASONS[-1]:
            for resource in resources:
                if not available(resource, year):
                    covenant.diary.append(
                        CovenantDiaryEntry(
                            year,
                            season,
                            f"{resource.name or 'A resource'} not received",
                            "A contested resource still unresolved at the year's "
                            "end: the covenant receives nothing from it this year.",
                            category="Covenant Season",
                        )
                    )
            for income in covenant.economics.income_sources:
                value = dwindle(income, income.current_income, round_away_from_zero)
                if income.dwindling:
                    income.income = value
            for source in _vis_sources(covenant):
                source.pawns = dwindle(source, source.pawns, round_down)
        if harvested:
            lines.append(
                SeasonRecordLine(
                    covenant.id,
                    covenant.name,
                    covenant.id,
                    "Vis harvest",
                    "",
                    ", ".join(harvested),
                )
            )
    return lines


#: The covenant Seasons tab's lists: (character kind, title). A Mythic
#: Companion is listed with the Companions.
SEASON_KINDS: tuple[tuple[str, str], ...] = (
    ("magus", "Magi"),
    ("companion", "Companions"),
    ("grog", "Grogs"),
)


#: The widest the name and each season's column may be on the Seasons
#: board, so the year fits the tab at 120 columns.
_NAME_CAP, _SEASON_CAP = 18, 12


def covenant_people(saga: Saga, covenant: Covenant, kind: str) -> list[Character]:
    """The covenant's characters of `kind` (a SEASON_KINDS key), in the
    saga's order, leaving out any marked departed."""
    return [
        c
        for c in saga.characters
        if c.covenant_id == covenant.id
        and character_kind(c) == kind
        and takes_part_in_play(c)
        and not is_departed(saga, c)
    ]


def season_title(saga: Saga, covenant: Covenant, kind: str, title: str) -> str:
    """A Seasons list's title: "Magi (1 of 2 planned)", or "Grogs (3)"."""
    people = covenant_people(saga, covenant, kind)
    if kind == "grog":
        return f"{title} ({len(people)})"
    planned = sum(1 for c in people if plan_for(saga, c) is not None)
    return f"{title} ({planned} of {len(people)} planned)"


def _worked(saga: Saga, character: Character) -> str:
    """ "1 of 2": a companion's working seasons this year, those in the
    Diary and those planned for the rest of it."""
    year = saga.current_year
    done = working_seasons_done(character, year, saga.current_season)
    for season in SEASONS[SEASONS.index(saga.current_season) :]:
        plan = plan_for(saga, character, season, year)
        activity = rules.ACTIVITIES.get(plan.activity) if plan else None
        if activity is not None and activity.working:
            done += 1
    return f"{done} of {rules.working_seasons(character, year)}"


def season_board(saga: Saga, covenant: Covenant, kind: str) -> Grid:
    """People of `kind` down and the year to plan across (this season and
    the three after it), each cell the activity planned or "nothing";
    companions also count their working seasons this year. A grog's
    yearly update covers the year."""
    year = planning_year(saga)
    companions = kind == "companion"
    columns = ["Name", *(f"{season} {y}" for season, y in year)]
    if companions:
        columns.append("Worked")
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    for row, character in enumerate(covenant_people(saga, covenant, kind)):
        name = (character.name or "(unnamed)") + (
            " (Mythic)" if character.type == "mythic companion" else ""
        )
        cells = [name]
        if not rules.is_planned(character):
            cells += ["yearly", *([""] * (len(year) - 1))]
        else:
            for column, (season, y) in enumerate(year, start=1):
                plan = plan_for(saga, character, season, y)
                activity = rules.ACTIVITIES.get(plan.activity) if plan else None
                if plan is None:
                    cells.append("nothing")
                    styles[(row, column)] = "$text-warning" if column == 1 else "dim"
                else:
                    cells.append(activity.label if activity else plan.activity)
        if companions:
            cells.append(_worked(saga, character))
        rows.append(cells)
    return Grid(
        columns,
        rows,
        list(range(len(rows))),
        "Nobody here.",
        styles,
        caps=[_NAME_CAP, *([_SEASON_CAP] * len(year)), 6],
    )


def season_rows(
    saga: Saga, covenant: Covenant, kind: str
) -> list[tuple[int | None, str]]:
    """The Seasons board as a list's rows (season_board): a heading of the
    seasons, then a row per person."""
    return season_board(saga, covenant, kind).lines()


def season_table(saga: Saga, covenant: Covenant, kind: str) -> Table:
    """season_board as a table (markup)."""
    return season_board(saga, covenant, kind).table()


def season_info_text(saga: Saga, character: Character | None) -> str:
    """The Seasons tab's details panel for the chosen person."""
    if character is None:
        return "[dim]Select someone to see their seasons.[/]"
    text = f"[b]{escape(character.name)}[/]\n" + plan_text(saga, character)
    if not rules.is_planned(character):
        return text
    ahead = [
        f"{season} {year}: "
        + (escape(plan_summary(saga, character, plan)) if plan else "[dim]nothing[/]")
        for season, year in seasons_ahead(saga)
        for plan in [plan_for(saga, character, season, year)]
    ]
    return text + "\n\n[$label]Seasons ahead[/]\n" + "\n".join(ahead)
