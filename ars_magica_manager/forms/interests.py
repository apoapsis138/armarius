"""Interests: the kinds of deed a character takes up, chosen on the
Manage chapter, More on the record, or the Creation Worksheet's Review
Interests -- no UI in here.

An interest left unticked hides its actions (deeds.INTEREST_OF) from the
Deeds chapter, A Season's Work and More; the rules still decide what a
ticked interest offers. The desktop draws the form as cards (FormCard),
each counting the actions the saga's books bring and its inspector saying
where they are; those places come from deeds' tables, so they can't drift."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .. import action_books, deeds, default_interests, sourcebooks
from ..commands import Act, Form, FormCard, notes
from ..deeds import OPTIONAL
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Covenant, Saga
from ..rules import faiths

TITLE = "Interests"
HELP = "interests"
#: The reminder a worksheet and these windows give.
REMINDER = (
    "You can change these at any time, on the Manage chapter, as {}'s "
    "interests grow and change."
)
LEAD = (
    "The kinds of deed this character takes up. Unticked interests leave the "
    "sheet; choose a card to see what it adds. "
) + REMINDER.format("the character")
COVENANT_LEAD = (
    "What this covenant takes up. Unticked interests leave its sheet; choose "
    "a card to see what it adds. "
) + REMINDER.format("the covenant")
#: Where a card that can't be turned off has a switch.
ALWAYS_ON = "Always on"
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
    names: Mapping[str, str],
    interest: str,
    ready: list[str],
    waiting: list[str],
    others: list[str],
) -> str:
    """An interest's inspector: what it is, where each of its actions
    appears, those of other faiths, then those waiting for a book, under
    the book."""
    parts = [deeds.ABOUT[interest]]
    for heading, notes_of in (
        ("On the Religion chapter", deeds.RELIGION_NOTES),
        ("On the Agents chapter", deeds.AGENT_NOTES),
        ("On the Hermetic Magic chapter", deeds.HERMETIC_NOTES),
        ("On the Deeds chapter", deeds.NOTES),
        ("On Planning, in A Season's Work", deeds.SEASON_NOTES),
        ("Under Aging", deeds.AGING_NOTES),
    ):
        lines = [f"[b]{names[a]}[/]: {notes_of[a]}" for a in ready if a in notes_of]
        if lines:
            parts.append("\n".join([f"[$label]{heading}[/]", *lines]))
    if others:
        listed = ", ".join(names[a] for a in others)
        parts.append(f"[dim]For other faiths: {listed}.[/]")
    books: dict[str, list[str]] = {}
    for action in waiting:
        titles = [
            sourcebooks.SOURCEBOOKS[book] for book in action_books.ACTION_BOOKS[action]
        ]
        books.setdefault(" or ".join(titles), []).append(names[action])
    parts += [
        f"[dim]With {book}: {', '.join(labels)}.[/]" for book, labels in books.items()
    ]
    return "\n\n".join(parts)


def _card(
    saga: Saga, character: Character, interest: str, names: Mapping[str, str]
) -> FormCard:
    members = deeds.members(interest)
    ready = [a for a in members if action_books.book_allows(a, saga)]
    waiting = [a for a in members if a not in ready]
    others: list[str] = []
    reader = ""
    if interest == deeds.RELIGION:
        others = _other_faiths(character, ready)
        ready = [a for a in ready if a not in others]
        reader = _FOR.get(faiths.religion(character), "their faith")
    detail = _detail(names, interest, ready, waiting, others)
    fixed = "" if interest in OPTIONAL else ALWAYS_ON
    gate = deeds.CHARACTER_GATES.get(interest)
    if gate is not None and gate.kept_on(character):
        fixed = gate.fixed
        detail = f"[$label]{gate.why}[/]\n\n{detail}"
    return FormCard(
        "" if fixed else _key(interest),
        interest,
        deeds.SUMMARIES[interest],
        _count(len(ready), len(waiting), reader)
        if members
        else f"The {interest} chapter",
        detail,
        usable=bool(ready or others) or gate is not None,
        fixed=fixed,
    )


def interest_cards(
    saga: Saga, character: Character, names: Mapping[str, str]
) -> list[FormCard]:
    """A card for each interest, counting what the saga's books bring and,
    for Religion, what the character's faith offers; whether an action also
    fits the character changes in play, so it isn't counted."""
    return [
        _card(saga, character, interest, names)
        for interest in deeds.INTERESTS
        if deeds.applies(character, interest)
    ]


def _covenant_card(
    saga: Saga, covenant: Covenant, interest: str, names: Mapping[str, str]
) -> FormCard:
    heading, notes_of = deeds.COVENANT_ACTIONS[interest]
    ready = [a for a in notes_of if action_books.book_allows(a, saga)]
    lines = [f"[b]{names[a]}[/]: {notes_of[a]}" for a in ready]
    detail = f"{deeds.COVENANT_ABOUT[interest]}\n\n[$label]{heading}[/]\n" + (
        "\n".join(lines)
    )
    gate = deeds.COVENANT_GATES[interest]
    fixed = gate.fixed if gate.kept_on(covenant) else ""
    if fixed:
        detail = f"[$label]{gate.why}[/]\n\n{detail}"
    return FormCard(
        "" if fixed else _key(interest),
        interest,
        deeds.COVENANT_SUMMARIES[interest],
        _count(len(ready), len(notes_of) - len(ready)),
        detail,
        usable=bool(ready) or bool(fixed),
        fixed=fixed,
    )


