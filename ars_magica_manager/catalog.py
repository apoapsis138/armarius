"""Loads the shared catalogs -- Virtues/Flaws, Abilities, Houses, Boons & Hooks,
Laboratory Virtues/Flaws, Laboratory Features, Spells, Weapons & Armor,
Shape & Material bonuses and Character and Grog Templates (reference data, not
per-saga)."""

from __future__ import annotations

import json
from collections.abc import Callable, Collection, Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from . import DATA_DIR
from .models import (
    BOON_HOOK_DETAIL,
    COVENANT_BOON_HOOK_CATEGORIES,
    AbilityDef,
    ArmorDef,
    CharacterTemplateDef,
    CovenantBoonHookDef,
    CovenantSituationDef,
    GoodDef,
    GrogTemplateDef,
    HouseDef,
    LabFeatureDef,
    LabVirtueFlawDef,
    Saga,
    ShapeMaterialDef,
    Spell,
    TraditionDef,
    VirtueFlawDef,
    VirtueFlawInstance,
    WeaponDef,
)
from .models.ancient_magic import AncientChapter

CATALOG_PATH = DATA_DIR / "virtue_flaw_catalog.json"
ABILITY_CATALOG_PATH = DATA_DIR / "ability_catalog.json"
HOUSE_CATALOG_PATH = DATA_DIR / "house_catalog.json"
TRADITION_CATALOG_PATH = DATA_DIR / "tradition_catalog.json"
COVENANT_BOON_HOOK_CATALOG_PATH = DATA_DIR / "covenant_boon_hook_catalog.json"
COVENANT_SITUATION_CATALOG_PATH = DATA_DIR / "covenant_situation_catalog.json"
LAB_VF_CATALOG_PATH = DATA_DIR / "lab_virtue_flaw_catalog.json"
SPELL_CATALOG_PATH = DATA_DIR / "spell_catalog.json"
LAB_FEATURE_CATALOG_PATH = DATA_DIR / "lab_feature_catalog.json"
WEAPON_ARMOR_CATALOG_PATH = DATA_DIR / "weapon_armor_catalog.json"
SHAPE_MATERIAL_CATALOG_PATH = DATA_DIR / "shape_material_catalog.json"
CHARACTER_TEMPLATE_CATALOG_PATH = DATA_DIR / "character_template_catalog.json"
GROG_TEMPLATE_CATALOG_PATH = DATA_DIR / "grog_template_catalog.json"
ANIMAL_TEMPLATE_CATALOG_PATH = DATA_DIR / "animal_template_catalog.json"
GOODS_CATALOG_PATH = DATA_DIR / "goods_catalog.json"


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
def _spell_catalog_by_id(path: Path) -> Mapping[str, Spell]:
    return MappingProxyType({spell.id: spell for spell in _spell_catalog(path)})


def load_spell_catalog_by_id(path: Path = SPELL_CATALOG_PATH) -> Mapping[str, Spell]:
    return _spell_catalog_by_id(path)


def _fill_placeholders(name: str, params: dict[str, str]) -> str:
    for key, value in params.items():
        name = name.replace(f"{{{key}}}", value.title())
    return name


@lru_cache(maxsize=16)
def _cached_entries(
    path: Path, from_dict: Callable[[dict[str, Any]], Any]
) -> tuple[Any, ...]:
    return tuple(_load_entries(path, from_dict))


@lru_cache(maxsize=16)
def _cached_by_id(
    path: Path, from_dict: Callable[[dict[str, Any]], Any]
) -> Mapping[str, Any]:
    """Shared by every caller, so read-only: a change raises TypeError."""
    return MappingProxyType(
        {entry.id: entry for entry in _cached_entries(path, from_dict)}
    )


#: The user-made entries of the saga in use, by the kind of
#: catalog they join: set by use_saga(), read by the three loaders below.
_SAGA_ENTRIES: dict[str, tuple[Any, ...]] = {
    "character": (),
    "lab": (),
    "covenant": (),
    "goods": (),
}
#: Each catalog with the saga's entries merged in, by (kind, path): built on
#: first use and dropped whenever use_saga() changes the entries.
_MERGED_BY_ID: dict[tuple[str, Path], Mapping[str, Any]] = {}


