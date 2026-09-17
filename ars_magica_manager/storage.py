"""JSON persistence for sagas. One file per saga, under data/sagas/."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import Saga

SAGAS_DIR = Path(__file__).resolve().parent.parent / "data" / "sagas"


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


def list_sagas() -> list[str]:
    if not SAGAS_DIR.exists():
        return []
    return sorted(path.stem for path in SAGAS_DIR.glob("*.json"))
