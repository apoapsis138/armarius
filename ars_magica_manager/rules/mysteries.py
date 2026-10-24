"""Mystery initiation.

    Initiation Total = Mystagogue's Presence + (Mystery Cult) Lore
                       + Script bonus (the sum of its components)

No die: the Initiation succeeds when the total at least equals the Target
Level: a Minor Virtue 15, a Major 21, or 18 / 30 when the Mystagogue lacks
the Virtue (DE pp. 387-388). An Ordeal suffered in an earlier Initiation
lowers the Target of the next three, by 3/2/1 (Minor), 6/4/2 (Medium) or
9/6/3 (Major); only the best one counts, never below 9, and it doesn't help
the Initiation it was suffered in.

Varying a Script (DE pp. 388-389): the Mystagogue may make one change in an
Initiation, a stress die + Intelligence + the Lore against 9 to add a
component or 12 to change one (The Mysteries Revised Edition p. 17 adds 15
to remove one). If the test fails, the Initiation fails; the Script as it
was may be tried another season.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character
from .breakdown import Breakdown, Line
from .lab import ability_score

SOURCE = (
    "Ars Magica Definitive Edition, Mystery Initiation, pp. 387-389; The "
    "Mysteries Revised Edition, Varying a Script, p. 17"
)

#: (tier, Mystagogue has the Virtue) -> Target Level.
TARGET_LEVELS: dict[tuple[str, bool], int] = {
    ("Minor", True): 15,
    ("Minor", False): 18,
    ("Major", True): 21,
    ("Major", False): 30,
}
MINIMUM_TARGET = 9
ADD, CHANGE, REMOVE = "add", "change", "remove"
#: Varying a Script: the Ease Factor of each kind of change.
VARY_EASE: dict[str, int] = {ADD: 9, CHANGE: 12, REMOVE: 15}
VARY_LABELS: dict[str, str] = {
    ADD: "Add a component (9)",
    CHANGE: "Change a component (12)",
    REMOVE: "Remove a component (15)",
}

#: Ordeal size -> the Target reduction for the 1st, 2nd and 3rd later
#: Initiation (the Definitive Edition's table).
ORDEAL_REDUCTIONS: dict[str, tuple[int, int, int]] = {
    "Minor": (3, 2, 1),
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
