"""Crafting with Hermetic magic: the Finesse roll a craft spell needs and
its Ease Factor.

- Rego craft magic shapes raw materials as a craftsman would: Perception
  + Finesse against the highest Ease Factor a mundane craftsman would need
  for the tasks the spell covers, + 3, + the time the work would take one
  craftsman (a day +0, a month +3, a season +6, a year +9; a month is also
  thirty craftsmen for a day). A failure rearranges the materials into
  nothing useful; a botch looks right but has a hidden, fatal flaw.
- Creo craft magic makes a working example of the thing (as a craft
  Ease Factor of 6) with no roll; to fix details, Intelligence + Finesse:
  one basic property 0, two or three (or one precisely) 3, an elaborate
  specification or a better-quality item as Rego craft magic. A botch
  makes something that hinders the caster.
- The Ease Factors for Creating and Crafting Objects already hold the +3
  for magic and a day's work; with City & Guild's Workshop Totals, the
  Ease Factor is the Workshop Total + 3, then the time.

Every Finesse roll also takes the Wound and Fatigue penalties, -3 for
each of Clumsy and Inconstant Magic, and a mastered spell's Precise
Casting (rules.casting.aiming_base, which is the same roll for Rego).
"""

from __future__ import annotations

from ..models import Character
from . import casting, casting_virtues
from .lab import ability_score

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Nine: Hermetic Magic, Magical Craft, "
    "pp. 306-308 (Ease Factors for Creating and Crafting Objects, p. 308)"
)

REGO = "Rego"
CREO = "Creo"
TECHNIQUES: tuple[str, ...] = (REGO, CREO)

#: Ease Factors for Creating and Crafting Objects (p. 308): the task and
#: its Ease Factor, which includes the +3 for magic and a day's work.
CRAFT_TASKS: tuple[tuple[str, int, str], ...] = (
    ("Trivial", 3, "almost never worth rolling for"),
    ("Simple", 6, "work regularly done by untrained people"),
    ("Easy", 9, "the daily work of semiskilled craftsmen"),
    ("Average", 12, "the daily work of skilled craftsmen"),
    ("Hard", 15, "highly skilled craftsmen's daily work"),
    ("Very Hard", 18, "exceptionally skilled craftsmen's daily work"),
    ("Impressive", 21, "exceptional work by grandmasters"),
    ("Remarkable", 24, "the finest work of grandmasters"),
    ("Almost Impossible", 27, "the epitome of skill in a craft"),
)
TASK_EASE: dict[str, int] = {name: ease for name, ease, _ in CRAFT_TASKS}

#: What the magic adds to a mundane craftsman's Ease Factor (p. 307).
MAGIC_ADJUSTMENT = 3

#: The work's length for one craftsman, and what it adds (p. 307).
CRAFT_TIMES: tuple[tuple[str, int], ...] = (
    ("A day", 0),
    ("A month", 3),
    ("A season", 6),
    ("A year", 9),
)
TIME_EASE: dict[str, int] = dict(CRAFT_TIMES)

#: Creo craft magic's details (p. 307): a property's Ease Factor, or None
#: for an elaborate specification, which uses Rego craft magic's.
SINGLE = "One basic property"
FEW = "Two or three properties, or one precisely"
ELABORATE = "An elaborate specification or better quality"
CREO_DETAILS: tuple[tuple[str, int | None], ...] = (
    (SINGLE, 0),
    (FEW, 3),
    (ELABORATE, None),
)
DETAIL_EASE: dict[str, int | None] = dict(CREO_DETAILS)

#: A Creo craft spell with no Finesse roll makes a working example, as a
#: work of craft of this Ease Factor (p. 307).
UNROLLED_CREO_EASE = 6


def task_ease(task: str, time: str = "A day") -> int:
    """The Rego Ease Factor for a task from the table (already + 3) done in
    `time`."""
    return TASK_EASE[task] + TIME_EASE[time]


def mundane_ease(mundane: int, time: str = "A day") -> int:
    """The Rego Ease Factor from a mundane craftsman's Ease Factor or a
    City & Guild Workshop Total: + 3, then the time."""
    return mundane + MAGIC_ADJUSTMENT + TIME_EASE[time]


def creo_ease(detail: str, task: str = "Average", time: str = "A day") -> int:
    """The Creo Ease Factor for fixing `detail`; an elaborate one is the
    Rego Ease Factor of the task."""
    fixed = DETAIL_EASE[detail]
    return task_ease(task, time) if fixed is None else fixed


def roll_base(magus: Character, technique: str, precise: int = 0) -> int:
    """The Finesse roll before the stress die: Perception + Finesse for
    Rego, Intelligence + Finesse for Creo, with Precise Casting, the Wound
    and Fatigue penalties and Clumsy and Inconstant Magic."""
    if technique == REGO:
        return casting.aiming_base(magus, precise)
    return (
        casting.aiming_base(magus, precise)
        - magus.characteristics.perception
        + magus.characteristics.intelligence
    )


def characteristic(technique: str) -> str:
    """The Characteristic the roll uses."""
    return "Perception" if technique == REGO else "Intelligence"


def needed(base: int, ease: int) -> int:
    """What the stress die must reach: the Ease Factor less the base, at
    least 1 (a roll of 0 is no success)."""
    return max(ease - base, 1)


def finesse(magus: Character) -> int:
    """The magus's Finesse score."""
    return sum(ability_score(magus, "Finesse"))


def penalty_names(magus: Character) -> list[str]:
    """The Flaws taking 3 off the roll, by name."""
    names = {
        casting_virtues.CLUMSY_MAGIC: "Clumsy Magic",
        casting_virtues.INCONSTANT: "Inconstant Magic",
    }
    return [
        names[vf.vf_id]
        for vf in magus.virtues_flaws
        if vf.vf_id in casting_virtues.FINESSE_FLAWS
    ]


def failure(technique: str) -> str:
    """What a failed roll does (p. 307)."""
    if technique == REGO:
        return (
            "a failure still rearranges the materials, into nothing useful; a "
            "botch looks right but has a hidden, fatal flaw"
        )
    return (
        "a failure still makes a working example without the details; a "
        "botch makes something that hinders the caster"
    )


def summary_line(magus: Character) -> str:
    """One line for the casting notes: both rolls' bases and the table."""
    tasks = ", ".join(f"{name} {ease}" for name, ease, _ in CRAFT_TASKS)
    return (
        f"Craft magic: Rego Perception + Finesse {roll_base(magus, REGO):+d}, "
        f"Creo Intelligence + Finesse {roll_base(magus, CREO):+d} + stress die. "
        f"Ease Factors (with the +3 for magic, a day's work): {tasks}; +3 a "
        "month's work, +6 a season's, +9 a year's. Creo details: one property 0, "
        "two or three 3, elaborate as Rego (DE pp. 306-308)."
    )
