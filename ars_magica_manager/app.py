"""Textual app entry point. Screen flow lives in screens.py."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App
from textual.binding import BindingType

from .screens import SagaPickerScreen
from .themes import SCRIPTORUM, SCRIPTORUM_DARK


class ArsMagicaManagerApp(App[None]):
    """Ars Magica Manager TUI."""

    TITLE = "Ars Magica Manager"
    BINDINGS: ClassVar[list[BindingType]] = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.register_theme(SCRIPTORUM)
        self.register_theme(SCRIPTORUM_DARK)
        self.push_screen(SagaPickerScreen())
