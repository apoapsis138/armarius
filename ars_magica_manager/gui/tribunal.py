"""The desktop Tribunal page in the Codex layout: a header with its name,
when it next meets and its facts, over its chapters: the Roster of its
covenants and magi of note, worked out from the covenants that belong to
it, its Docket of cases, the Meeting being held, its Peripheral Code,
its Treasury, its Diary, and Manage.

What it says comes from the shared core (sheets/tribunal.py), as the
terminal's Tribunal sheet does, and its buttons run the core's forms
(forms/tribunal.py)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import acta, artwork, hall, meeting, tribunal_packages, tribunals, world
from ..commands import Command, Form, Refuse, SectionOps, Then
from ..forms import tribunal as tribunal_forms
from ..markup import aligned, escape, markdown_text
from ..models import Case, Saga, Tribunal, TribunalDiaryEntry
from ..sections import (
    ATTENDANCE_SECTION,
    BUSINESS_SECTION,
    CASES_SECTION,
    CODE_SECTION,
    PAST_CASES_SECTION,
    ROSTER_SECTION,
    TREASURY_SECTION,
    TRIB_DIARY_SECTION,
    VOTE_SECTION,
)
from ..sheets import character as cs
from ..sheets import tribunal as tribunal_sheet
from ..sheets.tribunal import Grid
from ..tribunal_packages.rhine import gild_tree
from . import marks, print_sheet
from .bookmark import with_bookmark
from .character_sheet import TextBlock, secrets_chapter, section
from .editing import Chooser, RowVerb, Run, verb_buttons
from .figures import fact_grid, prose
from .hall import GrandHall, OpeningCard
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
        outer.addWidget(
            with_bookmark(self._header(), controls.bookmark(p) if controls else None)
        )
        self.codex = Codex(p)
        self.ops = tribunal_forms.tribunal_ops(saga, tribunal)
        self.ops[BUSINESS_SECTION] = self._with_opening_card(self.ops[BUSINESS_SECTION])
        self.codex.add("Roster", "tribunal", self._roster())
        self.codex.add("History", "year", self._history())
        self.codex.add("Docket", "worksheet", self._docket())
        self.codex.add("Meeting", "tribunal", self._meeting())
        self.codex.add("Peripheral Code", "lab_text", self._code())
        self.codex.add("Treasury", "income", self._treasury())
        for extra in tribunal_packages.of(tribunal).tabs:
            self.codex.add(
                extra.title,
                "tribunal",
                scrolling_page(
                    p,
                    *(
                        self._grid(
                            entry.section_title(saga, tribunal),
                            entry.grid(saga, tribunal),
                            entry.section_id,
                        )
                        for entry in extra.lists
                    ),
                ),
            )
        self.codex.add("Diary", "year", self._diary())
        self.codex.add("Secrets", "secrets", secrets_chapter(tribunal, p, run))
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
            elif text := grid.row_text(row):
                # A list with no inspector of its own shows its row in full,
                # a gild with its symbol.
                name = grid.rows[grid.keys.index(row)][0]
                tree = gild_tree(name) if grid.columns[0] == "Gild" else None
                symbol = marks.gild_pixmap(tree, p["heading"], 96) if tree else None
                self.codex.inspect(name, title, text, symbol)

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
            markdown_text(summary),
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

    def _show_ruling(self, row: int) -> None:
        rulings = self.tribunal.rulings
        if row >= len(rulings):
            return
        ruling = rulings[row]
        self.codex.inspect(
            ruling.title,
            "Peripheral Code",
            tribunal_sheet.ruling_text(self.tribunal, ruling),
        )

    def _show_diary_entry(self, row: int) -> None:
        diary = self.tribunal.diary
        if row >= len(diary):
            return
        entry = diary[row]
        self.codex.inspect(
            entry.title,
            world.when_text(entry.year, entry.season),
            tribunal_sheet.diary_text(entry),
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
        lede, rest = tribunal_sheet.summary_parts(t)
        said = (
            [prose(lede, p)]
            if lede
            else [_none("Not written yet: edit the Tribunal to say.", p)]
        )
        if rest:
            said.append(_none(tribunal_sheet.MORE_UNDER_HISTORY, p))
        return scrolling_page(
            p,
            section("In the Saga", p, *said, edits={"Edit Tribunal": self._edit}),
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

    def _history(self) -> QWidget:
        p, history = self.p, self.tribunal.history.strip()
        _lede, rest = tribunal_sheet.summary_parts(self.tribunal)
        continued = (
            [section("In the Saga, continued", p, prose(rest, p, initial=False))]
            if rest
            else []
        )
        return scrolling_page(
            p,
            *continued,
            section(
                "History",
                p,
                prose(history, p)
                if history
                else _none("Not written yet: edit the Tribunal to tell it.", p),
                edits={"Edit Tribunal": self._edit},
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

    def _show_step(self, row: int) -> None:
        self.codex.inspect(
            meeting.title(self.saga, self.tribunal),
            "",
            meeting.step_text(self.saga, self.tribunal, row),
        )

    def _meeting(self) -> QWidget:
        """The meeting being held (or the next): where and what is in
        hand, its order of business by day, and who is in the hall."""
        p, saga, t = self.p, self.saga, self.tribunal
        facts = aligned([(f.label, escape(f.value)) for f in meeting.facts(saga, t)])
        chooser = Chooser()

        def choose(row: int) -> None:
            chooser.choose(row)
            self._show_step(row)

        business = section(
            meeting.business_title(saga, t),
            p,
            table_view(meeting.business_grid(saga, t).table(), p, choose),
            buttons=verb_buttons(
                self.ops[BUSINESS_SECTION],
                chooser,
                self.run,
                p,
                nouns=("Add", "Hold", "Abandon"),
            ),
        )
        case = meeting.vote_case(saga, t)
        grand = GrandHall(saga, t, case, p)
        the_hall = section(
            "The Hall",
            p,
            grand,
            edits={"Call the Vote": grand.call_the_vote} if case is not None else None,
        )
        return scrolling_page(
            p,
            section(meeting.title(saga, t), p, TextBlock(facts, p)),
            the_hall,
            business,
            self._grid(
                meeting.vote_title(saga, t),
                meeting.vote_grid(saga, t, tally_row=True),
                VOTE_SECTION,
            ),
            self._grid(
                meeting.attendance_title(saga, t),
                meeting.attendance_grid(saga, t),
                ATTENDANCE_SECTION,
            ),
        )

    def _with_opening_card(self, ops: SectionOps) -> SectionOps:
        """Hold, when it opens the meeting, plays the opening card over the
        window once the roll call is saved; the next step opens when the
        card is closed."""
        hold, saga, t, p, run = ops.edit, self.saga, self.tribunal, self.p, self.run
        if hold is None:
            return ops

        def play(window: QWidget, following: Command | None) -> None:
            if t.meeting is not None:
                then = (lambda: run(following)) if following is not None else None
                OpeningCard(window, hall.opening_card(saga, t), p, then).play()

        def edit(row: int) -> Command:
            step = hold(row)
            if t.meeting is not None or not isinstance(step, Form):
                return step
            window = self.window()

            def apply(values: dict[str, Any]) -> Any:
                ended = step.apply(values)
                # The step that follows the roll call opens once the card
                # is closed, not under it.
                following = ended.step if isinstance(ended, Then) else None
                QTimer.singleShot(0, lambda: play(window, following))
                return None if following is not None else ended

            return replace(step, apply=apply)

        return replace(ops, edit=edit)

    def _code(self) -> QWidget:
        p, t = self.p, self.tribunal
        note = tribunal_sheet.customs_note(t)
        customs = [section("Customs", p, TextBlock(escape(note), p))] if note else []
        return scrolling_page(
            p,
            *customs,
            self._grid(
                tribunal_sheet.code_title(t),
                tribunal_sheet.code_grid(t),
                CODE_SECTION,
                self._show_ruling,
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

        def entry(row: int) -> TribunalDiaryEntry | None:
            # The table gives the chosen row's key: its place in the Diary.
            return t.diary[row] if row < len(t.diary) else None

        def print_acta(row: int) -> Command:
            found = entry(row)
            if found is None:
                return Refuse("Print", "Choose an Acta to print.")
            return acta.print_entry(
                t,
                tribunals.title(t),
                found,
                lambda doc, path: print_sheet.print_document(doc, path),
            )

        def is_acta(row: int) -> bool:
            found = entry(row)
            return found is not None and acta.is_acta(found.title)

        printing: RowVerb = ("Print", "export", print_acta, is_acta)
        return scrolling_page(
            self.p,
            self._grid(
                tribunal_sheet.diary_title(t),
                tribunal_sheet.diary_grid(t),
                TRIB_DIARY_SECTION,
                self._show_diary_entry,
                more=[printing],
            ),
        )
