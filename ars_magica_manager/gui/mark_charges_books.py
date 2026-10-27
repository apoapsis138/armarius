"""The charges of the Abilities from the hedge books beyond Hedge Magic:
the faerie, holy and infernal powers of Realms of Power, the Ex
Miscellanea and regional traditions, Rival Magic, Ancient Magic and the
Hunters' Arts. Drawn like mark_charges's, in the 100 x 100 box of
mark_shapes."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from itertools import pairwise

from PySide6.QtGui import QPainterPath, QTransform

from .mark_shapes import (
    bar,
    circle,
    curve,
    ellipse,
    flame,
    heart,
    over,
    poly,
    rect,
    ring,
    rotate,
    rrect,
    star,
    stroke,
    union,
    union_of,
    vesica,
    weave,
)


def _pt(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _open(*points: tuple[float, float]) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    return path


def circle_path(cx: float, cy: float, r: float) -> QPainterPath:
    """A circle as a line to weave, not a disc to fill."""
    points = [
        (
            cx + r * math.cos(2 * math.pi * i / 120),
            cy + r * math.sin(2 * math.pi * i / 120),
        )
        for i in range(121)
    ]
    return _open(*points)


def _bez(points: Sequence[tuple[float, float]], t: float) -> tuple[float, float]:
    """A point along the smooth curve the points outline (de Casteljau)."""
    pts = list(points)
    while len(pts) > 1:
        pts = [
            (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            for a, b in pairwise(pts)
        ]
    return pts[0]


def _tongue(points: Sequence[tuple[float, float]], w: float) -> QPainterPath:
    """A tongue of flame: a band along the curve, tapering to its tip."""
    return union_of(
        circle(*_bez(points, t / 40), w * (1 - t / 40) + 0.4) for t in range(41)
    )


# -- The faerie rites and the Ars Fabulosa --


def enchantment():
    """A player's mask, the rite hidden in the performance, its ribbons
    trailing."""
    face = ellipse(24, 22, 52, 60)
    eyes = union(
        rotate(vesica(38, 44, 14, 6), -10, 38, 44),
        rotate(vesica(62, 44, 14, 6), 10, 62, 44),
    )
    mouth = (
        circle(50, 66, 12)
        .subtracted(circle(50, 60, 12))
        .intersected(rect(30, 62, 40, 20))
    )
    brow = stroke(curve((32, 34), (38, 30), (46, 34)), 2.4).united(
        stroke(curve((54, 34), (62, 30), (68, 34)), 2.4)
    )
    mask = face.subtracted(union(eyes, mouth, brow))
    ribbons = union(
        stroke(curve((24, 48), (12, 60), (18, 76), (24, 90), (12, 96)), 3),
        stroke(curve((76, 48), (88, 60), (82, 76), (76, 90), (88, 96)), 3),
    )
    return union(mask, ribbons)


def empathy():
    """An eye closed in trance, a spiral turning below it."""
    lid = stroke(curve((14, 30), (50, 56), (86, 30)), 5)

    def under(x: float):
        return 30 + 26 * (1 - ((x - 50) / 36) ** 2) * 0.5 + 2

    lashes = union_of(
        bar(x, under(x), x + (x - 50) * 0.2, under(x) + 10, 3.2)
        for x in (28, 39, 50, 61, 72)
    )
    spiral = _spiral(50, 76, 16)
    return union(lid, lashes, spiral)


def _spiral(cx: float, cy: float, r: float):
    """A spiral of 1.3 turns winding out from its centre."""
    pts = []
    for i in range(80):
        t = i / 79 * 2.6 * 2 * math.pi
        rr = 3 + (r - 3) * i / 79
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return stroke(_open(*pts), 3.6)


def beguile():
    """A puppeteer's cross, its strings drawn down to a heart."""
    cross = union(rrect(16, 12, 68, 7, 3), rrect(46, 4, 8, 30, 3))
    strings = union(
        bar(22, 18, 38, 62, 1.6), bar(78, 18, 62, 62, 1.6), bar(50, 32, 50, 56, 1.6)
    )
    h = heart(50, 72, 0.9)
    return union(cross, strings, h)


def conjure():
    """A butterfly of glamour rising from the mist the rite conjures it
    out of."""
    wings = union(
        rotate(vesica(32, 34, 34, 22), -35, 32, 34),
        rotate(vesica(68, 34, 34, 22), 35, 68, 34),
        rotate(vesica(36, 60, 22, 14), 30, 36, 60),
        rotate(vesica(64, 60, 22, 14), -30, 64, 60),
    )
    body = rrect(47, 26, 6, 42, 3)
    feelers = union(
        stroke(curve((49, 27), (44, 14), (36, 10)), 2),
        stroke(curve((51, 27), (56, 14), (64, 10)), 2),
    )
    mist = union(
        stroke(curve((14, 82), (32, 76), (50, 82), (68, 88), (86, 82)), 3.4),
        stroke(curve((22, 92), (40, 86), (58, 92), (70, 96), (80, 92)), 3),
    )
    return union(wings.subtracted(rect(45, 20, 10, 56)), body, feelers, mist)


def dream():
    """The sleeping moon, an eye opening in it on what is to come."""
    moon = circle(46, 50, 36).subtracted(circle(62, 42, 30))
    eye = (
        vesica(34, 56, 20, 10)
        .subtracted(circle(34, 56, 3.4))
        .united(circle(34, 56, 1.6))
    )
    stars = union(
        star(4, 8, 2, 76, 72), star(4, 6, 1.6, 84, 50), star(4, 5, 1.4, 66, 86)
    )
    return union(moon.subtracted(vesica(34, 56, 24, 13)), eye, stars)


def grant():
    """A faerie's gift: a ring, its stone shining."""
    band = ring(50, 62, 26, 7)
    setting = poly((38, 38), (62, 38), (58, 30), (42, 30))
    stone = poly((42, 30), (58, 30), (50, 18))
    rays = union_of(
        bar(*_pt(50, 24, 14, a), *_pt(50, 24, 24, a), 3)
        for a in (-160, -125, -90, -55, -20)
    )
    return union(band, setting, stone.subtracted(bar(50, 20, 50, 30, 1.6)), rays)


def portage():
    """A door in the hill opening on the faerie road, stars beyond it."""
    hill = circle(50, 120, 74).intersected(rect(0, 46, 100, 54))
    door = union(rect(36, 50, 28, 40), circle(50, 50, 14))
    stars = union(
        star(4, 6, 1.6, 50, 52), star(4, 4, 1.2, 44, 66), star(4, 4, 1.2, 57, 72)
    )
    path = poly((44, 90), (56, 90), (66, 100), (34, 100))
    lintel = ring(50, 50, 19, 3.4).intersected(rect(0, 26, 100, 24))
    return union(hill.subtracted(union(door, path)), stars, lintel)


def ware():
    """A shield, a sprig of rowan across it against the fair folk."""
    shield = poly((18, 14), (82, 14), (82, 46), (50, 92), (18, 46))
    inner = poly((24, 20), (76, 20), (76, 45), (50, 84), (24, 45))
    sprig = stroke(curve((30, 74), (48, 52), (70, 26)), 3)
    leaves = union_of(
        rotate(vesica(x, y, 14, 5), r, x, y)
        for x, y, r in ((36, 58, -110), (46, 52, 20), (54, 40, -110), (62, 36, 20))
    )
    berries = union(circle(66, 22, 4), circle(72, 27, 4), circle(64, 30, 3.6))
    return union(shield.subtracted(inner), sprig, leaves, berries)


def weal():
    """The golden apple of the Isles of the Blessed, its leaf and blossom."""
    apple = union(circle(38, 60, 26), circle(62, 60, 26)).intersected(
        circle(50, 66, 32)
    )
    dent = circle(50, 34, 7)
    stalk = stroke(curve((50, 38), (50, 26), (56, 16)), 3.4)
    leaf = rotate(vesica(68, 22, 22, 9), -20, 68, 22)
    vein = bar(60, 25, 76, 19, 1.4)
    shine = rotate(vesica(34, 54, 16, 6), -60, 34, 54)
    return union(apple.subtracted(union(dent, shine)), stalk, leaf.subtracted(vein))


def woe():
    """A briar, its thorns drawing a drop of blood."""
    stem = stroke(curve((14, 88), (40, 60), (50, 50), (60, 40), (86, 12)), 4.5)
    thorns = union_of(
        rotate(poly((-5, 0), (5, 0), (0, -14)), r, 0, 0).translated(x, y)
        for x, y, r in ((26, 74, -45), (42, 58, 135), (58, 42, -45), (74, 26, 135))
    )
    drop = union(circle(64, 78, 8), poly((57, 75), (64, 60), (71, 75)))
    return union(stem, thorns, drop)


def faerie_summoning():
    """The hunting horn that calls a faerie to the summoner, on its
    baldric."""
    pts = [(12 + 66 * t, 74 - 48 * t * t) for t in [i / 40 for i in range(41)]]
    horn = union_of(
        circle(x, y, 2.5 + 12 * (i / 40) ** 2.2) for i, (x, y) in enumerate(pts)
    )
    # cut square across the bell so it ends in an open mouth
    horn = horn.subtracted(rotate(rect(78, -34, 60, 120), -55, 78, 26))
    mouth = rotate(rect(70, 10, 3, 34), -55, 78, 26)
    grooves = union(bar(32, 62, 38, 76, 2.4), bar(52, 52, 60, 66, 2.4))
    strap = stroke(curve((28, 74), (50, 98), (64, 58)), 2.6)
    return union(
        horn.subtracted(union(grooves, mouth.intersected(horn))), strap.subtracted(horn)
    )


