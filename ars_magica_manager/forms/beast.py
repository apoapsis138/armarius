"""Commanding a tamed animal (rules.tamed): More's Command the Beast on an
animal's Personality Traits, where its Loyal trait is. Both front-ends
draw it."""

from __future__ import annotations

import random
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import Character, Saga
from ..rules import tamed

TITLE = "Command the Beast"


def _commanders(saga: Saga, animal: Character) -> list[tuple[str, str]]:
    """The characters who may command it: anyone with Intelligence (not
    another animal)."""
    return [
        (escape(c.name), c.id)
        for c in sorted(saga.characters, key=lambda c: c.name.casefold())
        if c is not animal and c.animal is None
    ]


def fields(saga: Saga, animal: Character) -> list[DialogField]:
    commanders = _commanders(saga, animal)
    return [
        DialogField(
            "commander",
            "Commanded by",
            "select",
            commanders[0][1] if commanders else None,
            options=commanders,
            required=True,
            hint="Someone it is loyal to, or with Animal Handling; it obeys "
            "the one it is loyal to first (DE p. 386).",
        ),
        DialogField(
            "ability",
            "With",
            "select",
            tamed.COMMAND_ABILITIES[0],
            options=pairs(tamed.COMMAND_ABILITIES),
            hint="Ride for a mount; Magic Lore for a tamed elemental and the like.",
        ),
        DialogField(
            "task",
            "The task",
            "select",
            "unusual",
            options=[
                (
                    t.label
                    + (f" (Ease Factor {t.ease})" if t.ease is not None else ""),
                    key,
                )
                for key, t in tamed.TASKS.items()
            ],
        ),
    ]


def command_form(saga: Saga, animal: Character) -> Command:
    """Roll a command to a tamed animal, and any Loyalty test it asks."""
    if animal.animal is None:
        return Refuse(TITLE, f"{animal.name} isn't an animal.")
    if not _commanders(saga, animal):
        return Refuse(TITLE, "No one in the saga can command it.")

    def apply(values: dict[str, Any]) -> list[str]:
        commander = saga.character(values.get("commander"))
        if commander is None:
            return notes("Choose who commands it.")
        return notes(
            *tamed.command(
                saga,
                commander,
                animal,
                values.get("task") or "unusual",
                values.get("ability") or tamed.COMMAND_ABILITIES[0],
                random.Random(),
            )
        )

    def inspect(values: dict[str, Any]) -> str:
        commander = saga.character(values.get("commander"))
        if commander is None:
            return ""
        ability = values.get("ability") or tamed.COMMAND_ABILITIES[0]
        task = tamed.TASKS.get(values.get("task") or "unusual")
        total = tamed.command_total(commander, ability)
        line = f"Presence + {ability}: {total:+d} + stress die"
        if task is not None and task.ease is not None:
            line += f" against {task.ease}"
        if task is not None and task.loyalty is not None:
            line += (
                f"; then a Loyalty test (Loyal {tamed.loyalty(animal):+d} + "
                f"stress die) against {task.loyalty}"
            )
        return line + " (DE p. 386)."

    return Form(
        f"{TITLE}: {escape(animal.name)}",
        lambda: fields(saga, animal),
        apply,
        live=inspect,
        save_label="Roll",
        help_id="command-beast",
    )
