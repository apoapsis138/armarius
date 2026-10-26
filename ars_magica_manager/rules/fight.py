"""Playing a fight blow by blow (DE Chapter Eleven, Combat, pp. 394-398).

- **Initiative** is rolled once for the whole fight (Init + stress die)
  and stays the same every round; each party acts in order of decreasing
  Initiative, ties re-rolled between themselves (p. 394).
- **A blow**: the attacker's Attack + stress die against the defender's
  Defence + stress die; a hit beats it, by the Attack Advantage. The
  Damage Total (Damage + the Advantage) less the defender's Soak is read
  on the Damage Table for his Size (p. 394). Against missiles only a
  shield's Defence counts, with the Combat Ability (p. 395). A Greek
  Fire siphon's fire splashes round a shield: its Defence comes off the
  target's Defence and adds to his Soak (The Sundered Eagle p. 47).
- **Groups** act as one, with the vanguard's figures; a trained group's
  other members add their Combat Abilities (at most 3 x the leader's
  Leadership) to its Attack or its Defence. A group's hit lands once for
  each member, spread as evenly as can be over the other group, the
  vanguard taking at least as many blows; the defending group's Soak is
  its vanguard's. When the vanguard or leader falls, the group splits into
  individuals (pp. 395-397).
- **Magic** (rules.magic_combat; DE pp. 214, 219-226; Houses of Hermes:
  Societates pp. 25-33): a spell's Casting Score counts its Mastery, and
  its Penetration the Penetration Mastery, an Arcane Connection and
  sympathetic connections; an indirect spell isn't resisted but is aimed
  like a missile; an invisible fighter can't be struck until located,
  strikes with surprise and is harder to hit.
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
from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import catalog
from ..arts import FORMS, TECHNIQUES
from ..models import (
    CHARACTER_FIGHTER,
    CREATURE_FIGHTER,
    FATIGUE_LEVELS,
    Character,
    Combatant,
    Creature,
    Fight,
    FightEntry,
    FightGroup,
    FightSide,
    Grip,
    Possession,
    Saga,
    Wounds,
)
from . import (
    casting,
    casting_virtues,
    combat,
    combat_groups,
    derived,
    dice,
    magic_combat,
    penetration,
    realms,
    recovery,
)
from .apprentice_seasons import gifted
from .breakdown import Breakdown
from .disputatio import GENTLE_GIFT
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
GRAPPLE, BREAK_FREE, SPLIT, CAST, DEVICE = (
    "Grapple",
    "Break free",
    "Split the group",
    "Cast a spell",
    "Use a device",
)
#: The actions fought with bare hands, not a weapon.
BARE_ACTIONS = (SCUFFLE, GRAPPLE, BREAK_FREE)
#: Searching a round for an invisible foe (HoH:S p. 32); offered only
#: while one is unlocated.
LOCATE = "Locate the unseen"
ACTIONS: tuple[str, ...] = (
    ATTACK,
    EXERTION,
    SCUFFLE,
    GRAPPLE,
    BREAK_FREE,
    *combat_groups.SPECIAL_EFFECTS,
    SPLIT,
    CAST,
    DEVICE,
    DISENGAGE,
    WAIT,
)
#: The value of Spontaneous magic among a magus's spells.
SPONTANEOUS = "spontaneous"
ART_PAIRS: tuple[str, ...] = tuple(f"{t} {f}" for t in TECHNIQUES for f in FORMS)
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
    #: The Defence its carried shield adds (in missile_defence).
    shield_defence: int = 0
    #: Its weapon is a Greek Fire siphon, whose fire splashes round shields.
    splashes: bool = False


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

    def is_animal(self) -> bool:
        """A beast: an animal grog, or a creature with an animal mind."""
        if self.character is not None:
            return self.character.animal is not None
        if self.combatant.kind == CREATURE_FIGHTER:
            creature = self.saga.creature(self.combatant.ref_id)
            return creature is not None and creature.cunning
        return False

    def holder(self) -> Character | Creature | None:
        """The sheet or Bestiary entry it was drawn from (None when typed)."""
        if self.character is not None:
            return self.character
        if self.combatant.kind == CREATURE_FIGHTER:
            return self.saga.creature(self.combatant.ref_id)
        return None

    def signs(self) -> magic_combat.Clarity | None:
        """How clear the signs of its invisibility are (None: visible)."""
        return magic_combat.clarity(self.combatant.invisible)

    def hidden(self) -> bool:
        """Invisible with signs an observer can't simply see."""
        signs = self.signs()
        return signs is not None and not signs.seen

    def magical_blow(self, action: str) -> bool:
        """Whether its blow is kept out by Magic Resistance because it is
        invisible: its touch and the weapon it turned invisible with are
        both magical; only a non-magical weapon picked up after turning
        invisible gets through, never bare hands (HoH:S p. 32). Obvious
        signs alone don't change that."""
        if self.signs() is None:
            return False
        if not self.combatant.weapon_after_invisible or action in BARE_ACTIONS:
            return True
        c = self.character
        return c is not None and _weapon(c, self.combatant.weapon_id).gear_id == FIST

    def handling(self) -> int:
        """Its Animal Handling, which leads a group of tamed animals in
        place of Leadership (DE p. 385)."""
        if self.character is None:
            return 0
        return sum(ability_score(self.character, "Animal Handling"))

    def figures(self, *, bare: bool = False) -> Figures:
        """Its figures with its weapon, or with bare hands (`bare`, for a
        grapple, which needs Brawl and free hands)."""
        c = self.character
        weapon = (
            (bare_hands() if bare else _weapon(c, self.combatant.weapon_id))
            if c is not None
            else None
        )
        if c is not None and weapon is not None:
            # On horseback a lance is a Single Weapon; on foot a long spear
            # (DE pp. 400-401; Lords of Men p. 126). Ride's bonus is not in
            # these totals: ride_bonus() adds it to each blow.
            totals = combat.combat_totals(c, weapon, mounted_=self.combatant.mounted)

            def whole(part: Breakdown | None) -> int | None:
                return None if part is None else int(part.total)

            # The Ability the totals were worked with (a lance on foot is
            # fought with Great Weapon).
            ability = totals.ability
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
                missile=ability in MISSILE_ABILITIES or combat.is_missile(weapon),
                shield_defence=combat.shield_defence(c),
                splashes=weapon.gear_id == combat.GREEK_FIRE_SIPHON,
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
        # Fighters who can't see one another can't fight as a trained
        # group (HoH:S p. 33).
        if any(f.signs() is not None for f in self.standing()):
            return 0
        leader = next((f for f in self.fighters if f.id == group.leader), None)
        if leader is None:
            return 0
        lead = leads_with(self.fighters, leader)
        if len(self.fighters) > lead:
            return 0
        others = sum(f.figures().ability for f in self.standing()[1:])
        return min(others, combat_groups.BONUS_PER_LEADERSHIP * lead)


