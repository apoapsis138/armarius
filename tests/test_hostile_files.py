"""Files made to harm a saga or the computer (the import security fixes,
FEAT-26): each is refused, names what is wrong and changes nothing."""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest
from support import everything_saga

from ars_magica_manager import portraits, storage


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
    "wanted", ["ash_wand_of_ingrid-1", "session-1a2b3c4d", "mag1", "a" * 100]
)
def test_plain_ids_open(wanted: str):
    data = _data()
    data["characters"][0]["id"] = wanted
    _write("plain", data)
    assert storage.load_saga("plain").characters[0].id == wanted


@pytest.mark.parametrize(
    "wanted", ["Mag1", "-mag", "_mag", "mag 1", "mag.1", "a" * 101, "mág"]
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
