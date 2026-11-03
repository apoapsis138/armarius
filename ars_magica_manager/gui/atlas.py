"""The desktop saga page's Atlas chapter: a map, panned and zoomed, with a
pin for each record it shows, drawn as the app's own symbol (a covenant's
turret, a ruin, a place's or creature's realm, a lord's arms).

Hovering a pin shows the record in the inspector; clicking it opens the
record's page, so Back returns here; dragging one of the troupe's pins
moves it; its right-click menu opens it, makes it secret or takes it off
the map. The Table view, for a screen the players watch, leaves off the
secret pins and every record shown at them.

Which pins show, and where, is the core's (atlas.py); opening a pin's
record goes through the window's own opener for a link (a Go step), as
Connections and Linked From do.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFontMetricsF,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
    QResizeEvent,
    QShowEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsScene,
    QGraphicsSceneContextMenuEvent,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLayout,
    QMenu,
    QStyleOptionGraphicsItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .. import artwork
from .. import atlas as at
from ..arms import Arms
from ..commands import Act, Choose, Command, Go, Picked
from ..markup import escape
from ..models import AtlasMap, Covenant, Neighbour, Saga
from . import pictures, shields
from .markup_html import plain
from .themes import Palette
from .widgets import chapter_title, edit_button, serif, text

#: Runs a command and, once its last step is answered and the saga
#: saved, calls back with what it ended with instead of drawing the page
#: again (so the map keeps its place).
RunEnded = Callable[[Command, Callable[[object], None]], None]
#: Shows a record in the page's inspector.
Inspect = Callable[[str, str, str], None]

#: A pin's size on screen, in pixels, whatever the zoom, and its name
#: label's height under it.
PIN = 34
LABEL = 18
#: A placeholder's longer side, in pixels, and how many squares its grid
#: has each way.
PLACEHOLDER = 2400
GRID = 10
#: How far one wheel notch zooms, and the furthest in and out.
ZOOM_STEP = 1.15
ZOOM_MOST, ZOOM_LEAST = 8.0, 0.05


@dataclass
class _Kept:
    """What the Atlas keeps while the app runs: the map on show for each
    saga, where each map was looked at, the Table view and the kinds left
    off, and the record Show on Map asked for."""

    chosen: dict[str, str] = field(default_factory=dict)
    views: dict[str, tuple[float, float, float]] = field(default_factory=dict)
    table: bool = False
    hidden_kinds: set[str] = field(default_factory=set)
    focus: tuple[str, str] | None = None


KEPT = _Kept()


def show_on_map(kind: str, record_id: str) -> None:
    """Have the Atlas open on the record's pin the next time it is drawn."""
    KEPT.focus = (kind, record_id)


def _mark(saga: Saga, shown: at.ShownPin, p: Palette) -> QPixmap:
    """A pin's own picture: the record's arms where it bears any, else
    its symbol in the heading colour."""
    record = at.record(saga, shown.ref.kind, shown.ref.id)
    arms = (
        Arms.from_dict(record.arms)
        if isinstance(record, Covenant | Neighbour) and record.arms
        else None
    )
    if arms is not None:
        return shields.pixmap(arms, PIN - 14, p["foreground"])
    return pictures.pixmap(artwork.icon(shown.concept), p["heading"], PIN - 12, 2.0)


def placeholder_size(atlas_map: AtlasMap) -> tuple[int, int]:
    """A placeholder's size in pixels: the map's shape (its picture's size,
    or the shape the form gave), its longer side PLACEHOLDER pixels."""
    width, height = (
        (atlas_map.width, atlas_map.height)
        if atlas_map.width and atlas_map.height
        else at.PLACEHOLDER_SHAPE
    )
    scale = PLACEHOLDER / max(width, height)
    return round(width * scale), round(height * scale)


