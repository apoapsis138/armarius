"""Siegecraft (Lords of Men, Chapter Eight, pp. 109-116): a castle's
Garrison, Defenses and Supplies, each with the interval at which its
events come (the shortest sets the siege's pace), and the rolls of a
siege.

- Garrison by combat groups: 10 or fewer a Day and +1 Weight of Numbers,
  11-20 a Week +2, 21-40 a Month +3, 41 or more a Season +4.
- Defenses by quality: Shoddy a Day +1, Standard a Week +2, Superior a
  Month +3, Excellent a Season +4 (+1 for permanent enchantments). Each of
  the four walls has its Defense Bonus x 3 damage levels (Size +5 to +8)
  or x 4 (+9 and larger); a wall at 0 loses its bonus.
- Supplies: Shoddy a Week +1, Standard a Month +3, Superior a Season +5,
  Excellent a Year +7. A stockade (three walls or more held) makes a
  supplies roll each interval: Siege Conditions Bonus + stress die against
  3 + the Garrison's Weight of Numbers + the years under siege; failing
  drops Supplies a step (and at Shoddy, the castle surrenders); a botch
  (1 + full seasons under siege, botch dice) is disease.
- Undermining: Intelligence + Profession: Sapper + die against the same
  + the Defense Bonus (one step higher behind a moat); beating it takes the
  Defenses down a step. Artillery: Intelligence + Siege Weapon + the
  engine's Attack against Intelligence + Profession: Siege Engineer + the
  Defense Bonus; a hit costs the wall a damage level per engine (groups of
  up to five).
- Living under siege: -2 Living Conditions for each year with a season of
  it.

- Playing a siege (pp. 112-115): an event comes at the castle's shortest
  interval; the besiegers undermine a wall (with miners), bombard one
  (with mangonels or trebuchets) or scale it (escalade: a battlefield
  event, the garrison's Weight of Numbers and the Defense Bonus standing
  in for numbers and ground; each besiegers' win takes the Garrison a
  step down, and a win at a Shoddy or broken wall breaches the castle),
  or the garrison sallies out (a Battle Ease Factor 9 event that removes
  the units it targets). A stockade's supplies rolls come due at the
  Supplies interval. Time is counted in days: a week 7, a month 30, a
  season 91, a year 364.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import WALLS, Saga, Siege
from . import dice

SOURCE = "Lords of Men, Chapter Eight: Siegecraft, pp. 109-116"
QUALITIES = ("Shoddy", "Standard", "Superior", "Excellent")
INTERVALS = ("Day", "Week", "Month", "Season", "Year")
DEFENSES: dict[str, tuple[str, int]] = {
    "Shoddy": ("Day", 1),
    "Standard": ("Week", 2),
    "Superior": ("Month", 3),
    "Excellent": ("Season", 4),
}
SUPPLIES: dict[str, tuple[str, int]] = {
    "Shoddy": ("Week", 1),
    "Standard": ("Month", 3),
    "Superior": ("Season", 5),
    "Excellent": ("Year", 7),
}
ENCHANTED_DEFENSES = 1
MAX_ENGINE_GROUP = 5
LIVING_UNDER_SIEGE = -2
#: Siege engines: (Init, Attack, static Defence, Damage, crew, range,
#: Mythic Pounds).
ENGINES: dict[str, tuple[int, int, int, int, int, str, int]] = {
    "Ballista": (5, 5, 6, 15, 3, "50", 5),
    "Mangonel": (-3, 3, 6, 20, 5, "20-150", 10),
    "Trebuchet": (-4, 1, 6, 25, 5, "50-200", 15),
}


def garrison(groups: int) -> tuple[str, int]:
    """A garrison's interval and Weight of Numbers by its combat groups."""
    if groups <= 10:
        return "Day", 1
    if groups <= 20:
        return "Week", 2
    if groups <= 40:
        return "Month", 3
    return "Season", 4


def wall_damage_levels(defense_bonus: int, size: int) -> int:
    """A wall's damage levels: its Defense Bonus x 3, or x 4 for a castle,
    town or city of Size +9 or more."""
    return defense_bonus * (4 if size >= 9 else 3)


@dataclass(frozen=True)
class Castle:
    groups: int
    defenses: str = "Standard"
    supplies: str = "Standard"
    enchanted: bool = False
    moat: bool = False

    def defense_bonus(self, *, against_mines: bool = False) -> int:
        quality = self.defenses
        if against_mines and self.moat and quality != QUALITIES[-1]:
            quality = QUALITIES[QUALITIES.index(quality) + 1]
        bonus = DEFENSES[quality][1]
        return bonus + (ENCHANTED_DEFENSES if self.enchanted else 0)

    def interval(self) -> str:
        """How often the siege's events come: the shortest interval."""
        found = (
            garrison(self.groups)[0],
            DEFENSES[self.defenses][0],
            SUPPLIES[self.supplies][0],
        )
        return min(found, key=INTERVALS.index)

    def supplies_ease(self, years: int) -> int:
        """A stockaded castle's supplies roll: against 3 + the Garrison's
        Weight of Numbers + the years under siege."""
        return 3 + garrison(self.groups)[1] + years

    def supplies_bonus(self) -> int:
        return SUPPLIES[self.supplies][1]


