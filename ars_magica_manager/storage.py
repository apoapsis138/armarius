"""JSON persistence for sagas. One file per saga, under data/sagas/."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from . import DATA_DIR
from .models import Saga

SAGAS_DIR = DATA_DIR / "sagas"

_SLUG_RE = re.compile(r"[^a-z0-9]+")


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
    SAGAS_DIR.mkdir(parents=True, exist_ok=True)
    path = saga_path(saga.id)
    path.write_text(json.dumps(asdict(saga), indent=2), encoding="utf-8")
    return path


def load_saga(saga_id: str) -> Saga:
    data = json.loads(saga_path(saga_id).read_text(encoding="utf-8"))
    return Saga.from_dict(data)


def delete_saga(saga_id: str) -> None:
    """Permanently delete a saga's file (no-op if it is already gone)."""
    saga_path(saga_id).unlink(missing_ok=True)


def list_sagas() -> list[str]:
    if not SAGAS_DIR.exists():
        return []
    return sorted(path.stem for path in SAGAS_DIR.glob("*.json"))


def read_text_any(path: Path) -> str:
    """A text file's contents: UTF-8 (with or without Excel's byte-order mark),
    falling back to Windows-1252 for older spreadsheets."""
    data = Path(path).read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252")
