"""The desktop Seasons page: the saga's past seasons, as the terminal's
Seasons node lists them, and the results of the season just advanced.

It is a Codex: the rail lists the seasons, newest first (the season just
played out first of all, even when the saga keeps no records); the
chapter shows the chosen season's record (seasons.record_table), grouped
by covenant, a row a person.
"""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import advance_forms, seasons
from ..models import Saga, SeasonRecord
from .character_sheet import TextBlock
from .pages import page_header
from .themes import Palette
from .widgets import Codex, scrolling_page, serif, table_view, text

#: The chapter of the season just played out.
RESULTS = "Just played"


class SeasonsPage(QWidget):
    """`saga`'s seasons; `played`, the season just advanced, comes first
    with the line saying what advancing did."""

    def __init__(
        self, saga: Saga, p: Palette, played: advance_forms.Played | None = None
    ) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        records = list(reversed(saga.season_records))
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            page_header(
                "Seasons",
                f"It is {saga.current_season} {saga.current_year} · "
                f"{len(records)} season(s) recorded",
                p,
                "season",
            )
        )
        self.codex = Codex(p)
        self.codex.inspect("Seasons", "", advance_forms.records_note(saga))
        if played is not None:
            record = played.advanced.record
            self.codex.add(
                RESULTS, "season", self._record(record, played.message, results=True)
            )
            if records and records[0] is record:
                records = records[1:]
        for record in records:
            self.codex.add(seasons.record_label(record), "season", self._record(record))
        if not self.codex.chapters():
            outer.addWidget(
                text(
                    "No seasons recorded yet: they're kept as seasons are "
                    "advanced (Advance in the top bar)."
                    if saga.keep_season_records
                    else "Season records are off (Edit Saga): new seasons "
                    "aren't kept here.",
                    p["dim"],
                    serif(13, italic=True),
                    wrap=True,
                )
            )
            outer.addStretch(1)
            return
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _record(
        self, record: SeasonRecord, message: str = "", *, results: bool = False
    ) -> QWidget:
        p = self.p
        parts: list[QWidget] = []
        if message:
            parts.append(TextBlock(message, p))
        parts.append(
            text(f"{record.season} {record.year}", p["heading"], serif(15, bold=True))
        )
        if record.lines:
            parts.append(
                table_view(seasons.record_table(self.saga, record), p, lambda _: None)
            )
        else:
            parts.append(
                TextBlock("[dim]Nobody's season was planned or applied.[/]", p)
            )
        if results:
            parts.append(
                TextBlock(f"[dim]{advance_forms.records_note(self.saga)}[/]", p)
            )
        return scrolling_page(p, *parts)
