"""Painted figures for the desktop pages: the Warping and Decrepitude
dials, Personality Trait bars, the wound track and the Fatigue ladder,
a laboratory's Characteristics compass rose, seals (aura, Loyalty),
Specialization bars, a library's book spines, and labelled facts and prose
in the Codex's type.

Each draws one of the core's plain figures (character_sheet.Dial, Fact,
WoundBand, laboratory_sheet.Characteristic...), so what it shows is the
same as the terminal sheet's text.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPen,
    QPolygonF,
    QRadialGradient,
)
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import artwork, world
from .. import character_sheet as cs
from .. import covenant_sheet as cs_cov
from .. import laboratory_sheet as cs_lab
from ..models import Attitude
from . import pictures
from .paper import lift, shade
from .themes import Palette
from .widgets import mix, serif, text

#: How long a dial takes to wind up to its points, in milliseconds.
WIND_MS = 1100


class Dial(QWidget):
    """A score that rises as points gather. The arc fills with the points
    toward the next score, winding up when first shown, and the notches
    around it are those points, one each, lit as they are gained."""

    def __init__(self, dial: cs.Dial, caption: str, colour: str, p: Palette) -> None:
        super().__init__()
        self.dial, self.caption, self.colour, self.p = dial, caption, colour, p
        self.shown = 0.0
        self.setFixedSize(104, 104)
        points = (
            f"{dial.points} of {dial.span} points to {caption} {dial.score + 1}"
            if dial.span
            else "the highest score"
        )
        self.setToolTip(f"{caption} {dial.score}: {points}")
        self.wind = QVariantAnimation(self)
        self.wind.setStartValue(0.0)
        self.wind.setEndValue(dial.fraction if dial.points or not dial.span else 0.0)
        self.wind.setDuration(WIND_MS)
        self.wind.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.wind.valueChanged.connect(self._turn)
        self._wound = False

    def _turn(self, value: float) -> None:
        self.shown = value
        self.update()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._wound:
            self._wound = True
            self.wind.start()

    def _pen(self, colour: QColor | str, width: float) -> QPen:
        pen = QPen(QColor(colour), width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        return pen

    def paintEvent(self, event) -> None:
        p, d = self.p, self.dial
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ring = QRectF(22, 14, 60, 60)
        # A 240-degree arc open at the bottom; angles are in 1/16 degrees,
        # counter-clockwise from three o'clock.
        painter.setPen(self._pen(p["panel"], 7))
        painter.drawArc(ring, 210 * 16, -240 * 16)
        if self.shown > 0:
            painter.setPen(self._pen(self.colour, 7))
            painter.drawArc(ring, 210 * 16, round(-240 * 16 * self.shown))
        # A notch for each point the next score needs, outside the ring.
        centre = ring.center()
        for i in range(d.span):
            angle = 210 - 240 * (i + 0.5) / d.span
            painter.save()
            painter.translate(centre)
            painter.rotate(-angle)
            reached = i < d.points
            colour = self.colour if reached else mix(p["panel"], p["rule"], 0.5)
            painter.setPen(self._pen(colour, 2.5 if d.span <= 20 else 1.5))
            painter.drawLine(38, 0, 43 if reached else 41, 0)
            painter.restore()
        painter.setPen(QColor(p["foreground"]))
        painter.setFont(serif(19, bold=True))
        painter.drawText(ring, Qt.AlignmentFlag.AlignCenter, str(d.score))
        painter.setPen(QColor(p["label"]))
        painter.setFont(serif(8.5))
        points = f"{d.points}/{d.span}" if d.span else "—"
        painter.drawText(QRectF(22, 58, 60, 14), Qt.AlignmentFlag.AlignCenter, points)
        painter.setFont(serif(10, caps=True))
        painter.drawText(
            QRectF(0, 84, 104, 18), Qt.AlignmentFlag.AlignCenter, self.caption
        )
        painter.end()


def fact_grid(
    facts: Sequence[cs.Fact],
    p: Palette,
    columns: int = 3,
    beside: Mapping[str, QWidget] | None = None,
) -> QWidget:
    """Facts as small-caps labels over their values in the book face; a
    value not set is a dim dash, so the ones that are stand out. A widget
    in `beside`, by a fact's label, sits just after its value (a button
    that opens what it names)."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(28)
    grid.setVerticalSpacing(10)
    for i, fact in enumerate(facts):
        cell = QWidget()
        stack = QVBoxLayout(cell)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(0)
        stack.addWidget(text(fact.label, p["label"], serif(9.5, caps=True)))
        extra = (beside or {}).get(fact.label)
        if fact.missing:
            value = text("—", p["dim"], serif(13))
        else:
            # A value with a button after it keeps to one line, beside it.
            value = text(fact.value, p["foreground"], serif(13.5), wrap=extra is None)
        if extra is not None and not fact.missing:
            line = QHBoxLayout()
            line.setContentsMargins(0, 0, 0, 0)
            line.setSpacing(6)
            line.addWidget(value)
            line.addWidget(extra, 0, Qt.AlignmentFlag.AlignVCenter)
            line.addStretch(1)
            stack.addLayout(line)
        else:
            stack.addWidget(value)
        stack.addStretch(1)
        grid.addWidget(cell, i // columns, i % columns)
    for column in range(columns):
        grid.setColumnStretch(column, 1)
    return box


def prose(words: str, p: Palette, *, initial: bool = True) -> QWidget:
    """Free text in the book face, opening with a rubricated initial that
    hangs beside it, as the character's name does; nothing recorded is a
    dim italic line."""
    if not words.strip():
        return text("Nothing recorded yet.", p["dim"], serif(12.5, italic=True))
    body = text(words[1:] if initial else words, p["foreground"], serif(13), wrap=True)
    body.setTextFormat(Qt.TextFormat.PlainText)
    body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    if not initial:
        return body
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(2)
    letter = QLabel(words[0])
    letter.setFont(QFont(pictures.DISPLAY, 30))
    letter.setStyleSheet(f"color:{p['heading']}; background:transparent")
    row.addWidget(letter, 0, Qt.AlignmentFlag.AlignTop)
    row.addWidget(body, 1, Qt.AlignmentFlag.AlignTop)
    return box


class TraitBar(QWidget):
    """A Personality Trait or Reputation's score as a bar out from the
    middle: right for a positive score, left for a negative."""

    REACH = 6  # the score that fills a side

    def __init__(self, score: int, p: Palette) -> None:
        super().__init__()
        self.score, self.p = score, p
        self.setFixedHeight(14)
        self.setMinimumWidth(90)

    def paintEvent(self, event) -> None:
        p = self.p
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(0, 4, self.width(), 6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["panel"]))
        painter.drawRoundedRect(track, 3, 3)
        middle = track.center().x()
        share = min(abs(self.score), self.REACH) / self.REACH * track.width() / 2
        if self.score:
            colour = p["accent"] if self.score > 0 else p["text-error"]
            left = middle if self.score > 0 else middle - share
            painter.setBrush(QColor(colour))
            painter.drawRoundedRect(QRectF(left, 4, share, 6), 3, 3)
        painter.setPen(QPen(QColor(p["rule"]), 1.5))
        painter.drawLine(round(middle), 1, round(middle), 13)
        painter.end()


