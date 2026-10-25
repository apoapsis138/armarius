"""Whether a creature's build hangs together.

- Might is its Magic Resistance (+ the aura), fuels its powers and sets
  their Penetration: Might - 5 x the power's cost + the Penetration Bonus.
  A power costing more than the Might can never be used, since the Pool
  refreshes only to the Might Score. Only Magic Might goes with The Gift,
  and a creature with Might has no Warping Score (DE pp. 425-426).
- A creature designed with Magic Might (Realms of Power: Magic pp. 30-36)
  has as many Quality points as its Might Score, plus 1 for each Minor
  Inferiority and 3 for each Major one; a Minor Quality costs 1, a Major 3.
  A magic animal's Might is its base less its Size (more when Size is
  negative), and its Quality points count the base. Its inherent vis is
  typically Might / 5, rounded up. Characters made to fill a story's need
  needn't balance (p. 34), so the app reports the points rather than
  refusing them.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .. import catalog
from ..models import Creature, CreaturePower
from .rounding import round_down, round_up

SOURCE = (
    "Ars Magica Definitive Edition, Creature Might and Creature Powers, pp. "
    "425-426; Realms of Power: Magic, Magic Character Creation, pp. 30-36"
)

MAGIC = "Magic"
QUALITY, INFERIORITY = "Quality", "Inferiority"
POINTS = {"Minor": 1, "Major": 3}
MAGIC_ANIMAL = "vf_magic_animal"
THE_GIFT = "vf_the_gift"
VIS_PER_MIGHT = 5


@dataclass(frozen=True)
class QualityBudget:
    """A magic creature's Quality points: from its Might and its
    Inferiorities, and what its Qualities spend."""

    from_might: int
    from_inferiorities: int
    spent: int

    @property
    def left(self) -> int:
        return self.from_might + self.from_inferiorities - self.spent


def base_might(creature: Creature) -> int:
    """The Might its Qualities are counted from: a magic animal's Size
    added back."""
    ids = {vf.vf_id for vf in creature.virtues_flaws}
    return creature.might + (creature.size if MAGIC_ANIMAL in ids else 0)


def quality_budget(creature: Creature) -> QualityBudget | None:
    """The Quality points of a creature with Magic Might that has
    Qualities or Inferiorities (None otherwise)."""
    if creature.realm != MAGIC:
        return None
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    spent = gained = 0
    found = False
    for vf in creature.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        if entry is None or entry.type not in (QUALITY, INFERIORITY):
            continue
        found = True
        points = POINTS.get(entry.tier, 0)
        if entry.type == QUALITY:
            spent += points
        else:
            gained += points
    if not found:
        return None
    return QualityBudget(max(0, base_might(creature)), gained, spent)


#: The Magic Qualities that give a power, each a Strategy as two small
#: functions: (Might cost from magnitude, Initiative from Quickness and
#: magnitude), and the spell levels it grants (RoP: Magic p. 36; a
#: faerie's power Virtues are the same, RoP: Faerie p. 55). Halves
#: round down (DE p. 6).
POWERS: dict[str, tuple[Callable[[int], int], Callable[[int, int], int], int]] = {
    "Focus Power": (lambda m: m, lambda q, m: q - m, 25),
    "Lesser Power": (lambda m: m, lambda q, m: q - 2 * m, 25),
    "Greater Power": (
        lambda m: round_down(m / 2),
        lambda q, m: q - round_down(m / 2),
        50,
    ),
    "Ritual Power": (lambda m: m, lambda q, m: q - 2 * m, 25),
    "Personal Power": (
        lambda m: round_down(m / 2),
        lambda q, m: q - round_down(m / 2),
        25,
    ),
}


def magnitude(level: int) -> int:
    """An effect's magnitude: its level / 5, rounded up, at least 1."""
    return max(1, round_up(level / 5))


def suggested(creature: Creature, power: CreaturePower) -> tuple[int, int] | None:
    """The cost and Initiative the power's Quality suggests (None for a
    typed power, or one with no effect level)."""
    if power.quality not in POWERS or power.level is None:
        return None
    cost, init, _ = POWERS[power.quality]
    m = magnitude(power.level)
    return max(0, cost(m)), init(creature.characteristics.quickness, m)


def power_notes(creature: Creature, power: CreaturePower) -> list[str]:
    """Where a power's typed figures differ from its Quality's, and the
    Ritual Power limits (at least level 20; level 50 or more must be a
    Ritual Power). Mastery points and constant powers change the cost, so
    these are suggestions, never refusals."""
    found: list[str] = []
    figures = suggested(creature, power)
    if figures is not None and figures != (power.might_cost, power.init):
        found.append(
            f"{power.name}: as a {power.quality}, cost {figures[0]} and Init "
            f"{figures[1]:+d} (typed {power.might_cost}, {power.init:+d}; "
            + (
                "RoP: Faerie p. 55"
                if creature.realm == "Faerie"
                else "RoP: Magic p. 36"
            )
            + ")."
        )
    if power.quality and power.level is not None:
        if power.level >= 50 and power.quality != "Ritual Power":
            found.append(f"{power.name}: level 50 or more must be a Ritual Power.")
        if power.quality == "Ritual Power" and power.level < 20:
            found.append(f"{power.name}: a Ritual Power is at least level 20.")
    return found


def typical_vis(creature: Creature) -> int:
    """Inherent vis as Realms of Power: Magic suggests: Might / 5, rounded
    up."""
    return round_up(max(0, creature.might) / VIS_PER_MIGHT)


def problems(creature: Creature) -> list[str]:
    """What doesn't fit the Definitive Edition's creature rules."""
    found: list[str] = []
    ids = {vf.vf_id for vf in creature.virtues_flaws}
    if creature.realm and creature.realm != MAGIC and THE_GIFT in ids:
        found.append(
            f"Only a creature with Magic Might can have The Gift; this one's is "
            f"{creature.realm} (DE p. 426)."
        )
    if creature.realm:
        for power in creature.powers:
            if power.might_cost > creature.might:
                found.append(
                    f"{power.name} costs {power.might_cost} Might Points, more "
                    f"than the Might of {creature.might}: it can never be used "
                    "(DE p. 425)."
                )
        for power in creature.powers:
            found += power_notes(creature, power)
        if creature.might_pool is not None and creature.might_pool > creature.might:
            found.append(
                f"Its Might Pool ({creature.might_pool}) is above its Might "
                f"({creature.might}): the Pool refreshes only to the Score "
                "(DE p. 425)."
            )
    return found
