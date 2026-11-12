"""The desktop sheet's building blocks: headings, cards, pips,
the experience bar the tables draw, and the inspector, with the printer's
ornaments (ornaments.py) a book sets around them.

Colours always come from the palette, so a widget is rebuilt (not
restyled) when the theme changes.
"""

from __future__ import annotations

import weakref
from collections.abc import Callable, Sequence
from pathlib import Path

from PySide6.QtCore import (
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
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
    QLayout,
    QLayoutItem,
    QListView,
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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import artwork, seat, viewing
from ..arts import ART_ABBREVIATIONS, ARTS, FORMS, TECHNIQUES
from ..tables import Table
from ..tribunal_packages.rhine import gild_tree
from . import marks, motion, pictures, sounds
from .markup_html import cell_style, struck, to_html
from .style import gilding, liveries
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
    tier_badge,
)
from .style.pieces import heading as heading_font
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
    "tier_badge",
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


def changing_button(
    words: str, p: Palette, on_click: Callable[[], None], concept: str = "edit"
) -> QPushButton:
    """An edit_button that changes the record its page is of: not shown
    where whoever sits here may not change that record (seat.read_only)."""
    button = edit_button(words, p, on_click, concept)
    if seat.read_only():
        button.hide()
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


class FlowLayout(QLayout):
    """Items left to right, starting a new row when the next one won't
    fit the width: a row of seals that wraps instead of widening the page.
    Its height follows its width, so the page around it grows downward."""

    def __init__(self, parent: QWidget | None = None, spacing: int = 4) -> None:
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self.setSpacing(spacing)

    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> QLayoutItem | None:
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index: int) -> QLayoutItem | None:
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._place(QRect(0, 0, width, 0), move=False)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._place(rect, move=True)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        # As narrow as its widest item: never wider, so it never widens
        # the page around it.
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _place(self, rect: QRect, move: bool) -> int:
        """Lay the items out in `rect` (only measuring unless `move`), and
        return the height they take."""
        area = rect.marginsRemoved(self.contentsMargins())
        x, y, line = area.x(), area.y(), 0
        gap = self.spacing()
        for item in self._items:
            hint = item.sizeHint()
            if x > area.x() and x + hint.width() > area.right() + 1:
                x, y, line = area.x(), y + line + gap, 0
            if move:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x += hint.width() + gap
            line = max(line, hint.height())
        return y + line - rect.y() + self.contentsMargins().bottom()


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
#: The widest a table's column (but its stretching one) grows, in pixels.
WIDEST_COLUMN = 320
#: Marks a table's total row (Table.footed), for RuledRows to rule it off.
FOOT_ROLE = Qt.ItemDataRole.UserRole + 7


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
        if index.data(FOOT_ROLE):
            # A total: a double rule above it, as a ledger closes a column.
            painter.setPen(QPen(QColor(p["accent"]), 0.9))
            for top in (rect.top() + 0.5, rect.top() + 3.5):
                painter.drawLine(
                    QPointF(rect.left(), top), QPointF(rect.right() + 1, top)
                )
        y = rect.bottom() + 0.5
        painter.setPen(QPen(shade(p["rule"], 170), 0.8))
        painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right() + 1, y))
        if heading:
            painter.setPen(QPen(shade(p["accent"], 200), 0.8))
            painter.drawLine(
                QPointF(rect.left(), y - 2.5), QPointF(rect.right() + 1, y - 2.5)
            )
        painter.restore()


