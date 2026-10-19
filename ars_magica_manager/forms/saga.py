"""Managing the sagas themselves, as the core's command steps
(commands.py), for the list of sagas each front-end opens on: a new saga,
deleting one, and the folder the saves are kept in.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import creation, packs, paths, storage
from ..commands import Confirm, Form, Picked, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Saga
from . import creation as creation_forms


def create_saga(values: dict[str, Any]) -> Saga:
    """The saga the Create a New Saga form describes, started from its
    pack if it names one, and saved."""
    saga = creation.new_saga(
        values["name"],
        values["storyguide"],
        values["description"],
        values["year"],
        values["season"],
    )
    if values.get("pack"):
        packs.start_from(saga, Path(values["pack"]), packs.start_choices(values))
    storage.save_saga(saga)
    return saga


def new_saga_form() -> Form:
    """Create a New Saga: its name, storyguide, starting date and
    premise, and the pack it starts from, if any; saved at once, ending
    with the new saga's id."""

    def apply(values: dict[str, Any]) -> Picked:
        return Picked(create_saga(values).id)

    return Form(
        "Create a New Saga",
        lambda: creation_forms.saga_fields(None),
        apply,
        save_label="Create",
    )


def delete_saga(saga_id: str, name: str) -> Confirm:
    """Delete a saga's file, after a question that says it is for good."""
    return Confirm(
        f"Delete the saga {escape(name)}?\n\n"
        "Everything in it (covenants, characters, laboratories, library) is "
        "deleted for good. This cannot be undone.",
        lambda: storage.delete_saga(saga_id),
        yes_label="Delete",
    )


def save_folder_problem(folder: Path | None, current: Path) -> str | None:
    """Why `folder` can't be the save folder, or None."""
    if folder is None:
        return "Choose a folder."
    if folder.resolve() == current.resolve():
        return "That is already the save folder."
    if not paths.writable(folder):
        return (
            f"The app can't save in {escape(str(folder))}: a system setting "
            "or the folder's permissions stop it. Choose another folder."
        )
    return None


def use_save_folder(old: Path, folder: Path, move: bool) -> list[str]:
    """Keep the saves in `folder` from now on, moving them there from
    `old` if `move`: what it did, as notes."""
    moved_notes = paths.move_user_data(old, folder) if move else []
    paths.remember_data_dir(folder)
    storage.use_data_dir(folder)
    moved = sum(1 for note in moved_notes if note.startswith("Moved"))
    left = [note for note in moved_notes if not note.startswith("Moved")]
    return notes(
        f"The saves are kept in {escape(str(folder))}.",
        f"Moved {moved} file(s)." if move else "Nothing moved.",
        *(escape(note) for note in left),
    )


def save_folder_form(current: Path, folder: Path) -> Form:
    """Change save folder, once the new `folder` is chosen (each front-end
    chooses folders its own way): whether to move the saves there."""
    return Form(
        "Change save folder",
        lambda: [
            DialogField(
                "now",
                "Now",
                "info",
                f"{current} ({paths.source_text()})",
            ),
            DialogField("new", "New folder", "info", str(folder)),
            DialogField(
                "move",
                "Move the saves there",
                "check",
                True,
                hint="The sagas, their backups, exports and settings; a file "
                "already in the new folder is never overwritten.",
            ),
        ],
        lambda values: use_save_folder(current, folder, bool(values["move"])),
        validate=lambda _values: save_folder_problem(folder, current),
        save_label="Use this folder",
    )


def save_folder_refused() -> str | None:
    """Why the save folder can't be changed in the app (it is set by the
    environment), or None."""
    if paths.source() == "env":
        return (
            f"The save folder is set by {paths.env_var()}: unset it to choose one here."
        )
    return None
