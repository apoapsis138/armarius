"""Battles, fights and sieges: the saga's Conflicts.

A Fight is two sides of combatants, some in combat groups, with the order
they act in and a chronicle of every blow (rules.fight plays them). A
Siege is a castle, its garrison and the army besieging it, with the time
the siege has run and a chronicle of its events (rules.siege).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from .character import Wounds
from .common import FatigueLevel, known_fields
from .traits import new_instance_id

#: A combatant drawn from a character's sheet, from a Bestiary creature,
#: or typed in.
CHARACTER_FIGHTER, CREATURE_FIGHTER, TYPED_FIGHTER = "character", "creature", "typed"
#: The four walls every besieged castle is taken to have (Lords of Men p.
#: 111).
WALLS: tuple[str, ...] = ("North", "East", "South", "West")


@dataclass
class Combatant:
    """One fighter. A character's figures come from its sheet, with the
    weapon `weapon_id` names, and its wounds and Fatigue go onto the sheet;
    a creature's or a typed fighter's figures are kept here, copied from
    the Bestiary (its attack `weapon_id`) or typed, with their own wounds
    and Fatigue, so ten boglins from one stat block are ten fighters."""

    name: str = ""
    kind: str = TYPED_FIGHTER
    #: The character's or creature's id.
    ref_id: str = ""
    weapon_id: str = ""
    init: int = 0
    attack: int | None = 0
    defence: int = 0
    damage: int | None = 0
    soak: int = 0
    size: int = 0
    #: The Combat Ability, for Exertion and a trained group's bonus.
    ability: int = 0
    leadership: int = 0
    #: Fighting from horseback; a typed fighter's or creature's Ride score
    #: (a character's comes from its sheet).
    mounted: bool = False
    ride: int = 0
    #: The id of a combatant on its side it defends, as a shield grog
    #: defends a magus; "" for none.
    defends: str = ""
    #: A typed fighter's or creature's Magic Resistance (a creature's
    #: Might), against spells and devices; a character's comes from its
    #: sheet.
    resistance: int = 0
    wounds: Wounds = field(default_factory=Wounds)
    fatigue_level: FatigueLevel = "fresh"
    #: Invisible: how clear the signs that betray it are (a key of
    #: rules.magic_combat.CLARITIES); "" when it can be seen.
    invisible: str = ""
    #: Invisible: it fights with a non-magical weapon picked up after
    #: turning invisible, which Magic Resistance doesn't keep out (older
    #: saves load without one).
    weapon_after_invisible: bool = False
    #: Why it no longer fights ("Disengaged", "Fled"); "" while it does.
    out: str = ""
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Combatant:
        d = dict(data)
        d["wounds"] = Wounds.from_dict(d.get("wounds") or {})
        return cls(**known_fields(cls, d))


@dataclass
class FightGroup:
    """A combat group: its members' ids, the vanguard first; a trained
    group's leader, and whether its bonus goes to Attack or Defence."""

    name: str = ""
    members: list[str] = field(default_factory=list)
    trained: bool = False
    leader: str = ""
    bonus_to: str = "attack"
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FightGroup:
        d = dict(data)
        d["members"] = [str(m) for m in d.get("members") or []]
        return cls(**known_fields(cls, d))


@dataclass
class FightSide:
    """One side of a fight: its combatants and their groups (a Composite:
    a group acts as one, with its vanguard's figures). A side may fight
    under a covenant's arms."""

    name: str = ""
    covenant_id: str = ""
    combatants: list[Combatant] = field(default_factory=list)
    groups: list[FightGroup] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FightSide:
        d = dict(data)
        d["combatants"] = [Combatant.from_dict(c) for c in d.get("combatants") or []]
        d["groups"] = [FightGroup.from_dict(g) for g in d.get("groups") or []]
        return cls(**known_fields(cls, d))


