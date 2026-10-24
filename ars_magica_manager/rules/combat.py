"""Combat totals, before the stress die:

    Initiative = Quickness + weapon Init - Encumbrance
    Attack     = Dexterity + Combat Ability + weapon Atk
    Defence    = Quickness + Combat Ability + weapon Dfn
    Damage     = Strength + weapon Dam (+ the Attack Advantage when it hits)

Wound and Fatigue penalties apply to every roll. Encumbrance doesn't reduce
Attack or Defence when it comes mostly from weapons and armour, so it only
comes off Initiative here. The Combat Ability is the one the weapon's
catalog entry names; a weapon typed in by hand has none.

A specialty in the Combat Ability that names the weapon adds 1 to Attack
and Defence (DE Chapter Five, Specialties). Virtues and Flaws add their
combat_* modifiers, all or those for the weapon's table or name (Lame,
Missing Eye, Poor Eyesight, a natural weapon's Qualities); Primitive
Equipment takes 1 from Attack and Defence with a weapon that isn't
Inexpensive, and 1 from Initiative in armour that isn't.

With a weapon and a shield, the two items' modifiers add together (DE p.
393): a one-handed weapon of Single Weapon (a lance too) is fought with
the best shield the character carries. Against missiles only a shield's
Defence counts, with the Combat Ability (DE p. 395). A lance is wielded
from horseback; on foot it is a long spear (DE pp. 400-401).

How well an item is made adds to it (rules.equipment): +1 Attack for a
Superior weapon, +1 Defence for a Superior shield, an Excellent weapon's
bonus to both. A crossbow's Damage doesn't add Strength (Lords of Men p.
138). A weapon's minimum Strength is shown where the wielder's is lower
(DE p. 400 sets no penalty).

Mounted on a trained warhorse, a rider adds his Ride, at most +3, to
Attack and Defence, missile weapons included as the DE has it (Lords of
Men limits the Attack bonus to melee); a mounted charge adds his Combat
Ability to the Attack again, and the horse, not the rider, spends a
Fatigue level (Lords of Men).

No screen uses damage_dealt() yet: it is a rule for a screen still to come,
and only the tests call it.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .. import catalog
from ..models import Character, Possession
from . import effects, equipment
from .breakdown import Breakdown, Line
from .derived import (
    carried_load,
    encumbrance,
    fatigue_penalty,
    primitive_armour,
    worn_armour,
    wound_penalty,
)
from .lab import ability_score
from .scores import character_source

SOURCE = "Ars Magica Definitive Edition, Chapter 11: Obstacles, Combat, pp. 393-395"
CROSSBOW = "Crossbow"
LONG_SPEAR = "weapon_long_spear"


SPECIALTY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Five: Abilities, Specialties, p. 157"
)
VIRTUES_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, pp. 59-154"
)
MOUNTED_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Mounted Combat, p. 397; "
    "Lords of Men, Chapter Nine: Optional Combat Rules, Mounted Combat, pp. 126-128"
)
#: The most Ride adds to a mounted character's Attack and Defence.
MOUNTED_MAX = 3
#: A lance is wielded only from horseback; on foot it is a long spear.
LANCE = "weapon_lance"
PRIMITIVE = "vf_primitive_equipment"
INEXPENSIVE = "Inexpensive"


@dataclass
class CombatTotals:
    ability: str | None
    initiative: Breakdown
    attack: Breakdown | None
    defence: Breakdown
    damage: Breakdown | None
    #: The shield fought with, if any.
    shield: Possession | None = None
    #: Defence against missiles: the weapon's own modifiers don't count, a
    #: carried shield's do (DE p. 395).
    missile_defence: Breakdown | None = None


def carried_shield(character: Character) -> Possession | None:
    """The best shield the character carries (by its Defence)."""
    shields = [
        item
        for item in character.inventory
        if equipment.is_shield(item) and item.carried
    ]
    return max(
        shields,
        key=lambda s: s.weapon_defense + equipment.quality_bonus(s),
        default=None,
    )


#: The Combat Abilities whose weapons need both hands: a great weapon is
#: two-handed and a bow needs two free hands (DE pp. 400-401). Any other
#: weapon may be fought with a shield (DE p. 393).
TWO_HANDED = ("Great Weapon", "Bows")


def takes_shield(weapon: Possession) -> bool:
    """Whether the weapon leaves the other hand free for a shield: one not
    of a two-handed Ability, and not a shield itself."""
    return weapon_ability(weapon) not in TWO_HANDED and not equipment.is_shield(weapon)


def minimum_strength(weapon: Possession) -> int | None:
    """The weapon's minimum Strength (None: no minimum or not in the
    catalog)."""
    definition = catalog.load_weapon_catalog_by_id().get(weapon.gear_id or "")
    return definition.strength if definition is not None else None


def _on_foot(weapon: Possession) -> Possession:
    """A lance on foot is a long spear (DE pp. 400-401)."""
    if weapon.gear_id != LANCE:
        return weapon
    spear = catalog.load_weapon_catalog_by_id().get(LONG_SPEAR)
    if spear is None:
        return weapon
    return replace(
        weapon,
        gear_id=LONG_SPEAR,
        weapon_init=spear.init or 0,
        weapon_attack=spear.attack,
        weapon_defense=spear.defense or 0,
        weapon_damage=spear.damage,
    )


def weapon_ability(weapon: Possession) -> str | None:
    """The Combat Ability the weapon's catalog entry names (None when it was
    typed in)."""
    if weapon.gear_id is None:
        return None
    definition = catalog.load_weapon_catalog_by_id().get(weapon.gear_id)
    return definition.ability if definition else None


def _table(weapon: Possession) -> str:
    """The weapon's table ("melee", "missile", "natural"; "melee" when
    typed in)."""
    definition = catalog.load_weapon_catalog_by_id().get(weapon.gear_id or "")
    return definition.table if definition else "melee"


def _names(weapon: Possession) -> set[str]:
    """What a target may call the weapon: its tables and its names."""
    table = _table(weapon)
    found = {table, weapon.name}
    if table == "natural":
        found.add("melee")
    definition = catalog.load_weapon_catalog_by_id().get(weapon.gear_id or "")
    if definition is not None:
        found.add(definition.name)
    return {name.strip().casefold() for name in found if name}


def _plain(name: str) -> str:
    return "".join(ch for ch in name.casefold() if ch.isalnum()).removesuffix("s")


def specialty_applies(
    character: Character, ability: str | None, weapon: Possession
) -> bool:
    """Whether the Combat Ability's specialty names the weapon."""
    found = next((a for a in character.abilities if a.name == ability), None)
    if found is None or not found.specialty:
        return False
    names = {
        _plain(name)
        for name in _names(weapon)
        if name not in ("melee", "missile", "natural")
    }
    return _plain(found.specialty) in names


