"""Exporting one covenant, laboratory or character, or a whole saga, to a
file, and importing it into another saga.

An export is the app's own JSON: a small saga holding just the record and
what travels with it, so reading one runs the same load-time migrations a
save does and older exports keep working.

- A character takes its familiar, the enchanted devices it holds, its books
  and its Diary (which is on its sheet).
- A laboratory takes its books and the devices kept in it.
- A covenant takes its books and devices; optionally its laboratories and
  characters too, each with their own things.
- The saga's own spells and user-made catalog entries that
  those records use come along.
- A whole saga takes everything in it; importing it adds every one of its
  records, as importing each of them would.
- A content pack (packs.py) takes chosen Tribunals, covenants, characters,
  places, neighbours and calendar entries; importing one matches each
  record to one of the same name already in the saga instead of adding
  it beside it.

Links to records that aren't in the file (a character's covenant, a
laboratory's owner, a book's author...) are kept by name: importing matches
each to the one record of that kind and name in the target saga, or drops
it. A character's or laboratory's covenant also travels as a stub (its name,
aura and realm): where the target has no covenant of that name, the stub is
added, so the aura comes along. Nothing already in the target saga is changed, except that a
laboratory with no owner (or a magus with no laboratory) can be given the
imported partner the file names. Everything imported gets ids that are
free in the target. Season plans, season records and lab projects under
way stay behind.
"""

from __future__ import annotations

import json
import zipfile
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, TypedDict, cast

from . import __version__, catalog, places, portraits, shapes, storage, viewing
from .atlas import maps as atlas_maps
from .files import write_atomic
from .models import (
    ITEM_DEVICE_PARAM,
    REALMS,
    AtlasMap,
    Book,
    CalendarEntry,
    Character,
    Codex,
    Covenant,
    Creature,
    EnchantedDevice,
    Familiar,
    Laboratory,
    Neighbour,
    Pin,
    Saga,
    Spell,
    Tribunal,
)
from .rules import sites
from .seat_view import seat_view

FORMAT = "armarius-export"
#: The labels an import accepts: exports made before the app was Armarius
#: carry the older one.
FORMATS = (FORMAT, "ars-magica-manager-export")
SUFFIX = ".amm.json"
#: An export that carries pictures (maps, portraits): a zip of the same
#: JSON file and the pictures, each in its folder (PICTURE_FOLDERS).
ZIP_SUFFIX = ".amm.zip"
#: Where an export's pictures sit, in the zip and beside a shipped pack:
#: the maps folder's and the portraits folder's names.
MAPS, PORTRAITS = "maps", "portraits"
CHARACTER, LABORATORY, COVENANT = "character", "laboratory", "covenant"
#: The kind of a whole saga's export, and of a content pack's.
SAGA, PACK = "saga", "pack"
#: A pack's key for its introduction: a few paragraphs, separated by
#: blank lines, that Start from a pack shows under the pack chosen.
INTRODUCTION = "introduction"
#: A pack's key naming the shipped book pack it is built on (a saga
#: starter's Tribunal pack, "rhine"), brought in before it.
BASE = "base"
#: The kind of record a place or neighbour is, among the links.
NEIGHBOUR = "neighbour"
#: The kind of record a creature of the Bestiary is.
CREATURE = "creature"
#: The key in a neighbour's details holding its roll tables
#: (place_events.RollTable).
TABLES = "tables"
KIND_LABELS: dict[str, str] = {
    CHARACTER: "Character",
    LABORATORY: "Laboratory",
    COVENANT: "Covenant",
    SAGA: "Saga",
    PACK: "Content Pack",
    NEIGHBOUR: "Neighbour",
    CREATURE: "Creature",
}

Record = Character | Laboratory | Covenant
#: The kinds of record an export can link to outside it, by name.
LINKED_KINDS = (CHARACTER, LABORATORY, COVENANT, NEIGHBOUR, CREATURE)


def kind_of(record: Record) -> str:
    if isinstance(record, Character):
        return CHARACTER
    if isinstance(record, Laboratory):
        return LABORATORY
    return COVENANT


def default_file_name(record: Record) -> str:
    return f"{storage.slugify(record.name) or kind_of(record)}{SUFFIX}"


# ------------------------------------------------------------------ export


def strings(value: Any) -> Iterable[str]:
    """Every string in a JSON-shaped value, dict keys included."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, inner in value.items():
            if isinstance(key, str):
                yield key
            yield from strings(inner)
    elif isinstance(value, (list, tuple)):
        for inner in value:
            yield from strings(inner)


def export_data(
    saga: Saga, record: Record, *, with_members: bool = False
) -> dict[str, Any]:
    """The export of `record` as JSON-ready data. `with_members` (a covenant
    only) adds its laboratories and characters. Anyone but the storyguide
    exports from their seat view, so a file carries no more than the
    screen shows them."""
    if not viewing.storyguide_reads():
        saga = seat_view(saga, viewing.current())
        listed: list[Record] = [*saga.characters, *saga.laboratories, *saga.covenants]
        found = next(
            (r for r in listed if type(r) is type(record) and r.id == record.id), None
        )
        if found is None:
            raise LookupError(f"{record.name} is not one the reader may export.")
        record = found
    covenants = [record] if isinstance(record, Covenant) else []
    characters = [record] if isinstance(record, Character) else []
    labs = [record] if isinstance(record, Laboratory) else []
    if isinstance(record, Covenant) and with_members:
        characters += [c for c in saga.characters if c.covenant_id == record.id]
        labs += [lab for lab in saga.laboratories if lab.covenant_id == record.id]
    # A covenant's Tribunal travels by name only: the importing saga joins
    # its own of that name, or starts one.
    tribunals: list[Tribunal] = []
    for covenant in covenants:
        tribunal = saga.tribunal(covenant.tribunal_id)
        if tribunal is not None and all(t.id != tribunal.id for t in tribunals):
            tribunals.append(Tribunal(id=tribunal.id, name=tribunal.name))
    return bundle_data(
        saga,
        kind_of(record),
        record.name,
        covenants=covenants,
        characters=characters,
        laboratories=labs,
        tribunals=tribunals,
    )


def _revealed(secrets: object) -> list[Any]:
    """A saved record's secrets the players know: the revealed ones (an
    older export's words, never revealed, none)."""
    if not isinstance(secrets, list):
        return []
    return [
        s
        for s in cast(list[object], secrets)
        if isinstance(s, dict) and s.get("revealed_year") is not None
    ]


def without_secrets(data: dict[str, Any]) -> dict[str, Any]:
    """An export with every record's secrets the players don't know left
    out, the revealed ones kept: what a player downloads."""
    kept = dict(data)
    kept["saga"] = {
        key: (
            [
                {**r, "secrets": _revealed(r["secrets"])}
                if isinstance(r, dict) and "secrets" in r
                else r
                for r in value
            ]
            if isinstance(value, list)
            else value
        )
        for key, value in data["saga"].items()
    }
    return kept


#: The saga lists whose records can be unknown to the players.
_REVEALABLE = ("characters", "covenants", "neighbours", "creatures")


def _troupes_own(key: str, record: dict[str, Any]) -> bool:
    """Whether a saved record is the troupe's own, so always known (as
    viewing.troupes_own, on the saved shape)."""
    if key == "characters":
        background = record.get("background") or {}
        return bool(
            str(background.get("player") or "").strip() or background.get("player_id")
        )
    if key == "covenants":
        return record.get("played", True) is not False
    return False