def trait_list(
    traits: Sequence[tuple[str, int]],
    p: Palette,
    on_choose: Callable[[int], None] | None = None,
) -> QWidget:
    """Traits as name, score and a bar, one under another. With
    `on_choose`, clicking a row chooses it (its index) and outlines it."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(6)
    if not traits:
        grid.addWidget(text("None recorded.", p["dim"], serif(12, italic=True)), 0, 0)
    rows: list[_TraitRow] = []
    for row, (name, score) in enumerate(traits):
        if on_choose is not None:
            band = _TraitRow(row, p, lambda index: _chose(rows, index, on_choose))
            grid.addWidget(band, row, 0, 1, 3)
            rows.append(band)
        label = text(name, p["foreground"], serif(13))
        number = text(f"{score:+d}", p["heading"], serif(13, bold=True))
        number.setAlignment(Qt.AlignmentFlag.AlignRight)
        bar = TraitBar(score, p)
        for column, part in enumerate((label, number, bar)):
            # Clicks go through to the row's band beneath.
            part.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            grid.addWidget(part, row, column)
    grid.setColumnStretch(2, 1)
    return box


def _chose(rows: Sequence[_TraitRow], index: int, on_choose: Callable[[int], None]):
    for row in rows:
        row.chosen = row.index == index
        row.update()
    on_choose(index)


class _TraitRow(QWidget):
    """The band behind one trait's row: clicking it chooses the row, and
    the chosen row is shaded."""

    def __init__(self, index: int, p: Palette, clicked: Callable[[int], None]):
        super().__init__()
        self.index, self.p, self.clicked = index, p, clicked
        self.chosen = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event) -> None:
        self.clicked(self.index)
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        if not self.chosen:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.p["selection"]))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(-4, -2, 4, 2), 4, 4)


class CordFigure(QWidget):
    """A Cord of the bond as a twisted cord of its `metal` with a knot for
    each point of its score: tied knots shine, the cord beyond them is
    still bare thread."""

    TOP = 5
    HEIGHT = 34

    def __init__(self, score: int, metal: str, p: Palette) -> None:
        super().__init__()
        self.score, self.metal, self.p = score, metal, p
        self.setFixedHeight(self.HEIGHT)
        self.setMinimumWidth(160)
        self.setToolTip(f"{score} of {self.TOP}")

    def knots(self) -> list[float]:
        step = (self.width() - 16) / self.TOP
        return [8 + step * (i + 0.5) for i in range(self.TOP)]

    def paintEvent(self, event) -> None:
        p, metal = self.p, self.metal
        dark, light = p["binding-ink"], p["binding-light"]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        knots = self.knots()
        middle = self.HEIGHT / 2
        tied = knots[self.score - 1] if self.score else 0.0
        # Two strands twisted round each other: metal as far as the last
        # knot tied, bare thread after it.
        for phase, shade_to in ((math.pi, dark), (0.0, light)):
            strand = [
                QPointF(x, middle + 3.5 * math.sin(x / 5 + phase))
                for x in range(4, self.width() - 3)
            ]
            for points, reached in (
                ([q for q in strand if q.x() <= tied], True),
                ([q for q in strand if q.x() >= tied], False),
            ):
                if len(points) < 2:
                    continue
                colour = mix(metal, shade_to, 0.35) if reached else QColor(p["rule"])
                painter.setPen(QPen(colour, 2.6 if reached else 1.4))
                painter.drawPolyline(QPolygonF(points))
        for i, x in enumerate(knots):
            centre = QPointF(x, middle)
            if i < self.score:
                shine = QRadialGradient(QPointF(x - 2, middle - 2), 8)
                shine.setColorAt(0, mix(metal, light, 0.6))
                shine.setColorAt(0.5, QColor(metal))
                shine.setColorAt(1, mix(metal, dark, 0.4))
                painter.setPen(QPen(mix(metal, dark, 0.5), 1))
                painter.setBrush(shine)
                painter.drawEllipse(centre, 7.5, 7.5)
            else:
                painter.setPen(QPen(QColor(p["rule"]), 1.2))
                painter.setBrush(QColor(p["panel"]))
                painter.drawEllipse(centre, 4.5, 4.5)
        painter.end()


class _Box(QWidget):
    """One wound band's box: filled in the band's colour when the
    character has a wound of that kind."""

    def __init__(self, count: int, colour: str, p: Palette) -> None:
        super().__init__()
        self.count, self.colour, self.p = count, colour, p
        self.setFixedSize(26, 26)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(self.colour), 1.5))
        painter.setBrush(QColor(self.colour) if self.count else Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(2, 2, 22, 22), 4, 4)
        if self.count > 1:
            painter.setPen(QColor(self.p["background"]))
            painter.setFont(serif(11, bold=True))
            painter.drawText(
                QRectF(2, 2, 22, 22), Qt.AlignmentFlag.AlignCenter, str(self.count)
            )
        painter.end()


def wound_track(bands: Sequence[cs.WoundBand], p: Palette) -> QWidget:
    """The Damage Table as a row of boxes, worse to the right: each with
    the damage that causes it and its penalty."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(14)
    for i, band in enumerate(bands):
        colour = mix(p["text-warning"], p["text-error"], i / max(len(bands) - 1, 1))
        cell = QVBoxLayout()
        cell.setSpacing(2)
        cell.addWidget(
            _Box(band.count, colour.name(), p), 0, Qt.AlignmentFlag.AlignHCenter
        )
        name = text(band.name, p["foreground"], serif(10.5, caps=True))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cell.addWidget(name)
        damage = f"{band.low}–{band.high}" if band.high else f"{band.low}+"
        penalty = f"  ·  {band.penalty:+d}" if band.penalty is not None else ""
        figures = text(damage + penalty, p["label"])
        figures.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cell.addWidget(figures)
        row.addLayout(cell)
    row.addStretch(1)
    return box


