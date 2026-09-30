import json
from dataclasses import asdict

import pytest
from support import strip_markup
from textual.content import Content

from ars_magica_manager import catalog, storage
from ars_magica_manager import possessions as pos
from ars_magica_manager.arts import FORMS, TECHNIQUES
from ars_magica_manager.models import (
    GEAR_POINTS,
    POSSESSION_KINDS,
    Character,
    Covenant,
    LabCharacteristics,
    Laboratory,
    Possession,
    Saga,
)
from ars_magica_manager.screens.forms import _possession_fields


def _saga() -> tuple[Saga, Covenant]:
    covenant = Covenant(id="cov1", saga_id="s", name="Dammerstein")
    saga = Saga(
        id="s",
        name="Saga",
        covenants=[covenant, Covenant(id="cov2", saga_id="s", name="Elsewhere")],
        characters=[Character(id="mag1", name="Corvinus", type="magus")],
        laboratories=[
            Laboratory(
                id="lab1",
                covenant_id="cov1",
                name="Obsidian Crucible",
                owner_id="mag1",
                location="The north tower",
                build_points=30,
                characteristics=LabCharacteristics(general_quality=4, upkeep=12),
            ),
            Laboratory(id="lab2", covenant_id="cov2", name="Not Ours"),
            Laboratory(id="lab3", covenant_id=None, name="Loose Lab"),
        ],
    )
    return saga, covenant


def _labels(saga: Saga, cov: Covenant, kind: str) -> list[str]:
    return [pos.row_label(e) for e in pos.entries_for_kind(saga, cov, kind)]


# ------------------------------------------------------------------ entries


def test_the_covenants_laboratories_are_listed_as_sanctums():
    saga, cov = _saga()
    entries = pos.entries_for_kind(saga, cov, "sanctum")
    assert [e.name for e in entries] == ["Obsidian Crucible"]  # only this covenant's
    entry = entries[0]
    assert entry.auto and entry.owner == "Corvinus"
    assert entry.location == "The north tower" and entry.build_points == 30


def test_manual_sanctums_follow_the_laboratories():
    saga, cov = _saga()
    cov.possessions.append(
        Possession(id="s", kind="sanctum", name="Hidden Study", owner="Leandro")
    )
    entries = pos.entries_for_kind(saga, cov, "sanctum")
    assert [e.name for e in entries] == ["Obsidian Crucible", "Hidden Study"]
    assert not entries[1].auto and entries[1].owner == "Leandro"


def test_a_record_for_a_laboratory_only_adds_covenant_side_fields():
    saga, cov = _saga()
    cov.possessions.append(
        Possession(
            id="o",
            kind="sanctum",
            lab_id="lab1",
            name="IGNORED",
            owner="IGNORED",
            location="IGNORED",
            quality=999,  # ignored -- Quality comes from the laboratory
            upkeep=999,  # ignored -- Upkeep comes from the laboratory
            usage="Heavy (3+ Seasons)",
            description="Very busy.",
        )
    )
    entries = pos.entries_for_kind(saga, cov, "sanctum")
    assert len(entries) == 1  # not listed twice
    entry = entries[0]
    assert (entry.name, entry.owner, entry.location) == (
        "Obsidian Crucible",
        "Corvinus",
        "The north tower",
    )  # live from the laboratory
    assert (entry.quality, entry.upkeep, entry.usage) == (4, 12, "Heavy (3+ Seasons)")
    assert entry.description == "Very busy."


def test_sanctum_quality_and_upkeep_come_from_the_laboratory():
    """A laboratory's General Quality and Upkeep Characteristics (manual plus
    any Virtue/Flaw modifiers) map directly onto its Sanctum entry."""
    saga, cov = _saga()
    lab = saga.laboratories[0]
    entry = pos.entries_for_kind(saga, cov, "sanctum")[0]
    assert (entry.quality, entry.upkeep) == (
        lab.characteristics.general_quality,
        lab.characteristics.upkeep,
    )
    lab.characteristics.general_quality = 0
    lab.characteristics.upkeep = 0
    entry = pos.entries_for_kind(saga, cov, "sanctum")[0]
    assert (entry.quality, entry.upkeep) == (0, 0)


