"""Arms, armour and gear beyond their catalog figures.

- How well an item is made (City & Guild pp. 67-69, as Lords of Men p. 136
  sums it up): a Shoddy item is destroyed the first time it fails a stress
  check; a Superior weapon has +1 Attack, a Superior shield +1 Defence,
  Superior armour +1 Protection; an Excellent item +2 or more, on a
  weapon to Attack and Defence both.
- The Clash of Weapons (Lords of Men p. 138, optional): when a melee Attack
  Total exactly equals the Defence Total, the weaker side (Strength +
  Ability + simple die) rolls stress die + Ability against 9 (15 for an
  improvised weapon); failing costs the item a damage level. Most weapons
  and shields have two, spears and lances one.
- Damaged goods (City & Guild pp. 77-79): when a botch or an unnatural use
  threatens an item, a stress die + modifiers against 15 (the wielder's
  Ability, -1 once repaired, -1 Shoddy, +1 Superior, +3 Excellent, +5
  wondrous, + the magnitudes of a Hermetic item's effects; -1 to -3 for
  light and weather, -3 for prolonged use). Failing costs a damage level,
  a botch one more per botch; with none left the item is broken. Damage
  levels are 1 Shoddy, 2 standard, 3 Superior, 4 Excellent, 5 supernatural,
  times 1 for an item of Size +1 or less. A standard item is mended in a
  season; a Superior or Excellent one by a craftsman with Craft twice its
  bonus, 1 Labor Point a damage level.
- Carrying (Grogs pp. 47-48): a Load point is about 7 pounds; a character
  can carry a Burden of Strength + 5, lift Strength + 7 and drag Strength
  + 12, a four-footed beast with its Strength half again.
- Equipment that helps an Ability roll it isn't essential to takes 1 (minor)
  or 3 (major) off its Ease Factor, one item a roll (Grogs p. 47).
"""

from __future__ import annotations

from ..models import Character, Possession
from .rounding import round_down

SOURCE = (
    "Lords of Men, Arms and Armor, pp. 136-138; Grogs, Equipping the Grogs, "
    "pp. 47-48; City & Guild, Damaged Goods, pp. 77-79"
)
DAMAGE_SOURCE = "City & Guild, Damaged Goods, pp. 77-79"
QUALITY_SOURCE = (
    "City & Guild pp. 67-69, as summed up in Lords of Men, Arms and Armor, p. 136"
)
CLASH_SOURCE = "Lords of Men, Arms and Armor, Option: The Clash of Weapons, p. 138"
CARRY_SOURCE = "Grogs, Equipping the Grogs, pp. 47-48"

SHODDY = "Shoddy"
SUPERIOR = "Superior"
EXCELLENT = "Excellent"
#: How an item is made ("" for standard).
MAKES: tuple[str, ...] = ("", SHODDY, SUPERIOR, EXCELLENT)
EXCELLENT_LEAST = 2
BREAKAGE_EASE = 9
IMPROVISED_EASE = 15
#: Lords of Men's weapon tables (pp. 137-138): each catalog weapon's
#: damage types (C crushing, P piercing, S slashing) and damage levels.
LORDS_OF_MEN_WEAPONS: dict[str, tuple[str, int]] = {
    "weapon_gauntlet": ("C", 2),
    "weapon_bludgeon": ("C", 1),
    "weapon_dagger": ("P, S", 2),
    "weapon_knife": ("P, S", 2),
    "weapon_axe": ("S", 2),
    "weapon_club": ("C", 1),
    "weapon_hatchet": ("S", 2),
    "weapon_lance": ("P", 1),
    "weapon_mace": ("C", 2),
    "weapon_mace_and_chain": ("C", 2),
    "weapon_short_spear": ("P", 1),
    "weapon_short_sword": ("P, S", 2),
    "weapon_long_sword": ("S, P", 2),
    "weapon_buckler": ("", 2),
    "weapon_round_shield": ("", 1),
    "weapon_heater_shield": ("", 2),
    "weapon_cudgel": ("C", 2),
    "weapon_farm_implement": ("P, S", 1),
    "weapon_flail": ("C", 2),
    "weapon_pole_arm": ("S, P", 2),
    "weapon_pole_axe": ("S", 2),
    "weapon_long_spear": ("P", 1),
    "weapon_great_sword": ("S, P", 2),
    "weapon_staff": ("C", 2),
    "weapon_warhammer": ("C", 2),
    "weapon_throwing_axe": ("S", 2),
    "weapon_javelin": ("P", 2),
    "weapon_throwing_knife": ("P", 2),
    "weapon_sling": ("P", 1),
    "weapon_long_bow": ("P", 2),
    "weapon_short_bow": ("P", 2),
}
STRESS_EASE = 15
STANDARD_DAMAGE_LEVELS = 2
DAMAGE_LEVELS: dict[str, int] = {SHODDY: 1, SUPERIOR: 3, EXCELLENT: 4}
POUNDS_PER_LOAD = 7
#: Burden past Strength: carried, lifted off the ground, pushed or dragged.
CARRY, LIFT, DRAG = 5, 7, 12
#: What helpful equipment takes off an Ease Factor.
ASSISTANCE: dict[str, int] = {"Minor": 1, "Major": 3}


