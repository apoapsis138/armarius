"""Choosing a season's activity, independent of how it is drawn: the
activity picker the Plan Season form and the lab work form open, its
entries grouped by what the season is for (rules.activity_groups) and
filtered by that Type and by sourcebook, with the character's recent
activities first.

The groups are the activity registry's own (Activity.group), so a new
activity is listed under its group without another table to keep."""

from __future__ import annotations

from .. import sourcebooks
from ..commands import Choice, Choose, Picked, not_offered
from ..markup import escape
from ..models import SEASONS, Character, Saga
from ..rules import activities as season_rules
from ..rules import activity_groups as groups
from ..rules import lab_seasons
from ..seasons.plans import _cite

#: The picker's filters, in order: the first heads the list.
TYPE, BOOK = "Type", "Book"
#: The Book filter's value for an activity of the core rules.
CORE_BOOK = "Core rules"
#: How many recent activities head the list.
RECENT_COUNT = 3


def activity_label(key: str | None) -> str:
    """How the Activity field shows a chosen activity: its label."""
    activity = season_rules.ACTIVITIES.get(key or "")
    return activity.label if activity else (key or "")


def book_name(activity: season_rules.Activity) -> str:
    """The sourcebook an activity comes from, as the Book filter names it."""
    if activity.book in ("", sourcebooks.CORE):
        return CORE_BOOK
    return sourcebooks.SOURCEBOOKS.get(activity.book, activity.book)


def _choice(activity: season_rules.Activity) -> Choice:
    book = book_name(activity)
    return Choice(
        escape(activity.label),
        activity.key,
        f"[b]{escape(activity.label)}[/]\n{escape(activity.summary)}\n\n"
        f"[dim]Type: {escape(activity.group)}. Book: {escape(book)}. "
        f"Rule: {escape(_cite(activity.source))}.[/]",
        f"{activity.summary} {activity.group} {book}",
        ((TYPE, activity.group), (BOOK, book)),
    )


def _in_order(
    activities: list[season_rules.Activity], order: tuple[str, ...]
) -> list[season_rules.Activity]:
    """`activities` by their group's place in `order`, then by label."""
    place = {group: index for index, group in enumerate(order)}
    return sorted(
        activities, key=lambda a: (place.get(a.group, len(order)), a.label.lower())
    )


def _recent_keys(saga: Saga, character: Character) -> list[str]:
    """The activities `character` spent or planned their latest seasons
    on, newest first, each once: their plans, then their Diary."""
    by_label = {a.label: a.key for a in season_rules.ACTIVITIES.values()}
    dated = [
        (p.year, SEASONS.index(p.season), p.activity)
        for p in saga.season_plans
        if p.character_id == character.id and p.season in SEASONS
    ] + [
        (e.year, SEASONS.index(e.season), by_label[e.activity])
        for e in character.diary
        if e.activity in by_label and e.season in SEASONS
    ]
    return list(dict.fromkeys(key for *_, key in sorted(dated, reverse=True)))


def choose_activity(
    saga: Saga, character: Character, current: str | None = None, *, lab: bool = False
) -> Choose:
    """The activity picker for `character`'s season: on the character
    sheet, everything but lab work; with `lab`, the lab work. Activities
    from books not in play are listed only when asked for, marked."""
    books = sourcebooks.saga_books(saga)
    order = groups.LAB_GROUPS if lab else groups.GROUPS
    if lab:
        offered = [season_rules.ACTIVITIES[key] for key in lab_seasons.LAB_ACTIVITIES]
        others: list[season_rules.Activity] = []
    else:
        offered = season_rules.activities_for(
            character, books=books, keep=current or ""
        )
        everything = season_rules.activities_for(character, books=None)
        others = [a for a in everything if a not in offered]
    offered = _in_order(offered, order)
    keys = {a.key for a in offered}

    def recent() -> list[Choice]:
        found = [k for k in _recent_keys(saga, character) if k in keys]
        return [_choice(season_rules.ACTIVITIES[k]) for k in found[:RECENT_COUNT]]

    who = escape(character.name)
    return Choose(
        f"Choose {who}'s lab work" if lab else f"Choose {who}'s activity",
        lambda: [_choice(a) for a in offered],
        Picked,
        empty="No activities to choose from.",
        others=(
            (
                lambda: [
                    not_offered(_choice(a), "book not in play")
                    for a in _in_order(others, order)
                ]
            )
            if others
            else None
        ),
        help_id="invent-spell-activity" if lab else "plan-season-activity",
        filters=(TYPE, BOOK),
        recent=recent,
    )
