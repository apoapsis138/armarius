"""The desktop sheet's building blocks: headings, cards, pips,
the experience bar the tables draw, and the inspector, with the printer's
ornaments (ornaments.py) a book sets around them.

Colours always come from the palette, so a widget is rebuilt (not
restyled) when the theme changes.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from PySide6.QtCore import (
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPointF,
    QRectF,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QPixmap,
    QResizeEvent,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractButton,
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
from ..arts import ART_ABBREVIATIONS, ARTS, FORMS, TECHNIQUES
from ..tables import Table
from ..tribunal_packages.rhine import gild_tree
from . import marks, motion, pictures, sounds
from .markup_html import cell_style, to_html
from .style import gilding
from .style.ornaments import corner_flourishes
from .style.paper import lift, shade, translucent
from .style.pieces import (
    CARDS_ACROSS,
    Card,
    GiltName,
    badge,
    card_grid,
    chapter_title,
    chip,
    display_name,
    mix,
    scrolling_page,
    serif,
    text,
)
from .themes import HOVER_WASH, WASH, Palette

#: What the app's other modules take from style through here.
__all__ = [
    "CARDS_ACROSS",
    "Card",
    "GiltName",
    "badge",
    "card_grid",
    "chapter_title",
    "chip",
    "display_name",
    "mix",
    "scrolling_page",
    "serif",
    "text",
]

#: The item-data role holding an experience bar's (fraction, text).
XP_BAR = Qt.ItemDataRole.UserRole + 1
#: Where an experience bar that moved since it was last drawn grows from
#: (XpBarDelegate.at of the way to its new length).
XP_FROM = Qt.ItemDataRole.UserRole + 2

#: What the inspector shows beside a title: an SVG symbol, or a picture.
Symbol = Path | QPixmap | None


def edit_button(
    words: str, p: Palette, on_click: Callable[[], None], concept: str = "edit"
) -> QPushButton:
    """A section's button (Edit, Add, Delete...), with its verb's icon."""
    button = QPushButton(pictures.icon(concept, p["label"], 14), f" {words}")
    button.setObjectName("edit")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.clicked.connect(lambda _checked=False: on_click())
    return button


def chip_row(
    label: str, chips: Sequence[tuple[str, bool, Callable[[], None]]], p: Palette
) -> QWidget:
    """A line of chips after an italic `label`: each its words, lit or not,
    and what clicking it does (Ahead's Show, a history's records)."""
    row = QWidget()
    line = QHBoxLayout(row)
    line.setContentsMargins(0, 0, 0, 0)
    line.setSpacing(6)
    line.addWidget(text(label, p["label"], serif(11, italic=True)))
    for words, lit, on_click in chips:
        chip = chip_button(words, p["heading"] if lit else p["label"], on_click)
        chip.setCheckable(True)
        chip.setChecked(lit)
        line.addWidget(chip)
    line.addStretch(1)
    return row


class ToggleSwitch(QAbstractButton):
    """A small drawn switch, on or off: a tradition offered or not. Greyed
    out while disabled."""

    def __init__(self, on: bool, p: Palette, on_click: Callable[[], None]) -> None:
        super().__init__()
        self.p = p
        self.setCheckable(True)
        self.setChecked(on)
        self.setFixedSize(34, 18)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda _checked=False: on_click())

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QColor(self.p["text-success" if self.isChecked() else "dim"])
        if not self.isEnabled():
            track.setAlpha(90)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track)
        painter.drawRoundedRect(QRectF(0, 1, 34, 16), 8, 8)
        painter.setBrush(QColor(self.p["background"]))
        painter.drawEllipse(QRectF(20 if self.isChecked() else 2, 3, 12, 12))


def chip_button(
    words: str, colour: str, on_click: Callable[[], None], *, filled: str = ""
) -> QPushButton:
    """An outlined pill, as `chip` draws, that does something when clicked
    (a book's In play); `filled`, the words' colour on a pill filled with
    `colour` (a tradition the saga offers)."""
    button = QPushButton(words)
    button.setObjectName("chip")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setStyleSheet(
        f"color:{filled or colour}; border:1px solid {colour}; border-radius:9px;"
        f" padding:1px 10px; background:{colour if filled else 'transparent'}"
    )
    button.clicked.connect(lambda _checked=False: on_click())
    return button


class NewCard(QFrame):
    """A blank card at the end of a list of cards, which makes one more:
    a dashed gilt outline with the kind's icon, faint, and what it makes
    in italics."""

    def __init__(
        self,
        words: str,
        concept: str,
        p: Palette,
        on_click: Callable[[], None],
        hint: str = "",
    ) -> None:
        super().__init__()
        self.words = words
        self.on_click = on_click
        self.setObjectName("newCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(hint or words)
        self.setStyleSheet(
            f"QFrame#newCard {{ background:transparent;"
            f" border:1.5px dashed {p['accent']}; border-radius:6px; }}"
            f" QFrame#newCard:hover {{ background:{translucent(p['surface'], 160)}; }}"
            " QFrame#newCard QLabel { background:transparent; border:none; }"
        )
        self.setMinimumHeight(64)
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(10)
        symbol = QLabel()
        symbol.setPixmap(pictures.pixmap(artwork.icon(concept), p["dim"], 28, 2.0))
        row.addWidget(symbol, 0, Qt.AlignmentFlag.AlignVCenter)
        column = QVBoxLayout()
        column.setSpacing(0)
        column.addWidget(text(words, p["label"], serif(13.5, italic=True)))
        if hint:
            column.addWidget(text(hint, p["dim"], serif(11, italic=True), wrap=True))
        row.addLayout(column, 1)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.on_click()
        super().mousePressEvent(event)


class Pips(QWidget):
    """Filled and empty pips, as on a paper sheet."""

    SIZE = 14

    def __init__(self, filled: int, total: int, colour: str) -> None:
        super().__init__()
        self.filled, self.total, self.colour = filled, total, colour
        self.setFixedSize(total * self.SIZE, self.SIZE)
        self.setToolTip(f"{filled} of {total}")

    def paintEvent(self, event: QPaintEvent) -> None:
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
    """Draws cells as usual in rows `height` tall (ROW_HEIGHT unless the
    table's icons need more)."""

    def __init__(self, height: int = ROW_HEIGHT) -> None:
        super().__init__()
        self.height = height

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        size = super().sizeHint(option, index)
        size.setHeight(max(size.height(), self.height))
        return size


class XpBarDelegate(TallRows):
    """Draws a cell's XP_BAR data, (fraction, text), as a scribe would: a
    gilt line inked along a dotted rule as far as the experience reaches,
    ending in a rubric lozenge, with the words in italic after it."""

    def __init__(self, p: Palette, height: int = ROW_HEIGHT) -> None:
        super().__init__(height)
        self.p = p
        #: How far a bar with an XP_FROM has grown to its new length.
        self.at = 1.0

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
        grown_from = index.data(XP_FROM)
        if isinstance(grown_from, float):
            fraction = grown_from + (fraction - grown_from) * self.at
        p = self.p
        cell = QRectF(option.rect).adjusted(8, 0, -8, 0)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(serif(10.5, italic=True))
        room = painter.fontMetrics().horizontalAdvance(words) + 12
        y = cell.center().y()
        start, stop = cell.left(), max(cell.left(), cell.right() - room)
        painter.setPen(QPen(QColor(p["rule"]), 1, Qt.PenStyle.DotLine))
        painter.drawLine(QPointF(start, y), QPointF(stop, y))
        reach = start + (stop - start) * min(max(fraction, 0.0), 1.0)
        if reach > start:
            ink = QPen(QColor(p["accent"]), 2.6)
            ink.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(ink)
            painter.drawLine(QPointF(start, y), QPointF(reach, y))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["heading"]))
        lozenge = QPainterPath(QPointF(reach, y - 3.2))
        lozenge.lineTo(reach + 3.2, y)
        lozenge.lineTo(reach, y + 3.2)
        lozenge.lineTo(reach - 3.2, y)
        lozenge.closeSubpath()
        painter.drawPath(lozenge)
        painter.setPen(QColor(p["label"]))
        painter.drawText(
            QRectF(cell.right() - room + 8, cell.top(), room, cell.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            words,
        )
        painter.restore()


class Spread(QObject):
    """How far the gold wash has spread across a table's newly chosen row
    (0 to 1, from the left), its leaf showing once the wash is most of the
    way. Other chosen rows are washed in full."""

    #: How far the wash spreads before the leaf begins to show.
    LEAF = 0.6

    def __init__(self, view: QAbstractItemView) -> None:
        super().__init__(view)
        self.view = view
        self.chosen = QPersistentModelIndex()
        self.at = 1.0

    def reach(self, index: QModelIndex | QPersistentModelIndex) -> float:
        current = self.view.currentIndex()
        if index.row() != current.row() or index.parent() != current.parent():
            return 1.0
        chosen = QPersistentModelIndex(current.siblingAtColumn(0))
        if chosen != self.chosen:
            self.chosen = chosen
            motion.tween(self, self._spread, motion.QUICK, name="spread")
        return self.at

    def _spread(self, value: float) -> None:
        self.at = value
        self.view.viewport().update()


class RuledRows(QStyledItemDelegate):
    """A table's own delegate (`inner`) with the table ruled as a ledger:
    a hairline under every row and a gilt double rule under a heading,
    the chosen row in a gold wash fading to the right with a leaf in the
    margin before it, and no fill of the platform's own. With a `margin`
    (a table chosen by the row), the first column keeps room for the
    leaf."""

    #: The first column's margin, which the chosen row's leaf sits in.
    MARGIN = 14

    def __init__(
        self,
        inner: QStyledItemDelegate,
        p: Palette,
        *,
        margin: bool = True,
        spread: Spread | None = None,
    ) -> None:
        super().__init__()
        self.inner, self.p, self.spread = inner, p, spread
        self.margin = self.MARGIN if margin else 0

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        size = self.inner.sizeHint(option, index)
        if index.column() == 0:
            size.setWidth(size.width() + self.margin)
        return size

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        p, rect = self.p, QRectF(option.rect)
        state = option.state
        chosen = bool(state & QStyle.StateFlag.State_Selected)
        under = bool(state & QStyle.StateFlag.State_MouseOver)
        heading = not index.flags() & Qt.ItemFlag.ItemIsSelectable
        view = option.widget
        width = view.viewport().width() if isinstance(view, QAbstractItemView) else 0
        reach = 1.0
        if chosen and not heading and self.spread is not None:
            reach = self.spread.reach(index)
        if (chosen or under) and not heading:
            alpha = WASH if chosen else HOVER_WASH
            washed = rect.intersected(
                QRectF(0, rect.top(), max(width, 1) * reach, rect.height())
            )
            painter.fillRect(washed, gilding.wash(p, 0, max(width, 1), alpha))
        plain = QStyleOptionViewItem(option)
        plain.state &= ~(
            QStyle.StateFlag.State_Selected
            | QStyle.StateFlag.State_HasFocus
            | QStyle.StateFlag.State_MouseOver
        )
        if index.column() == 0 and not heading:
            plain.rect = option.rect.adjusted(self.margin, 0, 0, 0)
        self.inner.paint(painter, plain, index)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        leaf = (reach - Spread.LEAF) / (1 - Spread.LEAF)
        if chosen and self.margin and index.column() == 0 and not heading and leaf > 0:
            painter.setOpacity(leaf)
            gilding.margin_leaf(
                painter, rect.left() + 7, rect.center().y(), p["heading"]
            )
            painter.setOpacity(1.0)
        y = rect.bottom() + 0.5
        painter.setPen(QPen(shade(p["rule"], 170), 0.8))
        painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right() + 1, y))
        if heading:
            painter.setPen(QPen(shade(p["accent"], 200), 0.8))
            painter.drawLine(
                QPointF(rect.left(), y - 2.5), QPointF(rect.right() + 1, y - 2.5)
            )
        painter.restore()


