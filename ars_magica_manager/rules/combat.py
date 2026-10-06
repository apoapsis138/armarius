"""Combat totals, before the stress die:

    Initiative = Quickness + weapon Init - Encumbrance
    Attack     = Dexterity + Combat Ability + weapon Atk
    Defence    = Quickness + Combat Ability + weapon Dfn
    Damage     = Strength + weapon Dam (+ the Attack Advantage when it hits)

Wound and Fatigue penalties apply to every roll. Encumbrance doesn't reduce
Attack or Defence when it comes mostly from weapons and armour, so it only
comes off Initiative here. The Combat Ability is the one the weapon's
catalog entry names; a weapon typed in by hand has none.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog
from ..models import Character, Possession
from .breakdown import Breakdown, Line
from .derived import carried_load, encumbrance, fatigue_penalty, wound_penalty
from .lab import ability_score

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Combat Scores "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eleven:"
    "_Obstacles#Combat_Scores)"
)


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


def _total(lines: list[Line]) -> Breakdown:
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def combat_totals(character: Character, weapon: Possession) -> CombatTotals:
    c = character.characteristics
    ability = weapon_ability(weapon)
    skill = sum(ability_score(character, ability)) if ability else 0
    penalty = wound_penalty(character.wounds) + fatigue_penalty(character.fatigue_level)
    penalties = (
        [Line("Wounds and fatigue", amount=penalty, source=SOURCE)] if penalty else []
    )
    enc = encumbrance(carried_load(character.inventory), c.strength)
    skill_lines = [Line(ability, amount=skill, source=SOURCE)] if ability else []

    initiative = _total(
        [
            Line("Quickness", amount=c.quickness, source=SOURCE),
            Line("Weapon Init", amount=weapon.weapon_init, source=SOURCE),
            *([Line("Encumbrance", amount=-enc, source=SOURCE)] if enc else []),
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
                *penalties,
            ]
        )
    )
    defence = _total(
        [
            Line("Quickness", amount=c.quickness, source=SOURCE),
            *skill_lines,
            Line("Weapon Dfn", amount=weapon.weapon_defense, source=SOURCE),
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
            ]
        )
    )
    return CombatTotals(ability, initiative, attack, defence, damage)


def hits(attack_total: int, defence_total: int) -> bool:
    """A hit needs the Attack Total to beat the Defence Total."""
    return attack_total > defence_total


def damage_dealt(damage_total: int, attack_total: int, defence_total: int) -> int:
    """The Damage Total of a hit: Damage plus the Attack Advantage."""
    return damage_total + (attack_total - defence_total)
