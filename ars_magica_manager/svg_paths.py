"""SVG path data ("M10 20 C ...") flattened into polygons, so a drawing
made of curves can be drawn by any front-end (painter paths on the
desktop, half-blocks in the terminal) and tested by point, with no
graphics library.

Every command of the path grammar is read, absolute and relative: moves
and lines (M L H V), cubic and quadratic Béziers with their smooth forms
(C S Q T), elliptical arcs (A) and closing (Z). Each subpath becomes one
ring of points; curves are cut into short straight steps."""

from __future__ import annotations

import math
import re

Point = tuple[float, float]
Ring = tuple[Point, ...]

_TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")

#: How many straight steps stand for one curve segment.
STEPS = 12


def _cubic(p0: Point, p1: Point, p2: Point, p3: Point) -> list[Point]:
    out = []
    for i in range(1, STEPS + 1):
        t = i / STEPS
        u = 1 - t
        out.append(
            (
                u**3 * p0[0]
                + 3 * u * u * t * p1[0]
                + 3 * u * t * t * p2[0]
                + t**3 * p3[0],
                u**3 * p0[1]
                + 3 * u * u * t * p1[1]
                + 3 * u * t * t * p2[1]
                + t**3 * p3[1],
            )
        )
    return out


def _quadratic(p0: Point, p1: Point, p2: Point) -> list[Point]:
    out = []
    for i in range(1, STEPS + 1):
        t = i / STEPS
        u = 1 - t
        out.append(
            (
                u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
            )
        )
    return out


def _arc(
    p0: Point, rx: float, ry: float, phi: float, large: bool, sweep: bool, p1: Point
) -> list[Point]:
    """An elliptical arc from p0 to p1, by the SVG specification's
    endpoint-to-centre conversion."""
    if p0 == p1:
        return []
    if not rx or not ry:
        return [p1]
    rx, ry = abs(rx), abs(ry)
    cos, sin = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1, y1 = cos * dx + sin * dy, -sin * dx + cos * dy
    scale = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if scale > 1:
        rx, ry = rx * math.sqrt(scale), ry * math.sqrt(scale)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    root = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        root = -root
    cx1, cy1 = root * rx * y1 / ry, -root * ry * x1 / rx
    cx = cos * cx1 - sin * cy1 + (p0[0] + p1[0]) / 2
    cy = sin * cx1 + cos * cy1 + (p0[1] + p1[1]) / 2

    def angle(ux: float, uy: float, vx: float, vy: float) -> float:
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    start = angle(1, 0, (x1 - cx1) / rx, (y1 - cy1) / ry)
    delta = angle((x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi
    steps = max(2, round(abs(delta) / (math.pi / 2) * STEPS / 2))
    out = []
    for i in range(1, steps + 1):
        a = start + delta * i / steps
        ex, ey = rx * math.cos(a), ry * math.sin(a)
        out.append((cos * ex - sin * ey + cx, sin * ex + cos * ey + cy))
    return out


class _Reader:
    """Reads path data a command at a time: the pen's place, the ring
    being drawn and the last curve's control point, which the smooth
    curves (S, T) reflect."""

    def __init__(self, d: str, shortest: int = 3) -> None:
        self.d = d
        self.shortest = shortest
        self.tokens = _TOKEN.findall(d)
        self.i = 0
        self.at: Point = (0.0, 0.0)
        self.start: Point = (0.0, 0.0)
        self.control: Point | None = None
        self.ring: list[Point] = []
        self.out: list[Ring] = []
        self.origin: Point = (0.0, 0.0)

    def number(self) -> float:
        value = float(self.tokens[self.i])
        self.i += 1
        return value

    def point(self) -> Point:
        x, y = self.number(), self.number()
        return (self.origin[0] + x, self.origin[1] + y)

    def finish(self) -> None:
        if len(self.ring) >= self.shortest:
            self.out.append(tuple(self.ring))
        self.ring = []

    def reflected(self) -> Point:
        if self.control is None:
            return self.at
        return (2 * self.at[0] - self.control[0], 2 * self.at[1] - self.control[1])

    def line_to(self, end: Point) -> None:
        self.ring.append(end)
        self.at, self.control = end, None

    # One method per command, given the letter in upper case.

    def move(self) -> None:
        self.finish()
        self.at = self.start = self.point()
        self.ring = [self.at]
        self.control = None

    def line(self) -> None:
        self.line_to(self.point())

    def horizontal(self) -> None:
        self.line_to((self.origin[0] + self.number(), self.at[1]))

    def vertical(self) -> None:
        self.line_to((self.at[0], self.origin[1] + self.number()))

    def cubic(self, smooth: bool) -> None:
        c1 = self.reflected() if smooth else self.point()
        c2, end = self.point(), self.point()
        self.ring.extend(_cubic(self.at, c1, c2, end))
        self.control, self.at = c2, end

    def quadratic(self, smooth: bool) -> None:
        c = self.reflected() if smooth else self.point()
        end = self.point()
        self.ring.extend(_quadratic(self.at, c, end))
        self.control, self.at = c, end

    def arc(self) -> None:
        rx, ry, phi = self.number(), self.number(), self.number()
        large, sweep = bool(self.number()), bool(self.number())
        end = self.point()
        self.ring.extend(_arc(self.at, rx, ry, phi, large, sweep, end))
        self.at, self.control = end, None

    def close(self) -> None:
        self.finish()
        self.at, self.control = self.start, None

    def read(self) -> list[Ring]:
        steps = {
            "M": self.move,
            "L": self.line,
            "H": self.horizontal,
            "V": self.vertical,
            "C": lambda: self.cubic(False),
            "S": lambda: self.cubic(True),
            "Q": lambda: self.quadratic(False),
            "T": lambda: self.quadratic(True),
            "A": self.arc,
        }
        command = ""
        while self.i < len(self.tokens):
            if self.tokens[self.i].isalpha():
                command = self.tokens[self.i]
                self.i += 1
                if command in "Zz":
                    self.close()
                    continue
            elif not command:
                raise ValueError(f"Path data starts with a number: {self.d[:20]!r}")
            step = steps.get(command.upper())
            if step is None:
                raise ValueError(f"Unknown path command {command!r}")
            self.origin = self.at if command.islower() else (0.0, 0.0)
            step()
            # Further pairs after a move are lines.
            if command in "Mm":
                command = "l" if command == "m" else "L"
        self.finish()
        return self.out


def rings(d: str, shortest: int = 3) -> list[Ring]:
    """The path's subpaths as rings of points, in the path's own units.
    A subpath of fewer than `shortest` points is dropped (2 keeps the
    single lines a stroke draws)."""
    return _Reader(d, shortest).read()


def fitted(d: str, box: tuple[float, float, float, float]) -> list[Ring]:
    """The path's rings scaled into the unit square: `box` (min x, min y,
    width, height, as an SVG viewBox) is fitted to it, centred, keeping
    its proportions."""
    left, top, width, height = box
    side = max(width, height)
    dx, dy = (side - width) / 2, (side - height) / 2
    return [
        tuple(((px - left + dx) / side, (py - top + dy) / side) for px, py in ring)
        for ring in rings(d)
    ]
