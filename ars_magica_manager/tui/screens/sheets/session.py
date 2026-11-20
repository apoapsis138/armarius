"""A Session's own page in the terminal: its top panel names it and its
state, with its facts (sheets/session.py). e edits it; More has Cast at a
Glance and, with the Virtual Tabletop (Preview) on, Begin Session, End
Session and its Chronicle. The Session's Scenes and the evening's account
come under it."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Collapsible, TabbedContent

from ....markup import aligned, escape
from ....models import Saga, Session
from ....sections import SESSION_INFO_SECTION
from ....sheets import session as session_sheet
from ..widgets import PinnedCollapsible, TwoColumns, fact_markup
from .base import SheetView


def _title(session: Session) -> str:
    return (
        f"{escape(session_sheet.title(session))}  "
        f"[$label]{escape(session_sheet.subtitle(session))}[/]"
    )


class SessionSheetView(SheetView):
    """One Session: its top panel, with its facts in two columns."""

    DEFAULT_CSS = """
    SessionSheetView #session-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-session-notes"

    def __init__(self, saga: Saga, session: Session) -> None:
        super().__init__(saga)
        self.session = session

    def compose(self) -> ComposeResult:
        with (
            Vertical(id="session-top-panel"),
            PinnedCollapsible(title=_title(self.session), id=SESSION_INFO_SECTION),
        ):
            self._on_refresh(SESSION_INFO_SECTION, self._refresh_title)
            with TwoColumns(id="session-info-body", text=True):
                yield self._static(
                    SESSION_INFO_SECTION,
                    lambda: self._facts(0),
                    id="session-info-left",
                )
                yield self._static(
                    SESSION_INFO_SECTION,
                    lambda: self._facts(1),
                    id="session-info-right",
                )

        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Notes", self.INITIAL_TAB, self._notes_tab)

    def _notes_tab(self) -> ComposeResult:
        with VerticalScroll():
            yield self._static(
                SESSION_INFO_SECTION, self._notes_text, id="session-notes-content"
            )

    def _notes_text(self) -> str:
        notes = self.session.notes.strip()
        return (
            escape(notes)
            if notes
            else "[$label]No notes yet. e edits the Session to add some.[/]"
        )

    def _refresh_title(self) -> None:
        panel = self.query_one(f"#{SESSION_INFO_SECTION}", Collapsible)
        panel.title = _title(self.session)

    def _facts(self, column: int) -> str:
        """The facts but the notes, which have a tab of their own."""
        facts = [
            f
            for f in session_sheet.facts(self.saga, self.session)
            if f.label != "Notes"
        ]
        half = (len(facts) + 1) // 2
        shown = facts[:half] if column == 0 else facts[half:]
        return aligned([(f.label, fact_markup(f)) for f in shown])
