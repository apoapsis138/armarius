"""Painted figures for the desktop pages: the Warping and Decrepitude
dials, Personality Trait bars, the wound track and the Fatigue ladder,
a laboratory's Characteristics compass rose, aura seal and Specialization
bars, and labelled facts and prose in the Codex's type.

Each draws one of the core's plain figures (character_sheet.Dial, Fact,
WoundBand, laboratory_sheet.Characteristic...), so what it shows is the
same as the terminal sheet's text.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import character_sheet as cs
from .. import laboratory_sheet as cs_lab
from . import pictures
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


def fact_grid(facts: Sequence[cs.Fact], p: Palette, columns: int = 3) -> QWidget:
    """Facts as small-caps labels over their values in the book face; a
    value not set is a dim dash, so the ones that are stand out."""
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
        if fact.missing:
            value = text("—", p["dim"], serif(13))
        else:
            value = text(fact.value, p["foreground"], serif(13.5), wrap=True)
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


def trait_list(traits: Sequence[tuple[str, int]], p: Palette) -> QWidget:
    """Traits as name, score and a bar, one under another."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(6)
    if not traits:
        grid.addWidget(text("None recorded.", p["dim"], serif(12, italic=True)), 0, 0)
    for row, (name, score) in enumerate(traits):
        grid.addWidget(text(name, p["foreground"], serif(13)), row, 0)
        number = text(f"{score:+d}", p["heading"], serif(13, bold=True))
        number.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(number, row, 1)
        grid.addWidget(TraitBar(score, p), row, 2)
    grid.setColumnStretch(2, 1)
    return box


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


class AuraSeal(QWidget):
    """The laboratory's aura as a seal in its realm's colour: the total in
    the middle, the realm round it."""

    def __init__(self, aura: cs_lab.Aura, p: Palette) -> None:
        super().__init__()
        self.aura, self.p = aura, p
        self.setFixedSize(96, 104)
        working = f"{aura.covenant} from the covenant, {aura.modifier:+d} here"
        self.setToolTip(
            f"{aura.realm} aura {aura.total}: {working}"
            + (f"\n{aura.note}" if aura.note else "")
        )

    def paintEvent(self, event) -> None:
        p, a = self.p, self.aura
        colour = QColor(p[f"realm-{a.realm}"])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        seal = QRectF(14, 6, 68, 68)
        painter.setPen(QPen(colour, 2))
        painter.setBrush(mix(p["surface"], colour.name(), 0.18))
        painter.drawEllipse(seal)
        painter.setPen(QPen(colour, 1, Qt.PenStyle.DotLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(seal.adjusted(6, 6, -6, -6))
        painter.setPen(QColor(p["foreground"]))
        painter.setFont(serif(22, bold=True))
        painter.drawText(seal, Qt.AlignmentFlag.AlignCenter, str(a.total))
        painter.setPen(QColor(p["label"]))
        painter.setFont(serif(10, caps=True))
        painter.drawText(
            QRectF(0, 78, 96, 16), Qt.AlignmentFlag.AlignCenter, f"{a.realm} Aura"
        )
        painter.end()


def bar_list(
    rows: Sequence[tuple[str, int, bool]], p: Palette, reach: int = 6
) -> QWidget:
    """Names with a score and a bar from the left, one under another; a
    row that doesn't count is dimmed."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(6)
    for row, (name, score, counts) in enumerate(rows):
        ink = p["foreground"] if counts else p["dim"]
        grid.addWidget(text(name, ink, serif(13)), row, 0)
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