def leads_with(fighters: Sequence[Fighter], leader: Fighter) -> int:
    """How many the leader can coordinate: his Leadership, or for a group
    of tamed animals his Animal Handling (DE p. 385)."""
    others = [f for f in fighters if f is not leader]
    if others and all(f.is_animal() for f in others):
        return leader.handling()
    return leader.figures().leadership


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
    every = units(saga, fight)
    # An invisible fighter nobody has located goes first in the first
    # round (HoH:S p. 32); from the second the rolled order stands.
    surprising = [u for u in fight.order if every[u].vanguard.hidden()]
    if surprising:
        fight.order = surprising + [u for u in fight.order if u not in surprising]
        lines += [
            f"{every[u].name} is unseen: it acts first this round (HoH:S p. 32)."
            for u in surprising
        ]
    fight.round, fight.turn = 1, 0
    fight.attacked_by, fight.attacked_last = {}, {}
    return lines


# -- a blow --


@dataclass
class Blow:
    """What the actor does on its turn."""

    action: str = ATTACK
    target: str = ""
    #: Cast a Spell: the spell's id, or SPONTANEOUS with its Arts ("Creo
    #: Ignem"), level and whether it is fatiguing; Use a Device: the
    #: effect ("<device id>|<effect id>"). The damage either does, if any.
    spell: str = ""
    arts: str = ""
    level: int = 0
    fatiguing: bool = True
    effect: str = ""
    damage: int | None = None
    #: Cast a Spell: the Arts chosen as casting requisites for what it is
    #: used on (DE p. 312).
    casting_requisites: tuple[str, ...] = ()
    #: An indirect spell or effect: not resisted, but aimed (DE p. 223);
    #: the size steps past a basic Individual it is aimed with.
    indirect: bool = False
    aim_steps: int = 0
    #: Cast a Spell: the Arcane Connection to the target (a key of
    #: penetration.ARCANE_CONNECTIONS, "" for none) and the sympathetic
    #: connections used with it (DE pp. 219-220; HoH:S p. 27).
    arcane: str = ""
    named: bool = False
    symbol: bool = False


@dataclass
class Played:
    """One turn played: the chronicle's line and the working."""

    text: str
    lines: list[str] = field(default_factory=list)


def _roll(
    rng: random.Random,
    saga: Saga,
    label: str,
    base: int,
    lines: list[str],
    botch_dice: int = 1,
) -> tuple[int, bool]:
    die = dice.stress_die(rng, botch_dice, saga=saga)
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
    grip = grip_on(fight, actor.id)
    if grip is not None and grip.by in every:
        return every[grip.by]

    def open_(found: Unit | None) -> bool:
        return (
            found is not None
            and found.side != actor.side
            and not found.down()
            and not defenders_of(saga, fight, found)
            and not unseen(fight, actor, found)
        )

    for unit_id in reversed(fight.attacked_by.get(actor.id, [])):
        if open_(found := every.get(unit_id)):
            return found
    for unit_id in [*fight.order, *every]:
        if open_(found := every.get(unit_id)):
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


@dataclass
class Term:
    """One part of a total: its amount, and the chronicle's line for it
    ("" for the base figure, which the roll's own line shows)."""

    label: str
    amount: int
    line: str = ""


@dataclass
class Odds:
    """A blow worked out before the dice: the terms of its Attack,
    Defence, Damage (before the Advantage) and Soak, the Advantage it
    needs, and why it can't be struck at all ("" when it can). The
    inspector shows it; the blow rolls it."""

    attack: list[Term] = field(default_factory=list)
    defence: list[Term] = field(default_factory=list)
    damage: list[Term] = field(default_factory=list)
    soak: list[Term] = field(default_factory=list)
    #: The least Attack Advantage that does what the action wants: 1 to
    #: hit, a special effect's own, 0 to split a group.
    need: int = 1
    blocked: str = ""

    def total(self, part: str) -> int:
        terms: list[Term] = getattr(self, part)
        return sum(t.amount for t in terms)


#: Wooden weapons, whose blows a Herbam Form Bonus soaks; other weapons
#: are metal or stone (Terram), bare hands human (Corpus), and a
#: creature's teeth and claws an animal's (Animal) (DE pp. 208-209).
WOODEN_WEAPONS = frozenset(
    {"weapon_club", "weapon_cudgel", "weapon_staff", "weapon_bludgeon"}
)
UNARMED = frozenset({"weapon_fist", "weapon_kick", "natural_grapple"})


def harm_form(attacker: Fighter) -> str:
    """The Form whose Bonus soaks the attacker's blows."""
    if attacker.combatant.kind == CREATURE_FIGHTER:
        return "Animal"
    if attacker.character is None:
        return ""
    weapon = _weapon(attacker.character, attacker.combatant.weapon_id)
    gear = weapon.gear_id or ""
    if gear in UNARMED:
        return "Corpus"
    return "Herbam" if gear in WOODEN_WEAPONS else "Terram"


def range_penalty(fight: Fight) -> int:
    """A missile's penalty: -3 for each range increment past the first
    (DE p. 395)."""
    return -3 * max(0, fight.range - 1)


def defenders_of(saga: Saga, fight: Fight, unit: Unit) -> list[Fighter]:
    """The fighters still standing who defend one of `unit`'s. Allies
    can't defend one who is invisible (HoH:S p. 33)."""
    mine = {f.id for f in unit.fighters if not f.hidden()}
    return [
        f
        for u in units(saga, fight).values()
        for f in u.standing()
        if f.combatant.defends in mine
    ]


# -- fighting the invisible (HoH:S pp. 32-33) --


def engaged(fight: Fight, one: Unit, other: Unit) -> bool:
    """Whether the two are engaged in melee: one struck the other hand to
    hand this round or last. Melee range locates a foe by sound and touch
    (HoH:S p. 32)."""
    if fight.range > 0:
        return False
    for a, b in ((one, other), (other, one)):
        struck = fight.attacked_by.get(b.id, []) + fight.attacked_last.get(b.id, [])
        if a.id in struck and not a.vanguard.figures().missile:
            return True
    return False


def sees(fight: Fight, seer: Unit, unit: Unit) -> bool:
    """Whether `seer` knows where `unit`'s vanguard is: it is visible, its
    signs are obvious, `seer` located it, or the two are engaged in melee
    (HoH:S p. 32)."""
    if not unit.vanguard.hidden():
        return True
    return seer.id in fight.located.get(unit.vanguard.id, []) or engaged(
        fight, seer, unit
    )


