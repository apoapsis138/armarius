"""The widget every ledger-style list shares: an entry ruled off on the page,
clickable, bracketed when chosen (ornaments.ledger_entry). Each list's own
entry class fills in what the entry says."""

from __future__ import annotations

from collections.abc import Callable

from armarius_style.desktop.ornaments import ledger_entry
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QWidget

from .themes import Palette


class RuledEntry(QWidget):
    """One entry ruled off on the page; the chosen one is bracketed."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.chosen = False
        self.clicked: Callable[[], None] = lambda: None
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def ruled_row(self) -> QHBoxLayout:
        """The entry's row: a mark in the margin, then its words."""
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 8, 10, 10)
        row.setSpacing(12)
        return row

    def set_chosen(self, chosen: bool) -> None:
        self.chosen = chosen
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked()
        super().mousePressEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        ledger_entry(
            painter,
            QRectF(self.rect()).adjusted(12, 0, 0, 0),
            self.p,
            marked=self.chosen,
        )
        painter.end()
