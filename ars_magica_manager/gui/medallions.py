"""The season medallions, drawn: six sets of roundels (medallions.SETS),
each a painter keyed by its set (a Strategy), all drawn in code.

The glass, enamel, wax and illumination keep their own pigments on either
theme, as the illuminated initial does; only the rings and ink of the
quieter sets, and the present season's glow, follow the theme.

Screens draw a season through paint_season or the Medallion widget, which
take the saga and look up its set; they rest in the window's headpiece,
the Seasons page, Ahead, the covenant's header and Seasons chapter, a
character's This Season, the calendars and a siege's track.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from armarius_style.desktop.illumination import gold
from armarius_style.desktop.ornaments import Headpiece
from armarius_style.desktop.paper import shade
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPaintEvent,
    QPen,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import QHBoxLayout, QWidget

from .. import medallions
from ..models import Saga
from .pictures import SERIF
from .themes import DRAWN, PIGMENTS, SEASON_PIGMENTS, Palette

LEAD = QColor(DRAWN["lead"])
INK = QColor(PIGMENTS["ink"])
WHITE = QColor(PIGMENTS["lead-white"])
LAPIS, LAPIS_DEEP = QColor(PIGMENTS["lapis"]), QColor(PIGMENTS["lapis-deep"])
VERMILION = QColor(PIGMENTS["vermilion"])
VERMILION_DEEP = QColor(PIGMENTS["vermilion-deep"])
VERDIGRIS = QColor(PIGMENTS["verdigris"])
GOLD, GOLD_LIGHT, GOLD_DARK = (
    QColor(PIGMENTS["gold"]),
    QColor(PIGMENTS["gold-light"]),
    QColor(PIGMENTS["gold-dark"]),
)
COPPER = QColor(DRAWN["copper"])


def _font(size: float, *, bold: bool = False) -> QFont:
    f = QFont(SERIF)
    f.setPointSizeF(size)
    f.setBold(bold)
    return f


# -- the four emblems, as paths in a unit circle --


def _stroke(path: QPainterPath, width: float) -> QPainterPath:
    s = QPainterPathStroker()
    s.setWidth(width)
    s.setCapStyle(Qt.PenCapStyle.RoundCap)
    s.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return s.createStroke(path)


def _spring() -> QPainterPath:
    """A five-petalled flower on a stem with two leaves."""
    path = QPainterPath()
    for i in range(5):
        a = math.radians(i * 72 - 90)
        petal = QPainterPath()
        petal.addEllipse(
            QPointF(0.26 * math.cos(a), -0.22 + 0.26 * math.sin(a)), 0.2, 0.2
        )
        path = path.united(petal)
    stem = QPainterPath(QPointF(0, -0.05))
    stem.cubicTo(0.05, 0.25, -0.05, 0.45, 0, 0.75)
    path = path.united(_stroke(stem, 0.08))
    for sign in (-1, 1):
        leaf = QPainterPath(QPointF(0, 0.5))
        leaf.cubicTo(sign * 0.2, 0.25, sign * 0.5, 0.3, sign * 0.55, 0.38)
        leaf.cubicTo(sign * 0.45, 0.55, sign * 0.2, 0.6, 0, 0.5)
        path = path.united(leaf)
    return path.simplified()


def _summer() -> QPainterPath:
    """The sun with sixteen rays, long and short by turns."""
    path = QPainterPath()
    path.addEllipse(QPointF(0, 0), 0.38, 0.38)
    for i in range(16):
        a = math.radians(i * 22.5)
        ray = QPainterPath()
        r0, r1, w = 0.42, (0.85 if i % 2 == 0 else 0.68), 0.09
        ray.moveTo(r0 * math.cos(a - w), r0 * math.sin(a - w))
        ray.lineTo(r1 * math.cos(a), r1 * math.sin(a))
        ray.lineTo(r0 * math.cos(a + w), r0 * math.sin(a + w))
        ray.closeSubpath()
        path = path.united(ray)
    return path.simplified()


def _autumn() -> QPainterPath:
    """A bunch of grapes under a vine leaf."""
    path = QPainterPath()
    for y, n in ((-0.05, 3), (0.22, 3), (0.46, 2), (0.66, 1)):
        for k in range(n):
            berry = QPainterPath()
            berry.addEllipse(QPointF((k - (n - 1) / 2) * 0.27, y), 0.14, 0.14)
            path = path.united(berry)
    leaf = QPainterPath()
    leaf.moveTo(0.02, -0.18)
    leaf.cubicTo(0.2, -0.3, 0.45, -0.3, 0.6, -0.55)
    leaf.cubicTo(0.45, -0.58, 0.4, -0.7, 0.3, -0.8)
    leaf.cubicTo(0.2, -0.65, 0.1, -0.72, 0.05, -0.62)
    leaf.cubicTo(0.0, -0.45, 0.02, -0.3, 0.02, -0.18)
    path = path.united(leaf)
    stem = QPainterPath(QPointF(0, -0.15))
    stem.quadTo(-0.15, -0.45, -0.3, -0.6)
    return path.united(_stroke(stem, 0.07)).simplified()


def _winter() -> QPainterPath:
    """A six-armed snow-star, each arm branched."""
    lines = QPainterPath()
    for i in range(6):
        a = math.radians(i * 60 - 90)
        ca, sa = math.cos(a), math.sin(a)
        lines.moveTo(0, 0)
        lines.lineTo(0.82 * ca, 0.82 * sa)
        for r, length in ((0.42, 0.2), (0.62, 0.14)):
            for side in (-1, 1):
                b = a + side * math.radians(45)
                lines.moveTo(r * ca, r * sa)
                lines.lineTo(
                    r * ca + length * math.cos(b), r * sa + length * math.sin(b)
                )
    hub = QPainterPath()
    hub.addEllipse(QPointF(0, 0), 0.14, 0.14)
    return _stroke(lines, 0.09).united(hub).simplified()


_EMBLEMS: dict[str, QPainterPath] = {}
_MAKERS: dict[str, Callable[[], QPainterPath]] = {
    "Spring": _spring,
    "Summer": _summer,
    "Autumn": _autumn,
    "Winter": _winter,
}


def emblem(season: str) -> QPainterPath:
    """The season's emblem in a unit circle (Spring for an unknown one)."""
    key = season if season in _MAKERS else "Spring"
    if key not in _EMBLEMS:
        _EMBLEMS[key] = _MAKERS[key]()
    return _EMBLEMS[key]


