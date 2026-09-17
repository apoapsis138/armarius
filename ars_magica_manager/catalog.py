"""Loads the shared Virtue/Flaw catalog (reference data, not per-saga)."""

from __future__ import annotations

import json
from pathlib import Path

from .models import VirtueFlawDef, VirtueFlawInstance

CATALOG_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "virtue_flaw_catalog.json"
)


def load_virtue_flaw_catalog(path: Path = CATALOG_PATH) -> list[VirtueFlawDef]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [VirtueFlawDef.from_dict(entry) for entry in data]


def load_virtue_flaw_catalog_by_id(
    path: Path = CATALOG_PATH,
) -> dict[str, VirtueFlawDef]:
    return {entry.id: entry for entry in load_virtue_flaw_catalog(path)}


def describe_virtue_flaw(
    instance: VirtueFlawInstance, catalog_by_id: dict[str, VirtueFlawDef]
) -> str:
    """A human-readable label for a Virtue/Flaw instance, params filled in.

    E.g. an instance of "vf_affinity_with_art" with params {"art": "creo"}
    becomes "Affinity with Creo" (the catalog name's "{art}" placeholder
    matches the entry's `parameters`).
    """
    definition = catalog_by_id.get(instance.vf_id)
    if definition is None:
        return f"{instance.vf_id} (not in catalog)"
    name = definition.name
    for key, value in instance.params.items():
        name = name.replace(f"{{{key}}}", value.title())
    return name
