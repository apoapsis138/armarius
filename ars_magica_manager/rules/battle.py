"""Massed combat (Lords of Men, Chapter Eight), played as a few heroic
vignettes, each a battlefield event with a player character at its heart:

    Deployment Total     = Intelligence + Area Lore + stress die
    Territorial Advantage = Deployment Total - the enemy's
    Weight of Numbers    = by the ratio of the armies' combat groups
                           (3:2 +-1, 2:1 +-2, 3:1 +-3, 4:1 +-4)
    Event Bonus          = Maneuver + Enemy + Size
    Event Total          = Stamina + Leadership + Territorial Advantage
                           + Weight of Numbers + Event Bonus
                           (+1 for giving up the initiative)

An event is won when its Event Total reaches the stage's Battle Ease
Factor (Engaged 9, Advantage or Setback 12, Imminent Victory or Defeat
15). The losing side then loses combat groups equal to the event's Size
times the winner's Weight of Numbers bonus (when positive), of the kind
its Enemy names, and its commander makes a Morale roll against 6.

Raising an army: the lord's own vassal forces (lords.army_of), times the
Allied Troops Table's proportion for a Presence + Leadership + Affinity
simple roll (6 half, 12 equal, 18 double, 24 treble), plus mercenaries
bought from his budget (knights 15 pounds a group, serjeants 5, infantry
and archers 2, levies 1). Every ten groups (rounded up) need a group of
baggage; each one short is -1 to Leadership totals.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rounding import round_down, round_up

SOURCE = (
    "Lords of Men, Chapter Eight: Massed Combat "
    "(https://www.redcap.org/page/Lords_of_Men)"
)

#: The stages of a battle and their Battle Ease Factors.
STAGES: tuple[tuple[str, int], ...] = (
    ("Engaged", 9),
    ("Advantage or Setback", 12),
    ("Imminent Victory or Defeat", 15),
)

MANEUVERS: dict[str, int] = {
    "Defend": 0,
    "Attack": 1,
    "Run the Gauntlet": 2,
    "Take": 3,
    "Heroic Gesture": 4,
}
SIZES: dict[str, int] = {
    "Lesser": 0,
    "Even": 1,
    "Outnumbered": 2,
    "Overwhelmed": 3,
    "I Stand Alone": 4,
}
ENEMIES: dict[str, int] = {
    "Inexpensive": 0,
    "Standard": 1,
    "Expensive": 2,
    "Special": 3,
    "Baggage": 4,
}
#: The kind of combat group an Enemy is, for the losses it takes.
ENEMY_UNITS: dict[str, str] = {
    "Inexpensive": "levies",
    "Standard": "infantry",
    "Expensive": "knights",
    "Special": "special",
    "Baggage": "baggage",
}

#: Weight of Numbers: (the larger army's groups per the smaller's, bonus),
#: from the largest ratio down.
WEIGHT_OF_NUMBERS: tuple[tuple[float, int], ...] = (
    (4, 4),
    (3, 3),
    (2, 2),
    (1.5, 1),
)

#: The Allied Troops Table: (a roll of at least, proportion of the core
#: vassal force, its name), from the best down.
ALLIED_TROOPS: tuple[tuple[int, float, str], ...] = (
    (24, 3, "Treble"),
    (18, 2, "Double"),
    (12, 1, "Equal"),
    (6, 0.5, "Half"),
)

#: A mercenary combat group's cost in pounds.
MERCENARY_COST: dict[str, int] = {
    "knights": 15,
    "serjeants": 5,
    "infantry": 2,
    "archers": 2,
    "levies": 1,
}

GROUP_SIZE = 5
GROUPS_PER_BAGGAGE = 10
MORALE_EASE = 6
RALLY_EASE = 9
GIVE_UP_INITIATIVE = 1


def weight_of_numbers(ours: int, theirs: int) -> int:
    """The troupe's Weight of Numbers bonus (negative when outnumbered),
    from each army's combat groups."""
    if ours <= 0 or theirs <= 0:
        return 0
    larger, smaller = max(ours, theirs), min(ours, theirs)
    ratio = larger / smaller
    bonus = next((n for at_least, n in WEIGHT_OF_NUMBERS if ratio >= at_least), 0)
    return bonus if ours >= theirs else -bonus


def territorial_advantage(our_deployment: int, their_deployment: int) -> int:
    return our_deployment - their_deployment


def event_bonus(maneuver: str, enemy: str, size: str) -> int:
    return MANEUVERS[maneuver] + ENEMIES[enemy] + SIZES[size]


def ease_factor(stage: int) -> int:
    """The Battle Ease Factor of the `stage`th event (from 0); later events
    stay at the last stage's."""
    return STAGES[min(stage, len(STAGES) - 1)][1]


def stage_name(stage: int) -> str:
    return STAGES[min(stage, len(STAGES) - 1)][0]


@dataclass(frozen=True)
class Event:
    """One battlefield event's Event Total, before it is played out."""

    stamina: int
    leadership: int
    territorial: int
    weight: int
    maneuver: str
    enemy: str
    size: str
    gave_up_initiative: bool = False
    baggage_short: int = 0

    @property
    def bonus(self) -> int:
        return event_bonus(self.maneuver, self.enemy, self.size)

    @property
    def total(self) -> int:
        return (
            self.stamina
            + self.leadership
            - self.baggage_short
            + self.territorial
            + self.weight
            + self.bonus
            + (GIVE_UP_INITIATIVE if self.gave_up_initiative else 0)
        )

    def can_win(self, stage: int) -> bool:
        """Whether the Event Total reaches the stage's Ease Factor (below
        it the event is still played, but can't be won)."""
        return self.total >= ease_factor(stage)


def losses(size: str, winner_weight: int) -> int:
    """The combat groups the side that lost an event loses besides those
    lost in the fight itself: its Size times the winner's Weight of
    Numbers bonus, when that is positive."""
    return SIZES[size] * max(0, winner_weight)


def group_members(weight: int, *, ours: bool) -> int:
    """Combatants in one of a side's combat groups during an event: five,
    plus the Weight of Numbers bonus for the side it favours."""
    favoured = weight > 0 if ours else weight < 0
    return GROUP_SIZE + (abs(weight) if favoured else 0)


def allied_proportion(roll_total: int) -> tuple[float, str]:
    """The Allied Troops Table: the proportion of the lord's core vassal
    force his allies add for a Presence + Leadership + Affinity roll
    (nothing below 6)."""
    return next(
        (
            (share, name)
            for at_least, share, name in ALLIED_TROOPS
            if roll_total >= at_least
        ),
        (0, "None"),
    )


def allied_groups(core_groups: int, roll_total: int) -> int:
    share, _ = allied_proportion(roll_total)
    return round_down(core_groups * share)


def mercenary_cost(groups: dict[str, int]) -> int:
    """Pounds for the mercenary combat groups ({kind: groups})."""
    return sum(MERCENARY_COST[kind] * n for kind, n in groups.items())


def baggage_needed(groups: int) -> int:
    """Baggage groups an army of `groups` combat groups needs."""
    return round_up(groups / GROUPS_PER_BAGGAGE) if groups > 0 else 0
