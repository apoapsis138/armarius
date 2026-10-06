"""Season records: the summary shown after advancing the season,
and the saga's Seasons view listing past seasons."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label, Static

from .. import seasons
from ..models import Saga, SeasonRecord
from .fields import ModalDialog
from .widgets import SelectableList


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

    def __init__(self, saga: Saga, record: SeasonRecord) -> None:
        super().__init__()
        self.saga = saga
        self.record = record

    def compose(self) -> ComposeResult:
        with Vertical(id="summary-dialog", classes="dialog-box"):
            yield Label(
                "The Season's Results", id="summary-title", classes="dialog-title"
            )
            with VerticalScroll(id="summary-scroll"):
                yield Static(
                    seasons.record_text(self.saga, self.record), id="summary-text"
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


class SeasonRecordsView(Vertical):
    """The saga's Seasons node: its past seasons, newest first, over the
    chosen season's record (the newest to start with)."""

    DEFAULT_CSS = """
    SeasonRecordsView {
        height: 1fr;
    }

    SeasonRecordsView #season-records-list {
        height: auto;
        max-height: 12;
    }

    SeasonRecordsView #season-record-scroll {
        height: 1fr;
        margin-top: 1;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga

    def _records(self) -> list[SeasonRecord]:
        return list(reversed(self.saga.season_records))

    def compose(self) -> ComposeResult:
        records = self._records()
        yield Label(f"[b]Seasons ({len(records)})[/]", id="season-records-title")
        if not self.saga.keep_season_records:
            yield Static(
                "[dim]Season records are off (Edit Saga): new seasons aren't "
                "kept here.[/]",
                id="season-records-off",
            )
        yield SelectableList(
            [(i, seasons.record_label(r)) for i, r in enumerate(records)],
            id="season-records-list",
        )
        with VerticalScroll(id="season-record-scroll"):
            yield Static(self._text(0), id="season-record-text")

    def _text(self, index: int) -> str:
        records = self._records()
        if not records:
            return (
                "[dim]No seasons recorded yet: they're kept as seasons are "
                "applied (t).[/]"
            )
        return seasons.record_text(self.saga, records[min(index, len(records) - 1)])

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        self.query_one("#season-record-text", Static).update(
            self._text(event.data_index)
        )
