"""Draw the covenant's Attributes and Charter chapter icons in the manner
of the Phosphor icons beside them (Light weight: strokes 12 units wide on
a 256 square, round ends and joins):

- key.svg: a medieval key, its bow a ring, its bit cut with wards, laid
  aslant;
- charter.svg: a charter rolled at head and foot, three lines of writing,
  and a wax seal hanging from it on two tags.

    uv run --group charges python tools/draw_charter_icons.py

The strokes are widened into one filled outline with shapely (the
`charges` dependency group) and written to assets/drawn/, drawn in
currentColor like the other icons. Both are drawn here, not copied."""

from __future__ import annotations

import importlib
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ars_magica_manager import artwork

#: Half a Phosphor Light stroke.
HALF = 6.0

Point = tuple[float, float]


def _circle(cx: float, cy: float, r: float, steps: int = 48) -> list[Point]:
    return [
        (
            cx + r * math.cos(2 * math.pi * i / steps),
            cy + r * math.sin(2 * math.pi * i / steps),
        )
        for i in range(steps + 1)
    ]


def _rounded(x0: float, y0: float, x1: float, y1: float, r: float) -> list[Point]:
    """A rounded rectangle's outline, as one closed line."""
    points: list[Point] = []
    corners = (
        (x1 - r, y0 + r, -90),
        (x1 - r, y1 - r, 0),
        (x0 + r, y1 - r, 90),
        (x0 + r, y0 + r, 180),
    )
    for cx, cy, start in corners:
        for i in range(9):
            a = math.radians(start + 90 * i / 8)
            points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    points.append(points[0])
    return points


def _turned(
    points: list[Point], degrees: float, centre: Point = (128, 128)
) -> list[Point]:
    a = math.radians(degrees)
    cx, cy = centre
    return [
        (
            cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a),
            cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a),
        )
        for x, y in points
    ]


def key_strokes() -> list[list[Point]]:
    """The key drawn level, bow on the left, then laid aslant."""
    level: list[list[Point]] = [
        _circle(52, 128, 38),  # the bow
        _circle(52, 128, 14),  # its eye
        [(90, 128), (244, 128)],  # the shank
        [(244, 128), (244, 182), (216, 182), (216, 158), (198, 158), (198, 128)],
        [(112, 114), (112, 142)],  # the collar
    ]
    return [_turned(stroke, -40, (140, 140)) for stroke in level]


def charter_strokes() -> list[list[Point]]:
    return [
        _rounded(34, 22, 222, 50, 14),  # the head roll
        [(52, 50), (52, 150)],
        [(204, 50), (204, 150)],
        _rounded(34, 150, 222, 178, 14),  # the foot roll
        [(80, 78), (176, 78)],
        [(80, 102), (176, 102)],
        [(80, 126), (148, 126)],
        [(114, 178), (98, 214)],  # the seal's tags
        [(142, 178), (158, 214)],
    ]


def _outline(strokes: list[list[Point]], shapely: Any, extra: list[Any]) -> str:
    shapes = [
        shapely.LineString(stroke).buffer(HALF, cap_style="round", join_style="round")
        for stroke in strokes
    ]
    outline = shapely.unary_union(shapes + extra).simplify(0.2)
    parts = outline.geoms if hasattr(outline, "geoms") else [outline]
    rings = []
    for part in parts:
        rings.append(list(part.exterior.coords)[:-1])
        rings.extend(list(hole.coords)[:-1] for hole in part.interiors)
    return " ".join(
        "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + "Z" for ring in rings
    )


def _write(name: str, d: str, what: str) -> None:
    out = artwork.DRAWN / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"<!-- Drawn by tools/draw_charter_icons.py: {what}. -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" '
        f'fill="currentColor" fill-rule="evenodd"><path d="{d}"/></svg>\n',
        encoding="utf-8",
    )
    print(f"wrote {out.name}")


def main() -> None:
    shapely: Any = importlib.import_module("shapely")
    _write("key.svg", _outline(key_strokes(), shapely, []), "a key")
    # The seal: a disc of wax with the ring of its impression cut in it.
    disc = shapely.Point(128, 226).buffer(26)
    ring = (
        shapely.Point(128, 226)
        .buffer(19)
        .difference(shapely.Point(128, 226).buffer(15))
    )
    seal = disc.difference(ring)
    _write(
        "charter.svg",
        _outline(charter_strokes(), shapely, [seal]),
        "a charter with its seal",
    )


if __name__ == "__main__":
    main()
