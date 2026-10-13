"""The desktop sheet's building blocks: headings, cards, pips,
the experience bar the tables draw, and the inspector, with the printer's
ornaments (ornaments.py) a book sets around them.

Colours always come from the palette, so a widget is rebuilt (not
restyled) when the theme changes.
"""

from __future__ import annotations

import html
from collections.abc import Callable, Sequence
from pathlib import Path

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPen,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .. import artwork
from ..arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from . import pictures
from .markup_html import to_html
from .ornaments import FleuronRule, Tailpiece, corner_flourishes
from .paper import lift, translucent
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
    """A heading in small-caps serif over a rule that opens with a hedera
    leaf and fades out."""
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 6, 0, 2)
    column.setSpacing(1)
    column.addWidget(text(words, p["foreground"], serif(15, caps=True, bold=True)))
    column.addWidget(FleuronRule(p))
    return box


#: The section button pressed last, so the window can open the steps it
#: starts in place, beside it (see editing.place_for).
_pressed: list[QPushButton] = []


def edit_button(
    words: str, p: Palette, on_click: Callable[[], None], concept: str = "edit"
) -> QPushButton:
    """A section's button (Edit, Add, Delete...), with its verb's icon."""
    button = QPushButton(pictures.icon(concept, p["heading"], 16), f" {words}")
    button.setObjectName("edit")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.pressed.connect(lambda: _pressed.__setitem__(slice(None), [button]))
    button.clicked.connect(lambda _checked=False: on_click())
    return button


def take_pressed() -> QPushButton | None:
    """The section button pressed last, forgotten once taken."""
    button = _pressed[0] if _pressed else None
    _pressed.clear()
    return button


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

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        frame = QRectF(self.rect()).adjusted(3 if self.edge else 0, 0, 0, 0)
        corner_flourishes(
            QPainter(self), frame, self.p, 8 if self.height() < 80 else 12
        )


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
    symbol, a title, a line under it and the details (app markup), framed
    by corner flourishes."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.setObjectName("inspector")
        self.setStyleSheet(
            f"QFrame#inspector {{ background:{translucent(p['surface'], 225)};"
            f" border-left:1px solid {translucent(p['rule'], 160)}; }}"
            " QFrame#inspector QLabel { background:transparent; }"
        )
        lift(self, p, blur=24, drop=0)
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

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        frame = QRectF(self.rect()).adjusted(4, 2, -2, -2)
        corner_flourishes(QPainter(self), frame, self.p, 18)

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

    def set_chosen(self, chosen: bool) -> None:
        """Outline the card as the row its section's Edit and Delete act
        on."""
        self.chosen = chosen
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if getattr(self, "chosen", False):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor(self.p["heading"]), 2))
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 6, 6)


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


def table_style(view: QAbstractItemView, p: Palette) -> None:
    view.setStyleSheet(
        f"QAbstractItemView {{ background:{p['surface']};"
        f" alternate-background-color:{p['background']};"
        f" border:1px solid {p['rule']}; selection-background-color:"
        f" {p['selection']}; selection-color:{p['foreground']}; }}"
        f" QHeaderView::section {{ background:{p['panel']}; color:{p['foreground']};"
        " border:none; padding:5px; font-weight:600; }"
    )


