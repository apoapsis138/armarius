"""Enchanted Devices & Talismans: the item-side arithmetic of
ArM5 DE ch. 8 (capacity, modified level, vis, charges), the warnings,
saving and loading, what deleting a holder or maker does, and the
Shape & Material catalog."""

import pytest
from support import strip_markup

from ars_magica_manager import catalog, deletion
from ars_magica_manager import enchanted_devices as ed
from ars_magica_manager.models import (
    CHARGED,
    LESSER,
    PAY_HIGHEST,
    Ability,
    ArtScore,
    Character,
    Covenant,
    DeviceComponent,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    Saga,
    ShapeMaterialBonus,
)
from ars_magica_manager.rules import enchantment
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga(*devices: EnchantedDevice) -> Saga:
    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    magus.arts = {
        "creo": ArtScore(xp=art_xp(5)),
        "intellego": ArtScore(xp=art_xp(8)),
        "ignem": ArtScore(xp=art_xp(10)),
        "vim": ArtScore(xp=art_xp(6)),
    }
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(2))]
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov1", saga_id="s", name="Keep")],
        characters=[magus],
        laboratories=[Laboratory(id="lab1", name="Tower", covenant_id="cov1")],
        enchanted_devices=list(devices),
    )


def _device(**kwargs) -> EnchantedDevice:
    kwargs.setdefault("holder_kind", "character")
    kwargs.setdefault("holder_id", "mag1")
    return EnchantedDevice(id=kwargs.pop("id", "d1"), name="Wand", **kwargs)


def _effect(**kwargs) -> InstilledEffect:
    return InstilledEffect(id=kwargs.pop("id", "e1"), name="Pilum", **kwargs)


# -- capacity (DE ch. 8, Material and Size Tables) --


@pytest.mark.parametrize(
    ("material", "size", "pawns"),
    [("wood", "small", 4), ("wood", "large", 8), ("silver", "small", 12)],
)
def test_capacity_is_material_times_size(material, size, pawns):
    device = _device(components=[DeviceComponent("x", material, size)])
    assert enchantment.capacity(_saga(device), device) == pawns


def _staff() -> list[DeviceComponent]:
    """The book's compound example: staff 8 + shoe 5 + quartz 12."""
    return [
        DeviceComponent("staff", "wood", "large"),
        DeviceComponent("shoe", "base metal", "tiny"),
        DeviceComponent("quartz", "semi-precious gem", "tiny"),
    ]


def test_compound_item_pays_the_sum_or_the_highest_component():
    device = _device(components=_staff())
    assert enchantment.capacity(_saga(device), device) == 25
    device.payment = PAY_HIGHEST
    assert enchantment.capacity(_saga(device), device) == 12


def test_talisman_capacity_is_the_magus_highest_technique_plus_form():
    device = _device(talisman=True, maker_id="mag1", components=_staff())
    assert enchantment.capacity(_saga(device), device) == 8 + 10


def test_capacity_override_wins_and_charged_items_have_none():
    device = _device(components=_staff(), capacity_override=30)
    assert enchantment.capacity(_saga(device), device) == 30
    assert "typed; worked out: 25" in ed.capacity_text(_saga(device), device)
    charged = _device(type=CHARGED, components=_staff())
    assert enchantment.capacity(_saga(charged), charged) is None


def test_opening_status():
    device = _device(components=[DeviceComponent("x", "wood", "small")])
    saga = _saga(device)
    device.pawns_opened = 2
    assert ed.opening_text(saga, device) == "Opening 2/4"
    device.pawns_opened = 4
    assert ed.opening_text(saga, device) == "Opened 4/4"


# -- modified level and vis (Designing the Effect, Effect Modifications) --


def test_modified_level_adds_frequency_penetration_and_modifications():
    effect = _effect(
        level=30,
        uses_per_day="6",
        penetration=10,
        maintains_concentration=True,
        restricted_use=True,
        environmental_trigger=True,
        fast_trigger=True,
        linked_trigger=True,
    )
    device = _device(effects=[effect])
    assert enchantment.modified_level(device, effect) == 30 + 3 + 5 + 5 + 3 + 3 + 5 + 3
    assert enchantment.vis_cost(device, effect) == 6


@pytest.mark.parametrize(
    ("uses", "added"),
    [
        ("1", 0),
        ("2", 1),
        ("3", 2),
        ("6", 3),
        ("12", 4),
        ("24", 5),
        ("50", 6),
        ("Unlimited", 10),
    ],
)
def test_uses_per_day_table(uses, added):
    effect = _effect(level=10, uses_per_day=uses)
    assert enchantment.modified_level(_device(), effect) == 10 + added


def test_charged_items_take_no_uses_per_day_and_no_vis():
    effect = _effect(level=10, uses_per_day="Unlimited")
    device = _device(type=CHARGED, effects=[effect])
    assert enchantment.modified_level(device, effect) == 10
    assert enchantment.vis_cost(device, effect) == 0


