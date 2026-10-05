"""JSON persistence for app-wide settings (not tied to any one saga)."""

from __future__ import annotations

import json

from . import DATA_DIR
from .files import write_atomic

SETTINGS_PATH = DATA_DIR / "app_settings.json"


def load_settings() -> dict:
    """The saved settings; {} when there are none, or when the file can't be
    read as a JSON object (settings are only conveniences, so a damaged file
    must never stop the app starting)."""
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> None:
    write_atomic(SETTINGS_PATH, json.dumps(settings, indent=2))


def update_settings(**changes: object) -> None:
    """Save `changes` into the settings file, keeping every other setting."""
    save_settings(load_settings() | changes)