def _placed(path: QPainterPath, c: QPointF, r: float) -> QPainterPath:
    return QTransform().translate(c.x(), c.y()).scale(r, r).map(path)


def _circle(c: QPointF, r: float) -> QPainterPath:
    path = QPainterPath()
    path.addEllipse(c, r, r)
    return path


def _flower_heart(season: str, c: QPointF, r: float) -> QPointF:
    """Where the Spring flower's heart sits in an emblem of radius `r`."""
    return c + QPointF(0, -0.22 * r) if season == "Spring" else c


# -- 1. stained glass --

GLASS = SEASON_PIGMENTS["glass"]


def _glass(colour: str, c: QPointF, r: float, rng: random.Random) -> QBrush:
    base = QColor(colour)
    k = rng.uniform(-18, 18)
    base = base.lighter(int(100 + k)) if k > 0 else base.darker(int(100 - k))
    grad = QRadialGradient(c + QPointF(-r * 0.3, -r * 0.3), r * 1.6)
    grad.setColorAt(0, base.lighter(150))
    grad.setColorAt(0.5, base)
    grad.setColorAt(1, base.darker(135))
    return QBrush(grad)


def stained_glass(
    g: QPainter, c: QPointF, r: float, season: str, _year: int, _p: Palette
) -> None:
    """Leaded panes, a ring and a field, the emblem in its own glass."""
    rng = random.Random(season)
    field, field2, ring, emb = GLASS.get(season, GLASS["Spring"])
    width = max(1.2, r * 0.06)
    lead = QPen(
        LEAD,
        width,
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin,
    )
    outer = QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r)
    ri = r * 0.8
    inner = QRectF(c.x() - ri, c.y() - ri, 2 * ri, 2 * ri)
    for i in range(12):
        a0, a1 = i * 30, (i + 1) * 30
        pane = QPainterPath()
        pane.arcMoveTo(outer, a0)
        pane.arcTo(outer, a0, a1 - a0)
        pane.arcTo(inner, a1, a0 - a1)
        pane.closeSubpath()
        g.setBrush(_glass(ring if i % 2 == 0 else field2, c, r, rng))
        g.setPen(lead)
        g.drawPath(pane)
    angles = sorted(rng.uniform(0, 360) for _ in range(7))
    for i, a0 in enumerate(angles):
        a1 = angles[(i + 1) % len(angles)] + (360 if i == len(angles) - 1 else 0)
        pane = QPainterPath(c)
        pane.arcTo(inner, a0, a1 - a0)
        pane.closeSubpath()
        g.setBrush(_glass(field, c, ri, rng))
        g.drawPath(pane)
    e = _placed(emblem(season), c, ri * 0.82)
    g.setBrush(_glass(emb, c, ri * 0.7, rng))
    g.setPen(QPen(LEAD, width * 0.8))
    g.drawPath(e)
    if season == "Spring":
        g.setBrush(_glass(DRAWN["glass-gold"], c, 10, rng))
        g.drawEllipse(_flower_heart(season, c, ri * 0.82), ri * 0.1, ri * 0.1)
    g.save()
    g.setClipPath(_circle(c, r))
    for k in range(3):
        sheen = QLinearGradient(
            c + QPointF(-r, -r + k * r * 0.75), c + QPointF(r, r + k * r * 0.75)
        )
        sheen.setColorAt(0.45, QColor(255, 255, 255, 0))
        sheen.setColorAt(0.5, QColor(255, 255, 255, 38))
        sheen.setColorAt(0.55, QColor(255, 255, 255, 0))
        g.fillRect(outer, QBrush(sheen))
    g.restore()
    g.setBrush(Qt.BrushStyle.NoBrush)
    g.setPen(QPen(LEAD, width * 1.5))
    g.drawEllipse(c, r, r)


