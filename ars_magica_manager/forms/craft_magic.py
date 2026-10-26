"""More's Craft by Magic on a magus's Known Spells: the Finesse roll a
Rego or Creo craft spell needs, its Ease Factor from the Definitive
Edition's table, and a roll of it -- no UI in here, and nothing kept.
The rules and their pages are rules.craft_magic's (DE pp. 306-308)."""

from __future__ import annotations

import random
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import BULLET, escape
from ..models import Character, Saga
from ..rules import craft_magic as cm
from ..rules import dice

TITLE = "Craft by Magic"
HELP_ID = "craft-magic"
#: The task's Ease Factor typed in: a mundane craftsman's, or a City &
#: Guild Workshop Total.
TYPED = "typed"


def _is(technique: str):
    return lambda values: values.get("technique", cm.REGO) == technique


def _elaborate(values: dict[str, Any]) -> bool:
    return (
        values.get("technique", cm.REGO) == cm.REGO
        or values.get("detail") == cm.ELABORATE
    )


def craft_fields() -> list[DialogField]:
    """What Craft by Magic asks."""
    tasks = [(f"{name} ({ease}): {what}", name) for name, ease, what in cm.CRAFT_TASKS]
    tasks.append(("A mundane Ease Factor or Workshop Total, typed", TYPED))
    return [
        DialogField(
            "technique",
            "Technique",
            "select",
            cm.REGO,
            options=pairs(cm.TECHNIQUES),
            hint="Rego shapes raw materials (Perception + Finesse); Creo makes the "
            "thing from nothing (Intelligence + Finesse).",
        ),
        DialogField(
            "detail",
            "Details to fix",
            "select",
            cm.SINGLE,
            options=[
                (f"{name} ({ease})" if ease is not None else name, name)
                for name, ease in cm.CREO_DETAILS
            ],
            hint=f"With no roll it makes a working example (as Ease Factor "
            f"{cm.UNROLLED_CREO_EASE}), its details as chance falls.",
            show_if=_is(cm.CREO),
        ),
        DialogField(
            "task",
            "The work",
            "select",
            "Average",
            options=tasks,
            hint="The Ease Factors for Creating and Crafting Objects (DE p. 308), "
            "the +3 for magic included. For several tasks, the hardest.",
            show_if=_elaborate,
        ),
        DialogField(
            "mundane",
            "Mundane Ease Factor or Workshop Total",
            "int",
            9,
            hint="+3 for magic is added.",
            show_if=lambda v: _elaborate(v) and v.get("task") == TYPED,
        ),
        DialogField(
            "time",
            "Work for one craftsman",
            "select",
            "A day",
            options=[(f"{name} (+{ease})", name) for name, ease in cm.CRAFT_TIMES],
            hint="A month is also thirty craftsmen for a day.",
            show_if=_elaborate,
        ),
        DialogField(
            "precise",
            "Precise Casting on the spell",
            "int",
            0,
            hint="A mastered spell's Precise Casting adds to its Finesse rolls.",
        ),
    ]


def ease_of(values: dict[str, Any]) -> int:
    """The Ease Factor the choices give."""
    technique = values.get("technique") or cm.REGO
    time = str(values.get("time") or "A day")
    task = str(values.get("task") or "Average")
    if technique == cm.CREO and values.get("detail") != cm.ELABORATE:
        return cm.creo_ease(str(values.get("detail") or cm.SINGLE))
    if task == TYPED:
        mundane = values.get("mundane")
        return cm.mundane_ease(mundane if isinstance(mundane, int) else 0, time)
    return cm.task_ease(task, time)


def _base(magus: Character, values: dict[str, Any]) -> int:
    precise = values.get("precise")
    return cm.roll_base(
        magus,
        str(values.get("technique") or cm.REGO),
        precise if isinstance(precise, int) else 0,
    )


def lines(magus: Character, values: dict[str, Any]) -> list[str]:
    """What the roll is, plain."""
    technique = str(values.get("technique") or cm.REGO)
    base = _base(magus, values)
    ease = ease_of(values)
    said = [
        f"{cm.characteristic(technique)} + Finesse {base:+d} + stress die "
        f"against {ease}: the die must reach {cm.needed(base, ease)}.",
    ]
    flaws = cm.penalty_names(magus)
    if flaws:
        said.append(f"With {' and '.join(flaws)}: -3 each.")
    said.append(f"Then {cm.failure(technique)}.")
    return said


def _live(magus: Character):
    def live(values: dict[str, Any]) -> str:
        return "\n".join(f"{BULLET} {escape(line)}" for line in lines(magus, values))

    return live


def roll(
    saga: Saga, magus: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The roll, said: nothing is kept."""
    base = _base(magus, values)
    ease = ease_of(values)
    rolled = dice.roll(rng, base, ease_factor=ease, saga=saga)
    if rolled.die.botched:
        verdict = "botched"
    elif rolled.succeeded:
        verdict = "succeeds"
    else:
        verdict = "fails"
    return notes(
        f"Finesse {base:+d} + {rolled.die.value} = {rolled.total} against {ease}: "
        f"{verdict}.",
        f"On a failure {cm.failure(str(values.get('technique') or cm.REGO))}."
        if verdict != "succeeds"
        else "",
    )


def craft_form(
    saga: Saga, magus: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Craft by Magic: the calculator; Roll rolls it once."""
    if magus is None or magus.type != "magus":
        return Refuse(TITLE, "Only a magus crafts with Hermetic magic.")
    chance = rng or random.Random()
    caster = magus
    return Form(
        f"{TITLE}: {escape(caster.name)}",
        craft_fields,
        lambda values: roll(saga, caster, values, chance),
        live=_live(caster),
        save_label="Roll",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Finesse Roll",
    )
