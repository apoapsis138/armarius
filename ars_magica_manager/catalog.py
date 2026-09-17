"""Loads the shared Virtue/Flaw catalog (reference data, not per-saga)."""

from __future__ import annotations

import json
from pathlib import Path

from .models import VirtueFlawDef

CATALOG_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "virtue_flaw_catalog.json"
)


def load_virtue_flaw_catalog(path: Path = CATALOG_PATH) -> list[VirtueFlawDef]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [VirtueFlawDef.from_dict(entry) for entry in data]