class InkingIn(QWidget):
    """Laid over the inspector while a new item inks in: the bare leaf,
    fading away to show the words on it (for the first part of `at`, 0
    to 1), and a band of light crossing the gilt from left to right. It
    takes no clicks."""

    def __init__(self, inspector: QWidget, p: Palette) -> None:
        super().__init__(inspector)
        self.p, self.at = p, 1.0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        rect = QRectF(self.rect())
        bare = 1 - min(1.0, self.at * 1.5)
        if bare > 0:
            painter.setOpacity(bare)
            gilding.gilt_leaf(painter, rect, self.p)
            painter.setOpacity(1.0)
        gilding.sheen(painter, rect, self.at)
        painter.end()


class Inspector(QFrame):
    """The panel beside every chapter that shows what was last chosen: a
    symbol, a title, a line under it and the details (app markup) in the
    serif, on a gilt leaf (gilding.gilt_leaf). A new item inks in."""

    #: How far a new item's title drifts up as it inks in, in pixels.
    DRIFT = 4

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.setObjectName("inspector")
        self.setStyleSheet(
            "QFrame#inspector { background:transparent; border:none; }"
            " QFrame#inspector QLabel { background:transparent; }"
        )
        lift(self, p, blur=24, drop=0)
        self.setMinimumWidth(280)
        column = QVBoxLayout(self)
        column.setContentsMargins(26, 22, 26, 26)
        top = self.top = QHBoxLayout()
        self.action: QWidget | None = None
        self.symbol = QLabel()
        top.addWidget(self.symbol)
        self.title = text("", p["heading"], serif(17, bold=True), wrap=True)
        self.title.setContentsMargins(0, 0, 0, self.DRIFT)
        top.addWidget(self.title, 1)
        column.addLayout(top)
        self.subtitle = text("", p["label"], serif(11.5, italic=True), wrap=True)
        column.addWidget(self.subtitle)
        rule = QFrame()
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background:{p['rule']}")
        column.addWidget(rule)
        self.body = QLabel()
        self.body.setFont(serif(12.5))
        self.body.setTextFormat(Qt.TextFormat.RichText)
        self.body.setWordWrap(True)
        self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(self.body)
        area.setStyleSheet("background:transparent")
        column.addWidget(area, 1)
        self.ink = InkingIn(self, p)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        gilding.gilt_leaf(painter, QRectF(self.rect()), self.p)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.ink.setGeometry(self.rect())

    def _ink_in(self) -> None:
        """The new item inks in on the leaf, its title drifting up a few
        pixels, as a sheen of light crosses the gilt."""
        if not self.isVisible():
            return
        ink = self.ink
        ink.setGeometry(self.rect())

        def step(value: float) -> None:
            ink.at = value
            drift = round(self.DRIFT * (1 - min(1.0, value * 1.5)))
            self.title.setContentsMargins(0, drift, 0, self.DRIFT - drift)
            ink.update()

        ink.show()
        ink.raise_()
        motion.tween(ink, step, motion.SLOW, name="ink", done=ink.hide)

    def show_item(
        self,
        title: str,
        subtitle: str,
        markup: str,
        symbol: Symbol = None,
        action: QWidget | None = None,
    ) -> None:
        """Show an item: `symbol` is an Art's or House's SVG, drawn small in
        the heading colour, or a picture already drawn (an Ability's mark),
        shown at its own size; `action` goes at the top right (a switch)."""
        self._ink_in()
        if self.action is not None:
            self.action.setParent(None)
            self.action.deleteLater()
        self.action = action
        if action is not None:
            self.top.addWidget(action, 0, Qt.AlignmentFlag.AlignTop)
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.subtitle.setVisible(bool(subtitle))
        self.body.setText(to_html(markup, self.p))
        if symbol is None:
            self.symbol.hide()
            return
        if isinstance(symbol, Path):
            symbol = pictures.pixmap(symbol, self.p["heading"], 34, 2.0)
        self.symbol.setPixmap(symbol)
        self.symbol.show()


