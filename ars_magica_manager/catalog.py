"""Loads the shared catalogs -- Virtues/Flaws, Abilities, Houses, Boons & Hooks,
Laboratory Virtues/Flaws, Laboratory Features, Spells, and Weapons & Armor
(reference data, not per-saga)."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import DATA_DIR
from .models import (
    BOON_HOOK_DETAIL,
    COVENANT_BOON_HOOK_CATEGORIES,
    AbilityDef,
    ArmorDef,
    CovenantBoonHookDef,
    HouseDef,
    LabFeatureDef,
    LabVirtueFlawDef,
    Spell,
    VirtueFlawDef,
    VirtueFlawInstance,
    WeaponDef,
)

CATALOG_PATH = DATA_DIR / "virtue_flaw_catalog.json"
ABILITY_CATALOG_PATH = DATA_DIR / "ability_catalog.json"
HOUSE_CATALOG_PATH = DATA_DIR / "house_catalog.json"
COVENANT_BOON_HOOK_CATALOG_PATH = DATA_DIR / "covenant_boon_hook_catalog.json"
LAB_VF_CATALOG_PATH = DATA_DIR / "lab_virtue_flaw_catalog.json"
SPELL_CATALOG_PATH = DATA_DIR / "spell_catalog.json"
LAB_FEATURE_CATALOG_PATH = DATA_DIR / "lab_feature_catalog.json"
WEAPON_ARMOR_CATALOG_PATH = DATA_DIR / "weapon_armor_catalog.json"


def _load_entries[T](path: Path, from_dict: Callable[[dict[str, Any]], T]) -> list[T]:
    """Every entry of a catalog file: {"attribution": ..., "entries": [...]},
    or a bare JSON list of entries (as tests write them)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data["entries"] if isinstance(data, dict) else data
    return [from_dict(entry) for entry in entries]


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
    instance: VirtueFlawInstance,
    catalog_by_id: Mapping[str, VirtueFlawDef | LabVirtueFlawDef],
) -> str:
    """A human-readable label for a Virtue/Flaw instance, params filled in.

    E.g. an instance of "vf_affinity_with_art" with params {"art": "creo"}
    becomes "Affinity with Creo" (the catalog name's "{art}" placeholder
    matches the entry's `parameters`). A parameter the name has no
    placeholder for follows it in brackets: "Deficient Technique (Creo)".
    """
    definition = catalog_by_id.get(instance.vf_id)
    if definition is None:
        return f"{instance.vf_id} (not in catalog)"
    name = _fill_placeholders(definition.name, instance.params)
    extra = [
        instance.params[key].title()
        for key in getattr(definition, "parameters", [])
        if f"{{{key}}}" not in definition.name and instance.params.get(key)
    ]
    return f"{name} ({', '.join(extra)})" if extra else name


def virtue_flaw_offerable(
    definition: VirtueFlawDef, taken: Sequence[VirtueFlawInstance]
) -> bool:
    """Whether the picker should offer `definition` to a character already
    holding `taken`: an entry not yet taken, or a repeatable one below its
    `max_count`."""
    copies = sum(1 for vf in taken if vf.vf_id == definition.id)
    if not copies:
        return True
    if not definition.repeatable:
        return False
    return definition.max_count is None or copies < definition.max_count


def virtue_flaw_repeat_refusal(
    definition: VirtueFlawDef,
    taken: Sequence[VirtueFlawInstance],
    params: dict[str, str],
) -> str:
    """Why a character holding `taken` can't add `definition` with `params`
    ("" if it can): past `max_count` copies, or past `max_per_parameter`
    copies with the same parameters."""
    copies = [vf for vf in taken if vf.vf_id == definition.id]
    if not copies:
        return ""
    if not definition.repeatable:
        return f"{definition.name} may only be taken once."
    if definition.max_count is not None and len(copies) >= definition.max_count:
        return f"{definition.name} may be taken at most {definition.max_count} times."
    limit = definition.max_per_parameter
    if definition.parameters and limit is not None:
        same = sum(1 for vf in copies if vf.params == params)
        if same >= limit:
            label = describe_virtue_flaw(
                VirtueFlawInstance(vf_id=definition.id, params=params),
                {definition.id: definition},
            )
            times = "once" if limit == 1 else f"{limit} times"
            return f"Already taken: {label} (at most {times} for the same choice)."
    return ""


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


@lru_cache(maxsize=4)
def _lab_feature_catalog(path: Path) -> tuple[LabFeatureDef, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(LabFeatureDef.from_dict(entry) for entry in data["features"])


def load_lab_feature_catalog(
    path: Path = LAB_FEATURE_CATALOG_PATH,
) -> list[LabFeatureDef]:
    """The 36 Laboratory Features, in the reference's (alphabetical) order.
    Cached: read for every Feature shown."""
    return list(_lab_feature_catalog(path))


def load_lab_feature_catalog_by_id(
    path: Path = LAB_FEATURE_CATALOG_PATH,
) -> dict[str, LabFeatureDef]:
    return {entry.id: entry for entry in _lab_feature_catalog(path)}


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


@lru_cache(maxsize=4)
def _weapon_armor_catalog(
    path: Path,
) -> tuple[tuple[WeaponDef, ...], tuple[ArmorDef, ...]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return (
        tuple(WeaponDef.from_dict(entry) for entry in data["weapons"]),
        tuple(ArmorDef.from_dict(entry) for entry in data["armor"]),
    )


def load_weapon_catalog(
    path: Path = WEAPON_ARMOR_CATALOG_PATH, tables: Sequence[str] | None = None
) -> list[WeaponDef]:
    """The book's weapons, in its order: every one, or those of `tables`
    (WEAPON_TABLES: "melee", "missile", "natural"). Cached: read for every
    weapon shown."""
    weapons = _weapon_armor_catalog(path)[0]
    return [w for w in weapons if tables is None or w.table in tables]


def load_weapon_catalog_by_id(
    path: Path = WEAPON_ARMOR_CATALOG_PATH,
) -> dict[str, WeaponDef]:
    return {entry.id: entry for entry in _weapon_armor_catalog(path)[0]}


def load_armor_catalog(path: Path = WEAPON_ARMOR_CATALOG_PATH) -> list[ArmorDef]:
    """The book's armor Materials, in its order (cached)."""
    return list(_weapon_armor_catalog(path)[1])


def load_armor_catalog_by_id(
    path: Path = WEAPON_ARMOR_CATALOG_PATH,
) -> dict[str, ArmorDef]:
    return {entry.id: entry for entry in _weapon_armor_catalog(path)[1]}
