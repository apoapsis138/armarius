"""A record's bookmark: a ribbon at the foot of its page's header, as a
book's ribbon marks a page. Bookmarked, it is filled in the heading's
colour and the record is kept in the saga's The Troupe chapter
(troupe.py); otherwise it is a faint outline. Drawn in code."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QWidget

from .. import troupe
from .themes import Palette

#: The ribbon's size, in pixels.
WIDTH, HEIGHT = 18, 34
#: How deep the swallowtail notch at its foot is.
NOTCH = 8


class Ribbon(QAbstractButton):
    """The bookmark of one record; a click puts it in or takes it out."""

    def __init__(self, saga_id: str, kind: str, record_id: str, p: Palette) -> None:
        super().__init__()
        self.saga_id, self.kind, self.record_id, self.p = saga_id, kind, record_id, p
        self.setCheckable(True)
        self.setChecked(troupe.is_bookmarked(saga_id, kind, record_id))
        self.setFixedSize(QSize(WIDTH + 4, HEIGHT + 2))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setAccessibleName("Bookmark")
        self.toggled.connect(self._toggled)
        self._tell()

    def _toggled(self, on: bool) -> None:
        troupe.set_bookmarked(self.saga_id, self.kind, self.record_id, on)
        self._tell()

    def _tell(self) -> None:
        self.setToolTip(
            "Bookmarked: kept in the saga's The Troupe chapter. Click to take "
            "the bookmark out"
            if self.isChecked()
            else "Bookmark this page, to keep it in the saga's The Troupe chapter"
        )

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left, right, foot = 2.0, 2.0 + WIDTH, float(HEIGHT)
        ribbon = QPainterPath(QPointF(left, 0))
        ribbon.lineTo(right, 0)
        ribbon.lineTo(right, foot)
        ribbon.lineTo((left + right) / 2, foot - NOTCH)
        ribbon.lineTo(left, foot)
        ribbon.closeSubpath()
        marked = self.isChecked()
        ink = QColor(
            self.p["heading" if marked else "label" if self.underMouse() else "rule"]
        )
        painter.setPen(QPen(ink, 1.2))
        if marked:
            painter.setBrush(ink)
        painter.drawPath(ribbon)
        painter.end()


def with_bookmark(header: QWidget, ribbon: Ribbon | None) -> QWidget:
    """A page's header with its ribbon at the right of its foot; the header
    alone when the page has none."""
    if ribbon is None:
        return header
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    row.addWidget(header, 1)
    row.addWidget(ribbon, 0, Qt.AlignmentFlag.AlignBottom)
    return box