class ClickableCard(Card):
    """A card that calls `clicked` when clicked, and lights its border
    under the mouse. A `flourished` card (a troupe covenant's) has a gilt
    scroll in each corner."""

    def __init__(
        self,
        p: Palette,
        *,
        pad: int = 12,
        edge: str | None = None,
        flourished: bool = False,
    ) -> None:
        super().__init__(p, pad=pad, edge=edge)
        self.flourished = flourished
        self.clicked: Callable[[], None] = lambda: None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        left = f"border-left:4px solid {edge};" if edge else ""
        self.setStyleSheet(
            self.styleSheet()
            + f" QFrame#card:hover {{ border:1px solid {p['accent']}; {left} }}"
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked()
        super().mousePressEvent(event)

    def set_chosen(self, chosen: bool) -> None:
        """Outline the card as the row its section's Edit and Delete act
        on."""
        self.chosen = chosen
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        if self.flourished:
            painter = QPainter(self)
            corner_flourishes(
                painter, QRectF(self.rect()).adjusted(1, 1, -1, -1), self.p, 16
            )
            painter.end()
        if getattr(self, "chosen", False):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor(self.p["heading"]), 2))
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 6, 6)


class RailRows(QStyledItemDelegate):
    """The chapter rail's rows, the chosen chapter's gold wash spreading
    from the left (its border and colour come from the rail's style)."""

    def __init__(self, rail: QAbstractItemView, p: Palette) -> None:
        super().__init__(rail)
        self.p, self.spread = p, Spread(rail)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if option.state & QStyle.StateFlag.State_Selected:
            rect = QRectF(option.rect)
            reach = self.spread.reach(index)
            washed = QRectF(
                rect.left(), rect.top(), rect.width() * reach, rect.height()
            )
            painter.fillRect(
                washed, gilding.wash(self.p, rect.left(), rect.right(), WASH)
            )
        super().paint(painter, option, index)


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
            " QListWidget#rail::item:selected { background:transparent;"
            f" color:{p['heading']}; border-left:3px solid {p['heading']}; }}"
        )
        self.rail.setItemDelegate(RailRows(self.rail, p))
        self.pages = QStackedWidget()
        #: Chapters not drawn yet, by row: built when first turned to.
        self._later: dict[int, Callable[[], QWidget]] = {}
        self.rail.currentRowChanged.connect(self._turn_to)
        self.rail.currentRowChanged.connect(self._turned)
        self.setHandleWidth(1)
        self.addWidget(self.rail)
        self.addWidget(self.pages)
        self.addWidget(self.inspector)
        self.setStretchFactor(1, 1)
        self.setSizes([180, 900, 340])

    def add(
        self, name: str, concept: str, page: QWidget | Callable[[], QWidget]
    ) -> None:
        """Add a chapter, with its icon (artwork.ICON_NAMES); the first
        one added is shown. A chapter given as a function that builds it
        is built only when first turned to, for one too big to draw
        every time its page opens."""
        if not isinstance(page, QWidget):
            self._later[self.pages.count()] = page
            page = QWidget()
        self.pages.addWidget(page)
        QListWidgetItem(pictures.icon(concept, self.p["label"], 20), name, self.rail)
        if self.rail.count() == 1:
            self.rail.setCurrentRow(0)

    def chapter(self, row: int) -> QWidget:
        """The chapter at `row`, built if it was not yet."""
        build = self._later.pop(row, None)
        page = self.pages.widget(row)
        assert page is not None
        if build is None:
            return page
        built = build()
        self.pages.insertWidget(row, built)
        self.pages.removeWidget(page)
        page.deleteLater()
        return built

    def _turn_to(self, row: int) -> None:
        def turn() -> QWidget | None:
            page = self.chapter(row) if row >= 0 else None
            self.pages.setCurrentIndex(row)
            return page

        motion.turn_page(self.pages, turn)

    def _turned(self, row: int) -> None:
        """A page turned for the chapter chosen (the chest opened for the
        Inventory), once the page is on show."""
        if self.isVisible() and row >= 0:
            name = self.rail.item(row).text()
            sounds.play("chest" if name == "Inventory" else "page")

    def chapters(self) -> list[str]:
        return [self.rail.item(i).text() for i in range(self.rail.count())]

    def open_chapter(self, name: str) -> None:
        self.rail.setCurrentRow(self.chapters().index(name))

    def inspect(
        self,
        title: str,
        subtitle: str,
        markup: str,
        symbol: Symbol = None,
        action: QWidget | None = None,
    ) -> None:
        self.inspector.show_item(title, subtitle, markup, symbol, action)


