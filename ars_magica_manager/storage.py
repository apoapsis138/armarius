"""JSON persistence for sagas. One file per saga, in the sagas folder of the
user's data folder (paths.data_dir())."""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from dataclasses import fields as dataclass_fields
from pathlib import Path
from typing import Any

from . import __version__, laboratories, paths, settings
from .files import write_atomic
from .merge import merge
from .models import Saga

SAGAS_DIR = paths.data_dir() / paths.SAGAS

_SLUG_RE = re.compile(r"[^a-z0-9]+")


#: Where Export offers to write an exported covenant, laboratory or character;
#: the folder is made on the first export.
EXPORTS_DIR = paths.data_dir() / paths.EXPORTS

#: Where a character's portrait is copied when it is chosen.
PORTRAITS_DIR = paths.data_dir() / paths.PORTRAITS


def use_data_dir(folder: Path) -> None:
    """Read and write the sagas, exports and settings in `folder` from now
    on (a save folder chosen while the app runs)."""
    global SAGAS_DIR, EXPORTS_DIR, PORTRAITS_DIR
    SAGAS_DIR = folder / paths.SAGAS
    EXPORTS_DIR = folder / paths.EXPORTS
    PORTRAITS_DIR = folder / paths.PORTRAITS
    settings.SETTINGS_PATH = folder / paths.SETTINGS


def slugify(text: str) -> str:
    slug = _SLUG_RE.sub("_", text.strip().lower()).strip("_")
    return slug or "id"


def generate_unique_id(name: str, existing_ids: Iterable[str]) -> str:
    """A slug derived from `name`, disambiguated against `existing_ids`.

    Used for saga ids (checked against ids on disk) and for covenant/
    character/laboratory/book ids (checked against ids already in that
    saga) -- anywhere we need a filesystem- and JSON-key-safe id from a
    human-entered name.
    """
    base = slugify(name)
    existing = set(existing_ids)
    if base not in existing:
        return base
    suffix = 2
    while f"{base}_{suffix}" in existing:
        suffix += 1
    return f"{base}_{suffix}"


def generate_saga_id(name: str) -> str:
    """A filesystem-safe, unique saga id derived from its name."""
    return generate_unique_id(name, list_sagas())


def saga_path(saga_id: str) -> Path:
    return SAGAS_DIR / f"{saga_id}.json"


#: What this copy of the app last saw of each saga, by its file: the file's
#: text and data as this copy last read or wrote it, and this copy's own
#: saga as plain data then -- what save_saga merges its changes against.
_last_seen: dict[str, tuple[str, dict[str, Any], dict[str, Any]]] = {}

#: Takes back, before a save, the changes whoever is signed in to this copy
#: may not make (players.guard_changes, set while a player is signed
#: in): (this copy's saga as last seen, as now) -> (as it may be
#: saved, what was taken back).
guard: (
    Callable[[dict[str, Any], dict[str, Any]], tuple[dict[str, Any], list[str]]] | None
) = None

#: Who is saving from this copy (a signed-in player's name; "" for the
#: storyguide's own window), recorded in the saga as Saga.saved_by.
saved_by: str = ""

#: Where save_saga last kept this copy's value over another copy's newer
#: one ("characters[mag1].name", ...), for the saga last saved.
last_conflicts: list[str] = []


def save_saga(saga: Saga) -> Path:
    """Save `saga`. Other copies of the app may share the file (a hosted saga): under a
    lock, the file is re-read and only what this copy changed since it last loaded or
    saved the saga is written into it, so another copy's changes stay. Where both
    changed the same value, this save's wins (listed in last_conflicts)."""
    saga.app_version = __version__
    saga.saved_by = saved_by
    path = saga_path(saga.id)
    ours = asdict(saga)
    with _saga_lock(saga.id):
        seen = _last_seen.get(str(path))
        theirs = base = None
        if seen is not None:
            text, file_data, base = seen
            on_disk = _read_text(path)
            # The file as this copy left it needn't be read again.
            theirs = file_data if on_disk == text else _normalized(on_disk)
        if guard is not None and base is not None:
            ours, _ = guard(base, ours)
        if base is None or theirs is None:
            data, conflicts = ours, []
        else:
            data, conflicts = merge(base, ours, theirs)
        text = json.dumps(data, indent=2)
        write_atomic(path, text)
    _last_seen[str(path)] = (text, data, ours)
    last_conflicts[:] = conflicts
    return path


def reload_into(saga: Saga) -> list[tuple[str, str]] | None:
    """Bring `saga`, as this copy holds it, up to date with its file after
    another copy saved it, keeping its objects -- the sheets on
    show hold them -- and updating them in place. Returns the records that
    changed, as (list, id) pairs such as ("characters", "mag1"), with
    ("saga", "") for the saga's own fields; None when the file is as this
    copy last saw it (or can't be read)."""
    path = saga_path(saga.id)
    seen = _last_seen.get(str(path))
    text = _read_text(path)
    if text is None or (seen is not None and seen[0] == text):
        return None
    try:
        fresh = _from_data(json.loads(text))
    except ValueError, TypeError, KeyError:
        return None
    changed = _update_in_place(saga, fresh)
    data = asdict(saga)
    _last_seen[str(path)] = (text, data, data)
    return changed