def _cost(weapon: Possession) -> str:
    """The weapon's cost: its catalog entry's (none counts as Inexpensive),
    else the quality typed for it."""
    definition = catalog.load_weapon_catalog_by_id().get(weapon.gear_id or "")
    if definition is not None:
        return definition.cost or INEXPENSIVE  # a fist or a claw costs nothing
    return weapon.gear_quality


def virtue_lines(character: Character, weapon: Possession, kind: str) -> list[Line]:
    """The lines the character's Virtues and Flaws add to one combat total
    (`kind`: initiative, attack, defense or damage) with `weapon`."""
    names = _names(weapon)
    lines: list[Line] = []
    found = effects.collect(
        [character_source(character.virtues_flaws)], f"combat_{kind}"
    )
    for effect in found:
        if effect.target is not None and effect.target.strip().casefold() not in names:
            continue
        lines.append(
            Line(effect.entry.name, amount=effect.amount or 0, source=VIRTUES_SOURCE)
        )
    if not any(vf.vf_id == PRIMITIVE for vf in character.virtues_flaws):
        return lines
    if kind in ("attack", "defense") and _cost(weapon) != INEXPENSIVE:
        lines.append(
            Line("Primitive Equipment (weapon)", amount=-1, source=VIRTUES_SOURCE)
        )
    armour = worn_armour(character.inventory)
    if (
        kind == "initiative"
        and armour is not None
        and primitive_armour(character, armour)
    ):
        lines.append(
            Line("Primitive Equipment (armour)", amount=-1, source=VIRTUES_SOURCE)
        )
    return lines


