"""Exporting a covenant, laboratory or character and importing it into
another saga."""

from __future__ import annotations

import json

import pytest
from support import choose, menu

from ars_magica_manager import catalog, storage, transfer
from ars_magica_manager import house_rules as hr
from ars_magica_manager import spells as spl
from ars_magica_manager.models import (
    Book,
    Character,
    CharterSeal,
    Covenant,
    DiaryEntry,
    EnchantedDevice,
    Familiar,
    Inhabitant,
    InstilledEffect,
    KnownSpell,
    LabItemBenefit,
    Laboratory,
    LabSpecialtyGrant,
    LabTextAccess,
    Possession,
    Saga,
    Spell,
    VirtueFlawInstance,
)


def _source() -> Saga:
    covenant = Covenant(id="keep", saga_id="src", name="Keep")
    magus = Character(id="leandro", name="Leandro", type="magus", covenant_id="keep")
    other = Character(id="flavia", name="Flavia", type="magus", covenant_id="keep")
    grog = Character(id="hugo", name="Hugo", type="grog", covenant_id="keep")
    lab = Laboratory(id="tower", covenant_id="keep", name="Tower", owner_id="leandro")
    magus.assigned_lab_id = "tower"
    magus.raw_vis = {"creo": 3}
    magus.diary = [DiaryEntry(1220, "Spring", "Arrived")]
    magus.lab_text_access = {
        "flavia": LabTextAccess(20, "decoded"),
        "Old Jacobus": LabTextAccess(10),
    }
    saga = Saga(
        id="src",
        name="Source Saga",
        covenants=[covenant],
        characters=[magus, other, grog],
        laboratories=[lab],
    )
    virtue = hr.add(
        saga, hr.CHARACTER, {"name": "Storm-Touched", "type": "Virtue", "tier": "Minor"}
    )
    hook = hr.add(
        saga, hr.COVENANT, {"name": "Feuding Abbot", "type": "Hook", "tier": "Major"}
    )
    lab_flaw = hr.add(
        saga, hr.LABORATORY, {"name": "Leaky Roof", "type": "Flaw", "tier": "Free"}
    )
    hr.add(saga, hr.CHARACTER, {"name": "Unused", "type": "Flaw", "tier": "Minor"})
    magus.virtues_flaws = [VirtueFlawInstance(virtue.id)]
    covenant.boons_hooks = [VirtueFlawInstance(hook.id)]
    lab.virtues_flaws = [VirtueFlawInstance(lab_flaw.id)]
    own = spl.add_invented_spell(saga, magus, "Spark of Wit", "Creo", "Mentem")
    own.level = 10
    shared = Spell(
        id="saga_ward", name="Ward of Thorns", technique="Rego", form="Herbam", level=15
    )
    saga.spells.append(shared)
    catalog_spell = next(iter(catalog.load_spell_catalog_by_id()))
    magus.spells_known = [
        KnownSpell(spell_id=own.id),
        KnownSpell(spell_id=shared.id),
        KnownSpell(spell_id=catalog_spell),
    ]
    saga.familiars.append(Familiar(id="corax", character_id="leandro", name="Corax"))
    saga.enchanted_devices.append(
        EnchantedDevice(
            "wand",
            "Wand",
            holder_kind="character",
            holder_id="leandro",
            maker_id="flavia",
        )
    )
    saga.books += [
        Book(
            id="notes",
            name="Lab Text: Spark of Wit",
            type="Lab Text",
            text_kind="Spell",
            spell_id=own.id,
            spell_name="Spark of Wit",
            owner_kind="character",
            owner_id="leandro",
            author="Leandro",
            author_id="leandro",
            raw=True,
        ),
        Book(
            id="lab_book",
            name="Lab Text: Ward of Thorns",
            type="Lab Text",
            text_kind="Spell",
            spell_id=shared.id,
            spell_name="Ward of Thorns",
            owner_kind="laboratory",
            owner_id="tower",
            author="Flavia",
            author_id="flavia",
        ),
        Book(
            id="summa",
            name="Summa of Flame",
            type="Art Summa",
            art="Ignem",
            level=10,
            quality=8,
            owner_kind="covenant",
            owner_id="keep",
        ),
    ]
    covenant.inhabitants = [
        Inhabitant(id="i1", kind="turb", name="Hugo", character_id="hugo")
    ]
    covenant.possessions = [
        Possession(
            id="v1",
            kind="vis_store",
            name="Cask",
            art="Vim",
            pawns=4,
            location_kind="laboratory",
            location_id="tower",
        ),
        Possession(id="s1", kind="sanctum", lab_id="tower", usage="Heavy"),
    ]
    catalog.use_saga(None)
    return saga