def test_other_kinds_list_only_their_records_in_order():
    saga, cov = _saga()
    cov.possessions += [
        Possession(id="a", kind="weapon", name="Crossbows", quantity=6),
        Possession(id="b", kind="armor", name="Mail"),
        Possession(id="c", kind="weapon", name="Spears"),
    ]
    assert [e.name for e in pos.entries_for_kind(saga, cov, "weapon")] == [
        "Crossbows",
        "Spears",
    ]
    assert [e.name for e in pos.entries_for_kind(saga, cov, "armor")] == ["Mail"]
    assert pos.entries_for_kind(saga, cov, "item") == []


def test_total_pawns_adds_up_a_vis_list():
    saga, cov = _saga()
    cov.possessions += [
        Possession(id="a", kind="vis_store", name="A", art="Vim", pawns=9),
        Possession(id="b", kind="vis_store", name="B", art="Creo", pawns=3),
        Possession(id="c", kind="vis_source", name="C", art="Vim", pawns=4),
    ]
    assert pos.total_pawns(saga, cov, "vis_store") == 12
    assert pos.total_pawns(saga, cov, "vis_source") == 4


# --------------------------------------------------------------------- text


def test_row_labels_show_the_fields_the_sheet_lists():
    saga, cov = _saga()
    cov.possessions += [
        Possession(
            id="p",
            kind="property",
            name="North Field",
            location="By the river",
            dimensions="40 acres",
            inhabitants="Two families",
        ),
        Possession(id="p2", kind="property", name="Bare Plot"),
        Possession(
            id="s", kind="sanctum", name="Study", owner="Leandro", quality=3, upkeep=10
        ),
        Possession(id="w", kind="weapon", name="Crossbows", quantity=6),
        Possession(
            id="v", kind="vis_source", name="Well", art="Vim", pawns=3, season="Winter"
        ),
        Possession(id="r", kind="vis_store", name="Vim Vis", art="Vim", pawns=9),
    ]
    assert _labels(saga, cov, "property") == [
        "North Field         By the river      40 acres      Two families",
        "Bare Plot",  # every field but the name is optional
    ]
    sanctums = _labels(saga, cov, "sanctum")
    assert sanctums[0] == "Obsidian Crucible   Corvinus              4      12"
    assert sanctums[1] == "Study               Leandro               3      10"
    assert _labels(saga, cov, "weapon") == [
        # Weapons get four trailing combat-figure columns (Init/Attack/
        # Defense/Damage), defaulting to +0 -- see STORY-205 -- and Load.
        "Crossbows                               Standard        6   +0   +0   +0   +0    0"
    ]
    assert _labels(saga, cov, "vis_source") == [
        "Well                Vim            3  Winter"
    ]
    assert _labels(saga, cov, "vis_store") == ["Vim Vis             Vim            9"]


def test_row_labels_escape_user_text():
    saga, cov = _saga()
    cov.possessions.append(Possession(id="i", kind="item", name="[Bold] Lens"))
    assert _labels(saga, cov, "item")[0].startswith(r"\[Bold] Lens")


def test_detail_text_shows_everything_for_a_sanctum_and_renders_emphasis():
    saga, cov = _saga()
    cov.possessions.append(
        Possession(
            id="o",
            kind="sanctum",
            lab_id="lab1",
            description="Works **all** year, *never* idle.",
        )
    )
    text = pos.detail_text(pos.entries_for_kind(saga, cov, "sanctum")[0])
    plain = strip_markup(text)
    for expected in (
        "Name: Obsidian Crucible",
        "Owner: Corvinus",
        "Location: The north tower",
        "Quality: 4",
        "Upkeep: 12 Points",
        "Build Points: 30",
        "Usage: Standard (2 Seasons)",
        "A laboratory of this covenant: Obsidian Crucible.",
        "Description:",
        "Works all year, never idle.",
    ):
        assert expected in plain, expected
    content = Content.from_markup(text)
    styled = {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}
    assert ("all", "b") in styled and ("never", "i") in styled


