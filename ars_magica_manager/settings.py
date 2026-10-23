"""JSON persistence for app-wide settings (not tied to any one saga)."""

from __future__ import annotations

import json
from pathlib import Path

from . import paths
from .files import write_atomic


def settings_path() -> Path:
    """The settings file, in the data folder in use."""
    return paths.data_dir() / paths.SETTINGS


def load_settings() -> dict[str, object]:
    """The saved settings; {} when there are none, or when the file can't be
    read as a JSON object (settings are only conveniences, so a damaged file
    must never stop the app starting)."""
    try:
        data = json.loads(settings_path().read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict[str, object]) -> None:
    write_atomic(settings_path(), json.dumps(settings, indent=2))


def update_settings(**changes: object) -> None:
    """Save `changes` into the settings file, keeping every other setting."""
    save_settings(load_settings() | changes)
