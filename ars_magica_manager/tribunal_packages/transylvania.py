"""The Transylvanian Tribunal's customs (Against the Dark: The
Transylvanian Tribunal): each covenant holds one of five privilege
classes, which say what its magi may do: stand for office, take
apprentices, trade vis.

Kept in the package's data: "classes", {covenant id: class}. The roster
gains a Class column, entered through its Edit."""

from __future__ import annotations

from typing import Any

from ..form_spec import DialogField
from ..models import Covenant, Saga, Tribunal
from . import RosterColumn, TribunalPackage, data, register

KEY = "transylvania"

#: The privilege classes, each with the covenant whose class it is in
#: the book, and what it allows.
CLASSES: dict[str, str] = {
    "Cives": "any office, Praeco too; apprentices; chooses an aedile",
    "Socii": "any office but Praeco; must not provoke Wizard War",
    "Coloniae": "settlers: no office but aedile; apprentices by leave",
    "Hospites": "hired specialists: office, apprentices and more by leave",
    "Foederati": "keep their own customs; trade with outsiders by leave",
}


def classes(tribunal: Tribunal) -> dict[str, str]:
    """Each covenant's privilege class, by covenant id."""
    found = data(tribunal, KEY).setdefault("classes", {})
    assert isinstance(found, dict)
    return found


def class_of(_saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """The covenant's privilege class, or "" if none is entered."""
    return classes(tribunal).get(covenant.id, "")


def class_field(_saga: Saga, tribunal: Tribunal, covenant: Covenant) -> DialogField:
    return DialogField(
        "privilege",
        "Privilege class",
        "select",
        classes(tribunal).get(covenant.id),
        options=[(f"{name}: {allows}", name) for name, allows in CLASSES.items()],
        allow_blank=True,
        placeholder="(not entered)",
        hint="What its magi may do in the Tribunal.",
    )


def save_class(tribunal: Tribunal, covenant: Covenant, value: Any) -> None:
    if value:
        classes(tribunal)[covenant.id] = value
    else:
        classes(tribunal).pop(covenant.id, None)


TRANSYLVANIA = TribunalPackage(
    KEY,
    "Transylvania",
    customs="Privileges",
    book="AtD",
    columns=(RosterColumn("Class", class_of, 9, class_field, save_class),),
    about="Each covenant holds one of five privilege classes (cives, socii, "
    "coloniae, hospites, foederati), which say what its magi may do.",
)

register(TRANSYLVANIA)
