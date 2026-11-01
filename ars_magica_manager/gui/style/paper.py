"""The page the desktop version is drawn on, and the shadows that lift
things off it.

The window's body is a sheet of laid paper (grain, fibres, a little
mottling and the faint chain lines of the mould; vellum by candlelight in
the dark theme; ruled drafting vellum for a record In Creation), darker
toward its edges. Plain widgets are transparent
(sheet.style_sheet), so the paper shows through them; cards, seals and
the inspector sit on it with a soft shadow.
"""

from __future__ import annotations

import random

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QImage,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from ...style.palettes import Palette

#: The side of one tile of paper, in pixels.
TILE = 512

_tiles: dict[str, QPixmap] = {}


def shade(colour: str, alpha: int) -> QColor:
    """`colour` let through at `alpha` (0 to 255)."""
    shaded = QColor(colour)
    shaded.setAlpha(alpha)
    return shaded


def translucent(colour: str, alpha: int) -> str:
    """`colour` at `alpha`, as a style sheet's #AARRGGBB."""
    return shade(colour, alpha).name(QColor.NameFormat.HexArgb)


def _paper(p: Palette) -> QImage:
    """One tile of paper in palette `p`; the same every time it is made."""
    chance = random.Random(7)
    tile = QImage(TILE, TILE, QImage.Format.Format_RGB32)
    tile.fill(QColor(p["background"]))
    painter = QPainter(tile)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Mottling: soft blots of every size, drawn again across each edge so
    # that tiles meet without a seam.
    painter.setPen(Qt.PenStyle.NoPen)
    for _ in range(50):
        x, y = chance.uniform(0, TILE), chance.uniform(0, TILE)
        radius = chance.uniform(30, 110)
        blot = shade(p["paper-fleck"], chance.randint(3, 8))
        for dx in (-TILE, 0, TILE):
            for dy in (-TILE, 0, TILE):
                centre = QPointF(x + dx, y + dy)
                soft = QRadialGradient(centre, radius)
                soft.setColorAt(0, blot)
                soft.setColorAt(1, shade(p["paper-fleck"], 0))
                painter.setBrush(soft)
                painter.drawEllipse(centre, radius, radius)
    # The grain.
    for _ in range(TILE * TILE // 3):
        if chance.random() < 0.5:
            painter.setPen(
                shade(p["paper-sheen"], chance.randint(6, 10 if p.dark else 22))
            )
        else:
            painter.setPen(
                shade(p["paper-fleck"], chance.randint(6, 30 if p.dark else 20))
            )
        painter.drawPoint(chance.randrange(TILE), chance.randrange(TILE))
    # Fibres.
    fibre = "paper-sheen" if p.dark else "paper-fleck"
    for _ in range(60):
        x, y = chance.uniform(0, TILE), chance.uniform(0, TILE)
        painter.setPen(
            QPen(
                shade(
                    p[fibre],
                    chance.randint(5, 12) if p.dark else chance.randint(14, 30),
                ),
                0.7,
            )
        )
        painter.drawLine(
            QPointF(x, y),
            QPointF(x + chance.uniform(-14, 14), y + chance.uniform(-6, 6)),
        )
    # The chain lines the mould leaves in laid paper.
    if not p.dark and not p.ruled:
        painter.setPen(QPen(shade(p["paper-fleck"], 10), 1))
        for x in range(0, TILE, 48):
            painter.drawLine(x, 0, x, TILE)
    # A draft's ruling: faint lines across, as for writing.
    if p.ruled:
        ink = p["paper-sheen"] if p.dark else p["paper-fleck"]
        painter.setPen(QPen(shade(ink, 14 if p.dark else 22), 1))
        for y in range(0, TILE, 32):
            painter.drawLine(0, y, TILE, y)
    painter.end()
    return tile


def paper(p: Palette) -> QPixmap:
    """A tile of paper in palette `p`, made once."""
    if p.name not in _tiles:
        _tiles[p.name] = QPixmap.fromImage(_paper(p))
    return _tiles[p.name]


class Paper(QWidget):
    """A widget drawn as a sheet of paper, darker toward its edges."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p

    def paintEvent(self, event: QPaintEvent) -> None:
        p, page = self.p, self.rect()
        painter = QPainter(self)
        painter.drawTiledPixmap(page, paper(p))
        edges = QRadialGradient(
            QPointF(page.center()), max(page.width(), page.height()) * 0.75
        )
        edges.setColorAt(0.6, shade(p["shadow"], 0))
        edges.setColorAt(1.0, shade(p["shadow"], 120 if p.dark else 60))
        painter.fillRect(page, edges)
        painter.end()


def lift(widget: QWidget, p: Palette, *, blur: int = 18, drop: int = 3) -> None:
    """Lift `widget` off the page with a soft shadow `drop` pixels below it."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, drop)
    shadow.setColor(shade(p["shadow"], 130 if p.dark else 70))
    widget.setGraphicsEffect(shadow)
