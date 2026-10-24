"""Learning spells from a teacher (DE p. 251): a season in which another
magus, who knows the spells, guides the student through inventing them.
Unlike Lab Texts, the spells may be of several Techniques and Forms.

- The levels learned together are at most the teacher's highest Lab Total
  among the spells' Techniques and Forms;
- those of one Technique and Form at most the teacher's Lab Total in it;
- and no single spell above the student's own Lab Total for it.

The Spells Specialization applies to the student's Lab Total (DE p. 291).
Each total is worked out by the caller (rules.lab_seasons); this module is
only the three limits.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Spell

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Learning Spells "
    "from a Teacher, p. 251"
)


@dataclass(frozen=True)
class Taught:
    """One spell to be taught, with the two Lab Totals for its Technique
    and Form (requisites counted)."""

    spell: Spell
    student_total: int
    teacher_total: int

    @property
    def level(self) -> int:
        return self.spell.level or 0

    @property
    def arts(self) -> tuple[str, str]:
        return self.spell.technique, self.spell.form


def problems(taught: list[Taught], student: str, teacher: str) -> list[str]:
    """Why the season can't teach all of `taught` (none: it can)."""
    found: list[str] = []
    for one in taught:
        if one.level > one.student_total:
            found.append(
                f"{one.spell.name} is level {one.level}: above {student}'s "
                f"Lab Total {one.student_total} for it."
            )
    by_arts: dict[tuple[str, str], list[Taught]] = {}
    for one in taught:
        by_arts.setdefault(one.arts, []).append(one)
    for (technique, form), group in by_arts.items():
        levels = sum(one.level for one in group)
        most = max(one.teacher_total for one in group)
        if levels > most:
            found.append(
                f"{levels} levels of {technique} {form}: {teacher}'s Lab Total "
                f"there is {most}."
            )
    total = sum(one.level for one in taught)
    highest = max((one.teacher_total for one in taught), default=0)
    if total > highest:
        found.append(
            f"{total} levels in all: {teacher}'s highest Lab Total among them "
            f"is {highest}."
        )
    return found
