"""Textual app entry point. Screen flow lives in screens.py."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App
from textual.binding import BindingType

from .screens import SagaPickerScreen


class ArsMagicaManagerApp(App[None]):
    """Ars Magica Manager TUI."""

    TITLE = "Ars Magica Manager"
    BINDINGS: ClassVar[list[BindingType]] = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen(SagaPickerScreen())