def worse(quality: str) -> str | None:
    """The quality a step down (None below Shoddy: at Shoddy, failing a
    supplies roll means surrender)."""
    index = QUALITIES.index(quality)
    return QUALITIES[index - 1] if index else None


def disease_botch_dice(seasons: int) -> int:
    """A stockade supplies roll's botch dice: 1 + full seasons besieged."""
    return 1 + max(0, seasons)


# -- playing a siege --

INTERVAL_DAYS = {"Day": 1, "Week": 7, "Month": 30, "Season": 91, "Year": 364}
DAYS_PER_SEASON = INTERVAL_DAYS["Season"]
DAYS_PER_YEAR = INTERVAL_DAYS["Year"]
#: Walls a stockade must hold (three of the four).
STOCKADE_WALLS = 3
SALLY_EASE = 9
WALL_BREAKERS = ("Mangonel", "Trebuchet")
#: The Garrison's steps by combat groups: each besiegers' win in an
#: escalade takes it down to the top of the step below.
GARRISON_STEPS = (10, 20, 40)
UNDERMINE, ARTILLERY, ESCALADE, SALLY, WAIT = (
    "Undermine a wall",
    "Bombard a wall",
    "Escalade",
    "The garrison sallies out",
    "Keep the stockade",
)
EVENTS = (UNDERMINE, ARTILLERY, ESCALADE, SALLY, WAIT)
SALLY_TARGETS = ("Miners", *WALL_BREAKERS, "Ballista", "Soldiers")


@dataclass
class Played:
    """A siege event played: the chronicle's line and its working."""

    text: str
    lines: list[str] = field(default_factory=list)


def castle_of(siege: Siege) -> Castle:
    return Castle(
        groups=siege.garrison,
        defenses=siege.defenses,
        supplies=siege.supplies,
        enchanted=siege.enchanted,
        moat=siege.moat,
    )


def full_wall(siege: Siege) -> int:
    """A whole wall's damage levels: the Defense Bonus x 3 (x 4 at Size +9
    or more)."""
    return wall_damage_levels(castle_of(siege).defense_bonus(), siege.size)


def walls(siege: Siege) -> list[int]:
    """Each wall's damage levels left."""
    if siege.walls is not None:
        return list(siege.walls)
    return [full_wall(siege)] * len(WALLS)


def wall_bonus(siege: Siege, wall: int, *, against_mines: bool = False) -> int:
    """The Defense Bonus at a wall: none once it is down to 0."""
    if walls(siege)[wall] <= 0:
        return 0
    return castle_of(siege).defense_bonus(against_mines=against_mines)


def stockaded(siege: Siege) -> bool:
    """Besiegers at three walls or more hold the castle in stockade."""
    return sum(1 for n in siege.besieger_walls if n > 0) >= STOCKADE_WALLS


def interval_days(siege: Siege) -> int:
    return INTERVAL_DAYS[castle_of(siege).interval()]


def seasons_run(siege: Siege) -> int:
    """Full seasons the siege has run."""
    return siege.days // DAYS_PER_SEASON


def years_run(siege: Siege) -> int:
    return siege.days // DAYS_PER_YEAR


def engine_groups(siege: Siege) -> list[tuple[str, int]]:
    """The wall-breaking engines in groups of up to five: (kind, how
    many)."""
    found: list[tuple[str, int]] = []
    for kind in WALL_BREAKERS:
        left = siege.engines.get(kind, 0)
        while left > 0:
            found.append((kind, min(MAX_ENGINE_GROUP, left)))
            left -= MAX_ENGINE_GROUP
    return found


def _roll(
    rng: random.Random, saga: Saga | None, label: str, base: int, lines: list[str]
) -> tuple[int, bool]:
    die = dice.stress_die(rng, saga=saga)
    if die.botched:
        lines.append(f"{label}: {base} + a botch")
        return 0, True
    lines.append(f"{label}: {base} + stress die {die.value} = {base + die.value}")
    return base + die.value, False


def undermine(
    siege: Siege, wall: int, rng: random.Random, saga: Saga | None = None
) -> Played:
    """The miners dig under a wall and fire the mine: a success takes the
    Defenses a step down (two on a botched defence); a botched attack
    loses the miners' unit."""
    if siege.miners <= 0:
        return Played("The besiegers have no miners to dig with.")
    lines: list[str] = []
    bonus = wall_bonus(siege, wall, against_mines=True)
    attack, botched = _roll(rng, saga, "Mine Attack", siege.sapper, lines)
    defence, guard_botched = _roll(
        rng, saga, "Castle Defense", siege.counter_sapper + bonus, lines
    )
    name = WALLS[wall]
    if botched:
        siege.miners -= 1
        return Played(
            f"The mine under the {name} wall collapses on the sappers: a unit of "
            "miners is lost (or a story to rescue them).",
            lines,
        )
    if attack <= defence:
        return Played(f"The mine under the {name} wall is found and countered.", lines)
    for _ in range(2 if guard_botched else 1):
        lower = worse(siege.defenses)
        if lower is not None:
            siege.defenses = lower
    return Played(
        f"The mine under the {name} wall is fired and brings it down: the "
        f"Defenses fall to {siege.defenses}.",
        lines,
    )