class TitledRows(QStyledItemDelegate):
    """A list's rows as a ledger's two columns: what comes before a row's
    first ": " in rubric, the rest ruled up beside it in ink. A list whose
    rows aren't all written so shows them whole. Wrap in RuledRows."""

    SEPARATOR = ": "
    #: The gap between the two columns, and the height added to a row.
    GAP, AIR = 14, 8

    def __init__(self, view: QAbstractItemView, p: Palette) -> None:
        super().__init__(view)
        self.p = p
        #: Where the second column starts: 0 while the rows have no titles.
        self.column = 0

    def measure(self, rows: list[str]) -> None:
        """Set the second column from `rows`, as they are about to show."""
        self.column = 0
        if rows and all(self.SEPARATOR in row for row in rows):
            metrics = QFontMetrics(serif(12.5, bold=True))
            self.column = self.GAP + max(
                metrics.horizontalAdvance(row.partition(self.SEPARATOR)[0])
                for row in rows
            )

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        size = super().sizeHint(option, index)
        return QSize(size.width(), QFontMetrics(serif(12.5)).height() + self.AIR)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        words = str(index.data())
        rect = option.rect.adjusted(2, 0, -2, 0)
        flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        painter.save()
        painter.setFont(serif(12.5))
        painter.setPen(QColor(self.p["foreground"]))
        if self.column:
            title, _, rest = words.partition(self.SEPARATOR)
            room = rect.adjusted(self.column, 0, 0, 0)
            rest = QFontMetrics(painter.font()).elidedText(
                rest, Qt.TextElideMode.ElideRight, room.width()
            )
            painter.drawText(room, flags, rest)
            painter.setFont(serif(12.5, bold=True))
            painter.setPen(QColor(self.p["heading"]))
            words = title
        painter.drawText(rect, flags, words)
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
        self.title = text("", p["heading"], heading_font(17, p), wrap=True)
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
        words = QWidget()
        self.under = QVBoxLayout(words)
        self.under.setContentsMargins(0, 0, 0, 0)
        self.under.addWidget(self.body)
        self.under.addStretch(1)
        #: What `show_item` put under the words.
        self.extra: QWidget | None = None
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(words)
        area.setStyleSheet("background:transparent")
        column.addWidget(area, 1)
        self.ink = InkingIn(self, p)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        gilding.gilt_leaf(painter, QRectF(self.rect()), self.p)
        # A House theme's mark, watermarked faintly at the leaf's foot.
        liveries.look(self.p).inspector_mark(
            painter, QRectF(self.rect()).adjusted(14, 14, -14, -14), self.p
        )
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
        extra: QWidget | None = None,
    ) -> None:
        """Show an item: `symbol` is an Art's or House's SVG, drawn small in
        the heading colour, or a picture already drawn (an Ability's mark),
        shown at its own size; `action` goes at the top right (a switch),
        and `extra` under the words (pictures of the choices)."""
        self._ink_in()
        if self.extra is not None:
            self.extra.setParent(None)
            self.extra.deleteLater()
        self.extra = extra
        if extra is not None:
            self.under.insertWidget(1, extra)
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


#: A widget that shows a list a Find Spot names, and how to choose a
#: record's row in it (offer_rows).
_ROW_CHOOSERS: weakref.WeakKeyDictionary[
    QWidget, tuple[str, Callable[[str], QWidget | None]]
] = weakref.WeakKeyDictionary()


def offer_rows[W: QWidget](
    widget: W, listed: str, choose: Callable[[str], QWidget | None]
) -> W:
    """Let Codex.choose_row choose a row of `widget`, which shows the
    `listed` list (saga_index.BOOKS, DEVICES, SPELLS): `choose` takes a
    record's id, chooses its row as a click would, and returns what to
    bring into view, or None when the record isn't there."""
    _ROW_CHOOSERS[widget] = (listed, choose)
    return widget


def choose_key(view: QTableView, table: Table, key: int | None) -> QWidget | None:
    """Choose the row of a table_view whose key is `key`; the view, or
    None when no row has it."""
    row = next(
        (r for r in range(len(table.rows)) if key is not None and table.key(r) == key),
        None,
    )
    if row is None:
        return None
    view.selectRow(row)
    return view