def fatigue_ladder(levels: Sequence[tuple[str, int, bool]], p: Palette) -> QWidget:
    """The Fatigue levels left to right, the current one lit."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(4)
    for name, penalty, current in levels:
        words = f"{name} {penalty:+d}" if penalty else name
        step = QLabel(words)
        if current:
            style = (
                f"color:{p['background']}; background:{p['accent']}; font-weight:600;"
            )
        else:
            style = f"color:{p['label']}; background:{p['panel']};"
        step.setStyleSheet(style + " border-radius:4px; padding:3px 8px;")
        row.addWidget(step)
    row.addStretch(1)
    return box


class CompassRose(QWidget):
    """A laboratory's eight Characteristics as the rose of a sea chart:
    a point each, as long as its score, gilt when it adds and red when it
    takes away, inside a ruled ring with the dotted circle at 0."""

    REACH = 6  # the score at the rim, either way
    CENTRE, RADIUS = QPointF(150, 122), 70.0

    def __init__(self, rows: Sequence[cs_lab.Characteristic], p: Palette) -> None:
        super().__init__()
        self.rows, self.p = rows, p
        self.setFixedSize(300, 244)
        self.setToolTip("\n".join(f"{row.name} {row.total:+d}" for row in rows))

    def _length(self, value: float) -> float:
        """How far a point reaches: a stub at -REACH, the rim at +REACH."""
        clamped = max(-self.REACH, min(value, self.REACH))
        return self.RADIUS * (0.3 + 0.7 * (clamped + self.REACH) / (2 * self.REACH))

    def _at(self, degrees: float, distance: float) -> QPointF:
        angle = math.radians(degrees - 90)
        c = self.CENTRE
        return QPointF(
            c.x() + math.cos(angle) * distance, c.y() + math.sin(angle) * distance
        )

    def paintEvent(self, event) -> None:
        p = self.p
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c, r = self.CENTRE, self.RADIUS
        ink = QColor(p["rule"])
        # The ring: two circles with a tick every 10 degrees between them,
        # and the rhumb lines, sixteen of them, out to it.
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(ink, 1))
        for ring in (r + 6, r + 11):
            painter.drawEllipse(c, ring, ring)
        for degrees in range(0, 360, 10):
            painter.drawLine(self._at(degrees, r + 6), self._at(degrees, r + 11))
        faint = QColor(ink)
        faint.setAlpha(140)
        painter.setPen(QPen(faint, 0.8))
        for i in range(16):
            painter.drawLine(c, self._at(i * 22.5, r + 6))
        zero = self._length(0)
        painter.setPen(QPen(ink, 1, Qt.PenStyle.DotLine))
        painter.drawEllipse(c, zero, zero)
        # The points, each in two halves, the darker one clockwise.
        n = len(self.rows)
        for i, row in enumerate(self.rows):
            degrees = 360 * i / n
            colour = p["text-error"] if row.total < 0 else p["accent"]
            tip = self._at(degrees, self._length(row.total))
            left = self._at(degrees - 360 / (2 * n), r * 0.24)
            right = self._at(degrees + 360 / (2 * n), r * 0.24)
            painter.setPen(QPen(mix(colour, p["foreground"], 0.35), 0.8))
            painter.setBrush(mix(colour, p["surface"], 0.55))
            painter.drawPolygon(QPolygonF([c, left, tip]))
            painter.setBrush(QColor(colour))
            painter.drawPolygon(QPolygonF([c, tip, right]))
        # The boss at the centre.
        painter.setPen(QPen(QColor(p["accent"]), 1.5))
        painter.setBrush(QColor(p["surface"]))
        painter.drawEllipse(c, 7, 7)
        painter.setBrush(QColor(p["heading"]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(c, 2.5, 2.5)
        # The names outside the ring.
        painter.setFont(serif(9, caps=True))
        painter.setPen(QColor(p["label"]))
        for i, row in enumerate(self.rows):
            at = self._at(360 * i / n, r + 30)
            painter.drawText(
                QRectF(at.x() - 55, at.y() - 8, 110, 16),
                Qt.AlignmentFlag.AlignCenter,
                row.name,
            )
        painter.end()


class Seal(QWidget):
    """A figure as a wax seal in `colour`: the value in the middle, the
    caption under it. A laboratory's or covenant's aura, a covenant's
    Loyalty."""

    def __init__(
        self, value: str, caption: str, colour: str, tooltip: str, p: Palette
    ) -> None:
        super().__init__()
        self.value, self.caption, self.colour, self.p = value, caption, colour, p
        self.setFixedSize(104, 104)
        self.setToolTip(tooltip)
        lift(self, p, blur=12, drop=2)

    def paintEvent(self, event) -> None:
        p = self.p
        colour = QColor(self.colour)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        seal = QRectF(18, 6, 68, 68)
        painter.setPen(QPen(colour, 2))
        painter.setBrush(mix(p["surface"], colour.name(), 0.18))
        painter.drawEllipse(seal)
        painter.setPen(QPen(colour, 1, Qt.PenStyle.DotLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(seal.adjusted(6, 6, -6, -6))
        painter.setPen(QColor(p["foreground"]))
        painter.setFont(serif(22, bold=True))
        painter.drawText(seal, Qt.AlignmentFlag.AlignCenter, self.value)
        painter.setPen(QColor(p["label"]))
        painter.setFont(serif(10, caps=True))
        painter.drawText(
            QRectF(0, 78, 104, 16), Qt.AlignmentFlag.AlignCenter, self.caption
        )
        painter.end()


def aura_seal(aura: cs_lab.Aura, p: Palette) -> Seal:
    """An aura (a laboratory's or a covenant's) as a seal in its realm's
    colour."""
    working = (
        f"{aura.covenant} from the covenant, {aura.modifier:+d} {aura.modifier_from}"
    )
    return Seal(
        str(aura.total),
        f"{aura.realm} Aura",
        p[f"realm-{aura.realm}"],
        f"{aura.realm} aura {aura.total}: {working}"
        + (f"\n{aura.note}" if aura.note else ""),
        p,
    )


def attitude_seal(attitude: Attitude | None, p: Palette) -> Seal:
    """An attitude toward a player covenant as a seal: the score, its word
    under it, in its colour; the reasons behind it in the tooltip."""
    score = world.attitude_score(attitude)
    return Seal(
        world.signed(score),
        world.attitude_word(score),
        p[world.attitude_colour(score)],
        world.attitude_working(attitude),
        p,
    )


def bar_list(
    rows: Sequence[tuple[str, int, bool]],
    p: Palette,
    on_choose: Callable[[int], None] | None = None,
    reach: int = 6,
) -> QWidget:
    """Names with a score and a bar from the left, one under another; a
    row that doesn't count is dimmed. Clicking a name calls `on_choose`
    with its row."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(6)
    for row, (name, score, counts) in enumerate(rows):
        ink = p["foreground"] if counts else p["dim"]
        label = text(name, ink, serif(13))
        if on_choose is not None:
            label.setCursor(Qt.CursorShape.PointingHandCursor)
            label.mousePressEvent = lambda _event, row=row: on_choose(row)
        grid.addWidget(label, row, 0)
        number = text(
            f"{score:+d}", p["heading"] if counts else p["dim"], serif(13, bold=True)
        )
        number.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(number, row, 1)
        grid.addWidget(_Bar(score / reach, p, counts), row, 2)
    grid.setColumnStretch(2, 1)
    return box


