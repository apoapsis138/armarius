"""Find: the top bar's magnifier, and the panel it drops, to open any
record of the saga by its name.

The panel is a popup under the Find button, right-aligned to it, with a
field over the matches: each keystroke asks the core's index
(saga_index.search) again and redraws the list (Observer: the field's
textChanged is the only thing that fills it). Up and Down choose a
match, Enter or a click opens it, and Esc or a click outside closes the
panel, as a menu closes. It is never on show otherwise."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import (
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPoint,
    QPointF,
    QRectF,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QIcon,
    QKeyEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from .. import saga_index
from ..models import Saga
from ..style.palettes import Palette

#: How many matches the panel lists; more are counted under the list.
SHOWN = 60
#: The panel's width, and the rows it is tall before it scrolls.
WIDTH = 460
ROWS = 10
#: The width of the red rule along the panel's top.
TOP_RULE = 3


def magnifier_icon(colour: str, size: int = 20, ratio: float = 2.0) -> QIcon:
    """A reading glass drawn in `colour`: a ring with a short handle down
    to the right."""
    side = round(size * ratio)
    picture = QPixmap(side, side)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(side / 20, side / 20)
    pen = QPen(QColor(colour), 1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QPointF(8.5, 8.5), 5.5, 5.5)
    pen.setWidthF(2.6)
    painter.setPen(pen)
    painter.drawLine(QPointF(12.6, 12.6), QPointF(17.2, 17.2))
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return QIcon(picture)


def eye_icon(colour: str, size: int = 20, ratio: float = 2.0) -> QIcon:
    """An eye drawn in `colour`, for Player view: two arcs meeting at the
    corners, and the iris filled."""
    side = round(size * ratio)
    picture = QPixmap(side, side)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(side / 20, side / 20)
    pen = QPen(QColor(colour), 1.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    outline = QPainterPath(QPointF(2, 10))
    outline.quadTo(QPointF(10, 2), QPointF(18, 10))
    outline.quadTo(QPointF(10, 18), QPointF(2, 10))
    painter.drawPath(outline)
    painter.setBrush(QColor(colour))
    painter.drawEllipse(QPointF(10, 10), 2.6, 2.6)
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return QIcon(picture)


#: The role a row keeps its kind and place in, drawn dim after its name.
_AFTER = Qt.ItemDataRole.UserRole + 1
#: The role a row keeps the entry it opens in.
_REF = Qt.ItemDataRole.UserRole


@dataclass(frozen=True)
class RowLayout:
    """Where a match's name and its kind and place go across a row, from
    its left edge, and the text each shows (elided to fit)."""

    name: str
    name_x: int
    name_width: int
    after: str
    after_x: int
    after_width: int


def row_layout(
    name_metrics: QFontMetrics,
    after_metrics: QFontMetrics,
    width: int,
    name: str,
    after: str,
) -> RowLayout:
    """The name at the left, whole; its kind and place right-aligned after
    a gap of two ems, cut short with "…" when the row is too narrow. Only
    a name wider than the whole row is itself cut short, and then nothing
    follows it."""
    name_width = name_metrics.horizontalAdvance(name)
    if name_width >= width or not after:
        shown = name_metrics.elidedText(name, Qt.TextElideMode.ElideRight, width)
        return RowLayout(shown, 0, min(name_width, width), "", width, 0)
    gap = 2 * name_metrics.horizontalAdvance("M")
    room = width - name_width - gap
    shown = after_metrics.elidedText(after, Qt.TextElideMode.ElideRight, max(room, 0))
    if room <= 0 or shown in ("", "…"):
        return RowLayout(name, 0, name_width, "", width, 0)
    return RowLayout(name, 0, name_width, shown, name_width + gap, room)


class _MatchRow(QStyledItemDelegate):
    """A match: its name, then its kind and place (and why it matched) in
    the dim ink, italic and right-aligned (row_layout), on the selection's
    wash when chosen."""

    def __init__(self, p: Palette, parent: QWidget) -> None:
        super().__init__(parent)
        self.p = p

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        rect = option.rect
        state = option.state
        painter.save()
        if state & QStyle.StateFlag.State_Selected:
            painter.fillRect(rect, QColor(self.p["selection"]))
            painter.fillRect(
                rect.x(), rect.y(), 3, rect.height(), QColor(self.p["primary"])
            )
        painter.setFont(QFont(option.font))
        name_font = painter.font()
        after_font = QFont(name_font)
        after_font.setItalic(True)
        text = rect.adjusted(12, 0, -10, 0)
        row = row_layout(
            QFontMetrics(name_font, painter.device()),
            QFontMetrics(after_font, painter.device()),
            text.width(),
            str(index.data(Qt.ItemDataRole.DisplayRole) or ""),
            str(index.data(_AFTER) or ""),
        )
        align = Qt.AlignmentFlag.AlignVCenter
        painter.setPen(QColor(self.p["foreground"]))
        painter.drawText(
            QRectF(text.x() + row.name_x, text.y(), row.name_width, text.height()),
            align | Qt.AlignmentFlag.AlignLeft,
            row.name,
        )
        if row.after:
            painter.setFont(after_font)
            painter.setPen(QColor(self.p["dim"]))
            painter.drawText(
                QRectF(
                    text.x() + row.after_x, text.y(), row.after_width, text.height()
                ),
                align | Qt.AlignmentFlag.AlignRight,
                row.after,
            )
        painter.restore()


class FinderPanel(QFrame):
    """The panel Find drops: the field, the matches, and a line saying how
    many more there are. `opens` is called with the chosen match's Ref,
    after the panel has closed."""

    def __init__(
        self,
        saga: Saga,
        p: Palette,
        opens: Callable[[saga_index.Entry], None],
        parent: QWidget,
    ) -> None:
        super().__init__(parent, Qt.WindowType.Popup)
        self.setObjectName("finder")
        self.p = p
        self._opens = opens
        #: The saga's records, listed once when the panel opens.
        self._entries = saga_index.entries(saga)
        self.setFixedWidth(WIDTH)
        self.setAutoFillBackground(True)
        self.setStyleSheet(
            f"#finder {{ background: {p['surface']}; border: 1px solid {p['rule']};"
            f" border-top: none; }}"
            f"#finder QListWidget {{ background: transparent; border: none; }}"
            f"#finder QLabel {{ color: {p['dim']}; }}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10 + TOP_RULE, 10, 8)
        layout.setSpacing(6)
        self.field = QLineEdit()
        self.field.setPlaceholderText("A name, a place or a Tribunal")
        self.field.setAccessibleName("Find")
        self.field.setClearButtonEnabled(True)
        self.field.addAction(
            magnifier_icon(p["dim"], 16), QLineEdit.ActionPosition.LeadingPosition
        )
        self.field.textChanged.connect(self._fill)
        self.field.installEventFilter(self)
        layout.addWidget(self.field)
        self.matches = QListWidget()
        self.matches.setAccessibleName("Matches")
        self.matches.setItemDelegate(_MatchRow(p, self.matches))
        self.matches.setUniformItemSizes(True)
        self.matches.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.matches.itemClicked.connect(self._open_item)
        row = QFontMetrics(self.font()).height() + 10
        self._row = row
        layout.addWidget(self.matches)
        self.more = QLabel()
        self.more.setWordWrap(True)
        layout.addWidget(self.more)
        self._fill("")

    # -- the list, from the index --

    def _fill(self, text: str) -> None:
        found = saga_index.search(self._entries, text)
        self.matches.clear()
        for match in found[:SHOWN]:
            entry = match.entry
            after = saga_index.SEPARATOR.join(p for p in (entry.kind, entry.place) if p)
            if match.note:
                after += f"  ({match.note})"
            item = QListWidgetItem(entry.name)
            item.setData(_AFTER, after)
            item.setData(_REF, entry)
            item.setSizeHint(QSize(0, self._row))
            item.setToolTip(entry.line)
            self.matches.addItem(item)
        if found:
            self.matches.setCurrentRow(0)
        rest = len(found) - SHOWN
        if not found:
            self.more.setText("No record has that name." if text.strip() else "")
        elif rest > 0:
            self.more.setText(f"{rest} more: type more of the name to narrow them.")
        else:
            self.more.setText("")
        self.more.setVisible(bool(self.more.text()))
        shown = min(max(self.matches.count(), 1), ROWS)
        self.matches.setFixedHeight(shown * self._row + 4)
        self.matches.setVisible(bool(found))
        self.adjustSize()

    def shown(self) -> list[str]:
        """The names listed, in order."""
        return [self.matches.item(n).text() for n in range(self.matches.count())]

    # -- choosing and opening --

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            watched is self.field
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and self._key(event)
        ):
            return True
        return super().eventFilter(watched, event)

    def _key(self, event: QKeyEvent) -> bool:
        """Up, Down, Page Up/Down, Enter and Esc in the field."""
        key = event.key()
        steps = {
            Qt.Key.Key_Up: -1,
            Qt.Key.Key_Down: 1,
            Qt.Key.Key_PageUp: -ROWS,
            Qt.Key.Key_PageDown: ROWS,
        }
        if key in steps and self.matches.count():
            row = self.matches.currentRow() + steps[Qt.Key(key)]
            self.matches.setCurrentRow(max(0, min(row, self.matches.count() - 1)))
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = self.matches.currentItem()
            if item is not None:
                self._open_item(item)
            return True
        if key == Qt.Key.Key_Escape:
            self.close()
            return True
        return False

    def _open_item(self, item: QListWidgetItem) -> None:
        found = item.data(_REF)
        self.close()
        if isinstance(found, saga_index.Entry):
            self._opens(found)

    def drop_under(self, button: QWidget) -> None:
        """Show the panel just under `button`, its right edge on the
        button's, and put the cursor in its field."""
        self.adjustSize()
        corner = button.mapToGlobal(QPoint(button.width(), button.height()))
        left = corner.x() - self.width()
        screen = button.screen()
        if screen is not None:
            # Kept on the screen when the window is narrow or near its edge.
            left = max(left, screen.availableGeometry().left())
        self.move(left, corner.y())
        self.show()
        self.field.setFocus()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), TOP_RULE, QColor(self.p["primary"]))
        painter.end()