def test_detail_text_omits_empty_optional_fields():
    saga, cov = _saga()
    cov.possessions += [
        Possession(id="p", kind="property", name="Bare Plot"),
        Possession(
            id="v",
            kind="vis_source",
            name="Well",
            art="Vim",
            pawns=3,
            season="Winter",
            location="Chapel",
            physical_form="Water",
            description="Cold.",
        ),
        Possession(id="r", kind="vis_store", name="Vim Vis", art="Vim", pawns=9),
        Possession(id="w", kind="armor", name="Mail", quantity=2, description="Rusty."),
    ]
    bare = strip_markup(pos.detail_text(pos.entries_for_kind(saga, cov, "property")[0]))
    assert bare == "Name: Bare Plot"
    source = strip_markup(
        pos.detail_text(pos.entries_for_kind(saga, cov, "vis_source")[0])
    )
    for expected in (
        "Art: Vim",
        "Pawns: 3",
        "Season: Winter",
        "Location: Chapel",
        "Physical Form: Water",
        "Description:",
        "Cold.",
    ):
        assert expected in source, expected
    store = strip_markup(
        pos.detail_text(pos.entries_for_kind(saga, cov, "vis_store")[0])
    )
    assert "Location" not in store and "Physical Form" not in store
    armor = strip_markup(pos.detail_text(pos.entries_for_kind(saga, cov, "armor")[0]))
    assert "Quantity: 2" in armor and "Rusty." in armor
    assert "Select a possession" in strip_markup(pos.detail_text(None))


# -------------------------------------------------------------------- model


def test_legacy_vis_stock_becomes_raw_vis_stores():
    cov = Covenant.from_dict(
        {
            "id": "c",
            "saga_id": "s",
            "name": "Old",
            "vis_stock": {"ignem": 5, "Vim": 2, "Mystery": 1},
        }
    )
    stores = [
        (p.name, p.art, p.pawns) for p in cov.possessions if p.kind == "vis_store"
    ]
    assert stores == [
        ("Ignem Vis", "Ignem", 5),
        ("Vim Vis", "Vim", 2),
        ("Mystery Vis", "Mystery", 1),  # an unknown Art is kept as typed
    ]
    assert "vis_stock" not in asdict(cov)  # moved, not copied or saved again
    # Loading the migrated data again doesn't migrate twice.
    assert len(Covenant.from_dict(asdict(cov)).possessions) == 3


def test_unknown_possession_kind_is_rejected():
    with pytest.raises(ValueError, match="kind"):
        Possession(id="x", kind="spaceship")
    assert len(POSSESSION_KINDS) == 7


def test_save_entry_adds_a_new_possession_and_updates_an_existing_one():
    saga, cov = _saga()
    pos.save_entry(cov, "item", None, {"name": "Silver Chalice"})
    chalice = cov.possessions[-1]
    assert (chalice.id, chalice.kind, chalice.lab_id) == (
        "silver_chalice",
        "item",
        None,
    )
    entry = next(e for e in pos.entries_for_kind(saga, cov, "item"))
    pos.save_entry(cov, "item", entry, {"name": "Gold Chalice"})
    assert chalice.name == "Gold Chalice" and len(cov.possessions) == 1


def test_save_entry_records_a_labs_sanctum_the_first_time_it_is_edited():
    saga, cov = _saga()
    sanctum = next(e for e in pos.entries_for_kind(saga, cov, "sanctum"))
    assert sanctum.record is None and sanctum.lab is not None
    pos.save_entry(cov, "sanctum", sanctum, {"upkeep": 3})
    record = cov.possessions[-1]
    assert (record.kind, record.lab_id, record.upkeep) == ("sanctum", "lab1", 3)
    assert record.id == "sanctum_lab1"


@pytest.mark.parametrize(
    ("values", "problem"),
    [
        ({"quantity": 1, "pawns": 1}, None),
        ({"quantity": 0}, "Quantity must be at least 1."),
        ({"pawns": 0}, "Pawns must be at least 1."),
    ],
)
def test_form_problem_checks_counts(values, problem):
    assert pos.form_problem(values) == problem


def test_form_problem_rejects_a_quality_the_gear_type_does_not_come_in():
    gear_type = next(iter(GEAR_POINTS))
    allowed = next(iter(GEAR_POINTS[gear_type]))
    assert pos.form_problem({"gear_type": gear_type, "gear_quality": allowed}) is None
    assert pos.form_problem({"gear_type": gear_type, "gear_quality": "Nonsense"})


# ------------------------------------------------ weapons & armor (STORY-709)