def unseen(fight: Fight, seer: Unit, unit: Unit) -> bool:
    """`unit` is invisible and `seer` hasn't found it: it can't be engaged,
    shot or targeted (HoH:S p. 32)."""
    return not sees(fight, seer, unit)


def _shielded(saga: Saga, fight: Fight, fighter: Fighter) -> bool:
    """Whether the fighter has Magic Resistance at all, which keeps out an
    invisible weapon (DE pp. 221, 223): a magus always does, anyone else
    when it is above 0."""
    c = fighter.character
    if c is not None and c.arts:
        return True
    return resistance_of(saga, fight, fighter, "Imaginem") > 0


def _invisible_block(
    saga: Saga, fight: Fight, who: Unit, target: Unit, action: str
) -> str:
    """Why invisibility stops the blow ("" when it doesn't): the target
    can't be found, or the attacker's invisible weapon or touch can't pass
    the target's Magic Resistance (DE p. 223; HoH:S p. 32)."""
    if unseen(fight, who, target):
        return (
            f"{who.name} doesn't know where the invisible {target.name} is: "
            "locate it first (HoH:S p. 32)."
        )
    if who.vanguard.magical_blow(action) and _shielded(saga, fight, target.vanguard):
        return (
            f"{who.name}'s invisible weapon or touch is kept out by "
            f"{target.name}'s Magic Resistance (DE p. 223; HoH:S p. 32): only a "
            "non-magical weapon picked up after turning invisible gets through."
        )
    return ""


def _invisible_terms(
    saga: Saga, fight: Fight, who: Unit, target: Unit, chances: Odds, missile: bool
) -> None:
    """Invisibility's terms (HoH:S pp. 32-33): the invisible attacker's
    melee bonus, and +3 for a surprise attack on a foe who hasn't located
    him; the invisible defender's bonus to Defence."""
    signs = who.vanguard.signs()
    if signs is not None:
        if not missile:
            chances.attack.append(
                Term(
                    "Invisible",
                    signs.attack,
                    f"Invisible ({signs.label}): +{signs.attack} to a melee Attack",
                )
            )
        if unseen(fight, target, who):
            chances.attack.append(
                Term(
                    "Surprise",
                    magic_combat.SURPRISE_ATTACK,
                    f"A surprise attack on a foe who hasn't located it: "
                    f"+{magic_combat.SURPRISE_ATTACK}",
                )
            )
    theirs = target.vanguard.signs()
    if theirs is not None:
        chances.defence.append(
            Term(
                "Invisible",
                theirs.defence,
                f"{target.name} invisible ({theirs.label}): +{theirs.defence} to "
                "Defence",
            )
        )


def _splash(chances: Odds, mine: Figures, theirs: Figures) -> None:
    """Greek Fire splashes round a shield: the shield's Defence comes off
    the target's Defence and adds to his Soak (The Sundered Eagle p. 47)."""
    splash = theirs.shield_defence if mine.splashes and mine.missile else 0
    if not splash:
        return
    chances.defence.append(
        Term("Shield", -splash, f"Greek Fire splashes round the shield: -{splash}")
    )
    chances.soak.append(
        Term(
            "Shield",
            splash,
            f"The shield's Defence to Soak against Greek Fire: +{splash}",
        )
    )


def odds(saga: Saga, fight: Fight, who: Unit, target: Unit, action: str) -> Odds:
    """`who`'s blow at `target` with `action`, before the dice."""
    mine = who.vanguard.figures(bare=action == GRAPPLE)
    theirs = target.vanguard.figures()
    if mine.attack is None:
        return Odds(blocked=f"{who.name} has no attack and waits.")
    guards = defenders_of(saga, fight, target)
    if guards and action not in (SPLIT, BREAK_FREE):
        names = ", ".join(f.name for f in guards)
        return Odds(
            blocked=f"{target.name} is defended by {names}: strike them first "
            "(DE p. 397)."
        )
    unreached = (
        f"{who.name} can't reach {target.name} at range."
        if fight.range > 0 and not mine.missile
        else _invisible_block(saga, fight, who, target, action)
    )
    if unreached:
        return Odds(blocked=unreached)
    chances = Odds(attack=[Term("Attack", mine.attack)])
    bonus = who.bonus()
    if who.group is not None and who.group.bonus_to == "attack" and bonus:
        chances.attack.append(
            Term("Group bonus", bonus, f"Group bonus +{bonus} to Attack")
        )
    ride = ride_bonus(who.vanguard)
    if ride:
        chances.attack.append(Term("Mounted", ride, f"Mounted: +{ride} to Attack"))
    if mine.missile and range_penalty(fight):
        penalty = range_penalty(fight)
        chances.attack.append(
            Term("Range", penalty, f"{fight.range} range increments: {penalty}")
        )
    if action == EXERTION:
        chances.attack.append(
            Term(
                "Exertion",
                mine.ability,
                f"Exertion: +{mine.ability} (a Fatigue level spent)",
            )
        )
    if action == SCUFFLE and mine.damage != mine.bare_damage:
        chances.attack.append(
            Term(
                "Scuffling with a weapon",
                SCUFFLE_PENALTY,
                f"Scuffling with a weapon: {SCUFFLE_PENALTY}",
            )
        )
    chances.defence = [
        Term("Defence", theirs.missile_defence if mine.missile else theirs.defence)
    ]
    their_bonus = target.bonus()
    if target.group is not None and target.group.bonus_to == "defence" and their_bonus:
        chances.defence.append(
            Term(
                "Group bonus",
                their_bonus,
                f"{target.name}'s group bonus +{their_bonus} to Defence",
            )
        )
    their_ride = ride_bonus(target.vanguard)
    if their_ride:
        chances.defence.append(
            Term("Mounted", their_ride, f"{target.name} mounted: +{their_ride}")
        )
    _invisible_terms(saga, fight, who, target, chances, mine.missile)
    damage = mine.bare_damage if action in (SCUFFLE, GRAPPLE) else mine.damage or 0
    chances.damage = [Term("Damage", damage)]
    chances.soak = [Term("Soak", theirs.soak)]
    _splash(chances, mine, theirs)
    form = harm_form(who.vanguard)
    shield = target.vanguard.character
    form_bonus = derived.form_bonus(shield, form) if shield and form else 0
    if form_bonus:
        chances.soak.append(
            Term(f"{form} Form Bonus", form_bonus, f"{form} Form Bonus +{form_bonus}")
        )
    if action in combat_groups.SPECIAL_EFFECTS:
        chances.need = combat_groups.SPECIAL_EFFECTS[action]
    elif action == SPLIT:
        chances.need = 0
        if target.group is None or len(target.standing()) < 2:
            chances.blocked = f"{target.name} is no group to split."
    elif action == GRAPPLE:
        held = grip_on(fight, target.id)
        if held is not None and held.by != who.id:
            chances.blocked = f"{target.name} is already held."
    return chances


