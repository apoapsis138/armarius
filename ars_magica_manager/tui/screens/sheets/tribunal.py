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

from .... import tribunal_forms, tribunal_packages, tribunal_sheet
from ....markup import aligned, escape, markdown_inline
from ....models import Case, Saga, Tribunal
from ....sections import (
    CASES_SECTION,
    CODE_SECTION,
    PAST_CASES_SECTION,
    ROSTER_SECTION,
    TREASURY_SECTION,
    TRIB_DIARY_SECTION,
    TRIB_MAGI_SECTION,
    TRIBUNAL_INFO_SECTION,
)
from ..widgets import PinnedCollapsible, SelectableList, SheetSection, TwoColumns
from .base import SheetView

#: What each list's rows depend on besides its own section: the top
#: panel's next meeting and sizes, and the cases the others name.
_CASES = (CASES_SECTION, PAST_CASES_SECTION)


class TribunalSheetView(SheetView):
    """A Tribunal: the facts under its name, then its tabs."""

    DEFAULT_CSS = """
    TribunalSheetView #trib-top-panel {
        width: 1fr;
        height: auto;
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

    def compose(self) -> ComposeResult:
        info = (TRIBUNAL_INFO_SECTION, ROSTER_SECTION, *_CASES)
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
            yield self._tab("Docket", "tab-trib-docket", self._docket_tab)
            yield self._tab("Peripheral Code", "tab-trib-code", self._code_tab)
            yield self._tab("Treasury", "tab-trib-treasury", self._treasury_tab)
            for extra in self.package.lists:
                yield self._tab(extra.title, extra.tab_id, self._package_tab(extra))
            yield self._tab("Diary", "tab-trib-diary", self._diary_tab)

    def stale(self) -> bool:
        """Whether the Tribunal's customs changed since the sheet was
        built, so its tabs are no longer theirs."""
        return tribunal_packages.of(self.tribunal) is not self.package

    def _package_tab(
        self, extra: tribunal_packages.PackageList
    ) -> Callable[[], ComposeResult]:
        def build() -> ComposeResult:
            saga, t = self.saga, self.tribunal
            yield from self._grid_section(
                extra.section_id,
                (ROSTER_SECTION,),
                lambda: extra.section_title(saga, t),
                lambda: extra.grid(saga, t).lines(),
                f"{extra.section_id.removeprefix('section-')}-list",
            )

        return build

    def _refresh_title(self) -> None:
        panel = self.query_one(f"#{TRIBUNAL_INFO_SECTION}", Collapsible)
        panel.title = escape(self.tribunal.name)

    def _facts(self, column: int) -> str:
        facts = tribunal_sheet.facts(self.saga, self.tribunal)
        half = (len(facts) + 1) // 2
        shown = facts[:half] if column == 0 else facts[half:]
        return aligned([(f.label, escape(f.value)) for f in shown])

    def _summary_text(self) -> str:
        summary = self.tribunal.summary.strip()
        if not summary:
            return "[$label]In the Saga: not written yet. Edit the Tribunal to say.[/]"
        return markdown_inline(summary)

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
            (TRIBUNAL_INFO_SECTION, *(e.section_id for e in self.package.lists)),
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
                    (TRIBUNAL_INFO_SECTION, PAST_CASES_SECTION),
                    lambda: tribunal_sheet.cases_title(t),
                    lambda: tribunal_sheet.cases_grid(saga, t).lines(),
                    "trib-cases",
                )
                yield from self._grid_section(
                    PAST_CASES_SECTION,
                    (CASES_SECTION,),
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

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A case was chosen: show it in the Docket's details panel."""
        list_id = event.selectable_list.id or ""
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

    def _diary_tab(self) -> ComposeResult:
        t = self.tribunal
        yield from self._grid_section(
            TRIB_DIARY_SECTION,
            (),
            lambda: tribunal_sheet.diary_title(t),
            lambda: tribunal_sheet.diary_grid(t).lines(),
            "trib-diary",
        )
