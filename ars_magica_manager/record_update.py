"""Updating a covenant, laboratory or character from an export of it
(transfer.py), for example after working on it on another computer.

The file's version replaces the record's contents, and what travels with
it in an export replaces what it holds here: a character's familiar,
devices and books, a laboratory's or covenant's books and devices. The
record keeps its id, so everything in the saga that points at it still
does, and keeps where it sits in this saga: a character's covenant and
laboratory, a laboratory's covenant and owner. Other links in the file are
matched by name, as an import's are. A covenant's file exported with its
laboratories and characters updates the covenant only.

`plan_update` works out what would change, changing nothing; `apply`
makes the change.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from dataclasses import asdict, dataclass, field, fields, is_dataclass, replace
from typing import Any

from . import books as bk
from . import catalog, transfer
from .models import Book, Character, Covenant, EnchantedDevice, Familiar, Saga

#: Each kind's links to where it sits in the saga, kept from this saga.
PLACEMENT: dict[str, tuple[str, ...]] = {
    transfer.CHARACTER: ("covenant_id", "assigned_lab_id"),
    transfer.LABORATORY: ("covenant_id", "owner_id"),
    transfer.COVENANT: (),
}

#: The saga lists a kind of record is kept in, in an export's saga.
_LISTS: dict[str, str] = {
    transfer.CHARACTER: "characters",
    transfer.LABORATORY: "laboratories",
    transfer.COVENANT: "covenants",
}

#: Labels for fields whose name doesn't read well on its own.
_LABELS: dict[str, str] = {
    "virtues_flaws": "Virtues & Flaws",
    "boons_hooks": "Boons & Hooks",
    "raw_vis": "Raw Vis",
    "xp": "Experience",
    "creation_xp": "Creation experience",
    "spells_known": "Spells known",
    "invented_spells": "Invented spells",
    "inventory": "Personal gear",
    "lab_text_access": "Lab texts read",
    "tractatus_read": "Tractatus read",
    "summae_read": "Summae read",
}


@dataclass
class UpdatePlan:
    """What updating `record` from a file will do."""

    record: transfer.Record
    #: The file's version, with this saga's ids and links.
    incoming: transfer.Record
    #: The import planned around it: what it holds, and spells and house
    #: rules the saga doesn't have yet.
    imported: transfer.ImportPlan
    #: What changes, one line each ("Abilities: 1 added, 2 changed").
    changes: list[str] = field(default_factory=list)
    #: What the record holds here, to be replaced by the file's.
    familiars: list[Familiar] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    devices: list[EnchantedDevice] = field(default_factory=list)
    #: Anything else worth saying before updating.
    notes: list[str] = field(default_factory=list)


def label(name: str) -> str:
    """A field's name as the preview says it."""
    return _LABELS.get(name, name.replace("_", " ").capitalize())


# -------------------------------------------------------------- planning


def _held(saga: Saga, record: transfer.Record) -> tuple[list, list, list]:
    """The familiars, books and devices `record` holds here: what an
    export of it carries."""
    kind = transfer.kind_of(record)
    familiars = (
        [f for f in saga.familiars if f.character_id == record.id]
        if kind == transfer.CHARACTER
        else []
    )
    books = [b for b in saga.books if (b.owner_kind, b.owner_id) == (kind, record.id)]
    devices = [
        d
        for d in saga.enchanted_devices
        if (d.holder_kind, d.holder_id) == (kind, record.id)
    ]
    return familiars, books, devices