# -- 2. as an illuminated letter is adorned --


def _strand(g: QPainter, path: QPainterPath, width: float) -> None:
    """A gold strand of knotwork: an ink edge, gold, a lighter middle."""
    for colour, w in ((INK, width + 2.2), (GOLD, width), (GOLD_LIGHT, width * 0.45)):
        g.setPen(QPen(colour, w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawPath(path)


def _leaf(g: QPainter, at: QPointF, length: float, angle: float) -> None:
    """An ivy leaf in verdigris with an ink edge."""
    g.save()
    g.translate(at)
    g.rotate(angle)
    leaf = QPainterPath(QPointF(0, 0))
    leaf.cubicTo(length * 0.3, -length * 0.45, length * 0.8, -length * 0.35, length, 0)
    leaf.cubicTo(length * 0.8, length * 0.35, length * 0.3, length * 0.45, 0, 0)
    g.setPen(QPen(INK, 0.8))
    g.setBrush(VERDIGRIS)
    g.drawPath(leaf)
    g.restore()


def _penwork(g: QPainter, c: QPointF, r: float, rng: random.Random) -> None:
    """White pen-work on the ground: little curls and trefoils of dots."""
    g.setPen(QPen(WHITE, max(0.6, r * 0.012)))
    g.setBrush(Qt.BrushStyle.NoBrush)
    for _ in range(10):
        at = c + QPointF(rng.uniform(-r, r), rng.uniform(-r, r))
        size = rng.uniform(0.05, 0.09) * r
        g.drawArc(QRectF(at.x() - size, at.y() - size, 2 * size, 2 * size), 0, 270 * 16)
    g.setPen(Qt.PenStyle.NoPen)
    g.setBrush(WHITE)
    dot = max(0.6, r * 0.015)
    for _ in range(26):
        at = c + QPointF(rng.uniform(-r, r), rng.uniform(-r, r))
        for degrees in (-90, 30, 150):
            a = math.radians(degrees)
            g.drawEllipse(at + QPointF(dot * math.cos(a), dot * math.sin(a)), dot, dot)


def illuminated(
    g: QPainter, c: QPointF, r: float, season: str, _year: int, _p: Palette
) -> None:
    """The initial's quartered lapis and vermilion with white pen-work, the
    emblem in burnished gold, a plaited band and ivy sprays."""
    rng = random.Random(season + "i")
    for ang in (-30, 30, 150, 210):
        a = math.radians(ang)
        base = c + QPointF(r * 0.95 * math.cos(a), r * 0.95 * math.sin(a))
        tip = c + QPointF(r * 1.45 * math.cos(a), r * 1.45 * math.sin(a))
        bend = c + QPointF(r * 1.25 * math.cos(a + 0.25), r * 1.25 * math.sin(a + 0.25))
        vine = QPainterPath(base)
        vine.quadTo(bend, tip)
        g.setPen(QPen(INK, 1.2))
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawPath(vine)
        _leaf(g, tip, r * 0.22, ang + 20)
        berry = c + QPointF(
            r * 1.22 * math.cos(a + 0.12), r * 1.22 * math.sin(a + 0.12)
        )
        g.setPen(QPen(INK, 0.6))
        g.setBrush(gold(QRectF(berry.x() - 4, berry.y() - 4, 8, 8)))
        g.drawEllipse(berry, r * 0.06, r * 0.06)
    ri = r * 0.8
    g.save()
    g.setClipPath(_circle(c, ri))
    quarters = ((LAPIS, LAPIS_DEEP), (VERMILION, VERMILION_DEEP))
    for (x, y), which in zip(
        ((0, 0), (1, 0), (0, 1), (1, 1)), (0, 1, 1, 0), strict=True
    ):
        light, deep = quarters[which]
        grad = QRadialGradient(c, ri)
        grad.setColorAt(0, light)
        grad.setColorAt(1, deep)
        g.fillRect(
            QRectF(c.x() - ri + x * ri, c.y() - ri + y * ri, ri, ri), QBrush(grad)
        )
    _penwork(g, c, ri, rng)
    g.restore()
    e = _placed(emblem(season), c, ri * 0.8)
    g.setPen(QPen(INK, 1.3))
    g.setBrush(gold(e.boundingRect()))
    g.drawPath(e)
    width = max(1.2, r * 0.05)
    for sign in (-1, 1):
        band = QPainterPath()
        for k in range(181):
            t = k / 180 * 2 * math.pi
            rr = r * 0.9 + sign * r * 0.06 * math.sin(t * 9)
            pt = c + QPointF(rr * math.cos(t), rr * math.sin(t))
            if k:
                band.lineTo(pt)
            else:
                band.moveTo(pt)
        band.closeSubpath()
        _strand(g, band, width)
    g.setPen(QPen(INK, 1.1))
    g.setBrush(Qt.BrushStyle.NoBrush)
    g.drawEllipse(c, ri, ri)
    g.drawEllipse(c, r, r)


# -- 3. a wax seal --

WAX = SEASON_PIGMENTS["wax"]


def _wax(g: QPainter, c: QPointF, r: float, colour: QColor, rng: random.Random) -> None:
    """A pool of wax, its rim a little uneven, lit from the upper left and
    casting a soft shadow."""
    blob = QPainterPath()
    wobble = rng.uniform(0, 1)
    for k in range(73):
        t = k / 72 * 2 * math.pi
        rr = r * (1.0 + 0.05 * math.sin(t * 5 + wobble) + 0.03 * math.sin(t * 11))
        pt = c + QPointF(rr * math.cos(t), rr * math.sin(t))
        if k:
            blob.lineTo(pt)
        else:
            blob.moveTo(pt)
    blob.closeSubpath()
    g.fillPath(blob.translated(r * 0.05, r * 0.07), QBrush(QColor(60, 40, 20, 70)))
    grad = QRadialGradient(c + QPointF(-r * 0.3, -r * 0.35), r * 1.4)
    grad.setColorAt(0, colour.lighter(150))
    grad.setColorAt(0.6, colour)
    grad.setColorAt(1, colour.darker(160))
    g.fillPath(blob, QBrush(grad))


def _pressed_ring(
    g: QPainter, c: QPointF, r: float, width: float, colour: QColor
) -> None:
    """A ring the matrix pressed into the wax: dark, with light below it."""
    g.setBrush(Qt.BrushStyle.NoBrush)
    g.setPen(QPen(colour.darker(170), width))
    g.drawEllipse(c, r, r)
    g.setPen(QPen(colour.lighter(140), 1))
    g.drawEllipse(c + QPointF(1, 1), r, r)


#: The wax a member's seal is pressed in: the red of the summer seal.
MEMBER_WAX = QColor(WAX["Summer"])


def member_seal(
    g: QPainter, c: QPointF, r: float, mark: QPixmap | None, initial: str
) -> None:
    """A magus's seal on a charter, as the wax seal medallions are drawn:
    a pool of red wax, the matrix's rim pressed into it, and in its heart
    his House's symbol (`mark`, drawn in a dark tint of the wax at 2r
    across), or his initial when he has none."""
    g.save()
    g.setRenderHint(QPainter.RenderHint.Antialiasing)
    colour = MEMBER_WAX
    _wax(g, c, r, colour, random.Random(initial + "seal"))
    _pressed_ring(g, c, r * 0.8, max(1.0, r * 0.07), colour)
    if mark is not None:
        side = mark.width() / mark.devicePixelRatio()
        corner = c - QPointF(side / 2, side / 2)
        g.drawPixmap(corner + QPointF(0.8, 0.8), _tinted(mark, colour.lighter(150)))
        g.drawPixmap(corner, _tinted(mark, colour.darker(185)))
    else:
        g.setFont(_font(max(6.0, r * 0.75), bold=True))
        box = QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r)
        g.setPen(colour.lighter(150))
        g.drawText(box.translated(0.8, 0.8), Qt.AlignmentFlag.AlignCenter, initial)
        g.setPen(colour.darker(185))
        g.drawText(box, Qt.AlignmentFlag.AlignCenter, initial)
    g.restore()


def _tinted(mark: QPixmap, colour: QColor) -> QPixmap:
    """`mark` (one colour on clear) in `colour`."""
    out = QPixmap(mark.size())
    out.setDevicePixelRatio(mark.devicePixelRatio())
    out.fill(Qt.GlobalColor.transparent)
    g = QPainter(out)
    g.drawPixmap(0, 0, mark)
    g.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    g.fillRect(out.rect(), colour)
    g.end()
    return out


def empty_seal(g: QPainter, c: QPointF, r: float, p: Palette) -> None:
    """Where a member who hasn't sworn yet would seal: a dashed ring."""
    g.save()
    g.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(p["label"]), max(1.0, r * 0.06))
    pen.setStyle(Qt.PenStyle.DashLine)
    g.setPen(pen)
    g.setBrush(Qt.BrushStyle.NoBrush)
    g.drawEllipse(c, r * 0.92, r * 0.92)
    g.restore()


