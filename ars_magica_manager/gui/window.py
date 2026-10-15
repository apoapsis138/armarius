"""The desktop main window: one page at a time, the way a book is read,
with a trail across the top back to the pages above it (Sagas, the saga,
the covenant, the character, their familiar) and a printer's headpiece
over every page.

The pages are the shelf of sagas, a saga's covenants, a covenant (its
people, laboratories and seasons), a laboratory, a character's sheet and a
familiar's. Where the
reader is is a list of places, the trail; the page shown is built from
the last one, so changing the theme just builds it again.

A sheet's Edit buttons open the same forms the terminal shows
(character_forms.py); saving one saves the saga, merged with whatever the
terminal app (or the hosted copies players use) saved meanwhile, so the
two are safe to run side by side.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import shiboken6
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QShowEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .. import (
    advance_forms,
    creation_forms,
    help_text,
    menu_forms,
    paths,
    print_forms,
    saga_forms,
    storage,
    title_page,
)
from .. import familiars as fam
from .. import laboratory_sheet as ls
from .. import print_layout as pl
from ..actions import NodeKind
from ..commands import Act, Choose, ChooseFile, Command, Confirm, Form, Picked, Refuse
from ..markup import escape
from ..models import Character, Covenant, Familiar, Laboratory, Saga
from . import pictures, print_sheet, printing, snapping
from .character_sheet import CharacterSheet
from .covenant import CovenantPage
from .editing import InPlace, place_for
from .familiar import FamiliarPage
from .forms import ConfirmDialog, NoticeDialog, answer, run_steps, step_dialog
from .frame import MAXIMISE, DragStrip, Grips, TopStrip, WindowButtons
from .help import HelpPage
from .laboratory import LaboratoryPage
from .manage import Moded, RecordControls, fade_from
from .markup_html import plain
from .menus import Placer
from .ornaments import Headpiece
from .pages import SagaPage, SagaShelf
from .paper import Paper
from .region import NeighbourPage
from .saga_content import SagaContentPage
from .seasons import SeasonsPage
from .themes import PALETTES, Palette, for_mode, style_sheet
from .title import TitleScreen
from .tribunal import TribunalPage
from .widgets import take_pressed
from .worksheet import WorksheetPage

(
    SHELF,
    SAGA,
    COVENANT,
    CHARACTER,
    LABORATORY,
    FAMILIAR,
    CONTENT,
    WORKSHEET,
    SEASONS,
    HELP,
    TRIBUNAL,
    NEIGHBOUR,
) = (
    "shelf",
    "saga",
    "covenant",
    "character",
    "laboratory",
    "familiar",
    "content",
    "worksheet",
    "seasons",
    "help",
    "tribunal",
    "neighbour",
)

#: Each page's help topic (help_text: a page's id), most specific first.
_HELP_IDS = {
    SHELF: ["saga-picker"],
    SAGA: ["saga", "workspace"],
    COVENANT: ["covenant"],
    CHARACTER: ["character"],
    LABORATORY: ["laboratory"],
    FAMILIAR: ["familiar"],
    CONTENT: ["saga-content"],
    WORKSHEET: ["creation-worksheet"],
    SEASONS: ["seasons", "advance-season", "season-summary"],
    TRIBUNAL: ["tribunal"],
    NEIGHBOUR: ["neighbour"],
}

#: The prefix of each page's tab topics; a character's are the plain
#: "tab-" ones.
_TAB_PREFIX = {
    COVENANT: "tab-cov-",
    LABORATORY: "tab-lab-",
    FAMILIAR: "tab-fam-",
    CONTENT: "tab-content-",
    TRIBUNAL: "tab-trib-",
    NEIGHBOUR: "tab-nb-",
    CHARACTER: "tab-",
}
_OTHER_TABS = tuple(v for k, v in _TAB_PREFIX.items() if k != CHARACTER)

#: The chapters whose help is a tab named otherwise, by page and the
#: chapter's name (folded): the terminal's tabs are cut differently.
_CHAPTER_TABS = {
    (COVENANT, "sketch"): "tab-cov-overview",
    (COVENANT, "charter"): "tab-cov-attributes",
    (COVENANT, "people"): "tab-cov-inhabitants",
    (COVENANT, "covenfolk"): "tab-cov-inhabitants",
    (COVENANT, "treasury"): "tab-cov-economics",
    (LABORATORY, "specializations"): "tab-lab-attributes",
    (LABORATORY, "stores"): "tab-lab-inventory",
    (LABORATORY, "seasons"): "tab-lab-planning",
}


def _first_input(dialog: QDialog) -> QWidget | None:
    """The widget a step's typing starts in: a form's first field, a
    list's search, a question's Cancel."""
    inputs = getattr(dialog, "inputs", None)
    if inputs:
        return next(iter(inputs.values()))
    return getattr(dialog, "search", None) or getattr(dialog, "cancel", None)


def _title(command: Command) -> str:
    if isinstance(command, Confirm):
        return command.title or command.question
    return "" if isinstance(command, Act) else command.title


@dataclass(frozen=True)
class Place:
    """A page the reader has opened: what kind, and whose (a covenant's or
    a character's id; None for the saga's unassigned characters)."""

    kind: str
    id: str | None = None


class MainWindow(QMainWindow):
    def __init__(self, saga_ids: list[str] | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Armarius")
        self.setWindowIcon(pictures.app_icon())
        # The window draws its own title bar (frame.py).
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.palette_index = 0
        #: The palette pages are built in while one is printed.
        self._printing: Palette | None = None
        #: The palette the window is drawn in now.
        self._applied = PALETTES[0]
        self.saga_ids = storage.list_sagas() if saga_ids is None else saga_ids
        self.saga: Saga | None = None
        self.trail: list[Place] = []
        #: Shows a step and waits for it (in place; a test answers it).
        self.ask: Callable[[QDialog], int] = self._present
        #: Where the running button's steps open (editing.place_for), and
        #: the step open there now.
        self._place: InPlace | None = None
        self._open: QDialog | None = None
        self._help_from: QWidget | None = None
        #: The season just advanced, for the Seasons page to show first.
        self._played: advance_forms.Played | None = None

        bar = self._top_bar()

        self.sheet_area = QWidget()
        self.sheet_layout = QVBoxLayout(self.sheet_area)
        self.sheet_layout.setContentsMargins(0, 0, 0, 0)

        body = Paper(self.palette_)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(bar)
        self.headpiece = Headpiece(self.palette_)
        layout.addWidget(self.headpiece)
        layout.addWidget(self.sheet_area, 1)
        #: The pages, and over them the title page while it is on show.
        self.stack = QStackedWidget()
        self.stack.addWidget(body)
        self.setCentralWidget(self.stack)
        self.title: TitleScreen | None = None
        self.grips = Grips(self)

        self._apply_theme()
        if len(self.saga_ids) == 1:
            self.open_saga(self.saga_ids[0])
        else:
            self.go([Place(SHELF)])

    def _top_bar(self) -> QHBoxLayout:
        """The window's title bar: the trail on the left, the app's name
        in the middle (drag it to move the window), and Advance Season,
        Help, the theme and the window's own buttons on the right."""
        self.crumbs = QHBoxLayout()
        self.crumbs.setSpacing(2)
        self.theme = QPushButton()
        self.theme.setFlat(True)
        self.theme.clicked.connect(self.toggle_theme)
        bar = QHBoxLayout()
        bar.setContentsMargins(12, 4, 8, 0)
        bar.addLayout(self.crumbs)
        self.drag = DragStrip(self, self.palette_, "Armarius")
        bar.addWidget(self.drag, 1)
        #: Advance Season, while a saga is open: its date, and a click
        #: plays the season out (advance_forms).
        self.advance = QPushButton()
        self.advance.setObjectName("edit")
        self.advance.setFlat(True)
        self.advance.clicked.connect(self.advance_season)
        bar.addWidget(self.advance)
        self.help = QPushButton("  Help")
        self.help.setFlat(True)
        self.help.setToolTip("Help on this page (F1)")
        self.help.clicked.connect(self.open_help)
        bar.addWidget(self.help)
        QShortcut(QKeySequence(Qt.Key.Key_F1), self, self.open_help)
        bar.addWidget(self.theme)
        bar.addSpacing(10)
        self.controls = WindowButtons(self, self.palette_)
        bar.addWidget(self.controls, 0, Qt.AlignmentFlag.AlignTop)
        return bar

    def showEvent(self, event: QShowEvent) -> None:
        snapping.make_snappable(self)
        super().showEvent(event)

    def nativeEvent(self, eventType, message) -> tuple[bool, int]:
        """Windows Snap for the drawn title bar (snapping.py)."""
        result = snapping.native_event(self, bytes(eventType), int(message))
        if result is not None:
            return True, result
        return super().nativeEvent(eventType, message)  # pyright: ignore[reportReturnType]

    def changeEvent(self, event: QEvent) -> None:
        """Maximise turns to restore (and back) as the window does."""
        if event.type() == QEvent.Type.WindowStateChange:
            snapping.make_snappable(self)
            self.controls.update()
            self.controls.buttons[MAXIMISE].update()
            self.controls.buttons[MAXIMISE].setToolTip(
                "Restore" if self.isMaximized() else "Maximise"
            )
        super().changeEvent(event)

    @property
    def palette_(self) -> Palette:
        """The theme, in the mode of the record on show: drafting vellum
        while it is In Creation (themes.for_mode); parchment while a page
        is built for printing."""
        if self._printing is not None:
            return self._printing
        return for_mode(PALETTES[self.palette_index], self._drafting())

    def _drafting(self) -> bool:
        """Whether the page on show is a record In Creation, or its
        Creation Worksheet."""
        place = self.trail[-1] if self.trail else None
        if place is None or place.kind not in (
            CHARACTER,
            COVENANT,
            LABORATORY,
            WORKSHEET,
        ):
            return False
        record = self._creation_record(place.id)
        return record is not None and record.in_creation

    @property
    def character_id(self) -> str | None:
        place = self.trail[-1] if self.trail else None
        return place.id if place and place.kind == CHARACTER else None

    # Where to go

    # The title page

    def show_title(self) -> None:
        """Show the title page over the whole window, fading in."""
        page = title_page.title_page(self.saga_ids)
        self.title = TitleScreen(page, self.palette_, self.leave_title)
        TopStrip(self.title, self, self.palette_)
        self.stack.addWidget(self.title)
        self.stack.setCurrentWidget(self.title)
        self.title.setFocus()
        self.title.fade_in()

    def leave_title(self, key: str) -> None:
        """Go on from the title page by the way chosen (title_page.OPEN,
        SAGAS or HELP)."""
        title, self.title = self.title, None
        if title is None:
            return
        self.stack.setCurrentIndex(0)
        self.stack.removeWidget(title)
        title.deleteLater()
        if key == title_page.OPEN and title.page.saga_id is not None:
            self.open_saga(title.page.saga_id)
            return
        self.saga_ids = storage.list_sagas()
        self.saga = None
        self.go([Place(SHELF)])
        if key == title_page.HELP:
            self.open_help()

    # The shelf of sagas

    def _run_on_shelf(self, command: Command) -> tuple[bool, object]:
        """Run steps that act on the sagas themselves (saga_forms): they
        save what they change. Whether every step was answered, and what
        they ended with; a refusal is said and counts as unanswered."""
        self._place = None
        answered, end = run_steps(command, self.palette_, self, self.ask)
        if isinstance(end, Refuse):
            self.tell(end.title, end.why)
            return False, end
        return answered, end

    def _shelf_again(self) -> None:
        """Read the sagas again and show the shelf."""
        self.saga_ids = storage.list_sagas()
        self.saga = None
        self.go([Place(SHELF)])

    def new_saga(self) -> None:
        """Create a New Saga and open it."""
        answered, end = self._run_on_shelf(saga_forms.new_saga_form())
        if answered and isinstance(end, Picked):
            self.saga_ids = storage.list_sagas()
            self.open_saga(end.value)

    def delete_saga(self, saga_id: str) -> None:
        """Delete a saga, after asking."""
        try:
            name = storage.load_saga(saga_id).name
        except OSError, ValueError:
            name = saga_id
        answered, _end = self._run_on_shelf(saga_forms.delete_saga(saga_id, name))
        if answered:
            self._shelf_again()

    def change_save_folder(self) -> None:
        """Choose another folder to keep the saves in (moving them there
        if asked), and read the sagas from it from now on."""
        refused = saga_forms.save_folder_refused()
        if refused:
            self.tell("Change Save Folder", refused)
            return
        current = paths.data_dir()
        chosen = self.choose_folder(current)
        if not chosen:
            return
        answered, end = self._run_on_shelf(
            saga_forms.save_folder_form(current, Path(chosen))
        )
        if answered and isinstance(end, list):
            self._shelf_again()
            self.tell("Change Save Folder", "\n".join(end))

    def choose_folder(self, start: Path) -> str:
        """The folder chosen in the system's folder dialog ("" for none).
        Tests replace it."""
        return QFileDialog.getExistingDirectory(
            self, "Choose the save folder", str(start)
        )

    def open_saga(self, saga_id: str) -> None:
        saga = storage.load_saga(saga_id)
        self.load(saga)
        note = storage.newer_save_note(saga)
        if note is not None:
            # Once the saga is on show (open_saga runs before the window does
            # when only one saga is on the shelf).
            QTimer.singleShot(0, lambda: self.tell("Saved by a newer Armarius", note))

    def load(self, saga: Saga) -> None:
        """Open `saga` at its page of covenants."""
        self.saga = saga
        title_page.remember_saga(saga.id)
        self.go([Place(SHELF), Place(SAGA)])

    def open_covenant(self, covenant_id: str | None) -> None:
        self.go([*self._up_to(SAGA), Place(COVENANT, covenant_id)])

    def open_tribunal(self, tribunal_id: str) -> None:
        self.go([*self._up_to(SAGA), Place(TRIBUNAL, tribunal_id)])

    def open_neighbour(self, neighbour_id: str) -> None:
        self.go([*self._up_to(SAGA), Place(NEIGHBOUR, neighbour_id)])

    def show_character(self, character_id: str) -> None:
        """Open a character's sheet, below their covenant."""
        character = self.saga.character(character_id) if self.saga else None
        if character is None:
            return
        self.go(
            [
                Place(SHELF),
                Place(SAGA),
                Place(COVENANT, character.covenant_id),
                Place(CHARACTER, character_id),
            ]
        )

    def open_laboratory(self, lab_id: str) -> None:
        """Open a laboratory's page, below its covenant."""
        lab = self.saga.laboratory(lab_id) if self.saga else None
        if lab is None:
            return
        self.go(
            [
                Place(SHELF),
                Place(SAGA),
                Place(COVENANT, lab.covenant_id),
                Place(LABORATORY, lab_id),
            ]
        )

    def open_sanctum(self, character_id: str) -> None:
        """Open the magus's laboratory below their sheet, so Back returns
        to them; while they have none, create one first (it opens on its
        Creation Worksheet)."""
        saga = self.saga
        magus = saga.character(character_id) if saga else None
        if saga is None or magus is None:
            return
        lab = ls.sanctum(saga, magus)
        if lab is not None:
            self._visit(Place(LABORATORY, lab.id))
            return
        before = {lab.id for lab in saga.laboratories}

        def made() -> None:
            fresh = [lab.id for lab in saga.laboratories if lab.id not in before]
            if fresh:
                self._visit(Place(LABORATORY, fresh[-1]))
                self.go([*self.trail, Place(WORKSHEET, fresh[-1])])

        self.run(
            creation_forms.new_laboratory_form(saga, magus.covenant_id, magus.id),
            made,
        )

    def open_owner(self, lab_id: str) -> None:
        """Open the laboratory's owner below it, so Back returns to it."""
        saga = self.saga
        lab = saga.laboratory(lab_id) if saga else None
        magus = ls.owner(saga, lab) if saga and lab else None
        if magus is not None:
            self._visit(Place(CHARACTER, magus.id))

    def _visit(self, place: Place) -> None:
        """Go to `place` below the page on show, or back to it if the
        trail already passes through it (from a sanctum to its magus and
        back again)."""
        if place in self.trail:
            self.go(self.trail[: self.trail.index(place) + 1])
        else:
            self.go([*self.trail, place])

    def open_content(self) -> None:
        """Open the saga's Saga Content, below the saga."""
        self.go([Place(SHELF), Place(SAGA), Place(CONTENT)])

    def open_familiar(self, familiar_id: str) -> None:
        """Open a familiar's page, below its magus."""
        saga = self.saga
        familiar = self._familiar(familiar_id)
        if saga is None or familiar is None:
            return
        magus = fam.magus_of(saga, familiar)
        self.go(
            [
                Place(SHELF),
                Place(SAGA),
                Place(COVENANT, magus.covenant_id if magus else None),
                *([Place(CHARACTER, magus.id)] if magus else []),
                Place(FAMILIAR, familiar_id),
            ]
        )

    def open_help(self) -> None:
        """Open Help on the page on show, below it (the trail leads back
        to it)."""
        if self.trail and self.trail[-1].kind == HELP:
            return
        self.go([*self.trail, Place(HELP)])

    def _help_ids(self, place: Place, page: QWidget | None) -> list[str]:
        """The help topics for `place`: the tab for the chapter on show
        (_CHAPTER_TABS, else the one whose title starts with its name),
        then the page's."""
        ids = list(_HELP_IDS.get(place.kind, []))
        codex = getattr(page, "codex", None)
        item = codex.rail.currentItem() if codex is not None else None
        chapter = plain(item.text()).strip().casefold() if item is not None else ""
        prefix = _TAB_PREFIX.get(place.kind)
        if chapter and prefix is not None:
            tab = _CHAPTER_TABS.get((place.kind, chapter)) or next(
                (
                    topic.id
                    for topic in help_text.book(help_text.GUI).topics.values()
                    if topic.id.startswith(prefix)
                    and (prefix != "tab-" or not topic.id.startswith(_OTHER_TABS))
                    and topic.title.casefold().startswith(chapter)
                ),
                None,
            )
            if tab is not None:
                ids.insert(0, tab)
        return ids

    def open_seasons(self) -> None:
        """Open the saga's Seasons, below the saga."""
        self.go([Place(SHELF), Place(SAGA), Place(SEASONS)])

    def advance_season(self) -> None:
        """Advance the saga by one season (advance_forms), then show the
        season's results on the Seasons page when it did anything."""
        saga = self.saga
        if saga is None:
            return
        self.run(
            advance_forms.advance_season(saga, storage.backup_saga),
            ended=self._season_played,
        )

    def _season_played(self, end: object) -> None:
        if not isinstance(end, advance_forms.Played):
            self.redraw()
            return
        if end.results:
            self._played = end
            self.open_seasons()
            return
        self.redraw()
        self.tell("Advance Season", end.message)

    def open_worksheet(self, record_id: str) -> None:
        """Open the Creation Worksheet of a character, covenant or
        laboratory, below its page."""
        record = self._creation_record(record_id)
        if record is None:
            return
        if isinstance(record, Character):
            self.show_character(record_id)
        elif isinstance(record, Covenant):
            self.open_covenant(record_id)
        else:
            self.open_laboratory(record_id)
        self.go([*self.trail, Place(WORKSHEET, record_id)])

    def _creation_record(
        self, record_id: str | None
    ) -> Character | Covenant | Laboratory | None:
        saga = self.saga
        if saga is None:
            return None
        return (
            saga.character(record_id)
            or saga.covenant(record_id)
            or saga.laboratory(record_id)
        )

    def _up_to(self, kind: str) -> list[Place]:
        kinds = [place.kind for place in self.trail]
        return self.trail[: kinds.index(kind) + 1] if kind in kinds else [Place(kind)]

    def run(
        self,
        command: Command,
        then: Callable[[], None] | None = None,
        *,
        ended: Callable[[object], None] | None = None,
    ) -> None:
        """Run a button's steps (commands.py), each in its dialog; once
        the last is answered, save the saga and show the page again at the
        same chapter and place (or, given `then`, call it instead: a
        menu's New shows the new record; given `ended`, call it with what
        the steps ended with). Cancelling any step changes nothing."""
        if self.saga is None:
            return
        title = _title(command)
        page = self.page()
        pressed = take_pressed()
        self._place = place_for(pressed, page) if page is not None else None
        step: object = command
        try:
            while isinstance(step, Form | Choose | Confirm | ChooseFile | Act):
                if isinstance(step, Act):
                    step = step.apply()
                    continue
                answered, step = self._answer(step)
                if not answered:
                    return
        finally:
            if self._place is not None:
                self._place.close()
            self._place = None
        if isinstance(step, Refuse):
            # A refusal changes nothing, so there is nothing to save.
            self.tell(step.title, step.why)
            return
        storage.save_saga(self.saga)
        if ended is not None:
            ended(step)
            return
        if then is not None:
            then()
        else:
            self.redraw()
        if isinstance(step, list) and step:
            self.tell(title, "\n".join(step))

    def _answer(
        self, step: Form | Choose | Confirm | ChooseFile
    ) -> tuple[bool, object]:
        """Show one step; whether it was answered, and what it led to."""
        dialog = step_dialog(
            step,
            self.palette_,
            self,
            inline=self._place is not None,
            ask=lambda shown: self.ask(shown),
        )
        if dialog is None:
            assert isinstance(step, Choose)
            self.tell(step.title, step.empty)
            return False, None
        if self.ask(dialog) != QDialog.DialogCode.Accepted:
            return False, None
        return True, answer(step, dialog)

    def tell(self, title: str, words: str) -> None:
        """Show a message (markup): what a step refused, or the notes
        after it. Tests replace it to read the message instead."""
        NoticeDialog(title, words, self.palette_, self).exec()

    def _present(self, dialog: QDialog) -> int:
        """Show a step and wait for it: in place on the page when it was
        made to be (editing.place_for), else as a window. While a step is
        open in place, the page's other buttons and the menus wait."""
        place = self._place
        if place is None or not getattr(dialog, "inline", False):
            return dialog.exec()
        place.open(dialog, replace=not isinstance(dialog, ConfirmDialog))
        waiting = [
            button
            for button in self.findChildren(QPushButton)
            if button.isEnabled()
            and not dialog.isAncestorOf(button)
            and (button.objectName() == "edit" or button.menu() is not None)
        ]
        for button in waiting:
            button.setEnabled(False)
        first = _first_input(dialog)
        if first is not None:
            first.setFocus()
        fit = getattr(dialog, "_fit", None)
        if fit is not None:
            # Wrapped hints know their height only once drawn at width.
            QTimer.singleShot(0, fit)
        self._open = dialog
        try:
            return dialog.exec()
        finally:
            self._open = None
            for button in waiting:
                if shiboken6.isValid(button):
                    button.setEnabled(True)

    def redraw(self) -> None:
        """Build the page on show again, at the chapter and scroll place it
        was at."""
        codex = getattr(self.page(), "codex", None)
        chapter, scrolled = 0, 0
        if codex is not None:
            chapter = codex.rail.currentRow()
            area = codex.pages.currentWidget()
            if isinstance(area, QScrollArea):
                scrolled = area.verticalScrollBar().value()
        self.go(self.trail)
        codex = getattr(self.page(), "codex", None)
        if codex is not None:
            codex.rail.setCurrentRow(chapter)
            area = codex.pages.currentWidget()
            if isinstance(area, QScrollArea):
                body = area.widget()
                if body is not None:
                    body.adjustSize()
                area.verticalScrollBar().setValue(scrolled)

    def page(self) -> QWidget | None:
        """The page on show."""
        item = self.sheet_layout.itemAt(0)
        return item.widget() if item is not None else None

    def go(self, trail: list[Place]) -> None:
        """Show the last page of `trail`, with the trail above it. Leaving
        a page cancels a step open on it."""
        if self._open is not None and shiboken6.isValid(self._open):
            self._open.reject()
        #: The page Help is opened from, to find the chapter on show.
        self._help_from = self.page()
        self.trail = trail
        before = None
        if self.palette_ is not self._applied:
            # Into or out of a record In Creation: the colours change.
            if self.isVisible() and self.title is None:
                before = self.stack.grab()
            self._apply_theme()
        self._show(self._build(trail[-1]))
        self._draw_trail()
        self._draw_advance()
        if before is not None:
            fade_from(self.stack, before)

    # Drawing

    def _help_page(self) -> HelpPage:
        """Help on the page below it in the trail."""
        below = self.trail[-2] if len(self.trail) > 1 else Place(SHELF)
        return HelpPage(
            self.palette_,
            self._help_ids(below, self._help_from),
            self._name(below),
        )

    def _build(self, place: Place) -> QWidget:
        p, saga = self.palette_, self.saga
        if place.kind == HELP:
            return self._help_page()
        if place.kind == SHELF or saga is None:
            sagas = [storage.load_saga(saga_id) for saga_id in self.saga_ids]
            return SagaShelf(
                sagas,
                p,
                self.open_saga,
                self.new_saga,
                self.delete_saga,
                self.change_save_folder,
                str(paths.data_dir()),
            )
        if place.kind == SAGA:
            return SagaPage(
                saga,
                p,
                self.open_covenant,
                self.open_content,
                self.open_seasons,
                self._placer(),
                self.show_character,
                self.open_laboratory,
                self.open_tribunal,
                self.open_neighbour,
            )
        if place.kind == CONTENT:
            return SagaContentPage(saga, p, self.run)
        if place.kind == TRIBUNAL:
            tribunal = saga.tribunal(place.id)
            if tribunal is None:
                return QLabel("No Tribunal chosen.")
            return TribunalPage(saga, tribunal, p, self.run, self._controls())
        if place.kind == NEIGHBOUR:
            neighbour = saga.neighbour(place.id)
            if neighbour is None:
                return QLabel("No neighbour chosen.")
            return NeighbourPage(saga, neighbour, p, self.run, self._controls())
        if place.kind == SEASONS:
            played, self._played = self._played, None
            return SeasonsPage(saga, p, played)
        if place.kind == COVENANT:
            return CovenantPage(
                saga,
                place.id,
                p,
                self.show_character,
                self.open_laboratory,
                self.open_familiar,
                self.run,
                self._controls(),
                self._placer(),
            )
        if place.kind == LABORATORY:
            lab = saga.laboratory(place.id)
            if lab is None:
                return QLabel("No laboratory chosen.")
            return LaboratoryPage(
                saga,
                lab,
                p,
                self.run,
                self._controls(),
                self._placer(),
                open_owner=lambda: self.open_owner(lab.id),
            )
        if place.kind == FAMILIAR:
            familiar = self._familiar(place.id)
            if familiar is None:
                return QLabel("No familiar chosen.")
            return FamiliarPage(saga, familiar, p, self.run, self._controls())
        if place.kind == WORKSHEET:
            record = self._creation_record(place.id)
            if record is None:
                return QLabel("No record chosen.")
            return WorksheetPage(
                saga,
                record,
                p,
                self.run,
                played=lambda command: self.run(command, self._go_up),
            )
        character = saga.character(place.id)
        if character is None:
            return QLabel("No character chosen.")
        return CharacterSheet(
            saga,
            character,
            p,
            self.open_familiar,
            self.run,
            self._controls(),
            self._placer(),
            open_sanctum=lambda: self.open_sanctum(character.id),
        )

    def _controls(self) -> RecordControls | None:
        """What the record's page needs to manage the record (manage.py):
        none for a page with no record to manage."""
        page = self.menu_page()
        if page is None or page.record_to_delete() is None:
            return None
        return RecordControls(
            page,
            self.run,
            self._go_up,
            self.toggle_mode,
            self.open_worksheet,
            self.print_pdf,
        )

    def print_pdf(self) -> None:
        """Print the record on show to a PDF: its options first (the
        paper, and for a character's sheet the spells and background), then
        where to save it."""
        page = self.menu_page()
        record = page.record_to_delete() if page is not None else None
        if record is None:
            return
        name = record.name or "Untitled"
        folder = storage.EXPORTS_DIR
        folder.mkdir(parents=True, exist_ok=True)

        def where(options: pl.PrintOptions) -> ChooseFile:
            return ChooseFile(
                f"Print {escape(name)} to PDF",
                ".pdf",
                folder / f"{printing.file_stem(name)}.pdf",
                lambda path: self.print_to(path, name, options),
                save=True,
            )

        self.run(
            print_forms.print_form(where, sheet=isinstance(record, Character)), None
        )

    def print_to(
        self, path: Path, title: str, options: pl.PrintOptions = pl.DEFAULT_OPTIONS
    ) -> list[str]:
        """Print the record on show to the PDF at `path`; what it did, to
        tell. A character prints as a sheet laid out for paper
        (print_layout.py); other records print their page, drawn afresh in
        the parchment palette."""
        page = self.menu_page()
        record = page.record_to_delete() if page is not None else None
        if isinstance(record, Character) and self.saga is not None:
            doc = pl.document(self.saga, "character", record, options)
            pages = print_sheet.print_document(doc, path, options)
        else:
            self._printing = printing.PARCHMENT
            try:
                built = self._build(self.trail[-1])
            finally:
                self._printing = None
            pages = printing.print_page(
                built, path, title, printing.PARCHMENT, options.paper
            )
        return [f"{pages} page{'s' if pages != 1 else ''} saved to {path}."]

    def toggle_mode(self, record: Moded) -> None:
        """Move `record` between In Creation and In Play (the core asks
        first): into In Creation opens its Creation Worksheet; back to In
        Play shows its page."""

        def moved() -> None:
            if record.in_creation:
                self.open_worksheet(record.id)
            elif self.trail and self.trail[-1].kind == WORKSHEET:
                self._go_up()
            else:
                self.redraw()

        if self.saga is not None:
            self.run(menu_forms.toggle_mode(self.saga, record), moved)

    def _familiar(self, familiar_id: str | None) -> Familiar | None:
        saga = self.saga
        if saga is None:
            return None
        return next((f for f in saga.familiars if f.id == familiar_id), None)

    def _show(self, page: QWidget) -> None:
        layout = self.sheet_layout
        while layout.count():
            item = layout.takeAt(0)
            old = item.widget() if item is not None else None
            if old is not None:
                old.hide()
                old.deleteLater()
        layout.addWidget(page)

    def _name(self, place: Place) -> str:
        saga = self.saga
        if place.kind == SHELF:
            return "Sagas"
        if saga is None:
            return ""
        if place.kind == SAGA:
            return saga.name
        if place.kind == CONTENT:
            return "Saga Content"
        if place.kind == SEASONS:
            return "Seasons"
        if place.kind == HELP:
            return "Help"
        if place.kind == COVENANT:
            covenant = saga.covenant(place.id)
            return covenant.name if covenant else "Unassigned"
        if place.kind == LABORATORY:
            lab = saga.laboratory(place.id)
            return lab.name if lab else ""
        if place.kind == FAMILIAR:
            familiar = self._familiar(place.id)
            return (familiar.name or "(unnamed)") if familiar else ""
        if place.kind == WORKSHEET:
            return "Creation Worksheet"
        if place.kind == TRIBUNAL:
            tribunal = saga.tribunal(place.id)
            return tribunal.name if tribunal else ""
        if place.kind == NEIGHBOUR:
            neighbour = saga.neighbour(place.id)
            return neighbour.name if neighbour else ""
        character = saga.character(place.id)
        return character.name if character else ""

    def _draw_trail(self) -> None:
        while self.crumbs.count():
            item = self.crumbs.takeAt(0)
            old = item.widget() if item is not None else None
            if old is not None:
                old.hide()
                old.deleteLater()
        label = self.palette_["label"]
        for i, place in enumerate(self.trail):
            if i:
                arrow = QLabel("›")
                arrow.setStyleSheet(f"color:{label}; background:transparent")
                self.crumbs.addWidget(arrow)
            crumb = QPushButton(self._name(place))
            crumb.setObjectName("crumb")
            crumb.setFlat(True)
            last = i == len(self.trail) - 1
            crumb.setEnabled(not last)
            crumb.clicked.connect(
                lambda _checked=False, upto=i: self.go(self.trail[: upto + 1])
            )
            self.crumbs.addWidget(crumb)

    def menu_page(self) -> menu_forms.Page | None:
        """The page on show, as the actions it sets out see it."""
        saga = self.saga
        place = self.trail[-1] if self.trail else None
        if (
            saga is None
            or place is None
            or place.kind
            in (
                SHELF,
                WORKSHEET,
                SEASONS,
                HELP,
            )
        ):
            return None
        if place.kind == SAGA:
            return menu_forms.page_for(saga, NodeKind.SAGA)
        if place.kind == CONTENT:
            return menu_forms.page_for(saga, NodeKind.SAGA_CONTENT)
        if place.kind == COVENANT:
            if saga.covenant(place.id) is None:
                # The saga's unassigned characters and laboratories.
                return menu_forms.page_for(saga, NodeKind.CHARACTER_GROUP)
            return menu_forms.page_for(saga, NodeKind.COVENANT, covenant_id=place.id)
        if place.kind == CHARACTER:
            return menu_forms.page_for(saga, NodeKind.CHARACTER, character_id=place.id)
        if place.kind == TRIBUNAL:
            return menu_forms.page_for(saga, NodeKind.TRIBUNAL, tribunal_id=place.id)
        if place.kind == NEIGHBOUR:
            return menu_forms.page_for(saga, NodeKind.NEIGHBOUR, neighbour_id=place.id)
        if place.kind == LABORATORY:
            return menu_forms.page_for(
                saga, NodeKind.LABORATORY, laboratory_id=place.id
            )
        return menu_forms.page_for(saga, NodeKind.FAMILIAR, familiar_id=place.id)

    def _draw_advance(self) -> None:
        saga = self.saga
        shown = saga is not None and bool(self.trail) and self.trail[-1].kind != SHELF
        self.advance.setVisible(shown)
        if saga is not None:
            self.advance.setText(
                f"  {saga.current_season} {saga.current_year} · Advance Season"
            )
            self.advance.setIcon(pictures.icon("season", self.palette_["label"]))

    def _placer(self) -> Placer:
        """What the page on show sets out itself (menu_forms.PLACES)."""
        return Placer(self.menu_page(), self.palette_, self.run, self._show_made)

    def _show_made(self, action: str, record_id: str) -> None:
        """Open the page of what a New entry made: its Creation Worksheet
        while it is In Creation."""
        record = self._creation_record(record_id)
        if action != "create_familiar" and record is not None and record.in_creation:
            self.open_worksheet(record_id)
        elif action == "create_covenant":
            self.open_covenant(record_id)
        elif action == "create_tribunal":
            self.open_tribunal(record_id)
        elif action == "create_neighbour":
            self.open_neighbour(record_id)
        elif action == "create_character":
            self.show_character(record_id)
        elif action == "create_laboratory":
            self.open_laboratory(record_id)
        else:
            self.open_familiar(record_id)

    def _go_up(self) -> None:
        """Leave a deleted record's page for the one above it."""
        self.go(self.trail[:-1] or [Place(SHELF)])

    def crumb_names(self) -> list[str]:
        return [self._name(place) for place in self.trail]

    def toggle_theme(self) -> None:
        self.palette_index = (self.palette_index + 1) % len(PALETTES)
        self._apply_theme()
        if self.trail:  # the pages' colours are drawn in
            self.go(self.trail)

    def _apply_theme(self) -> None:
        p = self._applied = self.palette_
        body = self.stack.widget(0)
        if isinstance(body, Paper):
            body.p = p
            body.update()
        self.headpiece.p = p
        self.headpiece.update()
        self.drag.set_palette(p)
        self.controls.set_palette(p)
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setFont(QFont(pictures.UI, 10))
            app.setStyleSheet(style_sheet(p, pictures.SERIF))
        other = PALETTES[(self.palette_index + 1) % len(PALETTES)]
        self.theme.setText(f"  {other.name}")
        self.theme.setIcon(pictures.icon("theme", p["label"]))
        self.help.setIcon(pictures.icon("help", p["label"]))
