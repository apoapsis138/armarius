"""Draw House Diedne's mark: a triskelion, scraped away.

The books give Diedne no symbol: it was struck from the records (Houses
of Hermes, 3rd edition, p. 137) and showing it is forbidden (Against the
Dark p. 33). This mark is invented, the app's own: a triskelion, three
spirals running out from one centre (an old Celtic sign; the triquetra
was passed over, as by the thirteenth century it reads as the Trinity),
mostly scraped off the page so only parts of its arms survive, with one
stroke struck across what is left, as an erased record would be.

    uv run --group charges python tools/draw_diedne_mark.py

The strokes are widened into one filled outline with shapely (the
`charges` dependency group) and written to assets/drawn/diedne.svg on a
1000 square, in currentColor like the House symbols the app tints.
Everything stays well in from the square's edge, where a watermark cut
from a mark discards the frame a House's tile has. Drawn here, not copied.
"""

from __future__ import annotations

import importlib
import math
import random
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ars_magica_manager import artwork

Point = tuple[float, float]

#: The sign's centre, how far out each spiral's own centre sits, and the
#: spirals' outer and inner radii and turns, on a 1000 square.
CENTRE, OUT, OUTER, INNER, TURNS = 500.0, 195.0, 112.0, 18.0, 1.35
#: Half the arms' stroke, wide enough to read when the sign is 30 pixels,
#: and half the stroke struck across them.
HALF, STRUCK = 22.0, 11.0
#: The parts of each arm left after scraping, as fractions along it: only
#: bits of the spirals' outer rims, at the sign's very edge; the centre and
#: the inner turns are gone.
KEPT = (
    ((0.13, 0.19), (0.24, 0.30)),
    ((0.15, 0.27),),
    ((0.12, 0.17), (0.22, 0.26)),
)
#: The gouges cut through what is left, (angle in degrees, offset from the
#: centre across them, half their width): deep, wide strokes of the knife.
GOUGES = (
    (-24, -150, 26),
    (-30, -40, 34),
    (-20, 70, 30),
    (-35, 185, 24),
    (62, -110, 20),
    (55, 120, 22),
)
#: The fine scratches the knife left beside the gouges, (angle, offset,
#: half width).
SCRATCHES = (
    (-26, -95, 5),
    (-22, 20, 6),
    (-31, 130, 5),
    (-18, 240, 4),
)


def _arm(k: int) -> list[Point]:
    """The `k`th arm: from the sign's centre out onto its spiral's rim and
    winding in to the spiral's own centre, each arm turning the same way."""
    angle = math.radians(-90 + 120 * k)
    cx = CENTRE + OUT * math.cos(angle)
    cy = CENTRE + OUT * math.sin(angle)
    # Onto the rim a little past the point nearest the centre.
    start = math.atan2(CENTRE - cy, CENTRE - cx) + math.radians(55)
    points = [(CENTRE, CENTRE)]
    steps = 120
    for i in range(steps + 1):
        t = i / steps
        r = OUTER + (INNER - OUTER) * t
        a = start + math.tau * TURNS * t
        points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return points


def _part(points: list[Point], a: float, b: float) -> list[Point]:
    """The part of a line of `points` from `a` to `b` of the way along."""
    n = len(points) - 1
    return points[round(a * n) : round(b * n) + 1]


def _outline(shape: Any) -> str:
    parts = shape.geoms if hasattr(shape, "geoms") else [shape]
    rings: list[list[Point]] = []
    for part in parts:
        rings.append(list(part.exterior.coords)[:-1])
        rings.extend(list(hole.coords)[:-1] for hole in part.interiors)
    return " ".join(
        "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + "Z" for ring in rings
    )


def _across(shapely: Any, angle: float, offset: float, half: float) -> Any:
    """A straight band `half` either side of a line through the square at
    `angle` degrees, `offset` from its centre across the line."""
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    cx, cy = CENTRE - dy * offset, CENTRE + dx * offset
    return shapely.LineString(
        [(cx - dx * 340, cy - dy * 340), (cx + dx * 340, cy + dy * 340)]
    ).buffer(half, cap_style="flat")


def draw(shapely: Any) -> str:
    chance = random.Random(2253)
    shapes = []
    for k in range(3):
        arm = _arm(k)
        for a, b in KEPT[k]:
            shapes.append(
                shapely.LineString(_part(arm, a, b)).buffer(
                    HALF, cap_style="flat", join_style="round"
                )
            )
    remains = shapely.unary_union(shapes)
    # The gouges take out what they cross.
    for angle, offset, half in GOUGES:
        remains = remains.difference(
            _across(shapely, angle + chance.uniform(-2, 2), offset, half)
        )
    # The stroke struck across, and the knife's fine scratches, are left in
    # the page as marks of their own, short of the square's edge.
    marks = [remains]
    clear = shapely.Point(CENTRE, CENTRE).buffer(330)
    for angle, offset, half in ((-24, 0, STRUCK), *SCRATCHES):
        marks.append(_across(shapely, angle, offset, half).intersection(clear))
    outline = shapely.unary_union(marks).simplify(0.4)
    return (
        "<!-- Drawn by tools/draw_diedne_mark.py: House Diedne's invented "
        "sign, a triskelion scraped away and struck through. -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        f'fill="currentColor" fill-rule="evenodd"><path d="{_outline(outline)}"/>'
        "</svg>\n"
    )


def main() -> None:
    shapely: Any = importlib.import_module("shapely")
    path = artwork.DRAWN / "diedne.svg"
    path.write_text(draw(shapely), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
