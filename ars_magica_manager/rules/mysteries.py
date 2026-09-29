"""Mystery initiation (STORY-813).

    Initiation Total = Mystagogue's Presence + (Mystery Cult) Lore
                       + Script bonus (the sum of its components)

No die: the Initiation succeeds when the total at least equals the Target
Level (decision 18): a Minor Virtue 15, a Major 21, or 18 / 30 when the
Mystagogue lacks the Virtue. An Ordeal suffered in an earlier Initiation
lowers the Target of the next three (only the best one counts), never below
9; it doesn't help the Initiation it was suffered in (decision 79).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character
from .breakdown import Breakdown, Line
from .lab import ability_score

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Mystery "
    "Initiation "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Mystery_Initiation)"
)

#: (tier, Mystagogue has the Virtue) -> Target Level.
TARGET_LEVELS: dict[tuple[str, bool], int] = {
    ("Minor", True): 15,
    ("Minor", False): 18,
    ("Major", True): 21,
    ("Major", False): 30,
}
MINIMUM_TARGET = 9

#: Ordeal size -> the Target reduction for the 1st, 2nd and 3rd later
#: Initiation (the Definitive Edition's table).
ORDEAL_REDUCTIONS: dict[str, tuple[int, int, int]] = {
    "Minor": (3, 3, 1),
    "Medium": (6, 4, 2),
    "Major": (9, 6, 3),
}


@dataclass(frozen=True)
class Component:
    """A Script component: its bonus, and whether a Script may hold it only
    once."""

    name: str
    bonus: int
    once: bool = False


#: The Definitive Edition's example components (the sacrifice of something
#: of great symbolic value is +3 to +6, chosen per Script).
COMPONENTS: tuple[Component, ...] = (
    Component("Special place at a special time", 3),
    Component("Specific Quest", 3),
    Component("Sacrifice of time serving the cult", 1, once=True),
    Component("Sacrifice of material goods", 1),
    Component("Minor Ordeal", 3),
    Component("Medium Ordeal", 6),
    Component("Major Ordeal", 9),
)


def target_level(
    tier: str,
    mystagogue_has_virtue: bool,
    past_ordeals: Sequence[tuple[str, int]] = (),
) -> Breakdown:
    """The Target Level, less the best reduction from past Ordeals, each
    given as (size, how many Initiations ago: 1 for the next one)."""
    base = TARGET_LEVELS[tier, mystagogue_has_virtue]
    lines = [Line(f"{tier} Virtue", amount=base, source=SOURCE)]
    best = 0
    for size, since in past_ordeals:
        if 1 <= since <= 3:
            best = max(best, ORDEAL_REDUCTIONS[size][since - 1])
    if best:
        lines.append(Line("Past Ordeal", amount=-best, source=SOURCE))
    return Breakdown(total=max(MINIMUM_TARGET, base - best), lines=lines)


def script_bonus(components: Sequence[Component]) -> int:
    """A Script's bonus: the sum of its components. A once-only component
    held twice makes the Script invalid (ValueError)."""
    for component in components:
        if component.once and components.count(component) > 1:
            raise ValueError(f"A Script may include {component.name!r} only once.")
    return sum(component.bonus for component in components)


def initiation_total(
    mystagogue: Character, lore: str, components: Sequence[Component]
) -> Breakdown:
    lines = [
        Line("Presence", amount=mystagogue.characteristics.presence, source=SOURCE),
        Line(lore, amount=sum(ability_score(mystagogue, lore)), source=SOURCE),
    ]
    lines += [Line(c.name, amount=c.bonus, source=SOURCE) for c in components]
    script_bonus(components)  # validates
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def succeeds(total: int, target: int) -> bool:
    return total >= target
