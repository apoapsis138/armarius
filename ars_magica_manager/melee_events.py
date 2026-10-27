"""More's Melee Event on a character's Reputations: a roll on Lords of
Men's Melee Events Table for a tournament's grand charge (p. 68), and the
ransom fair from the knight it presents (p. 67), written in the Diary.
The rules are rules.tournament's.

Pattern: a commands.Form over the character, as Tournament is.
"""

from __future__ import annotations

import random
from typing import Any

from . import diaries
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, Saga
from .rules import dice, nobility, tournament

TITLE = "Melee Event"
HELP_ID = "melee-event"
SOURCE = "Lords of Men, The Grand Charge and Ransom, pp. 67-68"


def fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "events",
            "Events rolled this melee",
            "int",
            0,
            hint="One more botch die for each; each opponent past the first "
            "carries a Light Wound more.",
        ),
        DialogField(
            "confidence",
            "Confidence spent (+ or -)",
            "int",
            0,
            hint="Confidence may move the roll either way.",
        ),
        DialogField(
            "company",
            "With a company (one roll)",
            "check",
            False,
        ),
    ]


def live(character: Character) -> Any:
    def inspect(values: dict[str, Any]) -> str:
        bonus = nobility.prudhomme(character.reputations)
        events = int(values.get("events") or 0)
        return escape(
            f"Stress die + Prudhomme {bonus} + Confidence, "
            f"{tournament.melee_botch_dice(events)} botch dice."
        )

    return inspect


def roll(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    events = max(0, int(values.get("events") or 0))
    bonus = nobility.prudhomme(character.reputations) + int(
        values.get("confidence") or 0
    )
    die = dice.stress_die(rng, tournament.melee_botch_dice(events), saga=saga)
    total = die.value + bonus
    if die.botched:
        lines = [
            f"A botch ({die.botches}): an accident, a fall from the saddle, "
            "broken gear or an opponent badly hurt (p. 68)."
        ]
    else:
        line = tournament.melee_event(total)
        wounds = tournament.opponent_light_wounds(events + 1)
        lines = [
            f"{total} on the Melee Events Table: {line}",
            f"A fair ransom: {tournament.ransom_due(line)} (p. 67).",
        ]
        if wounds:
            lines.append(f"His opponents carry {wounds} short-term Light Wound(s).")
    who = "His company" if values.get("company") else character.name
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"{TITLE}: {who}",
        " ".join([*lines, f"Rules: {SOURCE}."]),
        characters=[character],
    )
    return notes(*map(escape, lines))


def melee_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: fields(character),
        lambda values: roll(saga, character, values, random.Random()),
        live=live(character),
        save_label="Roll",
        help_id=HELP_ID,
    )
