"""Draw the hedge traditions' symbols, the counterpart of the Houses' for a
character who belongs to a tradition instead of the Order: each a woodcut
block like the House symbols, a rule just inside its edge and a figure
cut out of it, drawn with the Ability marks' shapes (gui/mark_shapes).

    uv run python tools/draw_traditions.py

Each is written to assets/symbols/traditions/<name>.svg, one even-odd
path in currentColor like the other symbols, so artwork.py and the
front-ends treat it exactly as they treat a House's."""

from __future__ import annotations

import math
import os
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QPainterPath, QTransform
from PySide6.QtWidgets import QApplication

from ars_magica_manager import artwork
from ars_magica_manager.gui.mark_charges import RUNES, _rune
from ars_magica_manager.gui.mark_shapes import (
    bar,
    circle,
    ellipse,
    outline_triangle,
    over,
    poly,
    rect,
    rotate,
    rough,
    rrect,
    scaled,
    tile,
    union,
    union_of,
    vesica,
)


def elementalists() -> QPainterPath:
    """The four element triangles quartered, like a coat of arms."""
    signs = (
        outline_triangle(True),
        outline_triangle(True, True),
        outline_triangle(False),
        outline_triangle(False, True),
    )
    return union(
        *(
            QTransform().translate(x, y).scale(0.36, 0.36).map(sign)
            for sign, (x, y) in zip(
                signs, ((16, 16), (48, 16), (16, 48), (48, 48)), strict=True
            )
        ),
        rect(48, 18, 4, 64),
        rect(18, 48, 64, 4),
    )


def folk_witches() -> QPainterPath:
    """A hare leaping, the shape a witch takes to run abroad by night."""
    body = rotate(ellipse(22, 38, 50, 22), -8, 47, 49)
    haunch = circle(32, 50, 12)
    head = rotate(ellipse(62, 26, 22, 15), -10, 73, 33)
    ears = union(
        rotate(vesica(56, 21, 30, 7), 24, 56, 21),
        rotate(vesica(60, 18, 26, 6), 40, 60, 18),
    )
    fore = union(bar(66, 44, 90, 52, 5), bar(64, 46, 84, 60, 4.5))
    hind = union(bar(30, 54, 8, 64, 7), bar(10, 62, 2, 64, 5))
    tail = circle(19, 40, 5)
    eye = circle(76, 30, 2)
    return union(body, haunch, head, ears, fore, hind, tail).subtracted(eye)


def gruagachan() -> QPainterPath:
    """A Pictish symbol stone, its crescent and V-rod carved in the face."""
    stone = QPainterPath()
    stone.moveTo(28, 88)
    stone.lineTo(26, 34)
    stone.cubicTo(26, 12, 74, 12, 74, 34)
    stone.lineTo(72, 88)
    stone.closeSubpath()
    moon = circle(50, 52, 20).subtracted(circle(50, 40, 18))
    rod = union(
        bar(36, 30, 50, 66, 3.4),
        bar(50, 66, 64, 30, 3.4),
        poly((32, 26), (40, 30), (34, 35)),
        poly((68, 26), (60, 30), (66, 35)),
    )
    disc = union(circle(50, 78, 4), circle(40, 78, 3), circle(60, 78, 3))
    return stone.subtracted(union(moon, rod, disc))


def learned_magicians() -> QPainterPath:
    """A charta, the learned magicians' written charm: a sealed sheet with
    a seal hanging from it on a cord."""
    sheet = union(rect(20, 14, 60, 52), rrect(16, 10, 68, 8, 4))
    lines = union_of(
        rect(28, 26 + 8 * i, 44 - (12 if i == 4 else 0), 3) for i in range(5)
    )
    cord = union(bar(44, 64, 40, 74, 3), bar(56, 64, 60, 74, 3))
    seal = circle(50, 80, 12).subtracted(circle(50, 80, 7)).united(circle(50, 80, 3.5))
    return union(sheet.subtracted(lines), cord, seal)


def _umbel(cx: float, cy: float, r: float, w: float) -> QPainterPath:
    """A fennel flower head: rays spreading up from one point, each ending
    in a cluster of florets."""
    rays = []
    for a in (22, 61, 90, 119, 158):
        x = cx + r * math.cos(math.radians(a))
        y = cy - r * math.sin(math.radians(a))
        florets = union(
            circle(x, y - w, w * 0.9),
            circle(x - w, y, w * 0.9),
            circle(x + w, y, w * 0.9),
        )
        rays.append(union(bar(cx, cy, x, y, w * 0.7), florets))
    return union_of(rays)


def nightwalkers() -> QPainterPath:
    """A stalk of fennel, the benandanti's weapon in their night battles
    with the witches, held up in the cradle of the moon."""
    moon = circle(50, 58, 34).subtracted(circle(50, 44, 30))
    stalk = rect(46.5, 44, 7, 50)
    head = _umbel(50, 44, 28, 4.4)
    return over(union(stalk, head), moon)


def vitkir() -> QPainterPath:
    """Odin's rune, Ansuz, ringed by the eight runes of Freya's aett."""
    centre = scaled(_rune(*RUNES["Ansuz"]), 0.5)
    ring_of = union_of(
        rotate(
            QTransform().translate(46.2, 2).scale(0.2, 0.2).map(_rune(*RUNES[name])),
            45 * i,
        )
        for i, name in enumerate(list(RUNES)[:8])
    )
    band = circle(50, 50, 30).subtracted(circle(50, 50, 25))
    return union(centre, ring_of, band)


#: Each tradition's figure, by its tradition_catalog.json id.
FIGURES: dict[str, Callable[[], QPainterPath]] = {
    "trad_elementalists": elementalists,
    "trad_folk_witches": folk_witches,
    "trad_gruagachan": gruagachan,
    "trad_learned_magicians": learned_magicians,
    "trad_nightwalkers": nightwalkers,
    "trad_vitkir": vitkir,
}


def symbol(tradition_id: str) -> QPainterPath:
    """The block with its inner rule and the figure cut out of it."""
    seed = sum(map(ord, tradition_id))
    block = tile()
    rule = scaled(block, 0.9).subtracted(scaled(block, 0.86))
    figure = FIGURES[tradition_id]()
    box = figure.boundingRect()
    k = 62 / max(box.width(), box.height())
    c = box.center()
    figure = (
        QTransform().translate(50, 50).scale(k, k).translate(-c.x(), -c.y()).map(figure)
    )
    cut = rough(rule, seed + 1, 0.35).united(rough(figure, seed + 2, 0.4))
    return rough(block, seed, 0.8).subtracted(cut).simplified()


def svg(path: QPainterPath) -> str:
    rings = []
    for polygon in path.toSubpathPolygons():
        points = [polygon.at(i) for i in range(polygon.count())]
        rings.append("M" + " L".join(f"{p.x():.2f},{p.y():.2f}" for p in points) + "Z")
    return (
        "<!-- Drawn by tools/draw_traditions.py. -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        f'fill="currentColor" fill-rule="evenodd"><path d="{" ".join(rings)}"/></svg>\n'
    )


def main() -> None:
    if QApplication.instance() is None:
        QApplication([])
    for tradition_id, out in artwork.TRADITION_SYMBOLS.items():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg(symbol(tradition_id)), encoding="utf-8")
        print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
