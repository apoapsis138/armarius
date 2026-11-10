"""The small pieces a page is set with: labels in the book face, chapter
titles, a name with a gilt initial, cards and pills.
"""

from __future__ import annotations

import html
from collections.abc import Sequence
from math import ceil

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...style import fonts
from ...style.palettes import Palette
from . import gilding, liveries
from .ornaments import FleuronRule, Tailpiece, corner_flourishes
from .paper import lift, translucent


def serif(
    size: float, *, italic: bool = False, bold: bool = False, caps: bool = False
) -> QFont:
    font = QFont(fonts.SERIF)
    font.setPointSizeF(size)
    font.setItalic(italic)
    font.setBold(bold)
    if caps:
        font.setCapitalization(QFont.Capitalization.SmallCaps)
    return font


def heading(size: float, p: Palette, *, caps: bool = False) -> QFont:
    """A section heading's font in palette `p`'s theme: bold EB Garamond
    in Scriptorum, its House family's heading type in a House theme (the
    book face's small capitals in a Societas)."""
    look = liveries.look(p)
    caps = (caps or look.always_small_caps) and look.small_caps
    font = serif(size, bold=True, caps=caps)
    font.setFamily(look.heading_family)
    return font


def title(size: float, p: Palette) -> QFont:
    """A big title's font (a dialog's) in palette `p`'s theme: as a
    heading in Scriptorum, its House family's title type in a House
    theme (a Societas's blackletter)."""
    font = serif(size, bold=True)
    font.setFamily(liveries.look(p).title_family)
    return font


def heading_ink(p: Palette) -> str:
    """The colour a section heading is inked in on palette `p`'s page."""
    return p[liveries.look(p).heading_ink]


def text(
    words: str, colour: str, font: QFont | None = None, *, wrap: bool = False
) -> QLabel:
    """A plain label in one palette colour."""
    label = QLabel(words)
    label.setStyleSheet(f"color:{colour}; background:transparent")
    if font is not None:
        label.setFont(font)
    label.setWordWrap(wrap)
    return label


def mix(a: str, b: str, t: float) -> QColor:
    """The colour `t` of the way from `a` to `b`."""
    ca, cb = QColor(a), QColor(b)
    return QColor(
        round(ca.red() + (cb.red() - ca.red()) * t),
        round(ca.green() + (cb.green() - ca.green()) * t),
        round(ca.blue() + (cb.blue() - ca.blue()) * t),
    )


def chapter_title(
    words: str, p: Palette, *, rule: bool = True, emblem: QWidget | None = None
) -> QWidget:
    """A heading in small-caps serif over a rule that opens with a hedera
    leaf and fades out (the rule left to the caller when not `rule`), with
    `emblem` (a season's medallion) before the words."""
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 6, 0, 2 if rule else 0)
    column.setSpacing(1)
    # Beside buttons (no rule of its own), a long title wraps rather than
    # push them off the page.
    label = text(words, heading_ink(p), heading(15, p, caps=True), wrap=not rule)
    if emblem is None:
        column.addWidget(label)
    else:
        line = QHBoxLayout()
        line.setSpacing(8)
        line.addWidget(emblem, 0, Qt.AlignmentFlag.AlignVCenter)
        line.addWidget(label, 1, Qt.AlignmentFlag.AlignVCenter)
        column.addLayout(line)
    if rule:
        column.addWidget(FleuronRule(p))
    return box


class GiltName(QLabel):
    """A record's name in the book face, its first letter a rubricated
    initial in the display face with a gilt edge, as a chapter of a
    manuscript opens. Its text is
    the name as rich text, so it reads (and is read) as a plain label;
    only its painting is its own."""

    def __init__(self, name: str, p: Palette, size: int) -> None:
        first, rest = html.escape(name[0]), html.escape(name[1:])
        super().__init__(
            f"<span style=\"font-family:'{fonts.DISPLAY}';"
            f'font-size:{size}pt">{first}</span>{rest}'
        )
        self.name, self.p = name, p
        self.initial = QFont(fonts.DISPLAY)
        self.initial.setPointSizeF(size)
        self.setObjectName("sheetName")
        self.setTextFormat(Qt.TextFormat.RichText)

    def _metrics(self) -> tuple[QFontMetricsF, QFontMetricsF]:
        return QFontMetricsF(self.initial), QFontMetricsF(self.font())

    def _initial_advance(self) -> float:
        return gilding.initial_advance(self.name[0], self.initial, self.p)

    def sizeHint(self) -> QSize:
        big, small = self._metrics()
        width = self._initial_advance() + small.horizontalAdvance(self.name[1:])
        height = max(big.ascent(), small.ascent()) + max(big.descent(), small.descent())
        margins = self.contentsMargins()
        return QSize(
            ceil(width) + 4 + margins.left() + margins.right(),
            ceil(height) + margins.top() + margins.bottom(),
        )

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def paintEvent(self, _event: QPaintEvent) -> None:
        big, small = self._metrics()
        box = QRectF(self.contentsRect())
        ascent = max(big.ascent(), small.ascent())
        height = ascent + max(big.descent(), small.descent())
        baseline = box.top() + (box.height() - height) / 2 + ascent
        painter = QPainter(self)
        gilding.gilt_letter(
            painter, self.name[0], self.initial, QPointF(box.left(), baseline), self.p
        )
        painter.setFont(self.font())
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(
            QPointF(box.left() + self._initial_advance(), baseline),
            self.name[1:],
        )
        painter.end()


