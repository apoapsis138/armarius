"""Where the app keeps the user's data: the saga files, their
backups, exports and the app settings. The shared catalogs stay in the
repo's data/ folder (DATA_DIR).

By default the user data lives in "Armarius" at the top of the
user's OneDrive, wherever OneDrive is on this computer (the %OneDrive%
environment variable), where it is backed up and easy to find; with no
OneDrive (a Mac, Linux), in the user's app data folder (not
Documents, which Controlled folder access protects). Another folder can
be chosen, in order of precedence:

1. the ARMARIUS_DATA environment variable (or the older
   ARS_MAGICA_MANAGER_DATA);
2. a `data_dir` in LOCATION_FILE, a small JSON file in the user's config
   folder (it can't live in the data folder it points to), or in
   OLD_LOCATION_FILE when there is none.

The saga picker's Change save folder writes LOCATION_FILE
(remember_data_dir()) and can move the user data across (move_user_data()).

Older versions kept the user data in the repo's data/ folder;
move_legacy_data() moves it across once, the first time the app starts.
The app was called Ars Magica Manager before it was Armarius, and its
default folder had that name; move_old_default_folder() renames it once.

If the folder can't be made or written to -- on Windows, Defender's
Controlled folder access blocks python.exe from writing in protected folders
such as Documents -- settle_data_dir() falls back to where the data already
is.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import platformdirs

from . import DATA_DIR

APP_NAME = "Armarius"
#: The app's name before Armarius, still found in older users' folders,
#: settings and environment.
OLD_APP_NAME = "Ars Magica Manager"
ENV_VAR = "ARMARIUS_DATA"
OLD_ENV_VAR = "ARS_MAGICA_MANAGER_DATA"
#: {"data_dir": "D:/Games/Ars Magica"} chooses another folder.
LOCATION_FILE = (
    Path(platformdirs.user_config_dir(APP_NAME, appauthor=False)) / "location.json"
)
#: Where the folder was chosen under the old name, read when LOCATION_FILE
#: isn't there (choosing a folder writes LOCATION_FILE).
OLD_LOCATION_FILE = (
    Path(platformdirs.user_config_dir(OLD_APP_NAME, appauthor=False)) / "location.json"
)

#: The names of the user data inside the data folder (the same layout the
#: repo's data/ folder had, so moving it is a plain move).
SAGAS = "sagas"
EXPORTS = "exports"
PORTRAITS = "portraits"
SETTINGS = "app_settings.json"
#: The hosted app's SSH host key (tui/hosting.py).
HOST_KEY = "ssh_host_key"


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


def _default_named(name: str) -> Path:
    """The folder `name` at the top of the user's OneDrive, else in the
    user's app data folder."""
    root = onedrive_root()
    if root is not None:
        return root / name
    return Path(platformdirs.user_data_dir(name, appauthor=False))


def default_data_dir() -> Path:
    """Armarius at the top of the user's OneDrive, else in the user's app
    data folder."""
    return _default_named(APP_NAME)


def old_default_data_dir() -> Path:
    """Where the default folder was under the app's old name."""
    return _default_named(OLD_APP_NAME)


def env_var() -> str | None:
    """The environment variable choosing the data folder, if one is set:
    ENV_VAR, else the older OLD_ENV_VAR."""
    for var in (ENV_VAR, OLD_ENV_VAR):
        if os.environ.get(var, "").strip():
            return var
    return None


def chosen_data_dir() -> Path | None:
    """The folder chosen instead of the default, if any."""
    var = env_var()
    if var is not None:
        return Path(os.environ[var].strip()).expanduser()
    location = LOCATION_FILE if LOCATION_FILE.exists() else OLD_LOCATION_FILE
    try:
        data = json.loads(location.read_text(encoding="utf-8"))
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


def source() -> str:
    """What chose the data folder: "fallback" (the chosen one couldn't be
    used), "env" (ARMARIUS_DATA or ARS_MAGICA_MANAGER_DATA), "chosen"
    (LOCATION_FILE) or "default"."""
    if _fallback is not None:
        return "fallback"
    if env_var() is not None:
        return "env"
    return "chosen" if chosen_data_dir() is not None else "default"


#: How the saga picker says what chose the folder ("env" names the
#: variable: see source_text()).
SOURCE_TEXT = {
    "fallback": "the folder chosen couldn't be used, so the app fell back to this one",
    "env": "set by the {var} environment variable",
    "chosen": "chosen in the app",
    "default": "the default",
}


def source_text() -> str:
    """What chose the data folder, as the saga picker says it."""
    return SOURCE_TEXT[source()].format(var=env_var())


def remember_data_dir(folder: Path) -> None:
    """Use `folder` as the data folder from now on: it goes in
    LOCATION_FILE, and any fallback is dropped."""
    global _fallback
    LOCATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCATION_FILE.write_text(
        json.dumps({"data_dir": str(folder)}, indent=2), encoding="utf-8"
    )
    _fallback = None


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
        "nothing was moved. Change save folder, in More (m) on the saga "
        "picker, chooses another."
    )


def move_old_default_folder() -> str | None:
    """Rename the default folder from the app's old name to its new one,
    once, and return a line saying so (None when nothing was done).

    Only the default folder moves: one chosen in the app or by an
    environment variable stays where it is. When both folders already
    exist nothing is merged: the new one is used and the old one is left
    as it is (the line says so when only the old one holds sagas). When the rename fails (a file in it open elsewhere), the old
    folder goes on being used, as settle_data_dir()'s fallback is."""
    global _fallback
    if source() != "default":
        return None
    old, new = old_default_data_dir(), default_data_dir()
    if not old.is_dir() or old.resolve() == new.resolve():
        return None
    if new.exists():
        if any((old / SAGAS).glob("*.json")) and not any((new / SAGAS).glob("*.json")):
            return f"Your sagas are still in {old}: {new} is used now."
        return None
    try:
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)
    except OSError as problem:
        _fallback = old
        return f"Couldn't rename {old} to {new} ({problem}); using {old}."
    return f"Moved your data folder from {old} to {new}."


def move_legacy_data(old: Path = DATA_DIR, new: Path | None = None) -> list[str]:
    """Move the user data from the repo's data/ folder (`old`) to the data
    folder (`new`), once (see move_user_data())."""
    return move_user_data(old, data_dir() if new is None else new)


def move_user_data(old: Path, new: Path) -> list[str]:
    """Move the user data from the folder `old` to `new`: each saga file,
    backup, export, portrait, the settings file and the host key not already at
    `new` is moved; one already there is left where it was, never
    overwritten. Hidden files (a saga's presence marks) stay. Returns a
    line per thing moved or left, for the app to say so."""
    if old.resolve() == new.resolve():
        return []
    notes: list[str] = []
    sources: list[Path] = []
    for folder in (old / SAGAS, old / EXPORTS, old / PORTRAITS):
        if folder.is_dir():
            sources += sorted(
                p
                for p in folder.rglob("*")
                if p.is_file()
                and not any(part.startswith(".") for part in p.relative_to(old).parts)
            )
    sources += [old / name for name in (SETTINGS, HOST_KEY) if (old / name).is_file()]
    for source in sources:
        relative = source.relative_to(old)
        target = new / relative
        if target.exists():
            notes.append(f"Left {relative.as_posix()}: {target} already exists")
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source, target)
        except OSError as problem:
            # Left where it was, and the note says so.
            notes.append(f"Couldn't move {relative.as_posix()}: {problem}")
            continue
        notes.append(f"Moved {relative.as_posix()}")
    return notes
