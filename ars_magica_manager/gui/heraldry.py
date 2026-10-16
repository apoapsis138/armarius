"""Arms on the desktop: the shield painted at any size with painter
paths, from the shield's geometry in arms.py (its outline, the division's
areas and the charge's shapes), with a light sheen and an edge."""

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
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import arms as heraldry
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
from ..markup import escape
from ..models import Covenant, Saga
from .character_sheet import TextBlock, section
from .editing import Run
from .themes import TINCTURES, Palette
from .widgets import serif, text


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


def shield_label(
    arms: Arms, width: int, edge: str, parent: QWidget | None = None
) -> QLabel:
    label = QLabel(parent)
    label.setPixmap(pixmap(arms, width, edge))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


#: The shield's width in an Arms section, and in a row of others' arms.
LARGE, SMALL = 110, 44


def arms_section(record, p: Palette, run: Run) -> QWidget:
    """Arms: the shield, its motto and, smaller under it, its blazon,
    with Edit. The motto is the bearer's own words, so it leads."""
    found = heraldry.arms_of(record)
    body = QWidget()
    row = QHBoxLayout(body)
    row.setContentsMargins(0, 4, 0, 4)
    row.setSpacing(18)
    words = QVBoxLayout()
    words.setSpacing(6)
    if found is None:
        words.addWidget(text("No arms yet.", p["dim"], serif(12.5, italic=True)))
    else:
        row.addWidget(
            shield_label(found, LARGE, p["accent"]), 0, Qt.AlignmentFlag.AlignTop
        )
        if found.motto:
            words.addWidget(
                text(found.motto, p["foreground"], serif(17, italic=True), wrap=True)
            )
        words.addWidget(
            text(
                heraldry.blazon(found), p["label"], serif(12.5, italic=True), wrap=True
            )
        )
        said = heraldry.warning(found)
        if said:
            words.addWidget(TextBlock(f"[$text-warning]{escape(said)}[/]", p))
    words.addStretch(1)
    row.addLayout(words, 1)
    return section(
        "Arms", p, body, edits={"Edit Arms": lambda: run(heraldry.arms_form(record))}
    )


def neighbours_arms(saga: Saga, covenant: Covenant, p: Palette) -> QWidget | None:
    """The arms of the other covenants of the covenant's Tribunal, each
    with its name; None when none of them bears arms."""
    borne = [
        (c, found)
        for c in saga.covenants
        if c is not covenant
        and c.tribunal_id
        and c.tribunal_id == covenant.tribunal_id
        and (found := heraldry.arms_of(c)) is not None
    ]
    if not borne:
        return None
    body = QWidget()
    grid = QGridLayout(body)
    grid.setContentsMargins(0, 4, 0, 4)
    grid.setHorizontalSpacing(22)
    for column, (other, found) in enumerate(borne):
        cell = QWidget()
        stack = QVBoxLayout(cell)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(4)
        shield = shield_label(found, SMALL, p["accent"])
        shield.setToolTip(heraldry.blazon(found))
        stack.addWidget(shield)
        name = text(other.name, p["label"], serif(11))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stack.addWidget(name)
        grid.addWidget(cell, column // 8, column % 8)
    grid.setColumnStretch(min(len(borne), 8), 1)
    return section("Arms of the Tribunal's Covenants", p, body)
