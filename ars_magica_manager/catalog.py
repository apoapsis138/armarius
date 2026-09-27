"""Loads the shared catalogs -- Virtues/Flaws, Abilities, Houses, Boons & Hooks,
Laboratory Virtues/Flaws and Spells (reference data, not per-saga)."""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import DATA_DIR
from .models import (
    BOON_HOOK_DETAIL,
    COVENANT_BOON_HOOK_CATEGORIES,
    AbilityDef,
    CovenantBoonHookDef,
    HouseDef,
    LabVirtueFlawDef,
    Spell,
    VirtueFlawDef,
    VirtueFlawInstance,
)

CATALOG_PATH = DATA_DIR / "virtue_flaw_catalog.json"
ABILITY_CATALOG_PATH = DATA_DIR / "ability_catalog.json"
HOUSE_CATALOG_PATH = DATA_DIR / "house_catalog.json"
COVENANT_BOON_HOOK_CATALOG_PATH = DATA_DIR / "covenant_boon_hook_catalog.json"
LAB_VF_CATALOG_PATH = DATA_DIR / "lab_virtue_flaw_catalog.json"
SPELL_CATALOG_PATH = DATA_DIR / "spell_catalog.json"


def _load_entries[T](path: Path, from_dict: Callable[[dict[str, Any]], T]) -> list[T]:
    """Every entry of a catalog file that is a JSON list of entries."""
    return [from_dict(entry) for entry in json.loads(path.read_text(encoding="utf-8"))]


@lru_cache(maxsize=4)
def _spell_catalog(path: Path) -> tuple[Spell, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(Spell.from_dict(entry) for entry in data["spells"])


def load_spell_catalog(path: Path = SPELL_CATALOG_PATH) -> list[Spell]:
    """The published spells (built by tools/build_spell_catalog.py from the
    Grand Grimoire). Cached: it's large and read-only, and spells are looked
    up for every Lab Text and known spell shown."""
    return list(_spell_catalog(path))


@lru_cache(maxsize=4)
def _spell_catalog_by_id(path: Path) -> dict[str, Spell]:
    return {spell.id: spell for spell in _spell_catalog(path)}


def load_spell_catalog_by_id(path: Path = SPELL_CATALOG_PATH) -> dict[str, Spell]:
    return _spell_catalog_by_id(path)


def _fill_placeholders(name: str, params: dict[str, str]) -> str:
    for key, value in params.items():
        name = name.replace(f"{{{key}}}", value.title())
    return name


def load_virtue_flaw_catalog(path: Path = CATALOG_PATH) -> list[VirtueFlawDef]:
    return _load_entries(path, VirtueFlawDef.from_dict)


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
    return _load_entries(path, AbilityDef.from_dict)


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


def load_house_catalog(path: Path = HOUSE_CATALOG_PATH) -> list[HouseDef]:
    return _load_entries(path, HouseDef.from_dict)


def load_house_catalog_by_id(path: Path = HOUSE_CATALOG_PATH) -> dict[str, HouseDef]:
    return {entry.id: entry for entry in load_house_catalog(path)}


def load_lab_virtue_flaw_catalog(
    path: Path = LAB_VF_CATALOG_PATH,
) -> list[LabVirtueFlawDef]:
    return _load_entries(path, LabVirtueFlawDef.from_dict)


def load_lab_virtue_flaw_catalog_by_id(
    path: Path = LAB_VF_CATALOG_PATH,
) -> dict[str, LabVirtueFlawDef]:
    return {entry.id: entry for entry in load_lab_virtue_flaw_catalog(path)}


def load_covenant_boon_hook_catalog(
    path: Path = COVENANT_BOON_HOOK_CATALOG_PATH,
) -> list[CovenantBoonHookDef]:
    return _load_entries(path, CovenantBoonHookDef.from_dict)


def load_covenant_boon_hook_catalog_by_id(
    path: Path = COVENANT_BOON_HOOK_CATALOG_PATH,
) -> dict[str, CovenantBoonHookDef]:
    return {entry.id: entry for entry in load_covenant_boon_hook_catalog(path)}


def describe_boon_hook(
    instance: VirtueFlawInstance, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> str:
    """A human-readable label for a covenant Boon/Hook instance: its name,
    then " - " and the optional detail if one was given ("Edifice - Tower of
    the Silver Iris")."""
    definition = catalog_by_id.get(instance.vf_id)
    if definition is None:
        return f"{instance.vf_id} (not in catalog)"
    detail = instance.params.get(BOON_HOOK_DETAIL, "").strip()
    return f"{definition.name} - {detail}" if detail else definition.name


_TIER_ORDER = {"Free": 0, "Minor": 1, "Major": 2}


def boon_hook_sort_key(entry: CovenantBoonHookDef) -> tuple[int, int, str]:
    """Picker order: by type in the book's order (untyped last), then Free,
    Minor, Major, then name."""
    categories = COVENANT_BOON_HOOK_CATEGORIES
    category = (
        categories.index(entry.category)
        if entry.category in categories
        else len(categories)
    )
    return (category, _TIER_ORDER.get(entry.tier, 9), entry.name.lower())