def wax_seal(
    g: QPainter, c: QPointF, r: float, season: str, year: int, _p: Palette
) -> None:
    """The season pressed in coloured wax, its Latin name and the year in
    Roman numerals round the rim."""
    colour = QColor(WAX.get(season, WAX["Spring"]))
    _wax(g, c, r, colour, random.Random(season + "w"))
    for rr, w in ((r * 0.82, 2.0), (r * 0.6, 1.6)):
        _pressed_ring(g, c, rr, w, colour)
    legend = f"+ {medallions.LATIN.get(season, '')} · {medallions.roman(year)} ·"
    g.setFont(_font(max(5.0, r * 0.18), bold=True))
    step = 300 / max(1, len(legend))
    box = r * 0.12
    for i, ch in enumerate(legend):
        a = math.radians(-90 - 150 + i * step)
        g.save()
        g.translate(c + QPointF(r * 0.71 * math.cos(a), r * 0.71 * math.sin(a)))
        g.rotate(math.degrees(a) + 90)
        cell = QRectF(-box, -box, 2 * box, 2 * box)
        g.setPen(colour.lighter(140))
        g.drawText(cell.translated(0.8, 0.8), Qt.AlignmentFlag.AlignCenter, ch)
        g.setPen(colour.darker(190))
        g.drawText(cell, Qt.AlignmentFlag.AlignCenter, ch)
        g.restore()
    e = _placed(emblem(season), c, r * 0.48)
    g.fillPath(e.translated(1.2, 1.2), QBrush(colour.lighter(150)))
    g.fillPath(e, QBrush(colour.darker(175)))