def _update_in_place(saga: Saga, fresh: Saga) -> list[tuple[str, str]]:
    """Make `saga` hold `fresh`'s data: each list of records keeps the
    objects of the records still there (their fields updated), drops the
    ones gone and adds the new ones, in `fresh`'s order."""
    changed: list[tuple[str, str]] = []
    for f in dataclass_fields(Saga):
        old, new = getattr(saga, f.name), getattr(fresh, f.name)
        if old == new:
            continue
        if _is_records(old) and _is_records(new):
            by_id = {r.id: r for r in old}
            kept = []
            for record in new:
                existing = by_id.get(record.id)
                if existing is None:
                    kept.append(record)
                    changed.append((f.name, record.id))
                    continue
                if existing != record:
                    for rf in dataclass_fields(record):
                        setattr(existing, rf.name, getattr(record, rf.name))
                    changed.append((f.name, record.id))
                kept.append(existing)
            new_ids = {r.id for r in new}
            changed += [(f.name, r.id) for r in old if r.id not in new_ids]
            old[:] = kept
        else:
            setattr(saga, f.name, new)
            if f.name not in ("app_version", "saved_by"):
                changed.append(("saga", ""))
    return changed


def _is_records(value: object) -> bool:
    return isinstance(value, list) and all(
        is_dataclass(item) and isinstance(getattr(item, "id", None), str)
        for item in value
    )


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _normalized(text: str | None) -> dict[str, Any] | None:
    """A saga file's data as load_saga would read it (older shapes upgraded,
    stale keys dropped), or None if there's no readable file."""
    if text is None:
        return None
    try:
        return asdict(_from_data(json.loads(text)))
    except ValueError, TypeError, KeyError:
        return None


#: How long save_saga waits for another copy's save to finish, and after
#: how long a lock is taken to be left over from a copy that died mid-save.
_LOCK_WAIT = 10.0
_LOCK_STALE = 30.0


@contextmanager
def _saga_lock(saga_id: str) -> Iterator[None]:
    """Hold the saga's lock file (".<id>.lock" beside it) while saving, so two
    copies never merge into the file at once."""
    lock = SAGAS_DIR / f".{saga_id}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + _LOCK_WAIT
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except FileExistsError:
            try:
                stale = time.time() - lock.stat().st_mtime > _LOCK_STALE
            except OSError:
                continue  # just released: try again
            if stale or time.monotonic() > deadline:
                lock.unlink(missing_ok=True)
                continue
            time.sleep(0.02)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


#: How many backups backup_saga() keeps of each saga: the newest, plus older
#: ones numbered 1 (the one before) upwards.
BACKUPS_KEPT = 5


def backup_path(saga_id: str, age: int = 0) -> Path:
    """Where backup_saga() keeps a saga's backups (a subfolder, so
    list_sagas() never lists them): `<id>.json` for the newest (age 0), and
    `<id>.1.json` ... for older ones."""
    name = f"{saga_id}.json" if age == 0 else f"{saga_id}.{age}.json"
    return SAGAS_DIR / "backups" / name


def backup_saga(saga: Saga) -> Path:
    """Save `saga` as it stands as its newest backup -- taken just before a
    season is applied, so that season can be undone by copying the backup
    back over the saga's file. The previous backups move one place older and
    the oldest beyond BACKUPS_KEPT is dropped."""
    backup_path(saga.id, BACKUPS_KEPT - 1).unlink(missing_ok=True)
    for age in range(BACKUPS_KEPT - 2, -1, -1):
        older = backup_path(saga.id, age)
        if older.exists():
            older.replace(backup_path(saga.id, age + 1))
    path = backup_path(saga.id)
    saga.app_version = __version__
    write_atomic(path, json.dumps(asdict(saga), indent=2))
    return path


def load_saga(saga_id: str) -> Saga:
    path = saga_path(saga_id)
    text = path.read_text(encoding="utf-8")
    saga = _from_data(json.loads(text))
    data = asdict(saga)
    _last_seen[str(path)] = (text, data, data)
    return saga


def _from_data(data: dict[str, Any]) -> Saga:
    saga = Saga.from_dict(data)
    for lab in saga.laboratories:
        # Specialization grants typed in before the catalog carried them.
        laboratories.migrate_specialty_stand_ins(lab)
    return saga


def delete_saga(saga_id: str) -> None:
    """Permanently delete a saga's file (no-op if it is already gone)."""
    saga_path(saga_id).unlink(missing_ok=True)
    _last_seen.pop(str(saga_path(saga_id)), None)


def list_sagas() -> list[str]:
    if not SAGAS_DIR.exists():
        return []
    return sorted(path.stem for path in SAGAS_DIR.glob("*.json"))
