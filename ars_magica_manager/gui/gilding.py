"""The gilt the desktop version lays on its working parts: the inspector
framed as a gilt leaf, every scroll bar drawn as a burnished rod, and the
gold wash a chosen row takes, dark at its left and fading to nothing.

The gold is the illuminated initials' own (illumination.gold), so the
rods and frames shine as the letters do.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import QApplication, QScrollBar, QStyle, QStyleOptionSlider

from .illumination import gold
from .ornaments import HEDERA_RIGHT, _leaf, corner_flourishes
from .paper import paper, shade
from .themes import PIGMENTS, WASH, Palette


def wash(p: Palette, left: float, right: float, alpha: int = WASH) -> QLinearGradient:
    """The gold wash across a row from `left` to `right`: the accent at
    `alpha` fading to nothing."""
    gradient = QLinearGradient(left, 0, right, 0)
    gradient.setColorAt(0, shade(p["accent"], alpha))
    gradient.setColorAt(1, shade(p["accent"], 0))
    return gradient


def margin_leaf(painter: QPainter, x: float, y: float, colour: str) -> None:
    """The small pointing leaf (❧) that marks a chosen row, centred on
    (x, y) in the margin before it."""
    _leaf(painter, x, y, HEDERA_RIGHT, 10, colour)


# -- the inspector's leaf --


def gilt_leaf(painter: QPainter, rect: QRectF, p: Palette) -> None:
    """Paint `rect` as a gilt leaf: the page's paper, a little warmer, in
    a burnished frame with a fine inner rule and a flourish in each
    corner."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.drawTiledPixmap(rect.toRect(), paper(p))
    painter.fillRect(rect, shade(p["panel"], 70))
    outer = rect.adjusted(8, 8, -8, -8)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(gold(outer), 2.4))
    painter.drawRect(outer)
    painter.setPen(QPen(shade(p["accent"], 200), 0.8))
    painter.drawRect(outer.adjusted(5, 5, -5, -5))
    corner_flourishes(painter, outer.adjusted(6, 6, -6, -6), p, 30)


# -- the scroll bars --


def _slider(bar: QScrollBar) -> QRectF:
    option = QStyleOptionSlider()
    bar.initStyleOption(option)
    return QRectF(
        bar.style().subControlRect(
            QStyle.ComplexControl.CC_ScrollBar,
            option,
            QStyle.SubControl.SC_ScrollBarSlider,
            bar,
        )
    )


def paint_gilt_rod(painter: QPainter, bar: QScrollBar, p: Palette) -> None:
    """A scroll bar as a hairline rule with a lozenge at each end, and its
    handle as a burnished rod with a bead at each end. A horizontal bar is
    the vertical one turned on its side."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    slider = _slider(bar)
    across, along = bar.width(), bar.height()
    if bar.orientation() == Qt.Orientation.Horizontal:
        # Turn the bar so its length runs down, as a vertical bar's does.
        painter.translate(0, bar.height())
        painter.rotate(-90)
        across, along = bar.height(), bar.width()
        slider = QRectF(
            bar.height() - slider.bottom(),
            slider.left(),
            slider.height(),
            slider.width(),
        )
    cx = across / 2
    painter.setPen(QPen(shade(p["accent"], 140), 1))
    painter.drawLine(QPointF(cx, 8), QPointF(cx, along - 8))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(p["accent"]))
    for y in (4, along - 4):
        lozenge = QPainterPath(QPointF(cx, y - 3.5))
        lozenge.lineTo(cx + 3.5, y)
        lozenge.lineTo(cx, y + 3.5)
        lozenge.lineTo(cx - 3.5, y)
        lozenge.closeSubpath()
        painter.drawPath(lozenge)
    if bar.maximum() <= bar.minimum():
        return
    pressed = bar.isSliderDown()
    half = 4.0 if pressed else 3.5
    rod = QRectF(cx - half, slider.top() + 6, 2 * half, max(slider.height() - 12, 4))
    sheen = QLinearGradient(rod.topLeft(), rod.topRight())
    sheen.setColorAt(0.0, QColor(PIGMENTS["gold-dark"]))
    sheen.setColorAt(0.35, QColor(PIGMENTS["gold"]))
    sheen.setColorAt(0.5, QColor(PIGMENTS["gold-light"]))
    sheen.setColorAt(0.7, QColor(PIGMENTS["gold"]))
    sheen.setColorAt(1.0, QColor(PIGMENTS["gold-dark"]))
    painter.setBrush(QBrush(sheen))
    painter.setPen(QPen(QColor(PIGMENTS["gold-dark"]), 0.8))
    painter.drawRoundedRect(rod, half, half)
    for y in (rod.top() - 1.5, rod.bottom() + 1.5):
        painter.setBrush(gold(QRectF(cx - 4, y - 4, 8, 8)))
        painter.drawEllipse(QPointF(cx, y), 3.2, 3.2)


class GiltRods(QObject):
    """Draws every scroll bar in the application as a gilt rod, in the
    palette `p` (set again when the theme changes). The window's style
    sheet still sizes the bars; this only paints them, so it works
    whatever style the platform draws everything else in."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Paint and isinstance(watched, QScrollBar):
            painter = QPainter(watched)
            paint_gilt_rod(painter, watched, self.p)
            painter.end()
            return True
        return False


_rods: GiltRods | None = None


def gild_application(app: QApplication, p: Palette) -> None:
    """Draw every scroll bar in `app` as a gilt rod and every selection
    the platform draws itself (a menu's, a drop-down's, a text's) in the
    theme's colours, never the system's accent: in palette `p`."""
    global _rods
    if _rods is None:
        _rods = GiltRods(p)
        app.installEventFilter(_rods)
    _rods.p = p
    palette = app.palette()
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        palette.setColor(group, QPalette.ColorRole.Highlight, QColor(p["selection"]))
        palette.setColor(
            group, QPalette.ColorRole.HighlightedText, QColor(p["foreground"])
        )
        palette.setColor(group, QPalette.ColorRole.Accent, QColor(p["accent"]))
        palette.setColor(group, QPalette.ColorRole.Link, QColor(p["heading"]))
    app.setPalette(palette)


# -- a name's initial --


def gilt_letter(
    painter: QPainter, letter: str, font: QFont, baseline: QPointF, p: Palette
) -> None:
    """Draw `letter` in `font` with its baseline starting at `baseline`, in
    the rubric's colour with a gilt edge: a gold hairline along its left
    edges that fades out across the letter, as light catches raised gold."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addText(baseline, font, letter)
    painter.fillPath(path, QColor(p["heading"]))
    box = path.boundingRect()
    edge = QLinearGradient(box.left(), 0, box.left() + box.width() * 0.55, 0)
    # The edge shines up to white gold; on a dark page, where the initial
    # is gold already, it starts at white to show.
    edge.setColorAt(0.0, QColor(PIGMENTS["lead-white" if p.dark else "gold-light"]))
    edge.setColorAt(0.4, QColor(PIGMENTS["gold-light"]))
    edge.setColorAt(0.7, QColor(PIGMENTS["gold"]))
    edge.setColorAt(1.0, shade(PIGMENTS["gold"], 0))
    painter.strokePath(path, QPen(QBrush(edge), 1.7))
