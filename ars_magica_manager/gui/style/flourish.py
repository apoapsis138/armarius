"""Scriptorum's printer's ornaments as plain drawing: a hedera leaf, a
rule fading out, a heading's rule, the headpiece band, a tailpiece and a
card's corner flourishes.

They are the steps Scriptorum's own look (families.Look) paints a page
with; the House families draw their own in their place. The widgets that
show them are in ornaments.py. The leaves are EB Garamond's own fleurons
(❦ ❧ ☙), so nothing new is bundled.
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

from ...style import fonts
from ...style.palettes import Palette

HEDERA, HEDERA_LEFT, HEDERA_RIGHT = "❦", "☙", "❧"


def alpha(colour: str, opacity: int) -> QColor:
    """`colour` at `opacity` (0 to 255)."""
    c = QColor(colour)
    c.setAlpha(opacity)
    return c


def fading(colour: str, x0: float, x1: float, width: float) -> QPen:
    """A pen in full colour at x0 that fades out by x1."""
    fade = QLinearGradient(x0, 0, x1, 0)
    fade.setColorAt(0, QColor(colour))
    fade.setColorAt(0.7, alpha(colour, 150))
    fade.setColorAt(1, alpha(colour, 0))
    return QPen(QBrush(fade), width)


def leaf(
    painter: QPainter, x: float, y: float, glyph: str, size: float, colour: str
) -> float:
    """Draw a fleuron centred on (x, y); its width. The font sets its
    fleurons low in the line, so they are raised to sit on the centre."""
    painter.setFont(QFont(fonts.SERIF, round(size)))
    painter.setPen(QColor(colour))
    width = painter.fontMetrics().horizontalAdvance(glyph)
    box = QRectF(x - width, y - size * 1.7, 2 * width, size * 3)
    painter.drawText(box, Qt.AlignmentFlag.AlignCenter, glyph)
    return width


def lozenge(painter: QPainter, x: float, y: float, r: float) -> None:
    """A small filled lozenge centred on (x, y), `r` from centre to tip,
    in the painter's brush."""
    shape = QPainterPath(QPointF(x, y - r))
    shape.lineTo(x + r, y)
    shape.lineTo(x, y + r)
    shape.lineTo(x - r, y)
    shape.closeSubpath()
    painter.drawPath(shape)


def heading_rule(painter: QPainter, width: float, cy: float, p: Palette) -> None:
    """A heading's rule: a hedera leaf, then a double rule fading out."""
    gilt = p["accent"]
    start = leaf(painter, 9, cy, HEDERA_RIGHT, 13, gilt) + 13
    painter.setPen(fading(gilt, start, width * 0.8, 1.4))
    painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))
    painter.setPen(fading(gilt, start, width * 0.55, 0.6))
    painter.drawLine(QPointF(start, cy + 3), QPointF(width * 0.55, cy + 3))


def short_rule(painter: QPainter, width: float, cy: float, p: Palette) -> None:
    """A short rule under a title: a hedera leaf, with a rule fading out
    to each side."""
    gilt = p["accent"]
    cx = width / 2
    leaf(painter, cx, cy, HEDERA, 15, gilt)
    for side in (-1, 1):
        near, far = cx + side * 18, cx + side * 210
        painter.setPen(fading(gilt, near, far, 1.2))
        painter.drawLine(QPointF(near, cy), QPointF(far, cy))


def headpiece_centre(painter: QPainter, width: float, cy: float, p: Palette) -> None:
    """The headpiece's centre: a hedera between two leaves."""
    gilt = p["accent"]
    cx = width / 2
    leaf(painter, cx, cy, HEDERA, 24, gilt)
    leaf(painter, cx - 30, cy, HEDERA_LEFT, 16, gilt)
    leaf(painter, cx + 30, cy, HEDERA_RIGHT, 16, gilt)


def band(painter: QPainter, width: float, cy: float, inner: float, p: Palette) -> None:
    """The headpiece's band: dots `inner` out from the centre, and past
    them a double rule set with lozenges, running out to each side and
    fading."""
    gilt = p["accent"]
    cx = width / 2
    for side in (-1, 1):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(gilt))
        painter.drawEllipse(QPointF(cx + side * inner, cy), 2.2, 2.2)
        near, far = cx + side * (inner + 10), cx + side * (width / 2 - 6)
        painter.setPen(fading(gilt, near, far, 1.3))
        for dy in (-4, 4):
            painter.drawLine(QPointF(near, cy + dy), QPointF(far, cy + dy))
        painter.setPen(Qt.PenStyle.NoPen)
        x = near
        while (far - x) * side > 0:
            left = 1 - abs(x - near) / abs(far - near)
            painter.setBrush(alpha(gilt, int(255 * left**1.2)))
            lozenge(painter, x, cy, 3)
            x += side * 22


def tailpiece(painter: QPainter, width: float, p: Palette) -> None:
    """A cul-de-lampe closing a chapter: three leaves narrowing to a
    point, between two short rules."""
    gilt = p["accent"]
    cx, top = width / 2, 14
    painter.setPen(fading(gilt, cx - 34, cx - 150, 1.0))
    painter.drawLine(QPointF(cx - 150, top), QPointF(cx - 34, top))
    painter.setPen(fading(gilt, cx + 34, cx + 150, 1.0))
    painter.drawLine(QPointF(cx + 34, top), QPointF(cx + 150, top))
    leaf(painter, cx - 22, top, HEDERA_LEFT, 15, gilt)
    leaf(painter, cx, top, HEDERA, 17, gilt)
    leaf(painter, cx + 22, top, HEDERA_RIGHT, 15, gilt)
    leaf(painter, cx, top + 22, HEDERA, 10, gilt)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(gilt))
    painter.drawEllipse(QPointF(cx, top + 38), 2.2, 2.2)


#: Each corner of a rectangle: which corner, and the way inward (sx, sy).
def corners_of(r: QRectF) -> tuple[tuple[float, float, int, int], ...]:
    return (
        (r.left(), r.top(), 1, 1),
        (r.right(), r.top(), -1, 1),
        (r.left(), r.bottom(), 1, -1),
        (r.right(), r.bottom(), -1, -1),
    )


def corner_flourishes(painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
    """A curl in each corner of `rect`, with a bracket `arm` long and a
    dot at each end, as a printer frames a panel."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    gilt = QColor(p["accent"])
    r = rect.adjusted(3, 3, -3, -3)
    for x, y, sx, sy in corners_of(r):
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
