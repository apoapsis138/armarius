"""Files made to harm a saga or the computer (the import security fixes,
FEAT-26): each is refused, names what is wrong and changes nothing."""

from __future__ import annotations

import json
import zipfile
from dataclasses import asdict

import pytest
from admin_support import refused
from support import everything_saga

from ars_magica_manager import (
    books,
    creation,
    cult_transfer,
    incoming,
    packs,
    portraits,
    shapes,
    storage,
    transfer,
)
from ars_magica_manager.models import (
    Character,
    Covenant,
    Laboratory,
    LabProject,
    MysteryCult,
    Saga,
)


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


# -- a supplement overlay touches only what it may (STORY-2332) ----------------


def _provence_with_overlay() -> tuple[Saga, dict, dict]:
    """A saga started from the Provence pack, the shipped Through the Aegis
    overlay, and that overlay's Provence section (its changes to edit)."""
    saga = Saga(id="dst", name="Target")
    packs.start_from(saga, packs.SHIPPED_DIR / "provence.amm.json")
    overlay = transfer.read(packs.SHIPPED_DIR / "through_the_aegis.amm.json")
    section = next(s for s in overlay["overlay"] if "Proven" in s["tribunal"])
    return saga, overlay, section


@pytest.mark.parametrize(
    ("change", "refusal"),
    [
        ({"list": "players"}, "list: not a list an overlay can change"),
        ({"field": "no_such_field"}, "field: not a field of Tribunal"),
        ({"field": "id", "value": "../x"}, "field: not a field an overlay can change"),
        ({"value": {"a": "record"}}, "value: covenants_total: expected a single value"),
    ],
)
def test_an_overlay_change_it_may_not_make_is_refused_and_nothing_changes(
    change: dict, refusal: str
):
    saga, overlay, section = _provence_with_overlay()
    section["changes"][0].update(change)
    before = asdict(saga)
    with pytest.raises(ValueError, match=refusal):
        packs.apply_overlay(saga, overlay)
    assert asdict(saga) == before


def test_an_overlay_link_that_is_not_a_plain_id_is_refused():
    saga, overlay, section = _provence_with_overlay()
    section["changes"].append(
        {
            "list": "covenants",
            "name": saga.covenants[0].name,
            "kind": "",
            "field": "tribunal_id",
            "was": None,
            "value": "../x",
        }
    )
    before = asdict(saga)
    with pytest.raises(ValueError, match="tribunal_id: not a plain id"):
        packs.apply_overlay(saga, overlay)
    assert asdict(saga) == before


def test_an_overlay_pack_of_the_wrong_shape_is_refused_before_anything_is_added():
    saga, overlay, section = _provence_with_overlay()
    section["pack"]["saga"]["covenants"] = {"not": "a list"}
    before = asdict(saga)
    with pytest.raises(ValueError, match="covenants: expected a list"):
        packs.apply_overlay(saga, overlay)
    assert asdict(saga) == before


def test_a_sound_overlay_still_applies():
    saga, overlay, _ = _provence_with_overlay()
    packs.apply_overlay(saga, overlay)
    assert "Jardin" in {c.name for c in saga.covenants}


# -- a Mystery Cult file is shape-checked (STORY-2333) -------------------------


def _cult_file(tmp_path, change) -> object:
    saga = everything_saga()
    cult = MysteryCult(
        id="custom_cult_flame", name="The Hidden Flame", lore="Flame Lore"
    )
    path = cult_transfer.export_to(tmp_path / "flame.cult.json", cult)
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data["cult"])
    path.write_text(json.dumps(data), encoding="utf-8")
    return saga, path


@pytest.mark.parametrize(
    ("change", "refusal"),
    [
        (lambda c: c.update(degrees={"not": "a list"}), "degrees: expected a list"),
        (lambda c: c.update(name=["a", "list"]), "name: expected a single value"),
        (lambda c: c.pop("lore"), "lore: missing"),
    ],
)
def test_a_cult_file_of_the_wrong_shape_is_refused_by_its_field(
    tmp_path, change, refusal
):
    _, path = _cult_file(tmp_path, change)
    with pytest.raises(ValueError, match=refusal):
        cult_transfer.read(path)


