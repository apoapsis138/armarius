"""Aging Points still to place: an aging roll's points "in any
Characteristic", which the player chooses (DE p. 392), and a disease
Crisis survived, which leaves one in a Characteristic the storyguide
chooses (Art & Academe p. 47). The form
asks for each; Advance Season asks for them before it plays the next
season, and More on Aging & Warping places them at any time -- no UI in
here."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, DiaryEntry, Saga
from .rules import aging as aging_rules

TITLE = "Place Aging Points"
#: The Characteristics an Aging Point may go into.
CHARACTERISTICS = (
    "intelligence",
    "perception",
    "presence",
    "communication",
    "strength",
    "stamina",
    "dexterity",
    "quickness",
)


def due(saga: Saga) -> list[Character]:
    """The characters with Aging Points still to place."""
    return [c for c in saga.characters if c.aging.aging_due]


def _key(character: Character, index: int) -> str:
    return f"point_{character.id}_{index}"


def fields(people: list[Character]) -> list[DialogField]:
    """A Characteristic to choose for each Aging Point due."""
    found: list[DialogField] = []
    for character in people:
        for index, why in enumerate(character.aging.aging_due):
            rolled = why.startswith(aging_rules.ANY_POINT)
            found.append(
                DialogField(
                    _key(character, index),
                    f"{escape(character.name)}: {escape(why)}",
                    "select",
                    _suggested(why),
                    options=[(name.title(), name) for name in CHARACTERISTICS],
                    hint="One Aging Point in any Characteristic, the player's "
                    "choice (DE p. 392)."
                    if rolled
                    else "One Aging Point in a fitting Characteristic, the "
                    "storyguide's choice (Art & Academe p. 47).",
                )
            )
    return found


def _suggested(why: str) -> str:
    """The Characteristic an Aging Point due is offered in first: the one
    its roll suggested, else Stamina."""
    _, found, rest = why.partition("(suggested: ")
    name = rest.rstrip(")").strip().lower() if found else ""
    return name if name in CHARACTERISTICS else "stamina"


def place(saga: Saga, people: list[Character], values: dict[str, Any]) -> list[str]:
    """Add each chosen Aging Point, in the Diary too, and clear them."""
    lines: list[str] = []
    for character in people:
        for index, why in enumerate(character.aging.aging_due):
            name = str(values.get(_key(character, index)) or _suggested(why))
            if why.startswith(aging_rules.ANY_POINT):
                # Its Decrepitude was counted with the roll.
                changed = aging_rules.place_points(character, name, 1)
            else:
                changed = aging_rules.add_points(character, name, 1)
            text = f"{why}: an Aging Point in {name.title()}." + (
                f" {' '.join(changed)}" if changed else ""
            )
            lines.append(f"{character.name}: {text}")
            character.diary.append(
                DiaryEntry(
                    saga.current_year,
                    saga.current_season,
                    "Aging Point",
                    text,
                    activity="Aging",
                )
            )
        character.aging.aging_due = []
    return notes(*lines)


def place_form(
    saga: Saga, people: list[Character], then: Callable[[], Any] | None = None
) -> Command:
    """The form; `then` runs after it is saved (Advance Season goes on)."""
    if not people:
        return Refuse(TITLE, "No Aging Points are due.")

    def apply(values: dict[str, Any]) -> Any:
        placed = place(saga, people, values)
        return then() if then is not None else placed

    return Form(
        TITLE,
        lambda: fields(people),
        apply,
        save_label="Place" if then is None else "Place and continue",
        help_id="aging-due",
    )


def character_form(saga: Saga, character: Character | None) -> Command:
    """More on Aging & Warping: one character's Aging Points due."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    return place_form(saga, [character] if character.aging.aging_due else [])
