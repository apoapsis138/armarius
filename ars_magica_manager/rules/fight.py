"""Playing a fight blow by blow (DE Chapter Eleven, Combat, pp. 394-398).

- **Initiative** is rolled once for the whole fight (Init + stress die)
  and stays the same every round; each party acts in order of decreasing
  Initiative, ties re-rolled between themselves (p. 394).
- **A blow**: the attacker's Attack + stress die against the defender's
  Defence + stress die; a hit beats it, by the Attack Advantage. The
  Damage Total (Damage + the Advantage) less the defender's Soak is read
  on the Damage Table for his Size (p. 394). Against missiles only a
  shield's Defence counts, with the Combat Ability (p. 395).
- **Groups** act as one, with the vanguard's figures; a trained group's
  other members add their Combat Abilities (at most 3 x the leader's
  Leadership) to its Attack or its Defence. A group's hit lands once for
  each member, spread as evenly as can be over the other group, the
  vanguard taking at least as many blows; the defending group's Soak is
  its vanguard's. When the vanguard or leader falls, the group splits into
  individuals (pp. 395-397).
- **Options** (pp. 397-398): Exertion spends a Fatigue level (each member's,
  in a group) for the Combat Ability on the Attack; disengaging is a
  Defence Total against every attacker of the last round, +3 for each try
  after the first; a scuffle turns the wound into Fatigue (Scuffle
  Effects), -3 to Attack and no weapon Damage with a real weapon; a
  special effect (disarm, trip...) needs its Attack Advantage instead of
  doing damage.

A character's figures come from its sheet, wounds and Fatigue included,
and the wounds it takes are written onto the sheet; a creature's or a
typed fighter's are the Combatant's own.

Pattern: a side is a Composite of combatants and groups; Unit gives both
the same face, so the fight loop never asks which it has.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .. import catalog
from ..models import (
    CHARACTER_FIGHTER,
    FATIGUE_LEVELS,
    Character,
    Combatant,
    Fight,
    FightEntry,
    FightGroup,
    FightSide,
    Possession,
    Saga,
    Wounds,
)
from . import combat, combat_groups, derived, dice, recovery
from .breakdown import Breakdown
from .lab import ability_score

SOURCE = "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Combat, pp. 394-398"
MISSILE_ABILITIES = ("Bows", "Thrown Weapon", "Crossbow")
#: The actions a unit may take on its turn.
ATTACK, EXERTION, SCUFFLE, DISENGAGE, WAIT = (
    "Attack",
    "Attack with Exertion",
    "Scuffle",
    "Disengage",
    "Wait",
)
ACTIONS: tuple[str, ...] = (
    ATTACK,
    EXERTION,
    SCUFFLE,
    *combat_groups.SPECIAL_EFFECTS,
    DISENGAGE,
    WAIT,
)
SCUFFLE_PENALTY = combat_groups.SCUFFLE_WEAPON_PENALTY
DOWN = "Out of the fight"


@dataclass
class Figures:
    """A fighter's totals before the die, penalties included."""

    init: int
    attack: int | None
    defence: int
    damage: int | None
    soak: int
    size: int
    #: Defence against missiles (a shield's, not the weapon's).
    missile_defence: int
    ability: int
    leadership: int
    #: Damage with no weapon in it, for a scuffle.
    bare_damage: int
    missile: bool = False


FIST = "weapon_fist"


def bare_hands() -> Possession:
    """The book's Fist, for a character who carries no weapon (DE p. 400)."""
    fist = catalog.load_weapon_catalog_by_id()[FIST]
    return Possession(
        kind="weapon",
        name=fist.name,
        id=FIST,
        gear_id=FIST,
        weapon_init=fist.init,
        weapon_attack=fist.attack,
        weapon_defense=fist.defense,
        weapon_damage=fist.damage,
    )


def _weapon(character: Character, weapon_id: str) -> Possession:
    """The weapon the character fights with: the one chosen, else the
    first carried, else bare hands."""
    weapons = [i for i in character.inventory if i.kind == "weapon"]
    chosen = next((w for w in weapons if w.id == weapon_id), None)
    return chosen or (weapons[0] if weapons else bare_hands())