@dataclass
class FightEntry:
    """A line of the fight's chronicle, with the working of the blow."""

    round: int
    text: str
    lines: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FightEntry:
        d = dict(data)
        d["lines"] = [str(x) for x in d.get("lines") or []]
        return cls(**known_fields(cls, d))


@dataclass
class Grip:
    """A grapple: `held` is held by `by` with Grapple Strength `strength`
    (both units' ids)."""

    held: str
    by: str
    strength: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Grip:
        d = dict(data)
        if "held" not in d or "by" not in d:
            raise ValueError(f"A grapple needs who is held and by whom: {d!r}")
        return cls(str(d["held"]), str(d["by"]), int(d.get("strength") or 0))


@dataclass
class Fight:
    """A fight in the saga. `round` is 0 until initiative is rolled; then
    `order` lists who acts (a group's or a lone combatant's id), highest
    Initiative first, and `turn` is the one acting now."""

    name: str
    place: str = ""
    year: int = 1220
    season: str = "Spring"
    sides: list[FightSide] = field(default_factory=list)
    round: int = 0
    order: list[str] = field(default_factory=list)
    initiative: dict[str, int] = field(default_factory=dict)
    turn: int = 0
    #: Who attacked each of the units this round and last (for
    #: disengaging), and each unit's tries at disengaging.
    attacked_by: dict[str, list[str]] = field(default_factory=dict)
    attacked_last: dict[str, list[str]] = field(default_factory=dict)
    disengage_tries: dict[str, int] = field(default_factory=dict)
    #: Range increments between the sides: 0 hand to hand.
    range: int = 0
    #: The Magic aura where they fight, for the spells cast in it.
    aura: int = 0
    grips: list[Grip] = field(default_factory=list)
    #: Each group's successful splits this round, by its unit id.
    splits: dict[str, int] = field(default_factory=dict)
    #: The units that have located each invisible combatant, by its id.
    located: dict[str, list[str]] = field(default_factory=dict)
    log: list[FightEntry] = field(default_factory=list)
    #: How it ended ("The Covenant win the fight"); "" while it goes on.
    over: str = ""
    #: Whether its ending is written in its fighters' Diaries.
    recorded: bool = False
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Fight:
        d = dict(data)
        d["sides"] = [FightSide.from_dict(s) for s in d.get("sides") or []]
        d["log"] = [FightEntry.from_dict(e) for e in d.get("log") or []]
        d["grips"] = [Grip.from_dict(g) for g in d.get("grips") or []]
        d["splits"] = {str(k): int(v) for k, v in (d.get("splits") or {}).items()}
        d["order"] = [str(x) for x in d.get("order") or []]
        d["initiative"] = {
            str(k): int(v) for k, v in (d.get("initiative") or {}).items()
        }
        for key in ("attacked_by", "attacked_last"):
            d[key] = {
                str(k): [str(x) for x in v] for k, v in (d.get(key) or {}).items()
            }
        d["disengage_tries"] = {
            str(k): int(v) for k, v in (d.get("disengage_tries") or {}).items()
        }
        d["located"] = {
            str(k): [str(x) for x in v] for k, v in (d.get("located") or {}).items()
        }
        return cls(**known_fields(cls, d))


@dataclass
class SiegeEvent:
    """A line of the siege's chronicle: the day it came (from the siege's
    start), what it was, and its working."""

    day: int
    kind: str
    text: str
    lines: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SiegeEvent:
        d = dict(data)
        d["lines"] = [str(x) for x in d.get("lines") or []]
        return cls(**known_fields(cls, d))


def _four(values: Any, default: int = 0) -> list[int]:
    found = [int(v) for v in values or []][: len(WALLS)]
    return found + [default] * (len(WALLS) - len(found))