def bonding():
    """Two rings interlaced, the bargainer bound to the faerie."""
    return union(
        weave([circle_path(38, 50, 22), circle_path(62, 50, 22)], 6, 2.2),
        circle(50, 50, 3),
    )


def captivating():
    """A hand mirror, a stranger's eyes looking out of the glass."""
    frame = ring(50, 38, 28, 5)
    glass_eyes = union(vesica(40, 38, 14, 7), vesica(60, 38, 14, 7))
    pupils = union(circle(40, 38, 2.4), circle(60, 38, 2.4))
    handle = union(rrect(45, 64, 10, 30, 3), rect(40, 64, 20, 5))
    return union(frame, glass_eyes.subtracted(pupils), handle)


def dismissing():
    """A seal broken in two, the bargain undone, its ribbons hanging."""
    seal = circle(50, 40, 26).subtracted(star(5, 12, 5, 50, 40))
    crack = [(50, 8), (46, 24), (54, 34), (46, 48), (54, 60), (50, 72)]
    left = poly(*crack, (0, 72), (0, 8))
    halves = union(
        seal.intersected(left).translated(-4, 2),
        seal.subtracted(left).translated(4, -2),
    )
    ribbons = union(
        poly((36, 64), (44, 66), (34, 96), (28, 90)),
        poly((64, 64), (56, 66), (66, 96), (72, 90)),
    )
    return union(over(halves, ribbons), halves)


def evocation():
    """The silver branch whose bells call the fair folk, three bells
    hanging from it and a star where they answer."""
    branch = stroke(curve((10, 40), (40, 18), (88, 26)), 4.5)
    twigs = union(
        stroke(curve((30, 29), (30, 38), (30, 46)), 2.4),
        stroke(curve((52, 23), (52, 34), (52, 44)), 2.4),
        stroke(curve((74, 24), (74, 36), (74, 48)), 2.4),
        rotate(vesica(22, 30, 14, 6), -30, 22, 30),
        rotate(vesica(62, 18, 14, 6), 20, 62, 18),
        rotate(vesica(84, 18, 12, 5), -20, 84, 18),
    )

    def bell(x: float, y: float):
        body = poly((x - 3, y), (x + 3, y), (x + 7, y + 13), (x - 7, y + 13))
        return union(body, circle(x, y + 15, 2.4), circle(x, y, 3))

    bells = union(bell(30, 47), bell(52, 45), bell(74, 49))
    called = star(4, 14, 3.5, 50, 82, -90)
    return union(branch, twigs, bells, called)


# -- Holy Methods and Powers, and the holy traditions --


def _candle(x: float, base: float, h: float, w: float = 8):
    return union(rect(x - w / 2, base - h, w, h), flame(x, base - h - 2, w * 0.9, 14))


def ceremony():
    """Candles set round an altar, each for one who joins the rite."""
    altar = union(rect(30, 66, 40, 22), rect(26, 62, 48, 6))
    cross = union(rect(47, 34, 6, 26), rect(40, 40, 20, 5))
    candles = union(
        _candle(14, 86, 26, 7),
        _candle(86, 86, 26, 7),
        _candle(28, 58, 16, 6),
        _candle(72, 58, 16, 6),
    )
    return union(altar, cross, candles)


def invocation():
    """A prayer written on a scroll, its words rising as rays to a star."""
    sheet = rrect(26, 52, 48, 34, 3)
    rolls = union(rrect(20, 48, 60, 7, 3.5), rrect(20, 84, 60, 7, 3.5))
    words = union_of(rect(32, 60 + 7 * i, 36 - 8 * (i % 2), 2.6) for i in range(3))
    rays = union_of(
        bar(50, 44, *_pt(50, 44, 26, a), 2.6) for a in (-130, -110, -70, -50)
    )
    return union(rolls, sheet.subtracted(words), rays, star(5, 10, 4, 50, 14))


def meditation():
    """One flame burning still within a ring of quiet."""
    return union(
        ring(50, 52, 38, 4),
        ring(50, 52, 30, 1.8),
        flame(50, 74, 22, 44),
        rect(40, 74, 20, 6),
    )


def purity():
    """A lily, white and upright."""
    petals = union(
        rotate(vesica(50, 32, 40, 14), 90, 50, 32),
        rotate(vesica(36, 40, 34, 12), 125, 36, 40),
        rotate(vesica(64, 40, 34, 12), 55, 64, 40),
    )
    stamens = union(bar(50, 50, 42, 22, 1.6), bar(50, 50, 58, 22, 1.6))
    stem = stroke(curve((50, 50), (52, 72), (50, 94)), 4)
    leaves = union(
        rotate(vesica(38, 78, 24, 8), -35, 38, 78),
        rotate(vesica(62, 70, 24, 8), 35, 62, 70),
    )
    return union(petals.subtracted(stamens), stem, leaves)


def intervention():
    """Heaven's light breaking from a cloud."""
    cloud = union(
        circle(32, 28, 14),
        circle(50, 22, 17),
        circle(68, 28, 14),
        rrect(18, 26, 64, 18, 9),
    )
    rays = union_of(
        poly(
            *(
                _pt(50, 40, 6, a - 8),
                _pt(50, 40, 6, a + 8),
                _pt(50, 40, 56, a + 4),
                _pt(50, 40, 56, a - 4),
            )
        )
        for a in (50, 70, 90, 110, 130)
    )
    return union(cloud, rays.subtracted(circle(50, 40, 12)))


def transcendence():
    """A ladder climbing to a star, as the soul climbs to God."""
    rails = union(bar(30, 94, 42, 22, 4), bar(70, 94, 58, 22, 4))
    rungs = union_of(rect(32 + 2 * i, 84 - 13 * i, 36 - 4 * i, 4) for i in range(5))
    return union(rails, rungs, star(8, 14, 5, 50, 14))


def understanding():
    """An eye in a triangle, light going out from it."""
    tri = poly((50, 14), (88, 80), (12, 80)).subtracted(
        poly((50, 26), (78, 74), (22, 74))
    )
    eye = (
        vesica(50, 56, 28, 14).subtracted(circle(50, 56, 4.4)).united(circle(50, 56, 2))
    )
    rays = union_of(
        bar(*_pt(50, 56, 44, a), *_pt(50, 56, 54, a), 3)
        for a in range(-90 + 25, 270, 50)
        if not 20 < a % 360 < 160
    )
    return union(tri, eye, rays)


def wonders():
    """A star over the waters, as creation was called out of them."""
    st = star(8, 26, 10, 50, 40)
    core = circle(50, 40, 5)
    waves = union_of(
        stroke(
            _open(*((14 + 2 * i, y + 3 * math.sin(i * 0.5)) for i in range(37))), 3.4
        )
        for y in (76, 88)
    )
    return union(st.subtracted(core), waves)


def craft_amulets():
    """An amulet on its cord, the Shield of David on its face."""
    face = rrect(26, 34, 48, 56, 6).subtracted(rrect(31, 39, 38, 46, 3))
    tri = [_pt(50, 62, 15, a) for a in (-90, 30, 150, -90)]
    tri2 = [_pt(50, 62, 15, a) for a in (90, 210, 330, 90)]
    hexagram = weave([_open(*tri), _open(*tri2)], 3, 1.4)
    cord = stroke(curve((32, 36), (50, -6), (68, 36)), 3)
    return union(face, hexagram, cord)


def dream_interpretation():
    """Joseph's dream: the sun, the moon and the eleven stars."""
    sun = union(
        circle(36, 50, 13),
        union_of(
            bar(*_pt(36, 50, 16, a), *_pt(36, 50, 21, a), 2.6)
            for a in range(0, 360, 45)
        ),
    )
    moon = circle(68, 50, 13).subtracted(circle(74, 46, 11))
    stars = union_of(
        star(4, 4.5, 1.4, *_pt(50, 50, 40, -90 + i * 360 / 11)) for i in range(11)
    )
    return union(sun, moon, stars)


def _trefoil_end(x: float, y: float, r: float):
    return union(
        circle(x, y, r),
        circle(x - r * 0.9, y + r * 0.9, r * 0.8),
        circle(x + r * 0.9, y + r * 0.9, r * 0.8),
    )


def holy_magic():
    """A cross flowering at its ends, the Art turned to God, in a ring."""
    arms = union(rect(46, 16, 8, 68), rect(16, 46, 68, 8))
    ends = union(
        _trefoil_end(50, 14, 6),
        rotate(_trefoil_end(50, 14, 6), 90),
        rotate(_trefoil_end(50, 14, 6), 180),
        rotate(_trefoil_end(50, 14, 6), 270),
    )
    return union(
        arms,
        ends,
        ring(50, 50, 22, 3.4)
        .subtracted(rect(44, 0, 12, 100))
        .subtracted(rect(0, 44, 100, 12)),
    )


def ars_notoria():
    """The seven rings of Solomon set round an open book."""
    rings = union_of(
        ring(*_pt(50, 50, 36, -90 + i * 360 / 7), 7, 2.6) for i in range(7)
    )
    left = poly((26, 40), (49, 44), (49, 66), (26, 62))
    right = poly((74, 40), (51, 44), (51, 66), (74, 62))
    lines = union_of(rect(x, y, 16, 2) for x in (30, 54) for y in (48, 54))
    return union(rings, union(left, right).subtracted(lines))