class PaintedInitial(QWidget):
    """A passage's opening letter, painted as a name's initial is
    (gilding.gilt_letter), `size` points high: for a House theme whose
    initials are small illuminated letters."""

    def __init__(self, letter: str, p: Palette, size: float) -> None:
        super().__init__()
        self.letter, self.p = letter, p
        self.font_ = QFont(fonts.DISPLAY)
        self.font_.setPointSizeF(size)
        metrics = QFontMetricsF(self.font_)
        self.setFixedSize(
            ceil(gilding.initial_advance(letter, self.font_, p)) + 2,
            ceil(metrics.ascent() + metrics.descent() * 0.5),
        )
        self.setAccessibleName(letter)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        baseline = QPointF(1, QFontMetricsF(self.font_).ascent())
        gilding.gilt_letter(painter, self.letter, self.font_, baseline, self.p)
        painter.end()


def initial_letter(letter: str, p: Palette, size: float) -> QWidget:
    """A passage's opening letter, `size` points high: in the display face
    in the heading's colour, or a small illuminated letter in a House
    theme that paints its initials so."""
    if liveries.look(p).quartered_initials:
        return PaintedInitial(letter, p, size)
    label = QLabel(letter)
    label.setFont(QFont(fonts.DISPLAY, round(size)))
    label.setStyleSheet(f"color:{p['heading']}; background:transparent")
    return label


def display_name(name: str, p: Palette, size: int = 34) -> QLabel:
    """A name in the book face with its first letter a gilt-edged
    initial."""
    return GiltName(name or "(unnamed)", p, size)


#: Cards to a row of a page.
CARDS_ACROSS = 3


class Card(QFrame):
    """A panel lying on the page, with a soft shadow and a flourish in
    each corner; `edge` colours its left border (a Virtue's green)."""

    def __init__(self, p: Palette, *, pad: int = 12, edge: str | None = None) -> None:
        super().__init__()
        self.p, self.edge = p, edge
        self.setObjectName("card")
        left = f"border-left:4px solid {edge};" if edge else ""
        self.setStyleSheet(
            f"QFrame#card {{ background:{translucent(p['surface'], 215)};"
            f" border:1px solid {translucent(p['rule'], 150)}; border-radius:6px;"
            f" {left} }}"
            " QFrame#card QWidget { background:transparent; }"
        )
        lift(self, p)
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(pad, pad - 2, pad, pad)
        self.column.setSpacing(6)

    def set_edge(self, edge: str) -> None:
        """Colour its left border anew (it was given one when made)."""
        assert self.edge is not None
        self.setStyleSheet(self.styleSheet().replace(self.edge, edge))
        self.edge = edge

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        frame = QRectF(self.rect()).adjusted(3 if self.edge else 0, 0, 0, 0)
        corner_flourishes(
            QPainter(self), frame, self.p, 8 if self.height() < 80 else 12
        )


def card_grid(cards: Sequence[QWidget], across: int = CARDS_ACROSS) -> QWidget:
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(14)
    for i, card in enumerate(cards):
        grid.addWidget(card, i // across, i % across)
    for column in range(across):
        grid.setColumnStretch(column, 1)
    return box


#: Every tier pill's size, wide enough for Minor and Major.
TIER_BADGE = QSize(52, 18)


def badge(words: str, colour: str, p: Palette) -> QLabel:
    """A filled pill: a Virtue's tier."""
    label = QLabel(words)
    label.setStyleSheet(
        f"color:{p['background']}; background:{colour}; border-radius:8px;"
        " padding:1px 8px; font-size:8.5pt; font-weight:600"
    )
    return label


def tier_badge(tier: str, colour: str, p: Palette) -> QLabel:
    """A Virtue's, Flaw's, Boon's or Hook's tier, as a pill of one size
    whatever its word or the card beside it; a Free one is dimmed."""
    label = badge(tier, p["dim"] if tier == "Free" else colour, p)
    label.setFixedSize(TIER_BADGE)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


def chip(words: str, colour: str) -> QLabel:
    """An outlined pill: a status such as Fresh or Unhurt."""
    label = QLabel(words)
    label.setStyleSheet(
        f"color:{colour}; border:1px solid {colour}; border-radius:9px;"
        " padding:1px 10px; background:transparent"
    )
    return label


def scrolling_page(p: Palette, *widgets: QWidget) -> QScrollArea:
    """A chapter: its parts one under another, closed by a tailpiece,
    scrolling."""
    body = QWidget()
    column = QVBoxLayout(body)
    column.setContentsMargins(18, 4, 18, 12)
    column.setSpacing(12)
    for widget in widgets:
        column.addWidget(widget)
    column.addWidget(Tailpiece(p))
    column.addStretch(1)
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(body)
    return area
