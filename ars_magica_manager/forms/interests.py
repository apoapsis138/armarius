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
from ..rules import faiths

TITLE = "Interests"
HELP = "interests"
LEAD = (
    "The kinds of deed this character takes up. Unticked interests leave the "
    "sheet; choose a card to see what it adds."
)
#: Where a card that can't be turned off has a switch.
ALWAYS_ON = "Always on"
CHURCH_CAREER = "On for a Church career"
#: Who a faith's actions are counted for.
_FOR = {
    faiths.CHRISTIAN: "a Christian",
    faiths.MUSLIM: "a Muslim",
    faiths.JEWISH: "a Jew",
    faiths.MAZDEAN: "a Mazdean",
    faiths.PAGAN: "a pagan",
}


def _key(interest: str) -> str:
    return "interest_" + "".join(c if c.isalnum() else "_" for c in interest.lower())


def _name(action: str) -> str:
    """What More calls `action`."""
    return next(item.label for item in MORE_MENU if item.action == action)


def _count(ready: int, waiting: int, reader: str = "") -> str:
    """How many actions an interest brings to this saga (for `reader`, an
    interest whose actions go by faith)."""
    if not ready and not reader:
        return "Its books aren't in play"
    line = "1 action" if ready == 1 else f"{ready} actions"
    line += f" for {reader}" if reader else ""
    return f"{line}, {waiting} more with other books" if waiting else line


def _other_faiths(character: Character, actions: list[str]) -> list[str]:
    """Those of `actions` that are some other faith's, not his."""
    own = faiths.faith(character).actions
    listed = {a for f in faiths.FAITHS.values() for a in f.actions}
    return [a for a in actions if a in listed and a not in own]


def _detail(
    interest: str, ready: list[str], waiting: list[str], others: list[str]
) -> str:
    """An interest's inspector: what it is, where each of its actions
    appears, those of other faiths, then those waiting for a book, under
    the book."""
    parts = [deeds.ABOUT[interest]]
    for heading, notes_of in (
        ("On the Religion chapter", deeds.RELIGION_NOTES),
        ("On the Deeds chapter", deeds.NOTES),
        ("On Planning, in A Season's Work", deeds.SEASON_NOTES),
    ):
        lines = [f"[b]{_name(a)}[/]: {notes_of[a]}" for a in ready if a in notes_of]
        if lines:
            parts.append("\n".join([f"[$label]{heading}[/]", *lines]))
    if others:
        names = ", ".join(_name(a) for a in others)
        parts.append(f"[dim]For other faiths: {names}.[/]")
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


def _card(saga: Saga, character: Character, interest: str) -> FormCard:
    members = deeds.members(interest)
    ready = [a for a in members if action_books.book_allows(a, saga)]
    waiting = [a for a in members if a not in ready]
    others: list[str] = []
    reader = ""
    if interest == deeds.RELIGION:
        others = _other_faiths(character, ready)
        ready = [a for a in ready if a not in others]
        reader = _FOR.get(faiths.religion(character), "their faith")
    detail = _detail(interest, ready, waiting, others)
    fixed = "" if interest in OPTIONAL else ALWAYS_ON
    if interest == deeds.RELIGION and faiths.church_career(character):
        fixed = CHURCH_CAREER
        detail = (
            "[$label]Their Church career keeps this on: its Holy Orders, "
            f"Petitions and Canon Court are on the Religion chapter.[/]\n\n{detail}"
        )
    return FormCard(
        "" if fixed else _key(interest),
        interest,
        deeds.SUMMARIES[interest],
        _count(len(ready), len(waiting), reader),
        detail,
        usable=bool(ready or others),
        fixed=fixed,
    )


def interest_cards(saga: Saga, character: Character) -> list[FormCard]:
    """A card for each interest, counting what the saga's books bring and,
    for Religion, what the character's faith offers; whether an action also
    fits the character changes in play, so it isn't counted."""
    return [_card(saga, character, interest) for interest in deeds.INTERESTS]


def interests_text(character: Character) -> str:
    """The interests he has turned off, in words."""
    off = [i for i in OPTIONAL if i in deeds.interests_off(character)]
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
            if not (i == deeds.RELIGION and faiths.church_career(character))
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        # An interest with no field here (kept on) stays as it was chosen.
        character.interests_off = [
            i
            for i in OPTIONAL
            if not values.get(_key(i), i not in character.interests_off)
        ]
        return notes(f"{character.name}: {interests_text(character)}")

    return Form(
        TITLE,
        fields,
        apply,
        help_id=HELP,
        cards=lambda: interest_cards(saga, character),
        cards_lead=LEAD,
    )
