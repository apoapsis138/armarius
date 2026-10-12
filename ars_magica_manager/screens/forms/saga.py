"""The saga picker's forms: where the saves are kept."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ... import paths
from ...markup import escape
from ..fields import DialogField, FieldsDialog
from ..pickers import FolderPickerScreen

#: Why a folder may refuse saves, shown under the folder field.
FOLDER_WARNING = (
    "Some folders may not allow saving: on Windows, Controlled folder access "
    "protects Documents and the Desktop, and a read-only or synced folder can "
    "refuse too. The app checks it can save there before using it."
)


def _existing(folder: Path) -> Path:
    """The nearest folder at or above `folder` that exists, for the folder
    browser to start in."""
    while not folder.is_dir() and folder.parent != folder:
        folder = folder.parent
    return folder


def _save_folder_problem(values: dict[str, Any], current: Path) -> str | None:
    folder = values["folder"]
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


def _save_folder_dialog(current: Path) -> FieldsDialog[tuple[Path, bool]]:
    """Change save folder: the folder the sagas, backups, exports and
    settings are kept in, and whether to move them there. Dismisses with
    (the new folder, move them)."""
    return FieldsDialog(
        "Change save folder",
        [
            DialogField(
                "now",
                "Now",
                "info",
                f"{current} ({paths.SOURCE_TEXT[paths.source()]})",
            ),
            DialogField(
                "folder",
                "New folder",
                "picker",
                None,
                required=True,
                placeholder="(choose a folder...)",
                picker=lambda chosen: FolderPickerScreen(
                    "Choose the save folder", chosen or _existing(current)
                ),
                display=str,
                hint=FOLDER_WARNING,
            ),
            DialogField(
                "move",
                "Move the saves there",
                "check",
                True,
                hint="The sagas, their backups, exports and settings; a file "
                "already in the new folder is never overwritten.",
            ),
        ],
        validate=lambda values: _save_folder_problem(values, current),
        save_label="Use this folder",
        build=lambda values: (values["folder"], values["move"]),
    )
