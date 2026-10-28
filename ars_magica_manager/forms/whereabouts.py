"""More's Current Location on a character's Casting Scores: where he is now,
when away from home, so his casting counts that place's aura, a foreign
realm's included (DE pp. 410-411). A place of the saga gives its aura; one
not kept is typed in. His seasons, aging and warping stay at home.

Pattern: a commands.Form over the character.
"""

from __future__ import annotations

from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import Character, Saga
from ..rules import realms, sites

TITLE = "Current Location"
HELP_ID = "whereabouts"
HOME, PLACE, TYPED = "home", "place", "typed"


def fields(saga: Saga, character: Character) -> list[DialogField]:
    places = [(escape(p.name), p.id) for p in sites.all_places(saga)]
    if character.away_place_id:
        where = PLACE
    elif character.away_aura is not None:
        where = TYPED
    else:
        where = HOME
    return [
        DialogField(
            "where",
            "Location",
            "select",
            where,
            options=[
                ("At home (the covenant's aura)", HOME),
                *([("At a place of the saga", PLACE)] if places else []),
                ("Somewhere else (type its aura)", TYPED),
            ],
        ),
        DialogField(
            "place",
            "The place",
            "select",
            character.away_place_id or (places[0][1] if places else None),
            options=places,
            show_if=lambda v: v.get("where") == PLACE,
        ),
        DialogField(
            "aura",
            "Its aura",
            "int",
            character.away_aura if character.away_aura is not None else 0,
            show_if=lambda v: v.get("where") == TYPED,
        ),
        DialogField(
            "realm",
            "Of the realm",
            "select",
            character.away_realm or realms.HERMETIC,
            options=pairs(realms.REALMS),
            show_if=lambda v: v.get("where") == TYPED,
        ),
    ]


def apply(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    where = values.get("where") or HOME
    character.away_place_id = str(values.get("place") or "") if where == PLACE else ""
    character.away_aura = int(values.get("aura") or 0) if where == TYPED else None
    character.away_realm = str(values.get("realm") or "") if where == TYPED else ""
    aura, realm = realms.present_aura(saga, character)
    if where == HOME:
        return notes(f"{escape(character.name)} is at home: {realm} aura {aura}.")
    return notes(
        f"{escape(character.name)} is away: casting there counts a {realm} aura of "
        f"{aura} (DE pp. 410-411)."
    )


def where_line(saga: Saga, character: Character) -> str:
    """Where the character is now and the aura his casting counts there
    (markup), as the top of his Hermetic Magic shows it."""
    aura, realm = realms.present_aura(saga, character)
    if character.away_place_id:
        place = sites.place(saga, character.away_place_id)
        where = f"Away, at {escape(place.name)}" if place else "Away"
    elif character.away_aura is not None:
        where = "Away from home"
    else:
        covenant = saga.covenant(character.covenant_id)
        where = f"At home, at {escape(covenant.name)}" if covenant else "At home"
    return f"{where}: a {realm} aura of {aura}."


def where_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: fields(saga, character),
        lambda values: apply(saga, character, values),
        help_id=HELP_ID,
    )
