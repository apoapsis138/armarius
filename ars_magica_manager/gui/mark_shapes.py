"""The shapes the ability marks are cut from, in a 100 x 100 box with its
centre at (50, 50): circles, bars, polygons and curves that the charges
in mark_charges join and cut into one another.
"""

from __future__ import annotations

import math
import random
from collections.abc import Iterable
from itertools import pairwise

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPolygonF, QTransform

Point = tuple[float, float]


def tile() -> QPainterPath:
    """The Art symbols' block: a square whose corners are notched in."""
    n = 7
    return poly(
        (4 + n, 4),
        (96 - n, 4),
        (96 - n, 4 + n),
        (96, 4 + n),
        (96, 96 - n),
        (96 - n, 96 - n),
        (96 - n, 96),
        (4 + n, 96),
        (4 + n, 96 - n),
        (4, 96 - n),
        (4, 4 + n),
        (4 + n, 4 + n),
    )


def rough(path: QPainterPath, seed: int, amount: float) -> QPainterPath:
    """The path's outline with small seeded wobbles, as a cut block prints."""
    rng = random.Random(seed)
    out = QPainterPath()
    out.setFillRule(Qt.FillRule.OddEvenFill)
    for polygon in path.simplified().toSubpathPolygons():
        points = []
        n = polygon.count()
        for i in range(n):
            a, b = polygon.at(i), polygon.at((i + 1) % n)
            steps = max(1, int(math.hypot(b.x() - a.x(), b.y() - a.y()) / 6))
            for s in range(steps):
                t = s / steps
                points.append(
                    QPointF(
                        a.x() + (b.x() - a.x()) * t + rng.uniform(-amount, amount),
                        a.y() + (b.y() - a.y()) * t + rng.uniform(-amount, amount),
                    )
                )
        out.addPolygon(QPolygonF(points))
        out.closeSubpath()
    return out


def circle(cx: float, cy: float, r: float) -> QPainterPath:
    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy), r, r)
    return path


def ellipse(x: float, y: float, w: float, h: float) -> QPainterPath:
    path = QPainterPath()
    path.addEllipse(QRectF(x, y, w, h))
    return path


def ring(cx: float, cy: float, r: float, w: float) -> QPainterPath:
    return circle(cx, cy, r).subtracted(circle(cx, cy, r - w))


def poly(*points: Point) -> QPainterPath:
    path = QPainterPath()
    path.addPolygon(QPolygonF([QPointF(x, y) for x, y in points]))
    path.closeSubpath()
    return path


def rrect(x: float, y: float, w: float, h: float, r: float) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(QRectF(x, y, w, h), r, r)
    return path


def rect(x: float, y: float, w: float, h: float) -> QPainterPath:
    path = QPainterPath()
    path.addRect(QRectF(x, y, w, h))
    return path


def bar(x1: float, y1: float, x2: float, y2: float, w: float) -> QPainterPath:
    """A straight stroke of width w."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * w / 2, dx / length * w / 2
    return poly(
        (x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)
    )


def line(*points: Point, w: float = 1.6) -> QPainterPath:
    """Bars joining the points in turn."""
    return union(*(bar(*a, *b, w) for a, b in pairwise(points)))


def union(*paths: QPainterPath) -> QPainterPath:
    out = QPainterPath()
    for path in paths:
        out = out.united(path)
    return out


def union_of(paths: Iterable[QPainterPath]) -> QPainterPath:
    return union(*paths)


def rotate(
    path: QPainterPath, deg: float, cx: float = 50, cy: float = 50
) -> QPainterPath:
    return QTransform().translate(cx, cy).rotate(deg).translate(-cx, -cy).map(path)


def mirror(path: QPainterPath) -> QPainterPath:
    """The path reflected across the box's upright centre line."""
    return QTransform().translate(100, 0).scale(-1, 1).map(path)


def move(path: QPainterPath, dx: float, dy: float) -> QPainterPath:
    return QTransform().translate(dx, dy).map(path)


def scaled(
    path: QPainterPath, k: float, cx: float = 50, cy: float = 50
) -> QPainterPath:
    return QTransform().translate(cx, cy).scale(k, k).translate(-cx, -cy).map(path)


def stroke(path: QPainterPath, w: float) -> QPainterPath:
    """The path drawn as a round-ended line of width w."""
    stroker = QPainterPathStroker()
    stroker.setWidth(w)
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    return stroker.createStroke(path)


def curve(*points: Point) -> QPainterPath:
    """A path through points, smoothed with quadratic segments: every
    second point is a control point."""
    path = QPainterPath()
    path.moveTo(*points[0])
    for i in range(1, len(points) - 1, 2):
        path.quadTo(*points[i], *points[i + 1])
    return path


def star(
    points: int,
    r_out: float,
    r_in: float,
    cx: float = 50,
    cy: float = 50,
    turn: float = -90,
) -> QPainterPath:
    corners = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(turn + i * 180 / points)
        corners.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return poly(*corners)


def vesica(cx: float, cy: float, w: float, h: float) -> QPainterPath:
    """An almond: the overlap of two circles."""
    r = (w * w / 4 + h * h / 4) / h
    d = r - h / 2
    return circle(cx, cy - d, r).intersected(circle(cx, cy + d, r))


def eye() -> QPainterPath:
    return (
        vesica(50, 50, 64, 34)
        .subtracted(circle(50, 50, 13))
        .united(circle(50, 50, 6.5))
    )