def table_style(view: QAbstractItemView, p: Palette) -> None:
    """Rule `view` as a ledger: no box, fill or stripes; the column titles
    in small capitals over a gilt double rule; and its delegates wrapped
    in RuledRows, so the rows are ruled and the chosen one washed in gold.
    Called after the view's own delegates are set."""
    view.setAlternatingRowColors(False)
    view.setMouseTracking(True)
    view.setStyleSheet(
        "QAbstractItemView { background:transparent; border:none; outline:0;"
        f" selection-background-color:transparent; selection-color:{p['foreground']}; }}"
        " QHeaderView { background:transparent; border:none; }"
        f" QHeaderView::section {{ background:transparent; color:{p['label']};"
        " border:none; padding:4px 6px; }"
        f" QHeaderView::section:horizontal {{ border-bottom:3px double {p['accent']}; }}"
        " QHeaderView::section:vertical { font-weight:600; }"
        " QTableCornerButton::section { background:transparent; border:none; }"
    )
    for header in (
        getattr(view, "horizontalHeader", None),
        getattr(view, "header", None),
    ):
        if header is not None:
            header().setFont(serif(11.5, caps=True))
    # A table chosen by the row keeps a margin for the chosen row's leaf.
    margin = view.selectionBehavior() == QAbstractItemView.SelectionBehavior.SelectRows
    inner = view.itemDelegate()
    assert isinstance(inner, QStyledItemDelegate)
    spread = Spread(view)
    view.setItemDelegate(RuledRows(inner, p, margin=margin, spread=spread))
    model = view.model()
    for column in range(model.columnCount() if model is not None else 0):
        own = view.itemDelegateForColumn(column)
        if isinstance(own, QStyledItemDelegate) and not isinstance(own, RuledRows):
            view.setItemDelegateForColumn(
                column, RuledRows(own, p, margin=margin, spread=spread)
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
    """Rows of plain cells under their column titles (see table_view)."""
    return table_view(Table(columns, rows), p, on_choose)


def _numeric(words: str) -> bool:
    return words.lstrip("+-").isdigit() or words in ("", "-")


def _table_model(table: Table, p: Palette) -> QStandardItemModel:
    """table_view's cells: each in its markup's style, the numbers
    centred, the headings in rubric."""
    columns, rows = table.columns, table.rows

    def words(cell: str) -> tuple[str, str | None, bool, bool]:
        return cell_style(cell, p) if table.markup else (cell, None, False, False)

    def cell_of(row: list[str], c: int) -> str:
        return row[c] if c < len(row) else ""

    body = [row for r, row in enumerate(rows) if table.key(r) is not None]
    numeric = [
        bool(body) and all(_numeric(words(cell_of(row, c))[0]) for row in body)
        for c in range(len(columns))
    ]
    model = QStandardItemModel(len(rows), len(columns))
    for c, title in enumerate(columns):
        head = QStandardItem(title)
        if not numeric[c]:
            head.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
        model.setHorizontalHeaderItem(c, head)
    for r, row in enumerate(rows):
        heading = table.key(r) is None
        for c in range(len(columns)):
            shown, colour, bold, italic = words(cell_of(row, c))
            cell = QStandardItem(shown)
            cell.setEditable(False)
            font = serif(12.5) if c == 0 else cell.font()
            font.setBold(bold or heading)
            font.setItalic(italic)
            cell.setFont(font)
            if colour is not None:
                cell.setForeground(QBrush(QColor(colour)))
            if heading:
                cell.setFlags(Qt.ItemFlag.ItemIsEnabled)
                cell.setForeground(QBrush(QColor(colour or p["heading"])))
            elif numeric[c]:
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            elif columns[c] == "Art" and shown.title() in ARTS:
                cell.setIcon(art_icon(shown.title(), p))
            elif columns[c] == "Gild" and (tree := gild_tree(shown)) is not None:
                cell.setIcon(QIcon(marks.gild_pixmap(tree, p["foreground"], 18)))
            model.setItem(r, c, cell)
    return model


def art_icon(art: str, p: Palette) -> QIcon:
    """An Art's symbol, the size of a table's text."""
    return QIcon(pictures.pixmap(artwork.art_symbol(art), p["foreground"], 18, 2.0))


def table_view(
    table: Table, p: Palette, on_choose: Callable[[int], None]
) -> QTableView:
    """The core's table, every row shown (the chapter scrolls, not the
    table); choosing a row calls `on_choose` with its key. The first
    column is set in the serif and the table's `stretch` column takes the
    spare room; a column of numbers is centred, the others start at the
    left, and an Art column shows each Art's symbol (a Gild column, each
    gild's). A markup cell takes
    its tags' colour, bold and italics; a heading row is bold in rubric
    colour, its first cell across the row when it has no others, and
    can't be chosen."""
    rows = table.rows
    view = QTableView()
    view.setModel(_table_model(table, p))
    for r, row in enumerate(rows):
        if table.key(r) is None and not any(row[1:]):
            view.setSpan(r, 0, 1, len(table.columns))
    view.verticalHeader().hide()
    view.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)
    view.setShowGrid(False)
    view.setAlternatingRowColors(True)
    view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    header = view.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(table.stretch, QHeaderView.ResizeMode.Stretch)
    table_style(view, p)
    view.setFixedHeight(
        max(len(rows), 1) * ROW_HEIGHT
        + header.sizeHint().height()
        + 2 * view.frameWidth()
        + 2
    )
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def chosen(current: QModelIndex, _previous: QModelIndex) -> None:
        key = table.key(current.row()) if current.isValid() else None
        if key is not None:
            on_choose(key)

    view.selectionModel().currentRowChanged.connect(chosen)
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