def _only_the_record(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """`data` with only its record and what that holds, its placement
    links blanked (they are kept from this saga), and notes on what was
    left out."""
    data = copy.deepcopy(data)
    kind = data["kind"]
    content = data["saga"]
    links: dict[str, dict[str, str]] = data.setdefault("links", {})
    notes: list[str] = []
    main = content[_LISTS[kind]][0]
    if kind == transfer.COVENANT:
        members = [
            (record_kind, record)
            for record_kind in (transfer.CHARACTER, transfer.LABORATORY)
            for record in content.get(_LISTS[record_kind], [])
        ]
        if members:
            notes.append(
                f"The file also holds {len(members)} of its laboratories and "
                "characters: they are left as they are here (update each from "
                "its own export)."
            )
        for record_kind, record in members:
            # Pointed at by name now, as anything outside the file is.
            links.setdefault(record_kind, {})[record["id"]] = record["name"]
        content["characters"], content["laboratories"] = [], []
        content["familiars"] = []
        owner = (transfer.COVENANT, main["id"])
        content["books"] = [
            b
            for b in content.get("books", [])
            if (b["owner_kind"], b["owner_id"]) == owner
        ]
        content["enchanted_devices"] = [
            d
            for d in content.get("enchanted_devices", [])
            if (d["holder_kind"], d["holder_id"]) == owner
        ]
    for name in PLACEMENT[kind]:
        main[name] = None
    # Links only the placement used say nothing now.
    used = set(transfer.strings(content))
    for named in links.values():
        for old_id in [i for i in named if i not in used]:
            del named[old_id]
    return data, notes


def plan_update(
    saga: Saga, record: transfer.Record, data: dict[str, Any]
) -> UpdatePlan:
    """Work out updating `record` from `data` (transfer.read()), changing
    nothing. Raises ValueError when the file holds another kind of
    record."""
    kind = transfer.kind_of(record)
    if data["kind"] != kind:
        found = transfer.KIND_LABELS[data["kind"]].lower()
        raise ValueError(
            f"it holds a {found}, not a {transfer.KIND_LABELS[kind].lower()}"
        )
    if not data["saga"].get(_LISTS[kind]):
        raise ValueError("the export is incomplete")
    data, notes = _only_the_record(data)
    familiars, books, devices = _held(saga, record)
    # The saga as it would be without the record and what it holds, so
    # their ids are free for the file's and its name is not taken.
    others = replace(
        saga,
        covenants=[c for c in saga.covenants if c is not record],
        characters=[c for c in saga.characters if c is not record],
        laboratories=[lab for lab in saga.laboratories if lab is not record],
        familiars=[f for f in saga.familiars if f not in familiars],
        books=[b for b in saga.books if b not in books],
        enchanted_devices=[d for d in saga.enchanted_devices if d not in devices],
    )
    file_id = data["saga"][_LISTS[kind]][0]["id"]
    imported = transfer.plan_import(others, data, same_ids={kind: {file_id: record.id}})
    incoming = getattr(imported, _LISTS[kind])[0]
    for name in PLACEMENT[kind]:
        setattr(incoming, name, getattr(record, name))
    if isinstance(record, Character) and isinstance(incoming, Character):
        incoming.background.player_id = record.background.player_id
    if isinstance(record, Covenant) and isinstance(incoming, Covenant):
        incoming.saga_id = record.saga_id
    plan = UpdatePlan(
        record,
        incoming,
        imported,
        familiars=familiars,
        books=books,
        devices=devices,
        notes=notes + imported.notes,
    )
    plan.changes = _changes(plan)
    return plan


# ---------------------------------------------------------- what changes


def _bare(value: Any) -> Any:
    """`value` as JSON-shaped data without its own ids and links, which
    differ from saga to saga without the thing being different."""
    if is_dataclass(value) and not isinstance(value, type):
        value = asdict(value)
    if isinstance(value, dict):
        return {
            k: _bare(v)
            for k, v in value.items()
            if not (isinstance(k, str) and (k == "id" or k.endswith("_id")))
        }
    if isinstance(value, list):
        return [_bare(v) for v in value]
    return value


def _text(value: Any) -> str:
    return json.dumps(_bare(value), sort_keys=True)


def _key(item: Any) -> Any:
    """What says two entries of a list are the same entry, if anything."""
    if isinstance(item, dict):
        for name in ("name", "vf_id", "spell_id", "art", "kind"):
            if item.get(name):
                return (name, item[name])
    return None


def _counts(added: int, removed: int, changed: int) -> str:
    parts = [
        f"{number} {word}"
        for number, word in (
            (added, "added"),
            (removed, "removed"),
            (changed, "changed"),
        )
        if number
    ]
    return ", ".join(parts)


def _list_change(old: list[Any], new: list[Any]) -> str:
    """How two lists differ: entries added, removed and changed."""
    olds, news = [_bare(v) for v in old], [_bare(v) for v in new]
    by_key_old = {_key(v): v for v in olds if _key(v) is not None}
    by_key_new = {_key(v): v for v in news if _key(v) is not None}
    changed = sum(
        1 for k, v in by_key_new.items() if k in by_key_old and by_key_old[k] != v
    )
    keyed = set(by_key_old) & set(by_key_new)
    left = Counter(json.dumps(v, sort_keys=True) for v in olds if _key(v) not in keyed)
    right = Counter(json.dumps(v, sort_keys=True) for v in news if _key(v) not in keyed)
    return _counts(sum((right - left).values()), sum((left - right).values()), changed)


def _dict_change(old: dict[str, Any], new: dict[str, Any]) -> str:
    added = sum(1 for k in new if k not in old)
    removed = sum(1 for k in old if k not in new)
    changed = sum(1 for k in new if k in old and _text(old[k]) != _text(new[k]))
    return _counts(added, removed, changed)


def _scalar(value: Any) -> str:
    if value is None or value == "":
        return "(none)"
    words = str(value)
    return words if len(words) <= 40 else words[:39] + "…"


def _field_change(name: str, old: Any, new: Any) -> str | None:
    """One line for a field that differs, or None if it doesn't."""
    if _text(old) == _text(new):
        return None
    if isinstance(old, list) and isinstance(new, list):
        how = _list_change(old, new) or "changed"
    elif isinstance(old, dict) and isinstance(new, dict):
        how = _dict_change(old, new) or "changed"
    elif is_dataclass(old) and is_dataclass(new):
        parts = [
            label(f.name)
            for f in fields(old)
            if _text(getattr(old, f.name)) != _text(getattr(new, f.name))
        ]
        how = ", ".join(parts).lower().capitalize() or "changed"
    else:
        how = f"{_scalar(old)} → {_scalar(new)}"
    return f"{label(name)}: {how}"


def _changes(plan: UpdatePlan) -> list[str]:
    old, new = plan.record, plan.incoming
    lines = [
        line
        for f in fields(old)
        if f.name != "id"
        and (line := _field_change(f.name, getattr(old, f.name), getattr(new, f.name)))
    ]
    for noun, here, there in (
        ("Familiar", plan.familiars, plan.imported.familiars),
        ("Books", plan.books, plan.imported.books),
        ("Enchanted devices", plan.devices, plan.imported.devices),
    ):
        if _text(here) != _text(there):
            lines.append(f"{noun}: {_list_change(here, there) or 'changed'}")
    return lines


def preview(plan: UpdatePlan, file_name: str) -> str:
    """What the update will do, for the user to confirm (plain text)."""
    imported = plan.imported
    origin = f", exported from {imported.from_saga}" if imported.from_saga else ""
    lines = [
        f"Update {plan.record.name} from {file_name}{origin}?",
        "",
        "Changes:",
        *(f"  {line}" for line in plan.changes),
    ]
    added = len(imported.spells) + sum(len(e) for e in imported.custom.values())
    if added:
        lines.append(f"  Adds {added} spell(s) or House Rule(s) the saga lacks")
    if imported.dropped:
        lines += ["", "Links dropped:", *(f"  {text}" for text in imported.dropped)]
    placement = {
        transfer.CHARACTER: "Its covenant and laboratory stay as they are here.",
        transfer.LABORATORY: "Its covenant and owner stay as they are here.",
        transfer.COVENANT: "",
    }[transfer.kind_of(plan.record)]
    notes = [n for n in (placement, *plan.notes) if n]
    if notes:
        lines += ["", *notes]
    return "\n".join(lines)


# --------------------------------------------------------------- applying


def apply(saga: Saga, plan: UpdatePlan) -> None:
    """Make the update (the caller saves the saga). The record stays the
    same object, so whatever holds it sees the change."""
    record, imported = plan.record, plan.imported
    for f in fields(record):
        setattr(record, f.name, getattr(plan.incoming, f.name))
    saga.familiars = [f for f in saga.familiars if f not in plan.familiars]
    saga.books = [b for b in saga.books if b not in plan.books]
    saga.enchanted_devices = [
        d for d in saga.enchanted_devices if d not in plan.devices
    ]
    saga.familiars += imported.familiars
    saga.books += imported.books
    saga.enchanted_devices += imported.devices
    saga.codices += imported.codices
    saga.spells += imported.spells
    saga.custom_virtues_flaws += imported.custom.get("custom_virtues_flaws", [])
    saga.custom_lab_virtues_flaws += imported.custom.get("custom_lab_virtues_flaws", [])
    saga.custom_boons_hooks += imported.custom.get("custom_boons_hooks", [])
    bk.prune_codices(saga)
    catalog.use_saga(saga)