class _Bar(QWidget):
    def __init__(self, share: float, p: Palette, lit: bool) -> None:
        super().__init__()
        self.share, self.p, self.lit = max(0.0, min(share, 1.0)), p, lit
        self.setFixedHeight(14)
        self.setMinimumWidth(90)

    def paintEvent(self, event) -> None:
        p = self.p
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["panel"]))
        painter.drawRoundedRect(QRectF(0, 4, self.width(), 6), 3, 3)
        if self.share:
            painter.setBrush(QColor(p["accent"] if self.lit else p["dim"]))
            painter.drawRoundedRect(QRectF(0, 4, self.width() * self.share, 6), 3, 3)
        painter.end()


#: The leathers a book can be bound in, as palette keys.
_LEATHERS = (
    "season-lab",
    "season-study",
    "season-writing",
    "season-work",
    "season-adventure",
)


def _spine_lines(title: str, metrics: QFontMetricsF, length: float) -> list[str]:
    """`title` on one line if it fits in `length`, else on two, the
    second cut short with an ellipsis if it is still too long."""
    if metrics.horizontalAdvance(title) <= length:
        return [title]
    words = title.split()
    first = words[0]
    rest = words[1:]
    while rest and metrics.horizontalAdvance(f"{first} {rest[0]}") <= length:
        first = f"{first} {rest.pop(0)}"
    if metrics.horizontalAdvance(first) > length:
        first = metrics.elidedText(first, Qt.TextElideMode.ElideRight, length)
    second = metrics.elidedText(" ".join(rest), Qt.TextElideMode.ElideRight, length)
    return [first, second] if second else [first]


