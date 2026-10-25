"""The desktop's page for a neighbour (the saga page's Region chapter
lists them as cards: pages.region_chapter): its facts and summary over
its attitude toward each player covenant, the favours owed and its
links. What it says comes from sheets/region.py; its buttons run
forms/neighbour.py."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import arms, battles, lords, neighbours, place_events, towns
from ..forms import neighbour as neighbour_forms
from ..models import Neighbour, Saga
from ..neighbour_lists import KindList, KindTab
from ..sections import (
    BATTLES_SECTION,
    FAIRS_SECTION,
    GRATITUDE_SECTION,
    TABLES_SECTION,
)
from ..sheets import region as region_sheet
from .bookmark import with_bookmark
from .character_sheet import secrets_chapter, section
from .editing import Chooser, RowVerb, Run, follower, verb_buttons
from .figures import fact_grid, prose
from .heraldry import arms_section
from .manage import RecordControls
from .pages import page_header
from .themes import Palette
from .widgets import Codex, scrolling_page, serif, table_view, text
from .world import relations


class NeighbourPage(QWidget):
    """A neighbour in the Codex layout."""

    def __init__(
        self,
        saga: Saga,
        neighbour: Neighbour,
        p: Palette,
        run: Run = lambda _command: None,
        controls: RecordControls | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.neighbour, self.p, self.run = saga, neighbour, p, run
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            with_bookmark(
                page_header(
                    neighbour.name,
                    region_sheet.card_subtitle(neighbour),
                    p,
                    neighbours.icon_concept(neighbour),
                ),
                controls.bookmark(p) if controls else None,
            )
        )
        outer.addWidget(
            fact_grid(
                region_sheet.neighbour_facts(saga, neighbour),
                p,
                3,
                follow=follower(run),
            )
        )
        self.codex = Codex(p)
        self.ops = neighbour_forms.neighbour_ops(saga, neighbour)
        kind = neighbours.kind_of(neighbour)
        if kind.tab is not None:
            self.codex.add(kind.tab.title, kind.key, self._kind_chapter(kind.tab))
        for more in (m for m in kind.more if not m.after_standing):
            self.codex.add(more.title, kind.key, self._kind_chapter(more, facts=False))
        self.codex.add(
            "Standing" if kind.attitude else "Found Here", "region", self._standing()
        )
        for more in (m for m in kind.more if m.after_standing):
            self.codex.add(more.title, kind.key, self._kind_chapter(more, facts=False))
        self.codex.add("Secrets", "secrets", secrets_chapter(neighbour, p, run))
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _edit(self) -> None:
        self.run(neighbour_forms.edit_neighbour_form(self.saga, self.neighbour))

    def _kind_chapter(self, tab: KindTab, facts: bool = True) -> QWidget:
        """What the neighbour's kind works out (on its first chapter),
        then its lists."""
        saga, n, p = self.saga, self.neighbour, self.p
        worked_out = neighbours.kind_of(n).facts
        shown: list[QWidget] = []
        if facts:
            shown.append(
                section(
                    tab.title,
                    p,
                    fact_grid(
                        worked_out(saga, n) if worked_out is not None else [],
                        p,
                        2,
                        follow=follower(self.run),
                    ),
                    edits={"Edit Neighbour": self._edit},
                )
            )
        for entry in tab.lists:
            more: list[RowVerb] = []
            if entry.section_id == TABLES_SECTION:
                more.append(
                    (
                        "Roll",
                        "more",
                        lambda row: place_events.roll_table(saga, n, row),
                        lambda _row: True,
                    )
                )
            if entry.section_id == FAIRS_SECTION:
                more.append(
                    (
                        "Roll Income",
                        "income",
                        lambda row: towns.roll_fair(saga, n, row),
                        lambda _row: True,
                    )
                )
            if entry.section_id == GRATITUDE_SECTION:
                more.append(
                    (
                        "Redeem Gratitude",
                        "more",
                        lambda row: lords.redeem_form(saga, n, row),
                        lambda _row: True,
                    )
                )
            if entry.section_id == BATTLES_SECTION:
                more.append(
                    (
                        "Battle Event",
                        "more",
                        lambda row: battles.event_for(saga, n, row),
                        lambda _row: True,
                    )
                )
            shown.append(self._grid(entry, more))
        return scrolling_page(p, *shown)

    def _grid(self, entry: KindList, more: Sequence[RowVerb]) -> QWidget:
        """The list `entry` as a table under its title, with its section's
        Add, Edit and Delete (and `more`) acting on the row chosen;
        choosing a row also shows it in full in the inspector."""
        saga, n, p = self.saga, self.neighbour, self.p
        title, grid = entry.title(saga, n), entry.grid(saga, n)
        chooser = Chooser()

        def choose(row: int) -> None:
            chooser.choose(row)
            shown = (
                entry.info(saga, n, row)
                if entry.info is not None
                else grid.row_text(row)
            )
            if shown and row in grid.keys:
                name = grid.rows[grid.keys.index(row)][0]
                self.codex.inspect(name, title.split(" (")[0], shown)

        body = (
            table_view(grid.table(), p, choose)
            if grid.rows
            else text(grid.empty, p["dim"], serif(12.5, italic=True), wrap=True)
        )
        buttons = verb_buttons(
            self.ops[entry.section_id], chooser, self.run, p, more=more
        )
        return section(title, p, body, buttons=buttons)

    def _standing(self) -> QWidget:
        p = self.p
        summary = self.neighbour.summary.strip()
        return scrolling_page(
            p,
            section(
                "Summary",
                p,
                prose(summary, p)
                if summary
                else text(
                    "Not written yet: edit the neighbour to say.",
                    p["dim"],
                    serif(12.5, italic=True),
                    wrap=True,
                ),
                edits={"Edit Neighbour": self._edit},
            ),
            *(
                [arms_section(self.neighbour, p, self.run)]
                if arms.bears_arms(self.neighbour)
                else []
            ),
            *relations(
                self.saga,
                self.neighbour,
                p,
                self.run,
                attitude=neighbours.kind_of(self.neighbour).attitude,
            ),
        )