def use_saga(saga: Saga | None) -> None:
    """Make `saga`'s user-made entries part of the Virtue/Flaw, laboratory
    Virtue/Flaw and Boon/Hook catalogs (None: just the shared catalogs), and
    its hidden catalogs and entries (see hidden()) what pickers leave out.
    The app has one saga open at a time: the workspace calls this as it
    opens one, and house_rules and the Saga Content view do after every
    change."""
    _SAGA_ENTRIES["character"] = tuple(saga.custom_virtues_flaws) if saga else ()
    _SAGA_ENTRIES["lab"] = tuple(saga.custom_lab_virtues_flaws) if saga else ()
    _SAGA_ENTRIES["covenant"] = tuple(saga.custom_boons_hooks) if saga else ()
    _SAGA_ENTRIES["goods"] = tuple(saga.custom_goods) if saga else ()
    _MERGED_BY_ID.clear()
    _HIDDEN.clear()
    if saga is None:
        return
    for key, kind in SAGA_CATALOG_KINDS.items():
        ids = frozenset(saga.hidden_entries.get(key, ()))
        whole = key in saga.hidden_catalogs
        if whole or ids:
            _HIDDEN[kind] = (whole, ids)
    _OWN_IDS.clear()
    _OWN_IDS.update(
        entry.id
        for entry in (
            *saga.custom_virtues_flaws,
            *saga.custom_lab_virtues_flaws,
            *saga.custom_boons_hooks,
            *saga.custom_goods,
            *saga.spells,
        )
    )


#: The shared catalogs a saga can hide (whole, or entry by entry), by key:
#: what Saga.hidden_catalogs and Saga.hidden_entries name, and the kind of
#: entry each holds (how hidden() tells an entry's catalog). Their labels
#: and loaders are saga_content.CATALOGS.
SAGA_CATALOG_KINDS: dict[str, type] = {
    "virtues_flaws": VirtueFlawDef,
    "lab_virtues_flaws": LabVirtueFlawDef,
    "boons_hooks": CovenantBoonHookDef,
    "abilities": AbilityDef,
    "spells": Spell,
    "shapes_materials": ShapeMaterialDef,
    "goods": GoodDef,
}

#: The saga in use's hidden catalogs: entry kind -> (the whole catalog is
#: hidden, the ids of single hidden entries). Set by use_saga().
_HIDDEN: dict[type, tuple[bool, frozenset[str]]] = {}
#: The ids of the saga in use's own entries, which a hidden catalog keeps.
_OWN_IDS: set[str] = set()


def hides_any() -> bool:
    """Whether the saga in use hides any catalog or entry."""
    return bool(_HIDDEN)


def hidden(entry: Any) -> bool:
    """Whether the saga in use doesn't offer `entry`: its catalog is hidden
    (the saga's own entries excepted) or the entry is. A picker treats it
    like an entry from a book out of play. A (definition, bonus) pair, as
    the Shape & Material picker lists them, is its definition's."""
    if isinstance(entry, tuple):
        entry = entry[0]
    found = _HIDDEN.get(type(entry))
    if found is None:
        return False
    whole, ids = found
    entry_id = getattr(entry, "id", "")
    return entry_id in ids or (whole and entry_id not in _OWN_IDS)


def _with_saga_entries(kind: str, entries: tuple[Any, ...]) -> list[Any]:
    return [*entries, *_SAGA_ENTRIES[kind]]


def _by_id_with_saga_entries(
    kind: str, path: Path, from_dict: Callable[[dict[str, Any]], Any]
) -> Mapping[str, Any]:
    shared = _cached_by_id(path, from_dict)
    extra = _SAGA_ENTRIES[kind]
    if not extra:
        return shared
    merged = _MERGED_BY_ID.get((kind, path))
    if merged is None:
        merged = MappingProxyType({**shared, **{entry.id: entry for entry in extra}})
        _MERGED_BY_ID[(kind, path)] = merged
    return merged


def load_virtue_flaw_catalog(path: Path = CATALOG_PATH) -> list[VirtueFlawDef]:
    """The character Virtue/Flaw catalog, with the user-made entries of the saga in use
    (use_saga). The catalogs are read once per run and cached by path: every total and
    sheet row that looks at Virtues and Flaws reads them (the shared dicts must not be
    changed). Nothing checks the file again -- a stat per lookup cost ~80 us each on a
    synced folder -- so a rebuilt catalog is seen on the next start."""
    return _with_saga_entries(
        "character", _cached_entries(path, VirtueFlawDef.from_dict)
    )


def load_virtue_flaw_catalog_by_id(
    path: Path = CATALOG_PATH,
) -> Mapping[str, VirtueFlawDef]:
    return _by_id_with_saga_entries("character", path, VirtueFlawDef.from_dict)