def _target() -> Saga:
    return Saga(
        id="dst",
        name="Target Saga",
        covenants=[Covenant(id="hold", saga_id="dst", name="Keep")],
    )


def _roundtrip(saga: Saga, record, **options) -> dict:
    """What an export file would hold (through JSON, as on disk)."""
    return json.loads(json.dumps(transfer.export_data(saga, record, **options)))


def test_a_character_takes_its_familiar_devices_books_and_spells():
    source = _source()
    magus = source.character("leandro")
    data = _roundtrip(source, magus)
    assert (data["format"], data["kind"], data["name"]) == (
        transfer.FORMAT,
        "character",
        "Leandro",
    )
    held = data["saga"]
    assert [c["name"] for c in held["characters"]] == ["Leandro"]
    assert [f["name"] for f in held["familiars"]] == ["Corax"]
    assert [b["name"] for b in held["books"]] == ["Lab Text: Spark of Wit"]
    assert [d["name"] for d in held["enchanted_devices"]] == ["Wand"]
    # The saga's spell he knows travels; his own invention is on his sheet.
    assert [s["name"] for s in held["spells"]] == ["Ward of Thorns"]
    # Only the House Rule he holds, not the unused one or the others' kinds.
    assert [e["name"] for e in held["custom_virtues_flaws"]] == ["Storm-Touched"]
    assert held["custom_boons_hooks"] == [] and held["covenants"] == []
    # What it points at outside the file, by name.
    assert data["links"] == {
        "character": {"flavia": "Flavia"},
        "laboratory": {"tower": "Tower"},
        "covenant": {"keep": "Keep"},
        "neighbour": {},
        "creature": {},
    }


def test_importing_a_character_matches_links_by_name_or_drops_them():
    source = _source()
    data = _roundtrip(source, source.character("leandro"))
    target = _target()
    plan = transfer.plan_import(target, data)
    assert target.characters == []  # planning changes nothing
    text = transfer.preview(plan)
    assert text.splitlines()[0] == "Import Character: Leandro from Source Saga"
    assert "  Character: Leandro (magus)" in text and "  Familiar: Corax" in text
    assert "  1 book" in text and "  1 enchanted device" in text
    assert "  1 spell" in text and "  1 House Rule" in text
    assert plan.matched == ["Covenant Keep (matched by name)"]
    assert sorted(plan.dropped) == [
        "Character Flavia: not in this saga",
        "Laboratory Tower: not in this saga",
    ]
    transfer.apply(target, plan)
    [magus] = target.characters
    # The covenant of that name here, by its own id; no laboratory.
    assert (magus.covenant_id, magus.assigned_lab_id) == ("hold", None)
    assert magus.raw_vis == {"creo": 3} and magus.diary[0].name == "Arrived"
    assert target.familiars[0].character_id == magus.id
    [wand] = target.enchanted_devices
    # Its maker isn't here: remembered by name.
    assert (wand.holder_id, wand.maker_id, wand.maker_name) == (
        magus.id,
        None,
        "Flavia",
    )
    [book] = target.books
    assert (book.owner_id, book.author_id) == (magus.id, magus.id)
    assert catalog.find_spell(target, book.spell_id).name == "Spark of Wit"
    assert [catalog.find_spell(target, k.spell_id).name for k in magus.spells_known][
        :2
    ] == ["Spark of Wit", "Ward of Thorns"]
    assert [s.name for s in target.spells] == ["Ward of Thorns"]
    # His House Rule came too, and is in the catalogs of the saga in use.
    [virtue] = target.custom_virtues_flaws
    assert magus.virtues_flaws[0].vf_id == virtue.id
    assert virtue.id in catalog.load_virtue_flaw_catalog_by_id()
    # Whose Lab Texts he reads: the author who isn't here goes by name.
    assert magus.lab_text_access == {
        "Flavia": LabTextAccess(20, "decoded"),
        "Old Jacobus": LabTextAccess(10),
    }