# -- 4. Limoges enamel --

ENAMEL = SEASON_PIGMENTS["enamel"]


def enamel(
    g: QPainter, c: QPointF, r: float, season: str, _year: int, _p: Palette
) -> None:
    """Gilt copper with a jewelled ring and an enamel field, the emblem
    left in gold."""
    g.setPen(QPen(COPPER, 1.4))
    g.setBrush(gold(QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r)))
    g.drawEllipse(c, r, r)
    jewel = max(1.5, r * 0.07)
    for k in range(24):
        a = math.radians(k * 15)
        g.setPen(QPen(COPPER, 0.8))
        g.setBrush(
            QBrush(QColor(DRAWN["turquoise"] if k % 2 else DRAWN["enamel-white"]))
        )
        g.drawEllipse(
            c + QPointF(r * 0.88 * math.cos(a), r * 0.88 * math.sin(a)), jewel, jewel
        )
    ri = r * 0.76
    base = QColor(ENAMEL.get(season, ENAMEL["Spring"]))
    grad = QRadialGradient(c + QPointF(-ri * 0.3, -ri * 0.3), ri * 1.5)
    grad.setColorAt(0, base.lighter(140))
    grad.setColorAt(1, base.darker(130))
    g.setPen(QPen(COPPER, 1.6))
    g.setBrush(QBrush(grad))
    g.drawEllipse(c, ri, ri)
    for k in range(6):
        a = math.radians(k * 60 + 30)
        at = c + QPointF(ri * 0.82 * math.cos(a), ri * 0.82 * math.sin(a))
        g.setBrush(gold(QRectF(at.x() - 3, at.y() - 3, 6, 6)))
        g.setPen(Qt.PenStyle.NoPen)
        g.drawEllipse(at, jewel * 0.7, jewel * 0.7)
    e = _placed(emblem(season), c, ri * 0.72)
    g.setPen(QPen(COPPER, 1.4))
    g.setBrush(gold(e.boundingRect()))
    g.drawPath(e)
    g.setPen(QPen(QColor(DRAWN["engraving"]), 0.7))
    g.setBrush(QBrush(VERMILION))
    g.drawEllipse(_flower_heart(season, c, ri * 0.72), jewel, jewel)


