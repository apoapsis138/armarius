"""More's Roll on Personality Traits: a Personality Trait roll, a roll to
resist mental influence, or the familiar's rescue of a mind overcome,
each with the bond's Silver Cord added (DE p. 267). Results are shown,
not kept. Both the magus's and the familiar's sheets offer it.

Pattern: ROLLS is a dict from a kind of roll to the function that rolls
it (Strategy, reduced to a dict of functions), as Combat Options is; a
later bonus (Strong-Willed, Confidence) is one more term in a roll.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from .. import table_rolls
from ..commands import Form, notes
from ..dice_text import RolledOrTyped, dice_line, value_of
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Familiar, Saga
from ..rules import dice

TITLE = "Roll"
HELP_ID = "trait-roll"
SOURCE = "Ars Magica Definitive Edition, The Three Cords, p. 267"
#: The familiar's rescue of a mind overcome: 9+ on a stress die + the
#: Silver Cord, one try a day; a botch overcomes its mind too (p. 267).
RESCUE_EASE = 9

TRAIT, RESIST, RESCUE = "trait", "resist", "rescue"
KINDS: list[tuple[str, str]] = [
    ("A Personality Trait roll", TRAIT),
    ("Resisting mental influence", RESIST),
    ("The familiar frees a mind overcome", RESCUE),
]

Bearer = Character | Familiar


def silver_cord(saga: Saga, bearer: Bearer) -> int:
    """The Silver Cord a magus or his familiar adds: the bond's, 0 with
    none."""
    if isinstance(bearer, Familiar):
        return bearer.silver_cord
    familiar = saga.familiar_of(bearer.id)
    return familiar.silver_cord if familiar is not None else 0


def _traits(bearer: Bearer) -> list[tuple[str, str]]:
    return [
        (f"{escape(t.name)} {t.score:+d}", str(i))
        for i, t in enumerate(bearer.personality_traits)
    ]


def fields(saga: Saga, bearer: Bearer) -> list[DialogField]:
    traits = _traits(bearer)
    kinds = [k for k in KINDS if k[1] != RESCUE or silver_cord(saga, bearer)]
    return [
        DialogField("kind", "Roll", "select", TRAIT, options=kinds),
        DialogField(
            "trait",
            "Personality Trait",
            "select",
            traits[0][1] if traits else None,
            options=traits,
            allow_blank=True,
            placeholder="(none)",
            show_if=lambda v: v.get("kind") == TRAIT,
        ),
        DialogField(
            "score",
            "The roll's own total",
            "int",
            0,
            show_if=lambda v: v.get("kind") == RESIST,
            hint="What the rules for the influence add (a Characteristic, a "
            "trait, a Form bonus): the Silver Cord is added to it.",
        ),
        DialogField(
            "ease",
            "Ease Factor",
            "int",
            6,
            show_if=lambda v: v.get("kind") in (TRAIT, RESIST),
        ),
        DialogField("die", "Stress die", "optint", None, hint="Blank: rolled."),
    ]


def _trait_score(bearer: Bearer, values: dict[str, Any]) -> tuple[str, int]:
    raw = values.get("trait")
    if raw is None or not str(raw).isdigit():
        return "", 0
    index = int(raw)
    if not 0 <= index < len(bearer.personality_traits):
        return "", 0
    trait = bearer.personality_traits[index]
    return trait.name, trait.score


def _roll_trait(
    saga: Saga, bearer: Bearer, values: dict[str, Any], die: RolledOrTyped
) -> str:
    name, score = _trait_score(bearer, values)
    cord = silver_cord(saga, bearer)
    total = score + cord + value_of(die)
    ease = values.get("ease") or 0
    terms = [(name or "Personality Trait", score), ("Silver Cord", cord)]
    return f"{dice_line(die, terms, total, ease)}. " + (
        "It holds." if total >= ease else "It fails."
    )


def _roll_resist(
    saga: Saga, bearer: Bearer, values: dict[str, Any], die: RolledOrTyped
) -> str:
    own = values.get("score") or 0
    cord = silver_cord(saga, bearer)
    total = own + cord + value_of(die)
    ease = values.get("ease") or 0
    terms = [("Own total", own), ("Silver Cord", cord)]
    return f"Resisting: {dice_line(die, terms, total, ease)}. " + (
        "Resisted." if total >= ease else "Overcome."
    )


def _roll_rescue(
    saga: Saga, bearer: Bearer, _values: dict[str, Any], die: RolledOrTyped
) -> str:
    cord = silver_cord(saga, bearer)
    total = cord + value_of(die)
    line = dice_line(die, [("Silver Cord", cord)], total, RESCUE_EASE)
    return f"The familiar's rescue: {line}. " + (
        "The mind is freed." if total >= RESCUE_EASE else "Not today: try tomorrow."
    )


#: Each kind of roll and what it does with the die.
ROLLS: dict[str, Callable[[Saga, Bearer, dict[str, Any], RolledOrTyped], str]] = {
    TRAIT: _roll_trait,
    RESIST: _roll_resist,
    RESCUE: _roll_rescue,
}


def live(saga: Saga, bearer: Bearer, values: dict[str, Any]) -> str:
    cord = silver_cord(saga, bearer)
    return (
        f"[$label]Silver Cord[/] +{cord} to this roll (DE p. 267)"
        if cord
        else "[dim]No bound familiar's Silver Cord to add.[/]"
    )


def roll_form(saga: Saga, bearer: Bearer, rng: random.Random | None = None) -> Form:
    dice_ = rng or table_rolls.dice()

    def apply(values: dict[str, Any]) -> list[str]:
        typed = values.get("die")
        rolled = dice.stress_die(dice_, 1, saga=saga) if typed is None else None
        if rolled is not None and rolled.botched:
            kind = values.get("kind") or TRAIT
            return notes(
                escape(
                    "A botch: the familiar's mind is overcome too."
                    if kind == RESCUE
                    else "A botch."
                )
            )
        die: RolledOrTyped = typed if typed is not None else (rolled or 0)
        kind = values.get("kind") or TRAIT
        return notes(escape(ROLLS[kind](saga, bearer, values, die)))

    return table_rolls.form(
        Form(
            f"{TITLE}: {escape(bearer.name or 'the familiar')}",
            lambda: fields(saga, bearer),
            apply,
            live=lambda values: live(saga, bearer, values),
            save_label="Roll",
            help_id=HELP_ID,
        ),
        saga,
        character_id=bearer.id if isinstance(bearer, Character) else "",
        typed=("die",),
    )