def test_a_sound_cult_file_still_imports_with_an_id_of_its_own(tmp_path):
    saga, path = _cult_file(
        tmp_path, lambda c: c.update(id="custom_cult_../x", founder_id="../y")
    )
    cult = cult_transfer.add(saga, cult_transfer.read(path))
    assert shapes.is_plain_id(cult.id) and cult.founder_id == ""
    storage.save_saga(saga)
    assert storage.load_saga(saga.id).custom_cults[-1].id == cult.id


# -- a saga of the wrong shape is never saved (STORY-2334) ---------------------


def _saved() -> tuple[Saga, bytes]:
    saga = everything_saga()
    storage.save_saga(saga)
    return saga, storage.saga_path(saga.id).read_bytes()


def test_a_saga_holding_a_value_of_the_wrong_type_is_not_saved():
    saga, before = _saved()
    saga.characters[0].name = 5  # type: ignore[assignment]
    with pytest.raises(ValueError, match=r"characters\[.+\]\.name"):
        storage.save_saga(saga)
    assert storage.saga_path(saga.id).read_bytes() == before


def test_a_saga_holding_an_id_that_is_not_plain_is_not_saved():
    saga, before = _saved()
    saga.characters[0].covenant_id = "../x"
    with pytest.raises(ValueError, match=r"covenant_id: not a plain id"):
        storage.save_saga(saga)
    assert storage.saga_path(saga.id).read_bytes() == before
    # Put right, it saves.
    saga.characters[0].covenant_id = None
    storage.save_saga(saga)
    assert storage.load_saga(saga.id).characters[0].covenant_id is None


def test_a_refused_save_is_said_with_its_field_and_the_file_unchanged():
    saga, _ = _saved()
    saga.characters[0].covenant_id = "../x"
    with pytest.raises(ValueError) as refused:
        storage.save_saga(saga)
    assert storage.not_saved_note(refused.value) == (
        f"Not saved: characters[{saga.characters[0].id}].covenant_id: not a plain id. "
        "The file is unchanged."
    )


# -- from the review of PR 2 ---------------------------------------------------


def test_an_overlay_section_pack_that_cannot_be_planned_changes_nothing():
    saga, overlay, section = _provence_with_overlay()
    del section["pack"]["kind"]
    before = asdict(saga)
    with pytest.raises(ValueError, match=r"overlay\[\d+\]\.pack"):
        packs.apply_overlay(saga, overlay)
    assert asdict(saga) == before


def test_a_pack_whose_overlay_key_is_not_a_list_is_still_shape_checked(tmp_path):
    data = transfer.export_saga_data(Saga(id="src", name="Source"))
    data["overlay"] = {}
    data["saga"]["covenants"] = {"not": "a list"}
    path = tmp_path / "odd.amm.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="covenants: expected a list"):
        transfer.read(path)


def test_a_refused_save_leaves_the_saga_as_it_was_in_hand():
    saga, _ = _saved()
    saga.saved_by = "Before"
    saga.characters[0].covenant_id = "../x"
    with pytest.raises(ValueError):
        storage.save_saga(saga, storage.Saver("After"))
    assert saga.saved_by == "Before"


# -- files coming in are read within limits (STORY-2335) -----------------------


def _oversize(path, size: int) -> None:
    """A file of `size` bytes without writing them (sparse where it can be)."""
    with path.open("wb") as file:
        file.truncate(size)


def test_an_export_over_the_size_limit_is_refused_before_it_is_read(tmp_path):
    path = tmp_path / "huge.amm.json"
    _oversize(path, incoming.MAX_JSON + 1)
    with pytest.raises(ValueError, match="larger than 50 MB"):
        transfer.read(path)


def test_a_saga_file_over_the_size_limit_is_refused_on_open():
    storage.sagas_dir().mkdir(parents=True, exist_ok=True)
    _oversize(storage.saga_path("huge"), incoming.MAX_JSON + 1)
    with pytest.raises(ValueError, match="larger than 50 MB"):
        storage.load_saga("huge")


