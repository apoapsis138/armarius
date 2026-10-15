"""Content packs: a part of a saga's world (its Tribunals, covenants,
characters, places, neighbours and calendar) written to a file, to
populate another saga or start a new one.

A pack is an export (transfer.py) of the kind "pack": the same small
saga, so reading one runs the save's migrations and importing one uses
the same plan. Importing a pack differs from importing a record in one
way: a covenant, character, laboratory, neighbour or Tribunal the saga
already has one of the same name is matched rather than added beside it,
so a pack can be imported again, or over a saga that already holds part
of it, without doubling anything.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from . import places, storage, transfer
from .commands import Form, Refuse, notes
from .files import write_atomic
from .form_spec import DialogField
from .markup import escape, todo
from .models import Covenant, Neighbour, Saga, Tribunal
from .neighbours import kind_of

PACK = transfer.PACK


def _places_round(saga: Saga, ids: set[str]) -> set[str]:
    """`ids` with every place they sit in, however far out, and every
    place inside them, however deep."""
    found = set(ids)
    for place_id in ids:
        record = places.place(saga, place_id)
        if record is None:
            continue
        found |= {p.id for p in places.inside_of(saga, record)}
        found |= places.within(saga, record)
    return found


def contents(
    saga: Saga, tribunals: list[Tribunal], covenants: list[Covenant]
) -> tuple[list[Covenant], list[Neighbour]]:
    """What the chosen Tribunals and covenants take with them: every
    covenant of each Tribunal, then the places their covenants sit in
    (and the places round them), whoever sits in those places, and every
    neighbour that holds an attitude toward or a link to one of the
    covenants."""
    chosen_ids = {t.id for t in tribunals}
    members = [c for c in saga.covenants if c.tribunal_id in chosen_ids]
    taken = members + [c for c in covenants if c not in members]
    covenant_ids = {c.id for c in taken}
    place_ids = _places_round(saga, {c.place_id for c in taken if c.place_id})
    found: list[Neighbour] = []
    for neighbour in saga.neighbours:
        if (
            neighbour.id in place_ids
            or neighbour.place_id in place_ids
            or any(a.covenant_id in covenant_ids for a in neighbour.attitudes)
            or any(
                link.kind == "covenants" and link.target_id in covenant_ids
                for link in neighbour.links
            )
        ):
            found.append(neighbour)
    return taken, found


def pack_data(
    saga: Saga,
    name: str,
    tribunals: list[Tribunal],
    covenants: list[Covenant],
    neighbours: list[Neighbour],
    *,
    with_characters: bool = True,
    with_calendar: bool = True,
) -> dict[str, Any]:
    """The pack of the chosen records as JSON-ready data: the Tribunals,
    each with its covenants, and the covenants, each with the places and
    neighbours round it (contents()); then the neighbours chosen besides,
    with the places they sit in. `with_characters` adds the covenants'
    characters and laboratories and each Tribunal's officers;
    `with_calendar` the calendar entries of the covenants and the saga's
    own."""
    taken, round_them = contents(saga, tribunals, covenants)
    own_places = _places_round(saga, {n.place_id for n in neighbours if n.place_id})
    wanted = {n.id for n in [*round_them, *neighbours]} | own_places
    covenant_ids = {c.id for c in taken}
    characters, labs = [], []
    if with_characters:
        officers = {
            officer for t in tribunals for officer in (t.praeco_id, t.quaesitor_id)
        }
        characters = [
            c
            for c in saga.characters
            if c.covenant_id in covenant_ids or c.id in officers
        ]
        labs = [lab for lab in saga.laboratories if lab.covenant_id in covenant_ids]
    calendar = (
        [
            entry
            for entry in saga.calendar
            if entry.covenant_id is None or entry.covenant_id in covenant_ids
        ]
        if with_calendar
        else []
    )
    tribunal_ids = {t.id for t in tribunals} | {
        c.tribunal_id for c in taken if c.tribunal_id
    }
    return transfer.bundle_data(
        saga,
        PACK,
        name,
        covenants=taken,
        characters=characters,
        laboratories=labs,
        tribunals=[t for t in saga.tribunals if t.id in tribunal_ids],
        neighbours=[n for n in saga.neighbours if n.id in wanted],
        calendar=calendar,
    )


def write(path: Path, data: dict[str, Any]) -> Path:
    write_atomic(path, json.dumps(data, indent=2))
    return path


def summary(data: dict[str, Any]) -> str:
    """ "2 Tribunals, 5 covenants, 12 characters, 9 places and neighbours":
    what a pack holds."""
    held = data.get("saga") or {}
    counts = (
        (len(held.get("tribunals") or []), "Tribunal", "Tribunals"),
        (len(held.get("covenants") or []), "covenant", "covenants"),
        (len(held.get("characters") or []), "character", "characters"),
        (
            len(held.get("neighbours") or []),
            "place or neighbour",
            "places and neighbours",
        ),
        (len(held.get("calendar") or []), "calendar entry", "calendar entries"),
    )
    return ", ".join(f"{n} {one if n == 1 else many}" for n, one, many in counts if n)


# -- the export form --


def _label(neighbour: Neighbour) -> str:
    return f"{kind_of(neighbour).name}: {neighbour.name}"


def tick(kind: str, index: int) -> str:
    """The export form's key for the tick of the `index`th record of a
    kind ("tribunal", "covenant" or "neighbour") in the saga's lists."""
    return f"{kind}_{index}"