def without_unknown(data: dict[str, Any]) -> dict[str, Any]:
    """An export with every record the players don't know of left out, and
    the pins that showed one."""
    saga = data["saga"]
    gone: set[str] = set()
    kept_saga = dict(saga)
    for key in _REVEALABLE:
        records = saga.get(key)
        if not isinstance(records, list):
            continue
        kept = []
        for record in records:
            if (
                isinstance(record, dict)
                and record.get("known") is False
                and not _troupes_own(key, record)
            ):
                gone.add(str(record.get("id")))
            else:
                kept.append(record)
        kept_saga[key] = kept
    if isinstance(saga.get("pins"), list):
        kept_saga["pins"] = [
            p
            for p in saga["pins"]
            if not (isinstance(p, dict) and p.get("record_id") in gone)
        ]
    return {**data, "saga": kept_saga}


def for_reader(data: dict[str, Any]) -> dict[str, Any]:
    """An export as whoever is looking may take it away (viewing.py): the
    storyguide's whole; anyone else's (a player, or Player view) without
    Secrets or the records the players don't know of."""
    if viewing.storyguide_reads():
        return without_players(data)
    return without_players(without_unknown(without_secrets(data)))


def without_players(data: dict[str, Any]) -> dict[str, Any]:
    """An export with nothing of who may sign in to the saga: no Players,
    and no character's link to the Player who plays them (its id is made
    from their name). The free-text "Player" a character sheet names stays,
    as part of the character."""
    saga = data.get("saga")
    if not isinstance(saga, dict):
        return data
    kept_saga = dict(saga)
    kept_saga["players"] = []
    characters = []
    for character in saga.get("characters") or []:
        background = character.get("background")
        if isinstance(background, dict) and background.get("player_id"):
            character = {**character, "background": {**background, "player_id": None}}
        characters.append(character)
    kept_saga["characters"] = characters
    return {**data, "saga": kept_saga}


def bundle_data(
    saga: Saga,
    kind: str,
    name: str,
    *,
    covenants: list[Covenant],
    characters: list[Character],
    laboratories: list[Laboratory],
    tribunals: list[Tribunal],
    neighbours: list[Neighbour] | None = None,
    calendar: list[CalendarEntry] | None = None,
    creatures: list[Creature] | None = None,
) -> dict[str, Any]:
    """An export of the records given, and what travels with them, as
    JSON-ready data. A Tribunal's meeting under way stays behind."""
    labs = laboratories
    neighbours = neighbours or []
    creatures = creatures or []
    character_ids = {c.id for c in characters}
    owners = (
        {(CHARACTER, c.id) for c in characters}
        | {(LABORATORY, lab.id) for lab in labs}
        | {(COVENANT, c.id) for c in covenants}
    )
    familiars = [f for f in saga.familiars if f.character_id in character_ids]
    books = [b for b in saga.books if (b.owner_kind, b.owner_id) in owners]
    devices = [
        d for d in saga.enchanted_devices if (d.holder_kind, d.holder_id) in owners
    ]
    # Spells the records use that aren't the catalog's and don't already
    # travel on an exported magus: the saga's own, and other magi's.
    carried = {s.id for c in characters for s in c.invented_spells}
    shared = catalog.load_spell_catalog_by_id()
    wanted = [k.spell_id for c in characters for k in c.spells_known] + [
        b.spell_id for b in books if b.spell_id
    ]
    spells: list[Spell] = []
    for spell_id in wanted:
        if spell_id in shared or spell_id in carried:
            continue
        found = catalog.find_spell(saga, spell_id)
        if found is not None and all(s.id != found.id for s in spells):
            spells.append(found)
    held = {
        vf.vf_id
        for holder in [*characters, *familiars, *labs, *creatures]
        for vf in holder.virtues_flaws
    } | {bh.vf_id for c in covenants for bh in c.boons_hooks}
    # The pins on the exported Tribunals' maps of the records exported.
    map_ids = {m.id for t in tribunals for m in t.maps}
    exported = (
        {("covenants", c.id) for c in covenants}
        | {("neighbours", n.id) for n in neighbours}
        | {("creatures", c.id) for c in creatures}
    )
    mini = Saga(
        id="export",
        name=saga.name,
        current_year=saga.current_year,
        current_season=saga.current_season,
        covenants=covenants,
        tribunals=[replace(t, meeting=None) for t in tribunals],
        neighbours=neighbours,
        creatures=creatures,
        calendar=list(calendar or []),
        characters=characters,
        laboratories=labs,
        familiars=familiars,
        enchanted_devices=devices,
        books=books,
        codices=[c for c in saga.codices if any(b.codex_id == c.id for b in books)],
        spells=spells,
        custom_virtues_flaws=[e for e in saga.custom_virtues_flaws if e.id in held],
        custom_lab_virtues_flaws=[
            e for e in saga.custom_lab_virtues_flaws if e.id in held
        ],
        custom_boons_hooks=[e for e in saga.custom_boons_hooks if e.id in held],
        pins=[
            p
            for p in saga.pins
            if p.map_id in map_ids
            and not p.hidden
            and (p.kind, p.record_id) in exported
        ],
        custom_abilities=[
            a
            for a in saga.custom_abilities
            if any(
                held_ability.name == a.name
                for holder in [*characters, *familiars, *creatures]
                for held_ability in holder.abilities
            )
        ],
    )
    content = asdict(mini)
    # The records the file points at but doesn't hold, by name.
    used = set(strings(content))
    owners |= {(NEIGHBOUR, n.id) for n in neighbours}
    owners |= {(CREATURE, c.id) for c in creatures}
    links: dict[str, dict[str, str]] = {kind: {} for kind in LINKED_KINDS}
    for other_kind, others in (
        (CHARACTER, saga.characters),
        (LABORATORY, saga.laboratories),
        (COVENANT, saga.covenants),
        (NEIGHBOUR, saga.neighbours),
        (CREATURE, saga.creatures),
    ):
        for other in others:
            if (other_kind, other.id) not in owners and other.id in used:
                links[other_kind][other.id] = other.name
    return {
        "format": FORMAT,
        "app_version": __version__,
        "kind": kind,
        "name": name,
        "from_saga": saga.name,
        "links": links,
        "stubs": {COVENANT: _covenant_stubs(saga, [*characters, *labs], links)},
        "saga": content,
    }


class CovenantStub(TypedDict):
    """What an export holds of the covenant a character or laboratory in
    it belongs to when the covenant itself isn't in the file."""

    name: str
    aura: int
    aura_realm: str


def _covenant_stubs(
    saga: Saga,
    members: Iterable[Character | Laboratory],
    links: dict[str, dict[str, str]],
) -> dict[str, CovenantStub]:
    """The covenants the members belong to that the file links to: id ->
    name and the aura in force there (a placed covenant's is its place's)."""
    stubs: dict[str, CovenantStub] = {}
    for member in members:
        covenant = saga.covenant(member.covenant_id)
        if covenant is not None and covenant.id in links[COVENANT]:
            stubs[covenant.id] = CovenantStub(
                name=covenant.name,
                aura=covenant.aura,
                aura_realm=covenant.aura_realm,
            )
    return stubs


def pictures_named(data: dict[str, Any]) -> list[tuple[str, str]]:
    """The pictures an export's records name, as (folder, file name): its
    Tribunals' and the saga's maps, and its characters' portraits."""
    saga = data.get("saga") or {}
    found: list[tuple[str, str]] = []
    holders = [*(saga.get("tribunals") or []), saga]
    for holder in holders:
        for atlas_map in holder.get("maps") or []:
            if atlas_map.get("picture"):
                found.append((MAPS, str(atlas_map["picture"])))
    for character in saga.get("characters") or []:
        if character.get("portrait"):
            found.append((PORTRAITS, str(character["portrait"])))
    return list(dict.fromkeys(found))


def _local_picture(folder: str, name: str) -> Path | None:
    """One of this computer's pictures, by its folder and file name."""
    root = storage.maps_dir() if folder == MAPS else storage.portraits_dir()
    found = root / name
    return found if found.is_file() else None