# -- 5. a Book of Hours calendar roundel --

SKY = SEASON_PIGMENTS["sky"]
_CROWNS = SEASON_PIGMENTS["crowns"]
_SCENE = SEASON_PIGMENTS["scene"]


def book_of_hours(
    g: QPainter, c: QPointF, r: float, season: str, _year: int, p: Palette
) -> None:
    """A calendar page's little landscape: the season's sky, a hill and a
    tree (bare in Winter), framed in red and gold."""
    top, low, ground = SKY.get(season, SKY["Spring"])
    g.save()
    g.setClipPath(_circle(c, r * 0.86))
    sky = QLinearGradient(c + QPointF(0, -r), c + QPointF(0, r * 0.3))
    sky.setColorAt(0, QColor(top))
    sky.setColorAt(1, QColor(low))
    g.fillRect(QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r), QBrush(sky))
    hill = QPainterPath(c + QPointF(-r, r * 0.3))
    hill.cubicTo(
        c + QPointF(-r * 0.4, r * 0.05),
        c + QPointF(r * 0.3, r * 0.45),
        c + QPointF(r, r * 0.2),
    )
    hill.lineTo(c + QPointF(r, r))
    hill.lineTo(c + QPointF(-r, r))
    hill.closeSubpath()
    g.setPen(QPen(INK, 1))
    g.setBrush(QBrush(QColor(ground)))
    g.drawPath(hill)
    tx, ty = c.x() + r * 0.45, c.y() + r * 0.25
    g.setPen(QPen(QColor(DRAWN["timber"]), max(1.0, r * 0.04)))
    g.drawLine(QPointF(tx, ty), QPointF(tx, ty - r * 0.35))
    if season in _CROWNS:
        g.setPen(QPen(INK, 0.8))
        g.setBrush(QBrush(QColor(_CROWNS[season])))
        g.drawEllipse(QPointF(tx, ty - r * 0.45), r * 0.2, r * 0.17)
    else:
        for s in (-1, 1):
            g.drawLine(
                QPointF(tx, ty - r * 0.25), QPointF(tx + s * r * 0.15, ty - r * 0.45)
            )
    e = _placed(emblem(season), c + QPointF(-r * 0.25, -r * 0.25), r * 0.38)
    g.setPen(QPen(INK, 0.9))
    g.setBrush(QBrush(QColor(_SCENE.get(season, DRAWN["snow"]))))
    g.drawPath(e)
    g.restore()
    g.setBrush(Qt.BrushStyle.NoBrush)
    g.setPen(QPen(QColor(p["heading"]), max(1.2, r * 0.045)))
    g.drawEllipse(c, r * 0.86, r * 0.86)
    g.setPen(QPen(QColor(p["foreground"]), 1))
    g.drawEllipse(c, r * 0.94, r * 0.94)
    g.setPen(QPen(QColor(p["accent"]), max(1.0, r * 0.035)))
    g.drawEllipse(c, r * 0.9, r * 0.9)


# -- 6. pen and wash --

WASH = SEASON_PIGMENTS["wash"]


def pen_and_wash(
    g: QPainter, c: QPointF, r: float, season: str, _year: int, p: Palette
) -> None:
    """The quietest: inked and hatched over a pale wash, ringed in red."""
    wash = WASH.get(season, WASH["Spring"])
    ink = QColor(p["foreground"])
    red = QColor(p["heading"])
    g.setBrush(QBrush(shade(wash, 55)))
    g.setPen(Qt.PenStyle.NoPen)
    g.drawEllipse(c, r * 0.8, r * 0.8)
    e = _placed(emblem(season), c, r * 0.62)
    g.setBrush(QBrush(shade(wash, 140)))
    g.setPen(QPen(ink, 1.3))
    g.drawPath(e)
    g.save()
    g.setClipPath(e.intersected(_circle(c + QPointF(r * 0.5, r * 0.5), r * 0.8)))
    g.setPen(QPen(ink, 0.7))
    k = -r
    while k < r:
        g.drawLine(c + QPointF(k - r, -r), c + QPointF(k + r, r))
        k += max(2.5, r * 0.08)
    g.restore()
    g.setBrush(Qt.BrushStyle.NoBrush)
    g.setPen(QPen(red, 1.5))
    g.drawEllipse(c, r * 0.86, r * 0.86)
    g.drawEllipse(c, r * 0.94, r * 0.94)
    g.setPen(QPen(red, 0.9))
    for k in range(16):
        a = math.radians(k * 22.5)
        g.drawEllipse(
            c + QPointF(r * 0.9 * math.cos(a), r * 0.9 * math.sin(a)), 1.3, 1.3
        )


