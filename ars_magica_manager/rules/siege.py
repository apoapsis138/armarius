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
  step down, and a win at a Shoddy wall breaches the castle),
  or the garrison sallies out (a Battle Ease Factor 9 event that removes
  the units it targets). A stockade's supplies rolls come due at the
  Supplies interval. Time is counted in days: a week 7, a month 30, a
  season 91, a year 364.
- Each check comes an interval after the last, at the Supplies as they
  then stand, so a step down brings the next roll sooner but never rolls
  for days already past; an interval that ends without a stockade passes
  with no roll (p. 112).
- A whole wall's damage levels are fixed as the siege's first event is
  played: a mine lowers the Defense Quality and its Bonus (p. 114), not
  the walls' measure, and a wall at 0 stays at 0. Seal the Breach (CrTe 20
  ritual, p. 116; level from the errata, p. 75) restores up to five
  damage levels, never past that measure.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import WALLS, Outwork, Saga, Siege
from . import dice
from .scores import ability_level

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


#: Conjuration of Bread's bonus to a season's supplies rolls (p. 116).
BREAD_BONUS = 7


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
UNDERMINE, ARTILLERY, ESCALADE, SALLY, SEAL, WAIT, COUNTER = (
    "Undermine a wall",
    "Bombard a wall",
    "Escalade",
    "The garrison sallies out",
    "The magi seal a breach",
    "Keep the stockade",
    "The garrison's engines fire back",
)
EVENTS = (UNDERMINE, ARTILLERY, ESCALADE, SALLY, SEAL, COUNTER, WAIT)
#: The besiegers' engines a counter-battery aims at: each is targeted on
#: its own, its Defense an Ease Factor of 6 (Lords of Men pp. 113, 116).
ENGINE_EASE = 6
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
    or more), as they were set when the siege began. A mine lowers the
    Defenses, not this measure (pp. 112, 114)."""
    if siege.wall_max is not None:
        return siege.wall_max
    return wall_damage_levels(castle_of(siege).defense_bonus(), siege.size)


def begin(siege: Siege) -> None:
    """Fix a whole wall's damage levels, once, as the siege's first event
    is played; and the walls' levels left, all whole until a blow lands."""
    if siege.wall_max is None:
        siege.wall_max = full_wall(siege)
    if siege.walls is None:
        siege.walls = [siege.wall_max] * len(WALLS)


def walls(siege: Siege) -> list[int]:
    """Each wall's damage levels left."""
    if siege.walls is not None:
        return list(siege.walls)
    return [full_wall(siege)] * len(WALLS)


def migrate(siege: Siege) -> None:
    """A siege from a save older than the walls' fixed measure and the
    supplies roll's day: a whole wall is the larger of what the Defenses
    give now and the most any wall has left (a mine may have lowered the
    Defenses since); the next supplies roll is the first interval's end,
    counted from the rolls made, after today."""
    started = siege.days > 0 or bool(siege.events) or siege.walls is not None
    if siege.wall_max is None and started:
        siege.wall_max = max(
            wall_damage_levels(castle_of(siege).defense_bonus(), siege.size),
            *(siege.walls or [0]),
        )
    if siege.next_supply_day is None and started:
        every = supplies_interval(siege)
        due = (siege.supply_rolls + 1) * every
        while due <= siege.days:
            due += every
        siege.next_supply_day = due


SEAL_THE_BREACH = 5


def seal_breach(siege: Siege, wall: int) -> Played:
    """Seal the Breach (CrTe 20 ritual, Lords of Men p. 116; level from the
    errata, p. 75): a wall gets back up to five damage levels, never more
    than it had when the siege began."""
    begin(siege)
    left = walls(siege)
    name = WALLS[wall]
    mended = min(SEAL_THE_BREACH, full_wall(siege) - left[wall])
    if mended <= 0:
        return Played(f"The {name} wall stands whole: there is no breach to seal.")
    left[wall] += mended
    siege.walls = left
    plural = "s" if mended > 1 else ""
    return Played(
        f"Seal the Breach knits the {name} wall: {mended} damage level{plural} "
        f"restored, {left[wall]} of {full_wall(siege)}.",
        [f"Seal the Breach: up to {SEAL_THE_BREACH} damage levels (p. 116)"],
    )


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


def engine_groups(
    siege: Siege, engines: dict[str, int] | None = None
) -> list[tuple[str, int]]:
    """The wall-breaking engines in groups of up to five: (kind, how
    many); the besiegers' unless `engines` names another side's."""
    found: list[tuple[str, int]] = []
    held = siege.engines if engines is None else engines
    for kind in WALL_BREAKERS:
        left = held.get(kind, 0)
        while left > 0:
            found.append((kind, min(MAX_ENGINE_GROUP, left)))
            left -= MAX_ENGINE_GROUP
    return found


