"""A fighter's loadout and equipment, combat groups, Lords of Men's
combat options and siegecraft, and taming (DE pp. 384-386, 393-401;
Lords of Men pp. 109-142; Grogs pp. 47-48)."""

from ars_magica_manager import sheet_text
from ars_magica_manager.models import (
    Ability,
    AnimalForm,
    Character,
    Characteristics,
    Possession,
    Progress,
    ScoredTrait,
)
from ars_magica_manager.rules import (
    combat,
    combat_groups,
    combat_options,
    derived,
    equipment,
    siege,
    supplement_work,
    travel,
)
from ars_magica_manager.rules.xp import ability_xp


def _weapon(gear_id: str, name: str, **kw) -> Possession:
    return Possession(id=gear_id, kind="weapon", name=name, gear_id=gear_id, **kw)


SWORD = _weapon(
    "weapon_short_sword",
    "Short Sword",
    weapon_init=1,
    weapon_attack=3,
    weapon_defense=1,
    weapon_damage=5,
    load=1,
)
SHIELD = _weapon(
    "weapon_round_shield",
    "Round Shield",
    weapon_init=0,
    weapon_attack=None,
    weapon_defense=2,
    weapon_damage=None,
    load=2,
)


def _fighter(*inventory: Possession, **kw) -> Character:
    return Character(
        id="g",
        name="Grog",
        type="grog",
        characteristics=Characteristics(quickness=1, dexterity=2, strength=3),
        abilities=[
            Ability("Single Weapon", xp=ability_xp(5)),
            Ability("Leadership", xp=ability_xp(3)),
        ],
        inventory=list(inventory),
        **kw,
    )


def test_a_weapon_and_a_carried_shield_add_together():
    # DE p. 393: a short sword and round shield, Init +1, Atk +3, Dfn +3.
    fighter = _fighter(SWORD, SHIELD)
    totals = combat.combat_totals(fighter, SWORD)
    assert totals.shield is SHIELD
    assert totals.defence.total == 1 + 5 + 1 + 2
    assert totals.attack is not None and totals.attack.total == 2 + 5 + 3
    # Against missiles only the shield counts (DE p. 395).
    assert totals.missile_defence is not None
    assert totals.missile_defence.total == 1 + 5 + 2
    text = sheet_text.combat_text(fighter, SWORD)
    assert "(with Round Shield)" in text and "Defence against missiles +8" in text
    # Left at home, the shield is neither fought with nor carried.
    SHIELD_AT_HOME = _weapon("weapon_round_shield", "Round Shield", weapon_defense=2)
    SHIELD_AT_HOME.carried = False
    assert combat.combat_totals(_fighter(SWORD, SHIELD_AT_HOME), SWORD).shield is None


def test_a_lance_on_foot_is_a_long_spear():
    lance = _weapon(
        "weapon_lance", "Lance", weapon_init=2, weapon_attack=4, weapon_damage=5
    )
    fighter = _fighter(lance)
    fighter.abilities.append(Ability("Great Weapon", xp=ability_xp(2)))
    totals = combat.combat_totals(fighter, lance)
    assert totals.ability == "Great Weapon"


def test_how_well_a_weapon_is_made():
    superior = _weapon("weapon_short_sword", "Fine Sword", weapon_attack=3)
    superior.make = equipment.SUPERIOR
    plain = combat.combat_totals(_fighter(SWORD), SWORD)
    fine = combat.combat_totals(_fighter(superior), superior)
    assert fine.attack is not None and plain.attack is not None
    assert fine.attack.total == plain.attack.total + 1
    excellent = _weapon(
        "weapon_short_sword", "Great Sword", weapon_attack=3, weapon_defense=1
    )
    excellent.make, excellent.make_bonus = equipment.EXCELLENT, 3
    best = combat.combat_totals(_fighter(excellent), excellent)
    assert best.defence.total == plain.defence.total + 3


def test_damaged_goods():
    # Lords of Men pp. 137-138's damage levels, moved by make as City &
    # Guild p. 77's base levels move.
    fine = _weapon("weapon_short_sword", "Fine Sword")
    fine.make = equipment.SUPERIOR
    spear = _weapon("weapon_short_spear", "Spear")
    club = _weapon("weapon_club", "Club")
    club.make = equipment.EXCELLENT
    levels = [equipment.damage_levels(w) for w in (SWORD, fine, spear, club)]
    assert levels == [2, 3, 1, 3]
    assert equipment.stress_check_bonus(fine, 5) == 6
    text = sheet_text.combat_text(_fighter(SWORD), SWORD)
    assert (
        "2 damage level(s), damage P, S" in text and "stress die +5 against 15" in text
    )