def saints_aid():
    """A pilgrim's scallop shell, the badge of a saint's road."""
    shell = (
        circle(50, 58, 34)
        .intersected(rect(0, 0, 100, 58))
        .united(poly((30, 58), (70, 58), (50, 80)))
    )
    ribs = union_of(bar(50, 80, *_pt(50, 58, 36, a), 2) for a in range(-160, -15, 18))
    hinge = union(poly((38, 76), (50, 82), (62, 76), (64, 88), (36, 88)))
    return union(shell.subtracted(ribs), hinge)


def banishing():
    """Bell, book and candle, with which the unclean are driven out."""
    book = rrect(10, 60, 44, 30, 3).subtracted(rect(14, 64, 4, 22))
    bell = union(
        poly((64, 58), (78, 58), (86, 86), (56, 86)),
        circle(71, 54, 6),
        circle(71, 90, 4),
    )
    candle = _candle(30, 58, 22, 9)
    return union(book, bell, candle)


def gematria():
    """The magic square of Saturn and the sigil traced through its numbers
    one to nine, a ring at the first and a bar at the last."""
    frame = rrect(12, 12, 76, 76, 4).subtracted(rrect(18, 18, 64, 64, 2))
    grid = union(
        *(rect(18 + 64 * i / 3 - 1, 18, 2, 64) for i in (1, 2)),
        *(rect(18, 18 + 64 * i / 3 - 1, 64, 2) for i in (1, 2)),
    )
    # Lo Shu: 4 9 2 / 3 5 7 / 8 1 6
    cells = {4: (0, 0), 9: (1, 0), 2: (2, 0), 3: (0, 1), 5: (1, 1), 7: (2, 1),
             8: (0, 2), 1: (1, 2), 6: (2, 2)}  # fmt: skip

    def at(n: int):
        c, r = cells[n]
        return (28.7 + 21.3 * c, 28.7 + 21.3 * r)

    sigil = stroke(_open(*(at(n) for n in range(1, 10))), 4)
    x, y = at(1)
    start = ring(x, y, 5, 3)
    x, y = at(9)
    end = bar(x - 7, y, x + 7, y, 4)
    mark = union(sigil.subtracted(circle(*at(1), 4)), start, end)
    return union(frame, over(mark, grid, 2))


# -- The maleficia, the Goetic Arts and the Infernal --


def debauchery():
    """A wine goblet toppled on its side, its wine run out in a pool."""
    bowl = QPainterPath()
    bowl.moveTo(32, 22)
    bowl.cubicTo(30, 42, 38, 52, 50, 54)
    bowl.cubicTo(62, 52, 70, 42, 68, 22)
    bowl.closeSubpath()
    goblet = union(
        bowl, rect(47, 53, 6, 16), circle(50, 61, 4), rrect(36, 68, 28, 5, 2)
    )
    lying = rotate(goblet, -90, 50, 50).translated(24, 4)
    pool = QPainterPath()
    pool.moveTo(46, 74)
    pool.cubicTo(42, 82, 30, 80, 16, 82)
    pool.cubicTo(2, 84, 4, 94, 20, 94)
    pool.cubicTo(40, 95, 60, 94, 74, 90)
    pool.cubicTo(62, 88, 52, 86, 50, 76)
    pool.closeSubpath()
    return union(over(lying, pool, 2))


def incantation():
    """Lips parted on a forked tongue, the blasphemy spoken."""
    upper = poly(
        (10, 40), (30, 26), (44, 30), (50, 34), (56, 30), (70, 26), (90, 40), (50, 44)
    )
    lower = poly((12, 46), (50, 50), (88, 46), (70, 62), (50, 66), (30, 62))
    tongue = union(
        rect(44, 46, 12, 26), poly((44, 70), (56, 70), (64, 92), (50, 80), (36, 92))
    )
    return union(upper, over(tongue, lower, 2))


def consumption():
    """A leech fastened on the skin, swollen with what it has drawn."""
    swollen = rotate(ellipse(14, 26, 64, 34), 28, 46, 43)
    neck = poly((58, 50), (70, 40), (84, 72), (76, 76))
    body = union(swollen, neck)
    rings_ = union_of(
        rotate(rect(16 + 8 * i, 10, 1.8, 70), 28, 46, 43) for i in range(1, 7)
    ).intersected(swollen)
    sucker = ellipse(70, 72, 20, 8)
    tail = rotate(ellipse(10, 24, 12, 18), 28, 16, 33)
    skin = rect(8, 80, 84, 4)
    drop = union(circle(84, 92, 3.4), poly((81, 91), (84, 85), (87, 91)))
    return union(body.subtracted(rings_), sucker, tail, skin, drop)


def effusion():
    """A whirlwind lifting stones from the ground."""
    bands = union_of(
        stroke(
            curve(
                (50 + 3 * math.sin(i) - (34 - 6 * i), 18 + 11 * i),
                (50, 26 + 11 * i),
                (50 + 3 * math.sin(i) + (34 - 6 * i), 18 + 11 * i),
            ),
            4,
        )
        for i in range(5)
    )
    stones = union(
        rotate(rrect(10, 30, 9, 7, 2), 20, 14, 33),
        rotate(rrect(80, 52, 8, 6, 2), -30, 84, 55),
        rotate(rrect(18, 64, 7, 6, 2), 40, 21, 67),
    )
    tail = stroke(curve((48, 72), (54, 82), (50, 92)), 4)
    return union(bands, stones, tail)


def malediction():
    """A poppet, pins driven into it."""
    head = circle(50, 24, 12)
    body = union(
        rrect(36, 34, 28, 34, 6),
        bar(38, 40, 18, 56, 8),
        bar(62, 40, 82, 56, 8),
        bar(44, 64, 38, 90, 9),
        bar(56, 64, 62, 90, 9),
    )
    stitches = union_of(rect(48, 38 + 6 * i, 4, 2.4) for i in range(5))
    pins = union(
        bar(16, 20, 44, 48, 2.2),
        circle(16, 20, 4),
        bar(86, 30, 58, 54, 2.2),
        circle(86, 30, 4),
        bar(84, 80, 58, 60, 2.2),
        circle(84, 80, 4),
    )
    return union(over(pins, union(head, body).subtracted(stitches)))


def phantasm():
    """A castle in the air, and its image hanging upside down beneath:
    the mirage that deceives."""

    def castle():
        walls = rect(26, 30, 48, 16)
        towers = union(rect(22, 18, 12, 28), rect(66, 18, 12, 28), rect(43, 12, 14, 34))
        merlons = union_of(
            rect(x, y, 3.2, 4)
            for x, y in (
                (22, 14),
                (27.4, 14),
                (30.8, 14),
                (66, 14),
                (70.4, 14),
                (74.8, 14),
                (43, 8),
                (48.4, 8),
                (53.8, 8),
            )
        )
        gate = union(rect(46, 36, 8, 10), circle(50, 36, 4))
        return union(walls, towers, merlons).subtracted(gate)

    top = castle()
    image = QTransform().translate(0, 100).scale(1, -1).map(top)
    image = image.subtracted(union_of(rect(0, y, 100, 1.8) for y in range(56, 92, 5)))
    line = rect(10, 48, 80, 3)
    return union(top, line, image)


def psychomachia():
    """A heart being torn in two, the tear begun at its top."""
    h = heart(50, 52, 1.0)
    tear = poly(
        (50, 20), (46, 30), (53, 38), (47, 46), (52, 54), (50, 60),
        (51, 60), (55, 54), (50, 46), (56, 38), (49, 30), (54, 20),
    )  # fmt: skip
    left = h.subtracted(tear).intersected(rect(0, 0, 51, 100))
    right = h.subtracted(tear).subtracted(rect(0, 0, 51, 100))
    whole = h.intersected(rect(0, 60, 100, 40))
    left = rotate(left.subtracted(rect(0, 60, 100, 40)), -8, 50, 62)
    right = rotate(right.subtracted(rect(0, 60, 100, 40)), 8, 50, 62)
    return union(left, right, whole)


def summoning():
    """The triangle of art where the spirit is called, above the circle the
    summoner stands in: a ring of names round the square at its heart."""
    tri = poly((50, 8), (78, 46), (22, 46)).subtracted(
        poly((50, 18), (70, 42), (30, 42))
    )
    inner = circle(50, 33, 6)
    names = union_of(circle(*_pt(50, 74, 18.5, a), 1.8) for a in range(0, 360, 20))
    circ = union(ring(50, 74, 23, 3.4), ring(50, 74, 14, 2), names)
    square = rect(45, 69, 10, 10)
    return union(tri, inner, circ, square)


def ablating():
    """A spirit's flame flensed: a hooked blade paring a strip from it."""
    blaze = union(
        ellipse(18, 60, 44, 30),
        _tongue([(26, 70), (12, 56), (24, 40), (14, 26)], 8),
        _tongue([(40, 64), (32, 46), (46, 30), (38, 8)], 9),
        _tongue([(50, 70), (60, 54), (52, 40), (58, 26)], 6),
    )
    strip = _tongue([(58, 74), (72, 66), (80, 50), (72, 38)], 4.4)
    blade = QPainterPath()
    blade.moveTo(58, 82)
    blade.cubicTo(70, 74, 86, 76, 92, 64)
    blade.cubicTo(92, 80, 76, 88, 60, 88)
    blade.closeSubpath()
    grip = bar(60, 85, 44, 94, 6)
    return union(over(union(blade, grip), union(blaze, strip), 2))


