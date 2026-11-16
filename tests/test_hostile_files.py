"""Files made to harm a saga or the computer (the import security fixes,
FEAT-26): each is refused, names what is wrong and changes nothing."""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest
from support import everything_saga

from ars_magica_manager import books, creation, portraits, shapes, storage, transfer
from ars_magica_manager.models import Character, Covenant, Laboratory, LabProject, Saga


def _data() -> dict:
    return json.loads(json.dumps(asdict(everything_saga())))


def _write(name: str, data: dict) -> str:
    """A saga file named `name` in the sagas folder holding `data`; its text."""
    storage.sagas_dir().mkdir(parents=True, exist_ok=True)
    text = json.dumps(data)
    storage.saga_path(name).write_text(text, encoding="utf-8")
    return text


def _refused_on_open(name: str) -> str:
    with pytest.raises(ValueError) as refused:
        storage.load_saga(name)
    return str(refused.value)


def test_a_saga_file_whose_saga_id_climbs_out_of_the_folder_is_refused():
    data = _data()
    data["id"] = "../../escaped"
    text = _write("hostile", data)
    assert _refused_on_open("hostile") == "id: not a plain id"
    assert storage.saga_path("hostile").read_text(encoding="utf-8") == text


def test_a_saga_file_with_a_hostile_character_id_is_refused_by_its_field():
    data = _data()
    data["characters"][0]["id"] = "..\\portraits\\x"
    _write("hostile", data)
    assert _refused_on_open("hostile").endswith(".id: not a plain id")
    assert _refused_on_open("hostile").startswith("characters[")


def test_a_hostile_link_is_refused_too():
    data = _data()
    character = data["characters"][0]
    character["covenant_id"] = "../covenant"
    _write("hostile", data)
    assert _refused_on_open("hostile").endswith(".covenant_id: not a plain id")


@pytest.mark.parametrize(
    "wanted", ["ash_wand_of_ingrid-1", "session-1a2b3c4d", "mag1", "a" * 200]
)
def test_plain_ids_open(wanted: str):
    data = _data()
    data["characters"][0]["id"] = wanted
    _write("plain", data)
    assert storage.load_saga("plain").characters[0].id == wanted


@pytest.mark.parametrize(
    "wanted", ["Mag1", "-mag", "_mag", "mag 1", "mag.1", "a" * 201, "mág"]
)
def test_ids_that_are_not_plain_names_are_refused(wanted: str):
    data = _data()
    data["characters"][0]["id"] = wanted
    _write("odd", data)
    assert _refused_on_open("odd").endswith(".id: not a plain id")


def test_over_the_network_a_hostile_id_is_refused_as_well():
    data = _data()
    data["id"] = "../x"
    with pytest.raises(ValueError, match="not a plain id"):
        storage.saga_from_data(data, strict=True)


# -- an id never names a file outside its folder (STORY-2330) -----------------


@pytest.mark.parametrize("saga_id", ["../escaped", "../../escaped", "/tmp/escaped"])
def test_a_saga_id_that_would_leave_the_sagas_folder_names_no_file(saga_id: str):
    for named in (storage.saga_path, storage.backup_path, storage.after_path):
        with pytest.raises(ValueError, match="outside the sagas folder"):
            named(saga_id)
    with pytest.raises(ValueError, match="outside the sagas folder"):
        storage.undone_path(saga_id)


def test_a_saga_built_in_memory_with_a_hostile_id_is_never_saved():
    saga = everything_saga()
    saga.id = "../escaped"
    with pytest.raises(ValueError, match="outside the sagas folder"):
        storage.save_saga(saga)
    assert not (storage.sagas_dir().parent / "escaped.json").exists()


def test_a_portrait_is_never_named_outside_the_portraits_folder(tmp_path):
    saga = everything_saga()
    character = saga.characters[0]
    character.id = "../../escaped"
    picture = tmp_path / "face.png"
    picture.write_bytes(b"not really a png")
    with pytest.raises(ValueError, match="outside the portraits folder"):
        portraits.set_portrait(saga, character, picture)
    assert character.portrait == ""
    assert not any(storage.portraits_dir().parent.rglob("*escaped*"))


# -- an import re-ids what isn't plain (STORY-2331) ----------------------------