def test_a_zip_whose_json_would_unpack_past_the_limit_is_refused(tmp_path):
    path = tmp_path / "bomb.amm.json"
    with (
        zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive,
        archive.open("bomb.amm.json", "w", force_zip64=True) as member,
    ):
        block = b" " * (1024 * 1024)
        for _ in range(51):
            member.write(block)
    assert path.stat().st_size < 1024 * 1024  # small on disk
    with pytest.raises(ValueError, match="larger than 50 MB"):
        transfer.read(path)


#: JSON nested far deeper than Python's recursion limit.
DEEP = "[" * 100_000 + "]" * 100_000


def test_an_export_nested_too_deep_is_refused_not_crashed(tmp_path):
    path = tmp_path / "deep.amm.json"
    path.write_text(DEEP, encoding="utf-8")
    with pytest.raises(ValueError, match="nested too deeply"):
        transfer.read(path)


def test_a_saga_file_nested_too_deep_is_refused_not_crashed():
    storage.sagas_dir().mkdir(parents=True, exist_ok=True)
    storage.saga_path("deep").write_text(DEEP, encoding="utf-8")
    with pytest.raises(ValueError, match="nested too deeply"):
        storage.load_saga("deep")


def test_a_file_that_is_not_utf8_is_refused_as_such(tmp_path):
    path = tmp_path / "latin.amm.json"
    path.write_bytes(b'{"name": "\xe9"}')
    with pytest.raises(ValueError, match="not UTF-8 text"):
        transfer.read(path)


# -- pictures, cult files and the admin import too (STORY-2336) ----------------


def test_a_picture_over_the_limit_in_an_export_counts_as_missing(tmp_path):
    path = tmp_path / "home.amm.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("home.amm.json", "{}")
        archive.writestr("portraits/big.jpg", b"\0" * (incoming.MAX_PICTURE + 1))
        archive.writestr("portraits/face.jpg", b"a face")
    pictures = transfer.Pictures(path)
    assert pictures.get("portraits", "big.jpg") is None
    assert pictures.get("portraits", "face.jpg") == b"a face"


def test_a_picture_over_the_limit_beside_a_pack_counts_as_missing(tmp_path):
    pack = tmp_path / "pack.amm.json"
    pack.write_text("{}", encoding="utf-8")
    (tmp_path / "maps").mkdir()
    _oversize(tmp_path / "maps" / "big.png", incoming.MAX_PICTURE + 1)
    (tmp_path / "maps" / "small.png").write_bytes(b"a map")
    pictures = transfer.Pictures(pack)
    assert pictures.get("maps", "big.png") is None
    assert pictures.get("maps", "small.png") == b"a map"


def test_a_cult_file_over_the_limit_is_refused(tmp_path):
    path = tmp_path / "huge.cult.json"
    _oversize(path, incoming.MAX_JSON + 1)
    with pytest.raises(ValueError, match="larger than 50 MB"):
        cult_transfer.read(path)


def test_the_admin_s_saga_import_refuses_a_file_over_the_limit(tmp_path):
    path = tmp_path / "huge.json"
    _oversize(path, incoming.MAX_JSON + 1)
    assert "larger than 50 MB" in refused(["saga", "import", str(path)])
    assert storage.list_sagas() == []


# -- from the review of PR 3 ---------------------------------------------------


def test_a_saga_too_big_to_open_again_is_not_saved(monkeypatch):
    saga, before = _saved()
    monkeypatch.setattr(incoming, "MAX_JSON", len(before) + 10)
    saga.description = "x" * len(before)
    with pytest.raises(ValueError, match="larger than"):
        storage.save_saga(saga)
    assert storage.saga_path(saga.id).read_bytes() == before


def test_a_saga_file_that_cannot_be_read_is_not_written_over():
    saga, _ = _saved()
    storage.saga_path(saga.id).write_bytes(b'{"name": "\xe9"}')
    saga.description = "changed here"
    with pytest.raises(ValueError, match="not UTF-8"):
        storage.save_saga(saga)
    assert storage.saga_path(saga.id).read_bytes() == b'{"name": "\xe9"}'


def test_another_copy_s_unreadable_save_is_said_as_such():
    saga, _ = _saved()
    storage.saga_path(saga.id).write_bytes(b'{"name": "\xe9"}')
    with pytest.raises(ValueError, match="the saga file can't be read"):
        storage.reload_into(saga)