@dataclass
class Siege:
    """A siege (Lords of Men pp. 111-116): the castle's Garrison (combat
    groups), Defenses and Supplies, its four walls' damage levels, the
    besieging army's miners, engines and soldiers and where they stand,
    each side's experts, and the days the siege has run."""

    name: str
    castle: str = ""
    holder: str = ""
    besieger: str = ""
    year: int = 1220
    season: str = "Spring"
    size: int = 9
    garrison: int = 10
    defenses: str = "Standard"
    supplies: str = "Standard"
    enchanted: bool = False
    moat: bool = False
    #: Each wall's damage levels left (North, East, South, West); None
    #: until the first blow lands, meaning every wall whole.
    walls: list[int] | None = None
    #: A whole wall's damage levels, fixed when the siege's first event is
    #: played (Defense Bonus x the size's modifier, Lords of Men p. 112), so
    #: a mine that lowers the Defenses leaves the walls' measure alone.
    #: None until then: worked out from the Defenses and Size as they stand.
    wall_max: int | None = None
    miners: int = 0
    #: Siege engines by kind (rules.siege.ENGINES keys): how many.
    engines: dict[str, int] = field(default_factory=dict)
    soldiers: int = 0
    #: The besiegers' combat groups at each wall, and the garrison's.
    besieger_walls: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    garrison_walls: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    #: The experts' totals before the die: the besiegers' Intelligence +
    #: Profession: Sapper and Intelligence + Siege Weapon; the castle's
    #: Intelligence + Profession: Sapper and + Profession: Siege Engineer.
    sapper: int = 0
    gunner: int = 0
    counter_sapper: int = 0
    engineer: int = 0
    days: int = 0
    supply_rolls: int = 0
    #: The day the next supplies roll comes due: the last one's day plus
    #: the Supplies interval as it then stood (Lords of Men p. 112). None
    #: before the first interval is counted: the interval from day 0.
    next_supply_day: int | None = None
    events: list[SiegeEvent] = field(default_factory=list)
    #: How it ended ("Surrendered", "Breached", "Raised"); "" while it runs.
    ended: str = ""
    #: Whether its ending is written in the linked records' Diaries.
    recorded: bool = False
    #: The records whose diaries its ending is written into: the covenant
    #: that holds or besieges the castle, the castle as a neighbour (a lord
    #: or a place) and the besieging lord.
    covenant_id: str = ""
    castle_id: str = ""
    besieger_id: str = ""
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Siege:
        d = dict(data)
        d["events"] = [SiegeEvent.from_dict(e) for e in d.get("events") or []]
        d["engines"] = {str(k): int(v) for k, v in (d.get("engines") or {}).items()}
        if d.get("walls") is not None:
            d["walls"] = _four(d["walls"])
        d["besieger_walls"] = _four(d.get("besieger_walls"))
        d["garrison_walls"] = _four(d.get("garrison_walls"))
        return cls(**known_fields(cls, d))


@dataclass
class BattleSide:
    """One army in a battle: who it is (a neighbour of the Region, such as
    a lord, or a covenant, or just a name), its combat groups now, its
    commander's Deployment Total and its baggage groups."""

    name: str = ""
    neighbour_id: str = ""
    covenant_id: str = ""
    groups: int = 0
    deployment: int = 0
    baggage: int = 0
    #: Fighting on its home ground: only then does a lord's title raise
    #: his levies (Lords of Men pp. 31, 102).
    at_home: bool = False
    # A fleet battle (Tales of Power pp. 106-110): the side's ships.
    #: The ids of its covenant's ship Possessions that sail with it.
    ships: list[str] = field(default_factory=list)
    #: Ships besides those, kept on no covenant's Possessions.
    other_ships: int = 0
    #: The character whose seafaring Ability takes Area Lore's place in
    #: its Deployment Total ("" for none named).
    pilot_id: str = ""
    #: Its ships are bearded: iron plates on their prows.
    bearded: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BattleSide:
        d = known_fields(cls, data)
        name = str(d.get("name") or "a battle's side")
        ships = d.get("ships") or []
        if not isinstance(ships, list):
            raise ValueError(f"Battle side {name}: ships must be a list of ids")
        d["ships"] = [str(s) for s in cast(list[Any], ships)]
        other = d.get("other_ships", 0)
        if isinstance(other, bool) or not isinstance(other, int) or other < 0:
            raise ValueError(
                f"Battle side {name}: other_ships must be a whole number, not {other!r}"
            )
        return cls(**d)


