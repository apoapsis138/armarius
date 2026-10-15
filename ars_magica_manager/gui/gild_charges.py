"""The Rhine's six gild symbols, cut as marks.py cuts the ability marks: a
dark woodcut block with the gild's tree cut out of it in light, then the
veins and grain engraved back in on a large mark.

Each keeps the general shape the gilds are known by (an oak leaf, a
thorn, an ash spearhead, an elder sprig, a linden leaf, an apple), drawn
fresh here from circles, curves and bars, in the 100 x 100 box of
mark_shapes.
"""

from __future__ import annotations

from PySide6.QtGui import QPainterPath

from .mark_charges import Charge
from .mark_shapes import (
    bar,
    circle,
    curve,
    heart,
    line,
    poly,
    rect,
    ring,
    rotate,
    stroke,
    union,
    union_of,
    vesica,
)


def _almond(cx: float, cy: float, w: float, h: float) -> QPainterPath:
    """An upright almond, `w` across and `h` tall (h > w)."""
    return rotate(vesica(cx, cy, h, w), 90, cx, cy)


#: The oak leaf's lobes, from the stalk up: (where on the midrib they
#: spring, how far they reach, their radius, their slant from upright).
#: Those on the right sit a little higher, as a real leaf's do.
_OAK_LOBES = ((72, 16, 7.5, 70), (57, 21, 9.5, 62), (41, 20, 9, 52), (27, 14, 7.5, 40))


def _oak_lobe(y: float, reach: float, r: float, slant: float, side: int):
    """A lobe's tip and the finger joining it to the midrib."""
    tip = rotate(circle(50, y - reach, r), side * slant, 50, y)
    finger = rotate(bar(50, y, 50, y - reach, r * 1.5), side * slant, 50, y)
    return union(tip, finger)


def oak() -> QPainterPath:
    """An upright oak leaf: rounded lobes in pairs up a midrib, the
    largest midway, closing in a round tip over a short stalk."""
    lobes = union_of(
        union(
            _oak_lobe(y, reach, r, slant, -1),
            _oak_lobe(y - 3, reach, r, slant, 1),
        )
        for y, reach, r, slant in _OAK_LOBES
    )
    return union(
        _almond(50, 48, 16, 70),
        lobes,
        circle(50, 13, 8),
        bar(50, 80, 52, 95, 4.5),
    )


def _oak_veins() -> QPainterPath:
    veins = [line((50, 88), (50, 10), w=1.6)]
    for y, reach, _r, slant in _OAK_LOBES:
        for side, at in ((-1, y), (1, y - 3)):
            veins.append(
                rotate(line((50, at), (50, at - reach), w=1.1), side * slant, 50, at)
            )
    return union_of(veins)


def hawthorn() -> QPainterPath:
    """A hawthorn thorn rising from its twig: broad where it springs,
    sweeping up in a curve to a needle point."""
    thorn = QPainterPath()
    thorn.moveTo(16, 82)
    thorn.cubicTo(24, 50, 50, 22, 84, 6)
    thorn.cubicTo(64, 30, 66, 58, 72, 82)
    thorn.closeSubpath()
    twig = union(
        bar(8, 84, 92, 80, 9),
        circle(92, 80, 4.5),
        bar(70, 82, 86, 92, 4),  # a side shoot under the twig
    )
    return union(thorn, twig)


def _hawthorn_grain() -> QPainterPath:
    return union(
        stroke(curve((32, 79), (42, 48), (72, 18)), 1.2),
        stroke(curve((46, 80), (52, 50), (76, 16)), 1.0),
        stroke(curve((58, 80), (60, 54), (79, 13)), 0.9),
        line((14, 84), (40, 83), w=1.0),
        line((76, 82), (88, 80), w=1.0),
    )


def _ash_upright() -> QPainterPath:
    blade = QPainterPath()
    blade.moveTo(50, 2)
    blade.cubicTo(58, 22, 62, 42, 58, 58)
    blade.lineTo(54, 64)
    blade.lineTo(46, 64)
    blade.lineTo(42, 58)
    blade.cubicTo(38, 42, 42, 22, 50, 2)
    blade.closeSubpath()
    socket = poly((45, 63), (55, 63), (54, 84), (46, 84))
    lugs = union(
        poly((45, 70), (33, 80), (36, 84), (46, 76)),
        poly((55, 70), (67, 80), (64, 84), (54, 76)),
    )
    return union(blade, socket, lugs, ring(50, 90, 6, 3.5))


