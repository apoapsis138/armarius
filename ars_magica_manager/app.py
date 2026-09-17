"""Textual TUI shell. Grows into saga/covenant/character browsing in Phase 1."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.widgets import Footer, Header, Static

from . import storage


class ArsMagicaManagerApp(App[None]):
    """Skeleton shell for the Ars Magica Manager TUI."""

    TITLE = "Ars Magica Manager"
    BINDINGS: ClassVar[list[BindingType]] = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._saga_summary(), id="saga-summary")
        yield Footer()

    def _saga_summary(self) -> str:
        sagas = storage.list_sagas()
        if not sagas:
            return (
                "No sagas found yet.\n\n"
                "Saga data lives under data/sagas/*.json "
                "(see ars_magica_manager/storage.py)."
            )
        lines = ["Sagas:", *(f"  - {saga_id}" for saga_id in sagas)]
        return "\n".join(lines)
