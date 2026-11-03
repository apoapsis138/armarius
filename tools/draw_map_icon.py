"""Draw the Atlas's icon: a map folded in three, its panels tilted in and
out, with a road wandering across it to a cross marking a place, in the
weight of the app's Phosphor Light icons (strokes 12 units wide on a 256
square, round ends and joins).

    uv run --group charges python tools/draw_map_icon.py

The strokes are widened into one filled outline with shapely (the
`charges` dependency group) and written to assets/drawn/map.svg, drawn
in currentColor like the other icons."""

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

#: The strokes: the map's outline, its two folds, a road, and a cross.
STROKES: list[list[Point]] = [
    [
        (32, 64),
        (96, 40),
        (160, 64),
        (224, 40),
        (224, 192),
        (160, 216),
        (96, 192),
        (32, 216),
        (32, 64),
    ],
    [(96, 40), (96, 192)],
    [(160, 64), (160, 216)],
    [(56, 176), (76, 150), (104, 156), (124, 128), (148, 132), (164, 108)],
    [(178, 86), (202, 110)],
    [(202, 86), (178, 110)],
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
    out = artwork.DRAWN / "map.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "<!-- Drawn by tools/draw_map_icon.py: a folded map. -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" '
        f'fill="currentColor" fill-rule="evenodd"><path d="{d}"/></svg>\n',
        encoding="utf-8",
    )
    print(f"wrote {out.name}: {len(rings)} rings")


if __name__ == "__main__":
    main()