def test_travel_speeds():
    # Grogs pp. 51-52: 15 + 2 x Athletics on foot, 30 + 2 x Ride riding.
    walker = _fighter()
    walker.abilities.append(Ability("Athletics", xp=ability_xp(3)))
    assert travel.forced_march(walker) == 21
    assert travel.forced_ride(walker) == travel.UNSKILLED_RIDER
    rider = _fighter()
    rider.abilities.append(Ability("Ride", xp=ability_xp(4)))
    assert (travel.forced_ride(rider), travel.forced_ride(rider, 2)) == (38, 54)


def test_load_counts_the_armour_worn_and_the_weapons_carried():
    mail = Possession(id="m", kind="armor", name="Mail", armor_protection=7, load=6)
    leather = Possession(
        id="l", kind="armor", name="Leather", armor_protection=2, load=3
    )
    spare = _weapon("weapon_short_sword", "Spare", load=1)
    spare.carried = False
    assert derived.carried_load([mail, leather, SWORD, spare]) == 6 + 1


def test_carrying_and_moving():
    fighter = _fighter()  # Strength +3: carries Burden 8 (Load 36)
    assert equipment.carrying(fighter) == (36, 55, 120)
    assert derived.walking_pace(fighter) == 11


def test_a_trained_group_adds_its_members_abilities():
    members = [combat_groups.Member(_fighter(SWORD), SWORD) for _ in range(3)]
    group = combat_groups.CombatGroup(members, vanguard=0, leader=0, trained=True)
    assert combat_groups.problems(group) == []
    # The other two members' Single Weapon 5 each, at most 3 x Leadership 3.
    assert group.bonus() == 9
    assert combat_groups.blows(4, 3) == [2, 1, 1]
    assert combat_groups.scuffle("heavy") == (2, "light")


def test_lords_of_men_options():
    fighter = _fighter(SWORD)
    assert combat_options.action_priority(fighter, "Single Weapon") == 1 + 5
    assert combat_options.mounted_paces("Gallop", 0) == 50
    assert combat_options.rally_ease("Engaged in melee", 2, 3) == 12
    loyal = _fighter()
    loyal.personality_traits = [ScoredTrait("Loyal", 2)]
    assert combat_options.trait_bonus([loyal, loyal], "Loyal") == 2
    assert combat_options.trait_bonus([loyal, _fighter()], "Loyal") == 0


def test_a_siege():
    castle = siege.Castle(
        groups=15, defenses="Superior", supplies="Standard", moat=True
    )
    assert castle.interval() == "Week"
    assert castle.defense_bonus() == 3 and castle.defense_bonus(against_mines=True) == 4
    assert castle.supplies_ease(years=1) == 3 + 2 + 1
    assert siege.wall_damage_levels(4, 10) == 16
    assert siege.worse("Shoddy") is None


def test_taming_points_last_only_over_consecutive_seasons():
    record = Progress("taming", "Wolf", 10, points=6)
    record.last_season, record.last_year = "Spring", 1220
    assert supplement_work.kept_points(record, "Summer", 1220) == 6
    assert supplement_work.kept_points(record, "Autumn", 1220) == 0
    # Older records with no season kept are taken as unbroken.
    assert (
        supplement_work.kept_points(Progress("taming", "Hawk", 5, 3), "Winter", 1220)
        == 3
    )
    assert supplement_work.beast_might(2) == 5


def test_any_one_handed_weapon_takes_a_shield():
    # DE p. 393; a great weapon and a bow need both hands.
    dagger = _weapon("weapon_dagger", "Dagger")
    bow = _weapon("weapon_long_bow", "Long Bow")
    assert combat.takes_shield(dagger) and not combat.takes_shield(bow)


def test_the_mounted_attack_bonus_is_for_melee_only():
    # Lords of Men pp. 126-127: a missile user gains the Defence bonus alone.
    bow = _weapon("weapon_long_bow", "Long Bow", weapon_attack=4)
    archer = _fighter(bow)
    archer.abilities.append(Ability("Ride", xp=ability_xp(3)))
    archer.abilities.append(Ability("Bows", xp=ability_xp(4)))
    riding = combat.mounted(archer, bow)
    afoot = combat.combat_totals(archer, bow)
    assert riding is not None and afoot.attack is not None
    assert riding.attack == int(afoot.attack.total)
    assert riding.charge is None


def test_only_four_footed_beasts_carry_half_again():
    # Grogs p. 48.
    hawk = _fighter(animal=AnimalForm(kind="bird"))
    hound = _fighter(animal=AnimalForm(kind="clawed"))
    assert equipment.effective_strength(hawk) == 3
    assert equipment.effective_strength(hound) == 4