def write_export(path: Path, data: dict[str, Any]) -> Path:
    """Write an export to `path`: the JSON file alone, or, when its
    records name pictures this computer has, a zip of it and them, named
    with ZIP_SUFFIX in place of the JSON one. The file written."""
    data = without_players(data)
    pictures = [
        (folder, name, found)
        for folder, name in pictures_named(data)
        if (found := _local_picture(folder, name)) is not None
    ]
    text = json.dumps(data, indent=2)
    if not pictures:
        write_atomic(path, text)
        return path
    stem = path.name.removesuffix(SUFFIX).removesuffix(ZIP_SUFFIX)
    stem = stem.removesuffix(".json").removesuffix(".zip")
    zipped = path.with_name(stem + ZIP_SUFFIX)
    zipped.parent.mkdir(parents=True, exist_ok=True)
    partial = zipped.with_name(zipped.name + ".partial")
    with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(stem + SUFFIX, text)
        for folder, name, found in pictures:
            # Pictures are already compressed: stored as they are.
            archive.write(found, f"{folder}/{name}", zipfile.ZIP_STORED)
    partial.replace(zipped)
    return zipped


def export_to(
    path: Path, saga: Saga, record: Record, *, with_members: bool = False
) -> Path:
    """Write `record`'s export to `path` (its folder is made if needed):
    a zip with SUFFIX's name changed when it carries a portrait. The file
    written."""
    return write_export(
        path, for_reader(export_data(saga, record, with_members=with_members))
    )


def saga_file_name(saga: Saga) -> str:
    return f"{storage.slugify(saga.name) or SAGA}{SUFFIX}"


def export_saga_data(saga: Saga) -> dict[str, Any]:
    """The export of the whole saga as JSON-ready data: every record and
    what they hold, so nothing it points at is left outside it. Anyone but
    the storyguide exports their seat view."""
    if not viewing.storyguide_reads():
        saga = seat_view(saga, viewing.current())
    return {
        "format": FORMAT,
        "app_version": __version__,
        "kind": SAGA,
        "name": saga.name,
        "from_saga": saga.name,
        "links": {kind: {} for kind in LINKED_KINDS},
        # Players (names, passcode hashes) stay in the saga: an export carries
        # the saga's records, never who may sign in to it.
        "saga": asdict(
            replace(
                saga,
                players=[],
                tribunals=[replace(t, meeting=None) for t in saga.tribunals],
            )
        ),
    }


def export_saga_to(path: Path, saga: Saga) -> Path:
    """Write the whole saga's export to `path` (its folder is made if
    needed), with its maps and portraits as a zip when it has any. The
    file written."""
    return write_export(path, for_reader(export_saga_data(saga)))


# ------------------------------------------------------------------ import


def _text(path: Path) -> str:
    """An export's JSON text: the file itself, or the one JSON file at the
    top of its zip."""
    if not zipfile.is_zipfile(path):
        return path.read_text(encoding="utf-8")
    with zipfile.ZipFile(path) as archive:
        inside = [n for n in archive.namelist() if "/" not in n and n.endswith(".json")]
        if len(inside) != 1:
            raise ValueError("the zip should hold one export's JSON file")
        return archive.read(inside[0]).decode("utf-8")


def read(path: Path) -> dict[str, Any]:
    """An export file's data, from a JSON file or a zip holding one.
    Raises ValueError for anything else."""
    try:
        data = json.loads(_text(path))
    except json.JSONDecodeError as problem:
        raise ValueError(f"not a JSON file ({problem.msg})") from problem
    except (zipfile.BadZipFile, UnicodeDecodeError) as problem:
        raise ValueError(f"the zip can't be read ({problem})") from problem
    if not isinstance(data, dict) or data.get("format") not in FORMATS:
        raise ValueError(
            "not an Armarius export (export a covenant, laboratory or "
            "character from its sheet, or a saga from Saga Management, first)"
        )
    if data.get("kind") not in KIND_LABELS or not isinstance(data.get("saga"), dict):
        raise ValueError("the export is incomplete")
    # Its records' shape, before any is built (shapes.py): older shapes
    # allowed, as an export may come from an older version of the app. An
    # overlay's saga is never built whole: it is laid over a saga's own.
    if "overlay" not in data:
        shapes.check_raw(data["saga"], Saga)
    introduction = data.get(INTRODUCTION)
    if introduction is not None and not isinstance(introduction, str):
        raise ValueError(
            f"the introduction of {data.get('name') or 'the pack'} isn't text"
        )
    base = data.get(BASE)
    if base is not None and (not isinstance(base, str) or not base.strip()):
        raise ValueError(
            f"the base pack of {data.get('name') or 'the pack'} isn't named"
        )
    return data


class Pictures:
    """Where an export's pictures are read from, however it came: inside
    its zip, or in the maps and portraits folders beside a JSON file (a
    shipped pack's data/packs/maps/). The importer asks for a picture by
    its folder and name and never minds which.

    Pattern: Adapter, small: a zip and a folder answer the one question
    alike, so the import plan and its migrations don't change."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.zipped = path.is_file() and zipfile.is_zipfile(path)

    def get(self, folder: str, name: str) -> bytes | None:
        """The picture's bytes, or None when the export doesn't carry it."""
        if not name or "/" in name or "\\" in name or name.startswith("."):
            return None
        if self.zipped:
            with zipfile.ZipFile(self.path) as archive:
                try:
                    return archive.read(f"{folder}/{name}")
                except KeyError:
                    return None
        beside = self.path.parent / folder / name
        return beside.read_bytes() if beside.is_file() else None


@dataclass
class ImportPlan:
    """What importing an export into a saga will do: the records to add,
    already given their new ids and links, and what to tell the user."""

    kind: str
    name: str
    from_saga: str
    covenants: list[Covenant] = field(default_factory=list)
    #: Covenants a character or laboratory belongs to that the saga has
    #: none of the name of: added with only the name and aura the file
    #: gives.
    stub_covenants: list[Covenant] = field(default_factory=list)
    #: Tribunals the covenants name that the saga has none of the name of.
    tribunals: list[Tribunal] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    laboratories: list[Laboratory] = field(default_factory=list)
    familiars: list[Familiar] = field(default_factory=list)
    devices: list[EnchantedDevice] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    codices: list[Codex] = field(default_factory=list)
    spells: list[Spell] = field(default_factory=list)
    custom: dict[str, list[Any]] = field(default_factory=dict)
    neighbours: list[Neighbour] = field(default_factory=list)
    creatures: list[Creature] = field(default_factory=list)
    calendar: list[CalendarEntry] = field(default_factory=list)
    #: A pack's records the saga already has one of the same name of:
    #: "Covenant Keep". The saga's own is kept as it is, and links to the
    #: pack's go to it.
    already: list[str] = field(default_factory=list)
    #: What a pack holds that isn't added: "Book Summa: Keep is already here".
    skipped: list[str] = field(default_factory=list)
    #: Links kept: "Covenant Keep (matched by name)".
    matched: list[str] = field(default_factory=list)
    #: Links dropped: "Laboratory Tower: not in this saga".
    dropped: list[str] = field(default_factory=list)
    #: Anything else worth saying before importing.
    notes: list[str] = field(default_factory=list)
    #: Roll tables a pack adds to a place, threat, faction or lord the
    #: saga already has: (that record, the tables it hasn't one of the
    #: same name of). Nothing else on the record changes.
    new_tables: list[tuple[Neighbour, list[dict[str, Any]]]] = field(
        default_factory=list
    )
    #: Existing records given an imported partner: (laboratory, owner id).
    new_owners: list[tuple[Laboratory, str]] = field(default_factory=list)
    #: (existing magus, the imported laboratory's id) to assign.
    new_labs: list[tuple[Character, str]] = field(default_factory=list)
    #: The saga's own maps a whole saga's import adds.
    maps: list[AtlasMap] = field(default_factory=list)
    #: Maps of a Tribunal the saga already has, which the file adds to it:
    #: (the Tribunal's id, the map).
    maps_for: list[tuple[str, AtlasMap]] = field(default_factory=list)
    #: The pins the import adds; a pack's never move or double one the
    #: saga has (Pin.from_pack).
    pins: list[Pin] = field(default_factory=list)
    #: Where the export's pictures are read from (None: it carries none).
    pictures: Pictures | None = None


class _Ids:
    """Hands out ids that are free in the target, keeping an imported
    record's own id when nothing has it."""

    def __init__(self, taken: Iterable[str]) -> None:
        self.taken = set(taken)

    def new(self, wanted: str, name: str) -> str:
        chosen = wanted
        if not chosen or chosen in self.taken:
            chosen = storage.generate_unique_id(
                name or wanted or "imported", self.taken
            )
        self.taken.add(chosen)
        return chosen


