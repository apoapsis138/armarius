"""The clesrada, the Ulster heroes' feats of arms (The Contested Isle,
pp. 101-105). Each cles is a Faerie power gained by its own Initiation,
under Úathach at Leth Cuinn, and used by a stress feat roll:

    Feat roll = the cles's Characteristic + its Ability + a stress die
                (+ the aura's Faerie modifier), against its Ease Factor

- A cles may be used any number of times a day, at no cost unless it
  says so; a botch always costs a Fatigue level besides its own harm.
- A feat roll counts as casting a 15th-level spell with a Penetration
  Total of 0 + the Penetration bonus: magic that affects spells (an
  Aegis of the Hearth) can touch it. Clesa act on the user, like Aimed
  spells, and need not penetrate a foe's Magic Resistance; while one
  works the user counts as magical (p. 101).
- Several clesa of the same Ability may be chained into one action, each
  rolled in turn; the first failure ends the chain, and the user does
  nothing else that round, an Attack included (p. 102).
- Initiation: a quest tied in symbol to the feat and a geas (a
  Prohibition Flaw) as the Ordeal, Ease Factor 15, no bonus for an
  earlier Ordeal, so the unGifted can be Initiated (pp. 101, HMRE p. 14).
  Úathach's Presence + Organization Lore: Clesrada is 12. Breaking the
  geas loses that cles.

The catalog's Clesrada tradition holds the clesa as guidelines (each
Ease Factor) and a feat roll for each Characteristic; this module holds
the clesa's own numbers.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character
from . import hedge_casting as hc
from . import penetration, realms
from .lab_virtues import has
from .rounding import round_up

SOURCE = "The Contested Isle, The Clesrada, pp. 101-105"
TRADITION_ID = "trad_clesrada"
LORE = "Organization Lore: Clesrada"
PERFECT_BALANCE = "vf_perfect_balance"
#: A feat roll's equivalent spell level, for magic that affects spells.
FEAT_LEVEL = 15
INITIATION_EASE = 15
#: Úathach's Presence + Organization Lore: Clesrada (p. 101).
UATHACH_TOTAL = 12
PERFECT_BALANCE_BONUS = 6


@dataclass(frozen=True)
class Cles:
    """One feat: its Irish and English names, the Characteristic and
    Ability of its roll, and its base Ease Factor (0: the foe's Defense
    Total sets it)."""

    name: str
    english: str
    characteristic: str
    ability: str
    ease: int


CLESA: tuple[Cles, ...] = (
    Cles("Baí Brasse", "Profit of Speed", "Quickness", "Athletics", 9),
    Cles("Cless Caitt", "Cat Feat", "Dexterity", "Athletics", 9),
    Cles("Ích-n-Erred", "Hero's Salmon Leap", "Strength", "Athletics", 9),
    Cles("Ochtarchless", "Eight-Men Feat", "Stamina", "Athletics", 9),
    Cles("Rothchless", "Wheel Feat", "Strength", "Athletics", 9),
    Cles("Tétchless", "Rope Feat", "Dexterity", "Athletics", 3),
    Cles("Cless For Análaib", "Breath Feat", "Stamina", "Concentration", 9),
    Cles("Corpchless", "Body Feat", "Dexterity", "Concentration", 6),
    Cles(
        "Sáebchless Díberge", "Wild Feat of Contortion", "Quickness", "Concentration", 9
    ),
    Cles("Siaburchles", "Phantom Feat", "Quickness", "Concentration", 9),
    Cles("Béim Co Commus", "Stroke of Precision", "Dexterity", "Single Weapon", 9),
    Cles("Brúd nGeme", "Crushing Roar", "Stamina", "Single Weapon", 9),
    Cles("Fáenchless", "Sloped Shield Feat", "Strength", "Single Weapon", 9),
    Cles("Foramchles", "Swooping Feat", "Stamina", "Single Weapon", 3),
    Cles("Cless Cletenach", "Javelin Feat", "Dexterity", "Thrown Weapon", 9),
    Cles("Cless Nónbair", "Nine-Men Feat", "Strength", "Thrown Weapon", 6),
    Cles("Torannchless", "Thunder Feat", "Strength", "Thrown Weapon", 6),
    Cles("Ubullchless", "Apple Feat", "Dexterity", "Thrown Weapon", 3),
)
#: A Single Weapon cles may be learned with Great Weapon instead, chosen
#: at Initiation (p. 103).
WEAPON_SWAP = {"Single Weapon": "Great Weapon"}


def find(name: str) -> Cles:
    """A cles by its Irish or English name."""
    for cles in CLESA:
        if name in (cles.name, cles.english):
            return cles
    raise LookupError(f"No cles is called {name!r}")


def feat_total(
    character: Character,
    cles: Cles,
    die: int = 0,
    *,
    ability: str = "",
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
) -> int:
    """The feat roll: Characteristic + Ability + die + the aura's modifier
    for a Faerie power; `ability` names Great Weapon for a Single Weapon
    cles learned with it. Perfect Balance adds 6 to the Rope Feat
    (p. 103)."""
    used = ability or cles.ability
    if used != cles.ability and WEAPON_SWAP.get(cles.ability) != used:
        raise ValueError(f"{cles.english} doesn't use {used}")
    value = getattr(character.characteristics, cles.characteristic.lower())
    total = value + hc.score(character, used) + die
    total += realms.aura_modifier("Faerie", aura_realm, aura)
    if cles.english == "Rope Feat" and has(character, PERFECT_BALANCE):
        total += PERFECT_BALANCE_BONUS
    return total


def feat_penetration(character: Character) -> int:
    """The Penetration Total a feat counts as: 0 + the Penetration bonus
    (p. 101)."""
    return int(penetration.penetration_bonus(character).total)


def chain(results: Sequence[tuple[int, int]]) -> int:
    """How many feats of a chain are done: each (total, Ease Factor) in
    turn, until the first that falls short (p. 102)."""
    done = 0
    for total, ease in results:
        if total < ease:
            break
        done += 1
    return done


# ---------------------------------------------------------------------------
# Ease Factors that change with the feat (pp. 102-105)


def rope_ease(*, unstable: bool = False, moving: bool = False, slope: int = 0) -> int:
    """The Rope Feat: 3, +3 unstable, +3 moving, +3 for a slope up to 45
    degrees or +6 for a steeper one."""
    ease = 3 + (3 if unstable else 0) + (3 if moving else 0)
    if slope > 45:
        ease += 6
    elif slope > 0:
        ease += 3
    return ease


def fall_damage_ignored(total: int) -> int:
    """A Rope Feat roll against 3 when falling ignores a point of damage
    for every two points it beats the Ease Factor by."""
    return max(total - 3, 0) // 2


#: The Body Feat's Ease Factor by what it does.
BODY_EASE = {"escape shackles": 6, "one Size smaller": 9, "two Sizes smaller": 12}
#: Escaping a grapple with the Body Feat: +3 against Ease Factor 6.
BODY_GRAPPLE_EASE = 6


def crushing_roar_ease(quality: str = "Standard") -> int:
    """9, +1 Superior, +3 Excellent, +6 enchanted (C&G p. 67 qualities)."""
    return 9 + {"Standard": 0, "Superior": 1, "Excellent": 3, "Enchanted": 6}[quality]


def swooping_ease(protection: int) -> int:
    """The Swooping Feat: 3 + the armour's original Protection."""
    return 3 + protection


