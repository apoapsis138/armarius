"""A battlefield event played as a fight (Lords of Men pp. 105-108): the
fight the event's Maneuver, Enemy and Size make, and what the fight says
of the event once it is over.

The leader's own combat group faces the enemy groups the Size names
(Lesser: one about half his own; Even: one; Outnumbered: two;
Overwhelmed: three; I Stand Alone: he alone against a full group) of the
troops the Enemy names (Inexpensive levies, Standard infantry or archers,
Expensive knights or serjeants, the Baggage guarded by levies; a Special
enemy is the storyguide's, added with Add Combatant), each from the
Standard Combat Groups table (p. 108). Weight of Numbers adds that many
men to each group of the side it favours (p. 106). Knights, serjeants and
infantry fight as trained groups; archers, levies and baggage don't
(p. 108). The event lasts five rounds unless it says otherwise.

What the fight proposes is only a proposal: an event is won by its
Maneuver's own condition (a Defend held long enough, a Take held against
the counter-attack, a Heroic Gesture whose leader dies), which the Battle
Event form asks (pp. 106-108).

Pattern: Factory Method: the event's choices are the template the fight
is built from, as Form a Group builds a group.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import (
    CHARACTER_FIGHTER,
    Battle,
    Combatant,
    Fight,
    FightGroup,
    FightSide,
    Saga,
)
from .rules import battle
from .rules import fight as fight_rules

SOURCE = "Lords of Men, Battlefield Events, pp. 105-108"
#: A battlefield event lasts five combat rounds unless it says otherwise.
EVENT_ROUNDS = 5

#: The units an Enemy names, by the Standard Combat Groups table's names.
ENEMY_UNITS: dict[str, tuple[str, ...]] = {
    "Inexpensive": ("Levy",),
    "Standard": ("Infantry", "Archer"),
    "Expensive": ("Knight", "Serjeant"),
    "Special": (),
    "Baggage": ("Levy",),
}
#: How many enemy groups a Size sets against the leader's one.
SIZE_GROUPS: dict[str, int] = {
    "Lesser": 1,
    "Even": 1,
    "Outnumbered": 2,
    "Overwhelmed": 3,
    "I Stand Alone": 1,
}

#: Each Maneuver's ways to win or lose, as the Battle Event form offers
#: them (pp. 106-108): (key, words, whether it is a win).
WIN_CONDITIONS: dict[str, tuple[tuple[str, str, bool], ...]] = {
    "Defend": (
        ("beaten", "The attackers beaten", True),
        ("held", "Held for the rounds the storyguide set", True),
        ("taken", "Withdrew, or the place was taken", False),
    ),
    "Attack": (
        ("routed", "The enemy defeated or routed", True),
        ("repulsed", "The attack failed", False),
    ),
    "Run the Gauntlet": (
        ("reached", "The objective reached", True),
        ("stopped", "Stopped short of it", False),
    ),
    "Take": (
        ("held", "Taken, and held against the counter-attack", True),
        ("retaken", "Taken but lost to the counter-attack", False),
        ("failed", "Not taken", False),
    ),
    "Heroic Gesture": (
        ("died", "The leader died: his death secures the victory", True),
        ("survived", "He survived, meeting the storyguide's conditions", True),
        ("other", "Another player character was killed", False),
        ("failed", "It failed", False),
    ),
}


def troop_rows(unit: str) -> list[tuple[str, int]]:
    """(label, row) of the Standard Combat Groups table for a unit."""
    return [
        (f"{name}: {weapon}", i)
        for i, (name, weapon, *_figures) in enumerate(battle.STANDARD_TROOPS)
        if name == unit
    ]


def enemy_troop_options(enemy: str) -> list[tuple[str, str]]:
    """The table's rows an Enemy may field, as Select options."""
    return [
        (label, str(row))
        for unit in ENEMY_UNITS.get(enemy, ())
        for label, row in troop_rows(unit)
    ]


def own_troop_options() -> list[tuple[str, str]]:
    """The rows the leader's own group may be made of (all but baggage)."""
    return [
        (f"{name}: {weapon}", str(i))
        for i, (name, weapon, *_figures) in enumerate(battle.STANDARD_TROOPS)
        if name != "Baggage"
    ]


def _men(row: int, count: int, prefix: str) -> list[Combatant]:
    unit, weapon, init, attack, defence, damage, soak = battle.STANDARD_TROOPS[row]
    return [
        Combatant(
            f"{prefix}{unit} {n + 1}",
            init=init,
            attack=attack,
            defence=defence,
            damage=damage,
            soak=soak,
            mounted="(mounted)" in weapon,
        )
        for n in range(count)
    ]


def _group(name: str, men: list[Combatant], unit: str) -> FightGroup:
    return FightGroup(
        name,
        [c.id for c in men],
        trained=unit in battle.TRAINED_UNITS,
        leader=men[0].id if men else "",
    )


