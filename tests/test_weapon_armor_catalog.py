"""The Weapons & Armor catalog: the Definitive Edition's
Armor, Melee and Missile tables (Chapter 11) and Natural Weapons table
(Chapter 13), row for row, plus the supplements' weapons, each flagged
with its book and offered only with that book in play."""

import pytest

from ars_magica_manager import catalog
from ars_magica_manager import possessions as pos
from ars_magica_manager.forms.possession import possession_fields
from ars_magica_manager.models import (
    GEAR_QUALITIES,
    WEAPON_TABLES,
    Possession,
    WeaponDef,
)

#: The supplements' weapons, after the DE's rows of their table: id -> book.
SUPPLEMENT_WEAPONS = {"weapon_greek_fire_siphon": "TSE"}


def _table(table: str) -> list[WeaponDef]:
    return catalog.load_weapon_catalog(tables=(table,))


def test_every_row_of_the_books_tables_is_there_in_its_order():
    assert [w.name for w in _table("melee")] == [
        "Dodge",
        "Fist",
        "Kick",
        "Gauntlet",
        "Bludgeon",
        "Dagger",
        "Knife",
        "Axe",
        "Club",
        "Hatchet",
        "Lance",
        "Mace",
        "Mace and Chain",
        "Short Spear",
        "Short Sword",
        "Long Sword",
        "Buckler",
        "Round Shield",
        "Heater Shield",
        "Cudgel",
        "Farm Implement",
        "Flail",
        "Pole Arm",
        "Pole Axe",
        "Long Spear",
        "Great Sword",
        "Staff",
        "Warhammer",
    ]
    assert [w.name for w in _table("missile")] == [
        "Throwing Axe",
        "Javelin",
        "Knife",
        "Sling",
        "Stone",
        "Long Bow",
        "Short Bow",
        "Greek Fire Siphon",  # The Sundered Eagle p. 47
    ]
    assert [w.name for w in _table("natural")] == [
        "Grapple",
        "Dodge",
        "Teeth",
        "Large Teeth",
        "Tusks",
        "Claw",
        "Large Claws",
        "Horns",
        "Large Horns/Antlers",
        "Hooves",
    ]
    assert [a.name for a in catalog.load_armor_catalog()] == [
        "Quilted/Fur",
        "Heavy Leather",
        "Metal Reinforced Leather",
        "Leather Scale",
        "Metal Scale",
        "Chain Mail",
    ]
    assert len(catalog.load_weapon_catalog()) == 45 + len(SUPPLEMENT_WEAPONS)


# (id, Init, Atk, Dfn, Dam, Str, Load, Cost, Range) as the DE prints them.
@pytest.mark.parametrize(
    "row",
    [
        ("weapon_dodge", 0, None, 0, None, None, 0, None, None),
        ("weapon_kick", -1, 0, -1, 3, None, 0, None, None),
        ("weapon_knife", 0, 1, 0, 2, -6, 0, "Inexpensive", None),
        ("weapon_long_sword", 2, 4, 1, 6, 0, 1, "Expensive", None),
        ("weapon_buckler", 0, 0, 1, 0, -2, 1, "Standard", None),
        ("weapon_round_shield", 0, 0, 2, 0, -1, 2, "Inexpensive", None),
        ("weapon_pole_axe", 1, 5, 0, 11, 1, 2, "Standard", None),
        ("weapon_long_spear", 3, 3, 1, 7, 0, 3, "Inexpensive", None),
        ("weapon_warhammer", 0, 6, 0, 12, 2, 3, "Standard", None),
        ("weapon_sling", -3, 1, 0, 4, -3, 0, "Inexpensive", 20),
        ("weapon_throwing_knife", 0, 1, 0, 2, -2, 0, "Inexpensive", 5),
        ("weapon_long_bow", -2, 4, 0, 8, 2, 2, "Expensive", 30),
        # The Sundered Eagle p. 47.
        ("weapon_greek_fire_siphon", -2, 4, 0, 10, 2, 3, "Expensive", 5),
        ("natural_grapple", 0, 0, 0, None, None, None, None, None),
        ("natural_claw", -1, 2, 3, 2, None, None, None, None),
        ("natural_large_horns", 2, 3, 2, 3, None, None, None, None),
    ],
    ids=lambda row: row[0],
)
def test_weapon_figures_match_the_book(row):
    weapon = catalog.load_weapon_catalog_by_id()[row[0]]
    assert (
        weapon.id,
        weapon.init,
        weapon.attack,
        weapon.defense,
        weapon.damage,
        weapon.strength,
        weapon.load,
        weapon.cost,
        weapon.range,
    ) == row


def test_armor_figures_match_the_book():
    rows = {
        a.id: (a.figures(False), a.figures(True), a.cost)
        for a in catalog.load_armor_catalog()
    }
    assert rows == {
        "armor_quilted_fur": ((1, 2), None, "Inexpensive"),
        "armor_heavy_leather": ((2, 3), None, "Inexpensive"),
        "armor_metal_reinforced_leather": ((2, 2), (4, 4), "Standard"),
        "armor_leather_scale": ((3, 3), (5, 5), "Standard"),
        "armor_metal_scale": ((4, 4), (7, 7), "Standard"),
        "armor_chain_mail": ((6, 4), (9, 6), "Expensive"),
    }


def test_weapons_use_the_books_abilities_and_costs():
    abilities = {a.name for a in catalog.load_ability_catalog()}
    # A parameterized Ability ("Profession: {profession}") by its prefix.
    prefixes = tuple(name.split("{")[0] for name in abilities if "{" in name)
    for weapon in catalog.load_weapon_catalog():
        assert weapon.table in WEAPON_TABLES
        assert weapon.ability in abilities or weapon.ability.startswith(prefixes), (
            weapon.id
        )
        assert weapon.cost is None or weapon.cost in GEAR_QUALITIES
        assert weapon.source == SUPPLEMENT_WEAPONS.get(weapon.id, "DE"), weapon.id
    # Missile weapons, and only they, have a range.
    assert all(w.range for w in _table("missile"))
    assert not any(w.range for w in _table("melee") + _table("natural"))


def test_natural_weapons_are_brawl_with_no_strength_load_or_cost():
    for weapon in _table("natural"):
        assert weapon.ability == "Brawl"
        assert (weapon.strength, weapon.load, weapon.cost) == (None, None, None)


def test_an_unknown_cost_or_table_is_refused():
    with pytest.raises(ValueError, match="cost"):
        WeaponDef("w", "W", "melee", "Brawl", 0, 0, 0, 0, cost="Cheap")
    with pytest.raises(ValueError, match="table"):
        WeaponDef("w", "W", "siege", "Brawl", 0, 0, 0, 0)


def _weapon_choices(
    books: set[str] | None, entry: pos.PossessionEntry | None = None
) -> list[str]:
    [book] = [
        f for f in possession_fields("weapon", entry, books=books) if f.key == "gear_id"
    ]
    return [value for _, value in book.options]


def test_a_supplements_weapon_is_offered_only_with_its_book_in_play():
    siphon = "weapon_greek_fire_siphon"
    assert siphon in _weapon_choices(None)  # every book
    assert siphon in _weapon_choices({"DE", "TSE"})
    assert siphon not in _weapon_choices({"DE"})
    assert "weapon_long_bow" in _weapon_choices({"DE"})
    # One already filled from it keeps its entry with the book set aside.
    held = Possession(id="s", kind="weapon", name="Siphon", gear_id=siphon)
    assert siphon in _weapon_choices({"DE"}, pos.PossessionEntry("weapon", held))