class Fighter:
    """A combatant as the fight sees it, whatever it was drawn from."""

    def __init__(self, saga: Saga, combatant: Combatant) -> None:
        self.saga, self.combatant = saga, combatant
        self.character = (
            saga.character(combatant.ref_id)
            if combatant.kind == CHARACTER_FIGHTER
            else None
        )

    @property
    def id(self) -> str:
        return self.combatant.id

    @property
    def name(self) -> str:
        if self.character is not None:
            return self.character.name
        return self.combatant.name or "A fighter"

    def figures(self) -> Figures:
        c = self.character
        weapon = _weapon(c, self.combatant.weapon_id) if c is not None else None
        if c is not None and weapon is not None:
            totals = combat.combat_totals(c, weapon)

            def whole(part: Breakdown | None) -> int | None:
                return None if part is None else int(part.total)

            ability = combat.weapon_ability(weapon)
            skill = sum(ability_score(c, ability)) if ability else 0
            return Figures(
                init=int(totals.initiative.total),
                attack=whole(totals.attack),
                defence=int(totals.defence.total),
                damage=whole(totals.damage),
                soak=int(derived.soak(c).total),
                size=int(derived.size(c).total),
                missile_defence=int((totals.missile_defence or totals.defence).total),
                ability=skill,
                leadership=sum(ability_score(c, "Leadership")),
                bare_damage=c.characteristics.strength,
                missile=ability in MISSILE_ABILITIES,
            )
        typed = self.combatant
        wounds = c.wounds if c is not None else typed.wounds
        level = c.fatigue_level if c is not None else typed.fatigue_level
        vfs = c.virtues_flaws if c is not None else []
        penalty = derived.wound_penalty(wounds, vfs) + derived.fatigue_penalty(
            level, vfs
        )
        return Figures(
            init=typed.init + penalty,
            attack=None if typed.attack is None else typed.attack + penalty,
            defence=typed.defence + penalty,
            damage=typed.damage,
            soak=typed.soak,
            size=typed.size,
            missile_defence=typed.defence + penalty,
            ability=typed.ability,
            leadership=typed.leadership,
            bare_damage=typed.damage or 0,
        )

    @property
    def wounds(self) -> Wounds:
        """The sheet's wounds, or the combatant's own."""
        return (
            self.character.wounds
            if self.character is not None
            else self.combatant.wounds
        )

    def down(self) -> bool:
        """Out of the fight: dead, incapacitated, unconscious, or gone."""
        if self.combatant.out:
            return True
        level = (
            self.character.fatigue_level
            if self.character is not None
            else self.combatant.fatigue_level
        )
        return self.wounds.dead or self.wounds.incapacitated or level == "unconscious"

    def wound(self, severity: str) -> None:
        recovery.add_wound(self.wounds, severity)

    def tire(self, levels: int = 1) -> None:
        """Lose `levels` Fatigue levels (unconscious at the last)."""
        holder = self.character if self.character is not None else self.combatant
        index = (
            FATIGUE_LEVELS.index(holder.fatigue_level)
            if holder.fatigue_level in FATIGUE_LEVELS
            else 0
        )
        holder.fatigue_level = FATIGUE_LEVELS[
            min(len(FATIGUE_LEVELS) - 1, index + levels)
        ]


@dataclass
class Unit:
    """Who acts on a turn: a group, or a combatant fighting alone."""

    id: str
    name: str
    side: int
    fighters: list[Fighter]
    group: FightGroup | None = None

    def standing(self) -> list[Fighter]:
        return [f for f in self.fighters if not f.down()]

    @property
    def vanguard(self) -> Fighter:
        return self.fighters[0]

    def down(self) -> bool:
        return not self.standing() or self.vanguard.down()

    def bonus(self) -> int:
        """A trained group's bonus: the other members' Combat Abilities, at
        most three times its leader's Leadership, while the leader can
        coordinate them all."""
        group = self.group
        if group is None or not group.trained:
            return 0
        leader = next((f for f in self.fighters if f.id == group.leader), None)
        if leader is None:
            return 0
        lead = leader.figures().leadership
        if len(self.fighters) > lead:
            return 0
        others = sum(f.figures().ability for f in self.standing()[1:])
        return min(others, combat_groups.BONUS_PER_LEADERSHIP * lead)


