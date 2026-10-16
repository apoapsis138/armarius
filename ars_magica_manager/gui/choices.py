"""Every drop-down drawn as a blank in a manuscript: its choice in italic
on a dotted line, a murex-purple silk bookmark hanging at its right; and
its open list as a slip of paper ruled in ink, a purple margin rule down
its left and the chosen line washed in purple, fading to the right. A
spin box is the same blank, with two small purple steps for its arrows.

The purple is murex, the dye of royal books, and is kept apart from the
rubric's red and the gilt, which stay with headings and selections.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QModelIndex, QObject, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionSpinBox,
    QStyleOptionViewItem,
    QWidget,
)

from .paper import shade
from .themes import Palette, murex

#: A row of an open list, and where its margin rule runs.
ROW_HEIGHT, MARGIN = 28, 18
#: How strongly the chosen line's wash starts, and a line under the pointer's.
CHOSEN_WASH, HOVER_WASH = 75, 22
#: Room at a drop-down's right for its bookmark.
RIBBON_ROOM = 26


def _wash(colour: str, left: float, right: float, alpha: int) -> QLinearGradient:
    gradient = QLinearGradient(left, 0, right, 0)
    gradient.setColorAt(0, shade(colour, alpha))
    gradient.setColorAt(1, shade(colour, 0))
    return gradient


def paint_ribbon(
    painter: QPainter, x: float, top: float, bottom: float, colour: str
) -> None:
    """A silk bookmark 12 wide hanging from `top` to `bottom` at `x`, its
    end cut in a swallowtail, lit down its middle as silk is."""
    path = QPainterPath(QPointF(x, top))
    path.lineTo(x + 12, top)
    path.lineTo(x + 12, bottom)
    path.lineTo(x + 6, bottom - 5)
    path.lineTo(x, bottom)
    path.closeSubpath()
    silk = QLinearGradient(x, 0, x + 12, 0)
    base = QColor(colour)
    silk.setColorAt(0, base.darker(125))
    silk.setColorAt(0.5, base.lighter(115))
    silk.setColorAt(1, base.darker(125))
    painter.fillPath(path, QBrush(silk))


def _lively(widget: QWidget) -> bool:
    return widget.hasFocus() or widget.underMouse()


def paint_blank(painter: QPainter, widget: QWidget, right: float, p: Palette) -> None:
    """The dotted line a blank's words sit on, from `widget`'s left to
    `right`: solid purple while it has focus or the pointer."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    box = QRectF(widget.rect()).adjusted(1, 1, -1, -1)
    lively = _lively(widget)
    line = box.bottom() - 3
    pen = QPen(QColor(murex(p)) if lively else shade(p["label"], 200), 1.2)
    if not lively:
        pen.setStyle(Qt.PenStyle.DotLine)
    painter.setPen(pen)
    painter.drawLine(QPointF(box.left(), line), QPointF(right, line))


def paint_choice(painter: QPainter, combo: QComboBox, p: Palette) -> None:
    """A closed drop-down: its choice in italic on a dotted line (solid
    purple while it has focus or the pointer), its bookmark at its right."""
    box = QRectF(combo.rect()).adjusted(1, 1, -1, -1)
    purple = murex(p)
    lively = _lively(combo)
    paint_blank(painter, combo, box.right() - RIBBON_ROOM, p)
    font = combo.font()
    painter.setFont(font)
    if not combo.isEnabled():
        colour = p["dim"]
    elif combo.objectName() == "quiet" and not lively:
        colour = p["label"]
    else:
        colour = p["foreground"]
    painter.setPen(QColor(colour))
    room = box.adjusted(5, 0, -RIBBON_ROOM - 4, -5)
    words = QFontMetricsF(font).elidedText(
        combo.currentText(), Qt.TextElideMode.ElideRight, room.width()
    )
    painter.drawText(
        room, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, words
    )
    paint_ribbon(painter, box.right() - 17, box.top(), box.bottom() + 1, purple)


def _step(painter: QPainter, centre: QPointF, up: bool, colour: QColor) -> None:
    """A small solid triangle pointing up or down."""
    tip, base = (-3.0, 2.0) if up else (3.0, -2.0)
    path = QPainterPath(QPointF(centre.x() - 4, centre.y() + base))
    path.lineTo(centre.x() + 4, centre.y() + base)
    path.lineTo(centre.x(), centre.y() + tip)
    path.closeSubpath()
    painter.fillPath(path, colour)