@dataclass
class BattleEvent:
    """A battlefield event played: the character at its heart (an id) and
    the side they fought on, the maneuver, the enemy unit and its size,
    whether the initiative was given up, its Event Total, whether that
    side won it, and the combat groups the losing side lost."""

    who: str = ""
    side: int = 0
    maneuver: str = "Defend"
    enemy: str = "Standard"
    size: str = "Even"
    initiative: bool = False
    total: int = 0
    won: bool = False
    losses: int = 0
    #: The losing commander's Morale roll after it, and his rally at the
    #: next event's start when that failed (None: not rolled).
    morale: int | None = None
    rally: int | None = None
    # At sea (Tales of Power pp. 106-110).
    #: What the event was, told at sea (a key of rules.fleet_battle.
    #: FLEET_EVENTS); "" on land.
    deed: str = ""
    #: The ship Possessions engaged in it, on either side, and each side's
    #: other ships engaged (first side, second side).
    engaged_ships: list[str] = field(default_factory=list)
    engaged_other: list[int] = field(default_factory=lambda: [0, 0])
    #: The enemy threw naptha bombs.
    naptha: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BattleEvent:
        d = known_fields(cls, data)
        ships = d.get("engaged_ships") or []
        other = d.get("engaged_other") or [0, 0]
        if not isinstance(ships, list) or not isinstance(other, list):
            raise ValueError("A battle event's engaged ships must be lists")
        d["engaged_ships"] = [str(s) for s in cast(list[Any], ships)]
        counts: list[int] = []
        for value in cast(list[Any], other)[:2]:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"A battle event's other ships engaged must be whole "
                    f"numbers, not {value!r}"
                )
            counts.append(value)
        d["engaged_other"] = counts + [0] * (2 - len(counts))
        return cls(**d)


@dataclass
class Battle:
    """A battle between two armies (Lords of Men, Massed Combat), kept once
    in the saga and shown on the page of each lord it names."""

    name: str
    place: str = ""
    year: int = 1220
    season: str = "Spring"
    sides: list[BattleSide] = field(default_factory=list)
    events: list[BattleEvent] = field(default_factory=list)
    id: str = field(default_factory=new_instance_id)
    #: Fought at sea, between fleets (Tales of Power pp. 106-110).
    at_sea: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Battle:
        d = dict(data)
        d["sides"] = [BattleSide.from_dict(s) for s in d.get("sides") or []]
        d["events"] = [BattleEvent.from_dict(e) for e in d.get("events") or []]
        return cls(**known_fields(cls, d))


def battle_from_lord(lord_id: str, index: int, entry: dict[str, Any]) -> Battle:
    """A battle as older saves kept it, in its lord's details ({"name",
    "enemy", "ours", "theirs", "our_deployment", "their_deployment",
    "baggage", "events"}), as a saga's Battle with the lord its first
    side. Its id comes from the lord's and its place in his list, so reading
    the same old file twice gives the same saga."""

    def number(key: str) -> int:
        value = entry.get(key) or 0
        if (
            not isinstance(value, int | float | str)
            or not str(value).lstrip("-").isdigit()
        ):
            raise ValueError(f"A battle's {key} should be a number, not {value!r}.")
        return int(value)

    return Battle(
        str(entry.get("name") or "A battle"),
        sides=[
            BattleSide(
                neighbour_id=lord_id,
                groups=number("ours"),
                deployment=number("our_deployment"),
                baggage=number("baggage"),
            ),
            BattleSide(
                str(entry.get("enemy") or ""),
                groups=number("theirs"),
                deployment=number("their_deployment"),
            ),
        ],
        events=[BattleEvent.from_dict(e) for e in entry.get("events") or []],
        id=f"{lord_id}-battle-{index}",
    )
