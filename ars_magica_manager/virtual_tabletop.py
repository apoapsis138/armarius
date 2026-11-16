"""The Virtual Tabletop (Preview) setting: off by default, it shows the
Chronicle and Begin and End Session while the Virtual Tabletop is still
being built (ADR 0027). It is an app setting of the computer that hosts,
not of a saga; Remote seats work without it."""

from __future__ import annotations

from . import settings

#: The setting's key in the app's settings file.
KEY = "virtual_tabletop"


def on() -> bool:
    """Whether the preview is turned on here; anything but True is off."""
    return settings.load_settings().get(KEY) is True


def set_on(value: bool) -> None:
    settings.update_settings(**{KEY: value})
