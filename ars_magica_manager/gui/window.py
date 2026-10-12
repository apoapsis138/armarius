"""The desktop main window: a saga chooser, the saga's covenants and
characters as a tree, and the chosen character's sheet beside it.

Read-only for now: it loads sagas and never saves them, so it is safe to
open beside the terminal app.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import storage
from ..models import Saga
from . import pictures
from .character_sheet import CharacterSheet
from .themes import PALETTES, Palette, style_sheet

#: The tree's role holding a character's id.
CHARACTER_ID = Qt.ItemDataRole.UserRole


class MainWindow(QMainWindow):
    def __init__(self, saga_ids: list[str] | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Ars Magica Manager")
        self.setWindowIcon(pictures.app_icon())
        self.palette_index = 0
        self.saga: Saga | None = None
        self.character_id: str | None = None

        self.sagas = QComboBox()
        self.sagas.addItems(storage.list_sagas() if saga_ids is None else saga_ids)
        self.sagas.currentTextChanged.connect(self.open_saga)
        self.theme = QPushButton()
        self.theme.setFlat(True)
        self.theme.clicked.connect(self.toggle_theme)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Saga"))
        bar.addWidget(self.sagas, 1)
        bar.addStretch(2)
        bar.addWidget(self.theme)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self._tree_chosen)
        self.sheet_area = QWidget()
        self.sheet_layout = QVBoxLayout(self.sheet_area)
        self.sheet_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.sheet_area)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([240, 1000])

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.addLayout(bar)
        layout.addWidget(splitter, 1)
        self.setCentralWidget(body)

        self._apply_theme()
        if self.sagas.count():
            self.open_saga(self.sagas.currentText())

    @property
    def palette_(self) -> Palette:
        return PALETTES[self.palette_index]

    def open_saga(self, saga_id: str) -> None:
        self.load(storage.load_saga(saga_id))

    def load(self, saga: Saga) -> None:
        """Show `saga`: its covenants with their characters, then anyone
        unassigned; the first character's sheet is opened."""
        self.saga = saga
        self.tree.clear()
        groups: list[tuple[str, str | None]] = [(c.name, c.id) for c in saga.covenants]
        if any(ch.covenant_id is None for ch in saga.characters):
            groups.append(("Unassigned", None))
        first: QTreeWidgetItem | None = None
        for name, covenant_id in groups:
            group = QTreeWidgetItem(self.tree, [name])
            group.setFlags(Qt.ItemFlag.ItemIsEnabled)
            group.setIcon(0, pictures.icon("covenant", self.palette_["label"]))
            for ch in saga.characters:
                if ch.covenant_id == covenant_id:
                    item = QTreeWidgetItem(group, [ch.name])
                    item.setData(0, CHARACTER_ID, ch.id)
                    first = first or item
        self.tree.expandAll()
        if first is not None:
            self.tree.setCurrentItem(first)
        else:
            self._show(None)

    def show_character(self, character_id: str) -> None:
        for item in self._character_items():
            if item.data(0, CHARACTER_ID) == character_id:
                self.tree.setCurrentItem(item)

    def _character_items(self) -> list[QTreeWidgetItem]:
        items = []
        for i in range(self.tree.topLevelItemCount()):
            group = self.tree.topLevelItem(i)
            if group is not None:
                items += [group.child(j) for j in range(group.childCount())]
        return items

    def _tree_chosen(self) -> None:
        chosen = self.tree.selectedItems()
        if chosen and chosen[0].data(0, CHARACTER_ID):
            self._show(chosen[0].data(0, CHARACTER_ID))

    def _show(self, character_id: str | None) -> None:
        self.character_id = character_id
        layout = self.sheet_layout
        while layout.count():
            item = layout.takeAt(0)
            old = item.widget() if item is not None else None
            if old is not None:
                old.deleteLater()
        character = (
            next((c for c in self.saga.characters if c.id == character_id), None)
            if self.saga
            else None
        )
        if character is None or self.saga is None:
            layout.addWidget(QLabel("No character chosen."))
        else:
            layout.addWidget(CharacterSheet(self.saga, character, self.palette_))

    def toggle_theme(self) -> None:
        self.palette_index = (self.palette_index + 1) % len(PALETTES)
        self._apply_theme()
        if self.saga is not None:  # the sheet's colours are drawn in
            character_id = self.character_id
            self.load(self.saga)
            if character_id:
                self.show_character(character_id)

    def _apply_theme(self) -> None:
        p = self.palette_
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setFont(QFont(pictures.UI, 10))
            app.setStyleSheet(style_sheet(p, pictures.SERIF))
        other = PALETTES[(self.palette_index + 1) % len(PALETTES)]
        self.theme.setText(f"  {other.name}")
        self.theme.setIcon(pictures.icon("theme", p["label"]))
