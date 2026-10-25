"""A church described in Build Points, Boons and Hooks, as a covenant is
(The Church pp. 48-51): its Build Points by kind, what its resources
cost, and the church-only Boons and Hooks.

A church may take up to 10 points of Hooks; a Major Hook or Boon is 3
points, a Minor 1. Most covenant Boons and Hooks (DE pp. 72-74, Covenants
pp. 6-27) suit a church too; the ones here are a church's alone, so they
are kept apart from the covenant catalog, which a covenant's Build chooses
from. A church buys books, specialists and vis at a covenant's prices; an
enchanted item costs 1 Build Point a level of its effects (churches can't
make their own), and a relic its Faith score's cost + 5 a power beyond
the common relic powers."""

from __future__ import annotations

from dataclasses import dataclass

SOURCE = "The Church, Creating Game Statistics for a Church, pp. 48-51"

#: Each kind of church's Build Points (p. 48); the kinds are churches.py's.
BUILD_POINTS: dict[str, int] = {
    "Chapel": 50,
    "Parish church": 250,
    "Large urban church": 500,
    "Monastery or nunnery": 500,
    "Bishop's cathedral": 500,
    "Archbishop's cathedral": 1000,
}
MAX_HOOK_POINTS = 10
TIER_POINTS: dict[str, int] = {"Minor": 1, "Major": 3}
#: A relic's cost by Faith score (p. 49), and per power beyond the common.
RELIC_COST: dict[int, int] = {1: 1, 2: 3, 3: 6, 4: 10, 5: 15}
RELIC_POWER_COST = 5
ENCHANTMENT_COST_PER_LEVEL = 1
#: The most levels of effects a church's enchanted item usually holds.
TYPICAL_ENCHANTMENT_LEVELS = 50


@dataclass(frozen=True)
class ChurchBoonHook:
    """A church Boon or Hook: its tier, what it does, and its Divine aura
    change, if any."""

    name: str
    kind: str  # "Boon" or "Hook"
    tier: str  # "Minor" or "Major"
    effect: str
    aura: int = 0
    repeatable: bool = False
    #: Not for a major church (a cathedral, monastery or large church).
    minor_church_only: bool = False


BOONS_AND_HOOKS: tuple[ChurchBoonHook, ...] = (
    ChurchBoonHook(
        "Military Order",
        "Boon",
        "Major",
        "An outpost of a military order, with barracks for knights and men-at-arms.",
    ),
    ChurchBoonHook(
        "Anchorite/Anchoress",
        "Boon",
        "Minor",
        "A cell where an anchorite lives in worship: the Divine aura is 1 higher.",
        aura=1,
    ),
    ChurchBoonHook(
        "Burial Rights",
        "Boon",
        "Minor",
        "A large cemetery and its burial fees: a Typical Source of Income.",
    ),
    ChurchBoonHook(
        "Chantry",
        "Boon",
        "Minor",
        "Masses for the dead: a Typical Source of Income, for four seasons of "
        "a priest's work a year.",
        repeatable=True,
    ),
    ChurchBoonHook(
        "Chapter of Canons",
        "Boon",
        "Minor",
        "At least half a dozen priests holding benefices together: a Typical "
        "Source of Income.",
    ),
    ChurchBoonHook(
        "Church School",
        "Boon",
        "Minor",
        "A school, with pupils and teachers in minor orders.",
    ),
    ChurchBoonHook(
        "Corrupt",
        "Hook",
        "Major",
        "Corrupt priests: an Infernal aura instead of a Divine one, until they "
        "are found out, excommunicated and replaced.",
    ),
    ChurchBoonHook(
        "Heretics",
        "Hook",
        "Major",
        "Heretical priests: if found out, frequent visitations, and the risk of "
        "excommunication and crusade.",
    ),
    ChurchBoonHook(
        "Jurisdiction",
        "Hook",
        "Major",
        "A cathedral, archdeaconry or deanery over many churches, holding "
        "regional synods at least yearly.",
    ),
    ChurchBoonHook(
        "Absent Rector",
        "Hook",
        "Minor",
        "The beneficed priest lives elsewhere; a curate does his duties.",
    ),
    ChurchBoonHook(
        "Incompetent Curate",
        "Hook",
        "Minor",
        "An incompetent curate: if found out, removed, and many visitations.",
        minor_church_only=True,
    ),
    ChurchBoonHook(
        "Vast Sanctuary",
        "Hook",
        "Minor",
        "Sanctuary for miles around, so the priest is often at odds with the sheriff.",
    ),
)
BY_NAME: dict[str, ChurchBoonHook] = {e.name: e for e in BOONS_AND_HOOKS}
#: The kinds of church a Minor-church-only Hook can't be taken by.
MAJOR_CHURCHES: frozenset[str] = frozenset(
    {
        "Large urban church",
        "Monastery or nunnery",
        "Bishop's cathedral",
        "Archbishop's cathedral",
    }
)


def relic_cost(faith_score: int, powers: int = 0) -> int:
    """A relic's Build Points: its Faith score's cost + 5 a power. The
    book's table (1, 3, 6, 10, 15) stops at 5; above it the app carries on
    its pattern, 1 + 2 + ... + the score."""
    if faith_score < 1:
        raise ValueError("A relic has a Faith score of at least 1.")
    cost = RELIC_COST.get(faith_score, faith_score * (faith_score + 1) // 2)
    return cost + RELIC_POWER_COST * max(0, powers)


def points(names: list[str], kind: str) -> int:
    """The points of the church Boons (or Hooks) named."""
    return sum(
        TIER_POINTS[BY_NAME[n].tier]
        for n in names
        if n in BY_NAME and BY_NAME[n].kind == kind
    )


def problems(church_kind: str, names: list[str]) -> list[str]:
    """What's wrong with a church's chosen Boons and Hooks: more than 10
    points of Hooks, a Boon not paid for by Hooks, a Minor-church-only Hook
    on a major church, or a Boon taken twice that can't be."""
    found: list[str] = []
    unknown = [n for n in names if n not in BY_NAME]
    if unknown:
        found.append("Not a church Boon or Hook: " + ", ".join(unknown) + ".")
    hooks, boons = points(names, "Hook"), points(names, "Boon")
    if hooks > MAX_HOOK_POINTS:
        found.append(
            f"{hooks} points of Hooks: a church takes up to {MAX_HOOK_POINTS}."
        )
    if boons > hooks:
        found.append(
            f"{boons} points of Boons, but only {hooks} of Hooks to pay for them."
        )
    for name in sorted({n for n in names if n in BY_NAME}):
        entry = BY_NAME[name]
        if entry.minor_church_only and church_kind in MAJOR_CHURCHES:
            found.append(f"{name} can't be taken by a {church_kind.lower()}.")
        if not entry.repeatable and names.count(name) > 1:
            found.append(f"{name} can be taken only once.")
    return found


def aura_change(names: list[str]) -> int:
    """What the chosen Boons and Hooks add to the church's Divine aura."""
    return sum(BY_NAME[n].aura for n in names if n in BY_NAME)
