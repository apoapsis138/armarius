"""The packs' maps and base pins, as they were placed on the desktop.

Each pack's are a file, data/packs/atlas/<pack key>.json, written by
tools/pack_pins.py from a saga in which the pins were placed by clicking
(Place on Map), never typed: a map's name, its Tribunal's name (none for
a region's own map), its picture (a file in data/packs/maps/, or none for
a placeholder in its shape), its credit and scale, and each pin as its
record's kind and name with its place on the map. `chart` adds them once
a pack is assembled, through the Builder's map and pin steps; a pin
naming a record the pack doesn't hold stops the build, as a stale row in
waters.py does. A pack with no file has no maps.

    {"maps": [{"name": "The Rhine", "tribunal": "The Rhine Tribunal",
               "picture": "", "width": 3, "height": 2, "credit": "",
               "scale_bar": [], "scale_miles": 0,
               "pins": [{"kind": "covenants", "name": "Durenmar",
                         "x": 0.72, "y": 0.68}]}]}
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .. import DATA_DIR, atlas, transfer
from ..files import write_atomic
from ..models import AtlasMap, Covenant, Creature, Neighbour, Saga
from .builder import Builder

#: Where each pack's maps and pins are kept, and the pictures they name.
ATLAS_DIR = DATA_DIR / "packs" / "atlas"
MAPS_DIR = DATA_DIR / "packs" / transfer.MAPS


def path_of(key: str, folder: Path = ATLAS_DIR) -> Path:
    return folder / f"{key}.json"


def read(key: str, folder: Path = ATLAS_DIR) -> list[dict[str, Any]]:
    """The pack's maps, with their pins; none when it has no file."""
    path = path_of(key, folder)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    found = data.get("maps") if isinstance(data, dict) else None
    if not isinstance(found, list):
        raise ValueError(f"{path.name} should hold a list of maps.")
    return found


def _record(b: Builder, kind: str, name: str) -> Covenant | Neighbour | Creature:
    held: dict[str, list[Covenant] | list[Neighbour] | list[Creature]] = {
        "covenants": b.saga.covenants,
        "neighbours": b.saga.neighbours,
        "creatures": b.saga.creatures,
    }
    for record in held.get(kind, []):
        if record.name == name:
            return record
    raise ValueError(f"No {kind[:-1]} named {name!r} in this pack.")


def chart(key: str, b: Builder, folder: Path = ATLAS_DIR) -> None:
    """Add the pack `key`'s maps and base pins to its assembled saga."""
    for entry in read(key, folder):
        tribunal_name = entry.get("tribunal")
        tribunal = next((t for t in b.saga.tribunals if t.name == tribunal_name), None)
        if tribunal_name and tribunal is None:
            raise ValueError(f"No Tribunal named {tribunal_name!r} in this pack.")
        atlas_map = b.atlas_map(
            str(entry["name"]),
            tribunal=tribunal,
            picture=str(entry.get("picture") or ""),
            width=int(entry.get("width") or 3),
            height=int(entry.get("height") or 2),
            credit=str(entry.get("credit") or ""),
            scale_bar=[float(n) for n in entry.get("scale_bar") or []],
            scale_miles=float(entry.get("scale_miles") or 0),
        )
        for pin in entry.get("pins") or []:
            record = _record(b, str(pin["kind"]), str(pin["name"]))
            b.pin(atlas_map, record, (float(pin["x"]), float(pin["y"])))


# -- writing them from a saga --


def pack_records(data: dict[str, Any]) -> set[tuple[str, str]]:
    """The records a built pack (its file's data) holds that can have a
    pin, as (kind, name)."""
    saga = data.get("saga") or {}
    return {
        (kind, str(record.get("name")))
        for kind in atlas.PIN_KINDS
        for record in saga.get(kind) or []
    }


def from_saga(
    saga: Saga,
    chosen: list[AtlasMap],
    *,
    pictures: bool = False,
    held: set[tuple[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """The pack file's maps from `chosen` maps of `saga`: each with the
    pins placed on it, by their records' names, only those of records
    `held` (pack_records) when it is given, so the troupe's own records
    stay out of the pack. With `pictures`, each map's picture is copied
    into MAPS_DIR to ship with the packs (its licence and NOTICE.md
    credit are the author's to add); without, the pack shows a
    placeholder in the map's shape."""
    entries: list[dict[str, Any]] = []
    for atlas_map in chosen:
        on = atlas.find_map(saga, atlas_map.id)
        tribunal = on[1] if on is not None else None
        found = atlas.picture_path(atlas_map) if pictures else None
        if found is not None:
            MAPS_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(found, MAPS_DIR / found.name)
        placed = []
        for pin in saga.pins:
            if pin.map_id != atlas_map.id or pin.hidden:
                continue
            record = atlas.record(saga, pin.kind, pin.record_id)
            if record is None or pin.kind not in atlas.PIN_KINDS:
                continue
            if held is not None and (pin.kind, record.name) not in held:
                continue
            placed.append(
                {"kind": pin.kind, "name": record.name, "x": pin.x, "y": pin.y}
            )
        entries.append(
            {
                "name": atlas_map.name,
                "tribunal": tribunal.name if tribunal is not None else None,
                "picture": found.name if found is not None else "",
                "width": atlas_map.width or atlas.PLACEHOLDER_SHAPE[0],
                "height": atlas_map.height or atlas.PLACEHOLDER_SHAPE[1],
                "credit": atlas_map.credit,
                "scale_bar": atlas_map.scale_bar,
                "scale_miles": atlas_map.scale_miles,
                "pins": sorted(placed, key=lambda p: (p["kind"], p["name"])),
            }
        )
    return entries


def write(key: str, entries: list[dict[str, Any]], folder: Path = ATLAS_DIR) -> Path:
    """Write the pack `key`'s maps and pins (from_saga) to its file."""
    folder.mkdir(parents=True, exist_ok=True)
    path = path_of(key, folder)
    write_atomic(path, json.dumps({"maps": entries}, indent=2) + "\n")
    return path
