"""A sheet of paper as an image: the laid paper every theme's page starts
from (grain, fibres, a little mottling and the faint chain lines of the
mould; vellum by candlelight on a dark palette; ruled for a draft), and
how dark or light a page's ground gets, for checking text stands out on
it.
"""

from __future__ import annotations

import random

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QRadialGradient

from ...style.palettes import Palette, luminance

#: The side of one tile of paper, in pixels.
TILE = 512


def shade(colour: str, alpha: int) -> QColor:
    """`colour` let through at `alpha` (0 to 255)."""
    shaded = QColor(colour)
    shaded.setAlpha(alpha)
    return shaded


def translucent(colour: str, alpha: int) -> str:
    """`colour` at `alpha`, as a style sheet's #AARRGGBB."""
    return shade(colour, alpha).name(QColor.NameFormat.HexArgb)


def laid_paper(p: Palette) -> QImage:
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


#: How much of a page may be darker (on a light page) or lighter (on a
#: dark one) than its worst ground: a speck of grain under a letter does
#: not stop it being read, a texture all through the text does.
SPECKS = 0.02


def worst_ground(image: QImage, dark: bool) -> str:
    """The ground text on `image` has to stand out against: the darkest
    of its colours on a light page (the lightest on a dark one), leaving
    out the few specks (SPECKS) a reader's eye passes over."""
    step = 3
    seen: list[tuple[float, str]] = []
    for y in range(0, image.height(), step):
        for x in range(0, image.width(), step):
            colour = QColor(image.pixel(x, y)).name()
            seen.append((luminance(colour), colour))
    seen.sort(reverse=dark)
    return seen[int(len(seen) * SPECKS)][1]
