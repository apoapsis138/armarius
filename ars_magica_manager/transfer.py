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
it. Nothing already in the target saga is changed, except that a
laboratory with no owner (or a magus with no laboratory) can be given the
imported partner the file names. Everything imported gets ids that are
free in the target. Season plans, season records and lab projects under
way stay behind.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any

from . import __version__, catalog, places, storage
from .files import write_atomic
from .models import (
    ITEM_DEVICE_PARAM,
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
    Saga,
    Spell,
    Tribunal,
)

FORMAT = "armarius-export"
#: The labels an import accepts: exports made before the app was Armarius
#: carry the older one.
FORMATS = (FORMAT, "ars-magica-manager-export")
SUFFIX = ".amm.json"
CHARACTER, LABORATORY, COVENANT = "character", "laboratory", "covenant"
#: The kind of a whole saga's export, and of a content pack's.
SAGA, PACK = "saga", "pack"
#: The kind of record a place or neighbour is, among the links.
NEIGHBOUR = "neighbour"
#: The kind of record a creature of the Bestiary is.
CREATURE = "creature"
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
    only) adds its laboratories and characters."""
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


def without_secrets(data: dict[str, Any]) -> dict[str, Any]:
    """An export with every record's secrets left out: what a player
    signed in to a hosted copy downloads."""
    kept = dict(data)
    kept["saga"] = {
        key: (
            [
                {**r, "secrets": ""} if isinstance(r, dict) and "secrets" in r else r
                for r in value
            ]
            if isinstance(value, list)
            else value
        )
        for key, value in data["saga"].items()
    }
    return kept


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
        "saga": content,
    }


def export_to(
    path: Path, saga: Saga, record: Record, *, with_members: bool = False
) -> Path:
    """Write `record`'s export to `path` (its folder is made if needed)."""
    data = export_data(saga, record, with_members=with_members)
    write_atomic(path, json.dumps(data, indent=2))
    return path


def saga_file_name(saga: Saga) -> str:
    return f"{storage.slugify(saga.name) or SAGA}{SUFFIX}"


def export_saga_data(saga: Saga) -> dict[str, Any]:
    """The export of the whole saga as JSON-ready data: every record and
    what they hold, so nothing it points at is left outside it."""
    return {
        "format": FORMAT,
        "app_version": __version__,
        "kind": SAGA,
        "name": saga.name,
        "from_saga": saga.name,
        "links": {kind: {} for kind in LINKED_KINDS},
        "saga": asdict(
            replace(saga, tribunals=[replace(t, meeting=None) for t in saga.tribunals])
        ),
    }


def export_saga_to(path: Path, saga: Saga) -> Path:
    """Write the whole saga's export to `path` (its folder is made if
    needed)."""
    write_atomic(path, json.dumps(export_saga_data(saga), indent=2))
    return path


# ------------------------------------------------------------------ import


def read(path: Path) -> dict[str, Any]:
    """An export file's data. Raises ValueError for anything else."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as problem:
        raise ValueError(f"not a JSON file ({problem.msg})") from problem
    if not isinstance(data, dict) or data.get("format") not in FORMATS:
        raise ValueError(
            "not an Armarius export (export a covenant, laboratory or "
            "character from its sheet, or a saga from Saga Management, first)"
        )
    if data.get("kind") not in KIND_LABELS or not isinstance(data.get("saga"), dict):
        raise ValueError("the export is incomplete")
    return data


@dataclass
class ImportPlan:
    """What importing an export into a saga will do: the records to add,
    already given their new ids and links, and what to tell the user."""

    kind: str
    name: str
    from_saga: str
    covenants: list[Covenant] = field(default_factory=list)
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
    #: Existing records given an imported partner: (laboratory, owner id).
    new_owners: list[tuple[Laboratory, str]] = field(default_factory=list)
    #: (existing magus, the imported laboratory's id) to assign.
    new_labs: list[tuple[Character, str]] = field(default_factory=list)


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
            if len(found) == 1:
                job.outside[record_kind][old_id] = found[0].id
                job.plan.matched.append(f"{label} (matched by name)")
            else:
                job.outside[record_kind][old_id] = None
                why = "not in this saga" if not found else "more than one here"
                job.plan.dropped.append(f"{label}: {why}")


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
        )
        job.tribunal_map[tribunal.id] = added.id
        job.plan.tribunals.append(added)


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
                if possession.lab_id is None:
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
            continue
        neighbour.id = job.record_map[NEIGHBOUR][neighbour.id]
        neighbour.answers_to = job.link(NEIGHBOUR, neighbour.answers_to)
        neighbour.ruler = _ruler(job, neighbour.ruler)
        _relink(job, neighbour)
        job.plan.neighbours.append(neighbour)


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
    COVENANT: _plan_covenants,
    CHARACTER: _plan_characters,
    LABORATORY: _plan_laboratories,
    "familiar": _plan_familiars,
    "device": _plan_devices,
    "book": _plan_books,
    NEIGHBOUR: _plan_neighbours,
    CREATURE: _plan_creatures,
    "calendar": _plan_calendar,
}


def plan_import(
    target: Saga,
    data: dict[str, Any],
    *,
    same_ids: dict[str, dict[str, str]] | None = None,
) -> ImportPlan:
    """Work out an import of `data` (from read()) into `target`, changing
    nothing yet: apply() does it. `same_ids` (kind -> the file's id -> an
    id) gives records in the file the id they are to have, whatever is
    free: updating a record from a file keeps the record's own id. A
    pack's records are matched by name to the target's own."""
    # Runs the load-time migrations.
    source = Saga.from_dict(data["saga"], lab_feature_names=catalog.lab_feature_names())
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


def apply(target: Saga, plan: ImportPlan) -> None:
    """Add everything in `plan` to `target` (the caller saves it)."""
    target.covenants += plan.covenants
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
    for lab, owner_id in plan.new_owners:
        lab.owner_id = owner_id
    for owner, lab_id in plan.new_labs:
        owner.assigned_lab_id = lab_id
    places.sync(target)
    catalog.use_saga(target)
