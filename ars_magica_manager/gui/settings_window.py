"""The Settings window the title bar's gear opens: the theme the desktop
is drawn in, the sounds and Reduce Motion.

It stays open beside the page without blocking it. The theme is chosen in
a selector over the registry (style.liveries.THEMES): closed, it shows the
theme in use, its small page sample with its House's mark, its name and a
few words under it; open, every theme so drawn under its group's heading,
Scriptorum's two first. Choosing one applies it at once, with nothing to
confirm, and with the selector closed the arrow keys step from theme to
theme, each applied as it is reached. One delegate draws a row in both the
closed box and the list. The window decides nothing itself: it calls back
to the main window, which applies the theme and remembers it.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

from . import motion, pictures, sounds
from .choices import OwnRows, paint_choice
from .forms import Sheet
from .style.frame import CLOSE
from .style.liveries import GROUPS, THEMES, Theme
from .style.pieces import heading as heading_font
from .style.pieces import serif, text
from .themes import Palette

TITLE = "Settings"
#: A sample's size, in pixels, as a theme's row shows it.
SAMPLE = QSize(72, 44)
#: The data role a theme's row keeps its theme's name under.
NAME_ROLE = Qt.ItemDataRole.UserRole
#: The heights of a theme's row and of a group's heading, in pixels.
ROW_HEIGHT, HEADING_HEIGHT = 56, 28


def sample(theme: Theme, ratio: float = 2.0) -> QPixmap:
    """A small picture of `theme`'s page: its paper, a heading in its
    heading colour over a rule, two lines of ink, and its House's mark."""
    p = theme.palette
    width, height = SAMPLE.width(), SAMPLE.height()
    picture = QPixmap(round(width * ratio), round(height * ratio))
    picture.setDevicePixelRatio(ratio)
    picture.fill(QColor(p["background"]))
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(p["accent"]), 1))
    painter.drawRect(QRectF(0.5, 0.5, width - 1, height - 1))
    heading = QFont(pictures.SERIF)
    heading.setPixelSize(13)
    heading.setBold(True)
    painter.setFont(heading)
    painter.setPen(QColor(p["heading"]))
    painter.drawText(QRectF(6, 3, width - 12, 16), "Aa")
    painter.setPen(QPen(QColor(p["rule"]), 1))
    painter.drawLine(6, 20, width - 6, 20)
    painter.setPen(QPen(QColor(p["foreground"]), 1.6))
    painter.drawLine(6, 27, width - 24, 27)
    painter.drawLine(6, 34, width - 32, 34)
    if theme.mark is not None:
        side = 18
        mark = pictures.pixmap(theme.mark, p["heading"], side, ratio)
        painter.drawPixmap(round(width - side - 4), 3, mark)
    painter.end()
    return picture


def _theme_model(current: Theme) -> tuple[QStandardItemModel, int]:
    """The selector's rows: each group's heading (which can't be chosen),
    then its themes, each with its sample; and the row of `current`."""
    model = QStandardItemModel()
    at = 0
    for group in GROUPS:
        members = [theme for theme in THEMES if theme.group == group]
        if not members:
            continue
        heading = QStandardItem(group)
        heading.setFlags(Qt.ItemFlag.NoItemFlags)
        model.appendRow(heading)
        for theme in members:
            row = QStandardItem(theme.name)
            row.setData(theme.name, NAME_ROLE)
            row.setData(theme.blurb, Qt.ItemDataRole.ToolTipRole)
            row.setData(QPixmap(sample(theme)), Qt.ItemDataRole.DecorationRole)
            row.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            model.appendRow(row)
            if theme.name == current.name:
                at = model.rowCount() - 1
    return model, at


