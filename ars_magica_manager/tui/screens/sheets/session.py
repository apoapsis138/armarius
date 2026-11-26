"""A Session's own page in the terminal: its top panel names it and its
state, with its facts (sheets/session.py). e edits it; More has Cast at a
Glance and, with the Virtual Tabletop (Preview) on, Begin Session, End
Session and its Chronicle. Its Scenes tab lists the Scenes loaded into it
(a loads one, e changes who is present, its order or its Session, d takes
it out); its Notes tab, its notes."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Collapsible, Static, TabbedContent

from .... import chronicle, scenes, viewing
from ....boon_hook_text import counted
from ....forms import scenes as scene_forms
from ....markup import aligned, escape
from ....models import Saga, Session
from ....sections import (
    SESSION_EVENING_SECTION,
    SESSION_EVENING_TAB,
    SESSION_INFO_SECTION,
    SESSION_SCENES_SECTION,
    SESSION_SCENES_TAB,
)
from ....sheets import session as session_sheet
from ..widgets import (
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TwoColumns,
    fact_markup,
)
from .base import SheetView

_SCENES_LIST = "session-scenes-list"
_SCENES_INFO = "session-scenes-info"
SCENES_TAB = SESSION_SCENES_TAB
NOTES_TAB = "tab-session-notes"


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

    INITIAL_TAB = SCENES_TAB

    def __init__(self, saga: Saga, session: Session) -> None:
        super().__init__(saga)
        self.session = session
        #: The Scenes tab is the storyguide's prep (viewing.STORYGUIDE_ONLY):
        #: a player's page opens on its notes.
        self.scenes_shown = viewing.reads(part=SCENES_TAB)
        if not self.scenes_shown:
            self.INITIAL_TAB = NOTES_TAB

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
            if self.scenes_shown:
                yield self._tab("Scenes", SCENES_TAB, self._scenes_tab)
            yield self._tab(
                session_sheet.EVENING, SESSION_EVENING_TAB, self._evening_tab
            )
            yield self._tab("Notes", NOTES_TAB, self._notes_tab)

    def _evening_tab(self) -> ComposeResult:
        """The account End Session wrote, as whoever is looking may read
        it, each Scene's title over its lines; before then, that it will
        be (End Session refreshes it, so it fills in on this page)."""
        with (
            VerticalScroll(),
            SheetSection(title=session_sheet.EVENING, id=SESSION_EVENING_SECTION),
        ):
            yield self._static(
                SESSION_EVENING_SECTION, self._evening_text, id="session-evening"
            )

    def _evening_text(self) -> str:
        if not session_sheet.shows_evening(self.session):
            return f"[$label]{escape(session_sheet.NOT_YET)}[/]"
        groups = session_sheet.evening_groups(self.saga, self.session, chronicle.here())
        if not groups:
            return f"[$label]{escape(session_sheet.NO_EVENING)}[/]"
        parts: list[str] = []
        for heading, lines in groups:
            said = "\n".join(escape(line) for line in lines)
            parts.append(f"[b]{escape(heading)}[/b]\n{said}" if heading else said)
        return "\n\n".join(parts)

    def _scenes_tab(self) -> ComposeResult:
        """The Scenes loaded into it, in order, over the chosen one in full."""
        saga, session = self.saga, self.session
        with Vertical(classes="panel-body"):
            with (
                VerticalScroll(),
                SheetSection(
                    title=self._titled(
                        SESSION_SCENES_SECTION,
                        SESSION_SCENES_SECTION,
                        lambda: counted("Scenes", len(session.scenes)),
                    ),
                    id=SESSION_SCENES_SECTION,
                ),
            ):
                yield self._list(
                    SESSION_SCENES_SECTION,
                    lambda: (
                        [
                            (i, scenes.use_row(saga, session, u, now))
                            for now in [scene_forms.now_of(saga, session)]
                            for i, u in enumerate(session.scenes)
                        ]
                        or [(None, "[$label]None yet: a loads a Scene.[/]")]
                    ),
                    id=_SCENES_LIST,
                )
            yield self._panel(
                SESSION_SCENES_SECTION,
                lambda: self._use_text(self.section_row(SESSION_SCENES_SECTION)),
                id=_SCENES_INFO,
            )

    def _use_text(self, row: int | None) -> str:
        """The details panel for the use at `row` (None, or one since gone:
        the panel's prompt)."""
        uses = self.session.scenes
        chosen = uses[row] if row is not None and row < len(uses) else None
        now = scene_forms.now_of(self.saga, self.session)
        return scenes.use_detail(self.saga, self.session, chosen, now)

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        if event.selectable_list.id != _SCENES_LIST:
            return
        event.stop()
        self.query_one(f"#{_SCENES_INFO}", Static).update(
            self._use_text(event.data_index)
        )

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
