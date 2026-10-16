"""Draw the ruined covenant's icon: Phosphor's castle turret (the
covenant's icon, MIT) with its top broken off, a crack in its wall and
fallen stones at its foot, in the same Light weight (strokes 12 units
wide on a 256 square, round ends and joins).

    uv run --group charges python tools/draw_ruin.py

The strokes are widened into one filled outline with shapely (the
`charges` dependency group) and written to assets/drawn/ruin.svg, drawn
in currentColor like the other icons."""

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


def _arch(left: float, right: float, spring: float) -> list[Point]:
    """A doorway: up from the ground, a round arch, and down again."""
    r = (right - left) / 2
    cx = left + r
    top = [
        (cx - r * math.cos(math.pi * i / 16), spring - r * math.sin(math.pi * i / 16))
        for i in range(17)
    ]
    return [(left, 224), *top, (right, 224)]


def _stone(x: float, y: float, w: float, h: float, turn: float) -> list[Point]:
    """A fallen block, tipped by `turn` degrees about its centre."""
    a = math.radians(turn)
    cx, cy = x + w / 2, y + h / 2
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    return [
        (
            cx + (px - cx) * math.cos(a) - (py - cy) * math.sin(a),
            cy + (px - cx) * math.sin(a) + (py - cy) * math.cos(a),
        )
        for px, py in corners
    ]


#: The strokes: the ground, the tower's walls up to their broken top, the
#: doorway, a crack, and the stones that fell.
STROKES: list[list[Point]] = [
    [(28, 224), (228, 224)],
    [
        (64, 224),
        (64, 112),
        (50, 98),
        (50, 52),
        (72, 52),
        (80, 70),
        (96, 62),
        (108, 84),
        (124, 78),
        (136, 102),
        (152, 96),
        (164, 120),
        (180, 114),
        (192, 132),
        (192, 224),
    ],
    _arch(108, 148, 170),
    [(84, 132), (94, 146), (86, 160), (92, 172)],
    _stone(208, 202, 18, 14, 0),
    _stone(214, 176, 13, 11, -20),
    _stone(30, 207, 14, 11, 8),
]


def main() -> None:
    shapely: Any = importlib.import_module("shapely")
    outline = shapely.unary_union(
        [
            shapely.LineString(stroke).buffer(
                HALF, cap_style="round", join_style="round"
            )
            for stroke in STROKES
        ]
    ).simplify(0.2)
    parts = outline.geoms if hasattr(outline, "geoms") else [outline]
    rings = []
    for part in parts:
        rings.append(list(part.exterior.coords)[:-1])
        rings.extend(list(hole.coords)[:-1] for hole in part.interiors)
    d = " ".join(
        "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + "Z" for ring in rings
    )
    out = artwork.DRAWN / "ruin.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "<!-- Drawn by tools/draw_ruin.py after Phosphor's castle-turret (MIT). -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" '
        f'fill="currentColor" fill-rule="evenodd"><path d="{d}"/></svg>\n',
        encoding="utf-8",
    )
    print(f"wrote {out.name}: {len(rings)} rings")


if __name__ == "__main__":
    main()
