"""A grog's animal form, independent of how it is drawn: whether the
grog is an animal, its kind, species and Language, its Size and, for a
species with its own, its average lifespan (rules.animal_grogs). Saving
an animal form gives the grog what every animal has: Restricted
Learning, No Hands and Mute (held free), and its Language at 2 on the
Creation Worksheet.
"""

from __future__ import annotations

from typing import Any

from .. import creation
from ..commands import Form
from ..form_spec import DialogField
from ..markup import escape
from ..models import AnimalForm, Character, CreationXp, Saga, VirtueFlawInstance
from ..rules import animal_aging
from ..rules import animal_grogs as ag

#: The Kind select's value for a person.
PERSON = "person"


def _animal(values: dict[str, Any]) -> bool:
    return values.get("kind", PERSON) != PERSON


def animal_fields(character: Character) -> list[DialogField]:
    """Kind (or a person), species, Language, average lifespan and Size."""
    animal = character.animal
    return [
        DialogField(
            "kind",
            "Kind",
            "select",
            animal.kind if animal is not None else PERSON,
            options=[("A person, not an animal", PERSON)]
            + [(escape(name), key) for name, key in ag.kind_options()],
        ),
        DialogField(
            "species",
            "Species",
            "text",
            animal.species if animal is not None else "",
            placeholder="e.g. Dog",
            show_if=_animal,
        ),
        DialogField(
            "language",
            "Its Language",
            "text",
            animal.language if animal is not None else "",
            placeholder="blank: the species (Dog, Horse)",
            hint="Its kind's own Language: 2, and never raised.",
            show_if=_animal,
        ),
        DialogField(
            "lifespan",
            "Average lifespan",
            "optint",
            animal.lifespan if animal is not None else None,
            placeholder="blank: its kind's",
            hint="Years. A species of its own scales its aging from the human 50.",
            show_if=_animal,
        ),
        DialogField(
            "size",
            "Size",
            "int",
            character.background.size,
            hint="Before Large or Small Frame: -3 (cat-sized) to +2 (horse-sized).",
            show_if=_animal,
        ),
    ]


def animal_problem(values: dict[str, Any]) -> str | None:
    """Why the values can't be saved: an animal needs its species, and a
    lifespan is a year or more."""
    if not _animal(values):
        return None
    if not str(values.get("species") or "").strip():
        return "Name the species (Dog, Horse, Hawk)."
    lifespan = values.get("lifespan")
    if lifespan is not None and lifespan < 1:
        return "An average lifespan is at least a year."
    return None


def animal_from(values: dict[str, Any]) -> AnimalForm | None:
    """The values as an AnimalForm; None for a person."""
    if not _animal(values):
        return None
    species = str(values.get("species") or "").strip()
    language = str(values.get("language") or "").strip() or species
    return AnimalForm(values["kind"], species, language, values.get("lifespan"))


def animal_live(values: dict[str, Any]) -> str:
    """The kind's aging and its Presence and Communication with humans."""
    animal = animal_from(values)
    if animal is None:
        return "[dim]A person: the usual Native Language and Early Childhood.[/]"
    kind = ag.KINDS[animal.kind]
    found = animal_aging.kind_figures(animal.kind, animal.lifespan)
    sample = Character(id="", name="", type="grog", animal=animal)
    return "\n".join(
        [
            escape(
                f"{ag.describe(animal)}: grown at {found.grown} "
                f"(120 xp, then 15 a year); "
                f"{animal_aging.schedule_text(sample)}."
            ),
            escape(
                f"With humans: Presence {kind.presence:+d}, "
                f"Communication {kind.communication:+d}."
            ),
        ]
    )


def apply_animal(character: Character, values: dict[str, Any]) -> None:
    """Make the grog the animal the values say (or a person again); an
    animal takes Restricted Learning, No Hands and Mute if it lacks them,
    and while In Creation its Language's 2 on the worksheet."""
    animal = animal_from(values)
    character.animal = animal
    if animal is None:
        # A person again: a person has no Pre-adult Life step, so its xp
        # is taken back rather than left where the worksheet can't show it.
        for entry in [x for x in character.creation_xp if x.step == "youth"]:
            creation.refund_creation_xp(character, entry)
        return
    character.background.size = int(values.get("size") or 0)
    held = {vf.vf_id for vf in character.virtues_flaws}
    for vf_id in (ag.RESTRICTED_LEARNING, *ag.FREE_FLAWS):
        if vf_id not in held:
            character.virtues_flaws.append(VirtueFlawInstance(vf_id))
    if character.in_creation and animal.language:
        set_language(character, animal.language)


def set_language(character: Character, language: str) -> None:
    """The animal Language's fixed 15 xp on the Pre-adult Life step,
    renamed if the Language was."""
    found = language_entry(character)
    if found is None:
        creation.spend_creation_xp(
            character, CreationXp("youth", language, ag.LANGUAGE_XP, ag.LANGUAGE_NOTE)
        )
    elif found.target != language:
        creation.change_creation_xp(character, found, language, ag.LANGUAGE_XP)


def language_entry(character: Character) -> CreationXp | None:
    return next(
        (
            x
            for x in character.creation_xp
            if x.step == "youth" and x.note == ag.LANGUAGE_NOTE
        ),
        None,
    )


def animal_form(saga: Saga, character: Character) -> Form:
    """Edit whether the grog is an animal, and which."""
    return Form(
        "Animal Form",
        lambda: animal_fields(character),
        lambda values: apply_animal(character, values),
        validate=animal_problem,
        live=animal_live,
        help_id="animal-grogs",
    )