class BookSpine(QWidget):
    """A book standing on a shelf: bound in a muted leather picked by its
    subject, as wide as its kind is thick (a summa stout, a lab text slim),
    a summa as tall as its level, with raised bands, its Art's symbol and
    its title tooled in gilt up the spine, on two lines when it is long
    (the book bound thicker to hold them), and its level and quality at
    the foot; clicking it calls `clicked`."""

    #: The title's size up the spine, in points.
    TITLE_SIZE = 10.5

    def __init__(self, spine: cs_cov.Spine, p: Palette) -> None:
        super().__init__()
        self.spine, self.p = spine, p
        self.clicked: Callable[[], None] = lambda: None
        self.hovered = False
        book = spine.book
        tall = 176 + 3 * min(spine.level or 0, 20)
        width, height = {
            "Art Summa": (48, tall),
            "Ability Summa": (46, tall),
            "Tractatus": (40, 186),
            "Lab Text": (36, 170),
            "Casting Tablet": (48, 96),
        }.get(book.type, (42, 190))
        # The title runs up the spine below the Art's symbol and above the
        # numbers; a title too long for one line takes two, and a book
        # with a two-line title is bound thicker to hold them.
        metrics = QFontMetricsF(serif(self.TITLE_SIZE))
        length = height - 36 - (20 + (26 if spine.art else 0)) - 8
        self.lines = _spine_lines(book.name, metrics, length)
        width = max(width, int(len(self.lines) * metrics.lineSpacing()) + 14)
        self.setFixedSize(width + 2, height + 2)
        self.body = QRectF(1, 1, width, height)
        key = spine.subject or book.name
        tint = p[_LEATHERS[sum(map(ord, key)) % len(_LEATHERS)]]
        self.leather = mix(mix(tint, p["leather"], 0.5).name(), p["binding-ink"], 0.12)
        numbers = [
            *([f"Level {spine.level}"] if spine.level is not None else []),
            *([f"Quality {spine.quality}"] if spine.quality is not None else []),
        ]
        self.setToolTip(
            "\n".join(
                [
                    book.name,
                    book.type + (f" on {spine.subject}" if spine.subject else ""),
                ]
                + (["  ·  ".join(numbers)] if numbers else [])
            )
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event) -> None:
        self.hovered = True
        self.update()

    def leaveEvent(self, event) -> None:
        self.hovered = False
        self.update()

    def mousePressEvent(self, event) -> None:
        self.clicked()

    def paintEvent(self, event) -> None:
        p, body, spine = self.p, self.body, self.spine
        hide = self.leather.name()
        gilt = mix(p["accent"], p["gilt"], 0.25)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        edge = gilt if self.hovered else mix(hide, p["binding-ink"], 0.45)
        painter.setPen(QPen(edge, 1.5 if self.hovered else 1))
        painter.setBrush(self.leather)
        painter.drawRoundedRect(body, 2, 2)
        # Raised bands: a dark groove with a lighter ridge under it.
        for y in (body.top() + 12, body.bottom() - 30):
            painter.setPen(QPen(mix(hide, p["binding-ink"], 0.4), 2))
            painter.drawLine(QPointF(body.left() + 1, y), QPointF(body.right() - 1, y))
            painter.setPen(QPen(mix(hide, p["binding-light"], 0.12), 1))
            painter.drawLine(
                QPointF(body.left() + 1, y + 2), QPointF(body.right() - 1, y + 2)
            )
        # Gilt fillets at the head and the foot.
        painter.setPen(QPen(gilt, 0.8))
        for y in (body.top() + 6, body.bottom() - 6):
            painter.drawLine(QPointF(body.left() + 3, y), QPointF(body.right() - 3, y))
        top = body.top() + 20
        if spine.art:
            side = min(body.width() - 14, 20)
            symbol = pictures.pixmap(
                artwork.art_symbol(spine.art), gilt.name(), int(side), 2.0
            )
            painter.drawPixmap(
                QRectF(body.center().x() - side / 2, top, side, side),
                symbol,
                QRectF(symbol.rect()),
            )
            top += side + 6
        numbers = " ".join(
            [
                *([f"L{spine.level}"] if spine.level is not None else []),
                *([f"Q{spine.quality}"] if spine.quality is not None else []),
            ]
        )
        painter.setFont(serif(8.5))
        painter.setPen(gilt)
        painter.drawText(
            QRectF(body.left(), body.bottom() - 27, body.width(), 15),
            Qt.AlignmentFlag.AlignCenter,
            numbers,
        )
        # The title up the spine, on its one or two lines.
        area = QRectF(body.left() + 4, top, body.width() - 8, body.bottom() - 36 - top)
        painter.save()
        painter.translate(area.left(), area.bottom())
        painter.rotate(-90)
        painter.setFont(serif(self.TITLE_SIZE))
        painter.drawText(
            QRectF(4, 1, area.height() - 8, area.width() - 2),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            "\n".join(self.lines),
        )
        painter.restore()
        # The rounded back: lit down its left, falling into shade on its right.
        light, dark = p["binding-light"], p["binding-ink"]
        round_ = QLinearGradient(body.topLeft(), body.topRight())
        round_.setColorAt(0, shade(dark, 70))
        round_.setColorAt(0.18, shade(light, 26))
        round_.setColorAt(0.45, shade(light, 0))
        round_.setColorAt(0.8, shade(dark, 30))
        round_.setColorAt(1, shade(dark, 95))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(round_)
        painter.drawRoundedRect(body, 2, 2)
        # The leather's scuffs, the same each time it is drawn.
        chance = random.Random(sum(map(ord, spine.book.name)))
        for _ in range(int(body.width() * body.height() / 18)):
            if chance.random() < 0.6:
                painter.setPen(shade(dark, chance.randint(8, 26)))
            else:
                painter.setPen(shade(light, chance.randint(4, 12)))
            painter.drawPoint(
                QPointF(
                    chance.uniform(body.left() + 1, body.right() - 1),
                    chance.uniform(body.top() + 1, body.bottom() - 1),
                )
            )
        painter.end()


