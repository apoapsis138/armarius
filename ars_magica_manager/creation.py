"""Creating the saga's top-level records: a new saga, and a covenant,
character or laboratory added to one. (A Familiar is bound with
familiars.bind_familiar.) Each takes the values a create form collects and
returns the new record; nothing here saves."""

from __future__ import annotations

from . import storage
from .models import Character, Covenant, LabCharacteristics, Laboratory, Saga


def new_saga(
    name: str, storyguide: str, description: str, year: int, season: str
) -> Saga:
    """A new, empty saga, with an id no saved saga uses."""
    return Saga(
        id=storage.generate_saga_id(name),
        name=name,
        storyguide=storyguide,
        description=description,
        current_year=year,
        current_season=season,
    )


def add_covenant(saga: Saga, name: str, notes: str = "") -> Covenant:
    covenant = Covenant(
        id=storage.generate_unique_id(name, [c.id for c in saga.covenants]),
        saga_id=saga.id,
        name=name,
        notes=notes,
    )
    saga.covenants.append(covenant)
    return covenant


def add_character(
    saga: Saga, name: str, character_type: str, covenant_id: str | None
) -> Character:
    character = Character(
        id=storage.generate_unique_id(name, [c.id for c in saga.characters]),
        name=name,
        type=character_type,
        covenant_id=covenant_id,
    )
    saga.characters.append(character)
    return character


def add_laboratory(
    saga: Saga, name: str, size: int, covenant_id: str | None
) -> Laboratory:
    laboratory = Laboratory(
        id=storage.generate_unique_id(name, [lab.id for lab in saga.laboratories]),
        covenant_id=covenant_id,
        name=name,
        characteristics=LabCharacteristics(size=size),
    )
    saga.laboratories.append(laboratory)
    return laboratory