#: A lord's castle's Defenses by its kind: a free choice Standard, a minor
#: castle Superior, a great castle Excellent (Lords of Men p. 111).
CASTLE_KIND_DEFENSES: dict[str, str] = {
    "free": "Standard",
    "minor": "Superior",
    "great": "Excellent",
}
#: Each expert's Ability, after Intelligence (pp. 113-114).
EXPERT_ABILITIES: dict[str, str] = {
    "sapper": "Profession: Sapper",
    "gunner": "Siege Weapon",
    "counter_sapper": "Profession: Sapper",
    "engineer": "Profession: Siege Engineer",
}
#: Profession Sapper can't be used untrained; Profession Miner may run a
#: mine with three botch dice (p. 114).
MINER = "Profession: Miner"
MINER_BOTCH_DICE = 3


@dataclass(frozen=True)
class Expert:
    """An expert's total before the die, his botch dice, and why he can't
    do the work ("" when he can)."""

    total: int
    botch_dice: int = 1
    problem: str = ""


def expert(saga: Saga | None, siege: Siege, role: str) -> Expert:
    """The siege's expert in `role`: a character's Intelligence + Ability
    when one is named, else the typed total (pp. 113-114)."""
    typed = getattr(siege, role)
    who = saga.character(siege.experts.get(role)) if saga is not None else None
    if who is None:
        return Expert(typed)
    intelligence = who.characteristics.intelligence
    ability = EXPERT_ABILITIES[role]
    score = ability_level(who, ability)
    if score or not ability.startswith("Profession: Sapper"):
        return Expert(intelligence + score)
    miner = ability_level(who, MINER)
    if miner:
        return Expert(intelligence + miner, MINER_BOTCH_DICE)
    return Expert(
        intelligence,
        problem=f"{who.name} has no Profession: Sapper, which can't be used "
        "untrained (Lords of Men p. 114).",
    )


def _roll(
    rng: random.Random,
    saga: Saga | None,
    label: str,
    base: int,
    lines: list[str],
    botch_dice: int = 1,
) -> tuple[int, bool]:
    die = dice.stress_die(rng, botch_dice, saga=saga)
    if die.botched:
        lines.append(f"{label}: {base} + a botch")
        # A botch adds nothing, so a negative base stays negative (DE p. 393).
        return min(0, base), True
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
    begin(siege)
    lines: list[str] = []
    bonus = wall_bonus(siege, wall, against_mines=True)
    sapper = expert(saga, siege, "sapper")
    if sapper.problem:
        return Played(sapper.problem)
    if sapper.botch_dice > 1:
        lines.append(
            f"A miner, not a sapper, runs the mine: {sapper.botch_dice} botch dice "
            "(p. 114)."
        )
    attack, botched = _roll(
        rng, saga, "Mine Attack", sapper.total, lines, sapper.botch_dice
    )
    defence, guard_botched = _roll(
        rng,
        saga,
        "Castle Defense",
        expert(saga, siege, "counter_sapper").total + bonus,
        lines,
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
    siege: Siege,
    wall: int,
    rng: random.Random,
    saga: Saga | None = None,
    group_walls: list[int] | None = None,
) -> Played:
    """Each group of up to five engines makes one attack on its wall (the
    one `group_walls` names for it, else `wall`): several walls can be
    struck in one event given the engines (p. 114). A hit costs the wall a
    damage level for each engine in the group; each group's attack meets
    the castle's defence at its wall."""
    groups = engine_groups(siege)
    if not groups:
        return Played("The besiegers have no mangonel or trebuchet to bombard with.")
    begin(siege)
    lines: list[str] = []
    left = walls(siege)
    struck: dict[int, int] = {}
    targets = [
        (group_walls[i] if group_walls and i < len(group_walls) else wall)
        for i in range(len(groups))
    ]
    for (kind, count), at in zip(groups, targets, strict=True):
        bonus = wall_bonus(siege, at)
        plural = "s" if count > 1 else ""
        attack, botched = _roll(
            rng,
            saga,
            f"{count} {kind}{plural}",
            expert(saga, siege, "gunner").total + ENGINES[kind][1],
            lines,
        )
        defence, _ = _roll(
            rng,
            saga,
            "Castle Defense",
            expert(saga, siege, "engineer").total + bonus,
            lines,
        )
        if not botched and attack > defence:
            hit = min(count, left[at])
            left[at] -= hit
            struck[at] = struck.get(at, 0) + hit
    siege.walls = left
    if not struck:
        named = " and ".join(WALLS[w] for w in sorted(set(targets)))
        return Played(f"The engines pound the {named} wall to no effect.", lines)
    told = []
    for at, lost in sorted(struck.items()):
        plural = "s" if lost > 1 else ""
        end = ": it no longer gives its Defense Bonus" if left[at] == 0 else ""
        told.append(
            f"the {WALLS[at]} wall {lost} damage level{plural}, {left[at]} left{end}"
        )
    return Played("The engines batter " + "; ".join(told) + ".", lines)


