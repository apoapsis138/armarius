"""A Session's own page on the desktop: its title and state, its facts
(sheets/session.py), and its buttons: Edit, Cast at a Glance, Print the
Cast and, with the Virtual Tabletop (Preview) on, Begin Session, End
Session and its Chronicle, each offered as the Sessions list offers it;
then the Scenes loaded into it (scenes_section.py)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import chronicle, section_verbs, viewing, virtual_tabletop
from ..commands import Command
from ..forms import sessions as session_forms
from ..models import Saga, Session
from ..sections import SESSION_INFO_SECTION, SESSION_SCENES_SECTION
from ..sheets import session as session_sheet
from .conflicts import buttons
from .figures import fact_grid
from .pages import page_header
from .scenes_section import session_scenes_section
from .sessions_section import PRINT, print_cast
from .themes import Palette
from .widgets import scrolling_page

Run = Callable[[Command], None]


class SessionPage(QWidget):
    """One Session's page."""

    def __init__(self, saga: Saga, session: Session, p: Palette, run: Run) -> None:
        super().__init__()
        self.saga, self.session, self.run = saga, session, run
        column = QVBoxLayout(self)
        column.setContentsMargins(18, 12, 12, 8)
        column.setSpacing(8)
        header = page_header(
            session_sheet.title(session), session_sheet.subtitle(session), p, "season"
        )
        parts = [
            header,
            buttons(self._verbs(), p),
            fact_grid(session_sheet.facts(saga, session), p, 2),
        ]
        # Its Scenes are the storyguide's prep (viewing.STORYGUIDE_ONLY).
        if viewing.reads(part=SESSION_SCENES_SECTION):
            parts.append(session_scenes_section(saga, session, p, run))
        column.addWidget(scrolling_page(p, *parts), 1)

    def _verbs(self) -> list[tuple[str, str, Callable[[], None]]]:
        saga, session, run = self.saga, self.session, self.run
        verbs: list[tuple[str, str, Callable[[], None]]] = []
        edit = section_verbs.ops_of(saga, session)[SESSION_INFO_SECTION].edit
        if edit is not None:
            verbs.append(("Edit", "edit", lambda: run(edit(0))))
        verbs.append(
            (
                "Cast at a Glance",
                "players",
                lambda: run(session_forms.cast_glance(saga, session)),
            )
        )
        if session.castings:
            verbs.append(
                ("Print the Cast", PRINT, lambda: run(print_cast(saga, session)))
            )
        if virtual_tabletop.on():
            verbs += self._chronicle_verbs()
        return verbs

    def _chronicle_verbs(self) -> list[tuple[str, str, Callable[[], None]]]:
        saga, session, run, here = self.saga, self.session, self.run, chronicle.here()
        verbs: list[tuple[str, str, Callable[[], None]]] = []
        if (
            viewing.offers("begin_session")
            and chronicle.why_not_begin(saga, session, here) is None
        ):
            verbs.append(
                (
                    "Begin Session",
                    "season",
                    lambda: run(session_forms.begin_session(saga, session)),
                )
            )
        if (
            viewing.offers("close_session")
            and chronicle.why_not_end(session, here, saga) is None
        ):
            verbs.append(
                (
                    "End Session",
                    "season",
                    lambda: run(session_forms.end_session(saga, session)),
                )
            )
        if chronicle.has_chronicle(saga, session):
            verbs.append(
                (
                    "Chronicle",
                    "history",
                    lambda: run(session_forms.read_chronicle(saga, session)),
                )
            )
        return verbs