def swooping_protection_lost(protection: int) -> int:
    """A sundered location takes a fifth of the Protection, rounded up."""
    return round_up(protection / 5)


def nine_men_ease(javelins: int) -> int:
    """6, +1 a javelin after the first (up to nine)."""
    if not 1 <= javelins <= 9:
        raise ValueError("The Nine-Men Feat casts one to nine javelins")
    return 6 + javelins - 1


def thunder_ease(brawl_defense: int) -> int:
    """6 + the foe's Brawl Defense Total."""
    return 6 + brawl_defense


def apple_ease(missiles: int) -> int:
    """3 + 2 a missile juggled (up to nine)."""
    if not 1 <= missiles <= 9:
        raise ValueError("The Apple Feat juggles one to nine missiles")
    return 3 + 2 * missiles


def walking_pace(quickness: int, encumbrance: int) -> int:
    """Paces a round at a walk: 10 + Qik - Encumbrance (LoM p. 120)."""
    return 10 + quickness - encumbrance


def profit_of_speed(quickness: int, encumbrance: int) -> tuple[int, int]:
    """Paces a round hurrying and running with the Profit of Speed: three
    and six times walking pace (twice and four times without)."""
    pace = walking_pace(quickness, encumbrance)
    return 3 * pace, 6 * pace


def cat_feat_heights(encumbrance: int) -> int:
    """The Cat Feat's standing long jump, in the character's heights: 8 -
    Encumbrance."""
    return max(8 - encumbrance, 0)


def salmon_leap_heights(encumbrance: int) -> int:
    """The Salmon Leap's standing high jump, in heights: 4 - half the
    Encumbrance, rounded up."""
    return max(4 - round_up(encumbrance / 2), 0)


EIGHT_MEN_STRENGTH = 5
JAVELIN_RANGE = 15


def javelin_damage(strength: int, weapon_damage: int, advantage: int) -> int:
    """The Javelin Feat's Damage Total: 2 x (Strength + the weapon's
    Damage) + the Attack Advantage."""
    return 2 * (strength + weapon_damage) + advantage


def rothchless_damage(load: int) -> int:
    """The Wheel Feat's Weapon Damage Modifier: the object's Load."""
    return load