def binding():
    """A stoppered bottle, Solomon's seal on its stopper, a spirit coiled
    within it."""
    glass = union(circle(50, 64, 26), rect(42, 22, 16, 30))
    hollow = union(circle(50, 64, 21), rect(46, 26, 8, 30))
    stopper = rrect(38, 10, 24, 14, 3)
    seal = star(6, 7, 4, 50, 17)
    pts = [(50 + 9 * math.sin(i * 0.55), 78 - i * 0.9) for i in range(30)]
    spirit = stroke(_open(*pts), 3.2)
    return union(
        glass.subtracted(hollow), stopper.subtracted(seal), spirit, circle(*pts[-1], 3)
    )


def commanding():
    """A sceptre thrust through a crown: rule over the spirits."""
    sceptre = union(bar(14, 90, 70, 20, 5), circle(72, 17, 6), star(4, 5, 1.6, 77, 10))
    band = rrect(26, 52, 44, 10, 2)
    points = poly((26, 52), (26, 36), (36, 46), (48, 30), (60, 46), (70, 36), (70, 52))
    jewels = union(circle(36, 57, 2.4), circle(48, 57, 2.4), circle(60, 57, 2.4))
    crown = union(
        band.subtracted(jewels),
        points,
        circle(26, 34, 3),
        circle(48, 28, 3),
        circle(70, 34, 3),
    )
    behind = sceptre.subtracted(stroke(crown, 4.4).united(crown))
    front = sceptre.intersected(rect(0, 62, 100, 40)).subtracted(crown)
    return union(
        crown.subtracted(sceptre.intersected(rect(0, 0, 100, 52))),
        behind,
        front,
        sceptre.intersected(rect(0, 0, 100, 52)).intersected(points),
    )


def corruption():
    """An apple with a bite taken from it, a worm crawling out of the
    bite."""
    apple = union(circle(38, 58, 24), circle(62, 58, 24)).intersected(
        circle(50, 64, 30)
    )
    dent = circle(50, 34, 6)
    bite = union(circle(80, 56, 9), circle(78, 68, 9), circle(82, 44, 7))
    stalk = stroke(curve((50, 38), (50, 26), (54, 16)), 3.4)
    leaf = rotate(vesica(66, 22, 22, 9), -20, 66, 22).subtracted(
        bar(58, 25, 74, 19, 1.4)
    )
    worm_line = [(74, 58), (84, 52), (90, 40), (84, 28)]
    worm = union_of(circle(*_bez(worm_line, t / 30), 3.6) for t in range(31))
    segments = union_of(
        circle(*_bez(worm_line, t / 6), 4.4).subtracted(
            circle(*_bez(worm_line, t / 6), 3.4)
        )
        for t in range(1, 6)
    )
    head = circle(84, 28, 4.6)
    return union(
        apple.subtracted(union(dent, bite)),
        stalk,
        leaf,
        worm.subtracted(segments),
        head,
    )


def chthonic_magic():
    """A torch turned upside down, its flame toward the underworld, as the
    gods below were shown."""
    flame_ = QPainterPath()
    flame_.moveTo(30, 42)
    flame_.cubicTo(18, 28, 30, 14, 44, 10)
    flame_.cubicTo(52, 8, 60, 6, 66, 0)
    flame_.cubicTo(64, 10, 80, 20, 70, 36)
    flame_.cubicTo(70, 38, 70, 40, 70, 42)
    flame_.closeSubpath()
    licks = union(
        stroke(curve((38, 40), (32, 26), (52, 14)), 3),
        stroke(curve((50, 40), (48, 28), (64, 16)), 3),
    )
    rim = rrect(24, 42, 52, 7, 2)
    cup = poly((27, 49), (73, 49), (64, 59), (36, 59))
    handle = poly((38, 59), (62, 59), (55, 92), (45, 92))
    knob = rrect(42, 92, 16, 6, 2)
    torch = union(flame_.subtracted(licks), rim, cup, handle, knob)
    return rotate(torch, 180, 50, 50)


def diablerie():
    """The summoner's circle: a pentagram turned point down, its lines
    interlaced, in a double ring crowned with a goat's horns."""
    pts = [_pt(50, 56, 28, 90 + 144 * i) for i in range(6)]
    pentagram = weave([_open(*pts)], 3.4, 1.8)
    rings = union(ring(50, 56, 36, 3.4), ring(50, 56, 29.5, 2))
    horns = union(
        poly((40, 22), (46, 21), (36, 8), (24, 4), (33, 10)),
        poly((60, 22), (54, 21), (64, 8), (76, 4), (67, 10)),
    )
    return union(pentagram, rings, horns)


# -- Ex Miscellanea and the regional traditions --


def control_fertility():
    """An egg broken open, a green shoot rising out of it."""
    egg = ellipse(26, 36, 48, 58)
    jag = poly(
        (20, 60),
        (32, 54),
        (40, 62),
        (50, 52),
        (60, 62),
        (68, 54),
        (80, 60),
        (80, 0),
        (20, 0),
    )
    shell = egg.subtracted(jag)
    shoot = stroke(curve((50, 76), (50, 44), (50, 22)), 4)
    leaves = union(
        rotate(vesica(38, 26, 24, 9), 30, 38, 26),
        rotate(vesica(62, 20, 24, 9), -30, 62, 20),
    )
    return union(over(shoot, shell, 2), leaves)


def warding():
    """A circle drawn on the ground, the staff that drew it at its edge."""
    circ = ellipse(10, 56, 80, 30).subtracted(ellipse(16, 61, 68, 20))
    staff = union(rect(70, 10, 5, 64), circle(72.5, 10, 5))
    return over(staff, circ, 2)


def comprehend_magic():
    """A reading stone held over a star, magnifying it."""
    lens = ring(42, 42, 26, 5)
    handle = bar(60, 60, 86, 86, 8)
    inner = star(5, 18, 7, 42, 44)
    outer = union_of(star(4, 4, 1.2, x, y) for x, y in ((80, 20), (20, 84), (84, 44)))
    return union(lens, handle, inner, outer)


def sihr():
    """A jinni's smokeless fire held within the eight-pointed star."""
    sq = rect(22, 22, 56, 56)
    st = union(sq, rotate(sq, 45)).subtracted(
        union(rect(27, 27, 46, 46), rotate(rect(27, 27, 46, 46), 45))
    )
    return union(st, flame(50, 66, 22, 36))


def solomonic_alchemy():
    """A crucible over the fire, Solomon's seal on its side."""
    crucible = poly((24, 30), (76, 30), (66, 70), (34, 70))
    seal = star(6, 12, 6, 50, 48)
    fire = union(flame(36, 94, 12, 22), flame(50, 94, 14, 26), flame(64, 94, 12, 22))
    rim = rrect(20, 24, 60, 8, 3)
    return union(crucible.subtracted(seal), rim, fire)


def solomonic_astrology():
    """An astrolabe: its ring, its star-pointers and its sighting rule."""
    body = ring(50, 54, 36, 5)
    shackle = union(ring(50, 12, 6, 3), rect(46, 16, 8, 4))
    rete = ring(50, 60, 20, 2.6).intersected(circle(50, 54, 32))
    pointers = union_of(
        poly(_pt(50, 54, 22, a - 6), _pt(50, 54, 22, a + 6), _pt(50, 54, 31, a))
        for a in (-150, -60, 20, 110)
    )
    rule = rotate(rect(16, 52, 68, 4), -30, 50, 54)
    return union(body, shackle, rete, pointers, rule, circle(50, 54, 4))


def solomonic_physic():
    """The physician's flask held up to the light."""
    flask = union(circle(50, 62, 26), rect(42, 18, 16, 30))
    hollow = union(circle(50, 62, 21), rect(46, 18, 8, 30))
    level = circle(50, 62, 21).intersected(rect(0, 64, 100, 40))
    lip = rrect(38, 12, 24, 8, 3)
    rays = union_of(
        bar(*_pt(50, 62, 32, a), *_pt(50, 62, 40, a), 3) for a in (-40, -10, 170, 200)
    )
    return union(flask.subtracted(hollow), level, lip, rays)


def solomonic_storytelling():
    """A book open under a crescent, as the tales were told by night."""
    left = poly((10, 44), (48, 52), (48, 92), (10, 84))
    right = poly((90, 44), (52, 52), (52, 92), (90, 84))
    lines = union_of(rect(x, y, 26, 2.6) for x in (16, 58) for y in (60, 68, 76))
    moon = circle(50, 24, 16).subtracted(circle(58, 18, 14))
    return union(union(left, right).subtracted(lines), moon, star(4, 5, 1.4, 70, 30))


def solomonic_travel():
    """A carpet flying, its fringes trailing, under the stars."""
    pts = [
        (14 + 72 * t, 60 + 7 * math.sin(t * math.pi * 2))
        for t in [i / 30 for i in range(31)]
    ]
    top = [(x, y - 14) for x, y in pts]
    rug = poly(*top, *reversed(pts))
    border = poly(
        *[(x, y - 10) for x, y in pts[3:-3]],
        *reversed([(x, y - 4) for x, y in pts[3:-3]]),
    )
    fringe = union_of(bar(x, y, x - 2, y + 7, 1.8) for x, y in pts[::3])
    stars = union(
        star(4, 7, 1.8, 28, 22), star(4, 5, 1.4, 70, 18), star(4, 5, 1.4, 52, 30)
    )
    return union(rug.subtracted(border), fringe, stars)


def soban_alchemy():
    """The Sovereign Reagent in its crowned phial."""
    phial = union(ellipse(32, 44, 36, 46), rect(44, 26, 12, 22))
    hollow = union(ellipse(37, 49, 26, 36), rect(47, 26, 6, 24))
    fill = ellipse(37, 49, 26, 36).intersected(rect(0, 68, 100, 30))
    crown = poly((36, 26), (34, 10), (42, 18), (50, 6), (58, 18), (66, 10), (64, 26))
    return union(phial.subtracted(hollow), fill, crown)


