"""The desktop sheet's building blocks: headings, cards, pips,
the experience bar the tables draw, and the inspector.

Colours always come from the palette, so a widget is rebuilt (not
restyled) when the theme changes.
"""

from __future__ import annotations

import html
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from . import pictures
from .markup_html import to_html
from .themes import Palette

#: The item-data role holding an experience bar's (fraction, text).
XP_BAR = Qt.ItemDataRole.UserRole + 1


def serif(
    size: float, *, italic: bool = False, bold: bool = False, caps: bool = False
) -> QFont:
    font = QFont(pictures.SERIF)
    font.setPointSizeF(size)
    font.setItalic(italic)
    font.setBold(bold)
    if caps:
        font.setCapitalization(QFont.Capitalization.SmallCaps)
    return font


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


def chapter_title(words: str, p: Palette) -> QWidget:
    """A heading in small-caps serif over a gilded rule that fades out."""
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 6, 0, 2)
    column.setSpacing(3)
    column.addWidget(text(words, p["foreground"], serif(15, caps=True, bold=True)))
    rule = QFrame()
    rule.setFixedHeight(2)
    rule.setStyleSheet(
        "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
        f" stop:0 {p['accent']}, stop:0.6 {p['rule']}, stop:1 transparent);"
    )
    column.addWidget(rule)
    return box


def display_name(name: str, p: Palette, size: int = 34) -> QLabel:
    """A name in the book face with its first letter a rubricated
    initial, as a chapter of a manuscript opens."""
    name = name or "(unnamed)"
    first, rest = html.escape(name[0]), html.escape(name[1:])
    label = QLabel(
        f"<span style=\"font-family:'{pictures.DISPLAY}';color:{p['heading']};"
        f'font-size:{size}pt">{first}</span>{rest}'
    )
    label.setObjectName("sheetName")
    label.setTextFormat(Qt.TextFormat.RichText)
    return label


class Card(QFrame):
    """A raised panel; `edge` colours its left border (a Virtue's green)."""

    def __init__(self, p: Palette, *, pad: int = 12, edge: str | None = None) -> None:
        super().__init__()
        self.setObjectName("card")
        left = f"border-left:4px solid {edge};" if edge else ""
        self.setStyleSheet(
            f"QFrame#card {{ background:{p['surface']}; border:1px solid"
            f" {p['rule']}; border-radius:6px; {left} }}"
            " QFrame#card QWidget { background:transparent; }"
        )
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(pad, pad - 2, pad, pad)
        self.column.setSpacing(6)


def badge(words: str, colour: str, p: Palette) -> QLabel:
    """A filled pill: a Virtue's tier."""
    label = QLabel(words)
    label.setStyleSheet(
        f"color:{p['background']}; background:{colour}; border-radius:8px;"
        " padding:1px 8px; font-size:8.5pt; font-weight:600"
    )
    return label


def chip(words: str, colour: str) -> QLabel:
    """An outlined pill: a status such as Fresh or Unhurt."""
    label = QLabel(words)
    label.setStyleSheet(
        f"color:{colour}; border:1px solid {colour}; border-radius:9px;"
        " padding:1px 10px; background:transparent"
    )
    return label


def scrolling_page(*widgets: QWidget) -> QScrollArea:
    """A chapter: its parts one under another, scrolling."""
    body = QWidget()
    column = QVBoxLayout(body)
    column.setContentsMargins(18, 4, 18, 12)
    column.setSpacing(12)
    for widget in widgets:
        column.addWidget(widget)
    column.addStretch(1)
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(body)
    return area


class Pips(QWidget):
    """Filled and empty pips, as on a paper sheet."""

    SIZE = 14

    def __init__(self, filled: int, total: int, colour: str) -> None:
        super().__init__()
        self.filled, self.total, self.colour = filled, total, colour
        self.setFixedSize(total * self.SIZE, self.SIZE)
        self.setToolTip(f"{filled} of {total}")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(self.colour), 1.2))
        for i in range(self.total):
            if i < self.filled:
                painter.setBrush(QColor(self.colour))
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(i * self.SIZE + 2, 2, 10, 10))
        painter.end()


#: A table row's height, in pixels.
ROW_HEIGHT = 30


class TallRows(QStyledItemDelegate):
    """Draws cells as usual in rows ROW_HEIGHT tall."""

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        size = super().sizeHint(option, index)
        size.setHeight(max(size.height(), ROW_HEIGHT))
        return size


