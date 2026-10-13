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

import shiboken6
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import familiars as fam
from .. import menu_forms, storage
from ..actions import NodeKind
from ..commands import Act, Choose, Command, Confirm, Form, Refuse
from ..models import Character, Covenant, Familiar, Laboratory, Saga
from . import pictures
from .character_sheet import CharacterSheet
from .covenant import CovenantPage
from .editing import InPlace, place_for
from .familiar import FamiliarPage
from .forms import ConfirmDialog, answer, step_dialog
from .laboratory import LaboratoryPage
from .markup_html import plain
from .menus import menu_buttons
from .ornaments import Headpiece
from .pages import SagaPage, SagaShelf
from .paper import Paper
from .saga_content import SagaContentPage
from .themes import PALETTES, Palette, style_sheet
from .widgets import take_pressed
from .worksheet import WorksheetPage

SHELF, SAGA, COVENANT, CHARACTER, LABORATORY, FAMILIAR, CONTENT, WORKSHEET = (
    "shelf",
    "saga",
    "covenant",
    "character",
    "laboratory",
    "familiar",
    "content",
    "worksheet",
)


def _first_input(dialog: QDialog) -> QWidget | None:
    """The widget a step's typing starts in: a form's first field, a
    list's search, a question's Cancel."""
    inputs = getattr(dialog, "inputs", None)
    if inputs:
        return next(iter(inputs.values()))
    return getattr(dialog, "search", None) or getattr(dialog, "cancel", None)


def _title(command: Command) -> str:
    if isinstance(command, Confirm):
        return command.question
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
        self.setWindowTitle("Ars Magica Manager")
        self.setWindowIcon(pictures.app_icon())
        self.palette_index = 0
        self.saga_ids = storage.list_sagas() if saga_ids is None else saga_ids
        self.saga: Saga | None = None
        self.trail: list[Place] = []
        #: Shows a step and waits for it (in place; a test answers it).
        self.ask: Callable[[QDialog], int] = self._present
        #: Where the running button's steps open (editing.place_for), and
        #: the step open there now.
        self._place: InPlace | None = None
        self._open: QDialog | None = None

        self.crumbs = QHBoxLayout()
        self.crumbs.setSpacing(2)
        self.theme = QPushButton()
        self.theme.setFlat(True)
        self.theme.clicked.connect(self.toggle_theme)
        bar = QHBoxLayout()
        bar.setContentsMargins(12, 4, 8, 0)
        bar.addLayout(self.crumbs)
        bar.addStretch(1)
        #: The New and More menus for the page on show (menus.py).
        self.menus = QHBoxLayout()
        self.menus.setSpacing(2)
        bar.addLayout(self.menus)
        bar.addWidget(self.theme)

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
        self.setCentralWidget(body)

        self._apply_theme()
        if len(self.saga_ids) == 1:
            self.open_saga(self.saga_ids[0])
        else:
            self.go([Place(SHELF)])

    @property
    def palette_(self) -> Palette:
        return PALETTES[self.palette_index]

    @property
    def character_id(self) -> str | None:
        place = self.trail[-1] if self.trail else None
        return place.id if place and place.kind == CHARACTER else None

    # Where to go

    def open_saga(self, saga_id: str) -> None:
        self.load(storage.load_saga(saga_id))

    def load(self, saga: Saga) -> None:
        """Open `saga` at its page of covenants."""
        self.saga = saga
        self.go([Place(SHELF), Place(SAGA)])

    def open_covenant(self, covenant_id: str | None) -> None:
        self.go([*self._up_to(SAGA), Place(COVENANT, covenant_id)])

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

    def run(self, command: Command, then: Callable[[], None] | None = None) -> None:
        """Run a button's steps (commands.py), each in its dialog; once
        the last is answered, save the saga and show the page again at the
        same chapter and place (or, given `then`, call it instead: a
        menu's New shows the new record). Cancelling any step changes
        nothing."""
        if self.saga is None:
            return
        title = _title(command)
        page = self.page()
        pressed = take_pressed()
        self._place = place_for(pressed, page) if page is not None else None
        step: object = command
        try:
            while isinstance(step, Form | Choose | Confirm | Act):
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
        if then is not None:
            then()
        else:
            self.redraw()
        if isinstance(step, list) and step:
            self.tell(title, "\n".join(step))

    def _answer(self, step: Form | Choose | Confirm) -> tuple[bool, object]:
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
        QMessageBox.information(self, plain(title), plain(words))

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
        self.trail = trail
        self._show(self._build(trail[-1]))
        self._draw_trail()
        self._draw_menus()

    # Drawing

    def _build(self, place: Place) -> QWidget:
        p, saga = self.palette_, self.saga
        if place.kind == SHELF or saga is None:
            sagas = [storage.load_saga(saga_id) for saga_id in self.saga_ids]
            return SagaShelf(sagas, p, self.open_saga)
        if place.kind == SAGA:
            return SagaPage(saga, p, self.open_covenant, self.open_content)
        if place.kind == CONTENT:
            return SagaContentPage(saga, p, self.run)
        if place.kind == COVENANT:
            return CovenantPage(
                saga,
                place.id,
                p,
                self.show_character,
                self.open_laboratory,
                self.open_familiar,
                self.run,
            )
        if place.kind == LABORATORY:
            lab = saga.laboratory(place.id)
            if lab is None:
                return QLabel("No laboratory chosen.")
            return LaboratoryPage(saga, lab, p, self.run)
        if place.kind == FAMILIAR:
            familiar = self._familiar(place.id)
            if familiar is None:
                return QLabel("No familiar chosen.")
            return FamiliarPage(saga, familiar, p, self.run)
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
        return CharacterSheet(saga, character, p, self.open_familiar, self.run)

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
        """The page on show, as its New and More menus see it."""
        saga = self.saga
        place = self.trail[-1] if self.trail else None
        if saga is None or place is None or place.kind in (SHELF, WORKSHEET):
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
        if place.kind == LABORATORY:
            return menu_forms.page_for(
                saga, NodeKind.LABORATORY, laboratory_id=place.id
            )
        return menu_forms.page_for(saga, NodeKind.FAMILIAR, familiar_id=place.id)

    def _draw_menus(self) -> None:
        while self.menus.count():
            item = self.menus.takeAt(0)
            old = item.widget() if item is not None else None
            if old is not None:
                old.hide()
                old.deleteLater()
        for button in menu_buttons(
            self.menu_page(),
            self.palette_,
            self.run,
            self._show_made,
            self._go_up,
            worksheet=self.open_worksheet,
        ):
            self.menus.addWidget(button)

    def _show_made(self, action: str, record_id: str) -> None:
        """Open the page of what a New entry made: its Creation Worksheet
        while it is In Creation."""
        record = self._creation_record(record_id)
        if action != "create_familiar" and record is not None and record.in_creation:
            self.open_worksheet(record_id)
        elif action == "create_covenant":
            self.open_covenant(record_id)
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
        p = self.palette_
        body = self.centralWidget()
        if isinstance(body, Paper):
            body.p = p
            body.update()
        self.headpiece.p = p
        self.headpiece.update()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setFont(QFont(pictures.UI, 10))
            app.setStyleSheet(style_sheet(p, pictures.SERIF))
        other = PALETTES[(self.palette_index + 1) % len(PALETTES)]
        self.theme.setText(f"  {other.name}")
        self.theme.setIcon(pictures.icon("theme", p["label"]))