def test_importing_into_the_same_saga_makes_a_second_copy_with_new_ids():
    saga = _source()
    data = _roundtrip(saga, saga.character("leandro"))
    plan = transfer.plan_import(saga, data)
    assert any("already has a character named Leandro" in n for n in plan.notes)
    transfer.apply(saga, plan)
    first, second = [c for c in saga.characters if c.name == "Leandro"]
    assert first.id == "leandro" and second.id != "leandro"
    # Flavia is here, so the links to her are kept.
    assert "Character Flavia (matched by name)" in plan.matched
    assert second.lab_text_access["flavia"] == LabTextAccess(20, "decoded")
    # The Tower already has its owner: the copy gets no laboratory.
    assert second.assigned_lab_id is None
    assert saga.laboratory("tower").owner_id == "leandro"
    assert "Leandro's laboratory Tower: already has an owner here" in plan.dropped
    # Nothing is shared between the two: each has his own of everything.
    assert len({f.id for f in saga.familiars}) == 2
    assert len({d.id for d in saga.enchanted_devices}) == 2
    assert len({b.id for b in saga.books}) == 4
    copies = [s.id for s in first.invented_spells + second.invented_spells]
    assert len(set(copies)) == 2
    assert second.spells_known[0].spell_id == second.invented_spells[0].id
    # The saga's own spell and the House Rule are already here: reused.
    assert [s.id for s in saga.spells] == ["saga_ward"]
    assert len(saga.custom_virtues_flaws) == 2
    assert second.virtues_flaws[0].vf_id == first.virtues_flaws[0].vf_id
    # Still loads and saves.
    storage.save_saga(saga)
    assert len(storage.load_saga("src").characters) == 4


def test_a_laboratory_takes_its_books_and_finds_its_owner():
    source = _source()
    data = _roundtrip(source, source.laboratory("tower"))
    assert [b["name"] for b in data["saga"]["books"]] == ["Lab Text: Ward of Thorns"]
    assert [e["name"] for e in data["saga"]["custom_lab_virtues_flaws"]] == [
        "Leaky Roof"
    ]
    target = _target()
    leandro = Character(id="leo", name="Leandro", type="magus", covenant_id="hold")
    target.characters.append(leandro)
    plan = transfer.plan_import(target, data)
    transfer.apply(target, plan)
    [lab] = target.laboratories
    # A magus of that name with no laboratory here: he gets it.
    assert (lab.covenant_id, lab.owner_id) == ("hold", "leo")
    assert leandro.assigned_lab_id == lab.id
    [book] = target.books
    assert (book.owner_kind, book.owner_id) == ("laboratory", lab.id)
    # The author isn't here: the typed name stays, the link goes.
    assert (book.author, book.author_id) == ("Flavia", None)
    assert lab.virtues_flaws[0].vf_id == target.custom_lab_virtues_flaws[0].id


def test_a_covenant_alone_or_with_its_members():
    source = _source()
    covenant = source.covenants[0]
    alone = _roundtrip(source, covenant)
    assert alone["saga"]["characters"] == [] and alone["saga"]["laboratories"] == []
    assert [b["name"] for b in alone["saga"]["books"]] == ["Summa of Flame"]
    target = Saga(id="dst", name="Target Saga")
    plan = transfer.plan_import(target, alone)
    transfer.apply(target, plan)
    [keep] = target.covenants
    assert keep.saga_id == "dst"
    # No Hugo here: his line stays, as someone with no sheet.
    assert (keep.inhabitants[0].name, keep.inhabitants[0].character_id) == (
        "Hugo",
        None,
    )
    # No Tower here: the vis store is kept at the covenant, and the
    # laboratory's sanctum extras are left out.
    [cask] = keep.possessions
    assert (cask.location_kind, cask.location_id) == ("covenant", keep.id)
    assert keep.boons_hooks[0].vf_id == target.custom_boons_hooks[0].id

    everyone = _roundtrip(source, covenant, with_members=True)
    target = Saga(id="dst", name="Target Saga")
    plan = transfer.plan_import(target, everyone)
    assert plan.dropped == [] and plan.matched == []
    transfer.apply(target, plan)
    assert [c.name for c in target.characters] == ["Leandro", "Flavia", "Hugo"]
    keep, lab = target.covenants[0], target.laboratories[0]
    leandro = target.characters[0]
    assert (lab.covenant_id, lab.owner_id) == (keep.id, leandro.id)
    assert leandro.assigned_lab_id == lab.id
    assert keep.inhabitants[0].character_id == target.characters[2].id
    cask, sanctum = keep.possessions
    assert (cask.location_kind, cask.location_id) == ("laboratory", lab.id)
    assert sanctum.lab_id == lab.id
    assert len(target.books) == 3 and len(target.familiars) == 1
    assert target.enchanted_devices[0].maker_id == target.characters[1].id


