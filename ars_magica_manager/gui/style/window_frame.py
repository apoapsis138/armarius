"""Window: the frame every window the desktop opens over the main window
is built on (docs/adr/0033). No system title bar but the app's own
(frame.py): the app's name to drag it by and the glyph buttons its
`controls` name, grips when it can maximise, Windows' snapping, and an
opening size fitted to the screen. Inside, the theme's paper and a column
for a subclass to fill, with a heading over the hedera rule to put at its
top (Template Method: the frame is the same skeleton for every window,
and each kind fills in its body).
"""

from __future__ import annotations

import shiboken6
from PySide6.QtCore import QByteArray, QEvent, Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...markup import plain
from ...paths import APP_NAME
from ...style.palettes import Palette
from . import snapping
from .families import DIALOG
from .frame import (
    CLOSE,
    MAXIMISE,
    DragStrip,
    Grips,
    WindowButtons,
    keep_on_screen,
    native_frame_event,
)
from .ornaments import FleuronRule
from .paper import Paper
from .pieces import text
from .pieces import title as title_font


class _Page(Paper):
    """A window's sheet of paper, framed in its theme's look: in
    Scriptorum ruled round its edge, with a flourish in each corner."""

    def __init__(self, p: Palette) -> None:
        super().__init__(p, DIALOG)


#: The windows closed and waiting for Qt to delete them (Window.exec).
_closed: list[QDialog] = []


class Window(QDialog):
    """A window on paper over the page, wearing the app's title bar in
    place of the system's; its contents go in `column`."""

    #: The title bar's buttons; a window that can maximise also resizes.
    controls: tuple[str, ...] = (MAXIMISE, CLOSE)

    def __init__(
        self,
        title: str,
        p: Palette,
        parent: QWidget | None,
        *,
        as_written: bool = False,
    ) -> None:
        """`title` is the app's markup, read as plain words; one
        `as_written` (a record's own words) is kept as it is, brackets
        and all, here and in the window's heading (add_heading)."""
        super().__init__(parent)
        self.as_written = as_written
        self.setWindowTitle(title if as_written else plain(title))
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.p = p
        page = self.page = _Page(p)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(page)
        body = QVBoxLayout(page)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addLayout(self._title_bar())
        self.column = QVBoxLayout()
        self.column.setSpacing(8)
        self.column.setContentsMargins(26, 6, 26, 18)
        body.addLayout(self.column, 1)

    def add_heading(self, title: str) -> QLabel:
        """Put `title` as a heading over a hedera rule in the column; in a
        window whose title is `as_written` (a record's own words), it keeps
        its brackets, is never read as HTML, and wraps, so a long one never
        widens its window."""
        words = title if self.as_written else plain(title)
        heading = text(
            words, self.p["heading"], title_font(17, self.p), wrap=self.as_written
        )
        if self.as_written:
            heading.setTextFormat(Qt.TextFormat.PlainText)
        self.column.addWidget(heading)
        self.column.addWidget(FleuronRule(self.p))
        return heading

    def head_room(self) -> int:
        """The height the bar and what is in the column so far take: what
        a viewer sized for its body (put in after its heading) grows by."""
        layout = self.page.layout()
        assert layout is not None
        return layout.sizeHint().height()

    def add_close_row(self) -> QHBoxLayout:
        """A row of buttons at the foot of the column, ending in Close
        (which accepts); a viewer's other buttons go in front of it."""
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.close_button)
        self.column.addLayout(row)
        return row

    def exec(self) -> int:
        """Show the window and wait. exec() hands a dialog to Python, away
        from its parent, and a window refers to itself, so the collector
        would free it with the buttons it holds and delete them twice: it
        is kept in `_closed` until Qt has deleted it, which is safe. What
        it holds can still be read until the event loop next runs."""
        _closed[:] = [window for window in _closed if shiboken6.isValid(window)]
        result = super().exec()
        _closed.append(self)
        self.deleteLater()
        return result

    def _title_bar(self) -> QHBoxLayout:
        """The app's name in the middle (drag it to move the window) and
        the window's own buttons, as the main window has."""
        maximises = MAXIMISE in self.controls
        bar = QHBoxLayout()
        bar.setContentsMargins(12, 4, 8, 0)
        self.drag = DragStrip(self, self.p, APP_NAME, maximises)
        bar.addWidget(self.drag, 1)
        self.window_buttons = WindowButtons(self, self.p, kinds=self.controls)
        bar.addWidget(self.window_buttons, 0, Qt.AlignmentFlag.AlignTop)
        if maximises:
            self.grips = Grips(self)
        return bar

    def showEvent(self, event: QShowEvent) -> None:
        """Every window opens fitted to its screen, where Qt put it (over
        the window it was opened from): a window sized for a large screen
        would otherwise run off a small or highly scaled one."""
        snapping.make_snappable(self)
        if not self.isMaximized():
            keep_on_screen(self)
        super().showEvent(event)

    def nativeEvent(
        self, eventType: QByteArray | bytes | bytearray | memoryview, message: int
    ) -> tuple[bool, int]:
        """Fills the screen's work area when maximised (snapping.py)."""
        result = native_frame_event(self, eventType, message)
        if result is not None:
            return True, result
        return super().nativeEvent(eventType, message)  # pyright: ignore[reportReturnType]

    def changeEvent(self, event: QEvent) -> None:
        """Maximise turns to restore (and back) as the window does."""
        if event.type() == QEvent.Type.WindowStateChange:
            snapping.make_snappable(self)
            if MAXIMISE in self.controls:
                button = self.window_buttons.buttons[MAXIMISE]
                button.update()
                button.setToolTip("Restore" if self.isMaximized() else "Maximise")
        super().changeEvent(event)