def placeholder(name: str, words: str, size: tuple[int, int], p: Palette) -> QPixmap:
    """A map not drawn yet, drawn in code: parchment in a double frame, a
    grid lettered along the top and numbered down the side (so a place
    can be put "about D7"), a compass rose, and a cartouche with the map's
    name and `words`."""
    width, height = size
    picture = QPixmap(width, height)
    picture.fill(QColor(p["background"]))
    g = QPainter(picture)
    g.setRenderHint(QPainter.RenderHint.Antialiasing)
    # A darker edge, as old parchment browns toward its margins.
    edge = QRadialGradient(width / 2, height / 2, max(width, height) * 0.7)
    edge.setColorAt(0.55, QColor(0, 0, 0, 0))
    edge.setColorAt(1.0, QColor(p["panel"]))
    g.fillRect(0, 0, width, height, QBrush(edge))
    margin = 60.0
    inner = QRectF(margin, margin, width - 2 * margin, height - 2 * margin)
    grid = QColor(p["rule"])
    g.setPen(QPen(grid, 1.5, Qt.PenStyle.DashLine))
    g.setFont(serif(26, caps=True))
    for i in range(1, GRID):
        x = inner.left() + inner.width() * i / GRID
        y = inner.top() + inner.height() * i / GRID
        g.drawLine(QPointF(x, inner.top()), QPointF(x, inner.bottom()))
        g.drawLine(QPointF(inner.left(), y), QPointF(inner.right(), y))
    g.setPen(QColor(p["label"]))
    for i in range(GRID):
        cell_w, cell_h = inner.width() / GRID, inner.height() / GRID
        top = QRectF(inner.left() + i * cell_w, 8, cell_w, margin - 12)
        side = QRectF(8, inner.top() + i * cell_h, margin - 16, cell_h)
        g.drawText(top, Qt.AlignmentFlag.AlignCenter, "ABCDEFGHIJ"[i])
        g.drawText(side, Qt.AlignmentFlag.AlignCenter, str(i + 1))
    g.setBrush(Qt.BrushStyle.NoBrush)
    g.setPen(QPen(QColor(p["accent"]), 6))
    g.drawRect(inner)
    g.setPen(QPen(QColor(p["accent"]), 2))
    g.drawRect(inner.adjusted(-14, -14, 14, 14))
    _compass(g, QPointF(inner.right() - 150, inner.bottom() - 170), 110, p)
    # The cartouche, at the lower left: the map's name over what this page is.
    box = QRectF(
        inner.left() + 40, inner.bottom() - 230, min(1100, inner.width() * 0.6), 190
    )
    wash = QColor(p["surface"])
    wash.setAlpha(235)
    g.setPen(QPen(QColor(p["accent"]), 3))
    g.setBrush(QBrush(wash))
    g.drawRoundedRect(box, 18, 18)
    g.setPen(QColor(p["heading"]))
    g.setFont(serif(60, bold=True))
    g.drawText(
        box.adjusted(30, 18, -30, -80),
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        name,
    )
    g.setPen(QColor(p["label"]))
    g.setFont(serif(30, italic=True))
    g.drawText(
        box.adjusted(32, 110, -30, -16),
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        words,
    )
    g.end()
    return picture


def _compass(g: QPainter, centre: QPointF, radius: float, p: Palette) -> None:
    """An eight-pointed compass rose, its north point in the heading
    colour and marked N."""
    g.save()
    g.translate(centre)
    g.setPen(QPen(QColor(p["foreground"]), 2))
    for turn in range(8):
        long = turn % 2 == 0
        reach, waist = (
            (radius, radius * 0.16) if long else (radius * 0.6, radius * 0.12)
        )
        g.save()
        g.rotate(turn * 45)
        point = QPainterPath()
        point.moveTo(0, -reach)
        point.lineTo(waist, 0)
        point.lineTo(0, waist * 0.6)
        point.lineTo(-waist, 0)
        point.closeSubpath()
        north = turn == 0
        g.setBrush(
            QColor(p["heading"] if north else p["accent" if long else "surface"])
        )
        g.drawPath(point)
        g.restore()
    g.setPen(QColor(p["heading"]))
    g.setFont(serif(30, bold=True))
    g.drawText(QRectF(-40, -radius - 52, 80, 44), Qt.AlignmentFlag.AlignCenter, "N")
    g.restore()


#: What a Picking's clicks are for.
PLACE, SCALE, MEASURE = "place", "scale", "measure"