def quality_bonus(item: Possession) -> int:
    """What how well it is made adds: +1 Superior, +2 or more Excellent."""
    if item.make == SUPERIOR:
        return 1
    if item.make == EXCELLENT:
        return max(EXCELLENT_LEAST, item.make_bonus)
    return 0


def is_shield(item: Possession) -> bool:
    """A shield or buckler (a weapon carried in the off hand)."""
    words = f"{item.gear_id or ''} {item.name}".casefold()
    return item.kind == "weapon" and ("shield" in words or "buckler" in words)


def damage_levels(item: Possession) -> int:
    """The damage levels a weapon, shield or suit of armour takes before
    it breaks: a standard weapon's from Lords of Men's tables (pp.
    137-138; anything else 2), moved by how well it is made as City &
    Guild's base levels move (p. 77: Shoddy 1, standard 2, Superior 3,
    Excellent 4)."""
    standard = LORDS_OF_MEN_WEAPONS.get(
        item.gear_id or "", ("", STANDARD_DAMAGE_LEVELS)
    )[1]
    shift = (
        DAMAGE_LEVELS.get(item.make, STANDARD_DAMAGE_LEVELS) - STANDARD_DAMAGE_LEVELS
    )
    return max(1, standard + shift)


def damage_types(item: Possession) -> str:
    """The weapon's damage types from Lords of Men's tables ("" unknown)."""
    return LORDS_OF_MEN_WEAPONS.get(item.gear_id or "", ("", 0))[0]


def stress_check_bonus(item: Possession, ability: int) -> int:
    """What adds to a stress die against 15 to keep the item whole: the
    wielder's Ability and how well it is made; the scene's light, weather
    and use are the storyguide's."""
    made = {SHODDY: -1, SUPERIOR: 1, EXCELLENT: 3}.get(item.make, 0)
    return ability + made


def breakage_ease(item: Possession) -> int:
    """The Clash of Weapons' Ease Factor: 15 for something that isn't a
    weapon (a hand tool, a kitchen knife), 9 for one."""
    return BREAKAGE_EASE if item.gear_id else IMPROVISED_EASE


#: The animal kinds that go on four feet (not birds or fish).
FOUR_FOOTED = ("clawed", "hoofed")


def effective_strength(character: Character) -> int:
    """Strength for carrying: a four-footed beast's half again (Grogs p.
    48)."""
    strength = character.characteristics.strength
    if (
        character.animal is not None
        and character.animal.kind in FOUR_FOOTED
        and strength > 0
    ):
        return strength + round_down(strength / 2)
    return strength


def load_for_burden(burden: int) -> int:
    """The least Load that is this Burden: n(n + 1) / 2."""
    n = max(0, burden)
    return n * (n + 1) // 2


def carrying(character: Character) -> tuple[int, int, int]:
    """The Load the character can carry, lift off the ground and drag."""
    strength = effective_strength(character)
    return (
        load_for_burden(strength + CARRY),
        load_for_burden(strength + LIFT),
        load_for_burden(strength + DRAG),
    )