Painter = Callable[[QPainter, QPointF, float, str, int, Palette], None]

#: Each set's painter, by medallions.KEYS.
PAINTERS: dict[str, Painter] = {
    "stained_glass": stained_glass,
    "illuminated": illuminated,
    "wax_seal": wax_seal,
    "enamel": enamel,
    "book_of_hours": book_of_hours,
    "pen_and_wash": pen_and_wash,
}


def paint(
    painter: QPainter,
    key: str,
    centre: QPointF,
    radius: float,
    season: str,
    year: int,
    p: Palette,
    *,
    now: bool = False,
) -> None:
    """Draw the season's medallion of set `key` (stained glass for an
    unknown one); the present season glows behind it in the theme's gilt."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    if now:
        glow = QRadialGradient(centre, radius * 1.6)
        glow.setColorAt(0.55, shade(p["accent"], 120))
        glow.setColorAt(1, shade(p["accent"], 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(centre, radius * 1.6, radius * 1.6)
    PAINTERS.get(key, stained_glass)(painter, centre, radius, season, year, p)
    painter.restore()


#: The roundel a numbered medallion carries, for each set: the first
#: side's ground, the second side's, the rim, and the number's ink.
ROUNDELS: dict[str, tuple[QColor, QColor, QColor, QColor]] = {
    "stained_glass": (QColor(DRAWN["glass-gold"]), LAPIS.lighter(210), LEAD, INK),
    "illuminated": (VERMILION, LAPIS, GOLD_DARK, WHITE),
    "wax_seal": (VERMILION_DEEP, LAPIS_DEEP, VERMILION_DEEP.darker(140), WHITE),
    "enamel": (LAPIS, VERMILION, COPPER, WHITE),
    "book_of_hours": (LAPIS, VERMILION, GOLD_DARK, WHITE),
    "pen_and_wash": (WHITE, WHITE, INK, INK),
}


def numbered(
    painter: QPainter,
    key: str,
    centre: QPointF,
    radius: float,
    number: int,
    side: int,
    season: str,
    year: int,
    p: Palette,
    *,
    now: bool = False,
) -> None:
    """A medallion of set `key` for the season, with a roundel over its
    heart carrying `number`: an Initiative in a fight's order of blows.
    The roundel's ground tells the two sides apart (the second side's
    number is in vermilion where the set has one ground)."""
    paint(painter, key, centre, radius, season, year, p, now=now)
    first, second, rim, ink = ROUNDELS.get(key, ROUNDELS["stained_glass"])
    ground = first if side == 0 else second
    if key == "pen_and_wash" and side:
        ink = VERMILION
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    r = radius * 0.6
    shine = QRadialGradient(centre - QPointF(r * 0.3, r * 0.3), r * 1.4)
    shine.setColorAt(0, ground.lighter(125))
    shine.setColorAt(1, ground)
    painter.setBrush(QBrush(shine))
    painter.setPen(QPen(rim, max(1.0, radius * 0.07)))
    painter.drawEllipse(centre, r, r)
    painter.setPen(ink)
    painter.setFont(_font(max(8.0, radius * 0.5), bold=True))
    painter.drawText(
        QRectF(centre.x() - r, centre.y() - r, 2 * r, 2 * r),
        Qt.AlignmentFlag.AlignCenter,
        str(number),
    )
    painter.restore()


def duotone(image: QImage, tone: QColor) -> QImage:
    """`image` in shades of `tone` alone: deep where it was dark, pale
    where it was light, its own transparency kept."""
    out = image.convertToFormat(QImage.Format.Format_Grayscale8).convertToFormat(
        QImage.Format.Format_ARGB32_Premultiplied
    )
    out.setDevicePixelRatio(image.devicePixelRatio())
    g = QPainter(out)
    g.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
    g.fillRect(out.rect(), tone.darker(260))
    g.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
    g.fillRect(out.rect(), tone.lighter(165))
    g.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    g.drawImage(QPointF(), image)
    g.end()
    return out


def figure_medallion(
    painter: QPainter,
    key: str,
    centre: QPointF,
    radius: float,
    value: str,
    tone: QColor,
    year: int,
    p: Palette,
) -> None:
    """A figure (an aura, a Loyalty) as a numbered medallion of set `key`
    wholly in `tone`, so its colour says what the figure is or how it
    stands, never the season. The set's Spring medallion gives the shape."""
    scale = max(1.0, painter.device().devicePixelRatioF())
    reach = math.ceil(radius * ROOM / 2)
    art = QImage(
        math.ceil(2 * reach * scale),
        math.ceil(2 * reach * scale),
        QImage.Format.Format_ARGB32_Premultiplied,
    )
    art.fill(0)
    g = QPainter(art)
    g.scale(scale, scale)
    paint(g, key, QPointF(reach, reach), radius, "Spring", year, p)
    g.end()
    art.setDevicePixelRatio(scale)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.drawImage(centre - QPointF(reach, reach), duotone(art, tone))
    r = radius * 0.6
    shine = QRadialGradient(centre - QPointF(r * 0.3, r * 0.3), r * 1.4)
    shine.setColorAt(0, tone.lighter(125))
    shine.setColorAt(1, tone)
    painter.setBrush(QBrush(shine))
    painter.setPen(QPen(tone.darker(150), max(1.0, radius * 0.07)))
    painter.drawEllipse(centre, r, r)
    # A pale tone takes dark ink, so the number keeps its contrast.
    painter.setPen(tone.darker(320) if tone.lightnessF() > 0.6 else WHITE)
    painter.setFont(_font(max(8.0, radius * 0.5), bold=True))
    painter.drawText(
        QRectF(centre.x() - r, centre.y() - r, 2 * r, 2 * r),
        Qt.AlignmentFlag.AlignCenter,
        value,
    )
    painter.restore()


