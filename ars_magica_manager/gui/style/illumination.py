"""An illuminated initial, as a scribe paints one to open a book: the
letter in burnished gold on a quartered ground of lapis and vermilion
worked with white pen-work, framed by a plaited knotwork band with a
small knot in each corner.

Everything is painted here, in the manuscript's own pigments rather than
the theme's colours: the gold, ink and pen-work are the same on any page.
A House theme grinds its own ground (palettes.HOUSE_PIGMENTS), and the
glow follows the theme, stronger by candlelight.
"""

from __future__ import annotations

import math
import random

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPaintEvent,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from ...style import fonts
from ...style.palettes import BURNISH, PIGMENTS, Palette, pigments

LAPIS = QColor(PIGMENTS["lapis"])
LAPIS_DEEP = QColor(PIGMENTS["lapis-deep"])
VERMILION = QColor(PIGMENTS["vermilion"])
VERMILION_DEEP = QColor(PIGMENTS["vermilion-deep"])
VERDIGRIS = QColor(PIGMENTS["verdigris"])
VERDIGRIS_LIGHT = QColor(PIGMENTS["verdigris-light"])
INK = QColor(PIGMENTS["ink"])
WHITE = QColor(PIGMENTS["lead-white"])
KNOT_GROUND = QColor(PIGMENTS["knot-ground"])
GOLD = QColor(PIGMENTS["gold"])
GOLD_LIGHT = QColor(PIGMENTS["gold-light"])
GOLD_DARK = QColor(PIGMENTS["gold-dark"])


def gold(rect: QRectF) -> QBrush:
    """Burnished gold across `rect`, corner to corner."""
    gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
    for stop, colour in BURNISH:
        gradient.setColorAt(stop, QColor(colour))
    return QBrush(gradient)


# -- the pen-work on the ground --