def bombard(
    siege: Siege, wall: int, rng: random.Random, saga: Saga | None = None
) -> Played:
    """Each group of up to five engines makes one attack on the wall; a
    hit costs it a damage level for each engine in the group."""
    groups = engine_groups(siege)
    if not groups:
        return Played("The besiegers have no mangonel or trebuchet to bombard with.")
    lines: list[str] = []
    left = walls(siege)
    name = WALLS[wall]
    lost = 0
    for kind, count in groups:
        bonus = wall_bonus(siege, wall)
        plural = "s" if count > 1 else ""
        attack, botched = _roll(
            rng, saga, f"{count} {kind}{plural}", siege.gunner + ENGINES[kind][1], lines
        )
        defence, _ = _roll(rng, saga, "Castle Defense", siege.engineer + bonus, lines)
        if not botched and attack > defence:
            hit = min(count, left[wall])
            left[wall] -= hit
            lost += hit
    siege.walls = left
    if not lost:
        return Played(f"The engines pound the {name} wall to no effect.", lines)
    plural = "s" if lost > 1 else ""
    end = ": it no longer gives its Defense Bonus." if left[wall] == 0 else "."
    return Played(
        f"The engines batter the {name} wall: {lost} damage level{plural} lost, "
        f"{left[wall]} left{end}",
        lines,
    )


def step_down(groups: int) -> int:
    """The Garrison a step down: the top of the step below (half, at the
    lowest step, where the book gives no step below)."""
    lower = [top for top in GARRISON_STEPS if top < groups]
    return lower[-1] if lower else groups // 2


def escalade(siege: Siege, wall: int, besiegers_won: bool) -> Played:
    """An escalade at a wall, played as a battlefield event: a besiegers'
    win takes the Garrison a step down, and at a Shoddy or broken wall
    breaches the castle."""
    name = WALLS[wall]
    if not besiegers_won:
        return Played(f"The escalade at the {name} wall is thrown back.")
    siege.garrison = step_down(siege.garrison)
    if siege.defenses == QUALITIES[0] or walls(siege)[wall] <= 0:
        siege.ended = "Breached"
        return Played(
            f"The besiegers carry the {name} wall and breach the castle: fight the "
            "battle inside with the battle rules."
        )
    return Played(
        f"The besiegers win a foothold on the {name} wall: the garrison falls to "
        f"{siege.garrison} combat groups."
    )


def sally(siege: Siege, target: str, won: bool) -> Played:
    """The garrison sallies out against the miners, a group of engines or
    the soldiers (Battle Ease Factor 9); a win removes those units."""
    if not won:
        return Played(f"The sally against the {target.lower()} is beaten back.")
    if target == "Miners":
        siege.miners = 0
    elif target == "Soldiers":
        siege.soldiers = max(0, siege.soldiers - 1)
    else:
        siege.engines[target] = max(0, siege.engines.get(target, 0) - MAX_ENGINE_GROUP)
    return Played(f"The sally strikes the {target.lower()} and returns to the walls.")


def supplies_rolls(
    siege: Siege, rng: random.Random, saga: Saga | None = None
) -> list[str]:
    """Every supplies roll a stockade has come due for: Siege Conditions
    Bonus + stress die against 3 + Weight of Numbers + years besieged;
    failing drops the Supplies a step (and at Shoddy, the castle
    surrenders); a botch (1 + full seasons, botch dice) is disease."""
    told: list[str] = []
    if not stockaded(siege):
        return told
    while not siege.ended:
        every = INTERVAL_DAYS[SUPPLIES[siege.supplies][0]]
        if (siege.supply_rolls + 1) * every > siege.days:
            break
        siege.supply_rolls += 1
        castle = castle_of(siege)
        ease = castle.supplies_ease(years_run(siege))
        die = dice.stress_die(rng, disease_botch_dice(seasons_run(siege)), saga=saga)
        total = 0 if die.botched else castle.supplies_bonus() + die.value
        told.append(f"Supplies roll: {total} against {ease}")
        if die.botched:
            told.append("Disease breaks out within the castle.")
        if total >= ease:
            continue
        lower = worse(siege.supplies)
        if lower is None:
            siege.ended = "Surrendered"
            told.append("The supplies are gone: the castle surrenders.")
            break
        siege.supplies = lower
        told.append(f"Supplies fall to {lower}.")
    return told


def pass_interval(
    siege: Siege, rng: random.Random, saga: Saga | None = None
) -> list[str]:
    """The time to the next siege event, and the supplies rolls it brings."""
    siege.days += interval_days(siege)
    return supplies_rolls(siege, rng, saga)
