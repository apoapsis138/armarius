"""The windows' own frame, in place of the system's title bar: the
minimise, maximise and close glyphs drawn on the paper, a strip that
moves the window (a double-click maximises it), and thin grips along the
edges and corners that resize it. A window opens fitted to its screen
(fit_to_screen), since with no system title bar one that ran off the
screen couldn't be moved back.

Moving and resizing go through the system (QWindow.startSystemMove and
startSystemResize), and snapping.py gives the window back the styles
Windows snaps by, so it still snaps to the screen's edges and halves.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QByteArray,
    QEvent,
    QObject,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
)
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import (
    QAbstractButton,
    QHBoxLayout,
    QWidget,
)

from ...style import fonts
from ...style.palettes import Palette
from . import snapping

MINIMISE, MAXIMISE, CLOSE = "minimise", "maximise", "close"
#: The width of a resizing grip along an edge, in pixels.
GRIP = 6
#: The height of the strip that moves the window over the title page.
STRIP = 40
#: The most of a screen's free area a window opens over, so a large
#: window on a small or highly scaled screen still shows its edges.
SCREEN_SHARE = 0.9


def native_frame_event(
    window: QWidget,
    event_type: QByteArray | bytes | bytearray | memoryview,
    message: int,
) -> int | None:
    """`window`'s answer to a native message for its drawn title bar
    (snapping.py), or None to leave it to Qt."""
    raw = event_type.data() if isinstance(event_type, QByteArray) else event_type
    return snapping.native_event(window, bytes(raw), int(message))


def fitted(
    available: QRect, size: QSize, least: QSize, centre: QPoint | None = None
) -> QRect | None:
    """Where a window `size` big goes in a screen's free area `available`:
    no bigger than SCREEN_SHARE of it (but never under `least`, its
    minimum), centred on `centre` (else on the area) and kept inside it.
    None when even `least` won't fit, so the window should fill the
    screen instead."""
    if least.width() > available.width() or least.height() > available.height():
        return None
    width = min(size.width(), int(available.width() * SCREEN_SHARE))
    height = min(size.height(), int(available.height() * SCREEN_SHARE))
    place = QRect(0, 0, max(width, least.width()), max(height, least.height()))
    place.moveCenter(available.center() if centre is None else centre)
    left = min(place.left(), available.right() + 1 - place.width())
    top = min(place.top(), available.bottom() + 1 - place.height())
    place.moveTopLeft(QPoint(max(left, available.left()), max(top, available.top())))
    return place


def _least(window: QWidget) -> QSize:
    """The smallest `window`'s contents can be laid out in."""
    layout = window.layout()
    if layout is not None:
        layout.activate()
    return window.minimumSizeHint().expandedTo(window.minimumSize())


def fit_to_screen(
    window: QWidget, width: int, height: int, *, keep_centre: bool = False
) -> None:
    """Size `window` to `width` x `height`, shrunk to fit its screen
    (fitted), centred on the screen, or where it is now with
    `keep_centre`. A window whose contents can't fit is maximised, its
    restored size the whole free area."""
    available = window.screen().availableGeometry()
    centre = window.geometry().center() if keep_centre else None
    place = fitted(available, QSize(width, height), _least(window), centre)
    if place is None:
        window.setGeometry(available)
        window.setWindowState(window.windowState() | Qt.WindowState.WindowMaximized)
        return
    window.setGeometry(place)


def keep_on_screen(window: QWidget) -> None:
    """Shrink and move `window`, where it is, to fit its screen."""
    fit_to_screen(window, window.width(), window.height(), keep_centre=True)


def toggle_maximised(window: QWidget) -> None:
    if window.isMaximized():
        window.showNormal()
    else:
        window.showMaximized()


