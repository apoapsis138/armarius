"""The bundled artwork in Qt: the fonts registered with the app, and the
symbols and icons drawn in a theme colour.

Every SVG is one colour in currentColor (artwork.py); it is drawn here by
putting the wanted colour in its place before Qt reads it.
"""

from __future__ import annotations

import math
from functools import cache
from pathlib import Path

from PySide6.QtCore import QByteArray, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer

from .. import artwork
from ..style.fonts import DISPLAY, SERIF, TITLE, UI
from .style.fonts import register_fonts

#: What the app's other modules take from style through here.
__all__ = [
    "DISPLAY",
    "SERIF",
    "TITLE",
    "UI",
    "register_fonts",
]


@cache
def _svg(path: Path, colour: str) -> QByteArray:
    text = path.read_text(encoding="utf-8").replace("currentColor", colour)
    return QByteArray(text.encode("utf-8"))


@cache
def pixmap(path: Path, colour: str, size: int, ratio: float = 1.0) -> QPixmap:
    """The SVG at `path`, `size` pixels square, in `colour`, sharp on a
    screen of device-pixel `ratio`."""
    renderer = QSvgRenderer(_svg(path, colour))
    side = round(size * ratio)
    picture = QPixmap(QSize(side, side))
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, side, side))
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return picture


def icon(concept: str, colour: str, size: int = 20) -> QIcon:
    """A concept's Phosphor icon (artwork.ICON_NAMES) as a QIcon."""
    return QIcon(pixmap(artwork.icon(concept), colour, size, 2.0))


def gear_icon(colour: str, size: int = 20, ratio: float = 2.0) -> QIcon:
    """A gear drawn in `colour` (the title bar's settings): a toothed
    ring round a hole, outlined as the Phosphor icons are."""
    side = round(size * ratio)
    picture = QPixmap(side, side)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(side / 20, side / 20)
    centre, outer, inner, teeth = QPointF(10, 10), 8.2, 6.0, 8
    gear = QPainterPath()
    for i in range(teeth * 4):
        # Each tooth: up, across the top, down, across the root.
        angle = math.tau * (i / (teeth * 4)) - math.pi / 2
        radius = outer if i % 4 in (1, 2) else inner
        point = centre + QPointF(radius * math.cos(angle), radius * math.sin(angle))
        if i == 0:
            gear.moveTo(point)
        else:
            gear.lineTo(point)
    gear.closeSubpath()
    pen = QPen(QColor(colour), 1.5)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(gear)
    painter.drawEllipse(centre, 2.6, 2.6)
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return QIcon(picture)
