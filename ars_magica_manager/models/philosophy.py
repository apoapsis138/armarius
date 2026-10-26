"""Experimental philosophy's formulae a character knows (Art & Academe,
Chapter Five): each one's kind, level and whether its Laboratory Text is
written. The rules that read them are rules.philosophy's."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import known_fields

#: The three kinds of formula, each learned through its Academic Ability
#: (Art & Academe p. 69).
FORMULA_KINDS = ("inception", "reagent", "theriac")


@dataclass
class Formula:
    """A formula known or being learned: its name (the Progress record's
    and `Character.formulas`' name), kind, level (0: not yet set) and
    whether its maker has concocted it once, writing its Laboratory Text
    (p. 71)."""

    name: str
    kind: str = "theriac"
    level: int = 0
    lab_text: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Formula:
        found = cls(**known_fields(cls, data))
        if found.kind not in FORMULA_KINDS:
            raise ValueError(
                f"The formula {found.name!r} is of an unknown kind {found.kind!r} "
                f"(one of {', '.join(FORMULA_KINDS)})."
            )
        if not isinstance(found.level, int) or found.level < 0:
            raise ValueError(
                f"The formula {found.name!r} has a level of {found.level!r}: a "
                "whole number, 0 or more."
            )
        return found