def _strike(
    saga: Saga,
    fight: Fight,
    who: Unit,
    target: Unit,
    action: str,
    rng: random.Random,
) -> Played:
    chances = odds(saga, fight, who, target, action)
    if chances.blocked:
        return Played(chances.blocked)
    lines = [term.line for term in chances.attack + chances.defence if term.line]
    if action == EXERTION:
        for f in who.standing():
            f.tire()
    hit_total, botched = _roll(
        rng, saga, "Attack", chances.total("attack"), lines, group_dice(who, lines)
    )
    guard, guard_botched = _roll(
        rng, saga, "Defence", chances.total("defence"), lines, group_dice(target, lines)
    )
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
    if action == SPLIT:
        return _split_by(saga, fight, who, target, hit_total - guard, lines)
    if hit_total <= guard:
        return Played(f"{who.name} strikes at {target.name} and misses.", lines)
    advantage = hit_total - guard
    lines.append(f"Attack Advantage {advantage}")
    if action == GRAPPLE:
        return _take_hold(fight, who, target, advantage, lines)
    if action == BREAK_FREE:
        return _break_free(fight, who, target, advantage, lines)
    if action in combat_groups.SPECIAL_EFFECTS:
        need = combat_groups.SPECIAL_EFFECTS[action]
        done = advantage >= need
        return Played(
            f"{who.name} tries to {action.lower()} {target.name}: "
            + ("done." if done else f"fails (needs an Advantage of {need})."),
            lines,
        )
    damage = chances.total("damage") + advantage
    soak = chances.total("soak")
    lines += [term.line for term in chances.soak if term.line]
    excess = damage - soak
    lines.append(f"Damage {damage} against Soak {soak}: {max(0, excess)} through")
    if excess <= 0:
        return Played(f"{who.name} hits {target.name}, but the blow is soaked.", lines)
    victims = target.standing()
    exposed = _exposed(saga, fight, target) if guard_botched else []
    if exposed:
        lines.append(
            f"{target.name} botched defending: the blow reaches "
            + ", ".join(f.name for f in exposed)
            + " (DE p. 397)."
        )
        victims = exposed
    told = _land(victims, len(who.standing()), excess, scuffle=action == SCUFFLE)
    lines += told
    fallen = [f.name for f in victims if f.down()]
    text = f"{who.name} hits {target.name}: " + "; ".join(told) + "."
    if fallen:
        text += " " + ", ".join(fallen) + (" falls." if len(fallen) == 1 else " fall.")
    return Played(text, lines)


def group_dice(unit: Unit, lines: list[str] | None = None) -> int:
    """A unit's botch dice on its combat rolls: one, and one more for each
    invisible member of a group (HoH:S p. 33)."""
    if unit.group is None:
        return 1
    extra = magic_combat.group_botch_dice(
        sum(1 for f in unit.standing() if f.signs() is not None)
    )
    if extra and lines is not None:
        lines.append(
            f"{unit.name}: {extra} more botch dice for its invisible members "
            "(HoH:S p. 33)"
        )
    return 1 + extra


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
                    + (f" and takes {_a(wound.title())} Wound" if wound else "")
                )
            else:
                fighter.wound(severity)
                told.append(f"{fighter.name} takes {_a(band)} Wound")
    return told


def _a(word: str) -> str:
    """The word with its article: "an Incapacitating", "a Heavy"."""
    return f"{'an' if word[:1].lower() in 'aeiou' else 'a'} {word}"


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
    action = blow.action
    grip = grip_on(fight, who.id)
    if grip is not None and action not in (BREAK_FREE, CAST, DEVICE, WAIT):
        action = BREAK_FREE
    if action == WAIT:
        played = Played(f"{who.name} waits.")
    elif action == LOCATE:
        played = _locate(saga, fight, who, blow.target, rng)
    elif action == DISENGAGE:
        played = _disengage(saga, fight, who, rng)
    elif action == BREAK_FREE and grip is None:
        played = Played(f"{who.name} is held by nobody.")
    else:
        every = units(saga, fight)
        target = every.get(blow.target) if blow.target else None
        if action == BREAK_FREE and grip is not None:
            target = every.get(grip.by)
        if target is None or target.down() or target.side == who.side:
            target = default_target(saga, fight, who)
        if target is None:
            played = Played(f"{who.name} finds nobody to strike.")
        elif action in (CAST, DEVICE):
            played = _magic(saga, fight, who, target, action, blow, rng)
        else:
            played = _strike(saga, fight, who, target, action, rng)
    played.lines += _split(saga, fight)
    played.lines += _loosen(saga, fight)
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
    if fight.round == 2 and any(
        c.invisible for side in fight.sides for c in side.combatants
    ):
        # The unseen went first in the first round only (HoH:S p. 32).
        fight.order.sort(key=lambda u: -fight.initiative.get(u, 0))
    fight.attacked_last, fight.attacked_by = fight.attacked_by, {}
    fight.splits = {}


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
    fight.grips, fight.splits, fight.located = [], {}, {}
    for side in fight.sides:
        for combatant in side.combatants:
            combatant.out = ""


# -- spells and devices --


def spells_of(saga: Saga, character: Character | None) -> list[tuple[str, str]]:
    """The spells a character knows, as Cast a Spell offers them: (name
    and level, spell id)."""
    if character is None:
        return []
    found: list[tuple[str, str]] = []
    for known in character.spells_known:
        spell = catalog.find_spell(saga, known.spell_id)
        if spell is not None:
            found.append((f"{spell.name} ({spell.level})", spell.id))
    return found


def device_effects(saga: Saga, character: Character | None) -> list[tuple[str, str]]:
    """The effects of the devices a character holds, as Use a Device
    offers them: (device: effect, "<device id>|<effect id>")."""
    if character is None:
        return []
    return [
        (f"{d.name}: {e.name or 'effect'}", f"{d.id}|{e.id}")
        for d in saga.enchanted_devices
        if d.holder_kind == "character" and d.holder_id == character.id
        for e in d.effects
        if e.known
    ]


# -- what a unit may do --


def grip_on(fight: Fight, unit_id: str) -> Grip | None:
    """The grapple holding `unit_id`, if one does."""
    return next((g for g in fight.grips if g.held == unit_id), None)


def grips_by(fight: Fight, unit_id: str) -> list[Grip]:
    """The grapples `unit_id` holds."""
    return [g for g in fight.grips if g.by == unit_id]