@dataclass
class Picking:
    """Clicks on the map gathered for a step: the spot to put a record
    down (its kind, id and name), the two ends of the scale bar, or two
    points to measure between."""

    purpose: str
    record: tuple[str, str, str] | None = None
    points: list[tuple[float, float]] = field(default_factory=list)


class PinItem(QGraphicsObject):
    """The records shown at one spot of the map: one marker, the first
    record's mark, with a count when more share it, and the first's name
    on a label under it."""

    def __init__(self, view: MapView, here: list[at.ShownPin], mark: QPixmap) -> None:
        super().__init__()
        self.view, self.here, self.mark = view, here, mark
        self.name_font = serif(10, bold=True)
        self.name = here[0].ref.name
        self.name_width = (
            QFontMetricsF(self.name_font).horizontalAdvance(self.name) + 10
        )
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setZValue(1)
        self._pressed: QPointF | None = None
        self._dragged = False

    @property
    def movable(self) -> bool:
        """Whether a drag moves it: one record, at a pin of its own, off
        the Table view."""
        return len(self.here) == 1 and self.here[0].pin is not None and not KEPT.table

    def boundingRect(self) -> QRectF:
        half = max(PIN / 2 + 12, self.name_width / 2)
        return QRectF(-half, -PIN / 2 - 2, 2 * half, PIN + 4 + LABEL)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        p = self.view.p
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        disc = QRectF(-PIN / 2, -PIN / 2, PIN, PIN)
        ring = QPen(QColor(p["accent"]), 2.5)
        if any(s.secret for s in self.here):
            # A secret pin's ring is dashed, not only coloured.
            ring.setStyle(Qt.PenStyle.DashLine)
        if self.view.chosen is self:
            ring.setColor(QColor(p["heading"]))
            ring.setWidthF(3.5)
        painter.setPen(ring)
        painter.setBrush(QBrush(QColor(p["surface"])))
        painter.drawEllipse(disc)
        ratio = self.mark.devicePixelRatio() or 1.0
        size = self.mark.size() / ratio
        painter.drawPixmap(QPointF(-size.width() / 2, -size.height() / 2), self.mark)
        # The name on a pale label under the pin, readable over any map.
        label = QRectF(-self.name_width / 2, PIN / 2 + 2, self.name_width, LABEL - 2)
        painter.setPen(Qt.PenStyle.NoPen)
        wash = QColor(p["background"])
        wash.setAlpha(215)
        painter.setBrush(QBrush(wash))
        painter.drawRoundedRect(label, 4, 4)
        painter.setPen(QColor(p["foreground"]))
        painter.setFont(self.name_font)
        painter.drawText(label, Qt.AlignmentFlag.AlignCenter, self.name)
        if len(self.here) > 1:
            badge = QRectF(PIN / 2 - 8, -PIN / 2 - 2, 18, 16)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(p["heading"])))
            painter.drawRoundedRect(badge, 7, 7)
            painter.setPen(QColor(p["background"]))
            painter.setFont(serif(8.5, bold=True))
            painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, str(len(self.here)))

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.view.hovered(self.here)
        super().hoverEnterEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        self._pressed, self._dragged = event.scenePos(), False
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._pressed is None or not self.movable:
            return
        if (event.scenePos() - self._pressed).manhattanLength() * self.view.zoom() > 4:
            self._dragged = True
        if self._dragged:
            self.setPos(self.view.inside(event.scenePos()))

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._pressed is None:
            return
        self._pressed = None
        if self._dragged:
            self.view.moved(self.here[0], self.pos())
        else:
            self.view.clicked(self)

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        self.view.menu_for(self, event.screenPos())


