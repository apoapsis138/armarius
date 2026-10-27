"""The desktop's drawing of a character's Church chapter entries: each
ordination, petition or canon case ruled off on the page as a ledger
entry (a rubric in the margin, its heading in small capitals, an italic
line, a badge, its words and a note). What each entry says is
forms.church's; the chapter is put together on the character sheet."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..forms.church import Entry
from .editing import Chooser
from .markup_html import plain, to_html
from .ornaments import ledger_entry
from .themes import Palette
from .widgets import badge, serif, text


def _words(markup: str, p: Palette, size: float) -> QLabel:
    """Markup as wrapping rich text that lets clicks through to the entry."""
    label = QLabel(to_html(markup, p))
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    label.setFont(serif(size))
    label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    return label


class LedgerEntry(QWidget):
    """One entry ruled off on the page; the chosen one is bracketed."""

    def __init__(self, entry: Entry, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.chosen = False
        self.clicked: Callable[[], None] = lambda: None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 8, 10, 10)
        row.setSpacing(12)
        mark = text(entry.rubric, p["heading"], serif(18, bold=True))
        mark.setFixedWidth(40)
        mark.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        row.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(3)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(
            text(entry.title, p["heading"], serif(12.5, bold=True, caps=True))
        )
        if entry.meta:
            top.addWidget(text(entry.meta, p["label"], serif(11, italic=True)))
        top.addStretch(1)
        words, tone = entry.badge
        if words:
            top.addWidget(badge(words, p[tone], p))
        column.addLayout(top)
        if entry.body:
            column.addWidget(_words(entry.body, p, 13))
        if entry.note:
            column.addWidget(_words(entry.note, p, 11.5))
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


def ledger(
    entries: Sequence[Entry],
    p: Palette,
    chooser: Chooser,
    inspect: Callable[[str, str, str], None],
    empty: str,
) -> QWidget:
    """The entries one under another; clicking one chooses its row for
    Edit and Delete and shows it in full in the inspector. `empty` (markup)
    stands in for none."""
    if not entries:
        return text(plain(empty), p["dim"], serif(12.5, italic=True))
    body = QWidget()
    stack = QVBoxLayout(body)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setSpacing(2)
    rows = [LedgerEntry(entry, p) for entry in entries]
    for index, (row, entry) in enumerate(zip(rows, entries, strict=True)):
        lines = entry.info.split("\n")
        # The inspector's heading already names it.
        shown = "\n".join(lines[1:]).strip()

        def clicked(
            index: int = index, entry: Entry = entry, shown: str = shown
        ) -> None:
            chooser.choose(index)
            inspect(entry.title, entry.subtitle, shown)

        row.clicked = clicked
        stack.addWidget(row)

    def mark(chosen: int | None) -> None:
        for index, row in enumerate(rows):
            row.set_chosen(index == chosen)

    chooser.listeners.append(mark)
    return body