class GlyphButton(QAbstractButton):
    """A minimise, maximise (restore while maximised) or close glyph, in
    the label colour; hovered, it sits on the panel colour, and close on
    the error colour."""

    def __init__(self, kind: str, p: Palette, height: int = 28) -> None:
        super().__init__()
        self.kind = kind
        self.p = p
        self.setFixedSize(40, height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(
            {MINIMISE: "Minimise", MAXIMISE: "Maximise", CLOSE: "Close"}[kind]
        )
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        hovered = self.underMouse()
        ink = QColor(self.p["label"])
        if hovered:
            ground = self.p["text-error"] if self.kind == CLOSE else self.p["panel"]
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(ground))
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(2, 2, -2, -2), 4, 4)
            if self.kind == CLOSE:
                ink = QColor(self.p["background"])
        painter.setPen(QPen(ink, 1.3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        c = QRectF(self.rect()).center()
        s = 5.0
        if self.kind == MINIMISE:
            painter.drawLine(
                QPointF(c.x() - s, c.y() + 1), QPointF(c.x() + s, c.y() + 1)
            )
        elif self.kind == CLOSE:
            painter.drawLine(
                QPointF(c.x() - s, c.y() - s), QPointF(c.x() + s, c.y() + s)
            )
            painter.drawLine(
                QPointF(c.x() - s, c.y() + s), QPointF(c.x() + s, c.y() - s)
            )
        elif self.window().isMaximized():  # restore: two squares, one behind
            painter.drawRect(QRectF(c.x() - s, c.y() - s + 2, 2 * s - 2, 2 * s - 2))
            painter.drawPolyline(
                [
                    QPointF(c.x() - s + 2, c.y() - s + 2),
                    QPointF(c.x() - s + 2, c.y() - s),
                    QPointF(c.x() + s, c.y() - s),
                    QPointF(c.x() + s, c.y() + s - 2),
                    QPointF(c.x() + s - 2, c.y() + s - 2),
                ]
            )
        else:
            painter.drawRect(QRectF(c.x() - s, c.y() - s, 2 * s, 2 * s))
        # A small lozenge over the glyph, as the headpiece's.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.p["accent"]))
        painter.drawEllipse(QPointF(c.x(), c.y() - s - 4), 1.2, 1.2)


class WindowButtons(QWidget):
    """Minimise, maximise and close for `window`, or those of them `kinds`
    names."""

    def __init__(
        self,
        window: QWidget,
        p: Palette,
        height: int = 28,
        kinds: tuple[str, ...] = (MINIMISE, MAXIMISE, CLOSE),
    ) -> None:
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.buttons: dict[str, GlyphButton] = {}
        acts = {
            MINIMISE: window.showMinimized,
            MAXIMISE: lambda: toggle_maximised(window),
            CLOSE: window.close,
        }
        for kind in kinds:
            act = acts[kind]
            button = GlyphButton(kind, p, height)
            button.clicked.connect(act)
            row.addWidget(button)
            self.buttons[kind] = button

    def set_palette(self, p: Palette) -> None:
        for button in self.buttons.values():
            button.p = p
            button.update()


class DragStrip(QWidget):
    """Space that moves `window` when dragged and maximises it (or
    restores it) when double-clicked, with `title` over the middle of the
    window (or of the strip, when the window's middle is off it). A window
    that can't be maximised passes `maximises` False."""

    def __init__(
        self, window: QWidget, p: Palette, title: str = "", maximises: bool = True
    ) -> None:
        super().__init__()
        self.window_ = window
        self.title = title
        self.maximises = maximises
        self.p = p
        self.setFont(QFont(fonts.DISPLAY, 13))

    def set_palette(self, p: Palette) -> None:
        self.p = p
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.title:
            return
        width = self.fontMetrics().horizontalAdvance(self.title)
        middle = self.mapFrom(self.window_, QPoint(self.window_.width() // 2, 0)).x()
        if middle - width / 2 < 0 or middle + width / 2 > self.width():
            middle = self.width() // 2
        if width > self.width():
            return
        painter = QPainter(self)
        painter.setPen(QColor(self.p["heading"]))
        painter.drawText(
            QRectF(middle - width / 2 - 2, 0, width + 4, self.height()),
            Qt.AlignmentFlag.AlignCenter,
            self.title,
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        handle = self.window_.windowHandle()
        if event.button() == Qt.MouseButton.LeftButton and handle is not None:
            handle.startSystemMove()
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.maximises:
            toggle_maximised(self.window_)
        event.accept()


class BarRule(QWidget):
    """A thin upright rule in the palette's rule colour with a clear gap
    either side, to set a title bar's buttons apart into groups."""

    #: The gap on each side of the rule, in pixels.
    GAP = 10

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.setFixedWidth(2 * self.GAP + 1)

    def set_palette(self, p: Palette) -> None:
        self.p = p
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setPen(QPen(QColor(self.p["rule"]), 1))
        inset = self.height() // 4
        painter.drawLine(self.GAP, inset, self.GAP, self.height() - inset)


class TopStrip(QWidget):
    """A DragStrip and the WindowButtons laid over the top of `host` (a
    page with no bar of its own, as the title page), kept across its
    width as it resizes."""

    def __init__(self, host: QWidget, window: QWidget, p: Palette) -> None:
        super().__init__(host)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 8, 0)
        row.setSpacing(0)
        self.drag = DragStrip(window, p)
        # Short enough to stay above the title page's gilt frame.
        self.controls = WindowButtons(window, p, height=22)
        row.addWidget(self.drag, 1)
        row.addWidget(self.controls, 0, Qt.AlignmentFlag.AlignTop)
        host.installEventFilter(self)
        self._place(host)
        self.raise_()

    def _place(self, host: QWidget) -> None:
        self.setGeometry(0, 0, host.width(), STRIP)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Resize and isinstance(watched, QWidget):
            self._place(watched)
        return False


#: Each grip's edges, and its cursor.
_GRIPS: tuple[tuple[Qt.Edge, Qt.CursorShape], ...] = (
    (Qt.Edge.LeftEdge, Qt.CursorShape.SizeHorCursor),
    (Qt.Edge.RightEdge, Qt.CursorShape.SizeHorCursor),
    (Qt.Edge.TopEdge, Qt.CursorShape.SizeVerCursor),
    (Qt.Edge.BottomEdge, Qt.CursorShape.SizeVerCursor),
    (Qt.Edge.TopEdge | Qt.Edge.LeftEdge, Qt.CursorShape.SizeFDiagCursor),
    (Qt.Edge.BottomEdge | Qt.Edge.RightEdge, Qt.CursorShape.SizeFDiagCursor),
    (Qt.Edge.TopEdge | Qt.Edge.RightEdge, Qt.CursorShape.SizeBDiagCursor),
    (Qt.Edge.BottomEdge | Qt.Edge.LeftEdge, Qt.CursorShape.SizeBDiagCursor),
)


class Grip(QWidget):
    """An invisible band along an edge or corner of `window` that resizes
    it from there."""

    def __init__(self, window: QWidget, edges: Qt.Edge, cursor: Qt.CursorShape) -> None:
        super().__init__(window)
        self.edges = edges
        self.setCursor(cursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        handle = self.window().windowHandle()
        if event.button() == Qt.MouseButton.LeftButton and handle is not None:
            handle.startSystemResize(self.edges)
        event.accept()


class Grips(QObject):
    """The grips around `window`, kept on its edges and over its
    contents; hidden while it is maximised."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.grips = [Grip(window, edges, cursor) for edges, cursor in _GRIPS]
        window.installEventFilter(self)
        self.place()

    def place(self) -> None:
        w, h = self.window.width(), self.window.height()
        corner = 2 * GRIP
        for grip in self.grips:
            e = grip.edges
            left, right = Qt.Edge.LeftEdge in e, Qt.Edge.RightEdge in e
            top, bottom = Qt.Edge.TopEdge in e, Qt.Edge.BottomEdge in e
            width = corner if (left or right) and (top or bottom) else GRIP
            height = width
            if not (left or right):
                width = w - 2 * corner
            if not (top or bottom):
                height = h - 2 * corner
            x = 0 if left else w - width if right else corner
            y = 0 if top else h - height if bottom else corner
            grip.setGeometry(x, y, width, height)
            grip.setVisible(not self.window.isMaximized())
            grip.raise_()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.WindowStateChange,
            QEvent.Type.ChildAdded,
        ):
            self.place()
        return False