def units(saga: Saga, fight: Fight) -> dict[str, Unit]:
    """Every unit of the fight, by id: each group, then each combatant in
    none."""
    found: dict[str, Unit] = {}
    for index, side in enumerate(fight.sides):
        by_id = {c.id: c for c in side.combatants}
        grouped: set[str] = set()
        for group in side.groups:
            members = [Fighter(saga, by_id[m]) for m in group.members if m in by_id]
            if members:
                grouped.update(group.members)
                found[group.id] = Unit(
                    group.id, group.name or members[0].name, index, members, group
                )
        for combatant in side.combatants:
            if combatant.id not in grouped:
                fighter = Fighter(saga, combatant)
                found[combatant.id] = Unit(combatant.id, fighter.name, index, [fighter])
    return found


def side_name(fight: Fight, index: int) -> str:
    side = fight.sides[index] if index < len(fight.sides) else FightSide()
    return side.name or ("The first side", "The second side")[min(index, 1)]


# -- initiative --


def roll_initiative(saga: Saga, fight: Fight, rng: random.Random) -> list[str]:
    """Roll every unit's Initiative (Init + stress die, a botch 0) and set
    the order, highest first, ties re-rolled among themselves. Returns
    the chronicle's lines."""
    rolled: dict[str, int] = {}
    tie: dict[str, float] = {}
    lines: list[str] = []
    for unit in units(saga, fight).values():
        die = dice.stress_die(rng, saga=saga)
        total = unit.vanguard.figures().init + (0 if die.botched else die.value)
        rolled[unit.id] = total
        tie[unit.id] = rng.random()
        lines.append(f"{unit.name}: Init {total}")
    fight.initiative = rolled
    fight.order = sorted(rolled, key=lambda u: (-rolled[u], -tie[u]))
    fight.round, fight.turn = 1, 0
    fight.attacked_by, fight.attacked_last = {}, {}
    return lines


# -- a blow --


@dataclass
class Blow:
    """What the actor does on its turn."""

    action: str = ATTACK
    target: str = ""


@dataclass
class Played:
    """One turn played: the chronicle's line and the working."""

    text: str
    lines: list[str] = field(default_factory=list)


def _roll(
    rng: random.Random, saga: Saga, label: str, base: int, lines: list[str]
) -> tuple[int, bool]:
    die = dice.stress_die(rng, saga=saga)
    if die.botched:
        lines.append(f"{label}: {base:+d} + a botch ({die.botches} on the botch dice)")
        # A botch adds nothing, so a negative base stays negative (DE p. 393).
        return min(0, base), True
    lines.append(f"{label}: {base:+d} + stress die {die.value} = {base + die.value}")
    return base + die.value, False


def default_target(saga: Saga, fight: Fight, actor: Unit) -> Unit | None:
    """Who the actor strikes when nobody is chosen: whoever attacked it
    last, else the first enemy still standing in the order."""
    every = units(saga, fight)
    for unit_id in reversed(fight.attacked_by.get(actor.id, [])):
        found = every.get(unit_id)
        if found is not None and not found.down() and found.side != actor.side:
            return found
    for unit_id in fight.order:
        found = every.get(unit_id)
        if found is not None and found.side != actor.side and not found.down():
            return found
    return next(
        (u for u in every.values() if u.side != actor.side and not u.down()), None
    )


def actor(saga: Saga, fight: Fight) -> Unit | None:
    """The unit whose turn it is, skipping any that are down."""
    every = units(saga, fight)
    while fight.turn < len(fight.order):
        found = every.get(fight.order[fight.turn])
        if found is not None and not found.down():
            return found
        fight.turn += 1
    return None