def describe_virtue_flaw(
    instance: VirtueFlawInstance,
    catalog_by_id: Mapping[str, VirtueFlawDef | LabVirtueFlawDef],
) -> str:
    """A human-readable label for a Virtue/Flaw instance, params filled in.

    E.g. an instance of "vf_affinity_with_art" with params {"art": "creo"}
    becomes "Affinity with Creo" (the catalog name's "{art}" placeholder
    matches the entry's `parameters`). A parameter the name has no
    placeholder for follows it in brackets: "Deficient Technique (Creo)".
    A laboratory Virtue's parameters (a Servant's grog or Intelligence)
    are what its effect is read from, not part of its name.
    """
    definition = catalog_by_id.get(instance.vf_id)
    if definition is None:
        return f"{instance.vf_id} (not in catalog)"
    name = _fill_placeholders(definition.name, instance.params)
    if isinstance(definition, LabVirtueFlawDef):
        return name
    extra = [
        instance.params[key].title()
        for key in definition.parameters
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

#: The audiences a creature of the Bestiary is offered: every kind of
#: being that isn't a person.
CREATURE_AUDIENCES: frozenset[str] = frozenset(
    {"faerie", "magic being", "corrupted beast", "animal"}
)


def needs_the_gift(definition: VirtueFlawDef) -> bool:
    """Whether only a Gifted character may take `definition`: a Hermetic
    Virtue/Flaw (any of its printed types), unless the book also allows it
    as a non-Hermetic one (HERMETIC_OR_OTHER_IDS)."""
    types = (definition.category, *definition.extra_categories)
    return "Hermetic" in types and definition.id not in HERMETIC_OR_OTHER_IDS


def load_ability_catalog(path: Path = ABILITY_CATALOG_PATH) -> list[AbilityDef]:
    return list(_cached_entries(path, AbilityDef.from_dict))


def load_ability_catalog_by_id(
    path: Path = ABILITY_CATALOG_PATH,
) -> Mapping[str, AbilityDef]:
    return _cached_by_id(path, AbilityDef.from_dict)


def abilities_to_offer(held_names: Collection[str]) -> list[AbilityDef]:
    """The Abilities a character holding `held_names` can still take: an
    Ability already held isn't offered again (no point in a second
    "Athletics"), but a templated one ("Craft: {craft}") always is, since a
    character can hold several of the same family."""
    return [
        entry
        for entry in load_ability_catalog()
        if entry.parameters or entry.name not in held_names
    ]


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
    return list(_cached_entries(path, HouseDef.from_dict))


def load_house_catalog_by_id(path: Path = HOUSE_CATALOG_PATH) -> Mapping[str, HouseDef]:
    return _cached_by_id(path, HouseDef.from_dict)


def load_tradition_catalog(path: Path = TRADITION_CATALOG_PATH) -> list[TraditionDef]:
    return list(_cached_entries(path, TraditionDef.from_dict))


def load_tradition_catalog_by_id(
    path: Path = TRADITION_CATALOG_PATH,
) -> Mapping[str, TraditionDef]:
    return _cached_by_id(path, TraditionDef.from_dict)


def load_character_template_catalog(
    path: Path = CHARACTER_TEMPLATE_CATALOG_PATH,
) -> list[CharacterTemplateDef]:
    return list(_cached_entries(path, CharacterTemplateDef.from_dict))


def load_character_template_catalog_by_id(
    path: Path = CHARACTER_TEMPLATE_CATALOG_PATH,
) -> Mapping[str, CharacterTemplateDef]:
    return _cached_by_id(path, CharacterTemplateDef.from_dict)


def load_grog_template_catalog(
    path: Path = GROG_TEMPLATE_CATALOG_PATH,
) -> list[GrogTemplateDef]:
    return list(_cached_entries(path, GrogTemplateDef.from_dict))


def load_grog_template_catalog_by_id(
    path: Path = GROG_TEMPLATE_CATALOG_PATH,
) -> Mapping[str, GrogTemplateDef]:
    return _cached_by_id(path, GrogTemplateDef.from_dict)


def load_animal_template_catalog(
    path: Path = ANIMAL_TEMPLATE_CATALOG_PATH,
) -> list[GrogTemplateDef]:
    """Grogs' animal grog samples (Dog, Horse, Hawk), as grog templates
    with an animal form."""
    return list(_cached_entries(path, GrogTemplateDef.from_dict))


def load_animal_template_catalog_by_id(
    path: Path = ANIMAL_TEMPLATE_CATALOG_PATH,
) -> Mapping[str, GrogTemplateDef]:
    return _cached_by_id(path, GrogTemplateDef.from_dict)


def load_lab_virtue_flaw_catalog(
    path: Path = LAB_VF_CATALOG_PATH,
) -> list[LabVirtueFlawDef]:
    return _with_saga_entries("lab", _cached_entries(path, LabVirtueFlawDef.from_dict))


def load_lab_virtue_flaw_catalog_by_id(
    path: Path = LAB_VF_CATALOG_PATH,
) -> Mapping[str, LabVirtueFlawDef]:
    return _by_id_with_saga_entries("lab", path, LabVirtueFlawDef.from_dict)


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


def lab_feature_names() -> dict[str, str]:
    """Each Laboratory Feature's name, to its id: what an older save's
    free-text Features are matched by (Saga.from_dict)."""
    return {
        entry.name: entry.id for entry in _lab_feature_catalog(LAB_FEATURE_CATALOG_PATH)
    }


def load_lab_feature_catalog_by_id(
    path: Path = LAB_FEATURE_CATALOG_PATH,
) -> dict[str, LabFeatureDef]:
    return {entry.id: entry for entry in _lab_feature_catalog(path)}


def load_covenant_boon_hook_catalog(
    path: Path = COVENANT_BOON_HOOK_CATALOG_PATH,
) -> list[CovenantBoonHookDef]:
    return _with_saga_entries(
        "covenant", _cached_entries(path, CovenantBoonHookDef.from_dict)
    )


def load_covenant_boon_hook_catalog_by_id(
    path: Path = COVENANT_BOON_HOOK_CATALOG_PATH,
) -> Mapping[str, CovenantBoonHookDef]:
    return _by_id_with_saga_entries("covenant", path, CovenantBoonHookDef.from_dict)


def load_covenant_situation_catalog(
    path: Path = COVENANT_SITUATION_CATALOG_PATH,
) -> list[CovenantSituationDef]:
    """The books' Covenant Situations: ready-made sets of Boons and Hooks."""
    return list(_cached_entries(path, CovenantSituationDef.from_dict))


def load_goods_catalog(path: Path = GOODS_CATALOG_PATH) -> list[GoodDef]:
    """The Goods catalog (City & Guild's Prices of Goods table and Price
    List), with the saga in use's own goods after it (use_saga). The
    shared entries must not be changed."""
    return _with_saga_entries("goods", _cached_entries(path, GoodDef.from_dict))


def describe_boon_hook(
    instance: VirtueFlawInstance, catalog_by_id: Mapping[str, CovenantBoonHookDef]
) -> str:
    """A human-readable label for a covenant Boon/Hook instance: its name
    with what it names filled in (as describe_virtue_flaw's), then " - "
    and the optional detail if one was given ("Edifice - Tower of the
    Silver Iris")."""
    definition = catalog_by_id.get(instance.vf_id)
    if definition is None:
        return f"{instance.vf_id} (not in catalog)"
    named = {key: instance.params.get(key, "") for key in definition.parameters}
    name = _fill_placeholders(definition.name, named)
    extra = [
        value.title()
        for key, value in named.items()
        if f"{{{key}}}" not in definition.name and value
    ]
    if extra:
        name = f"{name} ({', '.join(extra)})"
    detail = instance.params.get(BOON_HOOK_DETAIL, "").strip()
    return f"{name} - {detail}" if detail else name


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
    (built by tools/build_shape_material_catalog.py), with the supplements'
    rows it lacks (Covenants, Against the Dark, Mystery Cults) in
    alphabetical place. Cached."""
    return list(_shape_material_catalog(path))


def find_spell(saga: Saga, spell_id: str | None) -> Spell | None:
    """The spell with this id, wherever it lives: the shared catalog, then the
    saga's own spells, then any magus's invented spells."""
    if not spell_id:
        return None
    found = load_spell_catalog_by_id().get(spell_id)
    if found is not None:
        return found
    for spell in saga.spells:
        if spell.id == spell_id:
            return spell
    for character in saga.characters:
        for spell in character.invented_spells:
            if spell.id == spell_id:
                return spell
    return None


def name_key(name: str) -> str:
    """How spell names are compared: any case, any spacing, typographic
    apostrophes allowed."""
    return " ".join(name.replace("’", "'").lower().split())


def find_spell_by_name(saga: Saga, name: str) -> Spell | None:
    """The spell with this name (any case, typographic apostrophes allowed),
    wherever it lives: the catalog, then the saga's own, then any magus's
    invented spells. How a book whose spell was typed (or imported) links."""
    key = name_key(name)
    if not key:
        return None
    for spell in load_spell_catalog():
        if name_key(spell.name) == key:
            return spell
    for spell in saga.spells:
        if name_key(spell.name) == key:
            return spell
    for character in saga.characters:
        for spell in character.invented_spells:
            if name_key(spell.name) == key:
                return spell
    return None


# -- Ancient Magic's chapters: integrations, Insight sources, rolls --------

ANCIENT_MAGIC_CATALOG_PATH = DATA_DIR / "ancient_magic_catalog.json"


def load_ancient_magic_catalog(
    path: Path = ANCIENT_MAGIC_CATALOG_PATH,
) -> list[AncientChapter]:
    """Ancient Magic's chapters as data (rules/ancient_integrations.py reads
    them)."""
    return list(_cached_entries(path, AncientChapter.from_dict))
