"""A hosted saga's backup, taken while it is in use (admin backup).

One zip per backup, named for the saga and the moment (UTC), holding the
saga's file and its Remote seat files laid out as in the data folder
(`sagas/ID.json`, `remote/NAME-devices.json`, its Sessions' Chronicles
`chronicles/ID/SESSION.jsonl`, its Shows' copies `shows/ID/...`), so
restoring is
unzipping into the data folder. Each file is read under the lock every
writer of it holds, so a backup taken while players save is whole: never
half of one save and half of the next.

The host key is never in it. Keys live apart, in the keychain or the key
folder (ADR 0022), and are kept, or lost and replaced, on their own: a
lost key costs a re-invite, a leaked backup that held one would cost the
saga's secrecy.
"""

from __future__ import annotations

import datetime
import os
import re
import tempfile
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from . import chronicle, paths, shows, storage
from .files import held_lock
from .remote.folder import lock_of, saga_remote_files
from .remote.key_files import FOLDER_VARIABLE

#: Where backups go when no folder is given (the container sets it).
BACKUPS_VARIABLE = "ARMARIUS_BACKUPS"
#: How many of a saga's backups are kept unless told otherwise.
KEEP = 30
_STAMP = "%Y%m%dT%H%M%SZ"


@dataclass(frozen=True)
class Backup:
    path: Path
    files: tuple[str, ...]
    removed: tuple[Path, ...]


def backups_folder(given: str | None) -> Path:
    """The folder `given`, else ARMARIUS_BACKUPS's, else ValueError."""
    chosen = (given or os.environ.get(BACKUPS_VARIABLE, "")).strip()
    if not chosen:
        raise ValueError(
            f"Say where backups go: --to FOLDER, or set {BACKUPS_VARIABLE}."
        )
    return Path(chosen)


def _name_pattern(saga_id: str) -> re.Pattern[str]:
    return re.compile(rf"{re.escape(saga_id)}-(\d{{8}}T\d{{6}}Z)(-\d+)?\.zip")


def saga_backups(folder: Path, saga_id: str) -> list[Path]:
    """The saga's backups in `folder`, oldest first (two in one second in
    the order they were taken)."""
    if not folder.is_dir():
        return []
    pattern = _name_pattern(saga_id)
    found = [(p, m) for p in folder.iterdir() if (m := pattern.fullmatch(p.name))]
    found.sort(key=lambda pm: (pm[1].group(1), int((pm[1].group(2) or "-0")[1:])))
    return [p for p, _ in found]


def _contents(saga_id: str, saga_name: str) -> dict[str, bytes]:
    """Each file's place in the zip and its bytes, each read under its lock."""
    found = {f"{paths.SAGAS}/{saga_id}.json": storage.saga_text_now(saga_id).encode()}
    for path in saga_remote_files(saga_name):
        with held_lock(lock_of(path)):
            found[f"remote/{path.name}"] = path.read_bytes()
    # A Chronicle is only ever appended to, a whole line at a time: a copy
    # taken mid-write ends in a half line, which reading it back drops.
    for path in chronicle.files_of(saga_id):
        found[f"{paths.CHRONICLES}/{saga_id}/{path.name}"] = path.read_bytes()
    # A Show's copy is written once, before its entry, and never changed.
    for path in shows.files_of(saga_id):
        found[f"{paths.SHOWS}/{saga_id}/{path.name}"] = path.read_bytes()
    return found


def _check_apart_from_keys(folder: Path) -> None:
    """Refuse a backup folder that is, or is inside, the key folder: a
    backup must never sit with the keys."""
    keys = os.environ.get(FOLDER_VARIABLE, "").strip()
    if keys:
        key_folder = Path(keys).resolve()
        target = folder.resolve()
        if target == key_folder or key_folder in target.parents:
            raise ValueError(
                f"{folder} is the key folder, or inside it. Keep backups apart "
                "from the keys."
            )


def take(
    saga_id: str,
    saga_name: str,
    folder: Path,
    keep: int = KEEP,
    now: Callable[[], datetime.datetime] = lambda: datetime.datetime.now(datetime.UTC),
) -> Backup:
    """Back the saga up into `folder` and keep its newest `keep` backups.
    ValueError for a folder that can't hold one, OSError if a file can't
    be read or written."""
    if keep < 1:
        raise ValueError("Keep at least one backup.")
    _check_apart_from_keys(folder)
    folder.mkdir(parents=True, exist_ok=True)
    contents = _contents(saga_id, saga_name)
    stem = f"{saga_id}-{now().strftime(_STAMP)}"
    target = folder / f"{stem}.zip"
    count = 1
    while target.exists():
        target = folder / f"{stem}-{count}.zip"
        count += 1
    # The temp file is the owner's alone from the start (mkstemp makes it
    # 0600): a backup holds the whole saga, Secrets included.
    handle, temp = tempfile.mkstemp(dir=folder, prefix=f".{stem}.", suffix=".tmp")
    try:
        with (
            os.fdopen(handle, "wb") as raw,
            zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as archive,
        ):
            for name, data in contents.items():
                archive.writestr(name, data)
        os.replace(temp, target)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise
    older = saga_backups(folder, saga_id)[:-keep]
    for path in older:
        path.unlink(missing_ok=True)
    return Backup(target, tuple(contents), tuple(older))