class Bookcase(QWidget):
    """Books standing side by side on wooden shelves, as many to a shelf as
    the page is wide: narrowing the window moves books down a shelf."""

    MARGIN, GAP, PLANK, BETWEEN = 12, 2, 9, 18

    def __init__(self, spines: Sequence[cs_cov.Spine], p: Palette) -> None:
        super().__init__()
        self.p = p
        self.books = [BookSpine(spine, p) for spine in spines]
        for book in self.books:
            book.setParent(self)
        self.rows: list[tuple[float, float]] = []
        self._arrange(self.width())

    def _shelves(self, width: int) -> list[list[BookSpine]]:
        rows: list[list[BookSpine]] = [[]]
        used = self.MARGIN
        for book in self.books:
            if rows[-1] and used + book.width() > width - self.MARGIN:
                rows.append([])
                used = self.MARGIN
            rows[-1].append(book)
            used += book.width() + self.GAP
        return rows

    def _arrange(self, width: int) -> None:
        self.rows = []
        y = 0
        for row in self._shelves(max(width, 200)):
            tallest = max((book.height() for book in row), default=0)
            floor = y + 10 + tallest
            x = self.MARGIN
            for book in row:
                book.move(x, floor - book.height())
                x += book.width() + self.GAP
            self.rows.append((y, floor))
            y = floor + self.PLANK + self.BETWEEN
        self.setFixedHeight(max(y - self.BETWEEN, 0))

    def resizeEvent(self, event) -> None:
        self._arrange(event.size().width())

    def paintEvent(self, event) -> None:
        p, width = self.p, self.width()
        wall, wood = p["shelf-back"], p["shelf-plank"]
        dark, light = p["binding-ink"], p["binding-light"]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        for top, floor in self.rows:
            # The back wall, in shadow under the shelf above.
            back = QRectF(0, top, width, floor - top)
            fall = QLinearGradient(back.topLeft(), back.bottomLeft())
            fall.setColorAt(0, mix(wall, dark, 0.45))
            fall.setColorAt(0.35, QColor(wall))
            fall.setColorAt(1, mix(wall, dark, 0.15))
            painter.setBrush(fall)
            painter.drawRect(back)
            for outside, inside in ((0, 10), (width, width - 10)):
                side = QLinearGradient(QPointF(outside, 0), QPointF(inside, 0))
                side.setColorAt(0, shade(dark, 110))
                side.setColorAt(1, shade(dark, 0))
                painter.setBrush(side)
                painter.drawRect(QRectF(min(outside, inside), top, 10, floor - top))
            # Each book's shadow on the wall behind it.
            for book in self.books:
                cover = book.geometry()
                if not top <= cover.top() < floor:
                    continue
                cast = QLinearGradient(
                    QPointF(cover.right(), 0), QPointF(cover.right() + 7, 0)
                )
                cast.setColorAt(0, shade(dark, 90))
                cast.setColorAt(1, shade(dark, 0))
                painter.setBrush(cast)
                painter.drawRect(
                    QRectF(cover.right(), cover.top() + 4, 7, cover.height() - 4)
                )
            # The plank: lit along its edge, its shadow falling below.
            plank = QRectF(0, floor, width, self.PLANK)
            lit = QLinearGradient(plank.topLeft(), plank.bottomLeft())
            lit.setColorAt(0, mix(wood, light, 0.25))
            lit.setColorAt(0.25, QColor(wood))
            lit.setColorAt(1, mix(wood, dark, 0.35))
            painter.setBrush(lit)
            painter.drawRect(plank)
            under = QLinearGradient(plank.bottomLeft(), QPointF(0, plank.bottom() + 8))
            under.setColorAt(0, shade(dark, 70))
            under.setColorAt(1, shade(dark, 0))
            painter.setBrush(under)
            painter.drawRect(QRectF(0, plank.bottom(), width, 8))
        painter.end()


def shelf(
    spines: Sequence[cs_cov.Spine],
    p: Palette,
    on_choose: Callable[[cs_cov.Spine], None],
) -> QWidget:
    """A bookcase of `spines`; clicking a book calls `on_choose` with it."""
    case = Bookcase(spines, p)
    for figure in case.books:
        figure.clicked = lambda spine=figure.spine: on_choose(spine)
    return case