class MapView(QGraphicsView):
    """One map's picture (a blank page while it has none) with its pins;
    the wheel zooms, a drag pans."""

    def __init__(self, chapter: AtlasChapter, atlas_map: AtlasMap) -> None:
        super().__init__()
        self.chapter, self.p, self.map = chapter, chapter.p, atlas_map
        self.chosen: PinItem | None = None
        self.pins: list[PinItem] = []
        #: What clicks on the map are for while Place on Map, Set Scale or
        #: Measure waits for them; None while they pan and open pins.
        self.picking: Picking | None = None
        #: The line and words a measurement left on the map.
        self.measured: list[QGraphicsItem] = []
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet(
            f"QGraphicsView {{ border:1px solid {self.p['rule']};"
            f" background:{self.p['panel']}; }}"
        )
        self._shown = False
        self._draw_picture()
        self.draw_pins()

    # The picture and the pins

    def _draw_picture(self) -> None:
        scene = self.scene()
        found = at.picture_path(self.map)
        picture = QPixmap(str(found)) if found is not None else QPixmap()
        if not picture.isNull():
            scene.addPixmap(picture)
            self.size_ = (picture.width(), picture.height())
        else:
            # A placeholder in the map's shape, the pins still on it.
            self.size_ = placeholder_size(self.map)
            words = (
                f"The picture {self.map.picture} is missing from the maps folder."
                if self.map.picture
                else "A placeholder: Edit Map adds the picture."
            )
            scene.addPixmap(placeholder(self.map.name, words, self.size_, self.p))
        scene.setSceneRect(QRectF(0, 0, *self.size_))

    def draw_pins(self) -> None:
        """The pins the map shows now, grouped where several share a spot."""
        scene = self.scene()
        chosen = self.chosen.here[0].ref if self.chosen is not None else None
        for item in self.pins:
            scene.removeItem(item)
        self.pins, self.chosen = [], None
        saga = self.chapter.saga
        kinds = [k for k in at.SHOWN_KINDS if k not in KEPT.hidden_kinds]
        spots: dict[tuple[float, float], list[at.ShownPin]] = {}
        for shown in at.shown_pins(saga, self.map.id, table=KEPT.table, kinds=kinds):
            spots.setdefault((shown.x, shown.y), []).append(shown)
        for (x, y), here in spots.items():
            # A record's own pin first, so its mark is the one drawn.
            here.sort(key=lambda s: s.pin is None)
            item = PinItem(self, here, _mark(saga, here[0], self.p))
            item.setPos(x * self.size_[0], y * self.size_[1])
            item.setToolTip(", ".join(s.ref.name for s in here))
            scene.addItem(item)
            self.pins.append(item)
            if chosen is not None and any(s.ref == chosen for s in here):
                self.chosen = item

    def item_of(self, kind: str, record_id: str) -> PinItem | None:
        return next(
            (
                item
                for item in self.pins
                if any(s.ref.kind == kind and s.ref.id == record_id for s in item.here)
            ),
            None,
        )

    def inside(self, at_: QPointF) -> QPointF:
        """`at_` kept on the map."""
        return QPointF(
            min(max(at_.x(), 0.0), self.size_[0]), min(max(at_.y(), 0.0), self.size_[1])
        )

    def fraction(self, at_: QPointF) -> tuple[float, float]:
        """A point of the map as fractions of its width and height."""
        inside = self.inside(at_)
        return inside.x() / self.size_[0], inside.y() / self.size_[1]

    # Looking around

    def zoom(self) -> float:
        return self.transform().m11()

    def fit(self) -> None:
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent) -> None:
        step = ZOOM_STEP if event.angleDelta().y() > 0 else 1 / ZOOM_STEP
        if ZOOM_LEAST <= self.zoom() * step <= ZOOM_MOST:
            self.scale(step, step)
        self.keep()

    def keep(self) -> None:
        """Remember where the map is looked at, for the next time it shows."""
        centre = self.mapToScene(self.viewport().rect().center())
        KEPT.views[self.map.id] = (self.zoom(), centre.x(), centre.y())

    def look_at(self, item: PinItem) -> None:
        self.centerOn(item.pos())
        self.keep()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self._shown:
            return
        self._shown = True
        kept = KEPT.views.get(self.map.id)
        if kept is None:
            self.fit()
        else:
            zoom, x, y = kept
            self.resetTransform()
            self.scale(zoom, zoom)
            self.centerOn(x, y)
        if self.chosen is not None:
            self.look_at(self.chosen)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._shown and self.map.id not in KEPT.views:
            self.fit()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.keep()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        picking = self.picking
        if picking is None or event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        at_ = self.mapToScene(event.position().toPoint())
        if picking.purpose == MEASURE:
            # A click on a pin measures from the pin itself: the nearest of
            # those under the click, as a label may reach over another pin.
            under = [
                item
                for item in self.items(event.position().toPoint())
                if isinstance(item, PinItem)
            ]
            if under:
                clicked = at_
                at_ = min(
                    under, key=lambda item: (item.pos() - clicked).manhattanLength()
                ).pos()
        picking.points.append(self.fraction(at_))
        if picking.purpose == PLACE and picking.record is not None:
            kind, record_id, _name = picking.record
            self.stop_picking(quietly=True)
            self.chapter.put_down(kind, record_id, picking.points[0])
            return
        if len(picking.points) == 1:
            self.clear_measured()
            self._mark_point(at_)
            self.chapter.say(
                "Now click the other end of the scale bar (Esc stops)."
                if picking.purpose == SCALE
                else "Now click where to measure to (Esc stops)."
            )
            return
        a, b = picking.points
        self.stop_picking(quietly=True)
        if picking.purpose == SCALE:
            self.clear_measured()
            self.chapter.scale_from(a, b)
        else:
            self.measure(a, b)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape and (self.picking or self.measured):
            self.stop_picking()
            self.clear_measured()
            return
        super().keyPressEvent(event)

    def start_picking(self, picking: Picking) -> None:
        self.picking = picking
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()

    def stop_picking(self, *, quietly: bool = False) -> None:
        self.picking = None
        self.viewport().unsetCursor()
        if not quietly:
            self.chapter.say("")

    # Measuring

    def _point(self, fraction: tuple[float, float]) -> QPointF:
        return QPointF(fraction[0] * self.size_[0], fraction[1] * self.size_[1])

    def _mark_point(self, at_: QPointF) -> None:
        ring = QPen(QColor(self.p["heading"]), 2.5)
        ring.setCosmetic(True)
        dot = self.scene().addEllipse(QRectF(-6, -6, 12, 12), ring)
        dot.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        dot.setPos(at_)
        dot.setZValue(0.5)
        self.measured.append(dot)

    def clear_measured(self) -> None:
        for item in self.measured:
            self.scene().removeItem(item)
        self.measured = []

    def measure(self, a: tuple[float, float], b: tuple[float, float]) -> None:
        """A dashed line between two points of the map, with how far apart
        they are, in a straight line, at its middle."""
        miles = at.miles_between(self.map, a, b)
        if miles is None:
            return
        start, end = self._point(a), self._point(b)
        line = QPen(QColor(self.p["heading"]), 2.5, Qt.PenStyle.DashLine)
        line.setCosmetic(True)
        # Under the pins, so it runs from one to the other.
        drawn = self.scene().addLine(start.x(), start.y(), end.x(), end.y(), line)
        drawn.setZValue(0.5)
        self.measured.append(drawn)
        words = at.distance_words(miles)
        # The words on a pale label beside the line's middle.
        text = QGraphicsSimpleTextItem(words)
        text.setFont(serif(11, bold=True))
        text.setBrush(QBrush(QColor(self.p["heading"])))
        box = text.boundingRect().adjusted(-6, -3, 6, 3)
        wash = QColor(self.p["background"])
        wash.setAlpha(225)
        label = self.scene().addRect(
            box, QPen(QColor(self.p["accent"]), 1), QBrush(wash)
        )
        text.setParentItem(label)
        label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        label.setPos((start + end) / 2 + QPointF(12, 8))
        label.setZValue(3)
        self.measured.append(label)
        self.chapter.say(f"{words[0].upper()}{words[1:]}. Esc clears it.")

    # What the pins do

    def hovered(self, here: list[at.ShownPin]) -> None:
        self.chapter.inspect_pins(here)

    def clicked(self, item: PinItem) -> None:
        self.chosen = item
        self.scene().update()
        if len(item.here) == 1:
            self.chapter.open(item.here[0])
            return
        menu = QMenu(self)
        for shown in item.here:
            action = menu.addAction(shown.ref.name)
            action.triggered.connect(lambda _c=False, s=shown: self.chapter.open(s))
        menu.exec(self.mapToGlobal(self.mapFromScene(item.pos())))

    def moved(self, shown: at.ShownPin, to: QPointF) -> None:
        self.chapter.put_down(shown.ref.kind, shown.ref.id, self.fraction(to))

    def menu_for(self, item: PinItem, where: QPoint) -> None:
        menu = QMenu(self)
        for shown in item.here:
            heading = menu.addAction(f"Open {shown.ref.name}")
            heading.triggered.connect(lambda _c=False, s=shown: self.chapter.open(s))
            pin = shown.pin
            if pin is None or KEPT.table:
                continue
            secret = menu.addAction("Secret: left off the Table view")
            secret.setCheckable(True)
            secret.setChecked(pin.secret)
            secret.triggered.connect(
                lambda checked, s=shown: self.chapter.set_secret(s, checked)
            )
            remove = menu.addAction(f"Take {shown.ref.name} off the map")
            remove.triggered.connect(lambda _c=False, s=shown: self.chapter.take_off(s))
        menu.exec(where)


