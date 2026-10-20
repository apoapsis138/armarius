"""Rulings made for a term: what a Tribunal settled for some years ("holds
the vis source for 7 years, until it is debated again") comes due when
the term ends. Ahead lists the season before it ends and the season it
does; advancing into the season before says so, and advancing into the
season it ends says so and puts the matter back on its Tribunal's
docket as a new case, to be debated at the next meeting.

A term is kept on its case (Case.term_ends_year and term_ends_season,
set when the meeting that ruled closes)."""

from __future__ import annotations

from collections.abc import Iterator

from .models import CASE_OPEN, SEASONS, Case, Saga, Tribunal
from .models.seasons import next_season


def _order(year: int, season: str) -> int:
    return year * len(SEASONS) + (SEASONS.index(season) if season in SEASONS else 0)


def termed(saga: Saga) -> Iterator[tuple[Tribunal, Case]]:
    """Every case with a term, and its Tribunal."""
    for tribunal in saga.tribunals:
        for case in tribunal.cases:
            if case.term_ends_year is not None:
                yield tribunal, case


def ends(case: Case) -> int:
    """When the term ends, as a season that sorts by date."""
    assert case.term_ends_year is not None
    return _order(case.term_ends_year, case.term_ends_season or "Summer")


def ends_text(case: Case) -> str:
    """ "Summer 1235"."""
    return f"{case.term_ends_season or 'Summer'} {case.term_ends_year}"


def again(case: Case, year: int, season: str) -> Case:
    """The case that puts a termed ruling back on the docket."""
    return Case(
        f"{case.title} (debated again)",
        kind=case.kind,
        brought_by=case.brought_by,
        against=case.against,
        charge=f"Its term ended in {ends_text(case)}. The ruling was: "
        f"{case.outcome.strip() or '(not recorded)'}",
        filed_year=year,
        filed_season=season,
        status=CASE_OPEN,
    )


def come_due(saga: Saga) -> list[str]:
    """After the date moves on: each term ending next season is told, and
    each that has ended (and isn't on the docket yet) is put back on its
    Tribunal's docket and told. Returns the lines to tell."""
    now = _order(saga.current_year, saga.current_season)
    following = next_season(saga.current_season, saga.current_year)
    soon = _order(following[1], following[0])
    lines: list[str] = []
    for tribunal, case in list(termed(saga)):
        if case.term_docketed:
            continue
        when = ends(case)
        if when == soon:
            lines.append(
                f"{case.title}: its term ends next season ({ends_text(case)}), "
                f"and it goes back on the {tribunal.name} docket."
            )
        elif when <= now:
            tribunal.cases.append(again(case, saga.current_year, saga.current_season))
            case.term_docketed = True
            lines.append(
                f"{case.title}: its term has ended ({ends_text(case)}); it is "
                f"on the {tribunal.name} docket to be debated again."
            )
    return lines
