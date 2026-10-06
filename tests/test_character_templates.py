"""Character Templates on New Character: the catalog of the
book's ready-to-play characters, filling a sheet from one, and the New
Character form's Template choice."""

import pytest
from dialog_openers import contract_saga, new_app, open_dialog
from support import wait_until
from textual.widgets import Input, Select

from ars_magica_manager import catalog, creation, storage
from ars_magica_manager import character_templates as ct
from ars_magica_manager.arts import ARTS
from ars_magica_manager.models import Saga
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules.creation_characteristics import CHARACTERISTICS
from ars_magica_manager.rules.xp import score_from_xp

TEMPLATES = catalog.load_character_template_catalog()
NAMES = {"area": "Rhine", "second_area": "Alps", "language": "German"}


def test_the_book_has_six_grog_five_companion_and_twelve_magus_templates():
    counts = {kind: len(ct.templates_for(kind)) for kind in ("grog", "companion")}
    assert counts == {"grog": 6, "companion": 5}
    houses = {t.house for t in ct.templates_for("magus")}
    assert houses == set(catalog.load_house_catalog_by_id())
    assert ct.templates_for("mythic companion") == []


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.id)
def test_a_template_names_only_what_the_catalogs_hold(template):
    vfs = catalog.load_virtue_flaw_catalog_by_id()
    for vf in template.virtues_flaws:
        definition = vfs[vf["vf_id"]]
        assert set(vf["params"]) <= set(definition.parameters), vf
    for ability in template.abilities:
        assert access.ability_def(ability["name"]) is not None, ability
    assert set(template.arts) <= {art.lower() for art in ARTS}
    assert set(template.characteristics) == {key for key, _ in CHARACTERISTICS}
    spells = catalog.load_spell_catalog_by_id()
    for spell in template.spells:
        assert spell.get("spell_id", spell.get("version_of")) in spells, spell
    gear = {w.id for w in catalog.load_weapon_catalog()} | {
        a.id for a in catalog.load_armor_catalog()
    }
    for item in template.equipment:
        assert item["kind"] == "item" or item["gear_id"] in gear, item
    assert (template.house is not None) == (template.type == "magus")


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.id)
def test_using_a_template_fills_the_sheet_and_puts_it_in_play(template):
    saga = Saga(id="s", name="S", current_year=1220)
    character = creation.add_character(saga, "New", template.type, None)
    ct.apply(saga, character, template, NAMES)

    assert not character.in_creation
    assert character.background.year_born == 1220 - template.age
    for key, score in template.characteristics.items():
        assert getattr(character.characteristics, key) == score
    shown = {a.name: (score_from_xp(a.xp, 5), a.specialty) for a in character.abilities}
    for entry in template.abilities:
        name = entry["name"].format(**NAMES)
        assert shown[name] == (entry["score"], entry.get("specialty")), name
    assert not any("{" in a.name for a in character.abilities)
    for art, entry in template.arts.items():
        assert score_from_xp(character.arts[art].xp, 1) == entry["score"], art
    assert len(character.spells_known) == len(template.spells)
    assert len(character.virtues_flaws) == len(template.virtues_flaws)
    assert len(character.inventory) == len(template.equipment)
    assert character.hermetic.house == template.house
    assert template.name in character.description.biography


def test_xp_toward_the_next_score_and_aging_are_kept():
    """The Grizzled Veteran: Decrepitude 1 (2), Aging Points in three
    Characteristics; the Tremere's Aquam 8 (3)."""
    saga = Saga(id="s", name="S", current_year=1220)
    veteran = creation.add_character(saga, "Vet", "grog", None)
    ct.apply(saga, veteran, ct.find("tpl_grizzled_veteran"), NAMES)
    assert veteran.aging.decrepitude == 1
    assert veteran.aging.decrepitude_points == 5 + 2
    assert veteran.aging.aging_points == {"stamina": 1, "dexterity": 2, "quickness": 2}

    tremere = creation.add_character(saga, "Tre", "magus", None)
    ct.apply(saga, tremere, ct.find("tpl_tremere"), NAMES)
    assert tremere.arts["aquam"].xp == 36 + 3


