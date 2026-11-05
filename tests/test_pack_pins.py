"""A pack's maps and base pins (book_packs/pins.py and transfer.py): read
from the pack's pins file into the Builder, carried in the pack, and
imported as the pack's own pins, never moving or doubling a pin the saga
already has; and written back from a saga where they were placed."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ars_magica_manager import atlas, packs, transfer
from ars_magica_manager.book_packs import pins
from ars_magica_manager.book_packs.builder import Builder
from ars_magica_manager.models import Covenant, Neighbour, Saga, Tribunal


def _pack_saga() -> Saga:
    saga = Saga(
        "pack",
        "Pack",
        tribunals=[Tribunal("rhine", "The Rhine Tribunal")],
        covenants=[Covenant("durenmar", "pack", "Durenmar", tribunal_id="rhine")],
        neighbours=[Neighbour("forest", "The Black Forest", kind="place")],
    )
    saga.covenants[0].place_id = "forest"
    return saga


def _pack(saga: Saga) -> dict:
    return packs.pack_data(saga, "The Rhine", saga.tribunals, [], [])


def _charted(tmp_path: Path) -> Saga:
    """A pack saga with its maps and pins added from a pins file."""
    pins.write(
        "rhine",
        [
            {
                "name": "The Rhine",
                "tribunal": "The Rhine Tribunal",
                "width": 4,
                "height": 3,
                "pins": [
                    {"kind": "covenants", "name": "Durenmar", "x": 0.7, "y": 0.6},
                    {
                        "kind": "neighbours",
                        "name": "The Black Forest",
                        "x": 0.5,
                        "y": 0.5,
                    },
                ],
            }
        ],
        tmp_path,
    )
    b = Builder.__new__(Builder)
    b.saga = _pack_saga()
    pins.chart("rhine", b, tmp_path)
    return b.saga


def test_a_pins_file_gives_the_pack_its_map_and_pins(tmp_path):
    saga = _charted(tmp_path)
    [rhine] = saga.tribunals[0].maps
    assert (rhine.name, rhine.width, rhine.height, rhine.picture) == (
        "The Rhine",
        4,
        3,
        "",
    )
    assert [(p.record_id, p.x, p.y, p.from_pack) for p in saga.pins] == [
        ("durenmar", 0.7, 0.6, True),
        ("forest", 0.5, 0.5, True),
    ]


def test_a_pin_naming_a_record_the_pack_lacks_stops_the_build(tmp_path):
    pins.write(
        "rhine",
        [
            {
                "name": "M",
                "tribunal": None,
                "pins": [{"kind": "covenants", "name": "Nowhere", "x": 0, "y": 0}],
            }
        ],
        tmp_path,
    )
    b = Builder.__new__(Builder)
    b.saga = _pack_saga()
    with pytest.raises(ValueError, match="No covenant named 'Nowhere'"):
        pins.chart("rhine", b, tmp_path)


def test_a_pack_has_no_maps_without_a_pins_file(tmp_path):
    assert pins.read("theban", tmp_path) == []


def test_a_packs_pins_travel_and_import_as_the_packs(tmp_path):
    data = _pack(_charted(tmp_path))
    assert len(data["saga"]["pins"]) == 2
    target = Saga("t", "Target")
    transfer.apply(target, transfer.plan_import(target, data))
    [rhine] = target.tribunals[0].maps
    shown = {s.ref.name: (s.x, s.y) for s in atlas.shown_pins(target, rhine.id)}
    assert shown == {"Durenmar": (0.7, 0.6), "The Black Forest": (0.5, 0.5)}
    assert all(p.from_pack for p in target.pins)


def test_importing_the_pack_again_never_moves_or_doubles_a_pin(tmp_path):
    data = _pack(_charted(tmp_path))
    target = Saga("t", "Target")
    transfer.apply(target, transfer.plan_import(target, data))
    [rhine] = target.tribunals[0].maps
    durenmar = next(p for p in target.pins if p.kind == "covenants")
    atlas.place_pin(target, rhine.id, "covenants", durenmar.record_id, 0.1, 0.1)
    forest = next(p for p in target.pins if p.kind == "neighbours")
    atlas.remove_pin(target, forest)
    transfer.apply(target, transfer.plan_import(target, data))
    assert len(target.tribunals) == 1 and len(target.tribunals[0].maps) == 1
    assert [(p.kind, p.x, p.y, p.hidden) for p in target.pins] == [
        ("covenants", 0.1, 0.1, False),
        ("neighbours", 0.5, 0.5, True),
    ]


def test_a_new_map_in_the_pack_joins_the_tribunal_already_here(tmp_path):
    first = _pack_saga()
    target = Saga("t", "Target")
    transfer.apply(target, transfer.plan_import(target, _pack(first)))
    assert target.tribunals[0].maps == []
    transfer.apply(target, transfer.plan_import(target, _pack(_charted(tmp_path))))
    [rhine] = target.tribunals[0].maps
    assert len([p for p in target.pins if p.map_id == rhine.id]) == 2


def test_pins_are_written_back_from_a_saga_by_their_records_names(tmp_path):
    saga = _pack_saga()
    rhine = atlas.add_map(saga, "The Rhine", "rhine", width=3, height=2)
    atlas.place_pin(saga, rhine.id, "covenants", "durenmar", 0.25, 0.75)
    saga.neighbours.append(Neighbour("mine", "Our Own Inn", kind="town"))
    atlas.place_pin(saga, rhine.id, "neighbours", "mine", 0.5, 0.5)
    held = pins.pack_records(_pack(_pack_saga()))
    entries = pins.from_saga(saga, [rhine], held=held)
    path = pins.write("rhine", entries, tmp_path)
    written = json.loads(path.read_text(encoding="utf-8"))
    [entry] = written["maps"]
    assert entry["tribunal"] == "The Rhine Tribunal"
    assert entry["picture"] == ""
    # The troupe's own inn stays out of the pack.
    assert entry["pins"] == [
        {"kind": "covenants", "name": "Durenmar", "x": 0.25, "y": 0.75}
    ]
