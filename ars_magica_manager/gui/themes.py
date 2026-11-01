"""The desktop's Scriptorum themes: the palettes and style sheet are
armarius_style's; which theme was chosen last is the app's.
"""

from __future__ import annotations

from armarius_style.desktop.sheet import style_sheet
from armarius_style.palettes import (
    BURNISH,
    DRAFTING,
    DRAFTING_DARK,
    DRAWN,
    HOVER_WASH,
    IN_CREATION,
    MUREX,
    OPENING_CARD,
    PALETTES,
    PIGMENTS,
    SCRIPTORUM,
    SCRIPTORUM_DARK,
    SEASON_PIGMENTS,
    TINCTURES,
    WASH,
    Palette,
    for_mode,
    murex,
    wash_style,
)

from .. import settings

#: What the app's other modules take from armarius_style through here.
__all__ = [
    "BURNISH",
    "DRAFTING",
    "DRAFTING_DARK",
    "DRAWN",
    "HOVER_WASH",
    "IN_CREATION",
    "MUREX",
    "OPENING_CARD",
    "PALETTES",
    "PIGMENTS",
    "SCRIPTORUM",
    "SCRIPTORUM_DARK",
    "SEASON_PIGMENTS",
    "TINCTURES",
    "WASH",
    "Palette",
    "for_mode",
    "murex",
    "style_sheet",
    "wash_style",
]

#: The settings key the desktop's theme is remembered under, by its name
#: (the terminal keeps its own Textual theme under "theme").
THEME = "desktop_theme"


def saved_theme() -> int:
    """The index in PALETTES of the theme chosen last on this computer;
    Scriptorum's when none was, or the one saved is no longer offered."""
    name = settings.load_settings().get(THEME)
    return next((i for i, p in enumerate(PALETTES) if p.name == name), 0)


def remember_theme(index: int) -> None:
    """Keep PALETTES[index] as the theme the desktop opens in."""
    settings.update_settings(**{THEME: PALETTES[index].name})