def covenant_interests_text(covenant: Covenant) -> str:
    """The interests it has turned off, in words."""
    off = deeds.covenant_interests_off(covenant)
    if not off:
        return "Every interest is ticked."
    return "Turned off: " + ", ".join(off) + "."


def covenant_interests_form(
    saga: Saga, covenant: Covenant, names: Mapping[str, str]
) -> Form:
    """A tick for each interest the covenant may turn off."""
    gates = deeds.COVENANT_GATES

    def fields() -> list[DialogField]:
        return [
            DialogField(
                _key(i),
                i,
                "check",
                value=i not in covenant.interests_off,
                hint=deeds.COVENANT_SUMMARIES[i],
            )
            for i in deeds.COVENANT_INTERESTS
            if not gates[i].kept_on(covenant)
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        # An interest with no field here (kept on) stays as it was chosen.
        covenant.interests_off = [
            i
            for i in deeds.COVENANT_INTERESTS
            if not values.get(_key(i), i not in covenant.interests_off)
        ]
        return notes(f"{escape(covenant.name)}: {covenant_interests_text(covenant)}")

    return Form(
        TITLE,
        fields,
        apply,
        help_id=HELP,
        cards=lambda: [
            _covenant_card(saga, covenant, i, names) for i in deeds.COVENANT_INTERESTS
        ],
        cards_lead=COVENANT_LEAD,
    )


def interests_text(character: Character) -> str:
    """Which of `character`'s interests are on, in words: those turned off,
    or those on when they're fewer."""
    off = deeds.interests_off(character)
    shown_off = [i for i in OPTIONAL if i in off and deeds.applies(character, i)]
    if not shown_off:
        return "Every interest is ticked."
    on = deeds.interests_on(character)
    if not on:
        return f"Only {deeds.SESSION} is on."
    if len(on) < len(shown_off):
        return "On: " + ", ".join(on) + ". The rest are off."
    return "Turned off: " + ", ".join(shown_off) + "."


def defaults_text(character: Character) -> str:
    """`character`'s Default Interests besides Session & Reputation, a line
    for each source ("From being a magus: Research, Tribunal & Order."),
    its interests in the order of the cards (deeds.INTERESTS)."""
    by_source: dict[str, set[str]] = {}
    for interest, why in default_interests.defaults(character):
        if interest != default_interests.SESSION:
            by_source.setdefault(why, set()).add(interest)
    lines = [
        f"From {escape(_source(why))}: "
        f"{', '.join(i for i in OPTIONAL if i in interests)}."
        for why, interests in by_source.items()
    ]
    return "\n".join(lines) or "None."


def whose_text(character: Character) -> str:
    """Whether `character`'s interests are still its Default Interests or
    the player's own."""
    if deeds.following_defaults(character):
        return (
            "These are the defaults: they follow the character's type, House "
            "and Virtues and Flaws until Edit Interests is saved."
        )
    if character.in_creation:
        return (
            "These are the player's own. Restore the defaults hands them back "
            "to the defaults."
        )
    return "These are the player's own."


def restore_defaults(character: Character) -> Act:
    """The Restore the defaults button: hand the interests back to the
    Default Interests (deeds.follow_defaults), and say which are on now."""

    def apply() -> list[str]:
        deeds.follow_defaults(character)
        on = ", ".join(deeds.interests_on(character)) or f"only {deeds.SESSION}"
        return notes(f"{escape(character.name)} is back to the defaults: {on}.")

    return Act(apply, TITLE)


def _source(why: str) -> str:
    """A reason as its line names it: "being a magus", "House Merinita"."""
    return f"being {why}" if why.startswith(("a ", "an ")) else why


def interests_form(saga: Saga, character: Character, names: Mapping[str, str]) -> Form:
    """A tick for each interest the character may turn off, ticked as they
    are now (the Default Interests, until chosen). Saving makes the choice
    the player's."""

    def fields() -> list[DialogField]:
        off = deeds.turned_off(character)
        return [
            DialogField(
                _key(i),
                i,
                "check",
                value=i not in off,
                hint=deeds.SUMMARIES[i],
            )
            for i in OPTIONAL
            if deeds.applies(character, i)
            and not (
                i in deeds.CHARACTER_GATES
                and deeds.CHARACTER_GATES[i].kept_on(character)
            )
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        # An interest with no field here (kept on) stays as it was.
        off = deeds.turned_off(character)
        character.interests_off = [
            i for i in OPTIONAL if not values.get(_key(i), i not in off)
        ]
        character.interests_chosen = True
        return notes(f"{escape(character.name)}: {interests_text(character)}")

    return Form(
        TITLE,
        fields,
        apply,
        help_id=HELP,
        cards=lambda: interest_cards(saga, character, names),
        cards_lead=LEAD,
    )
