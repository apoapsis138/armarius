"""Loads the shared Virtue/Flaw and Ability catalogs (reference data, not per-saga)."""

from __future__ import annotations

import json
from pathlib import Path

from .models import AbilityDef, VirtueFlawDef, VirtueFlawInstance

CATALOG_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "virtue_flaw_catalog.json"
)
ABILITY_CATALOG_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "ability_catalog.json"
)


def _fill_placeholders(name: str, params: dict[str, str]) -> str:
    for key, value in params.items():
        name = name.replace(f"{{{key}}}", value.title())
    return name


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
    return _fill_placeholders(definition.name, instance.params)


def load_ability_catalog(path: Path = ABILITY_CATALOG_PATH) -> list[AbilityDef]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [AbilityDef.from_dict(entry) for entry in data]


def load_ability_catalog_by_id(
    path: Path = ABILITY_CATALOG_PATH,
) -> dict[str, AbilityDef]:
    return {entry.id: entry for entry in load_ability_catalog(path)}


def resolve_ability_name(entry: AbilityDef, params: dict[str, str]) -> str:
    """The concrete Ability name for a catalog entry, params filled in.

    E.g. "Craft: {craft}" with params {"craft": "blacksmith"} becomes
    "Craft: Blacksmith". Unlike Virtues/Flaws, an Ability on a character
    (models.Ability) just stores this resolved name as a plain string --
    there's no per-instance wrapper, since a character can hold the same
    Ability family (e.g. two different Crafts) more than once.
    """
    return _fill_placeholders(entry.name, params)