def _strike(
    saga: Saga,
    fight: Fight,
    who: Unit,
    target: Unit,
    action: str,
    rng: random.Random,
) -> Played:
    lines: list[str] = []
    mine, theirs = who.vanguard.figures(), target.vanguard.figures()
    if mine.attack is None:
        return Played(f"{who.name} has no attack and waits.")
    bonus = who.bonus()
    attack = mine.attack
    if who.group is not None and who.group.bonus_to == "attack" and bonus:
        attack += bonus
        lines.append(f"Group bonus +{bonus} to Attack")
    if action == EXERTION:
        attack += mine.ability
        for f in who.standing():
            f.tire()
        lines.append(f"Exertion: +{mine.ability} (a Fatigue level spent)")
    if action == SCUFFLE and mine.damage != mine.bare_damage:
        attack += SCUFFLE_PENALTY
        lines.append(f"Scuffling with a weapon: {SCUFFLE_PENALTY}")
    defence = theirs.missile_defence if mine.missile else theirs.defence
    their_bonus = target.bonus()
    if target.group is not None and target.group.bonus_to == "defence" and their_bonus:
        defence += their_bonus
        lines.append(f"{target.name}'s group bonus +{their_bonus} to Defence")
    hit_total, botched = _roll(rng, saga, "Attack", attack, lines)
    guard, guard_botched = _roll(rng, saga, "Defence", defence, lines)
    if guard_botched:
        lines.append(f"{target.name} botches the defence.")
    fight.attacked_by.setdefault(target.id, []).append(who.id)
    fight.disengage_tries.pop(who.id, None)
    if botched:
        return Played(
            f"{who.name} botches the attack on {target.name}: the storyguide says "
            "what goes wrong.",
            lines,
        )
    if hit_total <= guard:
        return Played(f"{who.name} strikes at {target.name} and misses.", lines)
    advantage = hit_total - guard
    lines.append(f"Attack Advantage {advantage}")
    if action in combat_groups.SPECIAL_EFFECTS:
        need = combat_groups.SPECIAL_EFFECTS[action]
        done = advantage >= need
        return Played(
            f"{who.name} tries to {action.lower()} {target.name}: "
            + ("done." if done else f"fails (needs an Advantage of {need})."),
            lines,
        )
    damage = (mine.bare_damage if action == SCUFFLE else mine.damage or 0) + advantage
    excess = damage - theirs.soak
    lines.append(
        f"Damage {damage} against Soak {theirs.soak}: {max(0, excess)} through"
    )
    if excess <= 0:
        return Played(f"{who.name} hits {target.name}, but the blow is soaked.", lines)
    victims = target.standing()
    told = _land(victims, len(who.standing()), excess, scuffle=action == SCUFFLE)
    lines += told
    fallen = [f.name for f in victims if f.down()]
    text = f"{who.name} hits {target.name}: " + "; ".join(told) + "."
    if fallen:
        text += " " + ", ".join(fallen) + (" falls." if len(fallen) == 1 else " fall.")
    return Played(text, lines)


def _land(
    victims: list[Fighter], blows: int, excess: int, *, scuffle: bool
) -> list[str]:
    """A hit landing once per attacker, spread over the defenders (the
    vanguard first): each a wound for the defender's Size, or in a scuffle
    the Scuffle Effects' Fatigue."""
    told: list[str] = []
    spread = combat_groups.blows(blows, len(victims))
    for fighter, count in zip(victims, spread, strict=True):
        for _ in range(count):
            if fighter.down():
                break
            band = derived.wound_for(excess, fighter.figures().size)
            if band is None:
                continue
            severity = band.lower()
            if scuffle:
                levels, wound = combat_groups.scuffle(severity)
                fighter.tire(levels)
                if wound:
                    fighter.wound(wound)
                told.append(
                    f"{fighter.name} loses {levels} Fatigue level(s)"
                    + (f" and takes a {wound.title()} Wound" if wound else "")
                )
            else:
                fighter.wound(severity)
                told.append(f"{fighter.name} takes a {band} Wound")
    return told


def _disengage(saga: Saga, fight: Fight, who: Unit, rng: random.Random) -> Played:
    every = units(saga, fight)
    foes = [
        every[u]
        for u in dict.fromkeys(
            fight.attacked_last.get(who.id, []) + fight.attacked_by.get(who.id, [])
        )
        if u in every and not every[u].down()
    ]
    tries = fight.disengage_tries.get(who.id, 0) + 1
    fight.disengage_tries[who.id] = tries
    lines: list[str] = []
    if not foes:
        escaped = True
        lines.append("Nobody attacked it since its last turn: it leaves freely.")
    else:
        extra = combat_groups.disengage_bonus(tries)
        guard, botched = _roll(
            rng, saga, "Defence", who.vanguard.figures().defence + extra, lines
        )
        escaped = not botched
        for foe in foes:
            figures = foe.vanguard.figures()
            hit, _ = _roll(
                rng, saga, f"{foe.name}'s Attack", figures.attack or 0, lines
            )
            escaped = escaped and guard > hit
    if escaped:
        for f in who.fighters:
            f.combatant.out = f.combatant.out or "Disengaged"
        return Played(f"{who.name} disengages and leaves the fight.", lines)
    return Played(f"{who.name} tries to disengage, but is held.", lines)