@pytest.mark.parametrize(("level", "vis"), [(1, 1), (10, 1), (30, 3), (31, 4)])
def test_vis_is_modified_level_over_ten_rounded_up(level, vis):
    effect = _effect(level=level)
    assert enchantment.vis_cost(_device(), effect) == vis


def test_overrides_replace_modified_level_and_vis():
    effect = _effect(level=30, modified_level_override=44)
    device = _device(effects=[effect])
    assert enchantment.modified_level(device, effect) == 44
    assert enchantment.vis_cost(device, effect) == 5
    effect.vis_override = 2
    assert enchantment.vis_cost(device, effect) == 2


def test_pawns_used_counts_every_effect_including_unknown_and_partial():
    effects = [
        _effect(id="a", level=10),
        _effect(id="b", level=20, known=False),
        _effect(id="c", level=25, instilling_progress=5),
    ]
    assert enchantment.pawns_used(_device(effects=effects)) == 1 + 2 + 3


def test_expiry_year_counts_from_first_use():
    effect = _effect(expiry="7 years", first_use_year=1221)
    assert ed.expiry_year(effect) == 1228
    assert ed.expiry_year(_effect(expiry="None", first_use_year=1221)) is None


# -- charges (Charged Items) --


@pytest.mark.parametrize(
    ("lab_total", "level", "charges"),
    [(30, 20, 2), (20, 20, 1), (21, 20, 1), (46, 20, 6), (15, 20, 0)],
)
def test_maximum_charges(lab_total, level, charges):
    device = _device(type=CHARGED, lab_total=lab_total, effects=[_effect(level=level)])
    assert ed.max_charges(device) == charges


def test_charges_made_default_to_the_maximum_and_can_be_fewer():
    device = _device(type=CHARGED, lab_total=46, effects=[_effect(level=20)])
    assert (ed.charges_made(device), ed.charges_left(device)) == (6, 6)
    device.charges_made = 4
    assert (ed.charges_made(device), ed.charges_left(device)) == (4, 4)


def test_use_charge_takes_one_off_and_does_nothing_at_zero():
    device = _device(type=CHARGED, lab_total=25, effects=[_effect(level=20)])
    assert ed.use_charge(device)
    assert ed.charges_left(device) == 0
    assert not ed.use_charge(device)
    assert ed.charges_left(device) == 0


# -- warnings --


def test_no_warnings_for_a_sound_item():
    effect = _effect(level=30)
    device = _device(
        components=[DeviceComponent("x", "wood", "small")],
        pawns_opened=4,
        maker_id="mag1",
        effects=[effect],
    )
    assert ed.warnings(_saga(device), device) == []


def test_warns_when_effects_use_more_pawns_than_were_opened():
    device = _device(
        components=[DeviceComponent("x", "wood", "small")],
        pawns_opened=2,
        effects=[_effect(level=30)],
    )
    assert (
        "use 3 pawns, but only 2 were opened" in ed.warnings(_saga(device), device)[0]
    )


def test_warns_when_a_lesser_enchantments_vis_exceeds_its_capacity():
    device = _device(
        type=LESSER,
        components=[DeviceComponent("x", "cloth", "tiny")],
        effects=[_effect(level=20)],
    )
    assert (
        "more than its Material and Size allow (1)"
        in ed.warnings(_saga(device), device)[0]
    )


def test_warns_beyond_the_makers_magic_theory_in_components():
    device = _device(maker_id="mag1", components=_staff(), pawns_opened=25)
    assert ed.warnings(_saga(device), device) == [
        "3 components: at most the maker's Magic Theory (2)."
    ]


def test_warns_of_a_second_talisman_for_the_same_magus():
    first = _device(id="t1", talisman=True, maker_id="mag1")
    second = _device(id="t2", talisman=True, maker_id="mag1")
    saga = _saga(first, second)
    assert any("already this magus's talisman" in w for w in ed.warnings(saga, second))


def test_warns_of_a_talisman_not_held_or_made_by_its_magus():
    device = _device(talisman=True, maker_id="mag1", holder_kind="laboratory")
    device.holder_id = "lab1"
    assert "A talisman is held by the magus who made it." in ed.warnings(
        _saga(device), device
    )
    unmade = _device(talisman=True)
    assert "A talisman needs its magus as its Maker." in ed.warnings(
        _saga(unmade), unmade
    )


def test_warns_of_two_attunements_in_one_season():
    device = _device(
        talisman=True,
        maker_id="mag1",
        attunements=[
            ShapeMaterialBonus(3, "fire", "Oak", 1221, "Spring"),
            ShapeMaterialBonus(2, "air", "Oak", 1221, "Spring"),
            ShapeMaterialBonus(2, "air", "Oak", 1221, "Summer"),
        ],
    )
    assert ed.warnings(_saga(device), device) == [
        "2 attunements gained in Spring 1221: one a season."
    ]


