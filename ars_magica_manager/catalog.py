"""Loads the shared catalogs -- Virtues/Flaws, Abilities, Houses, Boons & Hooks,
Laboratory Virtues/Flaws, Laboratory Features, Spells, Weapons & Armor, and
Shape & Material bonuses (reference data, not per-saga)."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import DATA_DIR, sourcebooks
from .models import (
    BOON_HOOK_DETAIL,
    COVENANT_BOON_HOOK_CATEGORIES,
    AbilityDef,
    ArmorDef,
    Character,
    CovenantBoonHookDef,
    Familiar,
    HouseDef,
    LabFeatureDef,
    LabVirtueFlawDef,
    ShapeMaterialDef,
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
SHAPE_MATERIAL_CATALOG_PATH = DATA_DIR / "shape_material_catalog.json"


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


def _file_key(path: Path) -> tuple[int, int]:
    """What identifies a version of a catalog file for caching: a file
    rewritten (as tests do) is read again."""
    stat = path.stat()
    return stat.st_mtime_ns, stat.st_size


@lru_cache(maxsize=16)
def _cached_entries(
    path: Path, from_dict: Callable[[dict[str, Any]], Any], _key: tuple[int, int]
) -> tuple[Any, ...]:
    return tuple(_load_entries(path, from_dict))


@lru_cache(maxsize=16)
def _cached_by_id(
    path: Path, from_dict: Callable[[dict[str, Any]], Any], key: tuple[int, int]
) -> dict[str, Any]:
    return {entry.id: entry for entry in _cached_entries(path, from_dict, key)}


def load_virtue_flaw_catalog(path: Path = CATALOG_PATH) -> list[VirtueFlawDef]:
    """The character Virtue/Flaw catalog. The catalogs are cached while their
    file is unchanged: every total and sheet row that looks at Virtues and
    Flaws reads them (the shared lists and dicts must not be changed)."""
    return list(_cached_entries(path, VirtueFlawDef.from_dict, _file_key(path)))


def load_virtue_flaw_catalog_by_id(
    path: Path = CATALOG_PATH,
) -> dict[str, VirtueFlawDef]:
    return _cached_by_id(path, VirtueFlawDef.from_dict, _file_key(path))


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


#: The Gift, and the infernal False Gift that has all its benefits.
GIFT_IDS: frozenset[str] = frozenset({"vf_the_gift", "vf_the_false_gift"})

#: Hermetic entries the book also lets an unGifted character take, as a
#: General or Supernatural one ("Hermetic or General", "Supernatural or
#: Hermetic"; Inoffensive to (Beings) needs "The Gift, or Magical Air").
HERMETIC_OR_OTHER_IDS: frozenset[str] = frozenset(
    {
        "vf_inoffensive_to_being",
        "vf_offensive_to_being",
        "vf_unbearable_to_being",
        "vf_faerie_metamorphosis",
    }
)

#: The audiences a familiar is offered (a magical animal, with Magic Might).
FAMILIAR_AUDIENCES: frozenset[str] = frozenset({"animal", "magic being"})

#: Each audience as named in an "only for ..." note.
_AUDIENCE_PLURALS: dict[str, str] = {
    "faerie": "faeries",
    "magic being": "magic beings",
    "corrupted beast": "corrupted beasts",
    "animal": "animals",
    "mythic companion": "Mythic Companions",
}


def needs_the_gift(definition: VirtueFlawDef) -> bool:
    """Whether only a Gifted character may take `definition`: a Hermetic
    Virtue/Flaw (any of its printed types), unless the book also allows it
    as a non-Hermetic one (HERMETIC_OR_OTHER_IDS)."""
    types = (definition.category, *definition.extra_categories)
    return "Hermetic" in types and definition.id not in HERMETIC_OR_OTHER_IDS


@dataclass(frozen=True)
class VirtueFlawChooser:
    """Who is choosing from the character Virtue/Flaw catalog, for the
    picker's structural eligibility rules (STORY-710); prose prerequisites
    ("requires Demonic Blood") are left to the description.

    `audiences` are the VIRTUE_FLAW_AUDIENCES this chooser belongs to (an
    entry with an audience is only for those); `books` the sourcebooks in
    play (STORY-711), or None for every book.
    """

    grog: bool = False
    gifted: bool = False
    audiences: frozenset[str] = frozenset()
    books: frozenset[str] | None = None

    @classmethod
    def for_character(
        cls, character: Character, books: frozenset[str] | None = None
    ) -> VirtueFlawChooser:
        """A magus counts as Gifted before The Gift is added (the book
        makes every magus take it); anyone else once they hold it."""
        held = {vf.vf_id for vf in character.virtues_flaws}
        mythic = character.type == "mythic companion"
        return cls(
            grog=character.type == "grog",
            gifted=character.type == "magus" or bool(held & GIFT_IDS),
            audiences=frozenset({"mythic companion"}) if mythic else frozenset(),
            books=books,
        )

    @classmethod
    def for_familiar(
        cls, familiar: Familiar, books: frozenset[str] | None = None
    ) -> VirtueFlawChooser:
        held = {vf.vf_id for vf in familiar.virtues_flaws}
        return cls(
            gifted=bool(held & GIFT_IDS), audiences=FAMILIAR_AUDIENCES, books=books
        )

    def refusal(self, definition: VirtueFlawDef) -> str:
        """Why this chooser can't take `definition`, as a short note ("needs
        The Gift"), or "" if it can."""
        if definition.audience and not self.audiences & set(definition.audience):
            names = [_AUDIENCE_PLURALS[who] for who in definition.audience]
            return "only for " + " or ".join(names)
        if self.grog and definition.id in GIFT_IDS:
            return "not for grogs"
        if self.grog and definition.tier == "Major":
            return "not for grogs: Major"
        if self.grog and needs_the_gift(definition):
            return "not for grogs: Hermetic"
        if not self.gifted and needs_the_gift(definition):
            return "needs The Gift"
        if not sourcebooks.in_play(definition.source, self.books):
            return "book not in play"
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
    return list(_cached_entries(path, LabVirtueFlawDef.from_dict, _file_key(path)))


def load_lab_virtue_flaw_catalog_by_id(
    path: Path = LAB_VF_CATALOG_PATH,
) -> dict[str, LabVirtueFlawDef]:
    return _cached_by_id(path, LabVirtueFlawDef.from_dict, _file_key(path))


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
    return list(_cached_entries(path, CovenantBoonHookDef.from_dict, _file_key(path)))


def load_covenant_boon_hook_catalog_by_id(
    path: Path = COVENANT_BOON_HOOK_CATALOG_PATH,
) -> dict[str, CovenantBoonHookDef]:
    return _cached_by_id(path, CovenantBoonHookDef.from_dict, _file_key(path))


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


@lru_cache(maxsize=4)
def _shape_material_catalog(path: Path) -> tuple[ShapeMaterialDef, ...]:
    return tuple(_load_entries(path, ShapeMaterialDef.from_dict))


def load_shape_material_catalog(
    path: Path = SHAPE_MATERIAL_CATALOG_PATH,
) -> list[ShapeMaterialDef]:
    """DE's Shape and Material Bonuses Table, row for row in its order
    (built by tools/build_shape_material_catalog.py). Cached."""
    return list(_shape_material_catalog(path))