def _same_entry(a: Any, b: Any) -> bool:
    return (a.name.lower(), a.type, a.tier) == (b.name.lower(), b.type, b.tier)


def _same_spell(a: Spell, b: Spell) -> bool:
    return (a.name.lower(), a.technique, a.form, a.level) == (
        b.name.lower(),
        b.technique,
        b.form,
        b.level,
    )


@dataclass
class _Import:
    """One import being planned: the file's records, the target, and the
    old id -> new id maps every record's links are rewritten through."""

    source: Saga
    target: Saga
    plan: ImportPlan
    #: The export's links to records outside the file: kind -> id -> name.
    links: dict[str, dict[str, str]]
    #: What the file holds of the covenants it links to (kind -> id ->
    #: stub); older exports have none.
    stubs: dict[str, dict[str, CovenantStub]] = field(default_factory=dict)
    #: Whether a record the target has one of the same name of is taken
    #: for that one rather than added (a pack).
    match: bool = False
    #: Records in the file: kind -> old id -> new id.
    record_map: dict[str, dict[str, str]] = field(default_factory=dict)
    #: Records in the file the target already has: kind -> old ids.
    kept: dict[str, set[str]] = field(default_factory=dict)
    #: Records outside the file: kind -> old id -> the target's match, if any.
    outside: dict[str, dict[str, str | None]] = field(default_factory=dict)
    entry_map: dict[str, str] = field(default_factory=dict)
    spell_map: dict[str, str] = field(default_factory=dict)
    book_map: dict[str, str] = field(default_factory=dict)
    codex_map: dict[str, str] = field(default_factory=dict)
    device_map: dict[str, str] = field(default_factory=dict)
    tribunal_map: dict[str, str] = field(default_factory=dict)
    #: The Atlas's maps the import adds, by their id in the file.
    map_map: dict[str, str] = field(default_factory=dict)
    familiar_map: dict[str, str] = field(default_factory=dict)
    #: The ids of the possessions of the covenants added.
    possessions: set[str] = field(default_factory=set)

    def link(self, record_kind: str, old_id: str | None) -> str | None:
        if not old_id:
            return None
        if old_id in self.record_map[record_kind]:
            return self.record_map[record_kind][old_id]
        return self.outside[record_kind].get(old_id)

    def imported(self, record_kind: str, old_id: str | None) -> bool:
        """Whether the record is in the file and added (not kept)."""
        return (
            bool(old_id)
            and old_id in self.record_map[record_kind]
            and old_id not in self.kept.get(record_kind, set())
        )

    def held_by_kept(self, record_kind: str | None, old_id: str | None) -> bool:
        return bool(old_id) and old_id in self.kept.get(record_kind or "", set())

    def link_name(self, record_kind: str, old_id: str | None) -> str:
        return (self.links.get(record_kind) or {}).get(old_id or "", "")

    def new_spell_id(self, old_id: str | None) -> str | None:
        return self.spell_map.get(old_id or "", old_id)

    def entry(self, old_id: str) -> str:
        return self.entry_map.get(old_id, old_id)


def _map_records(job: _Import) -> None:
    """New ids for the covenants, characters, laboratories, places and
    neighbours in the file; in a pack, the target's own for one it has of
    the same name (and, for a neighbour, the same kind)."""
    source, target = job.source, job.target
    for record_kind, incoming, existing in (
        (COVENANT, source.covenants, target.covenants),
        (CHARACTER, source.characters, target.characters),
        (LABORATORY, source.laboratories, target.laboratories),
        (NEIGHBOUR, source.neighbours, target.neighbours),
        (CREATURE, source.creatures, target.creatures),
    ):
        ids = _Ids(r.id for r in existing)
        names = {r.name for r in existing}
        job.record_map[record_kind] = {}
        job.kept[record_kind] = set()
        for record in incoming:
            same = [
                r
                for r in existing
                if r.name == record.name
                and getattr(r, "kind", None) == getattr(record, "kind", None)
            ]
            if job.match and len(same) == 1:
                job.record_map[record_kind][record.id] = same[0].id
                job.kept[record_kind].add(record.id)
                job.plan.already.append(f"{_label(record_kind, record)} {record.name}")
                continue
            if record.name in names and record_kind not in (NEIGHBOUR, CREATURE):
                job.plan.notes.append(
                    f"This saga already has a {KIND_LABELS[record_kind].lower()} "
                    f"named {record.name}: the imported one is added beside it."
                )
            job.record_map[record_kind][record.id] = ids.new(record.id, record.name)


def _label(record_kind: str, record: Any) -> str:
    """ "Covenant", or a neighbour's kind: "Place", "Lord"."""
    if record_kind == NEIGHBOUR:
        return str(getattr(record, "kind", "") or "neighbour").capitalize()
    return KIND_LABELS[record_kind]


def _match_outside(job: _Import) -> None:
    """Links to records outside the file: by name, or dropped."""
    targets = {
        CHARACTER: job.target.characters,
        LABORATORY: job.target.laboratories,
        COVENANT: job.target.covenants,
        NEIGHBOUR: job.target.neighbours,
        CREATURE: job.target.creatures,
    }
    job.outside = {kind: {} for kind in LINKED_KINDS}
    for record_kind, named in job.links.items():
        if record_kind not in targets:
            continue
        for old_id, name in named.items():
            found = [r for r in targets[record_kind] if r.name == name]
            label = f"{KIND_LABELS[record_kind]} {name}"
            stub = (job.stubs.get(record_kind) or {}).get(old_id)
            if len(found) == 1:
                job.outside[record_kind][old_id] = found[0].id
                job.plan.matched.append(f"{label} (matched by name)")
            elif not found and record_kind == COVENANT and stub is not None:
                job.outside[record_kind][old_id] = _add_stub(job, old_id, stub)
            else:
                job.outside[record_kind][old_id] = None
                why = "not in this saga" if not found else "more than one here"
                job.plan.dropped.append(f"{label}: {why}")


def _add_stub(job: _Import, old_id: str, stub: CovenantStub) -> str:
    """A covenant the file only names, added with the aura it gives: its
    new id."""
    taken = [c.id for c in job.target.covenants]
    taken += [*job.record_map[COVENANT].values()]
    taken += [c.id for c in job.plan.stub_covenants]
    covenant = Covenant(
        id=_Ids(taken).new(old_id, stub["name"]),
        saga_id=job.target.id,
        name=stub["name"],
        aura=stub["aura"],
        aura_realm=stub["aura_realm"],
    )
    job.plan.stub_covenants.append(covenant)
    return covenant.id