def _tcherot(sign: QPainterPath):
    """A Tuareg leather amulet: a square pouch under a triangle, its face
    worked with a sign."""
    pouch = rrect(26, 40, 48, 44, 3)
    flap = poly((26, 40), (74, 40), (50, 14))
    fringe = union_of(rect(30 + 8 * i, 84, 3, 10) for i in range(6))
    cord = stroke(curve((50, 14), (50, 6), (50, 2)), 3)
    face = rrect(31, 45, 38, 34, 2)
    return union(flap, fringe, cord, pouch.subtracted(face), sign.intersected(face))


def disjunction():
    """A settut amulet, its sign a ring split apart."""
    return _tcherot(
        union(
            ring(46, 62, 10, 3.4)
            .subtracted(rect(48, 0, 4, 100))
            .intersected(rect(0, 0, 49, 100)),
            ring(54, 62, 10, 3.4).intersected(rect(51, 0, 50, 100)),
        )
    )


def dislocation():
    """A settut amulet, its sign a road folded short."""
    return _tcherot(stroke(_open((36, 74), (64, 66), (36, 58), (64, 50)), 3.6))


def dismay():
    """A settut amulet, its sign a stalk wilting."""
    return _tcherot(
        union(
            stroke(curve((50, 76), (52, 54), (62, 52)), 3.4),
            rotate(vesica(62, 60, 14, 6), 80, 62, 60),
        )
    )


def dismissal():
    """A settut amulet, its sign arrows driving outward."""
    arrows = union_of(
        rotate(
            union(rect(48.5, 52, 3, 10), poly((45, 54), (55, 54), (50, 47))), a, 50, 62
        )
        for a in (0, 90, 180, 270)
    )
    return _tcherot(union(arrows, circle(50, 62, 3)))


def dissidence():
    """A settut amulet, its sign two arrows turned against each other."""
    a = union(bar(36, 70, 56, 54, 3), poly((52, 50), (60, 50), (60, 58)))
    b = union(bar(64, 70, 44, 54, 3), poly((48, 50), (40, 50), (40, 58)))
    return _tcherot(union(a, b))


def dissolution():
    """A settut amulet, its sign a block crumbling."""
    block = rect(38, 50, 16, 16)
    crumbs = union(
        rect(57, 58, 6, 6), rect(58, 68, 4, 4), rect(46, 70, 5, 5), rect(64, 72, 3, 3)
    )
    return _tcherot(union(block, crumbs))


def settut_divination():
    """The seeress's cowries, cast and fallen."""

    def cowrie(x: float, y: float, r: float):
        shell = rotate(vesica(x, y, 34, 22), r, x, y)
        slit = rotate(rect(x - 12, y - 1.2, 24, 2.4), r, x, y)
        teeth = union_of(
            rotate(rect(x - 10 + 4 * i, y - 3.6, 1.8, 7.2), r, x, y) for i in range(6)
        )
        return shell.subtracted(union(slit, teeth))

    return union(cowrie(32, 30, 30), cowrie(68, 40, -20), cowrie(44, 72, 80))


def ecstatic_magic():
    """The dancers' ring at the akelarre, a spirit rising out of it."""
    dancers = union_of(circle(*_pt(50, 68, 30, a), 4.5) for a in range(0, 360, 30))
    ground = ring(50, 68, 30, 2).subtracted(
        union_of(circle(*_pt(50, 68, 30, a), 7) for a in range(0, 360, 30))
    )
    spirit = flame(50, 70, 20, 64)
    return union(dancers, ground, spirit)


def emotion_theft():
    """A heart taken from one and carried to another."""
    a = heart(26, 64, 0.5)
    b = heart(74, 64, 0.5)
    hollow = heart(26, 64, 0.32)
    arc = stroke(curve((30, 44), (50, 14), (70, 44)), 3.4)
    head = poly((64, 40), (76, 42), (70, 52))
    return union(a.subtracted(hollow), b, arc, head)


def hermetic_viresculture():
    """A vis plant in its pot, its buds opening as stars."""
    pot = poly((28, 66), (72, 66), (66, 94), (34, 94))
    rim = rrect(24, 62, 52, 8, 3)
    stems = union(
        stroke(curve((50, 62), (50, 40), (50, 20)), 3),
        stroke(curve((48, 62), (36, 46), (26, 34)), 3),
        stroke(curve((52, 62), (64, 46), (74, 34)), 3),
    )
    buds = union(
        star(5, 9, 3.6, 50, 16), star(5, 8, 3.2, 24, 30), star(5, 8, 3.2, 76, 30)
    )
    return union(pot, rim, stems, buds)


def _caduceus(cx: float, top: float, h: float):
    rod = rect(cx - 1.5, top, 3, h)
    pts1 = [
        (cx + 7 * math.sin(i * 0.45), top + 6 + i * (h - 10) / 30) for i in range(31)
    ]
    pts2 = [
        (cx - 7 * math.sin(i * 0.45), top + 6 + i * (h - 10) / 30) for i in range(31)
    ]
    snakes = weave([_open(*pts1), _open(*pts2)], 2.4, 1.2)
    wings = union(
        rotate(vesica(cx - 8, top + 2, 14, 5), -20, cx - 8, top + 2),
        rotate(vesica(cx + 8, top + 2, 14, 5), 20, cx + 8, top + 2),
    )
    return union(rod, snakes, wings)


def set_the_stones_of_the_via():
    """A Roman milestone, Mercury's staff cut in its face."""
    stone = union(
        rrect(28, 22, 44, 66, 4), rrect(22, 84, 56, 10, 2), ellipse(28, 14, 44, 16)
    )
    face = rrect(34, 30, 32, 50, 2)
    return union(stone.subtracted(face), _caduceus(50, 32, 46).intersected(face))


def link_the_rent_path():
    """A road broken across, joined again by a link of chain."""
    road = poly((40, 12), (60, 12), (90, 94), (10, 94))
    gap = rect(0, 46, 100, 12)
    dash = union_of(rect(48.5, y, 3, 6) for y in (20, 34, 66, 80))
    link = weave([circle_path(42, 52, 10), circle_path(58, 52, 10)], 4.4, 1.8)
    return union(road.subtracted(union(gap, dash)), link)


def geomancy():
    """A geomancer's sand tray, a figure of dots cast in it and the
    stylus that marked them."""
    tray = rrect(14, 18, 62, 70, 6).subtracted(rrect(20, 24, 50, 58, 3))
    figure = [(1, 2), (2, 2), (3, 1), (4, 1)]  # Fortuna Major, read top down
    dots = []
    for row, count in figure:
        y = 24 + row * 11.6
        xs = (45,) if count == 1 else (37, 53)
        dots += [circle(x, y, 4) for x in xs]
    stylus = rotate(union(rect(84, 10, 5, 66), poly((84, 76), (89, 76), (86.5, 86))), 0)
    return union(tray, union_of(dots), stylus)


# -- Rival Magic --


def alala():
    """A gate thrown open, light pouring through: the Vowel that opens."""
    left = poly((14, 20), (36, 28), (36, 88), (14, 94))
    right = poly((86, 20), (64, 28), (64, 88), (86, 94))
    studs = union_of(circle(x, y, 2.4) for x in (22, 78) for y in (40, 58, 76))
    light = union_of(
        poly((50, 30), (46, 92), (54, 92))
        if a == 0
        else rotate(poly((49, 30), (51, 30), (50, 92)), a, 50, 30)
        for a in (-14, 0, 14)
    )
    lintel = rect(10, 10, 80, 6)
    return union(union(left, right).subtracted(studs), light, lintel)


def maat():
    """The feather of Ma'at, by which all things are measured."""
    spine = stroke(curve((50, 94), (52, 50), (50, 8)), 3)
    vane = rotate(vesica(51, 46, 76, 34), 90, 51, 46)
    barbs = union_of(
        union(bar(51, y, 32, y - 10, 1.6), bar(51, y, 70, y - 10, 1.6))
        for y in range(22, 84, 9)
    )
    return union(vane.subtracted(barbs).subtracted(rect(49, 0, 4, 100)), spine)


def papaios():
    """A gate shut and barred: the Vowel that closes, ends and heals."""
    leaves = union(rect(16, 18, 33, 74), rect(51, 18, 33, 74))
    planks = union_of(rect(x, 22, 1.6, 66) for x in (27, 38, 62, 73))
    bar_ = rrect(8, 48, 84, 9, 2)
    brackets = union(rect(20, 44, 6, 17), rect(74, 44, 6, 17))
    lintel = rect(10, 10, 80, 6)
    return union(over(union(bar_, brackets), leaves.subtracted(planks), 2), lintel)


def api():
    """The sun over the earth: day and ground."""
    hill = circle(50, 120, 60).intersected(rect(0, 60, 100, 40))
    sun = circle(50, 44, 14)
    rays = union_of(
        bar(*_pt(50, 44, 18, a), *_pt(50, 44, 28, a), 3.4) for a in range(-180, 1, 30)
    )
    strata = union_of(stroke(curve((14, y), (50, y - 8), (86, y)), 2) for y in (80, 90))
    return union(hill.subtracted(strata), sun, rays)


def kardia():
    """A heart quartered for the four humours."""
    h = heart(50, 54, 1.05)
    cross = union(rect(48.5, 0, 3, 100), rect(0, 48.5, 100, 3))
    dots = union(
        circle(36, 38, 3.6),
        circle(64, 38, 3.6),
        circle(38, 62, 3.6),
        circle(62, 62, 3.6),
    )
    return h.subtracted(union(cross, dots))