def actions_for(saga: Saga, fight: Fight, who: Unit | None) -> tuple[str, ...]:
    """The actions open to `who` on its turn. One held in a grapple may
    only try to break free, or do what needs no moving about (DE p. 398);
    at range, only missiles strike (p. 395); a spell or a device is one
    fighter's, not a group's; splitting needs an enemy group and a second
    unit on one's own side to press it (p. 398)."""
    if who is None:
        return ACTIONS
    alone = who.group is None
    character = who.vanguard.character
    magic = tuple(
        a
        for a, open_ in (
            (CAST, alone and character is not None and bool(character.arts)),
            (DEVICE, alone and bool(device_effects(saga, character))),
        )
        if open_
    )
    every = units(saga, fight)
    search = (
        (LOCATE,)
        if any(
            u.side != who.side and not u.down() and unseen(fight, who, u)
            for u in every.values()
        )
        else ()
    )
    if grip_on(fight, who.id) is not None:
        return (BREAK_FREE, *magic, WAIT)
    if fight.range > 0 and not who.vanguard.figures().missile:
        return (*magic, *search, DISENGAGE, WAIT)
    allies = [u for u in every.values() if u.side == who.side and not u.down()]
    enemy_groups = [
        u
        for u in every.values()
        if u.side != who.side and u.group is not None and len(u.standing()) > 1
    ]
    blows = tuple(
        a
        for a in ACTIONS
        if a not in (BREAK_FREE, CAST, DEVICE, DISENGAGE, WAIT)
        and (a != GRAPPLE or alone)
        and (a != SPLIT or (bool(enemy_groups) and len(allies) > 1))
    )
    return (*blows, *magic, *search, DISENGAGE, WAIT)


def _locate(
    saga: Saga, fight: Fight, who: Unit, target_id: str, rng: random.Random
) -> Played:
    """A round's search for an invisible foe: Perception + Awareness +
    stress die against his Dexterity + Stealth - Encumbrance + Stealth
    bonus + stress die; beating it locates him (HoH:S p. 32)."""
    every = units(saga, fight)
    hidden = [
        u
        for u in every.values()
        if u.side != who.side and not u.down() and unseen(fight, who, u)
    ]
    target = next((u for u in hidden if u.id == target_id), None) or next(
        iter(hidden), None
    )
    if target is None:
        return Played(f"{who.name} looks about, but nobody is hidden from it.")
    signs = target.vanguard.signs()
    assert signs is not None  # unseen() holds only for the invisible
    lines: list[str] = []
    if signs.unseeable:
        lines.append(f"{target.name} leaves no signs: found by sound alone.")
    seek = magic_combat.locate_base(who.vanguard.holder())
    hide = magic_combat.hide_base(target.vanguard.holder(), signs)
    found, botched = _roll(rng, saga, "Perception + Awareness", int(seek.total), lines)
    cover, _ = _roll(rng, saga, "Dexterity + Stealth", int(hide.total), lines)
    if botched or found <= cover:
        return Played(
            f"{who.name} searches for {target.name}, but can't find it.", lines
        )
    fight.located.setdefault(target.vanguard.id, []).append(who.id)
    return Played(
        f"{who.name} locates the invisible {target.name}: it may now be struck.",
        lines,
    )


#: The most Ride adds to a mounted fighter's Attack and Defence (DE p. 397).
MOST_RIDE = 3


def ride_bonus(fighter: Fighter) -> int:
    """What riding adds to Attack and Defence: Ride, at most +3; none on
    foot (DE p. 397)."""
    if not fighter.combatant.mounted:
        return 0
    c = fighter.character
    ride = sum(ability_score(c, "Ride")) if c is not None else fighter.combatant.ride
    return max(0, min(MOST_RIDE, ride))


def tags(saga: Saga, fight: Fight, unit: Unit) -> list[str]:
    """What a unit's card says besides its figures: riding, whom it
    defends, and the grapples it is in."""
    every = units(saga, fight)
    named = {f.id: f.name for u in every.values() for f in u.fighters}
    named.update({u.id: u.name for u in every.values()})
    found: list[str] = []
    for f in unit.fighters:
        if f.combatant.mounted:
            found.append(f"Mounted, Ride {ride_bonus(f):+d}")
        if f.combatant.defends:
            found.append(f"Defends {named.get(f.combatant.defends, '(gone)')}")
        signs = f.signs()
        if signs is not None:
            found.append(f"Invisible ({signs.label})")
            seers = [named.get(u, "(gone)") for u in fight.located.get(f.id, [])]
            if seers:
                found.append("Located by " + ", ".join(seers))
    grip = grip_on(fight, unit.id)
    if grip is not None:
        found.append(f"Held by {named.get(grip.by, '(gone)')} (grip {grip.strength})")
    for g in grips_by(fight, unit.id):
        found.append(f"Holding {named.get(g.held, '(gone)')} (grip {g.strength})")
    return list(dict.fromkeys(found))


def range_text(fight: Fight) -> str:
    """ "Hand to hand", or the range increments between the sides."""
    if fight.range <= 0:
        return "Hand to hand"
    return f"{fight.range} range increment{'' if fight.range == 1 else 's'} apart"


def unsettles_horses(character: Character) -> bool:
    """Whether a horse will throw this rider: the Gift, unless it is the
    Gentle Gift (DE pp. 82, 205)."""
    return gifted(character) and not any(
        vf.vf_id == GENTLE_GIFT for vf in character.virtues_flaws
    )


# -- the magic a fighter brings --


@dataclass
class MagicOdds:
    """A spell or a device's effect before the dice: what it is, its
    Arts, level and Casting Score (none for a device), its Penetration
    bonus (a device's own Penetration), and the target's Magic
    Resistance against its Form."""

    name: str
    technique: str
    form: str
    level: int
    score: int | None
    penetration: int
    resistance: int
    spontaneous: bool = False
    #: A spell's Casting Score in full, for a spontaneous spell's total.
    breakdown: Breakdown | None = None
    requisites: tuple[str, ...] = ()
    #: Indirect: not resisted, but aimed with this roll (before the die)
    #: and these botch dice (DE p. 223).
    indirect: bool = False
    aim: Breakdown | None = None
    aim_botch_dice: int = 1
    #: The Mastery score, which also takes botch dice off (DE p. 225).
    mastery: int = 0
    #: The Penetration bonus's working, and why the target is out of
    #: reach ("" when it isn't).
    penetration_breakdown: Breakdown | None = None
    blocked: str = ""
    #: Notes for the inspector: the target's doubled resistance, the
    #: caster's schools of magical combat.
    notes: list[str] = field(default_factory=list)


