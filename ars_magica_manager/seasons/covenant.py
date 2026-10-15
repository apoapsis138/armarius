"""The covenant's side of a season: dwindling and lapsed resources, its
vis and income, and the covenant's Seasons tab."""

from __future__ import annotations

from collections.abc import Callable

from ..inhabitants import character_kind
from ..markup import escape, fit, todo
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
from ..rules.rounding import round_away_from_zero, round_down
from ..tables import Table
from ..world import takes_part_in_play
from .plans import is_departed, plan_for, plan_summary, plan_text

DWINDLING_SOURCE = (
    "Covenants, Chapter Two: Boons & Hooks, Minor Resources Hooks, Dwindling "
    "Resource (https://www.redcap.org/page/Covenants_Chapter_Two:_Boons_%26_Hooks"
    "#Minor_Resources_Hooks)"
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


def _add_vis(covenant: Covenant, art: str, pawns: int, name: str) -> None:
    store = next(
        (
            p
            for p in covenant.possessions
            if p.kind == "vis_store" and p.art.lower() == art.lower()
        ),
        None,
    )
    if store is None:
        covenant.possessions.append(
            Possession(
                id=f"vis_{new_instance_id()}",
                kind="vis_store",
                name=f"{art} vis",
                art=art,
                pawns=pawns,
                location_kind="covenant",
                location_id=covenant.id,
            )
        )
    else:
        store.pawns += pawns


def available(resource, year: int) -> bool:
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
            _add_vis(covenant, source.art, source.pawns, source.name)
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


#: Width of the name column in the Seasons lists.
_NAME_WIDTH = 24


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


def _season_cells(saga: Saga, covenant: Covenant, kind: str) -> list[tuple[str, str]]:
    """Each person's name and what they have planned for the current
    season ("Practice: Latin"), or that nothing is (markup)."""
    cells = []
    for character in covenant_people(saga, covenant, kind):
        name = character.name + (
            " (Mythic)" if character.type == "mythic companion" else ""
        )
        if not rules.is_planned(character):
            what = "[dim]updated yearly[/]"
        else:
            plan = plan_for(saga, character)
            what = (
                escape(plan_summary(saga, character, plan))
                if plan is not None
                else todo("nothing planned")
            )
        cells.append((name, what))
    return cells


def season_rows(saga: Saga, covenant: Covenant, kind: str) -> list[tuple[int, str]]:
    """(index, row) per person: their name and what they have planned for
    the current season ("Practice: Latin"), or that nothing is."""
    return [
        (index, f"{escape(fit(name, _NAME_WIDTH).ljust(_NAME_WIDTH))}  {what}")
        for index, (name, what) in enumerate(_season_cells(saga, covenant, kind))
    ]


def season_table(saga: Saga, covenant: Covenant, kind: str) -> Table:
    """season_rows as a table (markup): each person and their season."""
    return Table(
        ["Name", "This season"],
        [[escape(name), what] for name, what in _season_cells(saga, covenant, kind)],
        markup=True,
        stretch=1,
    )


def season_info_text(saga: Saga, character: Character | None) -> str:
    """The Seasons tab's details panel for the chosen person."""
    if character is None:
        return "[dim]Select someone to see their season.[/]"
    return f"[b]{escape(character.name)}[/]\n" + plan_text(saga, character)
