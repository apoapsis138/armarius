"""The Tribunal sheet: its facts and what it is like in the top panel,
then its roster of covenants, worked out from the covenants that belong
to it (tribunal_sheet.py)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Collapsible, TabbedContent

from .... import tribunal_forms, tribunal_sheet
from ....commands import SectionOps
from ....markup import aligned, escape, markdown_inline
from ....models import Saga, Tribunal
from ....sections import ROSTER_SECTION, TRIBUNAL_INFO_SECTION
from ..widgets import PinnedCollapsible, SheetSection, TwoColumns
from .base import SheetView


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
        self.core_ops = {
            TRIBUNAL_INFO_SECTION: SectionOps(
                edit=lambda _row: tribunal_forms.edit_tribunal_form(saga, tribunal)
            )
        }

    def compose(self) -> ComposeResult:
        with (
            Vertical(id="trib-top-panel"),
            PinnedCollapsible(
                title=escape(self.tribunal.name), id=TRIBUNAL_INFO_SECTION
            ),
        ):
            self._on_refresh(TRIBUNAL_INFO_SECTION, self._refresh_title)
            with TwoColumns(id="trib-info-body", text=True):
                yield self._static(
                    TRIBUNAL_INFO_SECTION,
                    lambda: self._facts(0),
                    id="trib-info-left",
                )
                yield self._static(
                    TRIBUNAL_INFO_SECTION,
                    lambda: self._facts(1),
                    id="trib-info-right",
                )
            yield self._static(
                TRIBUNAL_INFO_SECTION, self._summary_text, id="trib-summary"
            )
            yield Button("Edit (e)", id="btn-trib-edit", compact=True)
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Roster", "tab-trib-roster", self._roster_tab)

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

    def _roster_text(self) -> str:
        lines = tribunal_sheet.roster_lines(self.saga, self.tribunal)
        if not lines:
            return (
                "[dim]No covenant belongs to it yet: choose it as a covenant's "
                "Tribunal in Edit Covenant.[/]"
            )
        return "\n".join(lines)

    def _roster_tab(self) -> ComposeResult:
        with SheetSection(title="Roster", id=ROSTER_SECTION):
            yield self._static(
                (ROSTER_SECTION, TRIBUNAL_INFO_SECTION),
                self._roster_text,
                id="trib-roster",
            )
