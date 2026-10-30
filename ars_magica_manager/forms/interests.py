"""Interests: the kinds of deed a character takes up, ticked on the
Manage chapter, More on the record, or the Creation Worksheet's Review
Interests -- no UI in here.

An interest left unticked hides its actions (deeds.INTEREST_OF) from the
Deeds chapter, A Season's Work and More; the rules still decide what a
ticked interest offers."""

from __future__ import annotations

from typing import Any

from ..commands import Form, notes
from ..deeds import OPTIONAL
from ..form_spec import DialogField
from ..models import Character, Saga

TITLE = "Interests"
HELP = "interests"


def _key(interest: str) -> str:
    return "interest_" + "".join(c if c.isalnum() else "_" for c in interest.lower())


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
            DialogField(_key(i), i, "check", value=i not in character.interests_off)
            for i in OPTIONAL
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        character.interests_off = [i for i in OPTIONAL if not values.get(_key(i))]
        return notes(f"{character.name}: {interests_text(character)}")

    return Form(TITLE, fields, apply, help_id=HELP)