def test_charter_seals_follow_their_magi_to_new_ids():
    source = _source()
    charter = source.covenants[0].charter_of_covenant
    charter.seals = [
        CharterSeal("leandro", 1220, "Spring"),
        CharterSeal("flavia", 1221),
    ]
    data = _roundtrip(source, source.covenants[0], with_members=True)
    # The target already has a Leandro and a Flavia under these ids, so
    # the imported magi are given new ones.
    target = Saga(
        id="dst",
        name="Target Saga",
        characters=[
            Character(id="leandro", name="Someone Else", type="magus"),
            Character(id="flavia", name="Another", type="magus"),
        ],
    )
    transfer.apply(target, transfer.plan_import(target, data))
    [keep] = target.covenants
    leandro, flavia = target.characters[2:4]
    assert "leandro" != leandro.id and "flavia" != flavia.id
    seals = keep.charter_of_covenant.seals
    assert [(s.character_id, s.year) for s in seals] == [
        (leandro.id, 1220),
        (flavia.id, 1221),
    ]


def test_a_seal_whose_magus_is_not_imported_is_dropped():
    source = _source()
    source.covenants[0].charter_of_covenant.seals = [
        CharterSeal("leandro", 1220),
        CharterSeal("flavia", 1221),
    ]
    data = _roundtrip(source, source.covenants[0])
    # Flavia is here by name, Leandro isn't.
    target = Saga(
        id="dst",
        name="Target Saga",
        characters=[Character(id="flav", name="Flavia", type="magus")],
    )
    plan = transfer.plan_import(target, data)
    assert "Character Leandro: not in this saga" in plan.dropped
    transfer.apply(target, plan)
    [keep] = target.covenants
    assert [s.character_id for s in keep.charter_of_covenant.seals] == ["flav"]


def test_an_export_file_is_written_and_read_back(tmp_path):
    source = _source()
    magus = source.character("leandro")
    assert transfer.default_file_name(magus) == "leandro.amm.json"
    path = transfer.export_to(tmp_path / "exports" / "leandro.amm.json", source, magus)
    data = transfer.read(path)
    assert data["name"] == "Leandro"
    # An older export (fields added since are missing) still imports.
    for book in data["saga"]["books"]:
        del book["text_kind"]
    for character in data["saga"]["characters"]:
        character["lab_text_access"] = {"Flavia": 20}
    plan = transfer.plan_import(_target(), data)
    assert plan.books[0].text_kind == "Spell"
    assert plan.characters[0].lab_text_access == {"Flavia": LabTextAccess(20)}


def test_exports_made_before_the_rename_are_read(tmp_path):
    data = _roundtrip(_source(), _source().character("leandro"))
    assert data["format"] == "armarius-export"
    data["format"] = "ars-magica-manager-export"
    old = tmp_path / "leandro.amm.json"
    old.write_text(json.dumps(data), "utf-8")
    assert transfer.read(old)["name"] == "Leandro"


def test_only_export_files_are_read(tmp_path):
    other = tmp_path / "saga.json"
    other.write_text(json.dumps({"id": "x", "name": "A saga"}), "utf-8")
    with pytest.raises(ValueError, match="not an Armarius export"):
        transfer.read(other)
    other.write_text("not json", "utf-8")
    with pytest.raises(ValueError, match="not a JSON file"):
        transfer.read(other)


def _node(tree, data):
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


async def test_x_exports_a_character_and_the_saga_imports_it():  # noqa: PLR0915
    from support import wait_until
    from textual.widgets import Input, Static, Tree

    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens import (
        ConfirmScreen,
        CsvFilePickerScreen,
        FieldsDialog,
        WorkspaceScreen,
    )

    source = _source()
    source.id = "test_saga"
    storage.save_saga(source)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        tree = workspace.query_one("#nav-tree", Tree)
        # Nothing to export on the saga itself.
        assert not workspace.check_action("export_record", ())
        assert await wait_until(
            pilot, lambda: _node(tree, ("character", "leandro")) is not None
        )
        tree.select_node(_node(tree, ("character", "leandro")))
        assert await wait_until(
            pilot, lambda: workspace._character_sheet_view is not None
        )
        assert workspace.check_action("export_record", ())
        await menu(pilot, app, "m", "Export")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-file")))
        dialog = app.screen
        region = dialog.query_one("#fields-dialog").region
        assert region.bottom <= 45 and region.right <= 120
        box = dialog.query_one("#fld-file", Input)
        # Offered in the exports folder, named for the character.
        target = storage.exports_dir() / "leandro.amm.json"
        assert box.value == str(target)
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: target.is_file())
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert transfer.read(target)["name"] == "Leandro"

        # 'I' on the saga imports it back, as a second Leandro.
        tree.select_node(tree.root)
        assert await wait_until(pilot, lambda: workspace.selected_kind.value == "saga")
        await menu(pilot, app, "m", "Import")
        # One entry per kind: a character's file isn't taken as a covenant.
        await choose(pilot, app, "Covenants")
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, CsvFilePickerScreen)
        )
        wrong = app.screen.query_one("#picker-path", Input)
        wrong.value = str(target)
        wrong.focus()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert len(storage.load_saga("test_saga").characters) == 3
        await menu(pilot, app, "m", "Import")
        await choose(pilot, app, "Characters")
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, CsvFilePickerScreen)
        )
        picker = app.screen
        # The explorer opens in the exports folder, showing .json files.
        assert picker.query_one("#picker-path", Input).value == str(
            storage.exports_dir()
        )
        path_box = picker.query_one("#picker-path", Input)
        path_box.value = str(target)
        path_box.focus()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one(Static).render())
        assert "Import Character: Leandro" in message
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                [c.name for c in storage.load_saga("test_saga").characters].count(
                    "Leandro"
                )
                == 2
            ),
        )
        assert await wait_until(pilot, lambda: app.screen is workspace)
        labels = []
        pending = [tree.root]
        while pending:
            node = pending.pop()
            labels.append(str(node.label))
            pending.extend(node.children)
        assert sum(1 for label in labels if label.startswith("Leandro")) == 2


