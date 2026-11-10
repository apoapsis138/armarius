"""The desktop's themes: the palettes are in `style`, the themes by name
in `style.liveries`, the style sheet in `style.sheet`; which theme was
chosen last is the app's.
"""

from __future__ import annotations

from .. import settings
from ..style.palettes import (
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
    opening_card,
    wash_style,
)
from .style import liveries
from .style.liveries import THEMES, Theme
from .style.sheet import style_sheet

#: What the app's other modules take from style through here.
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
    "THEMES",
    "TINCTURES",
    "WASH",
    "Palette",
    "Theme",
    "for_mode",
    "liveries",
    "murex",
    "opening_card",
    "style_sheet",
    "wash_style",
]

#: The settings key the desktop's theme is remembered under, by its name
#: (the terminal keeps its own Textual theme under "theme").
THEME = "desktop_theme"


def saved_theme() -> Theme:
    """The theme chosen last on this computer (liveries.THEMES);
    Scriptorum when none was, or the one saved is no longer offered."""
    name = settings.load_settings().get(THEME)
    found = liveries.named(name if isinstance(name, str) else None)
    # A drafting twin's name is never saved; only a theme's own.
    return found if found is not None and found.name == name else THEMES[0]


def remember_theme(theme: Theme) -> None:
    """Keep `theme` as the theme the desktop opens in, by its name."""
    settings.update_settings(**{THEME: theme.name})
