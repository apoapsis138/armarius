"""Printer's ornaments, the small pieces of art a printed book sets
around its text: a headpiece band over every page, a hedera leaf opening
each heading's rule, a tailpiece closing each chapter, and flourishes in
a card's corners.

The leaves are EB Garamond's own fleurons (❦ ❧ ☙), so nothing new is
bundled; the rules, lozenges and corners are drawn, in the palette's gilt.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QEnterEvent,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QPushButton, QWidget

from .. import fonts
from ..palettes import Palette

HEDERA, HEDERA_LEFT, HEDERA_RIGHT = "❦", "☙", "❧"


def _alpha(colour: str, alpha: int) -> QColor:
    c = QColor(colour)
    c.setAlpha(alpha)
    return c


def _fading(colour: str, x0: float, x1: float, width: float) -> QPen:
    """A pen in full colour at x0 that fades out by x1."""
    fade = QLinearGradient(x0, 0, x1, 0)
    fade.setColorAt(0, QColor(colour))
    fade.setColorAt(0.7, _alpha(colour, 150))
    fade.setColorAt(1, _alpha(colour, 0))
    return QPen(QBrush(fade), width)


def _leaf(painter: QPainter, x: float, y: float, leaf: str, size: float, colour: str):
    """Draw a fleuron centred on (x, y); its width. The font sets its
    fleurons low in the line, so they are raised to sit on the centre."""
    painter.setFont(QFont(fonts.SERIF, round(size)))
    painter.setPen(QColor(colour))
    width = painter.fontMetrics().horizontalAdvance(leaf)
    box = QRectF(x - width, y - size * 1.7, 2 * width, size * 3)
    painter.drawText(box, Qt.AlignmentFlag.AlignCenter, leaf)
    return width


class _Ornament(QWidget):
    """A strip a fixed height high that only paints."""

    HEIGHT = 18

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.setFixedHeight(self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw(painter, self.width(), self.HEIGHT / 2)

    def draw(self, painter: QPainter, width: float, cy: float) -> None:
        raise NotImplementedError


class FleuronRule(_Ornament):
    """A heading's rule: a hedera leaf, then a double rule fading out."""

    def draw(self, painter: QPainter, width: float, cy: float):
        gilt = self.p["accent"]
        start = _leaf(painter, 9, cy, HEDERA_RIGHT, 13, gilt) + 13
        painter.setPen(_fading(gilt, start, width * 0.8, 1.4))
        painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))
        painter.setPen(_fading(gilt, start, width * 0.55, 0.6))
        painter.drawLine(QPointF(start, cy + 3), QPointF(width * 0.55, cy + 3))


class ShortRule(_Ornament):
    """A short rule under a title: a hedera leaf, with a rule fading out
    to each side."""

    HEIGHT = 26

    def draw(self, painter: QPainter, width: float, cy: float):
        gilt = self.p["accent"]
        cx = width / 2
        _leaf(painter, cx, cy, HEDERA, 15, gilt)
        for side in (-1, 1):
            near, far = cx + side * 18, cx + side * 210
            painter.setPen(_fading(gilt, near, far, 1.2))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))


class Headpiece(_Ornament):
    """The band over a page: a hedera between two leaves, and a double
    rule set with lozenges running out to each side and fading."""

    HEIGHT = 34

    def draw(self, painter: QPainter, width: float, cy: float):
        gilt = self.p["accent"]
        cx = width / 2
        _leaf(painter, cx, cy, HEDERA, 24, gilt)
        _leaf(painter, cx - 30, cy, HEDERA_LEFT, 16, gilt)
        _leaf(painter, cx + 30, cy, HEDERA_RIGHT, 16, gilt)
        self.band(painter, width, cy, 50)

    def band(self, painter: QPainter, width: float, cy: float, inner: float) -> None:
        """The dots `inner` out from the centre, and past them the double
        rule set with lozenges, running out to each side and fading."""
        gilt = self.p["accent"]
        cx = width / 2
        for side in (-1, 1):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(gilt))
            painter.drawEllipse(QPointF(cx + side * inner, cy), 2.2, 2.2)
            near, far = cx + side * (inner + 10), cx + side * (width / 2 - 6)
            painter.setPen(_fading(gilt, near, far, 1.3))
            for dy in (-4, 4):
                painter.drawLine(QPointF(near, cy + dy), QPointF(far, cy + dy))
            painter.setPen(Qt.PenStyle.NoPen)
            x = near
            while (far - x) * side > 0:
                left = 1 - abs(x - near) / abs(far - near)
                painter.setBrush(_alpha(gilt, int(255 * left**1.2)))
                lozenge = QPainterPath(QPointF(x, cy - 3))
                lozenge.lineTo(x + 3, cy)
                lozenge.lineTo(x, cy + 3)
                lozenge.lineTo(x - 3, cy)
                lozenge.closeSubpath()
                painter.drawPath(lozenge)
                x += side * 22