@dataclass(frozen=True)
class Template:
    """What the Battle Event form chose: the leader, the side, the
    Enemy, the Size, the Weight of Numbers for the leader's side, and the
    rows of the leader's group and the enemy's."""

    who: str
    weapon_id: str
    side_name: str
    enemy_name: str
    enemy: str
    size: str
    weight: int
    own_row: int
    enemy_row: int | None
    #: A Knight Banneret's or Mercenary Captain's company: one group whatever
    #: the Weight of Numbers (p. 104).
    company: bool = False


def fight_for(saga: Saga, entry: Battle, stage: int, made: Template) -> Fight:
    """The fight of the event: the leader and his group, and the enemy's
    groups (pp. 105-108)."""
    leader = saga.character(made.who)
    ours: list[Combatant] = []
    groups: list[FightGroup] = []
    if leader is not None:
        ours.append(
            Combatant(leader.name, CHARACTER_FIGHTER, leader.id, made.weapon_id)
        )
    alone = made.size == "I Stand Alone"
    if not alone:
        size = (
            battle.GROUP_SIZE
            if made.company
            else battle.group_members(made.weight, ours=True)
        )
        unit = battle.STANDARD_TROOPS[made.own_row][0]
        men = _men(made.own_row, size - len(ours), "")
        ours += men
        groups.append(_group(f"{made.side_name}'s group", ours, unit))
        groups[-1].leader = ours[0].id
    theirs: list[Combatant] = []
    their_groups: list[FightGroup] = []
    if made.enemy_row is not None:
        unit = battle.STANDARD_TROOPS[made.enemy_row][0]
        size = battle.group_members(made.weight, ours=False)
        if made.size == "Lesser":
            size = max(1, -(-len(ours) // 2))
        for g in range(SIZE_GROUPS[made.size]):
            men = _men(made.enemy_row, size, f"{g + 1}. ")
            theirs += men
            their_groups.append(_group(f"{unit}s {g + 1}", men, unit))
    if made.enemy == "Baggage":
        row = next(i for i, r in enumerate(battle.STANDARD_TROOPS) if r[0] == "Baggage")
        men = _men(row, battle.GROUP_SIZE, "")
        theirs += men
        their_groups.append(_group("The baggage", men, "Baggage"))
    return Fight(
        f"{entry.name}: {battle.stage_name(stage)}",
        place=entry.place,
        year=entry.year,
        season=entry.season,
        sides=[
            FightSide(made.side_name, combatants=ours, groups=groups),
            FightSide(made.enemy_name, combatants=theirs, groups=their_groups),
        ],
        battle_id=entry.id,
    )


#: A company that is one group whatever the Weight of Numbers (p. 104).
COMPANY_VIRTUES = frozenset({"vf_mercenary_captain", "vf_knight_banneret"})


def leads_a_company(saga: Saga, who: str) -> bool:
    character = saga.character(who)
    return character is not None and any(
        vf.vf_id in COMPANY_VIRTUES for vf in character.virtues_flaws
    )


def pending(saga: Saga, entry: Battle) -> Fight | None:
    """The fight made for the battle's next event, not yet recorded."""
    used = {e.fight_id for e in entry.events if e.fight_id}
    return next(
        (f for f in saga.fights if f.battle_id == entry.id and f.id not in used),
        None,
    )


@dataclass(frozen=True)
class Proposal:
    """What a finished fight says of its event: whether the leader's side
    won it, and the combat groups each side lost in it."""

    won: bool | None
    lost_ours: int
    lost_theirs: int


def _groups_down(saga: Saga, fight: Fight, side: int) -> int:
    units = fight_rules.units(saga, fight)
    found = 0
    for group in fight.sides[side].groups:
        unit = units.get(group.id)
        if unit is not None and unit.down():
            found += 1
    return found


def proposal(saga: Saga, fight: Fight) -> Proposal:
    """The fight's verdict on the event, once it is over (won None while it
    goes on)."""
    side = fight_rules.winner(saga, fight) if fight.over else None
    return Proposal(
        None if side is None else side == 0,
        _groups_down(saga, fight, 0),
        _groups_down(saga, fight, 1),
    )


def proposal_text(saga: Saga, fight: Fight) -> str:
    """A line on the fight's verdict for the Battle Event form."""
    found = proposal(saga, fight)
    if found.won is None:
        return (
            f"The fight {fight.name} goes on: play it on Conflicts, then record "
            "the event here."
        )
    words = "won" if found.won else "lost"
    return (
        f"The fight {fight.name} is over: the event looks {words} (check the "
        f"Maneuver's condition); groups lost in it: {found.lost_ours} of "
        f"yours, {found.lost_theirs} of theirs."
    )


def condition_won(maneuver: str, key: str) -> bool | None:
    """Whether a Maneuver's condition is a win (None: not one of its)."""
    return next(
        (won for k, _words, won in WIN_CONDITIONS.get(maneuver, ()) if k == key),
        None,
    )


def template_values(values: dict[str, Any]) -> dict[str, Any]:
    """The event's choices kept with its fight, to fill the form again."""
    keys = ("who", "side", "maneuver", "enemy", "size", "initiative", "weapon")
    return {k: values.get(k) for k in keys if values.get(k) is not None}
