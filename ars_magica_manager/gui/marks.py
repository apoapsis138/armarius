"""Ability marks, drawn in code after the Art symbols: a dark woodcut block
with notched corners and a light charge cut out of it.

The charges are a registry by ability name (mark_charges.MARKS), and
each drawn mark is cached by name, colour and size, so a table of forty
abilities draws each mark once however often it is shown.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPixmap, QTransform

from .mark_charges import CATEGORIES, DETAILS, IMAGES, MARKS, PLAIN
from .mark_shapes import rough, stroke, tile

#: The charge stays inside this square, clear of the block's edge.
CLEAR = (10.0, 90.0)
#: The size every charge is drawn at, along its longer side.
SPAN = 74.0
#: From this size up a mark is cut with its engraved lines and a rough edge.
DETAILED = 48


def key(name: str, category: str = "") -> str:
    """The mark an ability is drawn with: its own (by its name, or the part
    before its ":" or "(", as in Craft: Smith or Area Lore (Normandy)),
    else its category's."""
    for candidate in (name, name.split(":")[0].split(" (")[0].strip()):
        if candidate in MARKS or candidate in IMAGES:
            return candidate
    return category if category in CATEGORIES else "General"


def _charge(name: str) -> QPainterPath:
    return (MARKS.get(name) or CATEGORIES[name])()


def _fit(charge: QPainterPath) -> QTransform:
    """Scale the charge to SPAN along its longer side (less if it would
    reach the edge) and centre it on the block."""
    box = charge.boundingRect()
    scale = min(SPAN, CLEAR[1] - CLEAR[0]) / max(box.width(), box.height())
    c = box.center()
    return (
        QTransform().translate(-c.x(), -c.y())
        * QTransform().scale(scale, scale)
        * QTransform().translate(50, 50)
    )


#: An emblem's picture is read at this size before its light parts are
#: picked out (larger than any mark draws it, and quick to scan).
_EMBLEM_SIDE = 192


@cache
def _light_parts(path: Path) -> QImage:
    """The emblem's light (gilt) pixels as an opaque mask, the rest clear."""
    image = (
        QImage(str(path))
        .scaled(
            _EMBLEM_SIDE,
            _EMBLEM_SIDE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        .convertToFormat(QImage.Format.Format_ARGB32)
    )
    out = QImage(image.size(), QImage.Format.Format_ARGB32)
    out.fill(Qt.GlobalColor.transparent)
    ink = QColor(0, 0, 0, 255)
    for y in range(image.height()):
        for x in range(image.width()):
            c = image.pixelColor(x, y)
            if c.alpha() > 128 and c.lightness() > 95:
                out.setPixelColor(x, y, ink)
    return out


@cache
def pixmap(
    name: str, category: str, colour: str, size: int, ratio: float = 2.0
) -> QPixmap:
    """The ability's mark, `size` pixels square, its block in `colour`,
    sharp on a screen of device-pixel `ratio`."""
    mark = key(name, category)
    side = round(size * ratio)
    picture = QPixmap(side, side)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(side / 100, side / 100)
    ink = QColor(colour)
    detailed = size >= DETAILED
    seed = sum(map(ord, mark))
    block = rough(tile(), seed, 0.7) if detailed else tile()
    painter.fillPath(block, ink)
    if mark in IMAGES:
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationOut
        )
        painter.drawImage(QRectF(13, 13, 74, 74), _light_parts(IMAGES[mark]))
    else:
        fit = _fit(_charge(mark))
        smooth = fit.map(_charge(mark))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillPath(rough(smooth, seed + 1, 0.45) if detailed else smooth, ink)
        if detailed:
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceOver
            )
            if mark not in PLAIN:
                # The cutter's second line, just inside the charge's edge.
                inset = smooth.subtracted(stroke(smooth, 9)).simplified()
                painter.fillPath(stroke(inset, 1.5), ink)
            if mark in DETAILS:
                painter.fillPath(fit.map(DETAILS[mark]()), ink)
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return picture
