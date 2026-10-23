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

Mounted on a trained warhorse, a rider adds his Ride, at most +3, to
Attack and Defence (the DE); a mounted charge adds his Combat Ability to
the Attack again, and the horse, not the rider, spends a Fatigue level
(Lords of Men).
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog
from ..models import Character, Possession
from . import effects
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

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Combat Scores "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eleven:"
    "_Obstacles#Combat_Scores)"
)


SPECIALTY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Five: Abilities, Specialties "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Five:"
    "_Abilities)"
)
VIRTUES_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Four:"
    "_Virtues_and_Flaws)"
)
MOUNTED_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Mounted Combat "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eleven:"
    "_Obstacles); Lords of Men, Chapter Nine: Mounted Combat"
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


def combat_totals(character: Character, weapon: Possession) -> CombatTotals:
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

    initiative = _total(
        [
            Line("Quickness", amount=c.quickness, source=SOURCE),
            Line("Weapon Init", amount=weapon.weapon_init, source=SOURCE),
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
            *virtue_lines(character, weapon, "defense"),
            *penalties,
        ]
    )
    damage = (
        None
        if weapon.weapon_damage is None
        else _total(
            [
                Line("Strength", amount=c.strength, source=SOURCE),
                Line("Weapon Dam", amount=weapon.weapon_damage, source=SOURCE),
                *virtue_lines(character, weapon, "damage"),
            ]
        )
    )
    return CombatTotals(ability, initiative, attack, defence, damage)


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
    totals = combat_totals(character, weapon)
    attack = None if totals.attack is None else int(totals.attack.total) + ride
    ability = totals.ability
    charge = None
    if attack is not None and _table(weapon) != "missile" and ability:
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