def test_warns_of_a_lab_total_below_the_level_and_too_many_charges():
    effect = _effect(level=20)
    low = _device(type=CHARGED, lab_total=15, effects=[effect])
    assert "below its effect's level (20)" in ed.warnings(_saga(low), low)[0]
    many = _device(type=CHARGED, lab_total=30, charges_made=5, effects=[effect])
    assert ed.warnings(_saga(many), many) == [
        "5 charges made, but its Lab Total gives at most 2."
    ]


# -- lists and panels --


def test_rows_list_talismans_first_and_effects_indented():
    staff = _device(
        id="d1",
        components=[DeviceComponent("x", "wood", "small")],
        pawns_opened=4,
        effects=[_effect(level=35, technique="Creo", form="Ignem", uses_per_day="6")],
    )
    talisman = _device(id="t1", talisman=True, maker_id="mag1", pawns_opened=18)
    talisman.name = "Ring"
    hidden = _effect(id="e2", known=False)
    staff.effects.append(hidden)
    saga = _saga(staff, talisman)
    rows = [
        strip_markup(label) for _, label in ed.device_rows(saga, "character", "mag1")
    ]
    # The name column fits the longest name, "(unknown power)" indented.
    assert rows == [
        "Ring               Talisman  Opened 18/18  0 effects",
        "Wand               Invested  Opened 4/4  2 effects",
        "  Pilum            CrIg 35  6/day",
        "  (unknown power)",
    ]
    staff.pawns_opened = 3
    assert strip_markup(ed.device_rows(saga, "character", "mag1")[1][1]).endswith(
        "Opening 3/4  2 effects  ✘"
    )
    assert ed.device_targets(saga, "character", "mag1")[3] == (staff, hidden)


def test_charged_row_shows_charges_and_objects():
    device = _device(type=CHARGED, lab_total=40, objects=5, effects=[_effect(level=20)])
    device.charges_left = 3
    [row, _] = ed.device_rows(_saga(device), "character", "mag1")
    assert strip_markup(row[1]) == "Wand     Charged   3/4 charges x5 objects"


def test_effect_panel_shows_the_breakdown_vis_and_expiry():
    effect = _effect(
        level=30,
        technique="Creo",
        form="Ignem",
        uses_per_day="6",
        penetration=10,
        expiry="7 years",
        first_use_year=1221,
    )
    text = strip_markup(ed.effect_info_text(_device(effects=[effect]), effect))
    assert "Modified level: 38 = 30 + 3 (6/day) + 5 (Pen 10)" in text
    assert "Vis: 4 pawns of Creo or Ignem" in text
    assert "Effect Expiry: 7 years from 1221: expires 1228" in text


# -- saving, loading, deleting --


def test_a_deleted_characters_devices_pass_to_their_covenant():
    device = _device(maker_id="mag1")
    saga = _saga(device)
    character = saga.characters[0]
    assert "1 enchanted device they hold passes to Keep." in (
        deletion.character_consequences(saga, character)
    )
    deletion.delete_character(saga, character)
    assert (device.holder_kind, device.holder_id) == ("covenant", "cov1")
    assert (device.maker_id, device.maker_name) == (None, "Leandro")


def test_a_deleted_labs_devices_without_a_covenant_go_with_it():
    device = _device(holder_kind="laboratory", holder_id="lab1")
    saga = _saga(device)
    lab = saga.laboratories[0]
    lab.covenant_id = None
    assert "1 enchanted device kept there is deleted with it: Wand." in (
        deletion.laboratory_consequences(saga, lab)
    )
    deletion.delete_laboratory(saga, lab)
    assert saga.enchanted_devices == []


def test_a_deleted_covenants_devices_go_with_it():
    device = _device(holder_kind="covenant", holder_id="cov1")
    saga = _saga(device)
    deletion.delete_covenant(saga, saga.covenants[0])
    assert saga.enchanted_devices == []


# -- the Shape & Material catalog --


def test_catalog_is_the_books_table_row_for_row():
    rows = catalog.load_shape_material_catalog()
    # The book's table, the Book shape from Covenants (an epitome), and
    # black hawthorn from Against the Dark.
    assert len(rows) == 243
    assert rows[0].name == "Adze" and rows[-1].name == "Yoke"
    agate = next(r for r in rows if r.name == "Agate")
    assert agate.bonuses == (
        (3, "air"),
        (5, "protection from storms"),
        (7, "protection from venom"),
    )
    assert all(r.citation.startswith("https://") for r in rows)
    assert {r.name: r.source for r in rows if r.source != "DE"} == {
        "Book": "Covenants",
        "Black Hawthorn": "AtD",
    }
    hawthorn = next(r for r in rows if r.name == "Black Hawthorn")
    assert hawthorn.bonuses == (
        (7, "protection from vampires"),
        (4, "protection from evil"),
        (4, "prevent disease"),
    )
    assert len({r.id for r in rows}) == len(rows)
