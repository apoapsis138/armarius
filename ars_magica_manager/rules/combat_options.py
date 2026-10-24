"""Lords of Men's optional combat rules (Chapter Nine, pp. 117-135), as
figures and tables a combat screen can use: the totals each option rolls,
before the stress die, and the Ease Factors and modifiers it sets.

- Interrupting: Action Priority = Quickness + the action's Ability -
  Encumbrance (Finesse for a spell, Athletics to move, Ride riding).
- Charging on foot: + the Combat Ability to the Attack, a Fatigue level
  (none across difficult terrain); on horseback the horse spends it.
- Helpless: Defence -10, no roll; Diceless Defence: 6 for the die.
- Evasion: Quickness + Brawl (Ride mounted) - Size - Encumbrance + the
  shield's Defence.
- Mounted: the Attack bonus for melee only (the DE gives it to every
  attack, and the app follows the DE); the gaits' movement, missile
  penalty, falling damage, extended-action Ease Factor and defensive bonus;
  resisting a charge's shock; leaping from or vaulting into the saddle;
  being pinned under a horse; keeping a panicking horse in hand.
- Battlefield situations: cover and concealment Defence bonuses, higher
  ground +1, at most six attackers on one defender (four with his back to a
  wall, two from each side in a doorway), -1 to -3 in a cramped space.
- Maneuvers: the Attack Advantage each needs; a giant's +2 x the Size
  difference against them.
- Groups: accelerated training's Ease Factors; Discipline and Morale
  (leader's Presence + Leadership, + the members' lowest Loyal or Brave);
  rallying; replacing a vanguard or taking the lead in combat (9).

No screen plays combat rounds yet: these are the rules for one still to
come, and only the tests call them.
"""

from __future__ import annotations

from ..models import Character
from .derived import carried_load, encumbrance
from .lab import ability_score

SOURCE = "Lords of Men, Chapter Nine: Optional Combat Rules, pp. 117-135"
HELPLESS_DEFENCE = -10
DICELESS_DIE = 6
HIGHER_GROUND = 1
#: Attackers on one defender: in the open, back to a wall, in a doorway
#: (from each side).
MOST_ATTACKERS = {"open": 6, "wall": 4, "doorway": 2}
#: Cover: (Defence bonus).
COVER: dict[str, int] = {
    "One-quarter": 3,
    "One-half": 6,
    "Three-quarters": 9,
    "Near total": 12,
}
#: Concealment: (melee Attack bonus, Defence bonus).
CONCEALMENT: dict[str, tuple[int, int]] = {
    "Light": (1, 3),
    "Medium": (3, 6),
    "Heavy": (6, 9),
    "Total": (9, 9),
}
#: A gait: (missile Attack penalty, falling damage over the horse's Size,
#: extended action Ease Factor, optional defensive bonus).
GAITS: dict[str, tuple[int, int, int, int]] = {
    "Stationary": (0, 0, 0, 0),
    "Walk or Trot": (-1, 2, 6, 1),
    "Canter": (-3, 4, 9, 3),
    "Gallop": (-6, 6, 12, 6),
}
#: Paces a round by gait, for a horse's Quickness of -3 or less, -2 to -1,
#: 0, +1 to +2, +3 to +4, +5 (the table's bands).
MOUNTED_PACES: dict[str, tuple[int, ...]] = {
    "Walk": (7, 8, 10, 12, 15, 18),
    "Trot": (12, 15, 20, 25, 30, 35),
    "Canter": (20, 25, 30, 35, 45, 50),
    "Gallop": (30, 40, 50, 60, 70, 80),
}
#: Maneuvers: the Attack Advantage each needs (p. 133).
MANEUVERS: dict[str, int] = {
    "Trip or Throw": 3,
    "Grapple": 1,
    "Pin": 6,
    "Tackle": 1,
    "Disarm": 9,
    "Grab Worn Item": 6,
    "Unseat Rider": 6,
    "Wrest Weapon": 12,
}
GRAPPLED_PENALTY = -6
#: Shortening a group's training: the time and its Ease Factor.
TRAINING_TIME: dict[str, int] = {
    "Two Months": 6,
    "Six Weeks": 9,
    "One Month": 12,
    "Fortnight": 15,
    "One Week": 18,
}
DISCIPLINE: dict[str, int] = {
    "Crossing difficult terrain": 3,
    "Running (not charging)": 6,
    "The enemy disengages": 6,
    "The enemy routs": 9,
    "Disengaging": 9,
    "Changing between melee and missiles": 6,
}
MORALE: dict[str, int] = {
    "Missile wounds with no missiles of its own": 6,
    "Charged by an equal force": 6,
    "Charged by a superior force": 9,
    "Ambushed or attacked from the rear": 9,
    "Every member at -3 or worse": 9,
    "Vanguard or leader down": 9,
}
RALLY: dict[str, int] = {
    "Not engaged": 3,
    "Under missile fire": 6,
    "Engaged in melee": 9,
    "Routed and hotly pursued": 12,
}
RALLY_CASUALTIES = 1
RALLY_HALF_LOST = 3
TAKE_CHARGE_EASE = 9
LEAP_EASE = 9
VAULT_EASE = 6
PINNED_EASE = 6
PANIC_EASE = 6
#: A saddle's modifier to resisting a charge.
SADDLES = {"cantled": 3, "": 0, "no stirrups": -3}