def ash() -> QPainterPath:
    """An ash-shafted spearhead laid on the slant: a long leaf blade on a
    socket with two lugs, and the ring that binds it to its shaft."""
    return rotate(_ash_upright(), 35)


def _ash_detail() -> QPainterPath:
    return rotate(
        union(
            line((50, 10), (50, 60), w=1.4),
            line((46.5, 70), (53.5, 70), w=1.0),
            line((46.8, 77), (53.2, 77), w=1.0),
        ),
        35,
    )


#: The elder sprig's leaflets: (where on the stem, angle, length).
_ELDER_LEAFLETS = ((50, -58, 30), (50, 58, 30), (70, -64, 26), (70, 64, 26))


def _leaflet(y: float, angle: float, length: float) -> QPainterPath:
    """A pointed leaflet springing from the stem at height `y`."""
    return rotate(_almond(50, y - length / 2, length * 0.36, length), angle, 50, y)


def elder() -> QPainterPath:
    """An elder sprig: a tall leaflet at the tip of its stalk and two
    pairs of pointed leaflets spreading below it."""
    leaves = union_of(_leaflet(*leaf) for leaf in _ELDER_LEAFLETS)
    tip = _almond(50, 24, 13, 38)
    return union(tip, leaves, bar(50, 40, 50, 96, 4.5))


def _elder_ribs() -> QPainterPath:
    ribs = [line((50, 40), (50, 10), w=1.1)]
    for y, angle, length in _ELDER_LEAFLETS:
        ribs.append(rotate(line((50, y), (50, y - length + 5), w=1.0), angle, 50, y))
    return union_of(ribs)


def _linden_upright() -> QPainterPath:
    leaf = heart(50, 52, 1.12)
    return union(leaf, bar(50, 33, 56, 8, 3.6))


def linden() -> QPainterPath:
    """A linden leaf, heart-shaped, hanging from its stalk with its point
    turned aside."""
    return rotate(_linden_upright(), 28)


def _linden_veins() -> QPainterPath:
    veins = [line((50, 36), (50, 84), w=1.5)]
    for y, reach in ((46, 22), (58, 22), (70, 15)):
        veins.append(
            stroke(curve((50, y), (50 - reach / 2, y - 2), (50 - reach, y - 8)), 1.1)
        )
        veins.append(
            stroke(curve((50, y), (50 + reach / 2, y - 2), (50 + reach, y - 8)), 1.1)
        )
    return rotate(union_of(veins), 28)


def apple() -> QPainterPath:
    """An apple on its stalk, a single leaf beside it."""
    body = union(circle(40, 60, 27), circle(60, 60, 27), circle(50, 72, 22))
    body = body.subtracted(circle(50, 31, 7)).subtracted(circle(50, 92, 3.5))
    stalk = stroke(curve((50, 36), (49, 22), (55, 12)), 4)
    leaf = rotate(_almond(68, 18, 13, 30), 62, 56, 20)
    return union(body, stalk, leaf)


def _apple_detail() -> QPainterPath:
    return union(
        # The shine on its cheek, and the leaf's rib.
        stroke(curve((26, 58), (26, 44), (36, 38)), 1.6),
        rotate(line((68, 30), (68, 7), w=1.0), 62, 56, 20),
        rect(49.2, 88, 1.6, 4),
    )


#: Each gild's symbol, by the tree its name names
#: (tribunal_packages.rhine.GILD_TREES).
GILDS: dict[str, Charge] = {
    "Oak": oak,
    "Hawthorn": hawthorn,
    "Ash": ash,
    "Elder": elder,
    "Linden": linden,
    "Apple": apple,
}

#: Those cut without the cutter's second line inside the edge, which
#: would ring each of their small lobes.
GILD_PLAIN = {"Oak", "Elder"}

#: The lines engraved back into each on a large mark.
GILD_DETAILS: dict[str, Charge] = {
    "Oak": _oak_veins,
    "Hawthorn": _hawthorn_grain,
    "Ash": _ash_detail,
    "Elder": _elder_ribs,
    "Linden": _linden_veins,
    "Apple": _apple_detail,
}