def test_a_whole_saga_exports_and_imports_every_record(tmp_path):
    source = _source()
    path = transfer.export_saga_to(tmp_path / "all.amm.json", source)
    data = transfer.read(path)
    assert data["kind"] == transfer.SAGA and data["name"] == "Source Saga"
    target = Saga(id="dst", name="Target")
    plan = transfer.plan_import(target, data)
    assert transfer.preview(plan).startswith("Import Saga: Source Saga")
    transfer.apply(target, plan)
    assert [c.name for c in target.characters] == ["Leandro", "Flavia", "Hugo"]
    assert [c.name for c in target.covenants] == ["Keep"]
    assert target.laboratory(target.characters[0].assigned_lab_id) is not None
    assert len(target.books) == len(source.books)
    assert len(target.familiars) == len(source.familiars)


def test_import_names_the_entry_a_wrong_file_belongs_under(tmp_path):
    from ars_magica_manager.commands import Refuse
    from ars_magica_manager.forms import importing as import_forms

    saga = _source()
    path = transfer.export_saga_to(tmp_path / "all.amm.json", saga)
    refused = import_forms.import_file(saga, "characters", path)
    assert isinstance(refused, Refuse)
    assert "choose A Whole Saga in the Import list" in refused.why


async def test_the_terminal_exports_the_saga_from_more():
    from support import wait_until
    from textual.widgets import Tree

    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens import FieldsDialog, WorkspaceScreen

    source = _source()
    source.id = "test_saga"
    storage.save_saga(source)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        tree = workspace.query_one("#nav-tree", Tree)
        tree.select_node(tree.root)
        assert await wait_until(pilot, lambda: workspace.selected_kind.value == "saga")
        await menu(pilot, app, "m", "Export Saga")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#btn-save")))
        app.screen.query_one("#btn-save").press()
        target = storage.exports_dir() / "source_saga.amm.json"
        assert await wait_until(pilot, lambda: target.is_file())
        assert transfer.read(target)["kind"] == transfer.SAGA


def test_a_laboratory_s_magic_items_follow_its_device_to_its_new_id():
    source = _source()
    lab = source.laboratory("tower")
    source.enchanted_devices.append(
        EnchantedDevice(
            "lectern",
            "Lectern",
            holder_kind="laboratory",
            holder_id="tower",
            effects=[InstilledEffect(id="e1", name="Steady", level=20)],
        )
    )
    lab.virtues_flaws.append(
        VirtueFlawInstance("labvf_magic_item", {"device": "lectern"}, id="host")
    )
    lab.item_benefits = [
        LabItemBenefit(
            "b1",
            "lectern",
            "e1",
            virtue_id="host",
            name="Lectern",
            specializations=[LabSpecialtyGrant("Texts", 2)],
        )
    ]
    data = _roundtrip(source, lab)
    target = _target()
    # A device here already has that id: the imported one gets another.
    target.enchanted_devices.append(EnchantedDevice("lectern", "Old Lectern"))
    transfer.apply(target, transfer.plan_import(target, data))
    [imported] = [d for d in target.enchanted_devices if d.name == "Lectern"]
    assert imported.id != "lectern"
    [new_lab] = target.laboratories
    assert new_lab.item_benefits[0].device_id == imported.id
    host = next(vf for vf in new_lab.virtues_flaws if vf.vf_id == "labvf_magic_item")
    assert host.params["device"] == imported.id
