"""JSON persistence for sagas. One file per saga, in the sagas folder of the
user's data folder (paths.data_dir())."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from . import __version__, laboratories, paths
from .files import write_atomic
from .models import Saga

SAGAS_DIR = paths.data_dir() / paths.SAGAS

_SLUG_RE = re.compile(r"[^a-z0-9]+")


#: Where Export offers to write an exported covenant, laboratory or character
#: (STORY-109); the folder is made on the first export.
EXPORTS_DIR = paths.data_dir() / paths.EXPORTS


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


def save_saga(saga: Saga) -> Path:
    saga.app_version = __version__
    path = saga_path(saga.id)
    write_atomic(path, json.dumps(asdict(saga), indent=2))
    return path


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
    data = json.loads(saga_path(saga_id).read_text(encoding="utf-8"))
    saga = Saga.from_dict(data)
    for lab in saga.laboratories:
        # Specialization grants typed in before the catalog carried them.
        laboratories.migrate_specialty_stand_ins(lab)
    return saga


def delete_saga(saga_id: str) -> None:
    """Permanently delete a saga's file (no-op if it is already gone)."""
    saga_path(saga_id).unlink(missing_ok=True)


def list_sagas() -> list[str]:
    if not SAGAS_DIR.exists():
        return []
    return sorted(path.stem for path in SAGAS_DIR.glob("*.json"))