class ThemeRow(QStyledItemDelegate):
    """Draws a row of the theme selector, in the closed box and in its
    list: a theme's sample, its name, and its few words under the name
    in a quieter ink, cut short if they don't fit; or a group's heading,
    in italics, which can't be chosen."""

    def __init__(self, p: Palette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.p = p

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        heading = not index.flags() & Qt.ItemFlag.ItemIsSelectable
        return QSize(320, HEADING_HEIGHT if heading else ROW_HEIGHT)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.draw(painter, QRectF(option.rect), index, option.state)

    def draw(
        self,
        painter: QPainter,
        rect: QRectF,
        index: QModelIndex | QPersistentModelIndex,
        state: QStyle.StateFlag = QStyle.StateFlag.State_None,
    ) -> None:
        """Draw `index`'s row filling `rect` (highlighted when `state`
        says it is under the pointer or chosen in the list)."""
        p = self.p
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not index.flags() & Qt.ItemFlag.ItemIsSelectable:
            painter.setFont(serif(12.5, italic=True))
            painter.setPen(QColor(p["label"]))
            painter.drawText(
                rect.adjusted(10, 0, -10, 0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                str(index.data()),
            )
            painter.restore()
            return
        if state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver):
            painter.fillRect(rect, QColor(p["selection"]))
        picture = index.data(Qt.ItemDataRole.DecorationRole)
        left = rect.left() + 8
        if isinstance(picture, QPixmap):
            top = rect.top() + (rect.height() - SAMPLE.height()) / 2
            painter.drawPixmap(round(left), round(top), picture)
            left += SAMPLE.width() + 10
        words = rect.adjusted(left - rect.left(), 0, -8, 0)
        name, blurb = serif(12.5), serif(11, italic=True)
        name_height = QFontMetrics(name).height()
        blurb_height = QFontMetrics(blurb).height()
        top = words.top() + (words.height() - name_height - blurb_height) / 2
        painter.setFont(name)
        painter.setPen(QColor(p["foreground"]))
        painter.drawText(
            QRectF(words.left(), top, words.width(), name_height),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            str(index.data()),
        )
        painter.setFont(blurb)
        painter.setPen(QColor(p["label"]))
        few = QFontMetrics(blurb).elidedText(
            str(index.data(Qt.ItemDataRole.ToolTipRole) or ""),
            Qt.TextElideMode.ElideRight,
            round(words.width()),
        )
        painter.drawText(
            QRectF(words.left(), top + name_height, words.width(), blurb_height),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            few,
        )
        painter.restore()


class ThemeSelector(OwnRows):
    """A drop-down drawn as the app's inked blank (choices.py), whose
    closed blank shows its chosen theme's row as the list does
    (ThemeRow): sample, name and words."""

    def __init__(self, row: ThemeRow, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.row = row
        self.setItemDelegate(row)
        self.setMinimumHeight(ROW_HEIGHT + 8)

    def sizeHint(self) -> QSize:
        return QSize(super().sizeHint().width(), ROW_HEIGHT + 8)

    def paint_choice_row(self, painter: QPainter, room: QRectF) -> None:
        index = self.model().index(self.currentIndex(), 0)
        if index.isValid():
            self.row.draw(painter, room, index)

    def paintEvent(self, event: QPaintEvent) -> None:
        # Where the app's drop-down painter isn't installed, the same blank.
        painter = QPainter(self)
        paint_choice(painter, self, self.row.p)
        painter.end()


class SettingsWindow(Sheet):
    """The Settings window (see the module's docstring). `choose` applies
    a theme by name; `current` is the one in use."""

    controls = (CLOSE,)

    def __init__(
        self,
        p: Palette,
        current: Theme,
        choose: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(TITLE, p, "Close", parent)
        self.setModal(False)
        self.choose = choose
        self.column.addWidget(text("Theme", p["heading"], heading_font(14, p)))
        self.column.addWidget(
            text(
                "The look the app is drawn in. Choose one to see it at once; "
                "with the box chosen, the arrow keys step from theme to theme.",
                p["label"],
                serif(12, italic=True),
                wrap=True,
            )
        )
        self.themes = ThemeSelector(ThemeRow(p))
        self.themes.setAccessibleName("Theme")
        model, at = _theme_model(current)
        self.themes.setModel(model)
        self.themes.setCurrentIndex(at)
        # Tall enough to show most of the themes without scrolling.
        self.themes.setMaxVisibleItems(12)
        self.themes.currentIndexChanged.connect(self._picked)
        self.column.addWidget(self.themes)
        self.column.addSpacing(6)
        self.column.addWidget(
            text("Sound and motion", p["heading"], heading_font(14, p))
        )
        self.sounds = QCheckBox("Sounds")
        self.sounds.setToolTip("Sounds for moments that mean something")
        self.sounds.setChecked(sounds.enabled())
        self.sounds.toggled.connect(self._sounds)
        self.column.addWidget(self.sounds)
        self.motion = QCheckBox("Reduce motion")
        self.motion.setToolTip(
            "Still the pages' small movements, the dial and the seal"
        )
        self.motion.setChecked(motion.reduced())
        self.motion.toggled.connect(motion.set_reduced)
        self.column.addWidget(self.motion)
        self.column.addStretch(1)
        self.save.clicked.connect(self.close)
        self.cancel.hide()
        self.finish()
        self.resize(480, self.sizeHint().height())
        # Drawn again in a new theme as the arrows step through them, the
        # window keeps the selector ready for the next step.
        self.themes.setFocus()

    def chosen(self) -> str | None:
        """The name of the theme chosen in the selector."""
        name = self.themes.currentData(NAME_ROLE)
        return name if isinstance(name, str) else None

    def names(self) -> list[str | None]:
        """Each row's theme name in the selector, top to bottom; None for
        a group's heading."""
        model = self.themes.model()
        return [model.index(i, 0).data(NAME_ROLE) for i in range(model.rowCount())]

    def pick(self, name: str) -> None:
        """Choose the theme called `name` in the selector (as a click does)."""
        at = self.themes.findData(name, NAME_ROLE)
        if at >= 0:
            self.themes.setCurrentIndex(at)

    def _picked(self, at: int) -> None:
        name = self.themes.itemData(at, NAME_ROLE)
        if isinstance(name, str):
            self.choose(name)

    def _sounds(self, on: bool) -> None:
        sounds.set_enabled(on)
        sounds.play("page")
