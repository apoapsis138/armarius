"""The page the desktop version is drawn on, and the shadows that lift
things off it.

The window's body is a sheet of paper in its theme's look (families.py):
laid paper for Scriptorum (vellum by candlelight in the dark theme; ruled
drafting vellum for a record In Creation), a House's own paper and texture
in its theme, darker toward its edges. Plain widgets are transparent
(sheet.style_sheet), so the paper shows through them; cards, seals and
the inspector sit on it with a soft shadow.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage, QPainter, QPaintEvent, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from ...style.palettes import Palette
from . import liveries
from .families import WINDOW
from .vellum import TILE, shade, translucent

#: What the app's other modules take from here.
__all__ = ["TILE", "Paper", "lift", "paper", "shade", "translucent"]


def _paper(p: Palette) -> QImage:
    """One tile of paper in palette `p`, in its theme's look; the same
    every time it is made."""
    return liveries.look(p).paper(p)


def paper(p: Palette) -> QPixmap:
    """A tile of paper in palette `p`, in its theme's look, made once."""
    return liveries.look(p).tile(p)


class Paper(QWidget):
    """A widget drawn as a page of its theme: its paper, darker toward
    its edges and, for the window's body (`kind` WINDOW) in a House theme,
    framed in its House family's form."""

    def __init__(self, p: Palette, kind: str = WINDOW) -> None:
        super().__init__()
        self.p = p
        self.kind = kind

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        liveries.look(self.p).paint_page(
            painter, QRectF(self.rect()), self.p, self.kind
        )
        painter.end()


def lift(widget: QWidget, p: Palette, *, blur: int = 18, drop: int = 3) -> None:
    """Lift `widget` off the page with a soft shadow `drop` pixels below it."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, drop)
    shadow.setColor(shade(p["shadow"], 130 if p.dark else 70))
    widget.setGraphicsEffect(shadow)