def test_an_export_with_hostile_ids_comes_in_with_fresh_ones_and_its_links(tmp_path):
    keep = Covenant(id="../keep", saga_id="src", name="Keep")
    magus = Character(
        id="../../Leandro", name="Leandro", type="magus", covenant_id="../keep"
    )
    lab = Laboratory(
        id="tower", covenant_id="../keep", name="Tower", owner_id="../../Leandro"
    )
    magus.assigned_lab_id = "tower"
    source = Saga(
        id="src",
        name="Source",
        covenants=[keep],
        characters=[magus],
        laboratories=[lab],
    )
    path = transfer.export_to(
        tmp_path / "keep.amm.json", source, keep, with_members=True
    )
    data = transfer.read(path)
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, data))
    [covenant], [character], [laboratory] = (
        target.covenants,
        target.characters,
        target.laboratories,
    )
    assert all(
        shapes.is_plain_id(found)
        for found in (covenant.id, character.id, laboratory.id)
    )
    assert character.covenant_id == covenant.id
    assert (laboratory.covenant_id, laboratory.owner_id) == (covenant.id, character.id)
    assert character.assigned_lab_id == laboratory.id
    # And the saga, with them in it, saves and opens again.
    storage.save_saga(target)
    assert storage.load_saga("dst").characters[0].id == character.id


def test_an_export_with_a_hostile_id_inside_a_record_is_refused(tmp_path):
    source = everything_saga()
    character = source.characters[0]
    path = transfer.export_to(tmp_path / "one.amm.json", source, character)
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    held = data["saga"]["characters"][0]
    held["inventory"] = [{"id": "../../x", "kind": "weapon", "name": "Knife"}]
    path.write_text(json.dumps(data), encoding="utf-8")
    target = Saga(id="dst", name="Target")
    with pytest.raises(
        ValueError, match=r"inventory\[\.\./\.\./x\]\.id: not a plain id"
    ):
        transfer.plan_import(target, transfer.read(path))
    assert target.characters == []


# -- what the app makes itself always opens again (review of PR 1) -------------


def test_a_saga_with_lab_work_under_way_saves_and_opens_again():
    saga = everything_saga()
    magus = saga.characters[0]
    saga.lab_projects = [
        LabProject(magus.id, "design:ab12cd34ef56", 7),
        LabProject(magus.id, f"decode:{magus.id}:Old Jacobus of Tytalus", 4),
        LabProject(magus.id, "taming:The Grey Wolf of Rabenstein", 3),
        LabProject(magus.id, "effect:0f1e2d3c4b5a", 2),
    ]
    storage.save_saga(saga)
    opened = storage.load_saga(saga.id)
    assert [p.spell_id for p in opened.lab_projects] == [
        p.spell_id for p in saga.lab_projects
    ]


def test_a_saga_and_records_with_very_long_names_save_and_open_again():
    name = "The Most Exceedingly Long and Wordy Name " * 6
    saga = creation.new_saga(name, "Storyguide", "", 1220, "Spring")
    covenant = creation.add_covenant(saga, name)
    character = creation.add_character(saga, name, "magus", covenant.id)
    book = books.add_book(saga, name, "Summa")
    assert all(
        shapes.is_plain_id(found)
        for found in (saga.id, covenant.id, character.id, book.id)
    )
    storage.save_saga(saga)
    assert storage.load_saga(saga.id).characters[0].id == character.id


def test_ids_the_app_builds_from_a_long_character_id_stay_plain():
    name = "Aurelianus Maximus Constantinus of the Tower by the Black Lake " * 3
    saga = creation.new_saga("Lake", "Storyguide", "", 1220, "Spring")
    magus = creation.add_character(saga, name, "magus", None)
    built = f"labtext_longevity_{magus.id}_{'0f1e2d3c4b5a'}"
    assert shapes.is_plain_id(built)


def test_a_hosted_saga_brought_in_under_the_old_admin_rule_still_opens():
    data = _data()
    data["id"] = "MySaga"
    _write("MySaga", data)
    assert storage.load_saga("MySaga").id == "MySaga"


def test_a_record_id_with_capitals_is_still_refused():
    data = _data()
    data["characters"][0]["id"] = "MySaga"
    _write("odd", data)
    assert _refused_on_open("odd").endswith(".id: not a plain id")
