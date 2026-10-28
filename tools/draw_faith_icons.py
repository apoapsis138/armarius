"""Draw the Religion chapter's faith icons in the manner of the Phosphor
icons beside them (Light weight: strokes 12 units wide on a 256 square,
round ends and joins):

- star_of_david.svg: two interlaced triangles, for a Jew;
- crescent.svg: a crescent moon and a five-pointed star, for a Muslim;
- sacred_fire.svg: a flame on a fire altar, for a Mazdean;
- sacred_tree.svg: a tree with its roots and branches, for a pagan.

    uv run --group charges python tools/draw_faith_icons.py

The strokes are widened into one filled outline with shapely (the
`charges` dependency group) and written to assets/drawn/, drawn in
currentColor like the other icons. All are drawn here, not copied."""

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


def _circle(cx: float, cy: float, r: float, steps: int = 64) -> list[Point]:
    return [
        (
            cx + r * math.cos(2 * math.pi * i / steps),
            cy + r * math.sin(2 * math.pi * i / steps),
        )
        for i in range(steps + 1)
    ]


def _polygon(cx: float, cy: float, r: float, sides: int, turn: float) -> list[Point]:
    """A regular polygon's closed outline, its first corner `turn`
    degrees round from straight up."""
    points = [
        (
            cx + r * math.sin(math.radians(turn + 360 * i / sides)),
            cy - r * math.cos(math.radians(turn + 360 * i / sides)),
        )
        for i in range(sides)
    ]
    return [*points, points[0]]


def _star(cx: float, cy: float, r: float, inner: float) -> list[Point]:
    """A five-pointed star's closed outline, a point straight up."""
    points = []
    for i in range(10):
        radius = r if i % 2 == 0 else inner
        a = math.radians(36 * i)
        points.append((cx + radius * math.sin(a), cy - radius * math.cos(a)))
    return [*points, points[0]]


def _flame(cx: float, cy: float, r: float, steps: int = 64) -> list[Point]:
    """A teardrop, its point straight up."""
    points = []
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        points.append((cx + r * math.sin(t) * math.sin(t / 2), cy - r * math.cos(t)))
    return points


def star_of_david_strokes() -> list[list[Point]]:
    return [_polygon(128, 132, 100, 3, 0), _polygon(128, 124, 100, 3, 180)]


def fire_strokes() -> list[list[Point]]:
    return [
        _flame(128, 92, 62),
        _flame(128, 122, 28),  # the flame's heart
        [(68, 172), (188, 172)],  # the altar's top
        [(92, 172), (106, 222), (150, 222), (164, 172)],  # its body
        [(76, 222), (180, 222)],  # its foot
    ]


def tree_strokes() -> list[list[Point]]:
    return [
        _circle(128, 92, 64),  # the crown
        [(128, 232), (128, 128)],  # the trunk
        [(128, 182), (98, 156)],
        [(128, 166), (158, 140)],
        [(128, 232), (98, 238)],  # the roots
        [(128, 232), (158, 238)],
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
        f"<!-- Drawn by tools/draw_faith_icons.py: {what}. -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" '
        f'fill="currentColor" fill-rule="evenodd"><path d="{d}"/></svg>\n',
        encoding="utf-8",
    )
    print(f"wrote {out.name}")


def main() -> None:
    shapely: Any = importlib.import_module("shapely")
    _write(
        "star_of_david.svg",
        _outline(star_of_david_strokes(), shapely, []),
        "a Star of David",
    )
    # The crescent: a disc with a smaller one taken out of it, its edge
    # stroked, and a star in the hollow it leaves.
    moon = (
        shapely.Point(112, 128)
        .buffer(92, quad_segs=32)
        .difference(shapely.Point(150, 112).buffer(76, quad_segs=32))
    )
    _write(
        "crescent.svg",
        _outline(
            [list(moon.exterior.coords), _star(178, 136, 34, 14)],
            shapely,
            [],
        ),
        "a crescent and a star",
    )
    _write("sacred_fire.svg", _outline(fire_strokes(), shapely, []), "a fire altar")
    _write("sacred_tree.svg", _outline(tree_strokes(), shapely, []), "a sacred tree")


if __name__ == "__main__":
    main()