def _total(lines: list[Line]) -> Breakdown:
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def combat_totals(
    character: Character,
    weapon: Possession,
    *,
    mounted_: bool = False,
    shield: Possession | None | bool = True,
) -> CombatTotals:
    """The totals with `weapon`, and the shield carried with it (`shield`:
    True for the best one carried, None or False for none, or the shield
    itself). On foot a lance counts as a long spear."""
    if not mounted_:
        weapon = _on_foot(weapon)
    if shield is True:
        shield = carried_shield(character) if takes_shield(weapon) else None
    off: Possession | None = shield if isinstance(shield, Possession) else None
    c = character.characteristics
    ability = weapon_ability(weapon)
    skill = sum(ability_score(character, ability)) if ability else 0
    penalty = wound_penalty(
        character.wounds, character.virtues_flaws
    ) + fatigue_penalty(character.fatigue_level, character.virtues_flaws)
    penalties = (
        [Line("Wounds and fatigue", amount=penalty, source=SOURCE)] if penalty else []
    )
    enc = encumbrance(carried_load(character.inventory), c.strength)
    skill_lines = [Line(ability, amount=skill, source=SOURCE)] if ability else []
    if ability and specialty_applies(character, ability, weapon):
        skill_lines.append(
            Line(f"{ability} specialty", amount=1, source=SPECIALTY_SOURCE)
        )

    made = equipment.quality_bonus(weapon)
    made_lines = (
        [Line(f"{weapon.make} weapon", amount=made, source=equipment.QUALITY_SOURCE)]
        if made
        else []
    )
    shield_lines = _shield_lines(off)
    initiative = _total(
        [
            Line("Quickness", amount=c.quickness, source=SOURCE),
            Line("Weapon Init", amount=weapon.weapon_init, source=SOURCE),
            *shield_lines.get("init", []),
            *([Line("Encumbrance", amount=-enc, source=SOURCE)] if enc else []),
            *virtue_lines(character, weapon, "initiative"),
            *penalties,
        ]
    )
    attack = (
        None
        if weapon.weapon_attack is None
        else _total(
            [
                Line("Dexterity", amount=c.dexterity, source=SOURCE),
                *skill_lines,
                Line("Weapon Atk", amount=weapon.weapon_attack, source=SOURCE),
                *made_lines,
                *shield_lines.get("attack", []),
                *virtue_lines(character, weapon, "attack"),
                *penalties,
            ]
        )
    )
    defence = _total(
        [
            Line("Quickness", amount=c.quickness, source=SOURCE),
            *skill_lines,
            Line("Weapon Dfn", amount=weapon.weapon_defense, source=SOURCE),
            # An Excellent weapon's bonus is to Defence too; a Superior one's
            # to Attack only.
            *(made_lines if weapon.make == equipment.EXCELLENT else []),
            *shield_lines.get("defense", []),
            *virtue_lines(character, weapon, "defense"),
            *penalties,
        ]
    )
    # A crossbow's Damage is its own: no Strength (Lords of Men p. 138).
    strength = (
        []
        if weapon_ability(weapon) == CROSSBOW
        else [Line("Strength", amount=c.strength, source=SOURCE)]
    )
    damage = (
        None
        if weapon.weapon_damage is None
        else _total(
            [
                *strength,
                Line("Weapon Dam", amount=weapon.weapon_damage, source=SOURCE),
                *shield_lines.get("damage", []),
                *virtue_lines(character, weapon, "damage"),
            ]
        )
    )
    carried = carried_shield(character)
    against_missiles = _total(
        [
            Line("Quickness", amount=c.quickness, source=SOURCE),
            *skill_lines,
            *_shield_lines(carried).get("defense", []),
            *virtue_lines(character, weapon, "defense"),
            *penalties,
        ]
    )
    return CombatTotals(
        ability, initiative, attack, defence, damage, off, against_missiles
    )


