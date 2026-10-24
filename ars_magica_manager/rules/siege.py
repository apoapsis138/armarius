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

No screen runs a siege yet: these are the rules for one still to come, and
only the tests call them.
"""

from __future__ import annotations

from dataclasses import dataclass

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
