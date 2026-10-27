"""The Tribunal sheet: its facts and what it is like in the top panel,
then its tabs: the Roster of its covenants and magi of note, worked out
from the covenants that belong to it, its Docket of cases, its
Peripheral Code, its Treasury and its Diary (tribunal_sheet.py, edited
through tribunal_forms.py)."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, Collapsible, Static, TabbedContent

from .... import meeting, tribunal_packages
from ....forms import tribunal as tribunal_forms
from ....markup import aligned, escape, markdown_text
from ....models import Case, Saga, Tribunal
from ....sections import (
    ATTENDANCE_SECTION,
    BUSINESS_SECTION,
    CASES_SECTION,
    CODE_SECTION,
    PAST_CASES_SECTION,
    ROSTER_SECTION,
    TREASURY_SECTION,
    TRIB_DIARY_SECTION,
    TRIB_MAGI_SECTION,
    TRIBUNAL_INFO_SECTION,
    VOTE_SECTION,
)
from ....sheets import tribunal as tribunal_sheet
from ..widgets import PinnedCollapsible, SelectableList, SheetSection, TwoColumns
from .base import SheetView

#: What each list's rows depend on besides its own section: the top
#: panel's next meeting and sizes, and the cases the others name.
_CASES = (CASES_SECTION, PAST_CASES_SECTION)
#: The meeting's lists: holding a step can change the cases, the
#: roster's proxies, the Diary and the next meeting.
_HALL = (BUSINESS_SECTION, VOTE_SECTION, ATTENDANCE_SECTION)


class TribunalSheetView(SheetView):
    """A Tribunal: the facts under its name, then its tabs."""

    DEFAULT_CSS = """
    TribunalSheetView #trib-top-panel {
        width: 1fr;
        height: auto;
    }
    TribunalSheetView #trib-customs {
        margin-bottom: 1;
    }
    """

    INITIAL_TAB = "tab-trib-roster"

    def __init__(self, saga: Saga, tribunal: Tribunal) -> None:
        super().__init__(saga)
        self.tribunal = tribunal
        self.core_ops = tribunal_forms.tribunal_ops(saga, tribunal)
        #: The customs the sheet was built for: its tabs are theirs.
        self.package = tribunal_packages.of(tribunal)
        #: The case the Docket's details panel shows.
        self._case: Case | None = None
        #: The step of the meeting its details panel shows (None: the
        #: step in hand).
        self._step: int | None = None
        #: Each package tab's chosen row its details panel shows: the
        #: list and the row, by the tab's id.
        self._package_chosen: dict[str, tuple[tribunal_packages.PackageList, int]] = {}

    def compose(self) -> ComposeResult:
        info = (TRIBUNAL_INFO_SECTION, ROSTER_SECTION, *_CASES, *_HALL)
        with (
            Vertical(id="trib-top-panel"),
            PinnedCollapsible(
                title=escape(self.tribunal.name), id=TRIBUNAL_INFO_SECTION
            ),
        ):
            self._on_refresh(TRIBUNAL_INFO_SECTION, self._refresh_title)
            with TwoColumns(id="trib-info-body", text=True):
                yield self._static(info, lambda: self._facts(0), id="trib-info-left")
                yield self._static(info, lambda: self._facts(1), id="trib-info-right")
            yield self._static(
                TRIBUNAL_INFO_SECTION, self._summary_text, id="trib-summary"
            )
            yield Button("Edit (e)", id="btn-trib-edit", compact=True)
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Roster", "tab-trib-roster", self._roster_tab)
            yield self._tab("History", "tab-trib-history", self._history_tab)
            yield self._tab("Docket", "tab-trib-docket", self._docket_tab)
            yield self._tab("Meeting", "tab-trib-meeting", self._meeting_tab)
            yield self._tab("Peripheral Code", "tab-trib-code", self._code_tab)
            yield self._tab("Treasury", "tab-trib-treasury", self._treasury_tab)
            for extra in self.package.tabs:
                yield self._tab(extra.title, extra.tab_id, self._package_tab(extra))
            yield self._tab("Diary", "tab-trib-diary", self._diary_tab)
            yield from self._secrets_tab(self.tribunal)

    def stale(self) -> bool:
        """Whether the Tribunal's customs changed since the sheet was
        built, so its tabs are no longer theirs."""
        return tribunal_packages.of(self.tribunal) is not self.package

    def _package_tab(
        self, extra: tribunal_packages.PackageTab
    ) -> Callable[[], ComposeResult]:
        """A tab the Tribunal's customs add, with each of their lists."""

        saga, t = self.saga, self.tribunal
        watched = (
            ROSTER_SECTION,
            *((extra.text.section_id,) if extra.text is not None else ()),
            *(e.section_id for e in extra.lists),
        )

        def sections() -> ComposeResult:
            if extra.text is not None:
                words = extra.text
                with SheetSection(title=escape(words.title), id=words.section_id):
                    yield self._static(
                        watched,
                        lambda: self._package_words(words),
                        id=f"{words.section_id.removeprefix('section-')}-text",
                    )
            for entry in extra.lists:
                yield from self._grid_section(
                    entry.section_id,
                    watched,
                    lambda entry=entry: entry.section_title(saga, t),
                    lambda entry=entry: entry.grid(saga, t).lines(),
                    f"{entry.section_id.removeprefix('section-')}-list",
                )

        def build() -> ComposeResult:
            if not extra.panel_id:
                yield from sections()
                return
            with Vertical(classes="panel-body"):
                with VerticalScroll():
                    yield from sections()
                yield self._panel(
                    watched, lambda: self._package_info(extra), id=extra.panel_id
                )

        return build

    def _package_words(self, words: tribunal_packages.PackageText) -> str:
        """A package tab's section of words: its facts on a line, then what
        it says."""
        facts = words.facts(self.saga, self.tribunal)
        line = "  ·  ".join(f"[$label]{escape(k)}:[/] {escape(v)}" for k, v in facts)
        said = words.text(self.saga, self.tribunal)
        return f"{line}\n\n{said}" if line else said

    def _package_info(self, extra: tribunal_packages.PackageTab) -> str:
        """The package tab's details panel: the row chosen in one of its
        lists, or what to choose."""
        chosen = self._package_chosen.get(extra.tab_id)
        if chosen is not None:
            entry, row = chosen
            if entry.info is not None and (
                text := entry.info(self.saga, self.tribunal, row)
            ):
                return text
        return extra.panel_empty

    def _refresh_title(self) -> None:
        panel = self.query_one(f"#{TRIBUNAL_INFO_SECTION}", Collapsible)
        panel.title = escape(self.tribunal.name)

    def _facts(self, column: int) -> str:
        facts = tribunal_sheet.facts(self.saga, self.tribunal)
        half = (len(facts) + 1) // 2
        shown = facts[:half] if column == 0 else facts[half:]
        return aligned([(f.label, escape(f.value)) for f in shown])

    def _summary_text(self) -> str:
        lede, rest = tribunal_sheet.summary_parts(self.tribunal)
        if not lede:
            return "[$label]In the Saga: not written yet. Edit the Tribunal to say.[/]"
        more = f"\n[$label]{tribunal_sheet.MORE_UNDER_HISTORY}[/]" if rest else ""
        return markdown_text(lede) + more

    def _grid_section(
        self,
        section: str,
        sections: tuple[str, ...],
        title: Callable[[], str],
        rows: Callable[[], Sequence[tuple[int | None, str]]],
        list_id: str,
    ) -> ComposeResult:
        """A section titled `title()` listing `rows()`, both redrawn when
        `section` or any of `sections` refreshes."""
        watched = (section, *sections)
        with SheetSection(title=self._titled(watched, section, title), id=section):
            yield self._list(watched, rows, id=list_id)

    def _roster_tab(self) -> ComposeResult:
        saga, t = self.saga, self.tribunal
        yield from self._grid_section(
            ROSTER_SECTION,
            (
                TRIBUNAL_INFO_SECTION,
                *_HALL,
                *(e.section_id for e in self.package.lists),
            ),
            lambda: tribunal_sheet.roster_title(saga, t),
            lambda: tribunal_sheet.roster_grid(saga, t).lines(),
            "trib-roster",
        )
        yield from self._grid_section(
            TRIB_MAGI_SECTION,
            (TRIBUNAL_INFO_SECTION, *_CASES),
            lambda: tribunal_sheet.magi_title(saga, t),
            lambda: tribunal_sheet.magi_grid(saga, t).lines(),
            "trib-magi",
        )

    def _docket_tab(self) -> ComposeResult:
        """The cases for the next meeting and those past, and (docked
        below the scrolling part) the details panel of the chosen case."""
        saga, t = self.saga, self.tribunal
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield from self._grid_section(
                    CASES_SECTION,
                    (TRIBUNAL_INFO_SECTION, PAST_CASES_SECTION, *_HALL),
                    lambda: tribunal_sheet.cases_title(t),
                    lambda: tribunal_sheet.cases_grid(saga, t).lines(),
                    "trib-cases",
                )
                yield from self._grid_section(
                    PAST_CASES_SECTION,
                    (CASES_SECTION, *_HALL),
                    lambda: tribunal_sheet.past_title(t),
                    lambda: tribunal_sheet.past_grid(t).lines(),
                    "trib-past",
                )
            yield self._panel(
                (TRIBUNAL_INFO_SECTION, *_CASES), self._case_text, id="trib-case-info"
            )

    def _case_text(self) -> str:
        if self._case is not None and self._case not in self.tribunal.cases:
            self._case = None
        return tribunal_sheet.case_text(self.saga, self.tribunal, self._case)

    def _meeting_tab(self) -> ComposeResult:
        """The meeting being held (or the next): where and what is in
        hand, its order of business by day and who is in the hall, and
        (docked below) the details panel of the chosen step."""
        saga, t = self.saga, self.tribunal
        watched = (TRIBUNAL_INFO_SECTION, *_CASES, *_HALL)
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield self._static(watched, self._meeting_facts, id="meeting-facts")
                yield from self._grid_section(
                    BUSINESS_SECTION,
                    (TRIBUNAL_INFO_SECTION, *_CASES, VOTE_SECTION, ATTENDANCE_SECTION),
                    lambda: meeting.business_title(saga, t),
                    lambda: meeting.business_grid(saga, t).lines(),
                    "meeting-business",
                )
                watched_vote = (TRIBUNAL_INFO_SECTION, *_CASES, *_HALL)
                with SheetSection(
                    title=self._titled(
                        watched_vote,
                        VOTE_SECTION,
                        lambda: meeting.vote_title(saga, t),
                    ),
                    id=VOTE_SECTION,
                ):
                    yield self._list(
                        watched_vote,
                        lambda: meeting.vote_grid(saga, t).lines(),
                        id="meeting-vote",
                    )
                    yield self._static(
                        watched_vote, self._tally_text, id="meeting-tally"
                    )
                yield from self._grid_section(
                    ATTENDANCE_SECTION,
                    (TRIBUNAL_INFO_SECTION, *_CASES, BUSINESS_SECTION, VOTE_SECTION),
                    lambda: meeting.attendance_title(saga, t),
                    lambda: meeting.attendance_grid(saga, t).lines(),
                    "meeting-attendance",
                )
            yield self._panel(watched, self._step_text, id="meeting-step-info")

    def _meeting_facts(self) -> str:
        facts = meeting.facts(self.saga, self.tribunal)
        heading = escape(meeting.title(self.saga, self.tribunal))
        return f"[b]{heading}[/]\n" + aligned(
            [(f.label, escape(f.value)) for f in facts]
        )

    def _tally_text(self) -> str:
        """The tally as a bar: for in green, undecided, against in red."""
        case = meeting.vote_case(self.saga, self.tribunal)
        if case is None:
            return ""
        record = meeting.record(self.saga, self.tribunal)
        yes, no, abstain = meeting.tally(self.saga, self.tribunal, record, case)
        bar = meeting.tally_bar((yes, no, abstain))
        split = bar.count("█"), bar.count("░"), bar.count("▓")
        drawn = (
            f"[$success]{'█' * split[0]}[/][$label]{'░' * split[1]}[/]"
            f"[$error]{'█' * split[2]}[/]"
        )
        return f"  [b]For {yes}[/] {drawn} [b]Against {no}[/]  {abstain} undecided"

    def _step_text(self) -> str:
        return meeting.step_text(self.saga, self.tribunal, self._step)

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A case or a step of the meeting was chosen: show it in its
        tab's details panel."""
        list_id = event.selectable_list.id or ""
        for extra in self.package.tabs:
            for entry in extra.lists:
                if not extra.panel_id or entry.info is None:
                    continue
                if list_id == f"{entry.section_id.removeprefix('section-')}-list":
                    event.stop()
                    self._package_chosen[extra.tab_id] = (entry, event.data_index)
                    self.query_one(f"#{extra.panel_id}", Static).update(
                        self._package_info(extra)
                    )
                    return
        if list_id == "meeting-business":
            event.stop()
            self._step = event.data_index
            self.query_one("#meeting-step-info", Static).update(self._step_text())
            return
        if list_id not in ("trib-cases", "trib-past"):
            return
        event.stop()
        cases = (
            tribunal_sheet.open_cases(self.tribunal)
            if list_id == "trib-cases"
            else tribunal_sheet.closed_cases(self.tribunal)
        )
        index = event.data_index
        self._case = cases[index] if index < len(cases) else None
        self.query_one("#trib-case-info", Static).update(self._case_text())

    def _code_tab(self) -> ComposeResult:
        t = self.tribunal
        if tribunal_sheet.customs_note(t):
            yield self._static(
                TRIBUNAL_INFO_SECTION,
                lambda: escape(tribunal_sheet.customs_note(t)),
                id="trib-customs",
            )
        yield from self._grid_section(
            CODE_SECTION,
            _CASES,
            lambda: tribunal_sheet.code_title(t),
            lambda: tribunal_sheet.code_grid(t).lines(),
            "trib-code",
        )

    def _balance_text(self) -> str:
        return aligned(
            [
                (label, escape(words))
                for label, words in tribunal_sheet.balance_lines(self.tribunal)
            ]
        )

    def _treasury_tab(self) -> ComposeResult:
        t = self.tribunal
        yield self._static(TREASURY_SECTION, self._balance_text, id="trib-balance")
        yield from self._grid_section(
            TREASURY_SECTION,
            _CASES,
            lambda: tribunal_sheet.treasury_title(t),
            lambda: tribunal_sheet.treasury_grid(t).lines(),
            "trib-treasury",
        )

    def _history_tab(self) -> ComposeResult:
        with VerticalScroll():
            yield self._static(
                TRIBUNAL_INFO_SECTION, self._history_text, id="trib-history"
            )

    def _history_text(self) -> str:
        _lede, rest = tribunal_sheet.summary_parts(self.tribunal)
        history = self.tribunal.history.strip()
        told = (
            markdown_text(history)
            if history
            else "[$label]History: not written yet. Edit the Tribunal (e) to tell it.[/]"
        )
        if not rest:
            return told
        return (
            f"[$label]In the Saga, continued[/]\n{markdown_text(rest)}"
            f"\n\n[$label]History[/]\n{told}"
        )

    def _diary_tab(self) -> ComposeResult:
        t = self.tribunal
        yield from self._grid_section(
            TRIB_DIARY_SECTION,
            _HALL,
            lambda: tribunal_sheet.diary_title(t),
            lambda: tribunal_sheet.diary_grid(t).lines(),
            "trib-diary",
        )