def _read_stubs(data: dict[str, Any]) -> dict[str, dict[str, CovenantStub]]:
    """The file's covenant stubs, checked. Raises ValueError for one that
    isn't a name, a whole-number aura and a realm."""
    held = data.get("stubs") or {}
    raw = held.get(COVENANT) or {} if isinstance(held, dict) else None
    if not isinstance(raw, dict):
        raise ValueError("the export's covenant stubs aren't a list by id")
    stubs: dict[str, CovenantStub] = {}
    for old_id, stub in raw.items():
        name = stub.get("name") if isinstance(stub, dict) else None
        aura = stub.get("aura") if isinstance(stub, dict) else None
        realm = stub.get("aura_realm") if isinstance(stub, dict) else None
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(aura, int)
            or isinstance(aura, bool)
            or realm not in REALMS
        ):
            raise ValueError(
                f"the export's covenant {old_id!r} needs a name, an aura and "
                f"one of the realms ({', '.join(REALMS)})"
            )
        stubs[str(old_id)] = CovenantStub(name=name, aura=aura, aura_realm=realm)
    return {COVENANT: stubs}


def _map_entries(job: _Import) -> None:
    """User-made catalog entries: matched to the target's own, or added."""
    source, target = job.source, job.target
    for key, incoming, existing, shared in (
        (
            "custom_virtues_flaws",
            source.custom_virtues_flaws,
            target.custom_virtues_flaws,
            catalog.load_virtue_flaw_catalog_by_id(),
        ),
        (
            "custom_lab_virtues_flaws",
            source.custom_lab_virtues_flaws,
            target.custom_lab_virtues_flaws,
            catalog.load_lab_virtue_flaw_catalog_by_id(),
        ),
        (
            "custom_boons_hooks",
            source.custom_boons_hooks,
            target.custom_boons_hooks,
            catalog.load_covenant_boon_hook_catalog_by_id(),
        ),
    ):
        ids = _Ids([*shared, *(e.id for e in existing)])
        added: list[Any] = []
        for entry in incoming:
            same = next((e for e in existing if _same_entry(e, entry)), None)
            if same is not None:
                job.entry_map[entry.id] = same.id
                continue
            new_id = ids.new(entry.id, entry.name)
            job.entry_map[entry.id] = new_id
            added.append(replace(entry, id=new_id))
        job.plan.custom[key] = added
    # The saga's own Abilities are held by name: one the target already
    # knows by that name is its own; any other is added.
    in_use = catalog.saga_abilities()
    known = {a.name.lower() for a in catalog.load_ability_catalog() if a not in in_use}
    known |= {a.name.lower() for a in target.custom_abilities}
    ability_ids = _Ids(
        [
            *catalog.load_ability_catalog_by_id(),
            *(a.id for a in target.custom_abilities),
        ]
    )
    job.plan.custom["custom_abilities"] = [
        replace(a, id=ability_ids.new(a.id, a.name))
        for a in source.custom_abilities
        if a.name.lower() not in known
    ]


def _map_spells(job: _Import) -> None:
    """Spells: the saga's own, and each imported magus's inventions."""
    target = job.target
    spell_ids = _Ids(
        [
            *catalog.load_spell_catalog_by_id(),
            *(s.id for s in target.spells),
            *(s.id for c in target.characters for s in c.invented_spells),
        ]
    )
    for spell in job.source.spells:
        same = next((s for s in target.spells if _same_spell(s, spell)), None)
        if same is not None:
            job.spell_map[spell.id] = same.id
            continue
        new_id = spell_ids.new(spell.id, spell.name)
        job.spell_map[spell.id] = new_id
        spell.id = new_id
        job.plan.spells.append(spell)
    for character in job.source.characters:
        for spell in character.invented_spells:
            new_id = spell_ids.new(spell.id, spell.name)
            job.spell_map[spell.id] = new_id
            spell.id = new_id


def _plan_tribunals(job: _Import) -> None:
    """Each of the file's Tribunals: the target's of the same name, or a
    new one the import adds with what the file holds of it (its officers
    and proxies when they are here too; its Diary without what its
    entries changed, which belongs to the other saga)."""
    for tribunal in job.source.tribunals:
        key = tribunal.name.strip().casefold()
        known = next(
            (
                t
                for t in [*job.target.tribunals, *job.plan.tribunals]
                if t.name.strip().casefold() == key
            ),
            None,
        )
        if known is not None:
            job.tribunal_map[tribunal.id] = known.id
            _match_maps(job, known, tribunal.maps)
            if known in job.target.tribunals:
                line = f"Tribunal {known.name}"
                if job.match:
                    job.plan.already.append(line)
                elif f"{line} (matched by name)" not in job.plan.matched:
                    job.plan.matched.append(f"{line} (matched by name)")
            continue
        taken = [t.id for t in [*job.target.tribunals, *job.plan.tribunals]]
        proxies = {}
        for covenant_id, count in tribunal.proxies.items():
            found = job.link(COVENANT, covenant_id)
            if found is not None:
                proxies[found] = count
        added = replace(
            tribunal,
            id=_Ids(taken).new(tribunal.id, tribunal.name),
            praeco_id=job.link(CHARACTER, tribunal.praeco_id),
            quaesitor_id=job.link(CHARACTER, tribunal.quaesitor_id),
            proxies=proxies,
            diary=[replace(entry, changes=[]) for entry in tribunal.diary],
            meeting=None,
            maps=_new_maps(job, tribunal.maps),
        )
        job.tribunal_map[tribunal.id] = added.id
        job.plan.tribunals.append(added)


def _new_maps(job: _Import, found: list[AtlasMap]) -> list[AtlasMap]:
    """The file's maps, each given an id free in the target."""
    taken = _Ids(
        [m.id for m, _t in atlas_maps(job.target)]
        + [m.id for t in job.plan.tribunals for m in t.maps]
        + [m.id for m in job.plan.maps]
    )
    added = []
    for atlas_map in found:
        new_id = taken.new(atlas_map.id, atlas_map.name)
        job.map_map[atlas_map.id] = new_id
        added.append(replace(atlas_map, id=new_id))
    return added


def _match_maps(job: _Import, known: Tribunal, found: list[AtlasMap]) -> None:
    """A Tribunal the saga already has: each of the file's maps of it is
    the saga's own of that name, or one more the import adds to it."""
    for atlas_map in found:
        key = atlas_map.name.strip().casefold()
        mine = next((m for m in known.maps if m.name.strip().casefold() == key), None)
        if mine is not None:
            job.map_map[atlas_map.id] = mine.id
            continue
        [added] = _new_maps(job, [atlas_map])
        if known in job.plan.tribunals:
            known.maps.append(added)
        else:
            job.plan.maps_for.append((known.id, added))


#: A pin's kind (a Ref's) as the import's record kinds.
_PIN_KINDS: dict[str, str] = {
    "covenants": COVENANT,
    "neighbours": NEIGHBOUR,
    "creatures": CREATURE,
    "laboratories": LABORATORY,
}


def _plan_pins(job: _Import) -> None:
    """The file's pins, on the maps and records they became. A pack's pin
    is added only where the saga has no pin of that record on that map
    (one taken off it too), so importing a pack again never moves or
    doubles a pin; it is marked as the pack's."""
    placed = {(p.map_id, p.kind, p.record_id) for p in job.target.pins}
    for pin in job.source.pins:
        map_id = job.map_map.get(pin.map_id)
        record_kind = _PIN_KINDS.get(pin.kind)
        record_id = job.link(record_kind, pin.record_id) if record_kind else None
        if map_id is None or record_id is None:
            continue
        if job.match and (map_id, pin.kind, record_id) in placed:
            continue
        placed.add((map_id, pin.kind, record_id))
        job.plan.pins.append(
            replace(
                pin,
                map_id=map_id,
                record_id=record_id,
                from_pack=pin.from_pack or job.match,
            )
        )


def _plan_maps(job: _Import) -> None:
    """A whole saga's own maps (those of no Tribunal) come with it."""
    if job.plan.kind == SAGA:
        job.plan.maps += _new_maps(job, job.source.maps)