def resistance_of(saga: Saga, fight: Fight, fighter: Fighter, form: str) -> int:
    """A fighter's Magic Resistance against `form`, the highest it has
    (resistances don't add): a magus's Form and Parma in the fight's aura;
    a character's True Faith, office and relic, or Angelic Might; a
    creature's Might + the aura's modifier for its realm (DE pp. 412,
    419-420); else what was typed for it."""
    c = fighter.character
    if c is not None:
        parma = (
            int(
                penetration.magic_resistance(
                    c, form, aura=fight.aura, aura_realm=realms.HERMETIC
                ).total
            )
            if c.arts
            else 0
        )
        return max(parma, penetration.faith_magic_resistance(c, saga))
    if fighter.combatant.kind == CREATURE_FIGHTER:
        creature = saga.creature(fighter.combatant.ref_id)
        if creature is not None and creature.realm:
            return penetration.creature_resistance(
                creature.might, creature.realm, realms.HERMETIC, fight.aura
            )
    return fighter.combatant.resistance


def spell_odds(
    saga: Saga, fight: Fight, who: Unit, target: Unit, blow: Blow
) -> MagicOdds | None:
    """The spell Cast a Spell would cast: its Casting Score in the fight's
    aura (DE p. 214), Penetration bonus, and the target's Magic
    Resistance."""
    magus = who.vanguard.character
    if magus is None:
        return None
    requisites: tuple[str, ...] = ()
    known = None
    spell = None
    if blow.spell == SPONTANEOUS:
        technique, _, form = (blow.arts or "Creo Ignem").partition(" ")
        level = blow.level
        score = casting.casting_score(
            magus,
            technique,
            form,
            aura=fight.aura,
            spontaneous=True,
            requisites=blow.casting_requisites,
        )
        name = f"A spontaneous {technique} {form} spell"
        requisites = blow.casting_requisites
    else:
        spell = catalog.find_spell(saga, blow.spell)
        if spell is None:
            return None
        known = magic_combat.known_spell(magus, spell.id)
        technique, form, level = spell.technique, spell.form, spell.level or 0
        score = casting.spell_casting_score(
            magus,
            spell,
            aura=fight.aura,
            casting_requisites=blow.casting_requisites,
            mastery=known.mastery_score if known else 0,
            mastery_abilities=magic_combat.mastery_abilities(known),
        )
        name = spell.name
        requisites = (*spell.requisites, *blow.casting_requisites)
    abilities = magic_combat.mastery_abilities(known)
    pierce = _penetration(magus, target, blow, magic_combat.penetration_mastery(known))
    resistance = resistance_of(saga, fight, target.vanguard, form)
    notes: list[str] = []
    victim = target.vanguard.character
    if (
        spell is not None
        and resistance
        and magic_combat.resists_doubly(victim, spell.id)
    ):
        resistance *= 2
        notes.append(
            f"{target.name} has mastered {spell.name} with Magic Resistance: "
            "doubled against it (DE p. 226)."
        )
    school = magic_combat.schools_text(magus)
    if school:
        notes.append(school)
    limit = magic_combat.indirect_note(spell)
    if limit:
        notes.append(limit)
    indirect = blow.indirect or magic_combat.is_indirect(spell)
    named = magic_combat.indirect_spell(spell)
    harmless = (
        f"{named.name} holds or traps and does no harm itself (HoH:S p. 30): "
        "leave Damage blank."
        if named is not None and named.harmless and blow.damage is not None
        else ""
    )
    precise = abilities.get(casting.PRECISE_CASTING, 0)
    return MagicOdds(
        name,
        technique,
        form,
        level,
        int(score.total),
        int(pierce.total),
        resistance,
        spontaneous=blow.spell == SPONTANEOUS,
        breakdown=score,
        requisites=requisites,
        indirect=indirect,
        aim=(
            magic_combat.aiming(magus, precise=precise, steps=blow.aim_steps)
            if indirect
            else None
        ),
        aim_botch_dice=magic_combat.aim_botch_dice(precise),
        mastery=known.mastery_score if known else 0,
        penetration_breakdown=pierce,
        blocked=harmless
        or _out_of_reach(
            fight,
            who,
            target,
            spell.range if spell else "",
            spell.target if spell else "",
        ),
        notes=notes,
    )


def _penetration(magus: Character, target: Unit, blow: Blow, mastery: int) -> Breakdown:
    """The Penetration bonus: (Penetration + Penetration Mastery) x (1 +
    the Arcane Connection + the sympathetic connections with it) (DE pp.
    219-220, 226; HoH:S p. 27)."""
    arcane = blow.arcane if blow.arcane in penetration.ARCANE_CONNECTIONS else None
    by_name = {s.name: s for s in penetration.SYMPATHIES}
    sympathies = [
        by_name[name]
        for name, used in (
            (magic_combat.NAME_SYMPATHY, blow.named),
            (magic_combat.SYMBOL_SYMPATHY, blow.symbol),
        )
        if used and name in by_name
    ]
    return penetration.penetration_bonus(
        magus,
        arcane_connection=arcane,
        sympathies=sympathies,
        mastery=mastery,
        target=target.vanguard.character,
    )


def _out_of_reach(
    fight: Fight, who: Unit, target: Unit, range_: str, target_kind: str
) -> str:
    """Why a spell or effect can't be aimed at the target: Eye range needs
    both to see each other; an unlocated invisible foe is reached only by
    an area spell or through an Arcane Connection (HoH:S p. 32). "" when
    it can."""
    if range_ == magic_combat.EYE_RANGE and (
        who.vanguard.signs() is not None or target.vanguard.signs() is not None
    ):
        return (
            "Eye range needs the two to see each other: no invisible fighter "
            "casts it or is caught by it (HoH:S p. 32)."
        )
    if unseen(fight, who, target) and not magic_combat.reaches_unlocated(
        range_, target_kind
    ):
        return (
            f"{who.name} doesn't know where the invisible {target.name} is: only "
            "an area spell or an Arcane Connection reaches it (HoH:S p. 32)."
        )
    return ""


def device_odds(
    saga: Saga, fight: Fight, target: Unit, blow: Blow, who: Unit | None = None
) -> MagicOdds | None:
    """The effect Use a Device would use: its Penetration as enchanted
    (DE p. 259) against the target's Magic Resistance; an indirect one is
    aimed with the wielder's Perception + Finesse instead (DE p. 223)."""
    device_id, _, effect_id = blow.effect.partition("|")
    device = next((d for d in saga.enchanted_devices if d.id == device_id), None)
    effect = (
        next((e for e in device.effects if e.id == effect_id), None) if device else None
    )
    if device is None or effect is None:
        return None
    user = who.vanguard.character if who is not None else None
    return MagicOdds(
        f"{device.name}: {effect.name or 'its effect'}",
        effect.technique,
        effect.form,
        effect.level,
        None,
        effect.penetration,
        resistance_of(saga, fight, target.vanguard, effect.form),
        indirect=blow.indirect and user is not None,
        aim=(
            magic_combat.aiming(user, steps=blow.aim_steps)
            if blow.indirect and user is not None
            else None
        ),
        blocked=(
            _out_of_reach(fight, who, target, effect.range, effect.target)
            if who is not None
            else ""
        ),
    )


