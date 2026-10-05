"""Where the app keeps the user's data (STORY-1127): the saga files, their
backups, exports and the app settings. The shared catalogs stay in the
repo's data/ folder (DATA_DIR).

By default the user data lives in "Ars Magica Manager" at the top of the
user's OneDrive, wherever OneDrive is on this computer (the %OneDrive%
environment variable), where it is backed up and easy to find; with no
OneDrive (a Mac, Linux), in the user's app data folder (Hedda, 2026-10-05:
not Documents, which Controlled folder access protects). Another folder can
be chosen, in order of precedence:

1. the ARS_MAGICA_MANAGER_DATA environment variable;
2. a `data_dir` in LOCATION_FILE, a small JSON file in the user's config
   folder (it can't live in the data folder it points to).

Before STORY-1127 the user data lived in the repo's data/ folder;
move_legacy_data() moves it across once, the first time the app starts.

If the folder can't be made or written to -- on Windows, Defender's
Controlled folder access blocks python.exe from writing in protected folders
such as Documents -- settle_data_dir() falls back to where the data already
is (STORY-1132).
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import platformdirs

from . import DATA_DIR

APP_NAME = "Ars Magica Manager"
ENV_VAR = "ARS_MAGICA_MANAGER_DATA"
#: {"data_dir": "D:/Games/Ars Magica"} chooses another folder.
LOCATION_FILE = (
    Path(platformdirs.user_config_dir(APP_NAME, appauthor=False)) / "location.json"
)

#: The names of the user data inside the data folder (the same layout the
#: repo's data/ folder had, so moving it is a plain move).
SAGAS = "sagas"
EXPORTS = "exports"
SETTINGS = "app_settings.json"


#: Where Windows says OneDrive is, in order: the user's own OneDrive is set
#: as OneDrive, and also OneDriveConsumer or OneDriveCommercial.
ONEDRIVE_VARS = ("OneDrive", "OneDriveConsumer", "OneDriveCommercial")


def onedrive_root() -> Path | None:
    """The top of the user's OneDrive on this computer, or None."""
    for var in ONEDRIVE_VARS:
        value = os.environ.get(var, "").strip()
        if value and Path(value).is_dir():
            return Path(value)
    return None


def default_data_dir() -> Path:
    """Ars Magica Manager at the top of the user's OneDrive, else in the
    user's app data folder."""
    root = onedrive_root()
    if root is not None:
        return root / APP_NAME
    return Path(platformdirs.user_data_dir(APP_NAME, appauthor=False))


def chosen_data_dir() -> Path | None:
    """The folder chosen instead of the default, if any."""
    if os.environ.get(ENV_VAR, "").strip():
        return Path(os.environ[ENV_VAR].strip()).expanduser()
    try:
        data = json.loads(LOCATION_FILE.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None
    chosen = data.get("data_dir") if isinstance(data, dict) else None
    return Path(chosen).expanduser() if isinstance(chosen, str) and chosen else None


#: The folder settle_data_dir() fell back to, when the chosen or default
#: one can't be used.
_fallback: Path | None = None


def data_dir() -> Path:
    """The folder holding the user's data."""
    return _fallback or chosen_data_dir() or default_data_dir()


def writable(folder: Path) -> bool:
    """Whether `folder` exists or can be made, and a file can be written in
    it (Controlled folder access lets a folder be listed but not written)."""
    try:
        folder.mkdir(parents=True, exist_ok=True)
        probe = folder / ".write-test"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
    except OSError:
        return False
    return True


def settle_data_dir(legacy: Path = DATA_DIR) -> str | None:
    """Make sure the data folder can be used, before storage and settings
    read it. If it can't, use the repo's data/ folder when the saves are
    still there (`legacy`), else the user's app data folder, and return why
    for the app to show; None when all is well."""
    global _fallback
    _fallback = None
    wanted = data_dir()
    if writable(wanted):
        return None
    if any((legacy / SAGAS).glob("*.json")):
        _fallback = legacy
    else:
        _fallback = Path(platformdirs.user_data_dir(APP_NAME, appauthor=False))
    return (
        f"Couldn't use {wanted} (on Windows, Controlled folder access in "
        f"Windows Security may be blocking it). Using {_fallback} instead; "
        "nothing was moved. The README says how to choose another folder."
    )


def move_legacy_data(old: Path = DATA_DIR, new: Path | None = None) -> list[str]:
    """Move the user data from the repo's data/ folder (`old`) to the data
    folder (`new`), once: each saga file, backup, export and the settings
    file not already at `new` is moved; one already there is left where it
    was, never overwritten. Returns a line per thing moved or left, for the
    app to say so."""
    new = data_dir() if new is None else new
    if old.resolve() == new.resolve():
        return []
    notes: list[str] = []
    sources: list[Path] = []
    for folder in (old / SAGAS, old / EXPORTS):
        if folder.is_dir():
            sources += sorted(p for p in folder.rglob("*") if p.is_file())
    if (old / SETTINGS).is_file():
        sources.append(old / SETTINGS)
    for source in sources:
        if source.name == ".gitkeep":
            continue
        relative = source.relative_to(old)
        target = new / relative
        if target.exists():
            notes.append(f"Left {relative.as_posix()}: {target} already exists")
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source, target)
        except OSError as problem:
            # Left where it was: the app still finds the rest, and the next
            # start tries again.
            notes.append(f"Couldn't move {relative.as_posix()}: {problem}")
            continue
        notes.append(f"Moved {relative.as_posix()}")
    return notes
