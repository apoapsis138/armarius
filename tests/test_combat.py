"""Combat totals (STORY-811)."""

from ars_magica_manager import sheet_text
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Possession,
    Wounds,
)
from ars_magica_manager.rules import combat
from ars_magica_manager.rules.xp import ability_xp


def _fighter(*inventory: Possession, **kw) -> Character:
    return Character(
        id="g",
        name="Grog",
        type="grog",
        characteristics=Characteristics(quickness=1, dexterity=2, strength=3),
        abilities=[Ability("Brawl", xp=ability_xp(4))],
        inventory=list(inventory),
        **kw,
    )


BLUDGEON = Possession(
    id="w",
    kind="weapon",
    name="Club",
    gear_id="weapon_bludgeon",
    weapon_init=0,
    weapon_attack=2,
    weapon_defense=0,
    weapon_damage=2,
    load=1,
)


def test_combat_totals_from_the_weapon_and_its_ability():
    totals = combat.combat_totals(_fighter(BLUDGEON), BLUDGEON)
    assert totals.ability == "Brawl"
    assert totals.initiative.total == 1 + 0
    assert totals.attack is not None and totals.attack.total == 2 + 4 + 2
    assert totals.defence.total == 1 + 4 + 0
    assert totals.damage is not None and totals.damage.total == 3 + 2


def test_encumbrance_hits_initiative_and_wounds_hit_everything():
    armour = Possession(id="a", kind="armor", name="Chain", load=9)  # Load 10: Burden 4
    fighter = _fighter(BLUDGEON, armour, wounds=Wounds(light=1), fatigue_level="weary")
    totals = combat.combat_totals(fighter, BLUDGEON)
    # Encumbrance 4 - Str 3 = 1; penalties -1 wound -1 fatigue
    assert totals.initiative.total == 1 - 1 - 2
    assert totals.attack is not None and totals.attack.total == 8 - 2


def test_a_hand_typed_weapon_has_no_ability_and_na_figures_stay_na():
    dodge = Possession(
        id="d", kind="weapon", name="Dodge", weapon_attack=None, weapon_damage=None
    )
    totals = combat.combat_totals(_fighter(dodge), dodge)
    assert totals.ability is None and totals.attack is None and totals.damage is None
    assert "no Combat Ability" in sheet_text.combat_text(_fighter(dodge), dodge)


def test_hits_and_damage():
    assert combat.hits(12, 11) and not combat.hits(11, 11)
    assert combat.damage_dealt(5, 12, 9) == 8