def paint_spin(painter: QPainter, spin: QAbstractSpinBox, p: Palette) -> None:
    """A spin box as a blank: the dotted line under its number (which its
    own line edit draws), and its arrows as two small purple steps, faint
    at the end of its range."""
    option = QStyleOptionSpinBox()
    spin.initStyleOption(option)
    style = spin.style()
    complex_ = QStyle.ComplexControl.CC_SpinBox
    up = QRectF(
        style.subControlRect(complex_, option, QStyle.SubControl.SC_SpinBoxUp, spin)
    )
    down = QRectF(
        style.subControlRect(complex_, option, QStyle.SubControl.SC_SpinBoxDown, spin)
    )
    paint_blank(painter, spin, min(up.left(), down.left()) - 4, p)
    enabled = spin.stepEnabled()
    purple = murex(p)
    for rect, flag, pointing_up in (
        (up, QAbstractSpinBox.StepEnabledFlag.StepUpEnabled, True),
        (down, QAbstractSpinBox.StepEnabledFlag.StepDownEnabled, False),
    ):
        on = spin.isEnabled() and bool(enabled & flag)
        colour = QColor(purple) if on else shade(purple, 80)
        _step(painter, rect.center(), pointing_up, colour)


class InkSlipRows(QStyledItemDelegate):
    """Draws an open drop-down's lines: the purple margin rule down each,
    the chosen line washed in purple and the one under the pointer more
    faintly, the words in the book face."""

    def __init__(self, combo: QComboBox, choices: InkedChoices) -> None:
        super().__init__(combo)
        self.combo, self.choices = combo, choices

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        hint = super().sizeHint(option, index)
        return QSize(hint.width() + MARGIN + 16, max(hint.height(), ROW_HEIGHT))

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        p = self.choices.p
        purple = murex(p)
        row = QRectF(option.rect)  # type: ignore[attr-defined]
        state = option.state  # type: ignore[attr-defined]
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = row.left() + MARGIN
        chosen = index.row() == self.combo.currentIndex()
        under = bool(
            state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver)
        )
        if chosen or under:
            band = QRectF(margin, row.top(), row.right() - 4 - margin, row.height())
            alpha = CHOSEN_WASH if chosen else HOVER_WASH
            painter.fillRect(band, _wash(purple, band.left(), band.right(), alpha))
        painter.setPen(QPen(QColor(purple), 0.9))
        painter.drawLine(QPointF(margin, row.top()), QPointF(margin, row.bottom() + 1))
        # Upright, though the closed drop-down's choice is italic.
        font = QFont(option.font)  # type: ignore[attr-defined]
        font.setItalic(False)
        painter.setFont(font)
        painter.setPen(QColor(p["foreground"]))
        painter.drawText(
            row.adjusted(MARGIN + 10, 0, -6, 0),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            str(index.data() or ""),
        )
        painter.restore()


class InkedChoices(QObject):
    """Draws every drop-down and spin box in the application as an inked
    blank and rules a drop-down's open list, in the palette `p` (set again when the theme
    changes). The window's style sheet still sizes them; this only paints
    them, as gilding.GiltRods paints the scroll bars."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if isinstance(watched, QComboBox) and not watched.isEditable():
            paint = paint_choice
        elif isinstance(watched, QAbstractSpinBox):
            paint = paint_spin
        else:
            return False
        kind = event.type()
        if kind == QEvent.Type.Paint:
            painter = QPainter(watched)
            paint(painter, watched, self.p)  # type: ignore[arg-type]
            painter.end()
            return True
        if kind == QEvent.Type.Polish and isinstance(watched, QComboBox):
            self.rule(watched)
        elif kind in (
            QEvent.Type.Enter,
            QEvent.Type.Leave,
            QEvent.Type.FocusIn,
            QEvent.Type.FocusOut,
        ):
            watched.update()
        return False

    def rule(self, combo: QComboBox) -> None:
        """Give `combo`'s open list its ruled lines, once."""
        if not isinstance(combo.itemDelegate(), InkSlipRows):
            combo.setItemDelegate(InkSlipRows(combo, self))
            combo.view().setMouseTracking(True)


_choices: InkedChoices | None = None


def ink_choices(app: QApplication, p: Palette) -> None:
    """Draw every drop-down and spin box in `app` as an inked blank, in
    palette `p`."""
    global _choices
    if _choices is None:
        _choices = InkedChoices(p)
        app.installEventFilter(_choices)
    _choices.p = p
    for widget in app.allWidgets():
        if isinstance(widget, QComboBox) and not widget.isEditable():
            _choices.rule(widget)
            widget.update()
        elif isinstance(widget, QAbstractSpinBox):
            widget.update()