def chosen(
    saga: Saga, values: dict[str, Any]
) -> tuple[list[Tribunal], list[Covenant], list[Neighbour]]:
    """The records ticked on the export form."""
    tribunals = [
        t for i, t in enumerate(saga.tribunals) if values.get(tick("tribunal", i))
    ]
    ticked = {t.id for t in tribunals}
    covenants = [
        c
        for i, c in enumerate(saga.covenants)
        if values.get(tick("covenant", i)) and c.tribunal_id not in ticked
    ]
    neighbours = [
        n for i, n in enumerate(saga.neighbours) if values.get(tick("neighbour", i))
    ]
    return tribunals, covenants, neighbours


def file_name(name: str) -> str:
    return f"{storage.slugify(name) or PACK}{transfer.SUFFIX}"


def pack_fields(saga: Saga, folder: Path) -> list[DialogField]:
    """Export Pack: its name and file, then a tick for each Tribunal (with
    everything in it), each covenant not in a ticked Tribunal, and each
    place and neighbour."""
    fields = [
        DialogField("name", "Pack name", "text", f"{saga.name} pack", required=True),
        DialogField(
            "file",
            "File",
            "text",
            str(folder / file_name(f"{saga.name} pack")),
            hint="Import it into another saga with Import, A Content Pack, or "
            "start a new saga from it.",
        ),
        DialogField(
            "characters",
            "With their characters",
            "check",
            True,
            hint="The covenants' characters and laboratories, and each "
            "Tribunal's Praeco and Presiding Quaesitor.",
        ),
        DialogField(
            "calendar",
            "With the calendar",
            "check",
            True,
            hint="The covenants' calendar entries, and the saga's own.",
        ),
    ]
    for index, tribunal in enumerate(saga.tribunals):
        count = sum(1 for c in saga.covenants if c.tribunal_id == tribunal.id)
        fields.append(
            DialogField(
                tick("tribunal", index),
                f"Tribunal: {tribunal.name}",
                "check",
                False,
                hint=(
                    f"With its {count} covenant{'' if count == 1 else 's'}, "
                    "their places and neighbours."
                    if count
                    else "It has no covenants yet."
                ),
            )
        )

    def outside(tribunal_id: str | None) -> Callable[[dict[str, Any]], bool]:
        index = next(
            (i for i, t in enumerate(saga.tribunals) if t.id == tribunal_id), None
        )
        if index is None:
            return lambda _values: True
        return lambda values: not values.get(tick("tribunal", index))

    for index, covenant in enumerate(saga.covenants):
        fields.append(
            DialogField(
                tick("covenant", index),
                f"Covenant: {covenant.name}",
                "check",
                False,
                show_if=outside(covenant.tribunal_id),
            )
        )
    for index, neighbour in enumerate(saga.neighbours):
        fields.append(
            DialogField(tick("neighbour", index), _label(neighbour), "check", False)
        )
    return fields


