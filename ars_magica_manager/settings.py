"""JSON persistence for app-wide settings (not tied to any one saga)."""

from __future__ import annotations

import json

from . import DATA_DIR

SETTINGS_PATH = DATA_DIR / "app_settings.json"


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return {}
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def update_settings(**changes: object) -> None:
    """Save `changes` into the settings file, keeping every other setting."""
    save_settings(load_settings() | changes)
