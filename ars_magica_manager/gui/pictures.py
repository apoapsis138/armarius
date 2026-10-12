"""The bundled artwork in Qt: the fonts registered with the app, and the
symbols and icons drawn in a theme colour.

Every SVG is one colour in currentColor (artwork.py); it is drawn here by
putting the wanted colour in its place before Qt reads it.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QFontDatabase, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from .. import artwork

#: The families the style sheets name, once registered.
SERIF = "EB Garamond"
DISPLAY = "Uncial Antiqua"
#: Labels, numbers and tables: Windows's own UI face, else the system's.
UI = "Segoe UI"


def register_fonts() -> list[str]:
    """Register the bundled fonts with Qt; the families it couldn't load
    (the app falls back to a system serif for them)."""
    failed = []
    for family, paths in artwork.FONTS.items():
        for path in paths:
            if QFontDatabase.addApplicationFont(str(path)) < 0:
                failed.append(family)
    return sorted(set(failed))


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


def app_icon() -> QIcon:
    return QIcon(str(artwork.APP_ICON))
