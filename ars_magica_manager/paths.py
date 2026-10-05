"""Where the app keeps the user's data (STORY-1127): the saga files, their
backups, exports and the app settings. The shared catalogs stay in the
repo's data/ folder (DATA_DIR).

By default the user data lives in "Ars Magica Manager" in the user's
Documents folder -- the real one, which Windows may have moved into
OneDrive -- where it is easy to find and back up (Hedda, 2026-10-05). Another
folder can be chosen, in order of precedence:

1. the ARS_MAGICA_MANAGER_DATA environment variable;
2. a `data_dir` in LOCATION_FILE, a small JSON file in the user's config
   folder (it can't live in the data folder it points to).

Before STORY-1127 the user data lived in the repo's data/ folder;
move_legacy_data() moves it across once, the first time the app starts.
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


def default_data_dir() -> Path:
    """Ars Magica Manager in the user's Documents folder."""
    return Path(platformdirs.user_documents_dir()) / APP_NAME


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


def data_dir() -> Path:
    """The folder holding the user's data."""
    return chosen_data_dir() or default_data_dir()


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
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source, target)
        notes.append(f"Moved {relative.as_posix()}")
    return notes