class XpBarDelegate(TallRows):
    """Draws a cell's XP_BAR data, (fraction, text), as a rounded bar with
    the text over it: the way to the next score."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        bar = index.data(XP_BAR)
        if bar is None:
            super().paint(painter, option, index)
            return
        fraction, words = bar
        p = self.p
        rect = QRectF(option.rect).adjusted(4, 6, -4, -6)  # type: ignore[attr-defined]
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if option.state & QStyle.StateFlag.State_Selected:  # type: ignore[attr-defined]
            painter.fillRect(option.rect, QColor(p["selection"]))  # type: ignore[attr-defined]
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["panel"]))
        radius = rect.height() / 2
        painter.drawRoundedRect(rect, radius, radius)
        if fraction > 0:
            filled = QRectF(rect)
            filled.setWidth(max(rect.width() * min(fraction, 1.0), rect.height()))
            painter.setBrush(QColor(p["accent"]))
            painter.drawRoundedRect(filled, radius, radius)
        font = QFont(option.font)  # type: ignore[attr-defined]
        font.setPointSizeF(8.5)
        painter.setFont(font)
        # The words in the ink colour over the track and in the page colour
        # over the filled part, so they read on both.
        split = rect.left() + rect.width() * min(max(fraction, 0.0), 1.0)
        for clip, ink in (
            (
                QRectF(split, rect.top(), rect.right() - split, rect.height()),
                "foreground",
            ),
            (
                QRectF(rect.left(), rect.top(), split - rect.left(), rect.height()),
                "background",
            ),
        ):
            painter.setClipRect(clip)
            painter.setPen(QColor(p[ink]))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, words)
        painter.restore()


class Inspector(QFrame):
    """The panel beside every chapter that shows what was last chosen: a
    symbol, a title, a line under it and the details (app markup)."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.setObjectName("inspector")
        self.setStyleSheet(
            f"QFrame#inspector {{ background:{p['surface']};"
            f" border-left:1px solid {p['rule']}; }}"
            " QFrame#inspector QLabel { background:transparent; }"
        )
        self.setMinimumWidth(280)
        column = QVBoxLayout(self)
        column.setContentsMargins(16, 14, 16, 14)
        top = QHBoxLayout()
        self.symbol = QLabel()
        top.addWidget(self.symbol)
        self.title = text("", p["heading"], serif(17, bold=True), wrap=True)
        top.addWidget(self.title, 1)
        column.addLayout(top)
        self.subtitle = text("", p["label"], serif(11.5, italic=True), wrap=True)
        column.addWidget(self.subtitle)
        rule = QFrame()
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background:{p['rule']}")
        column.addWidget(rule)
        self.body = QLabel()
        self.body.setTextFormat(Qt.TextFormat.RichText)
        self.body.setWordWrap(True)
        self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(self.body)
        area.setStyleSheet("background:transparent")
        column.addWidget(area, 1)

    def show_item(
        self, title: str, subtitle: str, markup: str, symbol: Path | None = None
    ) -> None:
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.subtitle.setVisible(bool(subtitle))
        self.body.setText(to_html(markup, self.p))
        if symbol is None:
            self.symbol.hide()
        else:
            self.symbol.setPixmap(pictures.pixmap(symbol, self.p["heading"], 34, 2.0))
            self.symbol.show()


class ClickableCard(Card):
    """A card that calls `clicked` when clicked, and lights its border
    under the mouse."""

    def __init__(self, p: Palette, *, pad: int = 12, edge: str | None = None) -> None:
        super().__init__(p, pad=pad, edge=edge)
        self.clicked: Callable[[], None] = lambda: None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        left = f"border-left:4px solid {edge};" if edge else ""
        self.setStyleSheet(
            self.styleSheet()
            + f" QFrame#card:hover {{ border:1px solid {p['accent']}; {left} }}"
        )

    def mousePressEvent(self, event) -> None:
        self.clicked()
        super().mousePressEvent(event)


class Codex(QSplitter):
    """The Codex body every record's page shares: a rail of chapters on
    the left, the chosen chapter in the middle and the inspector, which
    shows whatever was last chosen, on the right."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.inspector = Inspector(p)
        self.inspector.show_item(
            "Inspector", "", "[dim]Choose anything on the page to see it here.[/]"
        )
        self.rail = QListWidget()
        self.rail.setObjectName("rail")
        self.rail.setIconSize(QSize(20, 20))
        self.rail.setFixedWidth(180)
        self.rail.setFont(serif(13))
        self.rail.setStyleSheet(
            "QListWidget#rail { background:transparent; border:none; }"
            f" QListWidget#rail::item {{ padding:8px 6px; color:{p['label']};"
            " border:none; }"
            f" QListWidget#rail::item:selected {{ background:{p['selection']};"
            f" color:{p['heading']}; border-left:3px solid {p['heading']}; }}"
        )
        self.pages = QStackedWidget()
        self.rail.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.setHandleWidth(1)
        self.addWidget(self.rail)
        self.addWidget(self.pages)
        self.addWidget(self.inspector)
        self.setStretchFactor(1, 1)
        self.setSizes([180, 900, 340])

    def add(self, name: str, concept: str, page: QWidget) -> None:
        """Add a chapter, with its icon (artwork.ICON_NAMES); the first
        one added is shown."""
        QListWidgetItem(pictures.icon(concept, self.p["label"], 20), name, self.rail)
        self.pages.addWidget(page)
        if self.rail.count() == 1:
            self.rail.setCurrentRow(0)

    def chapters(self) -> list[str]:
        return [self.rail.item(i).text() for i in range(self.rail.count())]

    def open_chapter(self, name: str) -> None:
        self.rail.setCurrentRow(self.chapters().index(name))

    def inspect(
        self, title: str, subtitle: str, markup: str, symbol: Path | None = None
    ) -> None:
        self.inspector.show_item(title, subtitle, markup, symbol)