def _relink_stops(job: _Import, covenant: Covenant) -> None:
    """A covenant's stops and route, and its ships', through the maps:
    those at Places that aren't here are dropped."""

    def kept(stops: list[Any]) -> list[Any]:
        for stop in stops:
            stop.place_id = job.link(NEIGHBOUR, stop.place_id) or ""
        return [stop for stop in stops if stop.place_id]

    covenant.stops = kept(covenant.stops)
    covenant.route = kept(covenant.route)
    for record in covenant.possessions:
        if record.place_id is not None:
            record.place_id = job.link(NEIGHBOUR, record.place_id)
            if record.place_id is None:
                record.place_level = 0
        if record.ship is not None:
            record.ship.stops = kept(record.ship.stops)
            record.ship.aboard = [
                who
                for old in record.ship.aboard
                if (who := job.link(CHARACTER, old)) is not None
            ]


def _relink(job: _Import, record: Any) -> None:
    """A record's place, attitudes, favours and links, through the maps:
    those to records that aren't here are dropped (a favour's names
    stay)."""
    if hasattr(record, "place_id"):
        record.place_id = job.link(NEIGHBOUR, record.place_id)
        if record.place_id is None:
            record.place_level = 0
    if hasattr(record, "attitudes"):
        kept = []
        for attitude in record.attitudes:
            attitude.covenant_id = job.link(COVENANT, attitude.covenant_id)
            if attitude.covenant_id is not None:
                kept.append(attitude)
        record.attitudes = kept
    for favour in getattr(record, "favours", []):
        for side in ("owed_by", "owed_to"):
            old = getattr(favour, side)
            for record_kind in (COVENANT, CHARACTER, NEIGHBOUR):
                new = job.link(record_kind, old)
                if new is not None:
                    setattr(favour, side, new)
                    break
    if hasattr(record, "links"):
        maps: dict[str, Callable[[str], str | None]] = {
            "characters": lambda old: job.link(CHARACTER, old),
            "covenants": lambda old: job.link(COVENANT, old),
            "places": lambda old: job.link(NEIGHBOUR, old),
            "creatures": lambda old: job.link(CREATURE, old),
            "books": job.book_map.get,
            "familiars": job.familiar_map.get,
            "possessions": lambda old: old if old in job.possessions else None,
        }
        kept_links = []
        for link in record.links:
            mapped = maps.get(link.kind, lambda _old: None)(link.target_id)
            if mapped is not None:
                link.target_id = mapped
                kept_links.append(link)
        record.links = kept_links


def _plan_covenants(job: _Import) -> None:
    for covenant in job.source.covenants:
        if covenant.id in job.kept[COVENANT]:
            continue
        covenant.id = job.record_map[COVENANT][covenant.id]
        covenant.saga_id = job.target.id
        covenant.tribunal_id = job.tribunal_map.get(covenant.tribunal_id or "")
        covenant.liege_id = job.link(COVENANT, covenant.liege_id)
        _relink(job, covenant)
        _relink_stops(job, covenant)
        for held in covenant.boons_hooks:
            held.vf_id = job.entry(held.vf_id)
        for person in covenant.inhabitants:
            if person.character_id:
                # Unmatched: the entry stays, as a person with no sheet.
                person.character_id = job.link(CHARACTER, person.character_id)
        # A seal whose magus isn't here goes: a seal is a magus's, not a name.
        charter = covenant.charter_of_covenant
        for seal in charter.seals:
            seal.character_id = job.link(CHARACTER, seal.character_id) or ""
        charter.seals = [s for s in charter.seals if s.character_id]
        kept = []
        for possession in covenant.possessions:
            if possession.lab_id:
                possession.lab_id = job.link(LABORATORY, possession.lab_id)
                if possession.lab_id is None and possession.ship is None:
                    continue  # only the extras of a laboratory that isn't here
            if possession.location_kind in (CHARACTER, LABORATORY):
                place = job.link(possession.location_kind, possession.location_id)
                if place is None:
                    possession.location_kind, place = COVENANT, covenant.id
                possession.location_id = place
            elif possession.location_kind == COVENANT:
                possession.location_id = covenant.id
            kept.append(possession)
        covenant.possessions = kept
        job.plan.covenants.append(covenant)


def _plan_characters(job: _Import) -> None:
    for character in job.source.characters:
        if character.id in job.kept[CHARACTER]:
            continue
        old_id = character.id
        character.id = job.record_map[CHARACTER][old_id]
        character.covenant_id = job.link(COVENANT, character.covenant_id)
        if character.stay is not None:
            # A guest of a covenant this saga hasn't is a guest no more.
            host = job.link(COVENANT, character.stay.host_id)
            if host is None:
                character.stay = None
            else:
                character.stay.host_id = host
        for held in character.virtues_flaws:
            held.vf_id = job.entry(held.vf_id)
        for known in character.spells_known:
            known.spell_id = job.new_spell_id(known.spell_id) or known.spell_id
        for spent in character.creation_xp:
            spent.target = job.spell_map.get(spent.target, spent.target)
        character.tractatus_read = [
            job.book_map[b] for b in character.tractatus_read if b in job.book_map
        ]
        character.summae_read = [
            job.book_map[b] for b in character.summae_read if b in job.book_map
        ]
        access = {}
        for author, level in character.lab_text_access.items():
            known_author = (
                author in job.record_map[CHARACTER] or author in job.outside[CHARACTER]
            )
            if not known_author:
                access[author] = level  # an author named, not linked
                continue
            # An author who isn't here is remembered by name.
            new_author = job.link(CHARACTER, author) or job.link_name(CHARACTER, author)
            access[new_author] = level
        character.lab_text_access = access
        _relink(job, character)
        job.plan.characters.append(character)


def _plan_laboratories(job: _Import) -> None:
    for lab in job.source.laboratories:
        if lab.id in job.kept[LABORATORY]:
            continue
        lab.id = job.record_map[LABORATORY][lab.id]
        lab.covenant_id = job.link(COVENANT, lab.covenant_id)
        _relink(job, lab)
        for held in lab.virtues_flaws:
            held.vf_id = job.entry(held.vf_id)
        job.plan.laboratories.append(lab)
    _pair_magi_and_labs(job)


def _pair_magi_and_labs(job: _Import) -> None:
    """A magus and a laboratory point at each other: keep the pair only when
    both ends can (an existing record already paired is left alone)."""
    plan, target = job.plan, job.target
    by_new_id = {c.id: c for c in plan.characters}
    labs_by_new_id = {lab.id: lab for lab in plan.laboratories}
    for lab in plan.laboratories:
        old_owner = lab.owner_id
        owner_id = job.link(CHARACTER, old_owner)
        lab.owner_id = None
        if owner_id is None:
            continue
        if owner_id in by_new_id:
            lab.owner_id = owner_id  # its magus is imported with it
            continue
        owner = target.character(owner_id)
        if owner is not None and owner.assigned_lab_id is None:
            lab.owner_id = owner_id
            plan.new_labs.append((owner, lab.id))
        elif owner is not None:
            plan.dropped.append(
                f"{lab.name}'s owner {owner.name}: already has a laboratory here"
            )
    for character in plan.characters:
        old_lab = character.assigned_lab_id
        lab_id = job.link(LABORATORY, old_lab)
        character.assigned_lab_id = None
        if lab_id is None:
            continue
        if lab_id in labs_by_new_id:
            if labs_by_new_id[lab_id].owner_id == character.id:
                character.assigned_lab_id = lab_id
            continue
        existing_lab = target.laboratory(lab_id)
        if existing_lab is not None and existing_lab.owner_id is None:
            character.assigned_lab_id = lab_id
            plan.new_owners.append((existing_lab, character.id))
        elif existing_lab is not None:
            plan.dropped.append(
                f"{character.name}'s laboratory {existing_lab.name}: already has "
                "an owner here"
            )


