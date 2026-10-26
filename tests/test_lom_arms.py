"""Lords of Men's arms and armour: its weapons in the catalog, offered with
the book in play (pp. 137-139; the Errata p. 76's bastard sword), and its
armour worn as pieces whose Protection and Load add up, fractions kept to
the end and rounded up (Expanded Armor Table, p. 140; Complex Armor Design,
p. 142). The Definitive Edition's tables win where Lords of Men differs."""

import random

import pytest

from ars_magica_manager import catalog
from ars_magica_manager import possessions as pos
from ars_magica_manager.forms.possession import possession_fields
from ars_magica_manager.models import (
    ARMOR_SLOTS,
    Ability,
    ArmorPieceDef,
    Character,
    Characteristics,
    Possession,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import armour, combat, derived, harm
from ars_magica_manager.rules.xp import ability_xp


def _piece(gear_id: str, **kw) -> Possession:
    """A piece filled from the catalog as the form fills it."""
    values = pos.armor_fills(
        {"gear_id": gear_id},
        catalog.load_armor_catalog_by_id(),
        catalog.load_armor_piece_catalog_by_id(),
    )
    return Possession(id=gear_id, kind="armor", gear_id=gear_id, **values | kw)


def _weapon(gear_id: str) -> Possession:
    weapons = catalog.load_weapon_catalog_by_id()
    values = pos.weapon_fills({"gear_id": gear_id}, weapons)
    return Possession(id=gear_id, kind="weapon", gear_id=gear_id, **values)


def _wearer(*inventory: Possession) -> Character:
    return Character(
        id="k",
        name="Knight",
        type="grog",
        characteristics=Characteristics(stamina=2, strength=1, quickness=1),
        abilities=[Ability("Crossbow", xp=ability_xp(3))],
        inventory=list(inventory),
    )


# The catalog


# (id, Init, Atk, Dfn, Dam, Str, Load, Cost, Range) as Lords of Men prints them.
@pytest.mark.parametrize(
    "row",
    [
        ("weapon_falchion", 1, 4, 1, 4, 0, 1, "Standard", None),
        ("weapon_net", -1, 2, 2, 0, -1, 3, "Standard", None),
        ("weapon_infantry_shield", 0, 0, 4, 0, 0, 3, "Standard", None),
        ("weapon_trident", 3, 3, 3, 5, 1, 3, "Expensive", None),
        ("weapon_whip", 2, 1, 1, -3, -2, 2, "Inexpensive", None),
        ("weapon_halberd", 2, 4, 1, 10, 1, 2, "Standard", None),
        # Errata p. 76: one-handed, Strength +1 and Load 2.
        ("weapon_bastard_sword_one_handed", 2, 4, 1, 6, 1, 2, "Expensive", None),
        ("weapon_bastard_sword_two_handed", 2, 5, 2, 9, 1, 2, "Expensive", None),
        ("weapon_sharpened_rock", 0, 0, 1, 3, -1, 1, "Inexpensive", 5),
        ("weapon_composite_bow", -2, 4, 0, 7, 2, 2, "Expensive", 30),
        ("weapon_horse_bow", -2, 5, 0, 8, 2, 2, "Expensive", 15),
        ("weapon_crossbow", 5, 5, 0, 8, 1, 2, "Expensive", 25),
        ("weapon_arbalest", 5, 5, 0, 10, -1, 3, "Expensive", 30),
        ("weapon_heavy_arbalest", 5, 5, 0, 12, 1, 2, "Expensive", 35),
    ],
    ids=lambda row: row[0],
)
def test_lords_of_mens_weapons_match_its_tables(row):
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
    assert "LoM" in weapon.source


def test_the_definitive_editions_figures_win_where_lords_of_men_differs():
    weapons = catalog.load_weapon_catalog_by_id()
    # Lords of Men p. 138 prints the throwing axe Atk 0 Dfn +2 and the short
    # bow ("Bow") Load 1; p. 137 the warhammer Inexpensive. DE pp. 400-401:
    axe, bow, hammer = (
        weapons["weapon_throwing_axe"],
        weapons["weapon_short_bow"],
        weapons["weapon_warhammer"],
    )
    assert (axe.attack, axe.defense, bow.load, hammer.cost) == (2, 0, 2, "Standard")


def test_the_crossbow_ability_comes_with_lords_of_men():
    ability = catalog.load_ability_catalog_by_id()["ab_crossbow"]
    assert (ability.name, ability.category, ability.source) == (
        "Crossbow",
        "Martial",
        "LoM",
    )


def _weapon_choices(books: set[str] | None) -> list[str]:
    [book] = [
        f for f in possession_fields("weapon", None, books=books) if f.key == "gear_id"
    ]
    return [value for _, value in book.options]


def test_lords_of_mens_weapons_are_offered_only_with_a_book_that_prints_them():
    assert "weapon_halberd" in _weapon_choices({"DE", "LoM"})
    assert "weapon_halberd" not in _weapon_choices({"DE"})
    # A row Lords of Men reprints from Ancient Magic comes with either book.
    assert "weapon_composite_bow" in _weapon_choices({"DE", "AM"})
    assert "weapon_composite_bow" not in _weapon_choices({"DE", "GotF"})
    assert "weapon_trident" in _weapon_choices({"DE", "GotF"})


def test_the_pieces_are_lords_of_mens_expanded_armor_table():
    pieces = catalog.load_armor_piece_catalog_by_id()
    assert len(pieces) == 38  # 28 body armours, 5 surcoats and greaves, 5 helmets
    assert all(p.source == "LoM" for p in pieces.values())

    def cell(gear_id: str) -> tuple[str, float, float, str]:
        p = pieces[gear_id]
        return p.slot, p.protection, p.load, p.cost

    assert cell("armor_piece_mail_hauberk") == ("Body", 5, 2.5, "Expensive")
    assert cell("armor_piece_reinforced_haubergeon") == ("Body", 2.5, 2.5, "Standard")
    assert cell("armor_piece_plate_full") == ("Body", 12, 6, "Expensive")
    assert cell("armor_piece_padded_full") == ("Body", 1, 1.5, "Inexpensive")
    # Rigid materials make no sleeved garment (n/a).
    assert "armor_piece_boiled_leather_haubergeon" not in pieces
    assert "armor_piece_plate_hauberk" not in pieces
    assert cell("armor_piece_gambeson") == ("Surcoat", 1, 1.5, "Inexpensive")
    assert cell("armor_piece_plate_and_mail_jambes") == ("Greaves", 2, 0.5, "Expensive")
    assert cell("armor_piece_coif") == ("Helmet", 0.5, 0, "Expensive")
    assert pieces["armor_piece_helm"].perception == -3
    assert pieces["armor_piece_mail_full"].full
    assert not pieces["armor_piece_mail_hauberk"].full


def test_a_piece_has_a_known_slot_and_cost():
    with pytest.raises(ValueError, match="slot"):
        ArmorPieceDef("p", "P", "Gloves", 1, 1, "Standard")
    with pytest.raises(ValueError, match="full"):
        ArmorPieceDef("p", "P", "Helmet", 1, 1, "Standard", full=True)


# The armour form


def _armor_fields(books: set[str] | None, entry: pos.PossessionEntry | None = None):
    return {f.key: f for f in possession_fields("armor", entry, books=books)}


def test_the_pieces_and_where_they_are_worn_come_with_lords_of_men():
    fields = _armor_fields({"DE", "LoM"})
    materials = [value for _, value in fields["gear_id"].options]
    assert "armor_chain_mail" in materials and "armor_piece_helm" in materials
    assert [value for _, value in fields["armor_slot"].options] == [
        "",
        *ARMOR_SLOTS,
    ]
    plain = _armor_fields({"DE"})
    assert "armor_slot" not in plain
    assert "armor_piece_helm" not in [value for _, value in plain["gear_id"].options]
    # A piece already worn keeps its entry and slot with the book set aside.
    helm = _piece("armor_piece_helm")
    kept = _armor_fields({"DE"}, pos.PossessionEntry("armor", helm))
    assert kept["armor_slot"].value == "Helmet"
    assert "armor_piece_helm" in [value for _, value in kept["gear_id"].options]


def test_choosing_a_piece_fills_its_figures_rounded_up_and_where_it_is_worn():
    filled = pos.armor_fills(
        {"gear_id": "armor_piece_mail_hauberk", "name": ""},
        catalog.load_armor_catalog_by_id(),
        catalog.load_armor_piece_catalog_by_id(),
    )
    assert filled == {
        "gear_quality": "Expensive",
        "armor_protection": 5,
        "load": 3,
        "armor_slot": "Body",
        "gear_type": "Partial armor",
        "name": "Mail Hauberk",
    }
    full = _piece("armor_piece_mail_full")
    assert full.gear_type == "Full armor"
    # Back to a whole suit: the Definitive Edition's material clears the slot.
    suit = pos.armor_fills(
        {"gear_id": "armor_chain_mail", "armor_slot": "Body", "name": "Mail Hauberk"},
        catalog.load_armor_catalog_by_id(),
        catalog.load_armor_piece_catalog_by_id(),
    )
    assert suit["armor_slot"] == "" and suit["name"] == "Chain Mail"
    assert "Perception -3" in pos.book_text("armor", "armor_piece_helm")


# Protection and Load summed over the pieces worn


def test_an_outfit_adds_its_pieces_and_rounds_up_at_the_end():
    # Mail hauberk +5 Load 2.5, gambeson +1 Load 1.5, open helmet +1 Load 1.
    knight = _wearer(
        _piece("armor_piece_mail_hauberk"),
        _piece("armor_piece_gambeson"),
        _piece("armor_piece_open_helmet"),
    )
    assert armour.protection(knight.inventory) == 7
    assert armour.load(knight.inventory) == 5
    assert derived.carried_load(knight.inventory) == 5
    assert derived.soak(knight).total == 2 + 7


def test_fractions_are_kept_until_the_end():
    # Reinforced haubergeon +2.5 and a coif +0.5: +3, not 3 + 1.
    inventory = [
        _piece("armor_piece_reinforced_haubergeon"),
        _piece("armor_piece_coif"),
    ]
    assert armour.protection(inventory) == 3
    assert armour.load(inventory) == 3  # 2.5 + 0 rounded up
    # A lone mail cuirass +3 Load 1.5 with a coif: +3.5 -> 4, Load 2.
    alone = [_piece("armor_piece_mail_cuirass"), _piece("armor_piece_coif")]
    assert (armour.protection(alone), armour.load(alone)) == (4, 2)
    lines = derived.soak(_wearer(*alone)).lines
    assert [(line.label, line.amount) for line in lines[1:]] == [
        ("Mail Cuirass or Jerkin", 3),
        ("Coif or Camail", 0.5),
        ("Rounded up", 0.5),
    ]


def test_full_body_armour_already_includes_greaves():
    inventory = [_piece("armor_piece_mail_full"), _piece("armor_piece_plate_jambes")]
    assert [p.gear_id for p in armour.worn(inventory)] == ["armor_piece_mail_full"]
    assert (armour.protection(inventory), armour.load(inventory)) == (7, 4)
    with_hauberk = [
        _piece("armor_piece_mail_hauberk"),
        _piece("armor_piece_plate_jambes"),
    ]
    assert armour.protection(with_hauberk) == 6


def test_one_piece_of_each_place_the_best_and_the_better_of_suit_or_outfit():
    cap, helm = _piece("armor_piece_iron_cap"), _piece("armor_piece_helm")
    padded = _piece("armor_piece_padded_cuirass")
    assert armour.worn([cap, helm, padded]) == [padded, helm]
    # A whole suit of chain mail (+6) protects better than padding and a helm.
    suit = Possession(
        id="s", kind="armor", name="Chain Mail", armor_protection=6, load=4
    )
    assert armour.worn([suit, padded, helm]) == [suit]
    assert derived.carried_load([suit, padded, helm]) == 4
    # Full plate (+12) beats it.
    plate = _piece("armor_piece_plate_full")
    assert armour.worn([suit, plate]) == [plate]
    # An old save's armour, with no slot, is a whole suit as before.
    assert not armour.is_piece(Possession(id="o", kind="armor"))


def test_how_well_made_adds_to_a_piece_but_a_helmet_only_against_the_head():
    body = _piece("armor_piece_metal_scale_hauberk", make="Superior")
    helm = _piece("armor_piece_helm", make="Superior")
    assert armour.protection([body, helm]) == 5 + 1 + 2


def test_a_changed_piece_counts_as_typed():
    # Filled in as +1 (the book's +0.5 rounded up), then typed +2.
    coif = _piece("armor_piece_coif", armor_protection=2)
    assert armour.figures(coif) == (2, 0)
    assert armour.figures(_piece("armor_piece_coif")) == (0.5, 0)


def test_primitive_equipment_counts_once_for_an_outfit_that_isnt_inexpensive():
    cheap = _wearer(
        _piece("armor_piece_padded_cuirass"), _piece("armor_piece_iron_cap")
    )
    cheap.virtues_flaws = [VirtueFlawInstance("vf_primitive_equipment")]
    assert not derived.primitive_outfit(cheap)
    dear = _wearer(_piece("armor_piece_mail_hauberk"), _piece("armor_piece_helm"))
    dear.virtues_flaws = [VirtueFlawInstance("vf_primitive_equipment")]
    assert derived.soak(dear).total == 2 + 7 - 1
    sword = _weapon("weapon_falchion")
    labels = [line.label for line in combat.combat_totals(dear, sword).initiative.lines]
    assert labels.count("Primitive Equipment (armour)") == 1


def test_harm_without_armour_takes_the_whole_outfit_off_soak():
    knight = _wearer(_piece("armor_piece_mail_hauberk"), _piece("armor_piece_helm"))
    _, with_armour, _ = harm.damage(knight, 0, random.Random(1))
    _, without, _ = harm.damage(knight, 0, random.Random(1), armour=False)
    assert with_armour - without == 7


def test_a_crossbows_damage_is_its_own():
    knight = _wearer(_weapon("weapon_heavy_arbalest"))
    totals = combat.combat_totals(knight, knight.inventory[0])
    assert totals.ability == "Crossbow"
    assert totals.damage is not None and totals.damage.total == 12


def test_complex_armour_design_matches_the_tables_full_mail():
    every = list(armour.BODY_PARTS)
    assert armour.design({"Mail": every}) == (7, 4)  # +7, Load 3.5 rounded up
    # Padded on the torso, boiled leather on the shins: 1 + 0.5 -> 2; Load
    # 1.5 + 0.75 -> 3.
    assert armour.design({"Padded": ["Torso"], "Boiled Leather": ["Shins"]}) == (2, 3)
    with pytest.raises(ValueError, match="material"):
        armour.design({"Mithril": ["Torso"]})