def _curl(
    painter: QPainter,
    centre: QPointF,
    radius: float,
    turns: float,
    start: float,
    direction: int,
) -> None:
    """A spiral of white pen-work ending in a dot."""
    path = QPainterPath()
    steps = int(40 * turns)
    for i in range(steps + 1):
        t = i / steps
        angle = start + direction * t * turns * 2 * math.pi
        r = radius * (1 - 0.85 * t)
        point = QPointF(
            centre.x() + r * math.cos(angle), centre.y() + r * math.sin(angle)
        )
        if i:
            path.lineTo(point)
        else:
            path.moveTo(point)
    painter.setPen(QPen(WHITE, 0.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WHITE)
    painter.drawEllipse(path.currentPosition(), 1.1, 1.1)


def _trefoil(painter: QPainter, x: float, y: float, size: float) -> None:
    """Three white dots, the scribe's commonest filler."""
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(WHITE)
    for degrees in (-90, 30, 150):
        a = math.radians(degrees)
        painter.drawEllipse(
            QPointF(x + size * math.cos(a), y + size * math.sin(a)),
            size * 0.9,
            size * 0.9,
        )


def _leaf(painter: QPainter, x: float, y: float, length: float, angle: float) -> None:
    """A pointed leaf with a curled tip and a pale vein."""
    painter.save()
    painter.translate(x, y)
    painter.rotate(angle)
    leaf = QPainterPath(QPointF(0, 0))
    leaf.cubicTo(length * 0.3, -length * 0.45, length * 0.8, -length * 0.35, length, 0)
    leaf.cubicTo(
        length * 0.8,
        length * 0.2,
        length * 0.55,
        length * 0.05,
        length * 0.45,
        length * 0.25,
    )
    leaf.cubicTo(length * 0.35, length * 0.15, length * 0.15, length * 0.3, 0, 0)
    painter.setPen(QPen(INK, 0.8))
    painter.setBrush(VERDIGRIS)
    painter.drawPath(leaf)
    vein = QPainterPath(QPointF(length * 0.08, 0))
    vein.quadTo(length * 0.5, -length * 0.12, length * 0.88, -length * 0.02)
    painter.setPen(QPen(VERDIGRIS_LIGHT, 0.9))
    painter.drawPath(vein)
    painter.restore()


def _flower(painter: QPainter, x: float, y: float, r: float) -> None:
    """A five-petalled white flower with a gold heart."""
    painter.setPen(QPen(INK, 0.7))
    painter.setBrush(WHITE)
    for i in range(5):
        a = math.radians(i * 72 - 90)
        painter.drawEllipse(
            QPointF(x + r * 0.7 * math.cos(a), y + r * 0.7 * math.sin(a)),
            r * 0.55,
            r * 0.55,
        )
    painter.setBrush(GOLD)
    painter.drawEllipse(QPointF(x, y), r * 0.42, r * 0.42)


# -- the knotwork --


def _strand(painter: QPainter, path: QPainterPath, width: float) -> None:
    """A knotwork strand: an ink edge, a gold ribbon with a lighter
    middle, and a fine dark line down its centre."""
    for colour, w in ((INK, width + 2.6), (GOLD, width), (GOLD_LIGHT, width * 0.45)):
        painter.setPen(
            QPen(
                colour,
                w,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.FlatCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
    painter.setPen(QPen(GOLD_DARK, 0.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
    painter.drawPath(path)


def _wave(
    a: QPointF,
    b: QPointF,
    amplitude: float,
    halves: int,
    sign: int,
    t0: float = 0.0,
    t1: float = 1.0,
) -> QPainterPath:
    """Part of a strand weaving from `a` to `b`, from t0 to t1 of the way:
    `halves` half-waves `amplitude` to either side, on side `sign`."""
    dx, dy = b.x() - a.x(), b.y() - a.y()
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    path = QPainterPath()
    steps = max(4, int(120 * (t1 - t0)))
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        off = sign * amplitude * math.sin(math.pi * halves * t)
        point = QPointF(a.x() + dx * t + nx * off, a.y() + dy * t + ny * off)
        if i:
            path.lineTo(point)
        else:
            path.moveTo(point)
    return path


def _plait(
    painter: QPainter,
    a: QPointF,
    b: QPointF,
    amplitude: float,
    halves: int,
    width: float,
) -> None:
    """Two strands plaited from `a` to `b`, each passing over the other in
    turn: the second is drawn whole, then the first redrawn where it
    crosses over."""
    _strand(painter, _wave(a, b, amplitude, halves, -1), width)
    _strand(painter, _wave(a, b, amplitude, halves, 1), width)
    span = 0.32 / halves
    for k in range(1, halves, 2):
        t = k / halves
        _strand(painter, _wave(a, b, amplitude, halves, -1, t - span, t + span), width)


def _corner_knot(painter: QPainter, centre: QPointF, size: float, width: float) -> None:
    """A corner's knot: four loops round a ring, and a garnet."""
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(KNOT_GROUND)
    painter.drawRect(QRectF(centre.x() - size / 2, centre.y() - size / 2, size, size))
    for ax, ay in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        loop = QPainterPath()
        loop.addEllipse(
            QPointF(centre.x() + ax * size * 0.2, centre.y() + ay * size * 0.2),
            size * 0.17,
            size * 0.17,
        )
        _strand(painter, loop, width * 0.8)
    ring = QPainterPath()
    ring.addEllipse(centre, size * 0.26, size * 0.26)
    _strand(painter, ring, width * 0.8)
    garnet = QRadialGradient(centre + QPointF(-0.8, -0.8), size * 0.12)
    garnet.setColorAt(0, QColor(PIGMENTS["garnet-light"]))
    garnet.setColorAt(1, VERMILION_DEEP)
    painter.setPen(QPen(INK, 0.8))
    painter.setBrush(garnet)
    painter.drawEllipse(centre, size * 0.09, size * 0.09)


# -- the whole initial --


def paint_initial(painter: QPainter, outer: QRectF, letter: str, p: Palette) -> None:
    """Paint the illuminated `letter` filling the square `outer`, with a
    glow round it reaching about a tenth of its side beyond."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # The same pen-work every time it is drawn.
    rng = random.Random(7)
    side = outer.width()

    # A glow of gold light, so the panel lifts off the page.
    reach = side / 2 + side * 0.09
    glow = QRadialGradient(outer.center(), reach)
    halo = QColor(PIGMENTS["glow"])
    halo.setAlpha(90 if p.dark else 55)
    glow.setColorAt(0.75, halo)
    halo.setAlpha(0)
    glow.setColorAt(1.0, halo)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(glow)
    painter.drawEllipse(outer.center(), reach, reach)

    rim = side * 0.03
    band = side * 0.11
    band_out = outer.adjusted(rim, rim, -rim, -rim)
    band_in = band_out.adjusted(band, band, -band, -band)
    inner = band_in.adjusted(rim * 0.6, rim * 0.6, -rim * 0.6, -rim * 0.6)

    # The gold rims and the knotwork band's dark ground.
    pigment = pigments(p)
    painter.setBrush(gold(outer))
    painter.drawRect(outer)
    painter.setBrush(QColor(pigment["knot-ground"]))
    painter.drawRect(band_out)
    painter.setBrush(gold(band_in))
    painter.drawRect(band_in)

    _paint_ground(painter, inner, side, rng, pigment)
    _paint_knotwork(painter, band_out, band)

    # Ink lines along every edge of the frame.
    painter.setPen(QPen(INK, 1.2))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for edge in (outer, band_out, band_in, inner):
        painter.drawRect(edge)

    _paint_letter(painter, inner, letter, rng)


def _paint_ground(
    painter: QPainter,
    inner: QRectF,
    side: float,
    rng: random.Random,
    pigment: dict[str, str],
) -> None:
    """The ground, quartered in its two pigments (lapis and vermilion in
    Scriptorum, a House's own in its theme) and darker toward its edges,
    worked with white pen-work, with a leaf and a flower in each corner."""
    cx, cy = inner.center().x(), inner.center().y()
    half_w, half_h = inner.width() / 2, inner.height() / 2
    first = QColor(pigment["lapis"]), QColor(pigment["lapis-deep"])
    second = QColor(pigment["vermilion"]), QColor(pigment["vermilion-deep"])
    for x, y, (light, deep) in (
        (inner.left(), inner.top(), first),
        (cx, inner.top(), second),
        (inner.left(), cy, second),
        (cx, cy, first),
    ):
        shade = QRadialGradient(inner.center(), inner.width() * 0.75)
        shade.setColorAt(0, light)
        shade.setColorAt(1, deep)
        painter.fillRect(QRectF(x, y, half_w, half_h), shade)

    painter.save()
    painter.setClipRect(inner)
    for _ in range(30):
        _curl(
            painter,
            QPointF(
                rng.uniform(inner.left(), inner.right()),
                rng.uniform(inner.top(), inner.bottom()),
            ),
            rng.uniform(4, 8) * side / 210,
            rng.uniform(1.2, 1.8),
            rng.uniform(0, 2 * math.pi),
            rng.choice((-1, 1)),
        )
    for _ in range(70):
        _trefoil(
            painter,
            rng.uniform(inner.left(), inner.right()),
            rng.uniform(inner.top(), inner.bottom()),
            side / 210,
        )
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        ox = cx - sx * inner.width() * 0.40
        oy = cy - sy * inner.height() * 0.40
        _leaf(
            painter,
            ox + sx * side * 0.03,
            oy + sy * side * 0.01,
            side * 0.10,
            (0 if sx > 0 else 180) + sy * 25,
        )
        _flower(painter, ox, oy, side * 0.03)
    painter.restore()


def _paint_knotwork(painter: QPainter, band_out: QRectF, band: float) -> None:
    """The knotwork band inside `band_out`, `band` wide: a plait along
    each side, a knot in each corner."""
    track = band_out.adjusted(band / 2, band / 2, -band / 2, -band / 2)
    width = band * 0.17
    corners = [
        track.topLeft(),
        track.topRight(),
        track.bottomRight(),
        track.bottomLeft(),
    ]
    painter.save()
    painter.setClipRect(band_out)
    for i, start in enumerate(corners):
        end = corners[(i + 1) % 4]
        dx, dy = end.x() - start.x(), end.y() - start.y()
        trim = (band / 2) / math.hypot(dx, dy)
        _plait(
            painter,
            QPointF(start.x() + dx * trim, start.y() + dy * trim),
            QPointF(end.x() - dx * trim, end.y() - dy * trim),
            band * 0.24,
            8,
            width,
        )
    painter.restore()
    for corner in corners:
        _corner_knot(painter, QPointF(corner), band, width)


def _paint_letter(
    painter: QPainter, inner: QRectF, letter: str, rng: random.Random
) -> None:
    """The letter in the title face, in burnished gold: a shadow, a white
    pen-line and an ink edge round it, tooled with fine punched dots, and
    a few glints where the light catches it."""
    font = QFont(fonts.TITLE)
    font.setPixelSize(round(inner.height()))
    shape = QPainterPath()
    shape.addText(0, 0, font, letter)
    shape.translate(inner.center() - shape.boundingRect().center())
    box = shape.boundingRect()
    # The pen widths below are for a letter 144 pixels high.
    scale = inner.width() / 144

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(0, 0, 0, 110))
    painter.drawPath(shape.translated(3 * scale, 4 * scale))
    stroker = QPainterPathStroker()
    stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    stroker.setWidth(7 * scale)
    painter.setBrush(WHITE)
    painter.drawPath(stroker.createStroke(shape).united(shape))
    stroker.setWidth(3.2 * scale)
    painter.setBrush(INK)
    painter.drawPath(stroker.createStroke(shape).united(shape))
    painter.setBrush(gold(box))
    painter.drawPath(shape)

    painter.save()
    painter.setClipPath(shape)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor(255, 250, 220, 170), 1.4 * scale))
    painter.drawPath(shape.translated(-1.6 * scale, -1.6 * scale))
    painter.setPen(QPen(QColor(90, 55, 10, 120), 1.6 * scale))
    painter.drawPath(shape.translated(1.8 * scale, 1.8 * scale))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(120, 80, 15, 110))
    for _ in range(140):
        painter.drawEllipse(
            QPointF(
                rng.uniform(box.left(), box.right()),
                rng.uniform(box.top(), box.bottom()),
            ),
            0.7 * scale,
            0.7 * scale,
        )
    for gx, gy in ((0.40, 0.30), (0.62, 0.58), (0.30, 0.78)):
        at = QPointF(box.left() + box.width() * gx, box.top() + box.height() * gy)
        glint = QRadialGradient(at, 9 * scale)
        glint.setColorAt(0, QColor(255, 255, 255, 230))
        glint.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(glint)
        painter.drawEllipse(at, 9 * scale, 9 * scale)
    painter.restore()


# -- a name's small illuminated initial --

#: A small initial's ground: how far it reaches round the letter, and the
#: gap after it before the rest of the name, as fractions of the font's
#: size.
_GROUND_PAD, _GROUND_GAP = 0.16, 0.10


def _quartered_box(letter: str, font: QFont) -> tuple[QPainterPath, QRectF]:
    """`letter`'s outline in `font` with its baseline at the origin, and
    the square ground round it, its left edge at the origin."""
    shape = QPainterPath()
    shape.addText(0, 0, font, letter)
    box = shape.boundingRect()
    pad = QFontMetricsF(font).height() * _GROUND_PAD
    side = max(box.width(), box.height()) + 2 * pad
    ground = QRectF(0, box.center().y() - side / 2, side, side)
    shape.translate(ground.center().x() - box.center().x(), 0)
    return shape, ground


def quartered_advance(letter: str, font: QFont) -> float:
    """How far quartered_letter's initial in `font` reaches along its
    line, its gap after it included."""
    _shape, ground = _quartered_box(letter, font)
    return ground.width() + QFontMetricsF(font).height() * _GROUND_GAP


def quartered_letter(
    painter: QPainter,
    letter: str,
    font: QFont,
    baseline: QPointF,
    pigment: dict[str, str],
) -> None:
    """`letter` as a small illuminated initial, its ground's left edge at
    `baseline` and the letter on that baseline: a square ground quartered
    in `pigment`'s two colours (a House's, palettes.HOUSE_PIGMENTS), each
    darker toward its edges, in a gold rim and an ink line, and the letter
    on it in burnished gold with an ink edge."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.translate(baseline)
    shape, ground = _quartered_box(letter, font)
    cx, cy = ground.center().x(), ground.center().y()
    half = ground.width() / 2
    first = QColor(pigment["lapis"]), QColor(pigment["lapis-deep"])
    second = QColor(pigment["vermilion"]), QColor(pigment["vermilion-deep"])
    for x, y, (light, deep) in (
        (ground.left(), ground.top(), first),
        (cx, ground.top(), second),
        (ground.left(), cy, second),
        (cx, cy, first),
    ):
        shade = QRadialGradient(ground.center(), ground.width() * 0.75)
        shade.setColorAt(0, light)
        shade.setColorAt(1, deep)
        painter.fillRect(QRectF(x, y, half, half), shade)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(gold(ground), max(1.2, ground.width() * 0.05)))
    painter.drawRect(ground.adjusted(0.6, 0.6, -0.6, -0.6))
    painter.setPen(QPen(INK, 0.8))
    painter.drawRect(ground)
    stroker = QPainterPathStroker()
    stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    stroker.setWidth(max(1.6, ground.width() * 0.06))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(INK)
    painter.drawPath(stroker.createStroke(shape).united(shape))
    painter.setBrush(gold(shape.boundingRect()))
    painter.drawPath(shape)
    painter.restore()


class IlluminatedInitial(QWidget):
    """An illuminated letter `side` pixels square, with room for its glow."""

    def __init__(self, letter: str, p: Palette, side: int = 210) -> None:
        super().__init__()
        self.letter = letter
        self.p = p
        self.set_side(side)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_side(self, side: int) -> None:
        """Draw the letter `side` pixels square."""
        self.side = side
        self.margin = round(side * 0.1)
        self.setFixedSize(side + 2 * self.margin, side + 2 * self.margin)
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        paint_initial(
            painter,
            QRectF(self.margin, self.margin, self.side, self.side),
            self.letter,
            self.p,
        )
        painter.end()