def arts_heat_grid(
    totals: dict[tuple[str, str], int],
    p: Palette,
    on_choose: Callable[[str, str], None],
) -> QTableView:
    """A total for every Technique (down) and Form (across) as a heat map,
    the higher the deeper its colour; choosing a cell calls `on_choose`
    with its Technique and Form. The Casting Scores and the Lab Totals."""
    values = list(totals.values())
    low, high = min(values), max(values)
    model = QStandardItemModel(len(TECHNIQUES), len(FORMS))
    for column, form in enumerate(FORMS):
        head = QStandardItem(ART_ABBREVIATIONS[form])
        head.setIcon(
            QIcon(pictures.pixmap(artwork.art_symbol(form), p["foreground"], 20, 2.0))
        )
        head.setToolTip(form)
        model.setHorizontalHeaderItem(column, head)
    for row, technique in enumerate(TECHNIQUES):
        head = QStandardItem(technique)
        head.setIcon(
            QIcon(
                pictures.pixmap(artwork.art_symbol(technique), p["foreground"], 20, 2.0)
            )
        )
        model.setVerticalHeaderItem(row, head)
        for column, form in enumerate(FORMS):
            total = totals[technique, form]
            heat = (total - low) / max(high - low, 1)
            cell = QStandardItem(str(total))
            cell.setEditable(False)
            cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.setBackground(
                QBrush(mix(p["surface"], p["primary"], 0.08 + 0.62 * heat))
            )
            cell.setForeground(
                QBrush(QColor(p["background"] if heat > 0.55 else p["foreground"]))
            )
            font = QFont(pictures.UI)
            font.setPointSizeF(11)
            font.setBold(heat > 0.55)
            cell.setFont(font)
            cell.setToolTip(f"{technique} {form}: {total}")
            model.setItem(row, column, cell)
    view = QTableView()
    view.setModel(model)
    view.setIconSize(QSize(20, 20))
    view.setShowGrid(False)
    view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    view.verticalHeader().setDefaultSectionSize(34)
    view.verticalHeader().setFont(serif(12, italic=True))
    table_style(view, p)
    view.setFixedHeight(
        34 * len(TECHNIQUES) + view.horizontalHeader().sizeHint().height() + 4
    )
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.clicked.connect(
        lambda index: on_choose(TECHNIQUES[index.row()], FORMS[index.column()])
    )
    return view


def cells_table(
    columns: list[str],
    rows: list[list[str]],
    p: Palette,
    on_choose: Callable[[int], None],
) -> QTableView:
    """Rows of plain cells under their column titles, every row shown (the
    chapter scrolls, not the table); choosing a row calls `on_choose` with
    its index. The first column stretches; a column of numbers is centred."""
    model = QStandardItemModel(len(rows), len(columns))
    for c, title in enumerate(columns):
        head = QStandardItem(title)
        if c == 0:
            head.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
        model.setHorizontalHeaderItem(c, head)
    numeric = [
        bool(rows)
        and all(row[c].lstrip("+-").isdigit() or row[c] in ("", "-") for row in rows)
        for c in range(len(columns))
    ]
    for r, row in enumerate(rows):
        for c, words in enumerate(row):
            cell = QStandardItem(words)
            cell.setEditable(False)
            if numeric[c]:
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if c == 0:
                cell.setFont(serif(12.5))
            model.setItem(r, c, cell)
    view = QTableView()
    view.setModel(model)
    view.verticalHeader().hide()
    view.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)
    view.setShowGrid(False)
    view.setAlternatingRowColors(True)
    view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    header = view.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    table_style(view, p)
    view.setFixedHeight(
        max(len(rows), 1) * ROW_HEIGHT
        + header.sizeHint().height()
        + 2 * view.frameWidth()
        + 2
    )
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.selectionModel().currentRowChanged.connect(
        lambda current, _previous: on_choose(current.row())
    )
    return view


#: A level filter left at "any".
ANY_LEVEL = -1


def filter_choice(blank: str, options: Sequence[tuple[str, object]]) -> QComboBox:
    """A filter's drop-down: `blank` (no filter) first, then `options` as
    (label, value)."""
    combo = QComboBox()
    combo.addItem(blank, None)
    for label, value in options:
        combo.addItem(label, value)
    return combo


def level_box(prefix: str) -> QSpinBox:
    """A filter's level: ANY_LEVEL (shown "`prefix`: any") for none."""
    spin = QSpinBox()
    spin.setRange(ANY_LEVEL, 100)
    spin.setSingleStep(5)
    spin.setValue(ANY_LEVEL)
    spin.setSpecialValueText(f"{prefix}: any")
    spin.setPrefix(f"{prefix}: ")
    return spin
