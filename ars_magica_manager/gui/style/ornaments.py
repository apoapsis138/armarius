"""Printer's ornaments, the small pieces of art a printed book sets
around its text: a headpiece band over every page, a rule under each
heading, a tailpiece closing each chapter, and an ornament in a card's
corners.

Each is drawn in its theme's look (families.py): Scriptorum's hedera
leaves and gilt flourishes (flourish.py), or a House family's own form.
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

from ...style.palettes import Palette
from . import liveries
from .flourish import HEDERA, HEDERA_LEFT, HEDERA_RIGHT, fading, leaf
from .flourish import alpha as _alpha

#: What other modules take from here.
__all__ = [
    "HEDERA",
    "HEDERA_LEFT",
    "HEDERA_RIGHT",
    "FleuronButton",
    "FleuronRule",
    "Headpiece",
    "InspectorFrame",
    "ShortRule",
    "Tailpiece",
    "corner_flourishes",
    "gloss_box",
    "heading_family",
    "ledger_entry",
]


def heading_family(p: Palette) -> str:
    """The headings' typeface in palette `p`'s theme."""
    return liveries.look(p).heading_family


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
    """A heading's rule: in Scriptorum, a hedera leaf, then a double rule
    fading out."""

    def draw(self, painter: QPainter, width: float, cy: float):
        liveries.look(self.p).heading_rule(painter, width, cy, self.p)


class ShortRule(_Ornament):
    """A short rule under a title: in Scriptorum, a hedera leaf, with a
    rule fading out to each side."""

    HEIGHT = 26

    def draw(self, painter: QPainter, width: float, cy: float):
        liveries.look(self.p).short_rule(painter, width, cy, self.p)


class Headpiece(_Ornament):
    """The band over a page: in Scriptorum, a hedera between two leaves,
    and a double rule set with lozenges running out to each side and
    fading."""

    HEIGHT = 34

    def draw(self, painter: QPainter, width: float, cy: float):
        liveries.look(self.p).headpiece_centre(painter, width, cy, self.p)
        self.band(painter, width, cy, 50)

    def band(self, painter: QPainter, width: float, cy: float, inner: float) -> None:
        """The band running out to each side from `inner` beside the
        centre."""
        liveries.look(self.p).band(painter, width, cy, inner, self.p)


class Tailpiece(_Ornament):
    """A cul-de-lampe closing a chapter: in Scriptorum, three leaves
    narrowing to a point, between two short rules."""

    HEIGHT = 60

    def draw(self, painter: QPainter, width: float, _cy: float):
        liveries.look(self.p).tailpiece(painter, width, self.p)


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
        leaf(painter, self.width() / 2, cy, HEDERA_RIGHT, 13, colour)
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
    """The ornament in each corner of `rect`, its arms `arm` long, as a
    printer frames a panel: in Scriptorum a curl and a bracket with a dot
    at each end; in a House theme its family's own."""
    liveries.look(p).corners(painter, rect, p, arm)


def gloss_box(painter: QPainter, rect: QRectF, p: Palette, heading: str) -> float:
    """A note boxed as a scribe boxes a gloss: a deeper leaf of parchment
    inside a double gilt rule, a flourish in each corner, a red margin rule
    down its left, and the heading in red small capitals between two hedera
    leaves. Returns where the text under the heading may begin."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    r = rect.adjusted(1, 1, -1, -1)
    sheet = QLinearGradient(0, r.top(), 0, r.bottom())
    sheet.setColorAt(0, QColor(p["surface"]))
    sheet.setColorAt(1, QColor(p["panel"]))
    painter.setBrush(QBrush(sheet))
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
    font = QFont(heading_family(p))
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
    leaf(painter, cx - width / 2 - 18, cy, HEDERA_LEFT, 14, gilt)
    leaf(painter, cx + width / 2 + 18, cy, HEDERA_RIGHT, 14, gilt)
    for side in (-1, 1):
        near = cx + side * (width / 2 + 34)
        far = cx + side * (r.width() / 2 - 22)
        painter.setPen(fading(gilt, near, far, 0.9))
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