def _split(saga: Saga, fight: Fight) -> list[str]:
    """Split every group whose vanguard or leader is down into
    individuals, each taking the group's place in the order."""
    told: list[str] = []
    for side in fight.sides:
        by_id = {c.id: c for c in side.combatants}
        for group in list(side.groups):
            members = [Fighter(saga, by_id[m]) for m in group.members if m in by_id]
            if not members:
                side.groups.remove(group)
                continue
            leader_down = bool(group.leader) and any(
                f.id == group.leader and f.down() for f in members
            )
            if not (members[0].down() or leader_down):
                continue
            side.groups.remove(group)
            standing = [f.id for f in members if not f.down()]
            if group.id in fight.order:
                at = fight.order.index(group.id)
                fight.order[at : at + 1] = standing
                for member in standing:
                    fight.initiative[member] = fight.initiative.get(group.id, 0)
                if at < fight.turn:
                    fight.turn += len(standing) - 1
            if standing:
                told.append(f"{group.name or 'The group'} splits up.")
    return told


def winner(saga: Saga, fight: Fight) -> int | None:
    """The side left standing when the other has nobody, else None."""
    every = units(saga, fight).values()
    standing = {u.side for u in every if not u.down()}
    if len(standing) == 1 and len(fight.sides) > 1:
        return standing.pop()
    return None


def play(saga: Saga, fight: Fight, blow: Blow, rng: random.Random) -> Played:
    """Play the turn of the unit acting now, then move on (a new round
    after the last). Rolls Initiative first if the fight hasn't begun."""
    begun: list[str] = []
    if fight.round == 0:
        begun = roll_initiative(saga, fight, rng)
        fight.log.append(FightEntry(1, "Initiative is rolled.", begun))
    who = actor(saga, fight)
    if who is None:
        _next_round(fight)
        who = actor(saga, fight)
    if who is None:
        return Played("Nobody is left to act.")
    if blow.action == WAIT:
        played = Played(f"{who.name} waits.")
    elif blow.action == DISENGAGE:
        played = _disengage(saga, fight, who, rng)
    else:
        every = units(saga, fight)
        target = every.get(blow.target) if blow.target else None
        if target is None or target.down() or target.side == who.side:
            target = default_target(saga, fight, who)
        played = (
            Played(f"{who.name} finds nobody to strike.")
            if target is None
            else _strike(saga, fight, who, target, blow.action, rng)
        )
    played.lines += _split(saga, fight)
    fight.log.append(FightEntry(fight.round, played.text, played.lines))
    fight.turn += 1
    side = winner(saga, fight)
    if side is not None:
        fight.over = f"{side_name(fight, side)} win the fight."
        fight.log.append(FightEntry(fight.round, fight.over))
    elif actor(saga, fight) is None:
        _next_round(fight)
    return played


def _next_round(fight: Fight) -> None:
    fight.round += 1
    fight.turn = 0
    fight.attacked_last, fight.attacked_by = fight.attacked_by, {}


def play_round(saga: Saga, fight: Fight, rng: random.Random) -> list[Played]:
    """Play every turn left in this round, each striking its default
    target (a new fight's first round from its start)."""
    played: list[Played] = []
    start = fight.round or 1
    for _ in range(4 * max(1, len(units(saga, fight)))):
        if fight.over or (fight.round > start):
            break
        played.append(play(saga, fight, Blow(), rng))
    return played


def restart(fight: Fight) -> None:
    """Back to before Initiative: the order, round and chronicle cleared.
    Wounds taken stay where they were written."""
    fight.round, fight.turn, fight.order, fight.initiative = 0, 0, [], {}
    fight.attacked_by, fight.attacked_last, fight.disengage_tries = {}, {}, {}
    fight.log, fight.over, fight.recorded = [], "", False
    for side in fight.sides:
        for combatant in side.combatants:
            combatant.out = ""
