"""The desktop Tribunal page in the Codex layout: a header with its name,
when it next meets and its facts, over its chapters: the Roster of its
covenants and magi of note, worked out from the covenants that belong to
it, its Docket of cases, its Peripheral Code, its Treasury, its Diary,
and Manage.

What it says comes from the shared core (tribunal_sheet.py), as the
terminal's Tribunal sheet does, and its buttons run the core's forms
(tribunal_forms.py)."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import (
    artwork,
    tribunal_forms,
    tribunal_packages,
    tribunal_sheet,
    tribunals,
    world,
)
from .. import character_sheet as cs
from ..markup import aligned, escape
from ..models import Case, Saga, Tribunal
from ..sections import (
    CASES_SECTION,
    CODE_SECTION,
    PAST_CASES_SECTION,
    ROSTER_SECTION,
    TREASURY_SECTION,
    TRIB_DIARY_SECTION,
)
from ..tribunal_sheet import Grid
from .character_sheet import TextBlock, section
from .editing import Chooser, RowVerb, Run, verb_buttons
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
        self.ops = tribunal_forms.tribunal_ops(saga, tribunal)
        self.codex.add("Roster", "tribunal", self._roster())
        self.codex.add("Docket", "worksheet", self._docket())
        self.codex.add("Peripheral Code", "lab_text", self._code())
        self.codex.add("Treasury", "income", self._treasury())
        for extra in tribunal_packages.of(tribunal).lists:
            self.codex.add(
                extra.title,
                "tribunal",
                scrolling_page(
                    p,
                    self._grid(
                        extra.section_title(saga, tribunal),
                        extra.grid(saga, tribunal),
                        extra.section_id,
                    ),
                ),
            )
        self.codex.add("Diary", "year", self._diary())
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _edit(self) -> None:
        self.run(tribunal_forms.edit_tribunal_form(self.saga, self.tribunal))

    def _grid(
        self,
        title: str,
        grid: Grid,
        section_id: str | None,
        on_choose: Callable[[int], None] | None = None,
        more: Sequence[RowVerb] = (),
    ) -> QWidget:
        """`grid` as a table under `title`, with its section's Add, Edit
        and Delete (and `more`) acting on the row chosen."""
        p = self.p
        chooser = Chooser()

        def choose(row: int) -> None:
            chooser.choose(row)
            if on_choose is not None:
                on_choose(row)

        body = (
            table_view(grid.table(), p, choose) if grid.rows else _none(grid.empty, p)
        )
        buttons = (
            verb_buttons(self.ops[section_id], chooser, self.run, p, more=more)
            if section_id is not None
            else []
        )
        return section(title, p, body, buttons=buttons)

    def _show_covenant(self, row: int) -> None:
        members = tribunals.covenants_of(self.saga, self.tribunal)
        if row >= len(members):
            return
        covenant = members[row]
        summary = covenant.summary.strip() or "Nothing written about it yet."
        self.codex.inspect(
            covenant.name,
            f"{covenant.detail} · {world.votes_text(self.saga, covenant)} votes",
            escape(summary),
        )

    def _show_magus(self, row: int) -> None:
        magus = tribunal_sheet.magi_of_note(self.saga, self.tribunal)[row]
        self.codex.inspect(
            magus.name, magus.detail, cs.statblock_text(self.saga, magus)
        )

    def _show_case(self, cases: Callable[[], list[Case]]) -> Callable[[int], None]:
        def show(row: int) -> None:
            case = cases()[row]
            self.codex.inspect(
                case.title,
                case.kind.title(),
                tribunal_sheet.case_text(self.saga, self.tribunal, case),
            )

        return show

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
            self._grid(
                tribunal_sheet.roster_title(saga, t),
                tribunal_sheet.roster_grid(saga, t),
                ROSTER_SECTION,
                self._show_covenant,
            ),
            self._grid(
                tribunal_sheet.magi_title(saga, t),
                tribunal_sheet.magi_grid(saga, t),
                None,
                self._show_magus,
            ),
        )

    def _docket(self) -> QWidget:
        saga, t = self.saga, self.tribunal
        withdraw: RowVerb = (
            "Withdraw",
            "delete",
            lambda row: tribunal_forms.withdraw_case(t, row),
            lambda _row: True,
        )
        return scrolling_page(
            self.p,
            self._grid(
                tribunal_sheet.cases_title(t),
                tribunal_sheet.cases_grid(saga, t),
                CASES_SECTION,
                self._show_case(lambda: tribunal_sheet.open_cases(t)),
                more=[withdraw],
            ),
            self._grid(
                tribunal_sheet.past_title(t),
                tribunal_sheet.past_grid(t),
                PAST_CASES_SECTION,
                self._show_case(lambda: tribunal_sheet.closed_cases(t)),
            ),
        )

    def _code(self) -> QWidget:
        t = self.tribunal
        return scrolling_page(
            self.p,
            self._grid(
                tribunal_sheet.code_title(t), tribunal_sheet.code_grid(t), CODE_SECTION
            ),
        )

    def _treasury(self) -> QWidget:
        p, t = self.p, self.tribunal
        balance = aligned(
            [(label, escape(words)) for label, words in tribunal_sheet.balance_lines(t)]
        )
        return scrolling_page(
            p,
            section("Balance", p, TextBlock(balance, p)),
            self._grid(
                tribunal_sheet.treasury_title(t),
                tribunal_sheet.treasury_grid(t),
                TREASURY_SECTION,
            ),
        )

    def _diary(self) -> QWidget:
        t = self.tribunal
        return scrolling_page(
            self.p,
            self._grid(
                tribunal_sheet.diary_title(t),
                tribunal_sheet.diary_grid(t),
                TRIB_DIARY_SECTION,
            ),
        )
