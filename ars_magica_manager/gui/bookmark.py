"""A record's bookmark: a ribbon at the foot of its page's header, as a
book's ribbon marks a page. Bookmarked, it is filled in the heading's
colour and the record is kept in the saga's The Troupe chapter
(troupe.py); otherwise it is a faint outline. Drawn in code.

Under the ribbon, on a record the players may not know of
(viewing.can_be_unknown), its seal: an eye, struck through while the
record is hidden from the players. It says Hidden or Known when the
mouse is over it, and a click reveals or hides the record (forms/reveal.py)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QVBoxLayout, QWidget

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


#: The seal's size, in pixels.
SEAL = 34


class Seal(QAbstractButton):
    """Whether the players know of a record: an eye in a ring, struck
    through and filled in the primary ink while it is hidden, a plain eye
    in the label ink once it is known. Its words are its tooltip; a click
    runs `act` (Reveal or Hide)."""

    def __init__(self, known: bool, p: Palette, act: Callable[[], None]) -> None:
        super().__init__()
        self.known, self.p = known, p
        self.setFixedSize(QSize(SEAL + 4, SEAL + 4))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setAccessibleName("Known" if known else "Hidden")
        self.setToolTip(
            "Known to the players. Click to hide it from them"
            if known
            else "Hidden from the players. Click to reveal it to them"
        )
        self.clicked.connect(act)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        hidden = not self.known
        ink = QColor(
            self.p["primary" if hidden else "heading" if self.underMouse() else "label"]
        )
        centre = QPointF(self.width() / 2, self.height() / 2)
        fill = QColor(ink)
        fill.setAlpha(40 if hidden else 15)
        painter.setPen(QPen(ink, 1.5))
        painter.setBrush(fill)
        painter.drawEllipse(centre, SEAL / 2, SEAL / 2)
        # The eye, 20 units across, drawn about the centre.
        painter.translate(centre.x() - 10, centre.y() - 10)
        pen = QPen(ink, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        lids = QPainterPath(QPointF(2, 10))
        lids.quadTo(QPointF(10, 2), QPointF(18, 10))
        lids.quadTo(QPointF(10, 18), QPointF(2, 10))
        painter.drawPath(lids)
        painter.setBrush(ink)
        painter.drawEllipse(QPointF(10, 10), 2.6, 2.6)
        if hidden:
            pen.setWidthF(2.0)
            painter.setPen(pen)
            painter.drawLine(QPointF(3, 17), QPointF(17, 3))
        painter.end()


def with_seal(ribbon: Ribbon, seal: Seal | None) -> QWidget:
    """The ribbon with the record's seal under it, when it has one."""
    if seal is None:
        return ribbon
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(6)
    column.addWidget(ribbon, 0, Qt.AlignmentFlag.AlignHCenter)
    column.addWidget(seal, 0, Qt.AlignmentFlag.AlignHCenter)
    return box


def with_bookmark(header: QWidget, ribbon: QWidget | None) -> QWidget:
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
