"""The covenant's side of a season: dwindling and lapsed resources, its
vis and income, and the covenant's Seasons tab."""

from __future__ import annotations

from collections.abc import Callable

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
    new_instance_id,
)
from ..rules import activities as rules
from ..rules import vis_kinds
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
            if (
                source.contested
                and source.season == saga.current_season
                and (source.secured_until or 0) < year
            ):
                found.append(
                    (source.id, f"{covenant.name}'s {source.name or 'vis source'}")
                )
        if saga.current_season == SEASONS[-1]:
            for income in covenant.economics.income_sources:
                if income.contested and (income.secured_until or 0) < year:
                    found.append(
                        (
                            income.id,
                            f"{covenant.name}'s {income.name or 'income source'}",
                        )
                    )
    return found


def _add_vis(covenant: Covenant, source: Possession) -> None:
    """The source's harvest into the covenant's first store of its Art and
    kind of vis (and Infernal mark), or a new one."""
    art, pawns = source.art, source.pawns
    store = next(
        (
            p
            for p in covenant.possessions
            if p.kind == "vis_store"
            and p.art.lower() == art.lower()
            and vis_kinds.same_kind(p, source)
        ),
        None,
    )
    if store is None:
        special = bool(source.vis_kind)
        store = Possession(
            id=f"vis_{new_instance_id()}",
            kind="vis_store",
            name=(source.name or f"{art} vis") if special else f"{art} vis",
            art=art,
            pawns=pawns,
            location_kind="covenant",
            location_id=covenant.id,
            physical_form=source.physical_form if special else "",
        )
        covenant.possessions.append(vis_kinds.copy_kind(source, store))
    else:
        store.pawns += pawns


def available(resource: Possession | IncomeSource, year: int) -> bool:
    """Whether a vis or income source gives anything this year: not contested,
    or secured through it: an unaddressed contested resource isn't
    available until it is addressed."""
    return not resource.contested or (resource.secured_until or 0) >= year


def covenant_season(saga: Saga, secured: dict[str, bool]) -> list[SeasonRecordLine]:
    """What the season does for each covenant: its vis sources
    harvested into its vis stores, and in Winter, Dwindling Resources shrink
    by a tenth. A contested resource gives nothing until it is addressed:
    `secured` answers "Was it secured this season?" for each lapsed one
    (yes: secured for five years), and a year that ends with it unaddressed
    is written in the covenant Diary. Returns record lines."""
    season, year = saga.current_season, saga.current_year
    lines: list[SeasonRecordLine] = []
    for covenant in filter(takes_part_in_play, saga.covenants):
        resources = [*_vis_sources(covenant), *covenant.economics.income_sources]
        for resource in resources:
            if secured.get(resource.id):
                resource.secured_until = year + 4
        harvested: list[str] = []
        for source in _vis_sources(covenant):
            if source.season != season or not source.art or source.pawns <= 0:
                continue
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
            _add_vis(covenant, source)
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
