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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import DATA_DIR, places, sourcebooks, storage, threats, transfer
from .commands import Form, Refuse, notes
from .files import write_atomic
from .form_spec import DialogField
from .markup import escape, todo
from .models import Character, Covenant, Creature, Neighbour, Saga, Tribunal
from .neighbours import kind_of
from .rules import sites

PACK = transfer.PACK


def _places_round(saga: Saga, ids: set[str]) -> set[str]:
    """`ids` with every place they sit in, however far out, and every
    place inside them, however deep."""
    found = set(ids)
    for place_id in ids:
        record = sites.place(saga, place_id)
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
    characters_besides: list[Character] | None = None,
    creatures_besides: list[Creature] | None = None,
) -> dict[str, Any]:
    """The pack of the chosen records as JSON-ready data: the Tribunals,
    each with its covenants, and the covenants, each with the places and
    neighbours round it (contents()); then the neighbours chosen besides,
    with the places they sit in. `with_characters` adds the covenants'
    characters and laboratories and each Tribunal's officers;
    `with_calendar` the calendar entries of the covenants and the saga's
    own; `characters_besides` adds characters who belong to no covenant
    taken (a wandering magus), and `creatures_besides` creatures found
    nowhere it takes (a book's bestiary)."""
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
        characters += [c for c in characters_besides or [] if c not in characters]
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
    held = [n for n in saga.neighbours if n.id in wanted]
    return transfer.bundle_data(
        saga,
        PACK,
        name,
        covenants=taken,
        characters=characters,
        laboratories=labs,
        tribunals=[t for t in saga.tribunals if t.id in tribunal_ids],
        neighbours=held,
        calendar=calendar,
        creatures=[
            *(found := creatures_round(saga, taken, held)),
            *(c for c in creatures_besides or [] if c not in found),
        ],
    )


def creatures_round(
    saga: Saga, covenants: list[Covenant], neighbours: list[Neighbour]
) -> list[Creature]:
    """The creatures a pack takes: those found at its places, those that
    link to its covenants, places or neighbours, and those they link to."""
    ids = {c.id for c in covenants} | {n.id for n in neighbours}
    linked = {
        link.target_id
        for record in neighbours
        for link in record.links
        if link.kind == "creatures"
    }
    return [
        c
        for c in saga.creatures
        if c.place_id in ids
        or c.id in linked
        or any(link.target_id in ids for link in c.links)
    ]


def write(path: Path, data: dict[str, Any]) -> Path:
    write_atomic(path, json.dumps(data, indent=2))
    return path


