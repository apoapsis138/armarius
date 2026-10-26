"""More's Hubris on a Verditius's Personality Traits -- no UI in here: the
experience a behaviour adds to Hubris (DE p. 242; Houses of Hermes: Mystery
Cults p. 120), refusing a vendetta (p. 115) and resisting one (p. 120;
DE p. 242), and waging the vendetta once refused, which with the Hubris
regained loses the Reputation (p. 115). The rules and their pages are
rules.verditius'."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import Character, DiaryEntry, Saga
from ..rules import lab_virtues
from ..rules import verditius as vd
from ..rules.rounding import round_up

TITLE = "Hubris"
HELP = "verditius-hubris"
REFUSE, RESIST, WAGE = "refuse", "resist", "wage"
#: What the form offers: each behaviour of the Hubris table but learning an
#: Inner Mystery (the Initiation season adds that), and the vendettas.
CHOICES: tuple[tuple[str, str], ...] = (
    *(
        (f"{label} (+{xp})", label)
        for label, xp in vd.HUBRIS_XP.items()
        if not label.startswith("Learning")
    ),
    (vd.AUTOMATON, vd.AUTOMATON),
    ("Refuses a declared vendetta (Dishonorable 4, a point of Hubris lost)", REFUSE),
    ("Resists a declared vendetta (a roll)", RESIST),
)
WAGE_CHOICE = ("Wages the vendetta on a magus he refused", WAGE)


def _choices(character: Character) -> list[tuple[str, str]]:
    """The table's choices, and waging a refused vendetta when he has one."""
    return [*CHOICES, *([WAGE_CHOICE] if character.refused_vendettas else [])]


def _refused(character: Character) -> list[tuple[str, str]]:
    names = [r.magus for r in character.refused_vendettas if not r.waged]
    return [(name or "(unnamed)", name) for name in dict.fromkeys(names)]


def offers(_saga: Saga, character: Character) -> bool:
    """Whether More offers Hubris: a magus with the Flaw or the trait."""
    return (
        lab_virtues.has(character, vd.HUBRIS_FLAW)
        or vd.hubris_trait(character) is not None
    )


def _is(*keys: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: values.get("what") in keys


def hubris_fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "what",
            "What happened",
            "select",
            CHOICES[0][1],
            options=_choices(character),
        ),
        DialogField(
            "refused",
            "The magus refused",
            "text",
            "",
            show_if=_is(REFUSE),
            hint="Waging a vendetta on him later, with the Hubris regained, "
            "loses the Reputation.",
        ),
        DialogField(
            "target",
            "The magus once refused",
            "select",
            next(iter(_refused(character)), ("", ""))[1],
            options=_refused(character) or [("(none)", "")],
            show_if=_is(WAGE),
        ),
        DialogField(
            "might",
            "The automaton's Might",
            "int",
            0,
            show_if=_is(vd.AUTOMATON),
            hint="A point of experience a magnitude (5 points) of Might.",
        ),
        DialogField(
            "resisting",
            "The trait set against Hubris",
            "int",
            character.characteristics.intelligence,
            show_if=_is(RESIST),
            hint="A Personality Trait that works against Hubris, or her "
            "Intelligence without one; a stress die is added.",
        ),
        DialogField(
            "challenger",
            "The challenger's Hubris",
            "int",
            0,
            show_if=_is(RESIST),
        ),
    ]


def _experience(values: dict[str, Any]) -> int:
    what = str(values.get("what") or "")
    if what == vd.AUTOMATON:
        might = max(0, int(values.get("might") or 0))
        return vd.hubris_xp(vd.AUTOMATON, round_up(might / 5))
    return vd.HUBRIS_XP.get(what, 0)


def hubris_lines(character: Character, values: dict[str, Any]) -> list[str]:
    what = str(values.get("what") or "")
    own = vd.hubris_of(character)
    if what == RESIST:
        ease = vd.vendetta_ease(own, int(values.get("challenger") or 0))
        return [
            f"Trait + stress die against {ease} (Hubris {own} + the challenger's) "
            f"({vd.VENDETTA_SOURCE})."
        ]
    if what == REFUSE:
        return [
            f"Refusing: the House Reputation Dishonorable 4, and Hubris {own} "
            f"falls to {max(0, own - 1)} (the experience of the score below); "
            "regaining the score and waging a vendetta on the magus refused "
            f"lose the Reputation ({vd.VENDETTA_SOURCE})."
        ]
    if what == WAGE:
        return [
            *vd.refusal_lines(character),
            f"The Reputation goes once Hubris is regained too ({vd.VENDETTA_SOURCE}).",
        ]
    experience = _experience(values)
    return [
        f"+{experience} Hubris experience; Hubris {own} needs "
        f"{vd.xp_to_next_hubris(character)} more for its next point "
        f"({vd.HUBRIS_SOURCE})."
    ]


def _live(character: Character) -> Callable[[dict[str, Any]], str]:
    return lambda values: "\n".join(
        f"{BULLET} {escape(line)}" for line in hubris_lines(character, values)
    )


def record(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """What happened, kept on the sheet, with a Diary entry."""
    what = str(values.get("what") or "")
    if what == RESIST:
        _, said = vd.resist_vendetta(
            rng,
            int(values.get("resisting") or 0),
            vd.hubris_of(character),
            int(values.get("challenger") or 0),
            saga,
        )
        lines = [said]
        name = "Resisted a vendetta"
    elif what == REFUSE:
        lines = vd.refuse_vendetta(character, str(values.get("refused") or ""))
        name = "Refused a vendetta"
    elif what == WAGE:
        lines = vd.wage_refused_vendetta(character, str(values.get("target") or ""))
        name = "Waged a refused vendetta"
    else:
        start = 0 if vd.hubris_trait(character) else vd.starting_hubris(character)
        lines = [vd.gain_hubris(character, _experience(values), start)]
        lines += vd.settle_vendettas(character)
        name = "Hubris"
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            name,
            "\n".join([what if what not in (REFUSE, RESIST, WAGE) else name, *lines]),
        )
    )
    return notes(*lines)


def hubris_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Hubris: what happened; Save keeps its experience, or the
    refused vendetta, or rolls the resistance."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if not offers(saga, character):
        return Refuse(
            TITLE,
            "Hubris comes with a Verditius's first Inner Mystery (the Flaw "
            "Hubris; DE p. 241).",
        )
    chance = rng or random.Random()
    magus = character
    return Form(
        f"{TITLE}: {escape(magus.name)}",
        lambda: hubris_fields(magus),
        lambda values: record(saga, magus, values, chance),
        live=_live(magus),
        help_id=HELP,
    )