def nux():
    """Night over the clouds: the crescent, the stars and the wind."""
    moon = circle(40, 34, 22).subtracted(circle(50, 28, 19))
    cloud = union(
        circle(36, 74, 12),
        circle(54, 68, 15),
        circle(70, 76, 11),
        rrect(24, 72, 56, 14, 7),
    )
    stars = union(
        star(4, 6, 1.6, 72, 22), star(4, 5, 1.4, 84, 40), star(4, 4, 1.2, 64, 44)
    )
    return union(moon, cloud, stars)


def soma():
    """A figure standing, arms open: the body of man."""
    head = circle(50, 18, 10)
    body = union(
        bar(50, 30, 50, 60, 12),
        bar(46, 34, 18, 52, 7),
        bar(54, 34, 82, 52, 7),
        bar(46, 58, 34, 92, 8),
        bar(54, 58, 66, 92, 8),
    )
    return union(head, body)


def zoi():
    """Breath rising in three curls: spirit."""
    curls = union_of(
        stroke(curve((x, 92), (x - 10, 70), (x, 54), (x + 12, 38), (x, 24)), 4)
        for x in (32, 50, 68)
    )
    tips = union(circle(32, 22, 5), circle(50, 22, 5), circle(68, 22, 5))
    return union(curls, tips)


def _pelta():
    """The Amazon's crescent shield: a half-moon with a peak between its
    two horns."""
    body = circle(50, 46, 40).intersected(rect(0, 26, 100, 74))
    bites = union(circle(30, 26, 18), circle(70, 26, 18))
    return (
        body.subtracted(bites).subtracted(ring(50, 60, 14, 3)).united(circle(50, 60, 4))
    )


def amazonian_chant():
    """A pelta, the song rising from it in waves."""
    shield = _scaled_pelta(0.8, 50, 66)
    waves = union_of(
        ring(50, 40, r, 3).intersected(poly((50, 40), (14, 0), (86, 0)))
        for r in (14, 24, 34)
    )
    return union(shield, waves)


def _scaled_pelta(k: float, cx: float, cy: float):
    return QTransform().translate(cx, cy).scale(k, k).translate(-50, -50).map(_pelta())


def amazonian_spellcraft():
    """A temple front: its pediment, columns and steps."""
    roof = poly((10, 34), (50, 10), (90, 34))
    tympanum = poly((22, 30), (50, 16), (78, 30))
    frieze = rect(14, 36, 72, 7)
    cols = union_of(rect(19 + 14.5 * i, 46, 6, 36) for i in range(5))
    steps = union(rect(12, 84, 76, 5), rect(8, 90, 84, 5))
    return union(roof.subtracted(tympanum), frieze, cols, steps, circle(50, 25, 3))


def amazonian_cult_lore():
    """A diadem crowned with the crescent of the huntress goddess."""
    band = (
        circle(50, 120, 74)
        .subtracted(circle(50, 120, 64))
        .intersected(rect(0, 0, 100, 100))
    )
    moon = circle(50, 34, 22).subtracted(circle(50, 22, 20))
    jewels = union(circle(30, 54, 4), circle(50, 48, 5), circle(70, 54, 4))
    return union(band.intersected(rect(10, 40, 80, 60)), moon, jewels)


def amazonia_lore():
    """An Amazon's pelta and her bow laid across it."""
    bow = union(
        stroke(curve((20, 14), (68, 30), (86, 80)), 4), bar(20, 14, 86, 80, 1.6)
    )
    return union(_scaled_pelta(0.9, 46, 56), bow)


def _wreath(sign: QPainterPath):
    """A laurel wreath round the school's sign, as a Roman watch-post's
    standard bore it."""
    leaves = []
    for side in (-1, 1):
        for i in range(7):
            a = 100 + i * 22
            x, y = _pt(50, 52, 38, a if side < 0 else 180 - a)
            leaves.append(
                rotate(vesica(x, y, 14, 6), (a + 90) if side < 0 else (90 - a), x, y)
            )
    ribbon = poly((44, 88), (56, 88), (60, 96), (50, 92), (40, 96))
    return union(union_of(leaves), ribbon, sign)


def school_of_boreas():
    """The north wind, its gusts blowing within the wreath."""
    gusts = union(
        stroke(curve((26, 40), (56, 34), (64, 42), (66, 50), (54, 50)), 4),
        stroke(curve((22, 54), (60, 54), (72, 62), (74, 70), (62, 70)), 4),
        stroke(curve((30, 66), (44, 66), (50, 72)), 3),
    )
    return _wreath(gusts)


def school_of_the_naiads():
    """A drop over the waves, within the wreath."""
    drop = union(circle(50, 44, 10), poly((41, 40), (50, 22), (59, 40)))
    waves = union_of(
        stroke(
            _open(*((30 + 2 * i, y + 3 * math.sin(i * 0.7)) for i in range(21))), 3.4
        )
        for y in (62, 72)
    )
    return _wreath(union(drop, waves))


def school_of_prometheus():
    """The fennel stalk in which Prometheus carried fire, within the
    wreath."""
    stalk = bar(36, 78, 56, 48, 6)
    knots = union(bar(38, 70, 44, 74, 1.8), bar(45, 60, 51, 64, 1.8))
    fire = rotate(flame(57, 50, 28, 36), 30, 57, 50)
    return _wreath(union(stalk.subtracted(knots), fire))


def school_of_the_stones():
    """An arch and its keystone, within the wreath."""
    arch = ring(50, 62, 22, 9).intersected(rect(0, 30, 100, 32))
    key = poly((44, 30), (56, 30), (54, 42), (46, 42))
    piers = union(rect(28, 62, 9, 18), rect(63, 62, 9, 18))
    joints = union_of(
        rotate(rect(49.4, 30, 1.2, 14), a, 50, 62) for a in (-60, -30, 30, 60)
    )
    return _wreath(
        union(
            arch.subtracted(joints).subtracted(key.translated(0, 0)).united(key), piers
        )
    )


def school_of_the_sylvan_dryads():
    """An oak leaf and its acorn, within the wreath."""
    leaf = union(
        rotate(vesica(48, 46, 44, 20), 90, 48, 46),
        *(circle(48 + s * 9, 34 + 10 * i, 5) for s in (-1, 1) for i in range(3)),
    )
    vein = rect(47, 26, 2, 40)
    acorn = union(
        ellipse(58, 60, 12, 16), circle(64, 60, 6.5).intersected(rect(0, 50, 100, 10))
    )
    return _wreath(union(leaf.subtracted(vein), acorn))


def school_of_the_vigilant_bees():
    """A bee, within the wreath."""
    body = ellipse(42, 36, 16, 40)
    stripes = union_of(rect(40, 50 + 7 * i, 20, 2.6) for i in range(3))
    head = circle(50, 32, 7)
    wings = union(
        rotate(vesica(36, 46, 22, 10), -30, 36, 46),
        rotate(vesica(64, 46, 22, 10), 30, 64, 46),
    )
    return _wreath(union(body.subtracted(stripes), head, wings))


def animo():
    """A bronze bird on its stand, the key that wakes it in its back."""
    body = union(ellipse(28, 34, 44, 26), poly((70, 44), (86, 34), (84, 46)))
    head = circle(32, 34, 11)
    beak = poly((22, 32), (8, 36), (22, 40))
    wing = vesica(52, 40, 30, 12)
    eye = circle(30, 31, 2.4)
    stand = union(rect(46, 60, 6, 22), rrect(34, 82, 30, 6, 2))
    key = union(rect(56, 16, 3, 18), ring(57.5, 12, 5, 2.6))
    return union(
        union(body, head, beak).subtracted(
            union(eye, wing.subtracted(vesica(52, 40, 24, 6)))
        ),
        stand,
        key,
    )


def virgilian_theory():
    """Virgil's egg in its iron cage, on which Naples was made to stand."""
    egg = ellipse(38, 40, 24, 32)
    bars = union_of(rect(26 + 12 * i, 30, 3, 56) for i in range(5)).subtracted(
        ellipse(36, 38, 28, 36)
    )
    hoops = union(rect(22, 28, 56, 4), rect(22, 84, 56, 4))
    dome = ring(50, 30, 28, 4).intersected(rect(0, 0, 100, 30))
    chain = union(ring(50, 6, 3, 1.6), rect(49, 0, 2, 3))
    return union(egg, bars, hoops, dome, rect(48, 0, 4, 4), chain)


def virgilian_rite():
    """Virgil's bronze fly, that drove the flies from Naples."""
    body = ellipse(44, 34, 12, 44)
    stripes = union_of(rect(44, 50 + 7 * i, 12, 2.4) for i in range(3))
    head = circle(50, 30, 8)
    eyes = union(circle(45, 27, 3.6), circle(55, 27, 3.6))
    wings = union(
        rotate(vesica(30, 50, 34, 14), -20, 30, 50),
        rotate(vesica(70, 50, 34, 14), 20, 70, 50),
    )
    veins = union(
        rotate(rect(16, 49, 28, 1.4), -20, 30, 50),
        rotate(rect(56, 49, 28, 1.4), 20, 70, 50),
    )
    legs = union(
        bar(46, 46, 30, 30, 2),
        bar(54, 46, 70, 30, 2),
        bar(46, 60, 30, 78, 2),
        bar(54, 60, 70, 78, 2),
    )
    return union(
        legs,
        wings.subtracted(veins),
        body.subtracted(stripes),
        head.subtracted(eyes),
        eyes,
    )


