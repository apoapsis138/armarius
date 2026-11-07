"""The saga's Seasons sheet: the date and how far Ahead looks, then what
is coming season by season (ahead.py) and the seasons recorded, newest
first, over the chosen one's record."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, Static, TabbedContent

from .... import ahead, attention, seasons, world_turns
from ....markup import aligned, escape
from ....models import Saga, SeasonRecord
from ....sections import (
    AHEAD_SECTION,
    ATTENTION_SECTION,
    SEASONS_INFO_SECTION,
    SEASONS_RECORDED_SECTION,
    WORLD_TURNS_SECTION,
)
from ..widgets import PinnedCollapsible, SelectableList, SheetSection, TwoColumns
from .base import SheetView


class SeasonsSheetView(SheetView):
    """The Seasons node: its facts, then Needs You, Looking Ahead and the
    Seasons Recorded, over the chosen season's record."""

    DEFAULT_CSS = """
    SeasonsSheetView #seasons-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-seasons"

    def __init__(self, saga: Saga) -> None:
        super().__init__(saga)
        self._record = 0
        #: The Needs You row the panel shows (None: the record chosen).
        self._need: int | None = None
        #: The Looking Ahead row the panel shows (None: the record chosen).
        self._entry: int | None = None
        #: The World Turned row the panel shows (None: the record chosen).
        self._turn: int | None = None

    def compose(self) -> ComposeResult:
        watched = (
            SEASONS_INFO_SECTION,
            ATTENTION_SECTION,
            AHEAD_SECTION,
            WORLD_TURNS_SECTION,
        )
        with (
            Vertical(id="seasons-top-panel"),
            PinnedCollapsible(title="Seasons", id=SEASONS_INFO_SECTION),
        ):
            with TwoColumns(id="seasons-info-body", text=True):
                yield self._static(
                    watched, lambda: self._facts(0), id="seasons-info-left"
                )
                yield self._static(
                    watched, lambda: self._facts(1), id="seasons-info-right"
                )
            yield Button("Edit (e)", id="btn-seasons-edit", compact=True)
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Seasons", "tab-seasons", self._seasons_tab)

    def _facts(self, column: int) -> str:
        found = [*ahead.facts(self.saga), attention.fact(self.saga)]
        shown = found[:2] if column == 0 else found[2:]
        return aligned([(f.label, escape(f.value)) for f in shown])

    def _seasons_tab(self) -> ComposeResult:
        saga = self.saga
        watched = (
            SEASONS_INFO_SECTION,
            ATTENTION_SECTION,
            AHEAD_SECTION,
            WORLD_TURNS_SECTION,
        )
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(
                    title=self._titled(
                        watched, ATTENTION_SECTION, lambda: attention.title(saga)
                    ),
                    id=ATTENTION_SECTION,
                ):
                    yield self._list(
                        watched,
                        lambda: attention.grid(saga).lines(),
                        id="attention-list",
                    )
                with SheetSection(
                    title=self._titled(
                        watched, AHEAD_SECTION, lambda: ahead.title(saga)
                    ),
                    id=AHEAD_SECTION,
                ):
                    yield self._list(
                        watched,
                        lambda: ahead.grid(saga).lines(),
                        id="ahead-list",
                    )
                    yield Static(
                        "[$label]Each Winter the world turns: after Advance "
                        "Season, the yearly step offers what has come due.[/]",
                        id="ahead-note",
                    )
                with SheetSection(
                    title=self._titled(
                        WORLD_TURNS_SECTION,
                        WORLD_TURNS_SECTION,
                        lambda: world_turns.turns_title(saga),
                    ),
                    id=WORLD_TURNS_SECTION,
                ):
                    yield self._list(
                        WORLD_TURNS_SECTION,
                        lambda: world_turns.turn_rows(saga),
                        id="world-turns-list",
                    )
                with SheetSection(
                    title=self._titled(
                        SEASONS_RECORDED_SECTION,
                        SEASONS_RECORDED_SECTION,
                        lambda: f"Seasons Recorded ({len(saga.season_records)})",
                    ),
                    id=SEASONS_RECORDED_SECTION,
                ):
                    if not saga.keep_season_records:
                        yield Static(
                            "[$label]Season records are off (the saga's settings): new "
                            "seasons aren't kept here.[/]",
                            id="season-records-off",
                        )
                    yield self._list(
                        SEASONS_RECORDED_SECTION,
                        self._record_rows,
                        id="season-records-list",
                    )
            yield self._panel(
                (*watched, SEASONS_RECORDED_SECTION, WORLD_TURNS_SECTION),
                self._panel_text,
                id="season-record-text",
            )

    def _records(self) -> list[SeasonRecord]:
        return list(reversed(self.saga.season_records))

    def _record_rows(self) -> list[tuple[int | None, str]]:
        records = self._records()
        if not records:
            return [
                (
                    None,
                    "[$label]No seasons recorded yet: they're kept as seasons "
                    "are applied (t).[/]",
                )
            ]
        return [(i, escape(seasons.record_label(r))) for i, r in enumerate(records)]

    def _record_text(self) -> str:
        records = self._records()
        if not records:
            return "[$label]Choose an entry, or a season recorded, to see it here.[/]"
        return seasons.record_text(
            self.saga, records[min(self._record, len(records) - 1)]
        )

    def _panel_text(self) -> str:
        if self._need is not None:
            found = attention.text(self.saga, self._need)
            if found:
                return found
            self._need = None
        if self._entry is not None:
            found = ahead.shown(self.saga)
            if self._entry < len(found):
                return ahead.detail_text(self.saga, found[self._entry])
            self._entry = None
        if self._turn is not None:
            turns = list(reversed(self.saga.world_turns))
            if self._turn < len(turns):
                return world_turns.turn_text(turns[self._turn])
            self._turn = None
        return self._record_text()

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A row was chosen: show it in the panel."""
        list_id = event.selectable_list.id
        if list_id == "attention-list":
            self._need, self._entry, self._turn = event.data_index, None, None
        elif list_id == "ahead-list":
            self._need, self._entry, self._turn = None, event.data_index, None
        elif list_id == "world-turns-list":
            self._need, self._entry, self._turn = None, None, event.data_index
        elif list_id == "season-records-list":
            self._need = self._entry = self._turn = None
            self._record = event.data_index
        else:
            return
        event.stop()
        self.query_one("#season-record-text", Static).update(self._panel_text())
