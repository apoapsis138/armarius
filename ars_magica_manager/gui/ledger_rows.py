"""Rows of a list ruled off on the page as a ledger's entries: a mark in
the margin, a heading in small capitals with an italic line beside it,
a badge, the entry's words and a note under them. The chosen entry is
bracketed (ornaments.ledger_entry). What each says is a core
tribunal_packages.LedgerCard."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..tribunal_packages import LedgerCard
from .character_sheet import TextBlock
from .editing import Chooser
from .ornaments import ledger_entry
from .themes import Palette
from .widgets import badge, serif, text


class LedgerRow(QWidget):
    """One entry ruled off on the page."""

    def __init__(self, card: LedgerCard, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.chosen = False
        self.clicked: Callable[[], None] = lambda: None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 8, 10, 10)
        row.setSpacing(12)
        mark = text(card.rubric, p["heading"], serif(18, bold=True))
        mark.setFixedWidth(40)
        mark.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        row.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(3)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(text(card.title, p["heading"], serif(12.5, bold=True, caps=True)))
        if card.meta:
            top.addWidget(text(card.meta, p["label"], serif(11, italic=True)))
        top.addStretch(1)
        if card.badge is not None and card.badge[0]:
            words, tone = card.badge
            top.addWidget(badge(words, p[tone], p))
        column.addLayout(top)
        if card.body:
            words = TextBlock(card.body, p)
            words.setFont(serif(13))
            column.addWidget(words)
        if card.note:
            note = TextBlock(card.note, p)
            note.setFont(serif(11.5))
            column.addWidget(note)
        row.addLayout(column, 1)

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


def ledger_rows(
    cards: Sequence[LedgerCard],
    p: Palette,
    chooser: Chooser,
    on_choose: Callable[[int], None],
) -> QWidget:
    """`cards` stacked as ledger entries; clicking one chooses its row for
    the section's buttons, brackets it and calls `on_choose(row)`."""
    body = QWidget()
    stack = QVBoxLayout(body)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setSpacing(2)
    rows = [LedgerRow(card, p) for card in cards]
    for index, row in enumerate(rows):

        def clicked(index: int = index) -> None:
            chooser.choose(index)
            on_choose(index)

        row.clicked = clicked
        stack.addWidget(row)

    def mark(chosen: int | None) -> None:
        for index, row in enumerate(rows):
            row.set_chosen(index == chosen)

    chooser.listeners.append(mark)
    return body
