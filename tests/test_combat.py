"""Combat totals."""

from ars_magica_manager import sheet_text
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Possession,
    VirtueFlawInstance,
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


def _weapon(gear_id: str, name: str, **kw) -> Possession:
    return Possession(id=gear_id, kind="weapon", name=name, gear_id=gear_id, **kw)


def test_a_specialty_naming_the_weapon_adds_one_to_attack_and_defence():
    fighter = _fighter(BLUDGEON)
    fighter.abilities = [Ability("Brawl", xp=ability_xp(4), specialty="dagger")]
    totals = combat.combat_totals(fighter, BLUDGEON)
    assert (totals.attack.total, totals.defence.total) == (8, 5)
    # The weapon's own name or its catalog entry's, either number.
    fighter.abilities[0].specialty = "Clubs"
    totals = combat.combat_totals(fighter, BLUDGEON)
    assert (totals.attack.total, totals.defence.total) == (9, 6)
    assert totals.initiative.total == 1  # a specialty isn't on Initiative
    assert combat.counted_text(totals) == "Brawl specialty +1 Atk, +1 Dfn"
    fighter.abilities[0].specialty = "bludgeon"
    assert combat.combat_totals(fighter, BLUDGEON).attack.total == 9


def test_flaws_that_hamper_combat():
    fighter = _fighter(BLUDGEON)
    fighter.virtues_flaws = [VirtueFlawInstance("vf_lame")]
    totals = combat.combat_totals(fighter, BLUDGEON)
    assert (totals.initiative.total, totals.attack.total, totals.defence.total) == (
        0,
        7,
        4,
    )
    dodge = _weapon("weapon_dodge", "Dodge", weapon_attack=None, weapon_damage=None)
    assert combat.combat_totals(fighter, dodge).defence.total == 1 + 4 - 3
    fighter.virtues_flaws = [VirtueFlawInstance("vf_missing_eye")]
    assert combat.combat_totals(fighter, BLUDGEON).attack.total == 8 - 1
    sling = _weapon("weapon_sling", "Sling", weapon_attack=1)
    assert combat.combat_totals(fighter, sling).attack.total == 2 + 1 - 3
    fighter.virtues_flaws = [
        VirtueFlawInstance("vf_poor_eyesight"),
        VirtueFlawInstance("vf_slow_reflexes"),
    ]
    totals = combat.combat_totals(fighter, BLUDGEON)
    assert (totals.initiative.total, totals.attack.total, totals.defence.total) == (
        1 - 3,
        8 - 3,
        5 - 3,
    )


def test_primitive_equipment_counts_only_what_isn_t_inexpensive():
    sword = _weapon("weapon_long_sword", "Sword", weapon_attack=4, weapon_defense=1)
    mail = Possession(
        id="a",
        kind="armor",
        name="Mail",
        gear_id="armor_chain_mail",
        armor_protection=4,
    )
    fighter = _fighter(BLUDGEON, sword, mail)
    fighter.virtues_flaws = [VirtueFlawInstance("vf_primitive_equipment")]
    club = combat.combat_totals(fighter, BLUDGEON)
    assert (club.attack.total, club.defence.total) == (8, 5)  # Inexpensive
    blade = combat.combat_totals(fighter, sword)
    assert any(
        line.label == "Primitive Equipment (weapon)" for line in blade.attack.lines
    )
    assert any(
        line.label == "Primitive Equipment (armour)" for line in club.initiative.lines
    )


def test_a_natural_weapon_s_qualities_count_for_that_weapon_only():
    claws = _weapon("natural_claw", "Claw", weapon_attack=2, weapon_damage=1)
    teeth = _weapon("natural_teeth", "Teeth", weapon_attack=1, weapon_damage=1)
    beast = _fighter(claws, teeth)
    beast.virtues_flaws = [
        VirtueFlawInstance("vf_improved_attack", params={"weapon": "claw"}),
        VirtueFlawInstance(
            "vf_improved_damage", params={"weapon": "claw", "bonus": "4"}
        ),
    ]
    clawing = combat.combat_totals(beast, claws)
    assert (clawing.attack.total, clawing.damage.total) == (2 + 4 + 2 + 2, 3 + 1 + 4)
    biting = combat.combat_totals(beast, teeth)
    assert (biting.attack.total, biting.damage.total) == (2 + 4 + 1, 3 + 1)
    text = sheet_text.combat_text(beast, claws)
    assert "Counted: Improved Attack +2 Atk; Improved Damage +4 Dam." in text


def test_mounted_totals_add_ride_up_to_three_and_a_charge():
    fighter = _fighter(BLUDGEON)
    assert combat.mounted(fighter, BLUDGEON) is None  # no Ride
    fighter.abilities.append(Ability("Ride", xp=ability_xp(5)))
    riding = combat.mounted(fighter, BLUDGEON)
    assert riding == combat.Mounted(ride=3, attack=8 + 3, defence=5 + 3, charge=11 + 4)
    sling = _weapon("weapon_sling", "Sling", weapon_attack=1)
    assert combat.mounted(fighter, sling).charge is None  # no missile charge
    text = sheet_text.combat_text(fighter, BLUDGEON)
    assert "Mounted (Ride +3): Attack +11   Defence +8; charging, Attack +15" in text