#: The room between the rail's foot (the season's panel) and the rule
#: beside the rail.
FOOT_GAP = 14


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
        # A long chapter name beside the rail's scroll bar (when the season's
        # panel leaves it too short for every chapter) is cut short, never
        # scrolled sideways.
        self.rail.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        #: The rail, with room at its foot for what the window puts there
        #: (the season's panel: set_foot).
        self.side = QWidget()
        self.side.setFixedWidth(180)
        column = self._side = QVBoxLayout(self.side)
        column.setContentsMargins(0, 0, 0, 12)
        column.setSpacing(8)
        column.addWidget(self.rail, 1)
        self.foot: QWidget | None = None
        self.addWidget(self.side)
        self.addWidget(self.pages)
        self.addWidget(self.inspector)
        self.setStretchFactor(1, 1)
        self.setSizes([180, 900, 340])

    def add(
        self,
        name: str,
        concept: str,
        page: QWidget | Callable[[], QWidget],
        part: str = "",
    ) -> None:
        """Add a chapter, with its icon (artwork.ICON_NAMES); the first
        one added is shown. A chapter given as a function that builds it
        is built only when first turned to, for one too big to draw
        every time its page opens. `part` is the chapter's id where only
        the storyguide may read it (viewing.STORYGUIDE_ONLY): left out
        for anyone else."""
        if part and not viewing.reads(part=part):
            if isinstance(page, QWidget):
                page.deleteLater()
            return
        if not isinstance(page, QWidget):
            self._later[self.pages.count()] = page
            page = QWidget()
        self.pages.addWidget(page)
        QListWidgetItem(pictures.icon(concept, self.p["label"], 20), name, self.rail)
        if self.rail.count() == 1:
            self.rail.setCurrentRow(0)

    def set_foot(self, widget: QWidget) -> None:
        """Put `widget` at the foot of the rail, in place of any there."""
        column = self._side
        if self.foot is not None:
            # Deleting it takes it out of its row.
            self.foot.deleteLater()
        self.foot = widget
        # Clear of the rule beside the rail, as the chapters' text is.
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, FOOT_GAP, 0)
        row.addWidget(widget)
        column.addLayout(row)

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

    def choose_row(self, listed: str, record_id: str) -> bool:
        """Choose `record_id`'s row of the `listed` list on the chapter on
        show (offer_rows), and scroll it into view; False when the
        chapter hasn't it."""
        row = self.rail.currentRow()
        if row < 0:
            return False
        chapter = self.chapter(row)
        for widget in (chapter, *chapter.findChildren(QWidget)):
            offered = _ROW_CHOOSERS.get(widget)
            if offered is None or offered[0] != listed:
                continue
            shown = offered[1](record_id)
            if shown is None:
                continue
            scroll = shown.parentWidget()
            while scroll is not None and not isinstance(scroll, QScrollArea):
                scroll = None if scroll is chapter else scroll.parentWidget()
            if scroll is not None:
                scroll.ensureWidgetVisible(shown)
            return True
        return False

    def open_chapter(self, name: str) -> None:
        self.rail.setCurrentRow(self.chapters().index(name))

    def inspect(
        self,
        title: str,
        subtitle: str,
        markup: str,
        symbol: Symbol = None,
        action: QWidget | None = None,
        extra: QWidget | None = None,
    ) -> None:
        self.inspector.show_item(title, subtitle, markup, symbol, action, extra)


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
    # A list has one column, and no delegates of its own to wrap.
    wrapped = model is not None and not isinstance(view, QListView)
    for column in range(model.columnCount() if wrapped else 0):
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
            font.setStrikeOut(table.markup and struck(cell_of(row, c)))
            cell.setFont(font)
            if table.footed and r == len(rows) - 1:
                cell.setData(True, FOOT_ROLE)
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
    table_style(view, p)
    # Each column as wide as its words, up to a cap, so one long cell (a
    # gild's whole membership) can't push the table past its page: what
    # is cut ends in an ellipsis, and the inspector shows the row in full.
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    view.setTextElideMode(Qt.TextElideMode.ElideRight)
    view.resizeColumnsToContents()
    for column in range(len(table.columns)):
        if column != table.stretch and view.columnWidth(column) > WIDEST_COLUMN:
            view.setColumnWidth(column, WIDEST_COLUMN)
    header.setSectionResizeMode(table.stretch, QHeaderView.ResizeMode.Stretch)
    rows_height = (
        max(len(rows), 1) * ROW_HEIGHT
        + header.sizeHint().height()
        + 2 * view.frameWidth()
        + 2
    )
    view.setFixedHeight(rows_height)
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def make_room(_least: int, most: int) -> None:
        # A table wider than its page scrolls sideways: its scroll bar
        # takes room of its own instead of hiding the last row.
        scroll_bar = view.horizontalScrollBar()
        view.setFixedHeight(
            rows_height + (scroll_bar.sizeHint().height() if most else 0)
        )

    view.horizontalScrollBar().rangeChanged.connect(make_room)

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


def ledger_table(columns: list[str], p: Palette) -> QTableWidget:
    """A ledger whose rows are refilled as data changes (fill_ledger) and
    chosen one at a time by id (ledger_choice), in the body serif: the
    app's style sheet sets a bare table in its display face. The core's
    fixed tables are table_view's instead."""
    table = QTableWidget(0, len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.verticalHeader().hide()
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    # The columns share the window's width and a long entry wraps, so a
    # narrow window never scrolls sideways.
    table.setWordWrap(True)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    table.setFont(serif(13))
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    table_style(table, p)
    return table


def fill_ledger(table: QTableWidget, rows: list[tuple[str, list[str]]]) -> None:
    """Put `rows` (an id, then each column's words) in `table`, keeping the
    chosen row chosen when it is still there, else choosing the first."""
    chosen = ledger_choice(table)
    table.setRowCount(len(rows))
    for row, (row_id, cells) in enumerate(rows):
        for column, words in enumerate(cells):
            item = QTableWidgetItem(words)
            item.setData(Qt.ItemDataRole.UserRole, row_id)
            table.setItem(row, column, item)
    ids = [row_id for row_id, _ in rows]
    if ids:
        table.selectRow(ids.index(chosen) if chosen in ids else 0)


def ledger_choice(table: QTableWidget) -> str | None:
    """The id of the row chosen, if any."""
    row = table.currentRow()
    item = table.item(row, 0) if row >= 0 else None
    return None if item is None else str(item.data(Qt.ItemDataRole.UserRole))
