"""Exports that carry pictures (transfer.py): a zip of the export's JSON
with its maps and portraits, read back by the same importer, its pictures
copied into another computer's folders, and a shipped pack's maps read
from beside it."""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import pytest

from ars_magica_manager import atlas, paths, portraits, storage, transfer
from ars_magica_manager.models import Character, Saga, Tribunal


def _picture(tmp_path: Path, name: str, data: bytes) -> Path:
    found = tmp_path / name
    found.write_bytes(data)
    return found


# A real PNG header is all store_picture reads: 4 by 2 pixels.
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x04\x00\x00\x00\x02"
    + b"\x08\x02\x00\x00\x00"
    + b"rest of the picture"
)


def _saga(tmp_path: Path) -> Saga:
    """A Tribunal with a map, and a character with a portrait."""
    saga = Saga(
        "home",
        "Home",
        tribunals=[Tribunal("rhine", "The Rhine")],
        characters=[Character("leandro", "Leandro", "Magus")],
    )
    name, width, height = atlas.store_picture(_picture(tmp_path, "rhine.png", PNG))
    atlas.add_map(saga, "The Rhine", "rhine", picture=name, width=width, height=height)
    portraits.set_portrait(
        saga, saga.characters[0], _picture(tmp_path, "face.jpg", b"a face")
    )
    return saga


def _other_computer(tmp_path: Path) -> Path:
    """Use a fresh data folder, with none of the first one's pictures."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    paths.use_data_dir(elsewhere)
    return elsewhere


def test_a_whole_saga_with_pictures_is_written_as_a_zip(tmp_path):
    saga = _saga(tmp_path)
    written = transfer.export_saga_to(tmp_path / "out" / "home.amm.json", saga)
    assert written.name == "home.amm.zip"
    with zipfile.ZipFile(written) as archive:
        names = sorted(archive.namelist())
    map_name = saga.tribunals[0].maps[0].picture
    assert names == [
        "home.amm.json",
        f"maps/{map_name}",
        "portraits/home--leandro.jpg",
    ]
    assert transfer.read(written)["kind"] == transfer.SAGA


def test_an_export_with_no_pictures_stays_a_json_file(tmp_path):
    saga = Saga("bare", "Bare", characters=[Character("c", "Cara", "Companion")])
    written = transfer.export_to(tmp_path / "cara.amm.json", saga, saga.characters[0])
    assert written == tmp_path / "cara.amm.json"
    assert json.loads(written.read_text(encoding="utf-8"))["kind"] == "character"


def test_importing_the_zip_elsewhere_copies_its_map_and_portrait(tmp_path):
    saga = _saga(tmp_path)
    written = transfer.export_saga_to(tmp_path / "home.amm.json", saga)
    _other_computer(tmp_path)
    target = Saga("away", "Away", tribunals=[Tribunal("t", "Elsewhere")])
    atlas.add_map(target, "The Rhine", "t")
    plan = transfer.plan_import(
        target, transfer.read(written), pictures=transfer.Pictures(written)
    )
    transfer.apply(target, plan)
    [rhine] = [t for t in target.tribunals if t.name == "The Rhine"]
    [imported] = rhine.maps
    # The target already had a map of that id: the import's gets another.
    assert imported.id != target.tribunals[0].maps[0].id
    assert atlas.picture_path(imported) is not None
    assert atlas.picture_path(imported).read_bytes() == PNG  # type: ignore[union-attr]
    [leandro] = [c for c in target.characters if c.name == "Leandro"]
    assert leandro.portrait == f"away--{leandro.id}.jpg"
    found = portraits.path(leandro)
    assert found is not None and found.read_bytes() == b"a face"


def test_a_character_export_carries_its_portrait(tmp_path):
    saga = _saga(tmp_path)
    written = transfer.export_to(
        tmp_path / "leandro.amm.json", saga, saga.characters[0]
    )
    assert written.suffix == ".zip"
    _other_computer(tmp_path)
    target = Saga("away", "Away")
    transfer.apply(
        target,
        transfer.plan_import(
            target, transfer.read(written), pictures=transfer.Pictures(written)
        ),
    )
    assert portraits.path(target.characters[0]) is not None


def test_a_map_already_here_is_kept_and_a_picture_not_carried_is_left_named(tmp_path):
    saga = _saga(tmp_path)
    data = transfer.export_saga_data(saga)
    # Not beside the data folder, whose portraits would be read as its own.
    (tmp_path / "out").mkdir()
    plain = tmp_path / "out" / "plain.amm.json"
    plain.write_text(json.dumps(data), encoding="utf-8")
    target = Saga("same", "Same computer")
    transfer.apply(
        target, transfer.plan_import(target, data, pictures=transfer.Pictures(plain))
    )
    # This computer has the map, so it shows; the portrait keeps its name.
    assert atlas.picture_path(target.tribunals[0].maps[0]) is not None
    assert target.characters[0].portrait == "home--leandro.jpg"


def test_a_shipped_packs_maps_are_read_from_beside_it(tmp_path):
    folder = tmp_path / "packs"
    (folder / transfer.MAPS).mkdir(parents=True)
    (folder / transfer.MAPS / "abc.png").write_bytes(PNG)
    pictures = transfer.Pictures(folder / "rhine.amm.json")
    assert pictures.get(transfer.MAPS, "abc.png") == PNG
    assert pictures.get(transfer.MAPS, "missing.png") is None
    assert pictures.get(transfer.MAPS, "../abc.png") is None


def test_a_zip_that_isnt_one_export_is_refused(tmp_path):
    two = tmp_path / "two.amm.zip"
    with zipfile.ZipFile(two, "w") as archive:
        archive.writestr("a.amm.json", "{}")
        archive.writestr("b.amm.json", "{}")
    with pytest.raises(ValueError, match="one export's JSON file"):
        transfer.read(two)
    broken = tmp_path / "broken.amm.zip"
    shutil.copyfile(two, broken)
    with broken.open("r+b") as handle:
        handle.truncate(30)
    with pytest.raises(ValueError):
        transfer.read(broken)


def test_storage_folders_are_asked_each_time(tmp_path):
    first = storage.maps_dir()
    _other_computer(tmp_path)
    assert storage.maps_dir() != first