def test_weapon_and_armor_rows_show_signed_figures_n_a_and_load():
    saga, cov = _saga()
    cov.possessions += [
        Possession(
            id="d",
            kind="weapon",
            name="Dodge",
            weapon_init=0,
            weapon_attack=None,
            weapon_defense=0,
            weapon_damage=None,
        ),
        Possession(
            id="k",
            kind="weapon",
            name="Kick",
            weapon_init=-1,
            weapon_defense=-1,
            weapon_damage=3,
        ),
        Possession(
            id="m",
            kind="armor",
            name="Mail",
            gear_type="Full armor",
            armor_protection=9,
            load=6,
        ),
    ]
    assert pos.table_header("weapon").endswith("Init  Atk  Def  Dmg Load")
    assert _labels(saga, cov, "weapon") == [
        "Dodge                                   Standard        1   +0  n/a   +0  n/a    0",
        "Kick                                    Standard        1   -1   +0   -1   +3    0",
    ]
    assert pos.table_header("armor").endswith("Qty Prot Load")
    assert _labels(saga, cov, "armor") == [
        "Mail                Full armor          Standard        1   +9    6"
    ]


def test_detail_text_names_the_book_entry_and_its_figures():
    saga, cov = _saga()
    cov.possessions += [
        Possession(
            id="b",
            kind="weapon",
            name="Hugo's bow",
            gear_id="weapon_short_bow",
            weapon_init=-1,
            weapon_attack=3,
            weapon_damage=6,
            load=2,
        ),
        Possession(id="g", kind="weapon", name="Gone", gear_id="weapon_gone"),
        Possession(
            id="m",
            kind="armor",
            name="Mail",
            gear_id="armor_chain_mail",
            armor_protection=6,
            load=4,
        ),
    ]
    bow, gone = pos.entries_for_kind(saga, cov, "weapon")
    text = strip_markup(pos.detail_text(bow))
    for expected in (
        "Weapon: Short Bow (Bows, Min Str -1, range 15 paces)",
        "Init: -1",
        "Attack: +3",
        "Defense: +0",
        "Damage: +6",
        "Load: 2",
    ):
        assert expected in text, expected
    assert "Weapon: weapon_gone (not in the catalog)" in strip_markup(
        pos.detail_text(gone)
    )
    mail = strip_markup(pos.detail_text(pos.entries_for_kind(saga, cov, "armor")[0]))
    for expected in ("Material: Chain Mail", "Protection: +6", "Load: 4"):
        assert expected in mail, expected
    # A typed-in weapon has no book line.
    plain = Possession(id="p", kind="weapon", name="Spear")
    assert "Weapon:" not in pos.detail_text(pos.PossessionEntry("weapon", plain))


def test_old_saves_load_weapons_and_armor_without_the_new_fields():
    cov = Covenant.from_dict(
        {
            "id": "c",
            "saga_id": "s",
            "name": "Old",
            "possessions": [
                {"id": "w", "kind": "weapon", "name": "Spears", "weapon_attack": 2},
                {"id": "a", "kind": "armor", "name": "Mail"},
            ],
        }
    )
    weapon, armor = cov.possessions
    assert (weapon.gear_id, weapon.weapon_attack, weapon.load) == (None, 2, 0)
    assert (armor.armor_protection, armor.load) == (0, 0)


def _weapons(*tables: str):
    return {w.id: w for w in catalog.load_weapon_catalog(tables=tables)}


def test_choosing_a_book_weapon_fills_its_figures_cost_load_and_name():
    weapons = _weapons("melee", "missile")
    filled = pos.weapon_fills({"gear_id": "weapon_long_sword", "name": ""}, weapons)
    assert filled == {
        "weapon_init": 2,
        "weapon_attack": 4,
        "weapon_defense": 1,
        "weapon_damage": 6,
        "load": 1,
        "gear_type": "Weapon or shield",
        "gear_quality": "Expensive",
        "name": "Long Sword",
    }
    # The name follows the choice while it's still a book name...
    dodge = pos.weapon_fills({"gear_id": "weapon_dodge", "name": "Long Sword"}, weapons)
    assert dodge["name"] == "Dodge"
    # ...n/a figures fill as None, and no cost leaves the Quality alone.
    assert (dodge["weapon_attack"], dodge["weapon_damage"]) == (None, None)
    assert "gear_quality" not in dodge
    # A name the user typed stays.
    axe = pos.weapon_fills({"gear_id": "weapon_axe", "name": "Grandad's"}, weapons)
    assert "name" not in axe
    assert pos.weapon_fills({"gear_id": None, "name": ""}, weapons) == {}