def _path(values: dict[str, Any]) -> Path:
    """The form's file, with the export suffix if it has none."""
    name = (values.get("file") or "").strip().strip('"')
    path = Path(name).expanduser()
    if name and not path.name.lower().endswith(".json"):
        path = path.with_name(path.name + transfer.SUFFIX)
    return path


def problem(saga: Saga, values: dict[str, Any]) -> str | None:
    if not any(chosen(saga, values)):
        return "Tick what the pack holds: a Tribunal, a covenant or a neighbour."
    if not (values.get("file") or "").strip():
        return "Give the file to write."
    raw = Path((values.get("file") or "").strip().strip('"')).expanduser()
    if raw.is_dir() or _path(values).is_dir():
        return "That is a folder: add a file name."
    return None


def live(saga: Saga, values: dict[str, Any]) -> str:
    if not any(chosen(saga, values)):
        return ""
    data = _data(saga, values)
    path = _path(values)
    line = f"Holds {escape(summary(data))}."
    if path.exists():
        return f"{line} {todo(f'{escape(path.name)} exists: it will be replaced.')}"
    return line


def _data(saga: Saga, values: dict[str, Any]) -> dict[str, Any]:
    tribunals, covenants, neighbours = chosen(saga, values)
    return pack_data(
        saga,
        (values.get("name") or "").strip() or f"{saga.name} pack",
        tribunals,
        covenants,
        neighbours,
        with_characters=bool(values.get("characters")),
        with_calendar=bool(values.get("calendar")),
    )


def export_pack(
    saga: Saga,
    folder: Path,
    deliver: Callable[[str, dict[str, Any]], list[str]] | None = None,
) -> Form:
    """Export Pack: write the ticked records, and what goes with them, to
    a pack. `deliver` (a file name and the pack's data -> notes) sends it
    another way than writing it to the file named, as a browser copy
    does."""

    def apply(values: dict[str, Any]) -> Any:
        data = _data(saga, values)
        path = _path(values)
        if deliver is not None:
            return deliver(path.name, data)
        try:
            write(path, data)
        except OSError as problem_:
            return Refuse(
                "Export Pack",
                f"Couldn't write {escape(path.name)}: {escape(str(problem_))}",
            )
        return notes(
            f"Exported {escape(data['name'])} ({escape(summary(data))}) to "
            f"{escape(str(path))}."
        )

    return Form(
        "Export Pack",
        lambda: pack_fields(saga, folder),
        apply,
        validate=lambda values: problem(saga, values),
        live=lambda values: live(saga, values),
        save_label="Export",
        help_id="export-pack",
    )


# -- starting a saga from a pack --


def available(folder: Path) -> list[tuple[str, str]]:
    """The packs in `folder`, as (label, path) choices."""
    if not folder.is_dir():
        return []
    found = []
    for path in sorted(folder.glob(f"*{transfer.SUFFIX}")):
        try:
            data = transfer.read(path)
        except OSError, ValueError:
            continue
        if data.get("kind") == PACK:
            found.append(
                (f"{data.get('name') or path.stem} ({summary(data)})", str(path))
            )
    return found


def start_from(saga: Saga, path: Path) -> list[str]:
    """Add the pack at `path` to `saga` (a new one): what it added, as
    notes. The caller saves the saga."""
    data = transfer.read(path)
    if data["kind"] != PACK:
        raise ValueError("it is not a content pack")
    plan = transfer.plan_import(saga, data)
    transfer.apply(saga, plan)
    return notes(escape(f"Started from {plan.name}: {summary(data)}."))
