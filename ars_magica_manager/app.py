"""Textual app entry point. Screen flow lives in the screens package."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App
from textual.binding import BindingType

from . import __version__
from .screens import SagaPickerScreen
from .settings import load_settings, update_settings
from .themes import SCRIPTORUM, SCRIPTORUM_DARK

#: Theme applied on first launch, or if a saved theme name is no longer registered.
DEFAULT_THEME = SCRIPTORUM.name


class ArsMagicaManagerApp(App[None]):
    """Ars Magica Manager TUI."""

    # In the title, not the sub-title: the workspace uses that for the saga
    # and its date (the Header shows "title — sub_title").
    TITLE = f"Ars Magica Manager v{__version__}"
    BINDINGS: ClassVar[list[BindingType]] = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.register_theme(SCRIPTORUM)
        self.register_theme(SCRIPTORUM_DARK)
        saved_theme = load_settings().get("theme")
        self.theme = (
            saved_theme if saved_theme in self.available_themes else DEFAULT_THEME
        )
        self.push_screen(SagaPickerScreen())

    def watch_theme(self, theme_name: str) -> None:
        update_settings(theme=theme_name)