def test_a_version_the_spell_catalog_lacks_is_added_to_the_saga_once():
    saga = Saga(id="s", name="S", current_year=1220)
    for name in ("One", "Two"):
        character = creation.add_character(saga, name, "magus", None)
        ct.apply(saga, character, ct.find("tpl_criamon"), NAMES)
    assert sorted(s.name for s in saga.spells) == [
        "Piercing the Magical Veil",
        "Unravelling the Fabric of Imaginem",
    ]
    veil = next(s for s in saga.spells if s.name == "Piercing the Magical Veil")
    assert (veil.technique, veil.form, veil.level) == ("Intellego", "Vim", 20)


def test_armor_and_weapons_take_the_books_figures():
    saga = Saga(id="s", name="S", current_year=1220)
    knight = creation.add_character(saga, "Sir", "companion", None)
    ct.apply(saga, knight, ct.find("tpl_knight"), NAMES)
    armor = next(item for item in knight.inventory if item.kind == "armor")
    assert (armor.name, armor.armor_protection) == ("Full Chain Mail", 9)
    sword = next(item for item in knight.inventory if item.name == "Great Sword")
    assert sword.gear_id == "weapon_great_sword"


# -- the New Character form --


async def _new_character(pilot, app, kind: str, template_id: str | None):
    base, dialog = await open_dialog(pilot, app, "create character")
    dialog.query_one("#fld-name", Input).value = "Ulla"
    dialog.query_one("#fld-type", Select).value = kind
    await pilot.pause()
    if template_id:
        dialog.query_one(f"#fld-template_{kind}", Select).value = template_id
        await pilot.pause()
    return base, dialog


async def _save_and_reach_blanks(pilot, app, dialog):
    """Create, and wait for the dialog asking for the template's names."""
    dialog.query_one("#btn-save").press()
    assert await wait_until(
        pilot,
        lambda: app.screen is not dialog and app.screen.query("#fld-language"),
        timeout=5.0,
    )
    await pilot.pause()
    return app.screen


async def test_the_template_choice_follows_the_type_and_describes_the_template():
    app = new_app()
    async with app.run_test(size=(120, 45)) as pilot:
        _, dialog = await _new_character(pilot, app, "grog", None)
        shown = {
            kind: dialog.query_one(f"#fdw-template_{kind}").display
            for kind in ("magus", "companion", "grog")
        }
        assert shown == {"magus": False, "companion": False, "grog": True}
        select = dialog.query_one("#fld-template_grog", Select)
        assert select.is_blank()
        offered = [str(prompt) for prompt, _ in select._options[1:]]
        assert offered == [t.name for t in ct.templates_for("grog")]

        select.value = "tpl_hunter"
        assert await wait_until(
            pilot,
            lambda: "The Hunter" in str(dialog.query_one("#fields-live").render()),
        )
        save = dialog.query_one("#btn-save")
        assert save.region.bottom <= 45


async def test_creating_from_a_template_asks_for_its_blanks_then_is_in_play():
    app = new_app()
    async with app.run_test(size=(120, 45)) as pilot:
        base, dialog = await _new_character(pilot, app, "grog", "tpl_hunter")
        blanks = await _save_and_reach_blanks(pilot, app, dialog)
        blanks.query_one("#fld-area", Input).value = "Black Forest"
        blanks.query_one("#fld-language", Input).value = "German"
        blanks.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is base)

        def ulla_shown() -> bool:
            view = base._current_sheet_view()
            return (
                view is not None and view.is_mounted and view.character.name == "Ulla"
            )

        # Let the new sheet finish mounting before the app closes.
        assert await wait_until(pilot, ulla_shown, timeout=5.0)
        await pilot.pause()
    saga = storage.load_saga(contract_saga().id)
    ulla = next(c for c in saga.characters if c.name == "Ulla")
    assert not ulla.in_creation
    assert ulla.type == "grog"
    assert "Area Lore: Black Forest" in {a.name for a in ulla.abilities}


async def test_cancelling_the_blanks_creates_no_character():
    app = new_app()
    async with app.run_test(size=(120, 45)) as pilot:
        base, dialog = await _new_character(pilot, app, "magus", "tpl_flambeau")
        blanks = await _save_and_reach_blanks(pilot, app, dialog)
        blanks.query_one("#btn-cancel").press()
        assert await wait_until(pilot, lambda: app.screen is base)
    saga = storage.load_saga(contract_saga().id)
    assert "Ulla" not in {c.name for c in saga.characters}
