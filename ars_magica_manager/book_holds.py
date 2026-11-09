"""Book holds: a book one character has planned to use in a season (to
read, copy, translate...) is theirs that season. Another character's plan
for the same book in that season is refused, saying who holds it and until
when ("That book is held by Aelfric until Summer 1222"), as a Study path
never plans it either.

Pattern: a plain query over the season plans, as seasons.plans' own
lookups are."""

from __future__ import annotations

from .markup import escape
from .models import Saga, SeasonPlan, next_season


def _uses(plan: SeasonPlan, book_id: str) -> bool:
    return plan.book_id == book_id or book_id in plan.more_book_ids


def holder(
    saga: Saga, book_id: str, season: str, year: int, other_than: str
) -> tuple[str, str, int] | None:
    """Who holds `book_id` in that season, other than the character
    `other_than`: their id, and the last season of their unbroken run of
    plans using it."""
    found = next(
        (
            p
            for p in saga.season_plans
            if p.season == season
            and p.year == year
            and p.character_id != other_than
            and _uses(p, book_id)
        ),
        None,
    )
    if found is None:
        return None
    until = (season, year)
    while True:
        after = next_season(*until)
        if not any(
            p.character_id == found.character_id
            and (p.season, p.year) == after
            and _uses(p, book_id)
            for p in saga.season_plans
        ):
            break
        until = after
    return found.character_id, until[0], until[1]


def problem(saga: Saga, plan: SeasonPlan) -> str | None:
    """Why `plan` can't use its book that season, or None."""
    for book_id in [plan.book_id, *plan.more_book_ids]:
        if not book_id:
            continue
        held = holder(saga, book_id, plan.season, plan.year, plan.character_id)
        if held is None:
            continue
        who, season, year = held
        character = saga.character(who)
        book = next((b for b in saga.books if b.id == book_id), None)
        name = escape(book.name) if book is not None else "That book"
        return (
            f"{name} is held by {escape(character.name if character else who)} "
            f"until {season} {year}."
        )
    return None


def free(saga: Saga, book_id: str, season: str, year: int, character_id: str) -> bool:
    """Whether the character may use `book_id` that season."""
    return holder(saga, book_id, season, year, character_id) is None
