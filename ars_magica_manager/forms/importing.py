"""Import Data as the core's command steps (commands.py), so the terminal
and the desktop import the same way: what to import, the file (a
ChooseFile, which each front-end asks for in its own way), a preview to
confirm, then a question for each book or spell whose name is already
taken. Nothing is added until every question is answered; the last step
ends with the notes saying what was imported.

Books and spells come from a CSV file (books.read_books_csv,
spells.read_spells_csv); a character, covenant or laboratory from a file
exported from its sheet (transfer.py).

Update from a File reads an export too, over the record it was made from
(record_update.py): the file, then what would change, to confirm.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .. import books as bk
from .. import packs, record_update, storage, transfer
from .. import spells as spl
from ..commands import Choice, Choose, ChooseFile, Command, Confirm, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Book, Covenant, Saga, Spell

#: What Import Data offers: (key, label).
IMPORT_KINDS: tuple[tuple[str, str], ...] = (
    # Books first: the import most often wanted.
    ("books", "Books"),
    ("spells", "Spells"),
    # An export made from More on its sheet: one entry per kind.
    ("characters", "Characters"),
    ("covenants", "Covenants"),
    ("laboratories", "Laboratories"),
    ("saga", "A Whole Saga"),
    ("pack", "A Content Pack"),
)

#: The records imported from an export, by Import Data's key.
RECORD_IMPORTS: dict[str, str] = {
    "characters": transfer.CHARACTER,
    "covenants": transfer.COVENANT,
    "laboratories": transfer.LABORATORY,
    "saga": transfer.SAGA,
    "pack": transfer.PACK,
}

_DETAILS = {
    "books": "Books from a CSV file, added as unassigned books.",
    "spells": "Spells from a CSV file, added to the saga's own spells.",
    "saga": "Every record of a saga exported from its Saga Management, "
    "added beside this saga's own.",
    "pack": "Tribunals, covenants, characters, places, neighbours and calendar "
    "entries from a pack written by Export Pack; what this saga already has "
    "is kept.",
}

TITLE = "Import Data"


def import_data(saga: Saga, covenant: Covenant | None = None) -> Command:
    """More's Import: on the saga, choose what to import first; on a
    covenant, import books straight into its library."""
    if covenant is not None:
        return choose_file(saga, "books", covenant)

    def chosen(kind: str) -> Command:
        if kind == "spells":
            return spell_import_help(saga)
        return choose_file(saga, kind)

    return Choose(
        TITLE,
        lambda: [
            Choice(
                label,
                key,
                _DETAILS.get(key, f"A {label.lower()[:-1]} exported from its sheet."),
            )
            for key, label in IMPORT_KINDS
        ],
        chosen,
        help_id="import-data",
    )


def choose_file(saga: Saga, kind: str, covenant: Covenant | None = None) -> ChooseFile:
    """Choose the file importing `kind` reads (books into `covenant`'s
    library, or unassigned when it's None), then import it."""

    def read(path: Path) -> Command:
        return import_file(saga, kind, path, covenant)

    if kind in RECORD_IMPORTS:
        wanted = transfer.KIND_LABELS[RECORD_IMPORTS[kind]].lower()
        start = storage.EXPORTS_DIR if storage.EXPORTS_DIR.is_dir() else Path.cwd()
        return ChooseFile(f"Import a {wanted}", ".json", start, read)
    if kind == "spells":
        return ChooseFile(
            "Import spells (into the saga's own spells)", ".csv", Path.cwd(), read
        )
    return ChooseFile(
        f"Import books into {covenant.name}'s library"
        if covenant is not None
        else "Import books (as unassigned books)",
        ".csv",
        Path.cwd(),
        read,
    )


# -- the spell CSV help ------------------------------------------------------------


def spell_csv_help() -> str:
    """What a spell CSV looks like (markup)."""
    columns = "\n".join(
        f"  [b]{name}[/]: {escape(meaning)}" for name, meaning in spl.CSV_COLUMN_HELP
    )
    example = escape(spl.EXAMPLE_CSV.splitlines()[1])
    return (
        "Spells are imported from a CSV file with a header row into the "
        "saga's own spells. Columns, in any order and any case:\n\n"
        f"{columns}\n\n[b]An example row:[/]\n  [dim]{example}[/]"
    )


def save_example(folder: Path) -> list[str]:
    """Save an example spell CSV in `folder` (never over a file already
    there): what it did, as notes."""
    target = folder / "spells_example.csv"
    n = 2
    while target.exists():
        target = folder / f"spells_example_{n}.csv"
        n += 1
    try:
        target.write_text(spl.EXAMPLE_CSV, encoding="utf-8")
    except OSError as error:
        return notes(f"Couldn't save the example: {escape(str(error))}")
    return notes(
        f"Saved {escape(target.name)} in {escape(str(folder))}. "
        "Edit it, then import it."
    )


def spell_import_help(saga: Saga, folder: Path | None = None) -> Form:
    """Import Spells: what a spell CSV looks like, then on to choosing the
    file, or save an example to start from in `folder` (the working
    folder by default) instead."""
    folder = folder or Path.cwd()

    def apply(values: dict[str, Any]) -> Command | list[str]:
        if values.get("example"):
            return save_example(folder)
        return choose_file(saga, "spells")

    return Form(
        "Import Spells",
        lambda: [
            DialogField(
                "example",
                "Save an example CSV instead",
                "check",
                False,
                hint=f"Saved in {folder}, to edit and then import.",
            ),
        ],
        apply,
        # The CSV's columns, under the tick.
        live=lambda _values: spell_csv_help(),
        save_label="Choose CSV File",
        help_id="import-spells",
    )


# -- importing a file --------------------------------------------------------------


def import_file(
    saga: Saga, kind: str, path: Path, covenant: Covenant | None = None
) -> Command:
    """Import the chosen file: `kind` is Import Data's key (books go into
    `covenant`'s library, or unassigned when it's None)."""
    if kind in RECORD_IMPORTS:
        return _import_record(saga, RECORD_IMPORTS[kind], path)
    if kind == "spells":
        return _import_spells(saga, path)
    return _import_books(saga, path, covenant)


def _import_record(saga: Saga, kind: str, path: Path) -> Command:
    """Preview what importing an exported character, covenant, laboratory
    or saga adds and which of its links this saga can keep, then add it."""
    wanted = transfer.KIND_LABELS[kind].lower()
    try:
        data = transfer.read(path)
        if data["kind"] != kind:
            found = transfer.KIND_LABELS[data["kind"]]
            labels = dict(IMPORT_KINDS)
            entry = next(k for k, v in RECORD_IMPORTS.items() if v == data["kind"])
            raise ValueError(
                f"it holds a {found.lower()}, not a {wanted}: choose "
                f"{labels[entry]} in the Import list"
            )
        if kind == transfer.PACK:
            return _import_pack(saga, data)
        plan = transfer.plan_import(saga, data)
    except (OSError, ValueError, KeyError, TypeError) as problem:
        return Refuse(
            TITLE, f"Couldn't import {escape(path.name)}: {escape(str(problem))}"
        )
    return _confirm_import(saga, plan)


def _confirm_import(
    saga: Saga, plan: transfer.ImportPlan, data: dict[str, Any] | None = None
) -> Confirm:
    """`data`, a pack's, for what importing it does besides its records
    (packs.after_import)."""

    def apply() -> list[str]:
        transfer.apply(saga, plan)
        found = notes(
            escape(f"Imported {plan.name} ({transfer.KIND_LABELS[plan.kind].lower()}).")
        )
        return found + (packs.after_import(saga, data) if data is not None else [])

    return Confirm(
        escape(transfer.preview(plan)), apply, yes_label="Import", title=TITLE
    )


def _import_pack(saga: Saga, data: dict[str, Any]) -> Command:
    """Import a Content Pack: which of its parts to bring in (its
    Tribunals and covenants always come), then the preview to confirm.
    A pack with nothing to leave out goes straight to the preview."""
    fields = packs.import_fields(data, saga)
    if not fields:
        return _confirm_import(saga, transfer.plan_import(saga, data), data)

    def apply(values: dict[str, Any]) -> Command:
        try:
            plan = transfer.plan_import(saga, packs.narrow(data, values))
        except (ValueError, KeyError, TypeError) as problem:
            return Refuse(TITLE, f"Couldn't import the pack: {escape(str(problem))}")
        return _confirm_import(saga, plan, data)

    def live(values: dict[str, Any]) -> str:
        return f"Brings {escape(packs.summary(packs.narrow(data, values)))}."

    return Form(
        f"Import {escape(str(data.get('name') or 'a Content Pack'))}",
        lambda: fields,
        apply,
        live=live,
        save_label="Preview",
        help_id="import-pack",
    )


def update_record(saga: Saga, record: transfer.Record) -> Command:
    """Update a character, covenant or laboratory from an export of it:
    choose the file, see what would change, then confirm."""
    kind = transfer.KIND_LABELS[transfer.kind_of(record)].lower()
    title = f"Update {escape(record.name)} from a File"
    start = storage.EXPORTS_DIR if storage.EXPORTS_DIR.is_dir() else Path.cwd()

    def read(path: Path) -> Command:
        try:
            plan = record_update.plan_update(saga, record, transfer.read(path))
        except (OSError, ValueError, KeyError, TypeError, IndexError) as problem:
            return Refuse(
                title, f"Couldn't read {escape(path.name)}: {escape(str(problem))}"
            )
        if not plan.changes:
            return Refuse(
                title,
                f"Nothing in {escape(path.name)} differs from {escape(record.name)}.",
            )

        def apply() -> list[str]:
            record_update.apply(saga, plan)
            return notes(escape(f"Updated {record.name} from {path.name}."))

        return Confirm(
            escape(record_update.preview(plan, path.name)),
            apply,
            yes_label="Update",
            title=title,
        )

    return ChooseFile(
        f"Update {record.name} from a {kind}'s export", ".json", start, read
    )


def _import_books(saga: Saga, path: Path, covenant: Covenant | None) -> Command:
    """Preview the books a CSV file holds, then add them: all owned by
    `covenant`, or all unassigned when it's None (the file's own owner
    column isn't used)."""
    destination = (
        f"into {covenant.name}'s library"
        if covenant is not None
        else "as unassigned books"
    )
    try:
        result = bk.read_books_csv(path)
    except (OSError, ValueError) as problem:
        return Refuse(
            TITLE, f"Couldn't read {escape(path.name)}: {escape(str(problem))}"
        )
    if not result.books:
        reason = f" {escape(result.skipped[0])}" if result.skipped else ""
        return Refuse(TITLE, f"No books to import from {escape(path.name)}.{reason}")
    names = {b.name for b in saga.books}

    def finish(accepted: list[Book], skipped: int) -> list[str]:
        bk.add_imported_books(saga, accepted, covenant, result.encyclopedias)
        count = len(accepted)
        message = f"Imported {count} book{'s' if count != 1 else ''}"
        message += f" {destination}" if count else ""
        if skipped:
            message += f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
        return notes(escape(message + "."))

    return Confirm(
        bk.import_preview(result, path.name, destination, names),
        lambda: _ask_about_duplicates(result.books, names, "book", finish),
        yes_label="Import",
        title=TITLE,
    )


def _import_spells(saga: Saga, path: Path) -> Command:
    """Preview the spells a CSV file holds, then add them to the saga's
    own."""
    try:
        result = spl.read_spells_csv(path)
    except (OSError, ValueError) as problem:
        return Refuse(
            TITLE, f"Couldn't read {escape(path.name)}: {escape(str(problem))}"
        )
    if not result.spells:
        reason = f" {escape(result.skipped[0])}" if result.skipped else ""
        return Refuse(TITLE, f"No spells to import from {escape(path.name)}.{reason}")
    existing = {sp.name for sp in spl.all_spells(saga)}

    def finish(accepted: list[Spell], skipped: int) -> list[str]:
        spl.add_imported_spells(saga, accepted)
        count = len(accepted)
        message = f"Imported {count} spell{'s' if count != 1 else ''}"
        if skipped:
            message += f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
        return notes(escape(message + "."))

    return Confirm(
        spl.spell_import_preview(result, path.name, existing),
        lambda: _ask_about_duplicates(
            result.spells, existing, "spell", finish, spl.name_key
        ),
        yes_label="Import",
        title=TITLE,
    )


#: A duplicate's answers: (value, label), Skip first so it is the default.
DUPLICATE_ANSWERS: tuple[tuple[str, str], ...] = (
    ("skip", "Skip"),
    ("skip_all", "Skip All"),
    ("duplicate", "Duplicate"),
    ("duplicate_all", "Duplicate All"),
)


def _ask_about_duplicates[T: Book | Spell](
    items: list[T],
    names: set[str],
    noun: str,
    finish: Callable[[list[T], int], list[str]],
    key: Callable[[str], str] = str,
) -> Command | list[str]:
    """Go through imported items, asking about each whose name is already
    taken -- by `names` or earlier in `items`, comparing names by `key` --
    (Skip / Skip All / Duplicate / Duplicate All), then `finish(accepted,
    skipped)`. Cancelling a question imports nothing."""
    accepted: list[T] = []
    taken = {key(name) for name in names}
    state: dict[str, Any] = {"all": None, "skipped": 0}

    def take(item: T, answer: str) -> None:
        if answer == "skip":
            state["skipped"] += 1
        else:
            accepted.append(item)
            taken.add(key(item.name))

    def step(index: int) -> Command | list[str]:
        while index < len(items):
            item = items[index]
            if key(item.name) in taken and state["all"] is None:
                return _duplicate_question(item, index)
            take(item, state["all"] if key(item.name) in taken else "duplicate")
            index += 1
        return finish(accepted, state["skipped"])

    def _duplicate_question(item: T, index: int) -> Choose:
        remaining = len(bk.duplicate_names(items[index + 1 :], taken, key))
        more = f" {remaining} more duplicate(s) after this one." if remaining else ""

        def answer(chosen: str) -> Command | list[str]:
            if chosen.endswith("_all"):
                chosen = chosen.removesuffix("_all")
                state["all"] = chosen
            take(item, chosen)
            return step(index + 1)

        return Choose(
            f"A {noun} named {escape(item.name)} is already in the saga. "
            f"Add this one as well?{more}",
            lambda: [Choice(label, value) for value, label in DUPLICATE_ANSWERS],
            answer,
        )

    return step(0)
