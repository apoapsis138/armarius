"""The summary shown after advancing the season (the saga's Seasons
sheet, sheets/seasons.py, lists the seasons recorded)."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Collapsible, Label, Static

from ... import seasons
from ...markup import escape
from ...models import Saga, SeasonRecord
from .fields import ModalDialog


class SeasonSummaryScreen(ModalDialog[None]):
    """What the season just applied gave everyone, by covenant. Closes with
    Enter or Escape."""

    help_id = "season-summary"

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "cancel", "Close"),
        ("enter", "cancel", "Close"),
    ]

    DEFAULT_CSS = """
    SeasonSummaryScreen {
        align: center middle;
    }

    #summary-dialog {
        width: 96;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #summary-scroll {
        height: auto;
        max-height: 30;
    }

    #summary-text {
        height: auto;
    }

    #summary-note {
        color: $text-muted;
        height: auto;
        margin-top: 1;
    }

    #summary-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        saga: Saga,
        record: SeasonRecord,
        changed: tuple[tuple[str, tuple[str, ...]], ...] = (),
    ) -> None:
        super().__init__()
        self.saga = saga
        self.record = record
        #: What changed in each player character over the season.
        self.changed = changed

    def compose(self) -> ComposeResult:
        with Vertical(id="summary-dialog", classes="dialog-box"):
            yield Label(
                "The Season's Results", id="summary-title", classes="dialog-title"
            )
            with VerticalScroll(id="summary-scroll"):
                yield Static(
                    seasons.record_text(self.saga, self.record), id="summary-text"
                )
                if self.changed:
                    with Collapsible(
                        title=f"What changed ({len(self.changed)})",
                        collapsed=True,
                        id="summary-changed",
                    ):
                        yield Static(
                            "\n".join(
                                f"[b]{escape(name)}:[/] {escape('; '.join(lines))}."
                                for name, lines in self.changed
                            )
                        )
            yield Static(
                "Kept under Seasons in the tree."
                if self.saga.keep_season_records
                else "Season records are off (Edit Saga): each character's "
                "Diary still has theirs.",
                id="summary-note",
            )
            with Horizontal(id="summary-buttons"):
                yield Button("Close", id="btn-close", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#btn-close", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss(None)
