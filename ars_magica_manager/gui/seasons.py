"""The desktop Seasons page: what is coming (Ahead), the saga's past
seasons, as the terminal's Seasons node lists them, and the results of
the season just advanced.

It is a Codex: the rail starts with Ahead (gui/ahead.py), then lists the
seasons, newest first (the season just played out first of all, even
when the saga keeps no records); a season's chapter shows its record
(seasons.record_table), grouped by covenant, a row a person.
"""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import seasons, world_turns
from ..forms import advance as advance_forms
from ..models import Saga, SeasonRecord
from .ahead import ahead_section, undertakings_section
from .character_sheet import TextBlock
from .editing import Run
from .medallions import Medallion, beside
from .pages import page_header
from .themes import Palette
from .widgets import Codex, scrolling_page, serif, table_view, text
from .world import table_section

#: The chapter of the season just played out.
RESULTS = "Just played"

#: The chapter of what is coming.
AHEAD = "Ahead"


class SeasonsPage(QWidget):
    """`saga`'s seasons; `played`, the season just advanced, comes first
    with the line saying what advancing did."""

    def __init__(
        self,
        saga: Saga,
        p: Palette,
        played: advance_forms.Played | None = None,
        run: Run = lambda _command: None,
    ) -> None:
        super().__init__()
        self.saga, self.p, self.run = saga, p, run
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
                emblem=Medallion(
                    saga, saga.current_season, saga.current_year, p, radius=24, now=True
                ),
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
        self.codex.add(AHEAD, "season", self._ahead())
        for record in records:
            self.codex.add(seasons.record_label(record), "season", self._record(record))
        if not records and played is None:
            outer.addWidget(
                text(
                    "No seasons recorded yet: they're kept as seasons are "
                    "advanced (Advance in the top bar)."
                    if saga.keep_season_records
                    else "Season records are off (Edit Saga): new seasons "
                    "aren't kept here.",
                    p["dim"],
                    serif(12, italic=True),
                    wrap=True,
                )
            )
        outer.addWidget(self.codex, 1)

    def _ahead(self) -> QWidget:
        """What is coming, then each yearly step's entry, to undo."""
        saga, p = self.saga, self.p
        turns = list(reversed(saga.world_turns))

        def show(row: int) -> None:
            self.codex.inspect(
                world_turns.entry_title(turns[row]),
                "The world turned",
                world_turns.turn_text(turns[row]),
            )

        return scrolling_page(
            p,
            ahead_section(saga, p, self.run, self.codex.inspect),
            undertakings_section(saga, p, self.run),
            table_section(
                world_turns.turns_title(saga),
                world_turns.turns_grid(saga).table(),
                world_turns.turn_ops(saga),
                p,
                self.run,
                empty="Nothing yet: each Winter, Advance Season asks what the "
                "year brought.",
                on_choose=show,
            ),
        )

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
            beside(
                Medallion(self.saga, record.season, record.year, p, radius=20),
                text(
                    f"{record.season} {record.year}", p["heading"], serif(15, bold=True)
                ),
            )
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