def _shield_lines(shield: Possession | None) -> dict[str, list[Line]]:
    """A shield's modifiers, to add to the weapon's (n/a counts as 0)."""
    if shield is None:
        return {}
    found: dict[str, list[Line]] = {}
    for key, value in (
        ("init", shield.weapon_init),
        ("attack", shield.weapon_attack),
        ("defense", shield.weapon_defense),
        ("damage", shield.weapon_damage),
    ):
        if value:
            found[key] = [Line(f"{shield.name} ({key})", amount=value, source=SOURCE)]
    made = equipment.quality_bonus(shield)
    if made:
        found.setdefault("defense", []).append(
            Line(f"{shield.make} shield", amount=made, source=equipment.QUALITY_SOURCE)
        )
    return found


def missile_defence(character: Character, weapon: Possession) -> Breakdown:
    """Defence against missiles: Quickness + the Combat Ability + the
    carried shield's Defence only (DE p. 395)."""
    totals = combat_totals(character, weapon)
    assert totals.missile_defence is not None
    return totals.missile_defence


@dataclass(frozen=True)
class Mounted:
    """A rider's totals on a trained warhorse: Ride (at most +3) added to
    Attack and Defence; charging adds the Combat Ability to Attack again
    (melee only), and the horse spends the Fatigue level."""

    ride: int
    attack: int | None
    defence: int
    charge: int | None


def mounted(character: Character, weapon: Possession) -> Mounted | None:
    """The weapon's totals on horseback (None for a character without
    Ride)."""
    ride = min(sum(ability_score(character, "Ride")), MOUNTED_MAX)
    if ride <= 0:
        return None
    totals = combat_totals(character, weapon, mounted_=True)
    # The Attack bonus is for melee only; a missile user gains the Defence
    # bonus alone (Lords of Men pp. 126-127, expanding DE p. 397).
    melee = _table(weapon) != "missile"
    attack = (
        None
        if totals.attack is None
        else int(totals.attack.total) + (ride if melee else 0)
    )
    ability = totals.ability
    charge = None
    if attack is not None and melee and ability:
        charge = attack + sum(ability_score(character, ability))
    return Mounted(ride, attack, int(totals.defence.total) + ride, charge)


def counted_text(totals: CombatTotals) -> str:
    """The specialty and the Virtues and Flaws in the totals, each with
    what it adds to which ("Poor Eyesight -3 Atk, -3 Dfn"); "" for none."""
    parts: dict[str, dict[str, float]] = {}
    for short, breakdown in (
        ("Init", totals.initiative),
        ("Atk", totals.attack),
        ("Dfn", totals.defence),
        ("Dam", totals.damage),
    ):
        for line in breakdown.lines if breakdown is not None else []:
            if line.source in (VIRTUES_SOURCE, SPECIALTY_SOURCE):
                found = parts.setdefault(line.label, {})
                found[short] = found.get(short, 0) + (line.amount or 0)
    return "; ".join(
        label + " " + ", ".join(f"{n:+g} {short}" for short, n in found.items())
        for label, found in parts.items()
    )


def hits(attack_total: int, defence_total: int) -> bool:
    """A hit needs the Attack Total to beat the Defence Total."""
    return attack_total > defence_total


def damage_dealt(damage_total: int, attack_total: int, defence_total: int) -> int:
    """The Damage Total of a hit: Damage plus the Attack Advantage."""
    return damage_total + (attack_total - defence_total)