def counter_battery(
    siege: Siege,
    target: str,
    rng: random.Random,
    saga: Saga | None = None,
    targets: list[str] | None = None,
) -> Played:
    """The garrison's mangonels and trebuchets fire at the besiegers'
    engines, each group once at the engine it picks (`targets`, by group;
    `target` for a group with none): Intelligence + Siege Weapon + the
    engine's Attack + stress die, a hit destroying that engine (Lords of Men
    pp. 114-116, which target engines individually; only a mangonel's or
    trebuchet's hit destroys one, so ballistae don't fire). The book gives
    the counter-battery no Ease Factor: 6, an engine's own Defense, is the
    app's (p. 113)."""
    groups = engine_groups(siege, siege.garrison_engines)
    if not groups:
        return Played("The garrison has no mangonel or trebuchet to fire back with.")
    begin(siege)
    lines: list[str] = []
    destroyed = 0
    for index, (kind, count) in enumerate(groups):
        aim = (targets or [])[index] if index < len(targets or []) else target
        if siege.engines.get(aim, 0) <= 0:
            continue
        plural = "s" if count > 1 else ""
        attack, botched = _roll(
            rng,
            saga,
            f"The garrison's {count} {kind}{plural}",
            siege.garrison_gunner + ENGINES[kind][1],
            lines,
        )
        if not botched and attack >= ENGINE_EASE:
            siege.engines[aim] -= 1
            destroyed += 1
            lines.append(f"It destroys one of the besiegers' {aim.lower()}s.")
            if siege.engines[aim] == 0:
                siege.engines.pop(aim, None)
    if not destroyed:
        return Played("The garrison's engines miss the besiegers' engines.", lines)
    plural = "s" if destroyed > 1 else ""
    return Played(
        f"The garrison's engines destroy {destroyed} of the besiegers' engine{plural}.",
        lines,
    )


# -- outworks (p. 114, optional) ----------------------------------------------


def outwork(siege: Siege) -> Outwork | None:
    """The first outwork not yet taken: the besiegers' events strike it
    before the castle (p. 114)."""
    return next((o for o in siege.outworks if not o.taken), None)


def outwork_walls(siege: Siege, work: Outwork) -> int:
    """An outwork's damage levels left: its Defense Bonus x the castle's
    size modifier until struck (its Size is the app's: the castle's)."""
    if work.walls is not None:
        return work.walls
    return wall_damage_levels(DEFENSES[work.defenses][1], siege.size)


def strike_outwork(
    siege: Siege, event: str, won: bool, rng: random.Random, saga: Saga | None
) -> Played:
    """An event aimed at the outwork: a mine lowers its Defense Quality,
    the engines its walls, an escalade won or its walls at 0 take it."""
    work = outwork(siege)
    assert work is not None
    begin(siege)
    lines: list[str] = []
    bonus = DEFENSES[work.defenses][1]
    if event == UNDERMINE:
        sapper = expert(saga, siege, "sapper")
        if sapper.problem:
            return Played(sapper.problem)
        attack, _ = _roll(
            rng, saga, "Mine Attack", sapper.total, lines, sapper.botch_dice
        )
        defence, _ = _roll(
            rng,
            saga,
            "Outwork Defense",
            expert(saga, siege, "counter_sapper").total + bonus,
            lines,
        )
        if attack > defence and (lower := worse(work.defenses)) is not None:
            work.defenses = lower
            return Played(f"The mine brings {work.name}'s Defenses to {lower}.", lines)
        return Played(f"The mine under {work.name} is countered.", lines)
    if event == ARTILLERY:
        left = outwork_walls(siege, work)
        for kind, count in engine_groups(siege):
            attack, botched = _roll(
                rng,
                saga,
                f"{count} {kind}",
                expert(saga, siege, "gunner").total + ENGINES[kind][1],
                lines,
            )
            defence, _ = _roll(
                rng,
                saga,
                "Outwork Defense",
                expert(saga, siege, "engineer").total + (bonus if left else 0),
                lines,
            )
            if not botched and attack > defence:
                left = max(0, left - count)
        work.walls = left
        if left == 0:
            work.taken = True
            return Played(f"{work.name}'s walls fall: it is taken.", lines)
        return Played(
            f"The engines batter {work.name}: {left} damage levels left.", lines
        )
    if event == ESCALADE:
        if won:
            work.taken = True
            return Played(f"The besiegers storm {work.name}: it is taken.")
        return Played(f"The assault on {work.name} is thrown back.")
    return Played("Nothing strikes the outwork.")