class AtlasChapter(QWidget):
    """The Atlas: the chosen map with its buttons, the filter of which
    kinds of record show and the Table view switch. Its buttons redraw the
    chapter in place, so the rest of the saga page is left as it was."""

    def __init__(
        self,
        saga: Saga,
        p: Palette,
        run: Callable[[Command], None],
        run_ended: RunEnded,
        inspect: Inspect,
    ) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        self.run, self.run_ended, self._inspect = run, run_ended, inspect
        self.view: MapView | None = None
        self.view_map: AtlasMap | None = None
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(4, 0, 4, 4)
        self.column.setSpacing(8)
        focus = KEPT.focus
        KEPT.focus = None
        self._fill(focus)

    def _clear(self) -> None:
        def empty(layout: QLayout) -> None:
            while layout.count():
                item = layout.takeAt(0)
                if item is None:
                    continue
                widget, inner = item.widget(), item.layout()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                elif inner is not None:
                    empty(inner)

        empty(self.column)
        self.view, self.view_map = None, None

    def _fill(self, focus: tuple[str, str] | None = None) -> None:
        """Draw the chapter for the map chosen (one showing `focus`, the
        record Show on Map asked for, when given)."""
        self._clear()
        saga, p = self.saga, self.p
        found = at.maps(saga)
        chosen = self._chosen_map(found, focus)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(chapter_title("The Atlas", p, rule=False), 1)
        self.choice = QComboBox()
        for m, tribunal in found:
            self.choice.addItem(at.map_label(m, tribunal), m.id)
        if chosen is not None:
            self.choice.setCurrentIndex(self.choice.findData(chosen.id))
        self.choice.currentIndexChanged.connect(self._choose)
        self.choice.setVisible(bool(found))
        top.addWidget(self.choice, 0, Qt.AlignmentFlag.AlignTop)
        buttons: list[tuple[str, str, Callable[[], None]]] = [
            ("New Map", "add", self._new_map)
        ]
        if chosen is not None:
            buttons += [
                ("Edit Map", "edit", lambda: self._edit_map(chosen)),
                ("Place on Map", "add", self.place),
                ("Set Scale", "edit", self.set_scale),
                ("Remove Map", "delete", lambda: self._remove_map(chosen)),
            ]
        for words, concept, act in buttons:
            top.addWidget(
                edit_button(words, p, act, concept), 0, Qt.AlignmentFlag.AlignTop
            )
        self.column.addLayout(top)
        if chosen is None:
            self.column.addWidget(
                text(
                    "No maps yet. New Map adds one: a picture of a Tribunal's "
                    "region, or of a region with none, and its records can then "
                    "be placed on it.",
                    p["dim"],
                    serif(12.5, italic=True),
                    wrap=True,
                )
            )
            self.column.addStretch(1)
            return
        self.view_map = chosen
        self.column.addLayout(self._controls())
        self.view = MapView(self, chosen)
        self.column.addWidget(self.view, 1)
        self.line = text("", p["label"], serif(11.5, italic=True), wrap=True)
        self.column.addWidget(self.line)
        self.say("")
        if focus is not None:
            item = self.view.item_of(*focus)
            if item is not None:
                self.view.chosen = item
                self.inspect_pins(item.here)

    # The maps

    def _new_map(self) -> None:
        before = {m.id for m, _t in at.maps(self.saga)}

        def made(done: object) -> None:
            new = [m.id for m, _t in at.maps(self.saga) if m.id not in before]
            if new:
                KEPT.chosen[self.saga.id] = new[0]
            self._fill()
            self._tell(done)

        self.run_ended(at.map_form(self.saga), made)

    def _edit_map(self, atlas_map: AtlasMap) -> None:
        def edited(done: object) -> None:
            self._fill()
            self._tell(done)

        self.run_ended(at.map_form(self.saga, atlas_map), edited)

    def _remove_map(self, atlas_map: AtlasMap) -> None:
        self.run_ended(
            at.remove_map_step(self.saga, atlas_map), lambda _d: self._fill()
        )

    def _tell(self, done: object) -> None:
        """The notes a form ended with, on the line under the map."""
        if isinstance(done, list) and done:
            self.say(" ".join(plain(str(line)) for line in done))

    def _chosen_map(
        self,
        found: Sequence[tuple[AtlasMap, object]],
        focus: tuple[str, str] | None,
    ) -> AtlasMap | None:
        """The map to show: one that shows the record Show on Map asked
        for, else the one last shown, else the first."""
        if not found:
            return None
        if focus is not None:
            showing = at.maps_showing(self.saga, *focus)
            if showing:
                KEPT.chosen[self.saga.id] = showing[0].id
                return showing[0]
        last = KEPT.chosen.get(self.saga.id)
        return next((m for m, _t in found if m.id == last), found[0][0])

    def _controls(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        kinds = QToolButton()
        kinds.setText("Show")
        kinds.setIcon(pictures.icon("filter", self.p["label"], 14))
        kinds.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        kinds.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(kinds)
        for kind in at.SHOWN_KINDS:
            action = menu.addAction(at.KIND_LABELS[kind])
            action.setCheckable(True)
            action.setChecked(kind not in KEPT.hidden_kinds)
            action.toggled.connect(lambda on, k=kind: self._show_kind(k, on))
        kinds.setMenu(menu)
        row.addWidget(kinds)
        self.table = QCheckBox("Table view: leave off the secret pins")
        self.table.setChecked(KEPT.table)
        self.table.toggled.connect(self._table_view)
        row.addWidget(self.table)
        row.addStretch(1)
        if self.view_map is not None and at.has_scale(self.view_map):
            row.addWidget(edit_button("Measure", self.p, self.measure, "search"))
        row.addWidget(edit_button("Fit", self.p, self._fit, "search"))
        return row

    # The controls

    def _choose(self, index: int) -> None:
        map_id = self.choice.itemData(index)
        if isinstance(map_id, str) and (
            self.view is None or map_id != self.view.map.id
        ):
            KEPT.chosen[self.saga.id] = map_id
            self._fill()

    def _show_kind(self, kind: str, on: bool) -> None:
        if on:
            KEPT.hidden_kinds.discard(kind)
        else:
            KEPT.hidden_kinds.add(kind)
        if self.view is not None:
            self.view.draw_pins()

    def _table_view(self, on: bool) -> None:
        KEPT.table = on
        if self.view is not None:
            self.view.draw_pins()
        self.say("")

    def _fit(self) -> None:
        if self.view is not None:
            self.view.fit()
            self.view.keep()

    def say(self, words: str) -> None:
        """The line under the map: what to do now, else the map's credit
        and how to move about it."""
        if self.view is None:
            return
        if not words:
            credit = self.view.map.credit
            words = (
                (f"{credit}.  " if credit else "")
                + at.scale_words(self.view.map)
                + "  Scroll to zoom, drag to look around; hover a pin to see it, "
                "click to open it, drag one to move it."
                + ("  Table view: secret pins are left off." if KEPT.table else "")
            )
        self.line.setText(words)

    # The pins

    def inspect_pins(self, here: list[at.ShownPin]) -> None:
        """Show the records at a pin in the inspector: one's summary, or
        each one's name and summary where several share it."""
        lines = []
        for shown in here:
            found = at.record(self.saga, shown.ref.kind, shown.ref.id)
            notes = [at.kind_word(found)] if len(here) > 1 else []
            if shown.at:
                notes.append(f"at {shown.at}")
            if shown.secret and not KEPT.table:
                notes.append("secret pin")
            note = f"[dim]{escape(', '.join(notes))}[/]" if notes else ""
            if len(here) > 1:
                lines.append(f"[b]{escape(shown.ref.name)}[/]  {note}")
            elif note:
                lines.append(note)
            if shown.summary:
                lines.append(escape(shown.summary))
        first = here[0]
        self._inspect(
            first.ref.name if len(here) == 1 else f"{len(here)} records here",
            at.kind_word(at.record(self.saga, first.ref.kind, first.ref.id))
            if len(here) == 1
            else "",
            "\n\n".join(lines),
        )

    def open(self, shown: at.ShownPin) -> None:
        if self.view is not None:
            self.view.keep()
        self.run(Act(lambda: Go(shown.ref)))

    def set_scale(self) -> None:
        """Set Scale: click the two ends of the map's scale bar, then say
        how long it is."""
        if self.view is not None:
            self.view.start_picking(Picking(SCALE))
            self.say("Click one end of the map's scale bar (Esc stops).")

    def scale_from(self, a: tuple[float, float], b: tuple[float, float]) -> None:
        """The scale bar's ends are clicked: ask its length, then draw the
        chapter again with Measure."""
        view = self.view
        if view is None:
            return
        if a == b:
            self.say("The scale bar's two ends should be apart: Set Scale again.")
            return
        self.run_ended(at.scale_form(view.map, a, b), lambda _done: self._fill())

    def measure(self) -> None:
        """Measure: click two points (or pins) to see how far apart they
        are in a straight line."""
        if self.view is not None:
            self.view.clear_measured()
            self.view.start_picking(Picking(MEASURE))
            self.say("Click a pin or a point to measure from (Esc stops).")

    def place(self) -> None:
        """Place on Map: choose a record, then click where it is."""
        view = self.view
        if view is None:
            return

        def chosen(done: object) -> None:
            if isinstance(done, Picked) and view is self.view:
                kind, record_id, name = done.value
                view.start_picking(Picking(PLACE, (kind, record_id, name)))
                self.say(
                    f"Click where {plain(escape(name))} is on the map (Esc stops)."
                )

        self.run_ended(
            Choose(
                f"Place on {escape(view.map.name)}",
                lambda: at.pinnable(self.saga, view.map.id),
                lambda ref: Picked((ref.kind, ref.id, ref.name)),
                empty="Every covenant, neighbour and creature is on this map.",
                filters=("Kind",),
                help_id="atlas-place",
            ),
            chosen,
        )

    def put_down(self, kind: str, record_id: str, where: tuple[float, float]) -> None:
        view = self.view
        if view is None:
            return
        map_id = view.map.id

        def drawn(_done: object) -> None:
            view.draw_pins()
            item = view.item_of(kind, record_id)
            if item is not None:
                view.chosen = item
                view.scene().update()
            self.say("")

        self.run_ended(
            Act(lambda: at.place_pin(self.saga, map_id, kind, record_id, *where)),
            drawn,
        )

    def set_secret(self, shown: at.ShownPin, secret: bool) -> None:
        pin = shown.pin
        view = self.view
        if pin is None or view is None:
            return

        def apply() -> None:
            pin.secret = secret

        self.run_ended(Act(apply), lambda _done: view.draw_pins())

    def take_off(self, shown: at.ShownPin) -> None:
        pin = shown.pin
        view = self.view
        if pin is None or view is None:
            return
        self.run_ended(
            Act(lambda: at.remove_pin(self.saga, pin)), lambda _done: view.draw_pins()
        )