def _score(character: Character, ability: str) -> int:
    return sum(ability_score(character, ability))


def _encumbrance(character: Character) -> int:
    return encumbrance(
        carried_load(character.inventory), character.characteristics.strength
    )


def action_priority(character: Character, ability: str) -> int:
    """Quickness + the action's Ability - Encumbrance."""
    return (
        character.characteristics.quickness
        + _score(character, ability)
        - _encumbrance(character)
    )


def evasion(
    character: Character, size: int, shield_defence: int = 0, *, mounted: bool = False
) -> int:
    """Quickness + Brawl (Ride mounted) - Size - Encumbrance + shield."""
    return (
        character.characteristics.quickness
        + _score(character, "Ride" if mounted else "Brawl")
        - size
        - _encumbrance(character)
        + shield_defence
    )


def mounted_paces(gait: str, quickness: int) -> int:
    """A horse's paces a round at a gait, by its Quickness."""
    bands = (-3, -1, 0, 2, 4)
    index = next((i for i, top in enumerate(bands) if quickness <= top), len(bands))
    return MOUNTED_PACES[gait][index]


def resist_charge(
    character: Character,
    size: int,
    *,
    mounted: bool,
    saddle: str = "",
    ability: str = "",
) -> int:
    """Resisting a charge's shock, before the die: mounted Dexterity + Ride
    + the saddle; on foot Strength + Size + the Combat Ability. Against the
    charge's Damage Total (before Soak) + the horse's Size."""
    c = character.characteristics
    if mounted:
        return c.dexterity + _score(character, "Ride") + SADDLES.get(saddle, 0)
    return c.strength + size + (_score(character, ability) if ability else 0)


def leap_from_saddle(character: Character) -> int:
    """Dexterity + Athletics - Encumbrance, against 9."""
    return (
        character.characteristics.dexterity
        + _score(character, "Athletics")
        - _encumbrance(character)
    )


def vault_into_saddle(character: Character) -> int:
    """Strength + Athletics - Encumbrance, against 6."""
    return (
        character.characteristics.strength
        + _score(character, "Athletics")
        - _encumbrance(character)
    )


def panic_ease(horse_wound_penalty: int) -> int:
    """Keeping a panicking horse in hand: Presence + Ride against 6 less
    the horse's (negative) Wound Penalty."""
    return PANIC_EASE - horse_wound_penalty


def giant_defence(size: int, other: int) -> int:
    """What a far larger creature adds to its Defence against maneuvers."""
    return max(0, 2 * (size - other))


def leadership_roll(leader: Character) -> int:
    """Discipline, Morale, rallying and taking charge: Presence +
    Leadership, before the die."""
    return leader.characteristics.presence + _score(leader, "Leadership")


def rally_ease(situation: str, casualties: int, members: int) -> int:
    """A rally's Ease Factor: the situation's, +1 with casualties, +3 with
    half or more."""
    ease = RALLY[situation]
    if members and casualties * 2 >= members:
        ease += RALLY_HALF_LOST
    elif casualties:
        ease += RALLY_CASUALTIES
    return ease


def trait_bonus(members: list[Character], trait: str) -> int:
    """The lowest Loyal (or Brave) trait among the members, when every one
    has it positive; else nothing."""
    scores: list[int] = []
    for member in members:
        found = [
            t.score
            for t in member.personality_traits
            if t.name.casefold().startswith(trait.casefold()) and t.score > 0
        ]
        if not found:
            return 0
        scores.append(max(found))
    return min(scores) if scores else 0