def flame(cx: float, base: float, w: float, h: float) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(cx, base - h)
    path.cubicTo(
        cx + w * 0.15,
        base - h * 0.6,
        cx + w * 0.6,
        base - h * 0.45,
        cx + w * 0.5,
        base - w * 0.4,
    )
    path.quadTo(cx + w * 0.4, base, cx, base)
    path.quadTo(cx - w * 0.4, base, cx - w * 0.5, base - w * 0.4)
    path.cubicTo(
        cx - w * 0.6, base - h * 0.45, cx - w * 0.15, base - h * 0.6, cx, base - h
    )
    path.closeSubpath()
    return path


def heart(cx: float = 50, cy: float = 50, k: float = 1.0) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(50, 82)
    path.cubicTo(20, 62, 14, 44, 22, 32)
    path.cubicTo(30, 20, 46, 22, 50, 34)
    path.cubicTo(54, 22, 70, 20, 78, 32)
    path.cubicTo(86, 44, 80, 62, 50, 82)
    path.closeSubpath()
    return scaled(move(path, cx - 50, cy - 50), k, cx, cy)


def outline_triangle(up: bool = True, bar_across: bool = False) -> QPainterPath:
    """The alchemists' element triangles, drawn as a thick outline."""
    tri = (
        poly((50, 16), (84, 78), (16, 78)) if up else poly((50, 84), (16, 22), (84, 22))
    )
    shape = tri.subtracted(scaled(tri, 0.66, 50, 57 if up else 43))
    if bar_across:
        y = 52 if up else 48
        shape = shape.united(rect(24, y - 3.5, 52, 7))
    return shape


def book_closed(emblem: QPainterPath | None = None) -> QPainterPath:
    """A closed codex with its spine and clasp; `emblem` is cut out of its
    cover."""
    shape = union(rrect(26, 16, 48, 68, 3), rect(22, 18, 6, 64), rect(72, 46, 8, 8))
    if emblem is not None:
        shape = shape.subtracted(emblem)
    return shape


def _crossings(
    lines: list[list[Point]],
) -> list[tuple[int, float, int, float, Point]]:
    """Where the polylines cross: (line, place along it, other line, place
    along that, point), a place being a segment index plus its fraction."""
    found = []
    segments = [
        (i, k, line[k], line[k + 1])
        for i, line in enumerate(lines)
        for k in range(len(line) - 1)
    ]
    for n, (i, k, a, b) in enumerate(segments):
        for j, m, c, d in segments[n + 1 :]:
            if i == j and abs(k - m) <= 1:
                continue
            closed = lines[i][0] == lines[i][-1]
            if i == j and closed and {k, m} == {0, len(lines[i]) - 2}:
                continue
            rx, ry = b[0] - a[0], b[1] - a[1]
            sx, sy = d[0] - c[0], d[1] - c[1]
            den = rx * sy - ry * sx
            if abs(den) < 1e-9:
                continue
            t = ((c[0] - a[0]) * sy - (c[1] - a[1]) * sx) / den
            u = ((c[0] - a[0]) * ry - (c[1] - a[1]) * rx) / den
            if 0 <= t < 1 and 0 <= u < 1:
                point = (a[0] + rx * t, a[1] + ry * t)
                found.append((i, k + t, j, m + u, point))
    return found


def _alternate(found: list[tuple[int, float, int, float, Point]]) -> list[bool]:
    """For each crossing, whether its first line goes over: along every
    line the crossings go over, under, over, under, as interlace does."""
    passes: dict[int, list[tuple[float, int, bool]]] = {}
    for c, (i, ti, j, tj, _) in enumerate(found):
        passes.setdefault(i, []).append((ti, c, True))
        passes.setdefault(j, []).append((tj, c, False))
    links: dict[int, list[tuple[int, bool]]] = {c: [] for c in range(len(found))}
    for seq in passes.values():
        seq.sort()
        for (_, c1, first1), (_, c2, first2) in pairwise(seq):
            # over-ness alternates: s1 ^ !first1 != s2 ^ !first2
            links[c1].append((c2, first1 == first2))
            links[c2].append((c1, first1 == first2))
    over: list[bool | None] = [None] * len(found)
    for start in range(len(found)):
        if over[start] is not None:
            continue
        over[start] = True
        queue = [start]
        while queue:
            c = queue.pop()
            for other, differ in links[c]:
                if over[other] is None:
                    over[other] = (not over[c]) if differ else bool(over[c])
                    queue.append(other)
    return [bool(o) for o in over]


def weave(strands: Iterable[QPainterPath], w: float, gap: float = 2.2) -> QPainterPath:
    """The strands drawn as bands of width w that interlace: wherever two
    cross, one passes over and the band beneath breaks off either side of
    it, alternating along each strand."""
    strands = list(strands)
    lines = [
        [(polygon.at(n).x(), polygon.at(n).y()) for n in range(polygon.count())]
        for strand in strands
        for polygon in strand.toSubpathPolygons()
    ]
    shape = union_of(stroke(s, w) for s in strands)
    found = _crossings(lines)
    for (i, ti, j, tj, point), first_over in zip(found, _alternate(found), strict=True):
        line, t = (lines[i], ti) if first_over else (lines[j], tj)
        k = int(t)
        a, b = line[k], line[min(k + 1, len(line) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        reach = w * 1.5 + gap
        ux, uy = dx / length * reach, dy / length * reach
        x, y = point
        local = bar(x - ux, y - uy, x + ux, y + uy, w + 2 * gap)
        halo = local.subtracted(bar(x - ux, y - uy, x + ux, y + uy, w))
        shape = shape.subtracted(halo.intersected(circle(x, y, reach)))
    return shape


def over(top: QPainterPath, beneath: QPainterPath, gap: float = 2.2) -> QPainterPath:
    """`top` laid over `beneath`, with a gap cut round it where they meet."""
    return beneath.subtracted(stroke(top, 2 * gap).united(top)).united(top)