def sjonhverfing():
    """An eye, a veil falling over it: the sight deceived."""
    eye = vesica(50, 60, 70, 34).subtracted(vesica(50, 60, 56, 22))
    iris = circle(50, 60, 9).subtracted(circle(50, 60, 3.4))
    veil = poly(
        (8, 14),
        (92, 14),
        (92, 40),
        (78, 50),
        (64, 42),
        (50, 50),
        (36, 42),
        (22, 50),
        (8, 40),
    )
    return union(eye.united(iris).subtracted(veil.translated(0, 2)), veil)


def spadomur():
    """A bowl of still water, an eye seen in its surface."""
    bowl = circle(50, 50, 38).intersected(rect(0, 56, 100, 44))
    surface = ellipse(14, 48, 72, 16).subtracted(ellipse(18, 51, 64, 10))
    seen = (
        vesica(50, 34, 40, 18)
        .subtracted(vesica(50, 34, 30, 10))
        .united(circle(50, 34, 4))
    )
    return union(bowl.subtracted(ellipse(14, 48, 72, 16)), surface, seen)


def storms_eye():
    """A storm turning about its still eye."""
    arms = union_of(
        rotate(stroke(curve((50, 50), (80, 46), (84, 16)), 8), a, 50, 50)
        for a in (0, 90, 180, 270)
    )
    return union(
        arms.subtracted(circle(50, 50, 13)), ring(50, 50, 10, 3.4), circle(50, 50, 3.4)
    )


def threads_of_fate():
    """A spindle, three threads twisted from it."""
    spindle = union(bar(50, 40, 50, 94, 4), ellipse(36, 74, 28, 10))
    threads = weave(
        [
            _open(*((50 + 14 * math.sin(i * 0.3 + p), 40 - i * 1.0) for i in range(36)))
            for p in (0, 2.1, 4.2)
        ],
        2.6,
        1.2,
    )
    return union(spindle, threads)


def valgaldrar():
    """The gallows, from which Odin learned the speech of the dead."""
    post = rect(24, 12, 8, 80)
    beam = rect(20, 12, 62, 8)
    brace = bar(28, 40, 52, 16, 5)
    rope = rect(70, 20, 3, 26)
    noose = ring(71.5, 54, 8, 3)
    ground = rrect(12, 88, 34, 6, 2)
    return union(post, beam, brace, rope, noose, ground)


def wildfire():
    """Fire running along the ground, catching as it goes."""
    return union(
        flame(24, 88, 18, 30),
        flame(48, 88, 24, 48),
        flame(74, 88, 28, 70),
        rect(10, 88, 80, 4),
    )


def winters_breath():
    """A frame drum, a snowflake on its skin."""
    drum = ring(50, 50, 38, 6)
    flake = union_of(
        rotate(
            union(
                rect(48.5, 22, 3, 28),
                bar(50, 30, 43, 24, 2.4),
                bar(50, 30, 57, 24, 2.4),
            ),
            a,
        )
        for a in range(0, 360, 60)
    )
    return union(drum, flake)


def aloe_magic():
    """An aloe, its thick spined leaves rising in a rosette."""
    leaves = union_of(
        rotate(rotate(vesica(50, 50, 70, 13), 90, 50, 50), a, 50, 86)
        for a in (-50, -25, 0, 25, 50)
    )
    spines = union_of(
        rotate(rect(46, 30 + 10 * i, 2, 2), a, 50, 86)
        for a in (-50, -25, 25, 50)
        for i in range(3)
    )
    return union(leaves.subtracted(spines), rrect(30, 84, 40, 8, 3))


def cinnabar_magic():
    """A cluster of cinnabar crystals."""

    def crystal(x: float, y: float, w: float, h: float, a: float):
        return rotate(
            poly(
                (x - w / 2, y),
                (x - w / 2, y - h),
                (x, y - h - w / 2),
                (x + w / 2, y - h),
                (x + w / 2, y),
            ),
            a,
            x,
            y,
        )

    facets = union(
        crystal(50, 86, 16, 56, 0),
        crystal(36, 86, 13, 38, -25),
        crystal(66, 86, 13, 42, 22),
        crystal(24, 88, 10, 22, -45),
        crystal(78, 88, 10, 24, 45),
    )
    edge = rect(49.4, 30, 1.2, 56)
    return union(facets.subtracted(edge), rrect(16, 84, 68, 8, 3))


def myrrh_magic():
    """A myrrh twig, its resin weeping in tears."""
    twig = union(
        stroke(curve((14, 82), (44, 52), (86, 20)), 4.5),
        stroke(curve((44, 52), (56, 56), (66, 66)), 3),
    )
    thorns = union_of(
        bar(x, y, x + 6, y - 6, 2) for x, y in ((28, 68), (60, 38), (72, 30))
    )
    tears = union(
        *(
            union(
                circle(x, y, 5), poly((x - 4.4, y - 2), (x, y - 12), (x + 4.4, y - 2))
            )
            for x, y in ((36, 76), (70, 80), (54, 30))
        )
    )
    return union(twig, thorns, tears)


def olibanum_magic():
    """The winged serpent that guards the frankincense tree, its smoke
    rising."""
    trunk = union(rect(46, 40, 8, 50), bar(50, 52, 30, 34, 4), bar(50, 48, 70, 30, 4))
    pts = [(50 + 14 * math.sin(i * 0.55), 88 - i * 1.6) for i in range(34)]
    serpent = stroke(_open(*pts), 4.4)
    head = circle(*pts[-1], 5)
    smoke = union(
        stroke(curve((30, 30), (24, 20), (30, 8)), 2.6),
        stroke(curve((70, 26), (76, 16), (70, 6)), 2.6),
    )
    return union(over(union(serpent, head), trunk, 2), smoke)


def sortes_virgilianae():
    """Virgil opened at random, a pin pricking the line that answers and a
    laurel sprig laid in the gutter."""
    left = poly((10, 30), (48, 36), (48, 88), (10, 82))
    right = poly((90, 30), (52, 36), (52, 88), (90, 82))
    text = union_of(rect(x, y, 30, 2.6) for x in (14, 56) for y in (46, 54, 62, 70, 78))
    pages = union(left, right).subtracted(text)
    pin = union(bar(82, 10, 68, 63, 2.6), circle(83, 8, 5))
    sprig = stroke(curve((50, 34), (49, 22), (44, 10)), 2.4)
    leaves = union(
        *(
            rotate(vesica(x, y, 12, 5), r, x, y)
            for x, y, r in (
                (43, 26, -50),
                (57, 22, -130),
                (40, 15, -60),
                (53, 12, -120),
            )
        )
    )
    return union(over(pin, pages), sprig, leaves)


# -- Ancient Magic, and the Hunters' Arts from Against the Dark --


def canaanite_necromancy():
    """A pinched saucer lamp burning before the door of a rock tomb."""
    rock = rrect(22, 8, 56, 46, 6)
    door = union(rect(40, 24, 20, 30), circle(50, 24, 10))
    lamp = union(ellipse(10, 66, 60, 22), poly((62, 70), (88, 76), (62, 84)))
    well = ellipse(18, 70, 42, 10)
    fire = flame(84, 74, 12, 26)
    return union(rock.subtracted(door), lamp.subtracted(well), fire)


def defixio_lore():
    """A lead tablet rolled up and nailed through."""
    roll = rrect(14, 38, 72, 26, 6)
    edge = ellipse(78, 38, 12, 26).subtracted(ellipse(81, 44, 6, 14))
    lines = union_of(rect(20, y, 52, 2) for y in (44, 50, 56))
    nail = union(
        rect(47, 10, 6, 76), poly((47, 86), (53, 86), (50, 94)), rrect(40, 8, 20, 6, 2)
    )
    return over(nail, union(roll.subtracted(lines), edge), 2)


def _hymn(sign: QPainterPath):
    """A ring of the seven vowels round the hymn's sign."""
    vowels = union_of(
        circle(*_pt(50, 50, 40, -90 + i * 360 / 7), 4.2) for i in range(7)
    )
    return union(ring(50, 50, 34, 3), vowels, sign)


def hymn_azai():
    """Beautiful Light: the sun in the ring of the seven vowels."""
    sun = union(
        circle(50, 50, 10),
        union_of(
            poly(_pt(50, 50, 12, a - 10), _pt(50, 50, 12, a + 10), _pt(50, 50, 24, a))
            for a in range(0, 360, 30)
        ),
    )
    return _hymn(sun)


def hymn_eloure():
    """Fire Delighter: the moon over the waters, in the ring of the
    seven vowels."""
    moon = circle(46, 40, 12).subtracted(circle(52, 36, 10))
    waves = union_of(
        stroke(
            _open(*((30 + 2 * i, y + 2.6 * math.sin(i * 0.8)) for i in range(21))), 3
        )
        for y in (60, 69)
    )
    return _hymn(union(moon, waves))


def hymn_iao():
    """Fire Feeler: the winds and sweet airs, in the ring of the seven
    vowels."""
    curls = union(
        stroke(curve((26, 44), (58, 38), (64, 46), (66, 54), (54, 54)), 3.4),
        stroke(curve((30, 60), (62, 58), (70, 66)), 3),
    )
    return _hymn(curls)


def hymn_oai():
    """Light Breather: a tongue of flame, for quick thought and eloquence,
    in the ring of the seven vowels."""
    return _hymn(union(flame(50, 72, 22, 42), rect(42, 72, 16, 3)))