def _map_familiars(job: _Import) -> None:
    familiar_ids = _Ids(f.id for f in job.target.familiars)
    job.familiar_map = {
        f.id: familiar_ids.new(f.id, f.name)
        for f in job.source.familiars
        if job.imported(CHARACTER, f.character_id)
    }


def _plan_familiars(job: _Import) -> None:
    for familiar in job.source.familiars:
        if job.held_by_kept(CHARACTER, familiar.character_id):
            job.plan.skipped.append(_held_line("Familiar", familiar.name))
            continue
        if not job.imported(CHARACTER, familiar.character_id):
            continue
        familiar.id = job.familiar_map[familiar.id]
        familiar.character_id = job.record_map[CHARACTER][familiar.character_id]
        for held in familiar.virtues_flaws:
            held.vf_id = job.entry(held.vf_id)
        job.plan.familiars.append(familiar)


def _plan_devices(job: _Import) -> None:
    device_ids = _Ids(d.id for d in job.target.enchanted_devices)
    job.device_map = {
        d.id: device_ids.new(d.id, d.name) for d in job.source.enchanted_devices
    }
    for device in job.source.enchanted_devices:
        if job.held_by_kept(device.holder_kind, device.holder_id):
            job.plan.skipped.append(_held_line("Enchanted device", device.name))
            continue
        device.id = job.device_map[device.id]
        device.holder_id = (
            job.link(device.holder_kind or "", device.holder_id)
            if (device.holder_kind in job.record_map)
            else None
        )
        if device.holder_id is None:
            device.holder_kind = None
        if device.maker_id:
            maker = job.link(CHARACTER, device.maker_id)
            if maker is None and not device.maker_name:
                device.maker_name = job.link_name(CHARACTER, device.maker_id)
            device.maker_id = maker
        job.plan.devices.append(device)
    # A laboratory's magic items name their devices by id.
    for lab in job.plan.laboratories:
        for benefit in lab.item_benefits:
            benefit.device_id = job.device_map.get(benefit.device_id, "")
        for held in lab.virtues_flaws:
            if ITEM_DEVICE_PARAM in held.params:
                held.params[ITEM_DEVICE_PARAM] = job.device_map.get(
                    held.params[ITEM_DEVICE_PARAM], ""
                )


def _plan_books(job: _Import) -> None:
    for book in job.source.books:
        if job.held_by_kept(book.owner_kind, book.owner_id):
            job.plan.skipped.append(_held_line("Book", book.name))
            continue
        book.id = job.book_map[book.id]
        book.owner_id = (
            job.link(book.owner_kind or "", book.owner_id)
            if (book.owner_kind in job.record_map)
            else None
        )
        if book.owner_id is None:
            book.owner_kind = None
        if book.author_id:
            author = job.link(CHARACTER, book.author_id)
            if author is None and not book.author:
                book.author = job.link_name(CHARACTER, book.author_id)
            book.author_id = author
        book.spell_id = job.new_spell_id(book.spell_id)
        book.codex_id = job.codex_map.get(book.codex_id or "")
        book.commentary_on = job.book_map.get(book.commentary_on or "")
        book.device_id = job.device_map.get(book.device_id or "")
        job.plan.books.append(book)
    held = {b.codex_id for b in job.plan.books}
    for codex in job.source.codices:
        codex.id = job.codex_map[codex.id]
        if codex.id in held:
            job.plan.codices.append(codex)


def _held_line(what: str, name: str) -> str:
    return f"{what} {name}: its holder is already here"


def _plan_neighbours(job: _Import) -> None:
    for neighbour in job.source.neighbours:
        if neighbour.id in job.kept[NEIGHBOUR]:
            _plan_new_tables(job, neighbour)
            continue
        neighbour.id = job.record_map[NEIGHBOUR][neighbour.id]
        neighbour.answers_to = job.link(NEIGHBOUR, neighbour.answers_to)
        neighbour.ruler = _ruler(job, neighbour.ruler)
        if sites.TRAVELS_WITH in neighbour.details:
            covenant = job.link(COVENANT, neighbour.details.pop(sites.TRAVELS_WITH))
            if covenant is not None:
                neighbour.details[sites.TRAVELS_WITH] = covenant
        _relink_roster(job, neighbour)
        if neighbour.details.get(places.LANDS):
            lands = job.tribunal_map.get(str(neighbour.details[places.LANDS]))
            if lands:
                neighbour.details[places.LANDS] = lands
            else:
                del neighbour.details[places.LANDS]
        _relink(job, neighbour)
        job.plan.neighbours.append(neighbour)


def _plan_new_tables(job: _Import, neighbour: Neighbour) -> None:
    """The pack's roll tables on a record the saga already has, that the
    saga's copy has none of the same name of (ignoring case): added to
    it, so a pack can bring tables to a Tribunal's places. Importing
    again adds nothing, and a table the saga has is never overwritten."""
    incoming = neighbour.details.get(TABLES)
    own = job.target.neighbour(job.record_map[NEIGHBOUR][neighbour.id])
    if not isinstance(incoming, list) or own is None:
        return
    had = {
        str(t.get("name") or "").strip().casefold()
        for t in own.details.get(TABLES) or []
        if isinstance(t, dict)
    }
    added = []
    for table in incoming:
        name = str(table.get("name") or "").strip() if isinstance(table, dict) else ""
        if name and name.casefold() not in had:
            had.add(name.casefold())
            added.append({**table, "last": ""})
    if added:
        job.plan.new_tables.append((own, added))


#: A faction's member's kind (memberships.MEMBER_KINDS) as the import's.
_MEMBER_KINDS = {
    "characters": CHARACTER,
    "covenants": COVENANT,
    "creatures": CREATURE,
    "neighbours": NEIGHBOUR,
}


def _relink_roster(job: _Import, neighbour: Neighbour) -> None:
    """A faction's members through the maps; a member left out of the
    import (and not already in the saga) is left off."""
    roster = neighbour.details.get("roster")
    if not isinstance(roster, list):
        return
    kept = []
    for member in roster:
        kind, _, old = str(member.get("who") or "").partition(":")
        new = job.link(_MEMBER_KINDS[kind], old) if kind in _MEMBER_KINDS else None
        if new is not None:
            kept.append({**member, "who": f"{kind}:{new}"})
    neighbour.details["roster"] = kept


def _ruler(job: _Import, old: str) -> str:
    """A neighbour's ruler through the maps: the record's new id, or its
    name when it isn't here; a typed name stays."""
    for record_kind in (CHARACTER, NEIGHBOUR, CREATURE):
        new = job.link(record_kind, old)
        if new is not None:
            return new
        named = job.link_name(record_kind, old)
        if named:
            return named
    return old


def _plan_creatures(job: _Import) -> None:
    for creature in job.source.creatures:
        if creature.id in job.kept[CREATURE]:
            continue
        creature.id = job.record_map[CREATURE][creature.id]
        for held in creature.virtues_flaws:
            held.vf_id = job.entry(held.vf_id)
        _relink(job, creature)
        job.plan.creatures.append(creature)


def _plan_calendar(job: _Import) -> None:
    """Calendar entries: each for the whole saga or for a covenant that is
    here; one the saga already has is skipped."""
    for entry in job.source.calendar:
        title = f"Calendar entry {entry.title} ({entry.season} {entry.year})"
        if entry.covenant_id:
            entry.covenant_id = job.link(COVENANT, entry.covenant_id)
            if entry.covenant_id is None:
                job.plan.skipped.append(f"{title}: its covenant isn't here")
                continue
        same = (entry.title, entry.year, entry.season, entry.covenant_id)
        if any(
            (e.title, e.year, e.season, e.covenant_id) == same
            for e in [*job.target.calendar, *job.plan.calendar]
        ):
            job.plan.skipped.append(f"{title}: already in the calendar")
            continue
        job.plan.calendar.append(entry)