class Tailpiece(_Ornament):
    """A cul-de-lampe closing a chapter: three leaves narrowing to a
    point, between two short rules."""

    HEIGHT = 60

    def draw(self, painter: QPainter, width: float, _cy: float):
        gilt = self.p["accent"]
        cx, top = width / 2, 14
        painter.setPen(_fading(gilt, cx - 34, cx - 150, 1.0))
        painter.drawLine(QPointF(cx - 150, top), QPointF(cx - 34, top))
        painter.setPen(_fading(gilt, cx + 34, cx + 150, 1.0))
        painter.drawLine(QPointF(cx + 34, top), QPointF(cx + 150, top))
        _leaf(painter, cx - 22, top, HEDERA_LEFT, 15, gilt)
        _leaf(painter, cx, top, HEDERA, 17, gilt)
        _leaf(painter, cx + 22, top, HEDERA_RIGHT, 15, gilt)
        _leaf(painter, cx, top + 22, HEDERA, 10, gilt)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(gilt))
        painter.drawEllipse(QPointF(cx, top + 38), 2.2, 2.2)


class FleuronButton(QPushButton):
    """A quiet button drawn as a printer's leaf pointing on (❧), as a
    book points its reader to the page that follows: in the label's
    colour, the heading's when the pointer is over it, with a fine rule
    under it as the filter's drop-downs have."""

    def __init__(self, p: Palette, tip: str) -> None:
        super().__init__()
        self.p = p
        self.setToolTip(tip)
        self.setAccessibleName(tip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setFixedSize(30, 22)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        hot = self.underMouse() or self.hasFocus()
        colour = self.p["heading"] if hot else self.p["label"]
        cy = self.height() / 2 - 1
        _leaf(painter, self.width() / 2, cy, HEDERA_RIGHT, 13, colour)
        painter.setPen(QPen(_alpha(self.p["rule"], 255), 1))
        painter.drawLine(
            QPointF(3, self.height() - 1.5),
            QPointF(self.width() - 3, self.height() - 1.5),
        )
        painter.end()

    def enterEvent(self, event: QEnterEvent) -> None:
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.update()
        super().leaveEvent(event)


def corner_flourishes(painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
    """A curl in each corner of `rect`, with a bracket `arm` long and a
    dot at each end, as a printer frames a panel."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    gilt = QColor(p["accent"])
    r = rect.adjusted(3, 3, -3, -3)
    for x, y, sx, sy in (
        (r.left(), r.top(), 1, 1),
        (r.right(), r.top(), -1, 1),
        (r.left(), r.bottom(), 1, -1),
        (r.right(), r.bottom(), -1, -1),
    ):
        painter.setPen(QPen(gilt, 1.1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        bracket = QPainterPath(QPointF(x + sx * arm, y))
        bracket.lineTo(x, y)
        bracket.lineTo(x, y + sy * arm)
        painter.drawPath(bracket)
        curl = QPainterPath(QPointF(x + sx * 3, y + sy * 3))
        curl.cubicTo(
            x + sx * 9, y + sy * 2, x + sx * 8, y + sy * 8, x + sx * 5, y + sy * 6
        )
        painter.drawPath(curl)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gilt)
        painter.drawEllipse(QPointF(x + sx * (arm + 2), y), 1.2, 1.2)
        painter.drawEllipse(QPointF(x, y + sy * (arm + 2)), 1.2, 1.2)


def gloss_box(painter: QPainter, rect: QRectF, p: Palette, heading: str) -> float:
    """A note boxed as a scribe boxes a gloss: a deeper leaf of parchment
    inside a double gilt rule, a flourish in each corner, a red margin rule
    down its left, and the heading in red small capitals between two hedera
    leaves. Returns where the text under the heading may begin."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    r = rect.adjusted(1, 1, -1, -1)
    leaf = QLinearGradient(0, r.top(), 0, r.bottom())
    leaf.setColorAt(0, QColor(p["surface"]))
    leaf.setColorAt(1, QColor(p["panel"]))
    painter.setBrush(QBrush(leaf))
    painter.setPen(QPen(QColor(p["accent"]), 1.3))
    painter.drawRect(r)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(_alpha(p["accent"], 170), 0.6))
    painter.drawRect(r.adjusted(4, 4, -4, -4))
    corner_flourishes(painter, r.adjusted(4, 4, -4, -4), p, 14)
    painter.setPen(QPen(_alpha(p["heading"], 150), 0.9))
    x = r.left() + InspectorFrame.MARGIN - 8
    painter.drawLine(QPointF(x, r.top() + 44), QPointF(x, r.bottom() - 14))
    cy = r.top() + 22
    font = QFont(fonts.SERIF)
    font.setPointSizeF(16)
    font.setBold(True)
    font.setCapitalization(QFont.Capitalization.SmallCaps)
    painter.setFont(font)
    width = painter.fontMetrics().horizontalAdvance(heading)
    cx = r.center().x()
    painter.setPen(QColor(p["heading"]))
    painter.drawText(
        QRectF(cx - width / 2 - 4, cy - 14, width + 8, 28),
        Qt.AlignmentFlag.AlignCenter,
        heading,
    )
    gilt = p["accent"]
    _leaf(painter, cx - width / 2 - 18, cy, HEDERA_LEFT, 14, gilt)
    _leaf(painter, cx + width / 2 + 18, cy, HEDERA_RIGHT, 14, gilt)
    for side in (-1, 1):
        near = cx + side * (width / 2 + 34)
        far = cx + side * (r.width() / 2 - 22)
        painter.setPen(_fading(gilt, near, far, 0.9))
        painter.drawLine(QPointF(near, cy), QPointF(far, cy))
    painter.restore()
    return r.top() + 44


def ledger_entry(
    painter: QPainter, rect: QRectF, p: Palette, *, marked: bool = False
) -> None:
    """An entry ruled off on the page, as in a muster roll: no box, a
    rubric's red rule down its left, a hairline under it, and, for the one
    whose turn it is, a gilt double bracket."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(
        QPen(_alpha(p["heading"], 200 if marked else 120), 1.6 if marked else 1)
    )
    painter.drawLine(rect.topLeft() + QPointF(0, 4), rect.bottomLeft() - QPointF(0, 4))
    painter.setPen(QPen(_alpha(p["rule"], 200), 0.8))
    painter.drawLine(rect.bottomLeft() + QPointF(8, 0), rect.bottomRight())
    if marked:
        gilt = QColor(p["accent"])
        for inset in (-6, -10):
            painter.setPen(QPen(gilt, 1.2 if inset == -6 else 0.6))
            x = rect.left() + inset
            bracket = QPainterPath(QPointF(x + 8, rect.top()))
            bracket.lineTo(x, rect.top())
            bracket.lineTo(x, rect.bottom())
            bracket.lineTo(x + 8, rect.bottom())
            painter.drawPath(bracket)
    painter.restore()


class InspectorFrame(QWidget):
    """A note boxed at the foot of a form, as a scribe boxes a gloss: a
    deeper leaf of parchment inside a double gilt rule, a flourish in each
    corner, a red margin rule down its left, and its heading between two
    hedera leaves."""

    MARGIN = 24

    def __init__(self, heading: str, p: Palette) -> None:
        super().__init__()
        self.heading, self.p = heading, p

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        gloss_box(painter, QRectF(self.rect()), self.p, self.heading)
        painter.end()
