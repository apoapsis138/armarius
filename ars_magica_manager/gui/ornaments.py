"""Printer's ornaments, the small pieces of art a printed book sets
around its text: a headpiece band over every page, a hedera leaf opening
each heading's rule, a tailpiece closing each chapter, and flourishes in
a card's corners.

The leaves are EB Garamond's own fleurons (❦ ❧ ☙), so nothing new is
bundled; the rules, lozenges and corners are drawn, in the palette's gilt.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QPushButton, QWidget

from . import pictures
from .themes import Palette

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
    painter.setFont(QFont(pictures.SERIF, round(size)))
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

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.draw(painter, self.width(), self.HEIGHT / 2)

    def draw(self, painter: QPainter, width: float, cy: float) -> None:
        raise NotImplementedError


class FleuronRule(_Ornament):
    """A heading's rule: a hedera leaf, then a double rule fading out."""

    def draw(self, painter, width, cy):
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

    def draw(self, painter, width, cy):
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

    def draw(self, painter, width, cy):
        gilt = self.p["accent"]
        cx = width / 2
        _leaf(painter, cx, cy, HEDERA, 24, gilt)
        _leaf(painter, cx - 30, cy, HEDERA_LEFT, 16, gilt)
        _leaf(painter, cx + 30, cy, HEDERA_RIGHT, 16, gilt)
        for side in (-1, 1):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(gilt))
            painter.drawEllipse(QPointF(cx + side * 50, cy), 2.2, 2.2)
            near, far = cx + side * 60, cx + side * (width / 2 - 6)
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

    def draw(self, painter, width, _cy):
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

    def paintEvent(self, _event) -> None:
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

    def enterEvent(self, event) -> None:
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
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