def paint_season(
    painter: QPainter,
    saga: Saga,
    centre: QPointF,
    radius: float,
    season: str,
    year: int,
    p: Palette,
    *,
    now: bool = False,
) -> None:
    """Draw the season's medallion in the saga's set. Every screen draws
    them through this (or Medallion, which calls it), so none picks a set
    itself, and each is drawn in the set the saga has when it is painted."""
    paint(painter, medallions.chosen(saga), centre, radius, season, year, p, now=now)


#: The room a medallion needs, in radii across: the illuminated set's ivy
#: reaches 1.47 r from the centre and the present season's glow 1.53 r.
ROOM = 3.35


class Medallion(QWidget):
    """One season's medallion in the saga's set, `radius` across with
    room round it for any set's ivy and the present season's glow; with
    its name under it when `caption`."""

    def __init__(
        self,
        saga: Saga,
        season: str,
        year: int,
        p: Palette,
        *,
        radius: float = 31,
        now: bool = False,
        caption: bool = False,
    ) -> None:
        super().__init__()
        self.saga, self.season, self.year, self.p = saga, season, year, p
        self.radius, self.now, self.caption = radius, now, caption
        side = math.ceil(radius * ROOM)
        self.setFixedSize(side, side + 20 if caption else side)
        self.setToolTip(f"{season} {year}" + (" (now)" if now else ""))

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = self.width()
        paint_season(
            painter,
            self.saga,
            QPointF(side / 2, side / 2),
            self.radius,
            self.season,
            self.year,
            self.p,
            now=self.now,
        )
        if self.caption:
            painter.setPen(QColor(self.p["heading"] if self.now else self.p["label"]))
            f = _font(10, bold=self.now)
            f.setCapitalization(QFont.Capitalization.SmallCaps)
            painter.setFont(f)
            painter.drawText(
                QRectF(0, side - 4, side, 22),
                Qt.AlignmentFlag.AlignCenter,
                f"{self.season} {self.year}",
            )
        painter.end()


def beside(medallion: QWidget, widget: QWidget, *, gap: int = 8) -> QWidget:
    """A row: `medallion`, then `widget` (a heading), centred on each other."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(gap)
    row.addWidget(medallion, 0, Qt.AlignmentFlag.AlignVCenter)
    row.addWidget(widget, 1, Qt.AlignmentFlag.AlignVCenter)
    return box


class SeasonHeadpiece(Headpiece):
    """The window's headpiece band, with the saga's present season at its
    centre in place of the hedera (the plain band while no saga is open).
    The band is tall enough that no set's medallion is clipped: without
    the glow, every set stays within 1.06 r of its centre up and down, and
    the illuminated set's ivy within 1.47 r to the sides, inside the dots."""

    HEIGHT = 46
    RADIUS = 17.0
    #: How far out from the centre the dots sit beside the medallion.
    INNER = math.ceil(RADIUS * 1.47) + 8

    def __init__(self, p: Palette) -> None:
        super().__init__(p)
        self.saga: Saga | None = None

    def draw(self, painter: QPainter, width: float, cy: float) -> None:
        saga = self.saga
        if saga is None:
            super().draw(painter, width, cy)
            return
        paint_season(
            painter,
            saga,
            QPointF(width / 2, cy),
            self.RADIUS,
            saga.current_season,
            saga.current_year,
            self.p,
        )
        self.band(painter, width, cy, self.INNER)