#: How each kind of record in the file is added, in order: a laboratory
#: pairs with a magus planned before it, and a familiar follows its magus.
_PLANNERS: dict[str, Callable[[_Import], None]] = {
    "tribunal": _plan_tribunals,
    "maps": _plan_maps,
    COVENANT: _plan_covenants,
    CHARACTER: _plan_characters,
    LABORATORY: _plan_laboratories,
    "familiar": _plan_familiars,
    "device": _plan_devices,
    "book": _plan_books,
    NEIGHBOUR: _plan_neighbours,
    CREATURE: _plan_creatures,
    "calendar": _plan_calendar,
    "pins": _plan_pins,
}


def plan_import(
    target: Saga,
    data: dict[str, Any],
    *,
    same_ids: dict[str, dict[str, str]] | None = None,
    pictures: Pictures | None = None,
) -> ImportPlan:
    """Work out an import of `data` (from read()) into `target`, changing
    nothing yet: apply() does it. `same_ids` (kind -> the file's id -> an
    id) gives records in the file the id they are to have, whatever is
    free: updating a record from a file keeps the record's own id. A
    pack's records are matched by name to the target's own. `pictures`
    is where the file's maps and portraits are read from."""
    # Runs the load-time migrations.
    source = Saga.from_dict(data["saga"], lab_feature_names=catalog.lab_feature_names())
    shapes.check_built(source)
    job = _Import(
        source=source,
        target=target,
        match=data["kind"] == PACK,
        plan=ImportPlan(
            kind=data["kind"],
            name=str(data.get("name") or ""),
            from_saga=str(data.get("from_saga") or ""),
        ),
        links=data.get("links") or {},
        stubs=_read_stubs(data),
    )
    _map_records(job)
    for record_kind, ids in (same_ids or {}).items():
        job.record_map[record_kind].update(ids)
    _match_outside(job)
    _map_entries(job)
    _map_spells(job)
    book_ids = _Ids(b.id for b in target.books)
    job.book_map = {b.id: book_ids.new(b.id, b.name) for b in source.books}
    codex_ids = _Ids(c.id for c in target.codices)
    job.codex_map = {c.id: codex_ids.new(c.id, c.name) for c in source.codices}
    _map_familiars(job)
    job.possessions = {
        p.id
        for c in source.covenants
        if c.id not in job.kept[COVENANT]
        for p in c.possessions
    }
    for planner in _PLANNERS.values():
        planner(job)
    job.plan.pictures = pictures
    return job.plan


def _count(number: int, noun: str) -> str:
    if number == 1:
        return f"1 {noun}"
    plural = f"{noun[:-1]}ies" if noun.endswith("y") else f"{noun}s"
    return f"{number} {plural}"


def preview(plan: ImportPlan) -> str:
    """What the import will do, for the user to confirm (plain text)."""
    origin = f" from {plan.from_saga}" if plan.from_saga else ""
    lines = [f"Import {KIND_LABELS[plan.kind]}: {plan.name}{origin}", "", "Adds:"]
    lines += [f"  Covenant: {c.name}" for c in plan.covenants]
    lines += [
        f"  Covenant: {c.name} (only its name and aura, {c.aura} {c.aura_realm})"
        for c in plan.stub_covenants
    ]
    lines += [f"  Tribunal: {t.name}" for t in plan.tribunals]
    lines += [f"  Laboratory: {lab.name}" for lab in plan.laboratories]
    lines += [f"  Character: {c.name} ({c.type})" for c in plan.characters]
    lines += [f"  Familiar: {f.name}" for f in plan.familiars]
    lines += [f"  {_label(NEIGHBOUR, n)}: {n.name}" for n in plan.neighbours]
    lines += [f"  Creature: {c.name}" for c in plan.creatures]
    for number, noun in (
        (len(plan.books), "book"),
        (len(plan.devices), "enchanted device"),
        (len(plan.spells), "spell"),
        (sum(len(added) for added in plan.custom.values()), "House Rule"),
        (len(plan.calendar), "calendar entry"),
    ):
        if number:
            lines.append(f"  {_count(number, noun)}")
    lines += [
        f"  {_count(len(tables), 'roll table')} to {own.name}"
        for own, tables in plan.new_tables
    ]
    if plan.already:
        lines += ["", "Already here, kept as they are:"]
        lines += [f"  {text}" for text in plan.already]
    if plan.skipped:
        lines += ["", "Skipped:"] + [f"  {text}" for text in plan.skipped]
    if plan.matched:
        lines += ["", "Links kept:"] + [f"  {text}" for text in plan.matched]
    if plan.dropped:
        lines += ["", "Links dropped:"] + [f"  {text}" for text in plan.dropped]
    if plan.notes:
        lines += [""] + plan.notes
    return "\n".join(lines)


def _copy_pictures(target: Saga, plan: ImportPlan) -> None:
    """Copy the pictures the file carries into this computer's folders: a
    map's under its own name (named by its bytes, so one already there is
    the same picture and is kept), a portrait under its character's new
    name. A picture the file doesn't carry is left as it was named: it
    shows if this computer has it, as on the computer it came from."""
    pictures = plan.pictures
    if pictures is None:
        return
    for atlas_map in [
        *(m for t in plan.tribunals for m in t.maps),
        *plan.maps,
        *(m for _t, m in plan.maps_for),
    ]:
        name = atlas_map.picture
        if not name or (storage.maps_dir() / name).is_file():
            continue
        found = pictures.get(MAPS, name)
        if found is not None:
            storage.maps_dir().mkdir(parents=True, exist_ok=True)
            (storage.maps_dir() / name).write_bytes(found)
    for character in plan.characters:
        found = pictures.get(PORTRAITS, character.portrait)
        if found is None:
            continue
        suffix = Path(character.portrait).suffix
        name = portraits.file_name(target, character, suffix)
        storage.portraits_dir().mkdir(parents=True, exist_ok=True)
        (storage.portraits_dir() / name).write_bytes(found)
        character.portrait = name


def apply(target: Saga, plan: ImportPlan) -> None:
    """Add everything in `plan` to `target` (the caller saves it)."""
    add_records(target, plan)
    _copy_pictures(target, plan)
    catalog.use_saga(target)


def add_records(target: Saga, plan: ImportPlan) -> None:
    """Add `plan`'s records to `target` and nothing more: no pictures
    copied, no catalog switched. apply() does the whole import; this
    alone lets a preview plan a second import over a copy of the saga
    with the first one's records in it."""
    target.covenants += plan.covenants + plan.stub_covenants
    target.tribunals += plan.tribunals
    target.characters += plan.characters
    target.laboratories += plan.laboratories
    target.familiars += plan.familiars
    target.enchanted_devices += plan.devices
    target.books += plan.books
    target.codices += plan.codices
    target.spells += plan.spells
    target.custom_virtues_flaws += plan.custom.get("custom_virtues_flaws", [])
    target.custom_lab_virtues_flaws += plan.custom.get("custom_lab_virtues_flaws", [])
    target.custom_boons_hooks += plan.custom.get("custom_boons_hooks", [])
    target.custom_abilities += plan.custom.get("custom_abilities", [])
    target.neighbours += plan.neighbours
    target.creatures += plan.creatures
    target.calendar += plan.calendar
    for own, tables in plan.new_tables:
        own.details[TABLES] = [*(own.details.get(TABLES) or []), *tables]
    for lab, owner_id in plan.new_owners:
        lab.owner_id = owner_id
    for owner, lab_id in plan.new_labs:
        owner.assigned_lab_id = lab_id
    target.maps += plan.maps
    for tribunal_id, atlas_map in plan.maps_for:
        found = target.tribunal(tribunal_id)
        if found is not None:
            found.maps.append(atlas_map)
    target.pins += plan.pins
    places.sync(target)
