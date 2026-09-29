"""How a total was worked out: each line is one term with where it came
from, so a sheet can show the working and cite the rule behind every
number (the Rules Engine's convention: every rule cites its source)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Source:
    """A citation: the book, its chapter and section, and the page on
    Project: Redcap the rules reference took it from."""

    book: str
    section: str
    url: str

    def __str__(self) -> str:
        return f"{self.book}, {self.section}"


@dataclass(frozen=True)
class Line:
    """One term of a total: a flat amount added, or a multiplier applied
    (see rules.effects.combine for the order)."""

    label: str
    amount: float | None = None
    multiplier: float | None = None
    #: The rule this term comes from, or the Virtue/Flaw/Boon/Hook that
    #: carries it ("" for a figure typed on the sheet).
    source: str = ""


@dataclass
class Breakdown:
    total: float
    lines: list[Line] = field(default_factory=list)
