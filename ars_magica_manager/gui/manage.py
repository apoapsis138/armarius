"""What a record's page draws to manage the record itself: its Manage
chapter (Export, Update from a File, Print to PDF, Delete: the record as a
file rather than as part of the saga) and, in its header, the In Creation / In Play
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

from .. import menu_forms, world
from ..commands import Command
from ..menu_forms import DELETE_RECORD, Page
from ..models import FULL, Character, Covenant, Laboratory
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

#: Print to PDF: the desktop's own, as only it draws the page for paper.
PRINT = "Print to PDF"
PRINT_DETAIL = (
    "Lay the record out for paper and save it as a PDF to print or send: "
    "choose US Letter or A4, and for a character short or full spells and a "
    "parchment or plain white page."
)

#: How long the palette takes to change between the modes, in ms.
FADE = 450


@dataclass(frozen=True)
class RecordControls:
    """The window's side of a record's page: the page as the core's
    menus see it, how to run a command, where to go once the record is
    deleted, how to change its mode, how to open its worksheet and how to
    print it."""

    page: Page
    run: RunThen
    up: Callable[[], None]
    toggle_mode: Callable[[Moded], None]
    worksheet: Callable[[str], None]
    print_pdf: Callable[[], None] | None = None

    def chapter(self, p: Palette) -> QWidget:
        return manage_chapter(self, p)

    def mode(self, p: Palette) -> QWidget | None:
        record = self.page.creation_record()
        if record is None or getattr(record, "detail", FULL) != FULL:
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
    entries: list[tuple[str, str, str, Callable[[], None]]] = []
    for item in menu_forms.manage_items(page):
        then = controls.up if item.action == DELETE_RECORD else None
        if item.action == "promote":
            then = _worksheet_once_creating(controls)
        entries.append(
            (
                item.action,
                plain(item.label),
                item.detail,
                _runs(controls, item.action, then),
            )
        )
    if controls.print_pdf is not None:
        at = len(entries) - (entries[-1][0] == DELETE_RECORD if entries else 0)
        entries.insert(at, ("print", PRINT, PRINT_DETAIL, controls.print_pdf))
    for row, (action, label, detail, go) in enumerate(entries):
        deleting = action == DELETE_RECORD
        button = edit_button(label, p, go, ICONS.get(action, "export"))
        if deleting:
            button.setIcon(pictures.icon("delete", p["text-error"], 16))
            button.setStyleSheet(
                f"color:{p['text-error']}; border-color:{p['text-error']}"
            )
            if row:
                grid.addWidget(rule(p), 2 * row - 1, 0, 1, 2)
        button.setToolTip(label)
        grid.addWidget(button, 2 * row, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(
            text(detail, p["label"], serif(12.5, italic=True), wrap=True),
            2 * row,
            1,
        )
    return scrolling_page(p, chapter_title("Manage", p), grid_box)


def _runs(
    controls: RecordControls, action: str, then: Callable[[], None] | None
) -> Callable[[], None]:
    """Run the Manage entry `action`, then `then` (or draw the page again)."""
    return lambda: controls.run(menu_forms.command(controls.page, action), then)


def _worksheet_once_creating(controls: RecordControls) -> Callable[[], None] | None:
    """After Promote: a sketch promoted to Full is In Creation, and its
    Creation Worksheet opens on what it already has; any other promotion
    draws the page again (None)."""
    record = controls.page.creation_record()
    if record is None or world.promoted(getattr(record, "detail", FULL)) != FULL:
        return None
    return lambda: controls.worksheet(record.id)


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
