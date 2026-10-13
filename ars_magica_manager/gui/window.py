"""The desktop main window: one page at a time, the way a book is read,
with a trail across the top back to the pages above it (Sagas, the saga,
the covenant, the character, their familiar) and a printer's headpiece
over every page.

The pages are the shelf of sagas, a saga's covenants, a covenant (its
people, laboratories and seasons), a laboratory, a character's sheet and a
familiar's. Where the
reader is is a list of places, the trail; the page shown is built from
the last one, so changing the theme just builds it again.

Read-only for now: it loads sagas and never saves them, so it is safe to
open beside the terminal app.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import familiars as fam
from .. import storage
from ..models import Familiar, Saga
from . import pictures
from .character_sheet import CharacterSheet
from .covenant import CovenantPage
from .familiar import FamiliarPage
from .laboratory import LaboratoryPage
from .ornaments import Headpiece
from .pages import SagaPage, SagaShelf
from .paper import Paper
from .saga_content import SagaContentPage
from .themes import PALETTES, Palette, style_sheet

SHELF, SAGA, COVENANT, CHARACTER, LABORATORY, FAMILIAR, CONTENT = (
    "shelf",
    "saga",
    "covenant",
    "character",
    "laboratory",
    "familiar",
    "content",
)


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

        self.crumbs = QHBoxLayout()
        self.crumbs.setSpacing(2)
        self.theme = QPushButton()
        self.theme.setFlat(True)
        self.theme.clicked.connect(self.toggle_theme)
        bar = QHBoxLayout()
        bar.setContentsMargins(12, 4, 8, 0)
        bar.addLayout(self.crumbs)
        bar.addStretch(1)
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

    def _up_to(self, kind: str) -> list[Place]:
        kinds = [place.kind for place in self.trail]
        return self.trail[: kinds.index(kind) + 1] if kind in kinds else [Place(kind)]

    def go(self, trail: list[Place]) -> None:
        """Show the last page of `trail`, with the trail above it."""
        self.trail = trail
        self._show(self._build(trail[-1]))
        self._draw_trail()

    # Drawing

    def _build(self, place: Place) -> QWidget:
        p, saga = self.palette_, self.saga
        if place.kind == SHELF or saga is None:
            sagas = [storage.load_saga(saga_id) for saga_id in self.saga_ids]
            return SagaShelf(sagas, p, self.open_saga)
        if place.kind == SAGA:
            return SagaPage(saga, p, self.open_covenant, self.open_content)
        if place.kind == CONTENT:
            return SagaContentPage(saga, p)
        if place.kind == COVENANT:
            return CovenantPage(
                saga,
                place.id,
                p,
                self.show_character,
                self.open_laboratory,
                self.open_familiar,
            )
        if place.kind == LABORATORY:
            lab = saga.laboratory(place.id)
            if lab is None:
                return QLabel("No laboratory chosen.")
            return LaboratoryPage(saga, lab, p)
        if place.kind == FAMILIAR:
            familiar = self._familiar(place.id)
            if familiar is None:
                return QLabel("No familiar chosen.")
            return FamiliarPage(saga, familiar, p)
        character = saga.character(place.id)
        if character is None:
            return QLabel("No character chosen.")
        return CharacterSheet(saga, character, p, self.open_familiar)

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
