"""The desktop Tribunal page in the Codex layout: a header with its name,
when it next meets and its facts, over its chapters: the Roster of its
covenants, worked out from the covenants that belong to it, and Manage.

What it says comes from the shared core (tribunal_sheet.py), as the
terminal's Tribunal sheet does, and its Edit runs the core's form
(tribunal_forms.py)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import artwork, tribunal_forms, tribunal_sheet, tribunals, world
from ..markup import escape
from ..models import Covenant, Saga, Tribunal
from .character_sheet import section
from .editing import Run
from .figures import fact_grid, prose
from .manage import RecordControls
from .pages import symbol_label
from .themes import Palette
from .widgets import Codex, display_name, scrolling_page, serif, table_view, text


def _none(words: str, p: Palette) -> QLabel:
    return text(words, p["dim"], serif(12.5, italic=True), wrap=True)


class TribunalPage(QWidget):
    """A Tribunal in the Codex layout."""

    def __init__(
        self,
        saga: Saga,
        tribunal: Tribunal,
        p: Palette,
        run: Run = lambda _command: None,
        controls: RecordControls | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.tribunal, self.p, self.run = saga, tribunal, p, run
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(self._header())
        self.codex = Codex(p)
        self.codex.add("Roster", "tribunal", self._roster())
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _edit(self) -> None:
        self.run(tribunal_forms.edit_tribunal_form(self.saga, self.tribunal))

    def _inspect(self, covenant: Covenant) -> None:
        summary = covenant.summary.strip() or "Nothing written about it yet."
        self.codex.inspect(
            covenant.name,
            f"{covenant.detail} · {world.votes_text(self.saga, covenant)} votes",
            escape(summary),
        )

    def _header(self) -> QWidget:
        p, t = self.p, self.tribunal
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)
        row.addWidget(
            symbol_label(artwork.icon("tribunal"), p, 56), 0, Qt.AlignmentFlag.AlignTop
        )
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(display_name(tribunals.title(t), p))
        names.addWidget(
            text(
                f"Next meeting: {tribunal_sheet.next_meeting(t)}",
                p["label"],
                serif(12.5, italic=True),
            )
        )
        row.addLayout(names)
        row.addStretch(1)
        # When and where it meets is the line under the name.
        facts = [
            f
            for f in tribunal_sheet.facts(self.saga, t)
            if f.label not in ("Next meeting", "Meeting place")
        ]
        row.addWidget(fact_grid(facts, p, 2))
        return box

    def _roster(self) -> QWidget:
        p, saga, t = self.p, self.saga, self.tribunal
        summary = t.summary.strip()
        members = tribunals.covenants_of(saga, t)
        table = tribunal_sheet.roster_table(saga, t)
        return scrolling_page(
            p,
            section(
                "In the Saga",
                p,
                prose(summary, p)
                if summary
                else _none("Not written yet: edit the Tribunal to say.", p),
                edits={"Edit Tribunal": self._edit},
            ),
            section(
                f"Covenants ({len(members)})",
                p,
                table_view(table, p, lambda row: self._inspect(members[row]))
                if members
                else _none(
                    "No covenant belongs to it yet: choose it as a covenant's "
                    "Tribunal in Edit Covenant.",
                    p,
                ),
            ),
        )