def step_down(groups: int) -> int:
    """The Garrison a step down: the top of the step below (half, at the
    lowest step, where the book gives no step below)."""
    lower = [top for top in GARRISON_STEPS if top < groups]
    return lower[-1] if lower else groups // 2


def escalade(siege: Siege, wall: int, besiegers_won: bool) -> Played:
    """An escalade at a wall, played as a battlefield event: a besiegers'
    win takes the Garrison a step down, and at a Shoddy wall breaches the
    castle (Lords of Men p. 115). A wall battered to 0 no longer gives its
    Defense Bonus (p. 114), which the escalade's battle already counts; it
    isn't a breach of itself."""
    name = WALLS[wall]
    if not besiegers_won:
        return Played(f"The escalade at the {name} wall is thrown back.")
    siege.garrison = step_down(siege.garrison)
    if siege.defenses == QUALITIES[0]:
        siege.ended = "Breached"
        return Played(
            f"The besiegers carry the {name} wall and breach the castle: fight the "
            "battle inside with the battle rules."
        )
    return Played(
        f"The besiegers win a foothold on the {name} wall: the garrison falls to "
        f"{siege.garrison} combat groups."
    )


def sally(siege: Siege, target: str, won: bool, *, units: int = 1) -> Played:
    """The garrison sallies out against the miners, a group of engines or
    the soldiers (Battle Ease Factor 9); a win removes those units: the
    `units` groups of soldiers it struck (p. 115)."""
    if not won:
        return Played(f"The sally against the {target.lower()} is beaten back.")
    if target == "Miners":
        siege.miners = 0
    elif target == "Soldiers":
        siege.soldiers = max(0, siege.soldiers - max(1, units))
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
    held = stockaded(siege)
    while not siege.ended:
        day = next_supplies_day(siege)
        if day > siege.days:
            break
        if held:
            told += _supplies_roll(siege, day, rng, saga)
        # The next check is an interval on from this one, at the Supplies
        # as they now stand: a step down brings it sooner, never earlier
        # than this day (p. 112).
        siege.next_supply_day = day + supplies_interval(siege)
    return told


def supplies_interval(siege: Siege) -> int:
    """Days between supplies rolls, by the Supplies now."""
    return INTERVAL_DAYS[SUPPLIES[siege.supplies][0]]


def next_supplies_day(siege: Siege) -> int:
    """The day the next supplies roll comes due."""
    if siege.next_supply_day is not None:
        return siege.next_supply_day
    return (siege.supply_rolls + 1) * supplies_interval(siege)


def _supplies_roll(
    siege: Siege, day: int, rng: random.Random, saga: Saga | None
) -> list[str]:
    """One supplies roll, on `day` of the siege."""
    siege.supply_rolls += 1
    castle = castle_of(siege)
    ease = castle.supplies_ease(day // DAYS_PER_YEAR)
    die = dice.stress_die(rng, disease_botch_dice(day // DAYS_PER_SEASON), saga=saga)
    bread = (
        BREAD_BONUS if siege.bread_until is not None and day < siege.bread_until else 0
    )
    total = 0 if die.botched else castle.supplies_bonus() + bread + die.value
    told = [
        f"Supplies roll: {total} against {ease}"
        + (f" (Conjuration of Bread +{bread})" if bread else "")
    ]
    if die.botched:
        told.append("Disease breaks out within the castle.")
    if total >= ease:
        return told
    lower = worse(siege.supplies)
    if lower is None:
        siege.ended = "Surrendered"
        told.append("The supplies are gone: the castle surrenders.")
        return told
    siege.supplies = lower
    told.append(
        f"Supplies fall to {lower}; those inside make deprivation checks (ArM5 p. 180)."
    )
    return told


def pass_interval(
    siege: Siege, rng: random.Random, saga: Saga | None = None
) -> list[str]:
    """The time to the next siege event, and the supplies rolls it brings."""
    siege.days += interval_days(siege)
    return supplies_rolls(siege, rng, saga)