def summary(data: dict[str, Any], tribunals: bool = True) -> str:
    """ "2 Tribunals, 5 covenants, 12 characters, 9 places and neighbours":
    what a pack holds; without the Tribunals' count when not
    `tribunals`."""
    held = data.get("saga") or {}
    counts = (
        (len(held.get("tribunals") or []) if tribunals else 0, "Tribunal", "Tribunals"),
        (len(held.get("covenants") or []), "covenant", "covenants"),
        (len(held.get("characters") or []), "character", "characters"),
        (
            len(held.get("neighbours") or []),
            "place or neighbour",
            "places and neighbours",
        ),
        (len(held.get("creatures") or []), "creature", "creatures"),
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


# -- choosing what a pack imports --


@dataclass(frozen=True)
class Group:
    """A part of a pack the importer can leave out: its tick's key and
    label, what it holds in words, and how many records of it a pack's
    data holds (for the tick's hint)."""

    key: str
    label: str
    hint: str
    count: Callable[[dict[str, Any]], int]


def _held(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return list((data.get("saga") or {}).get(key) or [])


def _is_place(neighbour: dict[str, Any]) -> bool:
    return neighbour.get("kind") == sites.PLACE


#: The pack key holding the sketch of each magus a book describes but
#: prints no stat block for, whose stats the pack generated
#: (book_packs.generated): {character id: the character as a sketch}.
GENERATED = "generated"
#: What a generated magus's sheet and the import form say of the stats.
INFERRED = (
    "These stats are not an official write-up: they are inferred from the "
    "book's description by the creation rules."
)


#: What a pack holds beyond its Tribunals and covenants, each a tick on
#: the import form. The Tribunals and covenants always come: they are
#: what the rest hangs on. A dict of predicates, not a class each.
GROUPS: tuple[Group, ...] = (
    Group(
        "people",
        "Their people",
        "The covenants' characters, laboratories and familiars, and each "
        "Tribunal's Praeco and Presiding Quaesitor.",
        lambda data: len(_held(data, "characters")),
    ),
    Group(
        GENERATED,
        "Generated stats for magi",
        f"The magi the book prints no stat block for come with full stats. "
        f"{INFERRED} Untick to bring them in as the book's sketches.",
        lambda data: len(data.get(GENERATED) or {}),
    ),
    Group(
        "places",
        "Places and regiones",
        "The places the covenants sit in, the places round and inside those, "
        "and their regio levels.",
        lambda data: sum(1 for n in _held(data, "neighbours") if _is_place(n)),
    ),
    Group(
        "world",
        "The mundane world",
        "Lords, towns, the Church, universities, factions and threats.",
        lambda data: sum(1 for n in _held(data, "neighbours") if not _is_place(n)),
    ),
    Group(
        "bestiary",
        "The Bestiary",
        "The creatures found in the pack's places and stories, with their stat blocks.",
        lambda data: len(_held(data, "creatures")),
    ),
    Group(
        "code",
        "Code, cases and fines",
        "Each Tribunal's Peripheral Code, docket and fines.",
        lambda data: sum(
            len(t.get("rulings") or []) + len(t.get("cases") or [])
            for t in _held(data, "tribunals")
        ),
    ),
    Group(
        "history",
        "The history",
        "Each Tribunal's and covenant's Diary, and the calendar entries.",
        lambda data: (
            sum(len(t.get("diary") or []) for t in _held(data, "tribunals"))
            + sum(len(c.get("diary") or []) for c in _held(data, "covenants"))
            + len(_held(data, "calendar"))
        ),
    ),
)


def story_key(neighbour_id: str, prefix: str = "") -> str:
    """The import form's key for beginning one of the pack's stories."""
    return f"{prefix}story_{neighbour_id}"


def stories(data: dict[str, Any], saga: Saga | None = None) -> list[dict[str, Any]]:
    """The pack's stories (its threats) that the saga doesn't already
    have one of the same name."""
    had = {n.name.casefold() for n in saga.neighbours} if saga is not None else set()
    return [
        n
        for n in _held(data, "neighbours")
        if n.get("kind") == threats.THREAT
        and str(n.get("name") or "").casefold() not in had
    ]


def story_fields(
    data: dict[str, Any],
    saga: Saga | None = None,
    *,
    prefix: str = "",
    show_if: Callable[[dict[str, Any]], bool] | None = None,
) -> list[DialogField]:
    """A tick for each of the pack's stories to begin, all ticked: one
    left unticked comes in dormant, to begin later."""
    return [
        DialogField(
            story_key(n["id"], prefix),
            f"Begin: {escape(str(n.get('name') or ''))}",
            "check",
            True,
            hint="Unticked, it comes in dormant: Begin This Story, in its "
            "More, starts it later.",
            show_if=show_if,
        )
        for n in stories(data, saga)
    ]


def _with_world(values: dict[str, Any]) -> bool:
    return bool(values.get("world", True))


def import_fields(data: dict[str, Any], saga: Saga | None = None) -> list[DialogField]:
    """Import a Content Pack: a tick for each group the pack holds any
    of, all ticked, then one for each of its stories the saga doesn't
    have, to begin. A group the pack has nothing of isn't asked about."""
    fields = []
    for group in GROUPS:
        number = group.count(data)
        if not number:
            continue
        fields.append(
            DialogField(
                group.key,
                f"{group.label} ({number})",
                "check",
                True,
                hint=group.hint,
                show_if=_with_people if group.key == GENERATED else None,
            )
        )
    if any(f.key == "world" for f in fields):
        fields += story_fields(data, saga, show_if=_with_world)
    return fields


def _with_people(values: dict[str, Any]) -> bool:
    return bool(values.get("people", True))


def _dormant(data: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    """`data` with each story left unticked in `values` marked dormant."""
    asleep = {
        n["id"]
        for n in _held(data, "neighbours")
        if n.get("kind") == threats.THREAT
        and story_key(n["id"]) in values
        and not values[story_key(n["id"])]
    }
    if not asleep:
        return data
    neighbours = [
        {**n, "details": {**(n.get("details") or {}), threats.DORMANT: True}}
        if n["id"] in asleep
        else n
        for n in _held(data, "neighbours")
    ]
    return {**data, "saga": {**data["saga"], "neighbours": neighbours}}


def narrow(data: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    """`data` (a pack, from transfer.read) without the groups unticked in
    `values`, as a new dict. A record left out is named in the pack's
    links instead, so the import plan matches what the pack points at
    to the saga's own of that name, or says the link is dropped. With
    the generated stats unticked, each magus the pack stats by inference
    comes in as the book's sketch instead. A story left unticked comes
    in dormant."""
    data = _dormant(data, values)
    out = ("people", GENERATED, "places", "world", "bestiary", "code", "history")
    left = {key for key in out if key in values and not values.get(key)}
    if not left:
        return data
    held = {k: list(v) if isinstance(v, list) else v for k, v in data["saga"].items()}
    links = {k: dict(v) for k, v in (data.get("links") or {}).items()}

    def name_links(kind: str, records: list[dict[str, Any]]) -> None:
        links.setdefault(kind, {})
        for record in records:
            links[kind][record["id"]] = record.get("name", "")

    if "people" in left:
        name_links(transfer.CHARACTER, held.get("characters") or [])
        name_links(transfer.LABORATORY, held.get("laboratories") or [])
        held["characters"], held["laboratories"], held["familiars"] = [], [], []
    elif GENERATED in left:
        sketches = data.get(GENERATED) or {}
        held["characters"] = [
            sketches.get(c["id"], c) for c in held.get("characters") or []
        ]
    neighbours = held.get("neighbours") or []
    gone = [
        n
        for n in neighbours
        if ("places" in left and _is_place(n)) or ("world" in left and not _is_place(n))
    ]
    if gone:
        name_links(transfer.NEIGHBOUR, gone)
        held["neighbours"] = [n for n in neighbours if n not in gone]
    if "bestiary" in left:
        name_links(transfer.CREATURE, held.get("creatures") or [])
        held["creatures"] = []
    if "code" in left or "history" in left:
        blank = ("rulings", "cases", "treasury") if "code" in left else ()
        blank += ("diary",) if "history" in left else ()
        held["tribunals"] = [
            {**t, **{key: [] for key in blank}} for t in held.get("tribunals") or []
        ]
    if "history" in left:
        # A pack with no Tribunal keeps its history in a covenant's Diary.
        held["calendar"] = []
        held["covenants"] = [{**c, "diary": []} for c in held.get("covenants") or []]
    return {**data, "links": links, "saga": held}


# -- starting a saga from a pack --

#: The packs shipped with the app, built from the Tribunal books
#: (book_packs).
SHIPPED_DIR = DATA_DIR / "packs"


#: A pack offered by Start from a pack: (label, path, its data). The data
#: is read once, when the packs are listed, and reused for their stories.
PackChoice = tuple[str, str, dict[str, Any]]


def available(*folders: Path) -> list[PackChoice]:
    """The packs in `folders`, as (label, path, data) choices: the shipped
    packs first when SHIPPED_DIR is given first."""
    found = []
    for folder in folders:
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob(f"*{transfer.SUFFIX}")):
            try:
                data = transfer.read(path)
            except OSError, ValueError:
                continue
            if data.get("kind") == PACK:
                found.append((choice_label(data, path.stem), str(path), data))
    return found


def _tribunal_title(name: str) -> str:
    """ "Rhine Tribunal" for "The Rhine Tribunal" or "Rhine"."""
    name = name.removeprefix("The ").strip()
    return name if name.endswith("Tribunal") else f"{name} Tribunal"


def choice_label(data: dict[str, Any], fallback: str) -> str:
    """How Start from a pack lists a pack: its Tribunals and what else it
    holds ("Rhine Tribunal: 10 covenants, 74 characters"), or, holding
    no Tribunal, its name (else `fallback`) and what it holds. Kept short
    so the choice fits the form."""
    names = [
        _tribunal_title(t["name"])
        for t in (data.get("saga") or {}).get("tribunals") or []
        if isinstance(t, dict) and t.get("name")
    ]
    if names:
        rest = summary(data, tribunals=False)
        return f"{', '.join(names)}: {rest}" if rest else ", ".join(names)
    return f"{data.get('name') or fallback}: {summary(data)}"


#: The pack key naming the help topic that lists what a book pack
#: inferred from its book or chose where the book is silent.
ASSUMPTIONS = "assumptions"


def after_import(saga: Saga, data: dict[str, Any]) -> list[str]:
    """What importing a pack does besides its records: a pack built from
    a sourcebook (its "book") puts that book in play, and one that names
    its assumptions page says where to read them. The notes to show."""
    book = data.get("book")
    if not isinstance(book, str):
        return []
    title = sourcebooks.title_of(book)
    found = []
    if sourcebooks.put_in_play(saga, book):
        found += notes(escape(f"{title} is now in play."))
    if data.get(ASSUMPTIONS):
        found += notes(escape(assumptions_note(title)))
    return found


def assumptions_note(title: str) -> str:
    """What importing a book's pack says of the values it had to supply."""
    return (
        "Some values in this pack are inferred from the book or chosen where "
        f"it is silent: Help's page Assumptions made for {title} lists them."
    )


def start_prefix(index: int) -> str:
    """The key prefix of Start from a pack's story ticks for the
    `index`th pack offered."""
    return f"pack{index}_"


def start_story_fields(found: list[PackChoice]) -> list[DialogField]:
    """Start from a pack's ticks for the stories to begin, each pack's
    shown while it is the one chosen."""
    fields = []
    for index, (_label, path, data) in enumerate(found):
        fields += story_fields(
            data,
            prefix=start_prefix(index),
            show_if=lambda values, path=path: values.get("pack") == path,
        )
    return fields


def start_choices(values: dict[str, Any]) -> dict[str, Any]:
    """The story ticks of the chosen pack in Start from a pack's
    `values`, keyed as the import form keys them (only the chosen
    pack's are shown, so only theirs are in `values`)."""
    found = {}
    for key, value in values.items():
        head, _, rest = key.partition("_")
        if head.startswith("pack") and head[4:].isdigit() and rest.startswith("story_"):
            found[rest] = value
    return found


def start_from(
    saga: Saga, path: Path, values: dict[str, Any] | None = None
) -> list[str]:
    """Add the pack at `path` to `saga` (a new one): what it added, as
    notes. `values` holds the stories to begin (start_choices); the
    rest come in dormant. The caller saves the saga."""
    data = transfer.read(path)
    if data["kind"] != PACK:
        raise ValueError("it is not a content pack")
    data = _dormant(data, values or {})
    plan = transfer.plan_import(saga, data)
    transfer.apply(saga, plan)
    return notes(escape(f"Started from {plan.name}: {summary(data)}.")) + after_import(
        saga, data
    )
