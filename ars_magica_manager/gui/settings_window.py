"""The Settings window the title bar's gear opens: the theme the desktop
is drawn in, the sounds and Reduce Motion.

It stays open beside the page without blocking it. The themes are listed
from the registry (style.liveries.THEMES) under their groups, Scriptorum's
two first, each with a small sample of its page and its House's mark;
choosing one applies it at once, with nothing to confirm. The window
decides nothing itself: it calls back to the main window, which applies
the theme and remembers it.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QWidget,
)

from . import motion, pictures, sounds
from .forms import Sheet
from .style.frame import CLOSE
from .style.liveries import GROUPS, THEMES, Theme
from .style.pieces import heading as heading_font
from .style.pieces import serif, text
from .themes import Palette

TITLE = "Settings"
#: A sample's size, in pixels, as the list shows it.
SAMPLE = QSize(72, 44)
#: The data role a theme's row keeps its theme's name under.
NAME_ROLE = Qt.ItemDataRole.UserRole


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
                "The look the app is drawn in. Choose one to see it at once.",
                p["label"],
                serif(12, italic=True),
                wrap=True,
            )
        )
        self.themes = QListWidget()
        self.themes.setIconSize(SAMPLE)
        # A long description wraps under its name rather than scroll.
        self.themes.setWordWrap(True)
        self.themes.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.themes.setAccessibleName("Theme")
        self._fill(p, current)
        self.themes.currentItemChanged.connect(self._picked)
        self.column.addWidget(self.themes, 1)
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
        self.save.clicked.connect(self.close)
        self.cancel.hide()
        self.finish()
        self.resize(480, 720)

    def _fill(self, p: Palette, current: Theme) -> None:
        """The themes under their groups' headings; `current` chosen."""
        for group in GROUPS:
            members = [theme for theme in THEMES if theme.group == group]
            if not members:
                continue
            heading = QListWidgetItem(group)
            heading.setFlags(Qt.ItemFlag.NoItemFlags)
            heading.setFont(serif(12.5, italic=True))
            heading.setForeground(QColor(p["label"]))
            self.themes.addItem(heading)
            for theme in members:
                row = QListWidgetItem(
                    QIcon(sample(theme)), f"{theme.name}\n{theme.blurb}"
                )
                row.setData(NAME_ROLE, theme.name)
                row.setFont(serif(12.5))
                row.setToolTip(theme.blurb)
                self.themes.addItem(row)
                if theme.name == current.name:
                    self.themes.setCurrentItem(row)

    def chosen(self) -> str | None:
        """The name of the theme chosen in the list."""
        row = self.themes.currentItem()
        return None if row is None else row.data(NAME_ROLE)

    def pick(self, name: str) -> None:
        """Choose the theme called `name` in the list (as a click does)."""
        for i in range(self.themes.count()):
            row = self.themes.item(i)
            if row.data(NAME_ROLE) == name:
                self.themes.setCurrentItem(row)
                return

    def _picked(self, row: QListWidgetItem | None, _before: object) -> None:
        name = None if row is None else row.data(NAME_ROLE)
        if isinstance(name, str):
            self.choose(name)

    def _sounds(self, on: bool) -> None:
        sounds.set_enabled(on)
        sounds.play("page")