def test_a_natural_weapon_fills_only_its_figures_and_name():
    filled = pos.weapon_fills(
        {"gear_id": "natural_large_claws", "name": ""}, _weapons("natural")
    )
    assert filled == {
        "weapon_init": 0,
        "weapon_attack": 5,
        "weapon_defense": 3,
        "weapon_damage": 4,
        "name": "Large Claws",
    }


def test_choosing_an_armor_material_fills_partial_or_full_figures():
    armors = catalog.load_armor_catalog_by_id()
    values = {"gear_id": "armor_chain_mail", "gear_type": "Partial armor", "name": ""}
    assert pos.armor_fills(values, armors) == {
        "gear_quality": "Expensive",
        "armor_protection": 6,
        "load": 4,
        "name": "Chain Mail",
    }
    values["gear_type"] = "Full armor"
    full = pos.armor_fills(values, armors)
    assert (full["armor_protection"], full["load"]) == (9, 6)
    # A partial-only material as full armor: no figures to suggest...
    values["gear_id"] = "armor_quilted_fur"
    assert "armor_protection" not in pos.armor_fills(values, armors)
    # ...and the form refuses it.
    assert (
        pos.form_problem(
            {
                "gear_id": "armor_quilted_fur",
                "gear_type": "Full armor",
                "gear_quality": "Inexpensive",
            }
        )
        == "Quilted/Fur only comes as partial armor."
    )
    assert (
        pos.form_problem(
            {
                "gear_id": "armor_quilted_fur",
                "gear_type": "Partial armor",
                "gear_quality": "Inexpensive",
            }
        )
        is None
    )


def test_form_problem_refuses_a_negative_load():
    assert pos.form_problem({"load": -1}) == "Load can't be negative."


def test_book_text_describes_the_chosen_entry():
    text = strip_markup(pos.book_text("weapon", "weapon_staff"))
    assert text.startswith("Staff (Great Weapon, Min Str -1): A common")
    armor = strip_markup(pos.book_text("armor", "armor_heavy_leather"))
    assert armor.startswith("Heavy Leather (partial +2 Load 3, partial only): ")
    assert "Choose a Weapon" in pos.book_text("weapon", None)
    assert "Choose a Material" in pos.book_text("armor", "armor_gone")


def test_a_new_save_has_no_vis_stock():
    # B17: the field was migrated away but still written (as {}) every save.
    saga = Saga(id="s", name="S", covenants=[Covenant(id="c", saga_id="s", name="C")])
    path = storage.save_saga(saga)
    assert (
        "vis_stock" not in json.loads(path.read_text(encoding="utf-8"))["covenants"][0]
    )


def test_siege_engines_only_come_expensive_and_points_follow_the_table():
    ballista = {"gear_type": "Ballista or light catapult"}
    problem = pos.form_problem(ballista | {"gear_quality": "Standard"})
    assert problem is not None and "only comes expensive" in problem
    assert pos.form_problem(ballista | {"gear_quality": "Expensive"}) is None
    saga, cov = _saga()
    cov.possessions = [
        Possession(
            id="b",
            kind="weapon",
            name="Ballista",
            gear_type="Ballista or light catapult",
            gear_quality="Expensive",
        )
    ]
    assert pos.gear_points(saga, cov) == 16


def test_the_weapon_form_offers_every_weapon_type():
    [types] = [f for f in _possession_fields("weapon", None) if f.key == "gear_type"]
    assert [value for _, value in types.options] == [
        "Weapon or shield",
        "Ballista or light catapult",
        "Heavy catapult or trebuchet",
    ]


def test_vis_forms_offer_the_fifteen_arts_and_the_four_seasons():
    fields = {f.key: f for f in _possession_fields("vis_source", None)}
    assert [v for _, v in fields["art"].options] == [*TECHNIQUES, *FORMS]
    assert [v for _, v in fields["season"].options] == [
        "Spring",
        "Summer",
        "Autumn",
        "Winter",
    ]
    # A store has no season harvested, and no description.
    store = {f.key for f in _possession_fields("vis_store", None)}
    assert "season" not in store and "description" not in store