def hymn_pentiterouni():
    """Firewalker: the mountain, in the ring of the seven vowels."""
    hill = poly((22, 70), (42, 34), (52, 48), (60, 40), (78, 70))
    snow = poly((42, 34), (36, 46), (42, 44), (46, 48), (48, 42))
    return _hymn(hill.subtracted(snow))


def hymn_psyrinpheu():
    """Fire Breather: the spear of war, in the ring of the seven vowels."""
    spear = union(
        rect(48, 38, 4, 40), poly((44, 40), (50, 18), (56, 40)), rect(43, 40, 14, 3)
    )
    return _hymn(union(spear, flame(36, 60, 12, 22), flame(64, 60, 12, 22)))


def hymn_semesilam():
    """Encloser, Lightmaker: Apollo's lyre, in the ring of the seven
    vowels."""
    arms = union(
        stroke(curve((40, 70), (22, 50), (32, 24)), 4.4),
        stroke(curve((60, 70), (78, 50), (68, 24)), 4.4),
    )
    yoke = rect(28, 30, 44, 4)
    sound = ellipse(36, 62, 28, 14)
    strings = union_of(rect(x, 34, 1.4, 30) for x in (43, 48, 53, 58))
    return _hymn(union(arms, yoke, sound, strings))


def fertility_lore():
    """An ear of barley crossed with a poppy head."""
    ear = union_of(
        rotate(
            vesica(38 + s * 5, 22 + 9 * i, 12, 6), s * 30 + 90, 38 + s * 5, 22 + 9 * i
        )
        for i in range(5)
        for s in (-1, 1)
    )
    stalk = bar(38, 20, 54, 94, 3)
    awns = union_of(
        bar(38 + s * 5, 18 + 9 * i, 38 + s * 12, 8 + 9 * i, 1.2)
        for i in range(2)
        for s in (-1, 1)
    )
    poppy = union(ellipse(58, 22, 22, 22), rect(62, 16, 14, 6), bar(69, 44, 56, 94, 3))
    crown = union_of(rect(61 + 4 * i, 14, 2, 6) for i in range(4))
    return union(ear, stalk, awns, poppy.subtracted(crown).united(rect(61, 18, 16, 3)))


def scry():
    """An arrow with an eye at its notch, that finds its quarry."""
    shaft = bar(20, 80, 76, 24, 3.4)
    head = poly((84, 16), (70, 24), (76, 30))
    fletch = union(
        poly((20, 80), (14, 72), (22, 66), (30, 70)),
        poly((20, 80), (28, 86), (34, 78), (30, 70)),
    )
    eye = (
        vesica(32, 34, 34, 18)
        .subtracted(vesica(32, 34, 26, 10))
        .united(circle(32, 34, 4.4))
    )
    return union(shaft, head, fletch, eye)


def ban():
    """A ring of hawthorn stakes driven round the quarry."""
    stakes = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        x, y = 50 + 34 * math.cos(a), 62 + 16 * math.sin(a)
        h = 30
        stakes.append(
            (
                y,
                poly(
                    (x - 4, y),
                    (x - 4, y - h),
                    (x, y - h - 7),
                    (x + 4, y - h),
                    (x + 4, y),
                ),
            )
        )
    ring_ = ellipse(14, 46, 72, 32).subtracted(ellipse(20, 50, 60, 24))
    shape = ring_
    for _, s in sorted(stakes, key=lambda t: t[0]):
        shape = over(s, shape, 1.4)
    return union(shape, circle(50, 62, 4))


def slay():
    """A hunting knife, its blade fresh charged."""
    blade = poly((24, 76), (70, 20), (80, 14), (76, 26), (32, 84))
    fuller = bar(32, 72, 70, 26, 1.8)
    guard = bar(16, 70, 34, 88, 6)
    grip = bar(22, 82, 10, 94, 7)
    return union(blade.subtracted(fuller), guard, grip)


def foe():
    """The quarry marked: a target's rings, an arrow in its heart."""
    target = union(ring(44, 56, 34, 5), ring(44, 56, 20, 5), circle(44, 56, 7))
    arrow = union(
        bar(44, 56, 88, 12, 3),
        poly((82, 8), (92, 6), (90, 16)),
        bar(86, 12, 80, 4, 2),
        bar(88, 14, 96, 20, 2),
    )
    return over(arrow, target, 2)


def divination():
    """The diviner's eye, open in the ring of the heavens, the seven
    planets about it."""
    sky = ring(50, 50, 40, 3.5)
    eye = (
        vesica(50, 50, 44, 24)
        .subtracted(vesica(50, 50, 36, 16))
        .united(circle(50, 50, 6))
    )
    planets = union_of(
        star(5, 5, 2, *_pt(50, 50, 40, -90 + i * 360 / 7)) for i in range(7)
    )
    gaps = union_of(circle(*_pt(50, 50, 40, -90 + i * 360 / 7), 7) for i in range(7))
    return union(sky.subtracted(gaps), eye, planets)


#: Each Ability's charge, by its name.
BOOK_MARKS: dict[str, Callable[[], QPainterPath]] = {
    "Enchantment": enchantment,
    "Empathy": empathy,
    "Beguile": beguile,
    "Conjure": conjure,
    "Dream": dream,
    "Grant": grant,
    "Portage": portage,
    "Ware": ware,
    "Weal": weal,
    "Woe": woe,
    "(Faerie) Summoning": faerie_summoning,
    "Bonding": bonding,
    "Captivating": captivating,
    "Dismissing": dismissing,
    "Evocation": evocation,
    "Ceremony": ceremony,
    "Invocation": invocation,
    "Meditation": meditation,
    "Purity": purity,
    "Intervention": intervention,
    "Transcendence": transcendence,
    "Understanding": understanding,
    "Wonders": wonders,
    "Craft Amulets": craft_amulets,
    "Dream Interpretation": dream_interpretation,
    "Holy Magic": holy_magic,
    "Ars Notoria": ars_notoria,
    "Saint's Aid": saints_aid,
    "Banishing": banishing,
    "Gematria": gematria,
    "Debauchery": debauchery,
    "Incantation": incantation,
    "Consumption": consumption,
    "Effusion": effusion,
    "Malediction": malediction,
    "Phantasm": phantasm,
    "Psychomachia": psychomachia,
    "Summoning": summoning,
    "Ablating": ablating,
    "Binding": binding,
    "Commanding": commanding,
    "Corruption": corruption,
    "Chthonic Magic": chthonic_magic,
    "Diablerie": diablerie,
    "Control Fertility": control_fertility,
    "Warding": warding,
    "Comprehend Magic": comprehend_magic,
    "Sihr": sihr,
    "Solomonic Alchemy": solomonic_alchemy,
    "Solomonic Astrology": solomonic_astrology,
    "Solomonic Physic": solomonic_physic,
    "Solomonic Storytelling": solomonic_storytelling,
    "Solomonic Travel": solomonic_travel,
    "Soban Alchemy": soban_alchemy,
    "Disjunction": disjunction,
    "Dislocation": dislocation,
    "Dismay": dismay,
    "Dismissal": dismissal,
    "Dissidence": dissidence,
    "Dissolution": dissolution,
    "Settut Divination": settut_divination,
    "Ecstatic Magic": ecstatic_magic,
    "Emotion Theft": emotion_theft,
    "Hermetic Viresculture": hermetic_viresculture,
    "Set the Stones of the Via": set_the_stones_of_the_via,
    "Link the Rent Path": link_the_rent_path,
    "Geomancy": geomancy,
    "Alala": alala,
    "Ma'at": maat,
    "Papaios": papaios,
    "Api": api,
    "Kardia": kardia,
    "Nux": nux,
    "Soma": soma,
    "Zoi": zoi,
    "Amazonian Chant": amazonian_chant,
    "Amazonian Spellcraft": amazonian_spellcraft,
    "Amazonian Cult Lore": amazonian_cult_lore,
    "Amazonia Lore": amazonia_lore,
    "School of Boreas": school_of_boreas,
    "School of the Naiads": school_of_the_naiads,
    "School of Prometheus": school_of_prometheus,
    "School of the Stones": school_of_the_stones,
    "School of the Sylvan Dryads": school_of_the_sylvan_dryads,
    "School of the Vigilant Bees": school_of_the_vigilant_bees,
    "Animo": animo,
    "Virgilian Theory": virgilian_theory,
    "Virgilian Rite": virgilian_rite,
    "Sjonhverfing": sjonhverfing,
    "Spadomur": spadomur,
    "Storm's Eye": storms_eye,
    "Threads of Fate": threads_of_fate,
    "Valgaldrar": valgaldrar,
    "Wildfire": wildfire,
    "Winter's Breath": winters_breath,
    "Aloe Magic": aloe_magic,
    "Cinnabar Magic": cinnabar_magic,
    "Myrrh Magic": myrrh_magic,
    "Olibanum Magic": olibanum_magic,
    "Sortes Virgilianae": sortes_virgilianae,
    "Canaanite Necromancy": canaanite_necromancy,
    "Defixio Lore": defixio_lore,
    "Hymn Azai": hymn_azai,
    "Hymn Eloure": hymn_eloure,
    "Hymn Iaó": hymn_iao,
    "Hymn Óai": hymn_oai,
    "Hymn Pentiterouni": hymn_pentiterouni,
    "Hymn Psyrinpheu": hymn_psyrinpheu,
    "Hymn Semesilam": hymn_semesilam,
    "Fertility Lore": fertility_lore,
    "Scry": scry,
    "Ban": ban,
    "Slay": slay,
    "Foe": foe,
    # Divination & Augury (The Mysteries Revised Edition).
    "Divination": divination,
}
