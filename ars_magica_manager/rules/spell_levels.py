"""Spell levels from their design (STORY-810): a guideline's base level
plus a magnitude per Range, Duration and Target step, plus any size and
requisite magnitudes.

| + magnitudes | Range             | Duration                 | Target                  |
|--------------|-------------------|--------------------------|-------------------------|
| 0            | Personal          | Momentary                | Individual, Circle, Taste |
| 1            | Touch, Eye        | Concentration, Diameter  | Part, Touch (sense)     |
| 2            | Voice             | Sun, Ring                | Group, Room, Smell      |
| 3            | Sight             | Moon                     | Structure, Hearing      |
| 4            | Arcane Connection | Year                     | Boundary, Vision        |

A magnitude is 5 levels, except below level 5, where it is 1 level. A spell
must be a Ritual with Year Duration, Boundary Target or a level over 50, and
a Ritual is always at least level 20.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Nine: Spells, Changing Ranges, "
    "Durations, and Targets "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Nine:"
    "_Spells#Changing_Ranges,_Durations,_and_Targets)"
)

RANGE_STEPS: dict[str, int] = {
    "Personal": 0,
    "Touch": 1,
    "Eye": 1,
    "Voice": 2,
    "Sight": 3,
    "Arcane Connection": 4,
}
DURATION_STEPS: dict[str, int] = {
    "Momentary": 0,
    "Concentration": 1,
    "Diameter": 1,
    "Sun": 2,
    "Ring": 2,
    "Moon": 3,
    "Year": 4,
}
TARGET_STEPS: dict[str, int] = {
    "Individual": 0,
    "Circle": 0,
    "Taste": 0,
    "Part": 1,
    "Touch": 1,
    "Group": 2,
    "Room": 2,
    "Smell": 2,
    "Structure": 3,
    "Hearing": 3,
    "Boundary": 4,
    "Vision": 4,
}
RITUAL_MINIMUM = 20
MAX_NON_RITUAL = 50


def add_magnitudes(level: int, magnitudes: int) -> int:
    """`level` raised (or, for a negative count, lowered) by magnitudes: 5
    levels each, 1 below level 5 (15 less 5 magnitudes is 2)."""
    for _ in range(magnitudes):
        level = level + 1 if level < 5 else level + 5
    for _ in range(-magnitudes):
        level = level - 1 if level <= 5 else level - 5
    return max(level, 1)


@dataclass
class Design:
    """A spell level worked out from its design."""

    level: int
    #: (what, magnitudes) for each step, as a stat block's design line lists.
    steps: list[tuple[str, int]] = field(default_factory=list)
    ritual_required: bool = False
    #: Why it must be a Ritual, or why the level was raised.
    notes: list[str] = field(default_factory=list)

    def design_line(self, base: int) -> str:
        """The stat block's design line: "Base 5, +2 Voice, +2 Sun, +2 Group"."""
        return ", ".join(
            [f"Base {base}", *(f"{n:+d} {what}" for what, n in self.steps)]
        )


def spell_level(
    base: int,
    range_: str,
    duration: str,
    target: str,
    *,
    extra_magnitudes: int = 0,
    ritual: bool = False,
) -> Design | None:
    """The level of a spell with this base and Range/Duration/Target, plus
    `extra_magnitudes` of size and requisites; None when a parameter isn't
    a standard one (a supplement's own, whose level the troupe sets)."""
    try:
        steps = [
            (range_, RANGE_STEPS[range_]),
            (duration, DURATION_STEPS[duration]),
            (target, TARGET_STEPS[target]),
        ]
    except KeyError:
        return None
    if extra_magnitudes:
        steps.append(("size/requisites", extra_magnitudes))
    level = add_magnitudes(base, sum(n for _, n in steps))
    design = Design(level=level, steps=steps)
    if duration == "Year":
        design.notes.append("Year Duration needs a Ritual.")
    if target == "Boundary":
        design.notes.append("Boundary Target needs a Ritual.")
    if level > MAX_NON_RITUAL:
        design.notes.append(f"Over level {MAX_NON_RITUAL} needs a Ritual.")
    design.ritual_required = bool(design.notes)
    if (ritual or design.ritual_required) and level < RITUAL_MINIMUM:
        design.level = RITUAL_MINIMUM
        design.notes.append(f"A Ritual is at least level {RITUAL_MINIMUM}.")
    return design


def extra_magnitudes(
    base: int, range_: str, duration: str, target: str, level: int
) -> int | None:
    """How many magnitudes of size, requisites or troupe ruling a listed
    level carries beyond its base and Range/Duration/Target (None when a
    parameter isn't standard)."""
    design = spell_level(base, range_, duration, target)
    if design is None:
        return None
    count = 0
    probe = design.level
    if level >= probe:
        while probe < level:
            probe = add_magnitudes(probe, 1)
            count += 1
    else:
        while probe > level and probe > 1:
            probe = add_magnitudes(probe, -1)
            count -= 1
    return count