# -- grappling, splitting and shield grogs --


def _take_hold(
    fight: Fight, who: Unit, target: Unit, advantage: int, lines: list[str]
) -> Played:
    """A grapple's Advantage becomes, or adds to, its Grapple Strength
    (DE p. 398)."""
    grip = grip_on(fight, target.id)
    if grip is None:
        grip = Grip(target.id, who.id, 0)
        fight.grips.append(grip)
    grip.strength += advantage
    lines.append(f"Grapple Strength {grip.strength}")
    return Played(f"{who.name} grapples {target.name} (grip {grip.strength}).", lines)


def _break_free(
    fight: Fight, who: Unit, holder: Unit, advantage: int, lines: list[str]
) -> Played:
    """An escape's Advantage comes off the Grapple Strength; at 0 or less
    the held one is free and the holder takes a Light Wound (DE p. 398)."""
    grip = grip_on(fight, who.id)
    if grip is None:
        return Played(f"{who.name} is held by nobody.", lines)
    grip.strength -= advantage
    if grip.strength > 0:
        lines.append(f"Grapple Strength {grip.strength}")
        return Played(
            f"{who.name} loosens {holder.name}'s grip (now {grip.strength}).", lines
        )
    fight.grips.remove(grip)
    holder.vanguard.wound("light")
    return Played(
        f"{who.name} breaks free of {holder.name}, who takes a Light Wound.", lines
    )


def _loosen(saga: Saga, fight: Fight) -> list[str]:
    """Let go every grapple whose holder or held one is down or gone."""
    every = units(saga, fight)
    told: list[str] = []
    for grip in list(fight.grips):
        held, by = every.get(grip.held), every.get(grip.by)
        if held is None or by is None or held.down() or by.down():
            fight.grips.remove(grip)
            if held is not None and by is not None:
                told.append(f"{by.name} lets go of {held.name}.")
    return told


def _exposed(saga: Saga, fight: Fight, unit: Unit) -> list[Fighter]:
    """Whom `unit`'s fighters defend: they are struck when their
    defenders botch (DE p. 397)."""
    guarded = {f.combatant.defends for f in unit.fighters if f.combatant.defends}
    return [
        f for u in units(saga, fight).values() for f in u.standing() if f.id in guarded
    ]


def _split_by(
    saga: Saga, fight: Fight, who: Unit, target: Unit, advantage: int, lines: list[str]
) -> Played:
    """An Advantage of 0 or more splits the group: in half, or in thirds
    when three or more press it and a second split succeeds this round
    (DE p. 398)."""
    lines.append(f"Attack Advantage {advantage}")
    group = target.group
    if advantage < 0 or group is None:
        return Played(f"{who.name} presses {target.name} but can't split it.", lines)
    fight.splits[target.id] = fight.splits.get(target.id, 0) + 1
    pressing = len(set(fight.attacked_by.get(target.id, [])))
    parts = 3 if fight.splits[target.id] >= 2 and pressing >= 3 else 2
    names = split_group(saga, fight, target, parts)
    return Played(f"{who.name} splits {target.name}: " + ", ".join(names) + ".", lines)


def split_group(saga: Saga, fight: Fight, unit: Unit, parts: int) -> list[str]:
    """Divide a group's standing members as evenly as can be into `parts`
    (the first keeps the group, its vanguard first); a part of one fights
    alone. Each new part acts at the group's place in the order. Returns
    the parts' names."""
    group = unit.group
    if group is None:
        return [unit.name]
    side = fight.sides[unit.side]
    standing = [f.id for f in unit.standing()]
    parts = max(1, min(parts, len(standing)))
    size, extra = divmod(len(standing), parts)
    chunks: list[list[str]] = []
    at = 0
    for k in range(parts):
        n = size + (1 if k < extra else 0)
        chunks.append(standing[at : at + n])
        at += n
    group.members = chunks[0]
    made: list[str] = []
    for k, chunk in enumerate(chunks[1:], start=2):
        if len(chunk) == 1:
            made.append(chunk[0])
        else:
            new = FightGroup(f"{group.name or unit.name} ({k})", chunk)
            side.groups.append(new)
            made.append(new.id)
    if group.id in fight.order:
        at = fight.order.index(group.id) + 1
        fight.order[at:at] = made
        for ident in made:
            fight.initiative[ident] = fight.initiative.get(group.id, 0)
        if at <= fight.turn:
            fight.turn += len(made)
    every = units(saga, fight)
    return [every[i].name for i in [group.id, *made] if i in every]


# -- casting and devices in the fight --


