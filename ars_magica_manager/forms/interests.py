"""Interests: the kinds of deed a character takes up, chosen on the
Manage chapter, More on the record, or the Creation Worksheet's Review
Interests -- no UI in here.

An interest left unticked hides its actions (deeds.INTEREST_OF) from the
Deeds chapter, A Season's Work and More; the rules still decide what a
ticked interest offers. The desktop draws the form as cards (FormCard),
each counting the actions the saga's books bring and its inspector saying
where they are; those places come from deeds' tables, so they can't drift."""

from __future__ import annotations

from typing import Any

from .. import action_books, deeds, sourcebooks
from ..actions import MORE_MENU
from ..commands import Form, FormCard, notes
from ..deeds import OPTIONAL
from ..form_spec import DialogField
from ..models import Character, Saga

TITLE = "Interests"
HELP = "interests"
LEAD = (
    "The kinds of deed this character takes up. Unticked interests leave the "
    "sheet; choose a card to see what it adds."
)
#: Where a card's Session & Reputation stands instead of a switch.
ALWAYS_ON = "Always on"


def _key(interest: str) -> str:
    return "interest_" + "".join(c if c.isalnum() else "_" for c in interest.lower())


def _name(action: str) -> str:
    """What More calls `action`."""
    return next(item.label for item in MORE_MENU if item.action == action)


def _count(ready: int, waiting: int) -> str:
    """How many actions an interest brings to this saga."""
    if not ready:
        return "Its books aren't in play"
    line = "1 action" if ready == 1 else f"{ready} actions"
    return f"{line}, {waiting} more with other books" if waiting else line


def _detail(interest: str, ready: list[str], waiting: list[str]) -> str:
    """An interest's inspector: what it is, where each of its actions
    appears, then those waiting for a book, under the book."""
    parts = [deeds.ABOUT[interest]]
    for heading, notes_of in (
        ("On the Deeds chapter", deeds.NOTES),
        ("On Planning, in A Season's Work", deeds.SEASON_NOTES),
    ):
        lines = [f"[b]{_name(a)}[/]: {notes_of[a]}" for a in ready if a in notes_of]
        if lines:
            parts.append("\n".join([f"[$label]{heading}[/]", *lines]))
    books: dict[str, list[str]] = {}
    for action in waiting:
        titles = [
            sourcebooks.SOURCEBOOKS[book] for book in action_books.ACTION_BOOKS[action]
        ]
        books.setdefault(" or ".join(titles), []).append(_name(action))
    parts += [
        f"[dim]With {book}: {', '.join(names)}.[/]" for book, names in books.items()
    ]
    return "\n\n".join(parts)


def interest_cards(saga: Saga) -> list[FormCard]:
    """A card for each interest, counting what the saga's books bring;
    whether an action also fits the character changes in play, so it isn't
    counted."""
    cards = []
    for interest in deeds.INTERESTS:
        members = deeds.members(interest)
        ready = [a for a in members if action_books.book_allows(a, saga)]
        waiting = [a for a in members if a not in ready]
        cards.append(
            FormCard(
                _key(interest) if interest in OPTIONAL else "",
                interest,
                deeds.SUMMARIES[interest],
                _count(len(ready), len(waiting)),
                _detail(interest, ready, waiting),
                usable=bool(ready),
                fixed="" if interest in OPTIONAL else ALWAYS_ON,
            )
        )
    return cards


def interests_text(character: Character) -> str:
    """The interests he has turned off, in words."""
    off = [i for i in OPTIONAL if i in character.interests_off]
    if not off:
        return "Every interest is ticked."
    return "Turned off: " + ", ".join(off) + "."


def interests_form(saga: Saga, character: Character) -> Form:
    """A tick for each interest he may turn off."""

    def fields() -> list[DialogField]:
        return [
            DialogField(
                _key(i),
                i,
                "check",
                value=i not in character.interests_off,
                hint=deeds.SUMMARIES[i],
            )
            for i in OPTIONAL
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        character.interests_off = [i for i in OPTIONAL if not values.get(_key(i))]
        return notes(f"{character.name}: {interests_text(character)}")

    return Form(
        TITLE,
        fields,
        apply,
        help_id=HELP,
        cards=lambda: interest_cards(saga),
        cards_lead=LEAD,
    )
