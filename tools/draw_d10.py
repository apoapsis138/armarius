"""Draw the ten-sided die of the Chronicle's rolls in the manner of the
Phosphor icons (Light weight: strokes 12 units wide on a 256 square, round
ends and joins). Phosphor has only six-sided dice.

- d10.svg: a pentagonal trapezohedron seen front-on: its outline, and the
  kite face turned to the viewer, with the edges running from it to the
  outline. The face is left open for the number, which the app writes in.

    uv run --with shapely python tools/draw_d10.py

The strokes are widened into one filled outline with shapely and written to assets/drawn/, drawn in
currentColor like the other icons. It is drawn here, not copied."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ars_magica_manager import artwork

#: Half a Phosphor Light stroke.
HALF = 6.0

Point = tuple[float, float]

#: The outline: top, the shoulders, the waist and the point below.
TOP: Point = (128, 22)
LEFT: Point = (26, 108)
LOW_LEFT: Point = (40, 172)
BOTTOM: Point = (128, 234)
LOW_RIGHT: Point = (216, 172)
RIGHT: Point = (230, 108)
#: The kite face turned to the viewer: its sides and its lower point.
FACE_LEFT: Point = (72, 140)
FACE_BOTTOM: Point = (128, 176)
FACE_RIGHT: Point = (184, 140)


def strokes() -> list[list[Point]]:
    outline = [TOP, LEFT, LOW_LEFT, BOTTOM, LOW_RIGHT, RIGHT, TOP]
    face = [TOP, FACE_LEFT, FACE_BOTTOM, FACE_RIGHT, TOP]
    return [
        outline,
        face,
        [FACE_LEFT, LOW_LEFT],
        [FACE_RIGHT, LOW_RIGHT],
        [FACE_BOTTOM, BOTTOM],
    ]


def _outline(lines: list[list[Point]], shapely: Any) -> str:
    shapes = [
        shapely.LineString(line).buffer(HALF, cap_style="round", join_style="round")
        for line in lines
    ]
    outline = shapely.unary_union(shapes).simplify(0.2)
    parts = outline.geoms if hasattr(outline, "geoms") else [outline]
    rings = []
    for part in parts:
        rings.append(list(part.exterior.coords)[:-1])
        rings.extend(list(hole.coords)[:-1] for hole in part.interiors)
    return " ".join(
        "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + "Z" for ring in rings
    )


def main() -> None:
    shapely: Any = importlib.import_module("shapely")
    out = artwork.DRAWN / "d10.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "<!-- Drawn by tools/draw_d10.py: a ten-sided die. -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" '
        f'fill="currentColor" fill-rule="evenodd"><path d="{_outline(strokes(), shapely)}"/></svg>\n',
        encoding="utf-8",
    )
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
