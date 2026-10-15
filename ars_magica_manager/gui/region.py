"""The desktop's page for a neighbour (the saga page's Region chapter
lists them as cards: pages.region_chapter): its facts and summary over
its attitude toward each player covenant, the favours owed and its
links. What it says comes from region_sheet.py; its buttons run
neighbour_forms.py."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import neighbour_forms, neighbours, region_sheet
from ..models import Neighbour, Saga
from .character_sheet import section
from .editing import Run
from .figures import fact_grid, prose
from .manage import RecordControls
from .pages import page_header
from .themes import Palette
from .widgets import Codex, scrolling_page, serif, text
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
            page_header(
                neighbour.name,
                region_sheet.card_subtitle(neighbour),
                p,
                neighbours.kind_of(neighbour).key,
            )
        )
        outer.addWidget(fact_grid(region_sheet.neighbour_facts(saga, neighbour), p, 3))
        self.codex = Codex(p)
        self.codex.add("Standing", "region", self._standing())
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _edit(self) -> None:
        self.run(neighbour_forms.edit_neighbour_form(self.saga, self.neighbour))

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
            *relations(self.saga, self.neighbour, p, self.run),
        )
