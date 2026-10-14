"""What a record's page draws to manage the record itself: its Manage
chapter (Export, Update from a File, Delete: the record as a file rather
than as part of the saga) and, in its header, the In Creation / In Play
toggle with the Creation Worksheet beside it.

The chapter is built from the core's list of what the record offers
(menu_forms.manage_items), as each sheet is built from the core's text.
Moving between the modes changes the page's palette (themes.for_mode);
`fade_from` cross-fades the window from how it looked before.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import menu_forms
from ..commands import Command
from ..menu_forms import DELETE_RECORD, Page
from ..models import Character, Covenant, Laboratory
from . import pictures
from .markup_html import plain
from .themes import Palette
from .widgets import chapter_title, edit_button, scrolling_page, serif, text

#: Runs a command, then (once its last step is answered) `then` instead
#: of drawing the page again.
RunThen = Callable[[Command, Callable[[], None] | None], None]

#: A record with an In Creation / In Play mode.
Moded = Character | Covenant | Laboratory

#: The icon of each entry of the Manage chapter (artwork.ICON_NAMES).
ICONS: dict[str, str] = {
    "export_record": "export",
    "update_record": "update",
    DELETE_RECORD: "delete",
}

#: How long the palette takes to change between the modes, in ms.
FADE = 450


@dataclass(frozen=True)
class RecordControls:
    """The window's side of a record's page: the page as the core's
    menus see it, how to run a command, where to go once the record is
    deleted, how to change its mode and how to open its worksheet."""

    page: Page
    run: RunThen
    up: Callable[[], None]
    toggle_mode: Callable[[Moded], None]
    worksheet: Callable[[str], None]

    def chapter(self, p: Palette) -> QWidget:
        return manage_chapter(self, p)

    def mode(self, p: Palette) -> QWidget | None:
        record = self.page.creation_record()
        if record is None:
            return None
        return ModeToggle(record, p, self.toggle_mode, self.worksheet)


def manage_chapter(controls: RecordControls, p: Palette) -> QWidget:
    """A button and a line on what it does for each of the core's Manage
    entries; Delete last, set apart, in the warning colour."""
    page = controls.page
    grid_box = QWidget()
    grid = QGridLayout(grid_box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(16)
    grid.setVerticalSpacing(14)
    grid.setColumnStretch(1, 1)
    for row, item in enumerate(menu_forms.manage_items(page)):
        deleting = item.action == DELETE_RECORD
        then = controls.up if deleting else None

        def go(action: str = item.action, then=then) -> None:
            controls.run(menu_forms.command(page, action), then)

        button = edit_button(plain(item.label), p, go, ICONS[item.action])
        if deleting:
            button.setIcon(pictures.icon("delete", p["text-error"], 16))
            button.setStyleSheet(
                f"color:{p['text-error']}; border-color:{p['text-error']}"
            )
            if row:
                grid.addWidget(rule(p), 2 * row - 1, 0, 1, 2)
        button.setToolTip(plain(item.label))
        grid.addWidget(button, 2 * row, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(
            text(item.detail, p["label"], serif(12.5, italic=True), wrap=True),
            2 * row,
            1,
        )
    return scrolling_page(p, chapter_title("Manage", p), grid_box)


def rule(p: Palette) -> QWidget:
    """A thin line between the record's files and its Delete."""
    line = QLabel()
    line.setFixedHeight(1)
    line.setStyleSheet(f"background:{p['rule']}")
    return line


class ModeToggle(QWidget):
    """The record's mode, quietly, in its header: a quill while it is In
    Creation, a seal In Play; clicking moves it to the other (the core
    asks first). While it is In Creation, its Creation Worksheet is a
    click away beside it."""

    def __init__(
        self,
        record: Moded,
        p: Palette,
        toggle: Callable[[Moded], None],
        worksheet: Callable[[str], None],
    ) -> None:
        super().__init__()
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(2)
        creating = record.in_creation
        self.switch = QPushButton(
            pictures.icon("in_creation" if creating else "in_play", p["label"], 16),
            " In Creation" if creating else " In Play",
        )
        self.switch.setObjectName("crumb")
        self.switch.setFlat(True)
        self.switch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.switch.setToolTip(
            "Move to In Play" if creating else "Move back to In Creation"
        )
        self.switch.clicked.connect(lambda _checked=False: toggle(record))
        column.addWidget(self.switch, 0, Qt.AlignmentFlag.AlignRight)
        self.worksheet: QPushButton | None = None
        if creating:
            self.worksheet = QPushButton(
                pictures.icon("worksheet", p["label"], 16), " Worksheet"
            )
            self.worksheet.setObjectName("crumb")
            self.worksheet.setFlat(True)
            self.worksheet.setCursor(Qt.CursorShape.PointingHandCursor)
            self.worksheet.setToolTip("Open the Creation Worksheet")
            self.worksheet.clicked.connect(lambda _checked=False: worksheet(record.id))
            column.addWidget(self.worksheet, 0, Qt.AlignmentFlag.AlignRight)
        column.addStretch(1)


def fade_from(host: QWidget, before: QPixmap, ms: int = FADE) -> QLabel:
    """Lay `before` (how `host` looked) over `host` and fade it away, so
    `host` seems to change into its new colours."""
    cover = QLabel(host)
    cover.setPixmap(before)
    cover.setGeometry(host.rect())
    cover.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    effect = QGraphicsOpacityEffect(cover)
    cover.setGraphicsEffect(effect)
    fade = QPropertyAnimation(effect, b"opacity", cover)
    fade.setDuration(ms)
    fade.setStartValue(1.0)
    fade.setEndValue(0.0)
    fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
    fade.finished.connect(cover.deleteLater)
    cover.show()
    cover.raise_()
    fade.start()
    return cover