def _magic(
    saga: Saga,
    fight: Fight,
    who: Unit,
    target: Unit,
    action: str,
    blow: Blow,
    rng: random.Random,
) -> Played:
    """A spell cast or a device used on `target`: the Casting Total
    against the level (a spell), then Penetration against its Magic
    Resistance, then any damage: stress die + X against Soak (with the
    Form's Bonus) + stress die (DE pp. 214, 259, 394)."""
    lines: list[str] = []
    odds_ = (
        spell_odds(saga, fight, who, target, blow)
        if action == CAST
        else device_odds(saga, fight, target, blow, who)
    )
    if odds_ is None:
        return Played(f"{who.name} has nothing to cast or use.", lines)
    if odds_.blocked:
        return Played(odds_.blocked, lines)
    if action == CAST:
        magus = who.vanguard.character
        if magus is not None and casting_virtues.incompatible(
            magus, odds_.technique, odds_.form, odds_.requisites
        ):
            return Played(
                f"{who.name} can't cast {odds_.name}: Incompatible Arts (DE p. 134).",
                lines,
            )
        total = _casting_total(saga, who, odds_, blow, rng, lines)
        if total is None:
            return Played(
                f"{who.name} botches {odds_.name}: the storyguide says what goes "
                "wrong.",
                lines,
            )
        if magus is not None and casting_virtues.painful(magus):
            who.vanguard.tire(1)
            lines.append("Painful Magic: a level of pain (DE p. 140).")
        if odds_.spontaneous:
            short = _spontaneous_short(who, odds_, blow, total, lines)
            if short is not None:
                return Played(short, lines)
        else:
            outcome = casting.formulaic_outcome(total, odds_.level)
            if not outcome.cast:
                return Played(f"{who.name} fails to cast {odds_.name}.", lines)
            if outcome.fatigue:
                who.vanguard.tire(outcome.fatigue)
                lines.append("Short of the level: a Fatigue level spent.")
        pierce = total - odds_.level + odds_.penetration
    else:
        pierce = odds_.penetration
    fight.attacked_by.setdefault(target.id, []).append(who.id)
    if odds_.indirect:
        missed = _aim(saga, fight, who, target, odds_, rng, lines)
        if missed is not None:
            return Played(missed, lines)
    else:
        lines.append(
            f"Penetration {pierce} against Magic Resistance {odds_.resistance}"
        )
        if not penetration.penetrates(pierce, odds_.resistance or None):
            return Played(f"{target.name} resists {odds_.name}.", lines)
    if blow.damage is None:
        return Played(f"{odds_.name} takes {target.name}.", lines)
    victim = target.vanguard
    damage, _ = _roll(rng, saga, "Damage", blow.damage, lines)
    shield = victim.character
    form_bonus = derived.form_bonus(shield, odds_.form) if shield else 0
    soak_base = victim.figures().soak + form_bonus
    if form_bonus:
        lines.append(f"{odds_.form} Form Bonus +{form_bonus}")
    soak, _ = _roll(rng, saga, "Soak", soak_base, lines)
    excess = damage - soak
    lines.append(f"Damage {damage} against Soak {soak}: {max(0, excess)} through")
    if excess <= 0:
        return Played(f"{odds_.name} strikes {target.name}, who shrugs it off.", lines)
    told = _land([victim], 1, excess, scuffle=False)
    lines += told
    return Played(
        f"{odds_.name} strikes {target.name}: " + "; ".join(told) + ".", lines
    )


def aim_defence(fight: Fight, target: Unit) -> list[Term]:
    """What an aimed spell rolls against: the target's Defence against a
    missile (aimed spells are treated like missiles, HoH:S p. 32), with its
    group's bonus and its invisibility's (DE p. 223)."""
    terms = [Term("Defence", target.vanguard.figures().missile_defence)]
    bonus = target.bonus()
    if target.group is not None and target.group.bonus_to == "defence" and bonus:
        terms.append(Term("Group bonus", bonus, f"Group bonus +{bonus} to Defence"))
    signs = target.vanguard.signs()
    if signs is not None:
        terms.append(
            Term(
                "Invisible",
                signs.defence,
                f"Invisible ({signs.label}): +{signs.defence} to Defence",
            )
        )
    return terms


def _aim(
    saga: Saga,
    fight: Fight,
    who: Unit,
    target: Unit,
    odds_: MagicOdds,
    rng: random.Random,
    lines: list[str],
) -> str | None:
    """An indirect spell's aiming roll: Perception + Finesse + stress die,
    as an attack total, against the target's Defence + stress die; Magic
    Resistance doesn't stop it (DE p. 223). Returns why it missed, or None
    when it hits."""
    lines.append(
        f"{odds_.name} is indirect: Magic Resistance doesn't stop it, but it "
        "must be aimed (DE p. 223)."
    )
    guard_terms = aim_defence(fight, target)
    lines += [t.line for t in guard_terms if t.line]
    aim = int(odds_.aim.total) if odds_.aim is not None else 0
    hit, botched = _roll(rng, saga, "Aiming", aim, lines, odds_.aim_botch_dice)
    guard, _ = _roll(rng, saga, "Defence", sum(t.amount for t in guard_terms), lines)
    if botched:
        return (
            f"{who.name} botches the aim of {odds_.name}: the storyguide says "
            "what it strikes instead."
        )
    if hit <= guard:
        return f"{odds_.name} misses {target.name}."
    return None


def _spontaneous_short(
    who: Unit, odds_: MagicOdds, blow: Blow, total: int, lines: list[str]
) -> str | None:
    """A spontaneous spell reaches the level declared only if its total
    does (DE p. 214), else it fails; with Life-Linked Spontaneous Magic, a
    fatiguing one still takes effect for a Fatigue level more for each 5
    short, and past the last level a wound of the levels still owed (DE p.
    91). Returns why it failed, or None when it takes effect."""
    if total >= odds_.level:
        return None
    magus = who.vanguard.character
    if magus is None or not blow.fatiguing or not casting_virtues.life_linked(magus):
        return f"{who.name}'s spell falls short of level {odds_.level} ({total})."
    owed = casting_virtues.life_linked_cost(odds_.level, total)
    fighter = who.vanguard
    left = len(FATIGUE_LEVELS) - 1 - FATIGUE_LEVELS.index(magus.fatigue_level)
    spent = min(owed, left)
    fighter.tire(spent)
    lines.append(f"Life-Linked: {spent} more Fatigue level(s)")
    if owed > spent:
        band = derived.wound_for(owed - spent, fighter.figures().size)
        if band is not None:
            fighter.wound(band.lower())
            lines.append(
                f"Life-Linked: {owed - spent} levels still owed, a {band} Wound"
            )
    return None


def _casting_total(
    saga: Saga,
    who: Unit,
    odds_: MagicOdds,
    blow: Blow,
    rng: random.Random,
    lines: list[str],
) -> int | None:
    """The Casting Total: Casting Score + stress die for a Formulaic
    spell; (score + stress die) / 2 for a fatiguing spontaneous one, which
    costs a Fatigue level, and score / 5 for a non-fatiguing one (DE pp.
    214-215). None on a botch."""
    score = odds_.score or 0
    # A mastered spell's score comes off its botch dice, to none (DE p. 225).
    botch_dice = max(0, 1 - odds_.mastery)
    if odds_.spontaneous and not blow.fatiguing:
        total = (
            casting.spontaneous_total(odds_.breakdown)
            if odds_.breakdown is not None
            else score // 5
        )
        lines.append(f"Casting Total {score} / 5 = {total}")
        return total
    die = dice.stress_die(rng, botch_dice, saga=saga)
    if die.botched:
        lines.append(f"Casting: a botch ({die.botches} on the botch dice)")
        return None
    if odds_.spontaneous:
        who.vanguard.tire(1)
        total = (
            casting.spontaneous_total(odds_.breakdown, die.value)
            if odds_.breakdown is not None
            else (score + die.value) // 2
        )
        lines.append(
            f"Casting Total ({score} + stress die {die.value}) / 2 = {total}; "
            "a Fatigue level spent"
        )
        return total
    total = score + die.value
    lines.append(f"Casting Total {score} + stress die {die.value} = {total}")
    return total
