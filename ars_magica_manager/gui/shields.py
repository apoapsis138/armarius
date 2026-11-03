"""A shield's arms painted at any size with painter paths, from the
shield's geometry in arms.py (its outline, the division's areas and the
charge's shapes), with a light sheen and an edge. Drawing only: the
Arms sections and forms that show them are heraldry.py's."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)

from ..arms import (
    CHARGE_ARMED,
    CHARGE_LINES,
    CHARGE_SHAPES,
    DIVISION_AREAS,
    ERMINE_SPOT,
    FUR_BOXES,
    FURS,
    HEIGHT,
    Arms,
    Shape,
    armed_tincture,
    charge_boxes,
    line_tincture,
    shield_outline,
)
from .themes import TINCTURES


def _path(
    shapes: Sequence[Shape], left: float, top: float, scale: float
) -> QPainterPath:
    """`shapes` (in their own unit square) as one path: each solid one
    added, each hole cut from what came before it."""
    solid = QPainterPath()
    for shape in shapes:
        part = QPainterPath()
        if shape.rings:
            part.setFillRule(Qt.FillRule.OddEvenFill)
            for ring in shape.rings:
                part.addPolygon(
                    QPolygonF(
                        [QPointF(left + x * scale, top + y * scale) for x, y in ring]
                    )
                )
                part.closeSubpath()
        elif shape.radius:
            cx, cy = shape.points[0]
            r = shape.radius * scale
            part.addEllipse(QPointF(left + cx * scale, top + cy * scale), r, r)
        else:
            part.addPolygon(
                QPolygonF(
                    [
                        QPointF(left + x * scale, top + y * scale)
                        for x, y in shape.points
                    ]
                )
            )
            part.closeSubpath()
        solid = solid.subtracted(part) if shape.hole else solid.united(part)
    return solid


def shield_path(rect: QRectF) -> QPainterPath:
    """The shield's edge, filling `rect`'s width."""
    scale = rect.width()
    path = QPainterPath()
    path.addPolygon(
        QPolygonF(
            [
                QPointF(rect.left() + x * scale, rect.top() + y * scale)
                for x, y in shield_outline(24)
            ]
        )
    )
    path.closeSubpath()
    return path


def _fill(painter: QPainter, area: QPainterPath, tincture: str, rect: QRectF) -> None:
    """Fill `area` in `tincture`: a fur as its ground strewn with its
    spots, placed on the shield in `rect` so they line up across parts."""
    if tincture not in FURS:
        painter.fillPath(area, QColor(TINCTURES[tincture]))
        return
    ground, spot = FURS[tincture]
    painter.fillPath(area, QColor(TINCTURES[ground]))
    scale = rect.width()
    spots = QPainterPath()
    for left, top, side in FUR_BOXES:
        spots = spots.united(
            _path(
                ERMINE_SPOT,
                rect.left() + left * scale,
                rect.top() + top * scale,
                side * scale,
            )
        )
    painter.fillPath(area.intersected(spots), QColor(TINCTURES[spot]))


def paint(painter: QPainter, arms: Arms, rect: QRectF, edge: str) -> None:
    """Paint `arms` in `rect` (as wide as the shield; its height follows),
    edged in `edge`."""
    scale = rect.width()
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    outline = shield_path(rect)
    painter.setClipPath(outline)
    _fill(painter, outline, arms.field, rect)
    second = _path(
        DIVISION_AREAS.get(arms.division, ()), rect.left(), rect.top(), scale
    )
    _fill(painter, second, arms.second, rect)
    if arms.charge in CHARGE_SHAPES:
        for left, top, side in charge_boxes(arms):
            charge = _path(
                CHARGE_SHAPES[arms.charge],
                rect.left() + left * scale,
                rect.top() + top * scale,
                side * scale,
            )
            _fill(painter, charge, arms.charge_tincture, rect)
            painter.strokePath(charge, QPen(QColor(0, 0, 0, 70), max(0.6, scale / 160)))
            for layer, tincture in (
                (CHARGE_LINES.get(arms.charge), line_tincture(arms)),
                (CHARGE_ARMED.get(arms.charge), armed_tincture(arms)),
            ):
                if layer is not None:
                    detail = _path(
                        (layer,),
                        rect.left() + left * scale,
                        rect.top() + top * scale,
                        side * scale,
                    )
                    painter.fillPath(detail, QColor(TINCTURES[tincture]))
    # A sheen from the upper left, as on a painted shield.
    sheen = QLinearGradient(
        rect.topLeft(), QPointF(rect.right(), rect.top() + scale * HEIGHT)
    )
    sheen.setColorAt(0, QColor(255, 255, 255, 34))
    sheen.setColorAt(0.5, QColor(255, 255, 255, 0))
    sheen.setColorAt(1, QColor(0, 0, 0, 40))
    painter.fillPath(outline, sheen)
    painter.setClipping(False)
    pen = QPen(QColor(edge), max(1.0, scale / 40))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.strokePath(outline, pen)
    painter.restore()


def pixmap(arms: Arms, width: int, edge: str, ratio: float = 2.0) -> QPixmap:
    """`arms` as a picture `width` pixels wide."""
    margin = max(1.0, width / 40)
    height = int(width * HEIGHT + 2 * margin) + 1
    full = int(width + 2 * margin) + 1
    picture = QPixmap(int(full * ratio), int(height * ratio))
    picture.setDevicePixelRatio(ratio)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    paint(painter, arms, QRectF(margin, margin, width, width * HEIGHT), edge)
    painter.end()
    return picture
