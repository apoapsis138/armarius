"""The charge cut out of each ability's mark, and one for each category (for
an ability without its own).

Each charge is drawn in the 100 x 100 box of mark_shapes; marks.py scales
every one to the same size, so a charge only needs the right proportions.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from PySide6.QtGui import QPainterPath, QTransform

from .. import artwork
from .mark_shapes import (
    bar,
    book_closed,
    circle,
    curve,
    ellipse,
    eye,
    flame,
    heart,
    line,
    mirror,
    move,
    outline_triangle,
    poly,
    rect,
    ring,
    rotate,
    rrect,
    scaled,
    star,
    stroke,
    union,
    union_of,
    vesica,
)

# -- General --


def animal_handling() -> QPainterPath:
    """A shepherd's crook: one staff curling over into its hook."""
    path = QPainterPath()
    path.moveTo(56, 90)
    path.lineTo(56, 34)
    path.cubicTo(56, 14, 30, 12, 28, 30)
    path.quadTo(27, 40, 34, 44)
    return stroke(path, 7)


def area_lore() -> QPainterPath:
    """A compass rose."""
    return union(star(4, 34, 8), ring(50, 50, 20, 4)).subtracted(circle(50, 50, 4))


def athletics() -> QPainterPath:
    """Two chevrons running forward."""
    chevron = poly((24, 30), (40, 50), (24, 70), (34, 70), (50, 50), (34, 30))
    return union(chevron, move(chevron, 22, 0))


def awareness() -> QPainterPath:
    return eye()


def bargain() -> QPainterPath:
    """A merchant's balance."""
    beam = bar(18, 30, 82, 30, 4)
    post = union(
        rect(48, 22, 4, 56), poly((36, 86), (50, 76), (64, 86)), circle(50, 22, 4)
    )

    def pan(x: float) -> QPainterPath:
        return union(
            bar(x, 30, x - 10, 56, 1.8),
            bar(x, 30, x + 10, 56, 1.8),
            circle(x, 56, 13).intersected(rect(x - 14, 56, 28, 14)),
        )

    return union(beam, post, pan(24), pan(76))


def carouse() -> QPainterPath:
    """A footed goblet."""
    bowl = (
        circle(50, 24, 26).intersected(rect(24, 24, 52, 28)).united(rect(24, 20, 52, 6))
    )
    return union(
        bowl, rect(46, 50, 8, 24), poly((32, 84), (40, 74), (60, 74), (68, 84))
    )


def charm() -> QPainterPath:
    """A five-petalled rose."""
    petals = union_of(
        circle(
            50 + 15 * math.cos(math.radians(a)), 50 + 15 * math.sin(math.radians(a)), 11
        )
        for a in range(-90, 270, 72)
    )
    return petals.subtracted(circle(50, 50, 7)).united(circle(50, 50, 4))


def chirurgy() -> QPainterPath:
    """A surgeon's bow saw: an arched frame, a toothed blade, a handle."""
    frame = stroke(curve((22, 62), (50, 4), (78, 62)), 6)
    blade = rect(20, 60, 60, 7)
    teeth = union_of(
        poly((22 + 6 * i, 67), (28 + 6 * i, 67), (25 + 6 * i, 73)) for i in range(10)
    )
    handle = union(
        rrect(76, 54, 18, 10, 4), rotate(rrect(80, 56, 8, 26, 4), -20, 84, 60)
    )
    return union(frame, blade, teeth, handle)


def craft() -> QPainterPath:
    """A hammer."""
    return union(rect(26, 24, 48, 16), rect(45, 40, 10, 38))


def etiquette() -> QPainterPath:
    """A fleur-de-lis, the courtly flower."""
    petal = QPainterPath()
    petal.moveTo(50, 12)
    petal.cubicTo(62, 26, 60, 44, 50, 56)
    petal.cubicTo(40, 44, 38, 26, 50, 12)
    petal.closeSubpath()
    side = QPainterPath()
    side.moveTo(46, 56)
    side.cubicTo(36, 40, 20, 38, 16, 50)
    side.cubicTo(14, 58, 22, 62, 26, 56)
    side.cubicTo(30, 50, 36, 54, 40, 60)
    side.closeSubpath()
    band = rrect(30, 58, 40, 7, 3)
    foot = poly((50, 64), (40, 84), (50, 78), (60, 84))
    return union(petal, side, mirror(side), band, foot)


def folk_ken() -> QPainterPath:
    """A village cottage."""
    house = union(
        poly((18, 46), (50, 18), (82, 46)), rect(24, 44, 52, 40), rect(64, 22, 8, 16)
    )
    return house.subtracted(rrect(43, 60, 14, 24, 6)).subtracted(rect(30, 54, 8, 8))


def guile() -> QPainterPath:
    """A masquer's half-mask."""
    mask = QPainterPath()
    mask.moveTo(14, 42)
    mask.cubicTo(30, 30, 44, 36, 50, 42)
    mask.cubicTo(56, 36, 70, 30, 86, 42)
    mask.cubicTo(84, 58, 70, 66, 58, 60)
    mask.quadTo(50, 54, 42, 60)
    mask.cubicTo(30, 66, 16, 58, 14, 42)
    mask.closeSubpath()
    holes = union(vesica(32, 47, 16, 7), vesica(68, 47, 16, 7))
    ribbon = union(bar(14, 42, 8, 62, 3), bar(86, 42, 92, 62, 3))
    return union(mask.subtracted(holes), ribbon)


def hunt() -> QPainterPath:
    """A hunting horn, mouthpiece to flared bell, on its baldric."""
    upper, lower = [], []
    steps = 40
    for i in range(steps + 1):
        t = math.radians(170 - 160 * i / steps)
        x, y = 50 + 32 * math.cos(t), 30 + 32 * math.sin(t)
        nx, ny = math.cos(t), math.sin(t)
        w = 2.5 + 9 * (i / steps) ** 1.6
        upper.append((x - nx * w, y - ny * w))
        lower.append((x + nx * w, y + ny * w))
    tube = poly(*upper, *reversed(lower))
    bell = rotate(rrect(76, 22, 8, 30, 3), 10, 80, 37)
    mouth = rrect(13, 30, 8, 6, 2)
    strap = stroke(curve((22, 36), (50, 4), (78, 36)), 2.4)
    return union(tube, bell, mouth, strap)


def intrigue() -> QPainterPath:
    """A spider's web."""
    web = QPainterPath()
    for i in range(8):
        a = math.radians(i * 45)
        web = web.united(bar(50, 50, 50 + 36 * math.cos(a), 50 + 36 * math.sin(a), 2.6))
    for r in (12, 22, 32):
        points = [
            (
                50 + r * math.cos(math.radians(i * 45)),
                50 + r * math.sin(math.radians(i * 45)),
            )
            for i in range(9)
        ]
        web = web.united(line(*points, w=2.4))
    return web.united(circle(50, 50, 4))


def judaic_lore() -> QPainterPath:
    """A seven-branched menorah."""
    xs = (20, 30, 40, 50, 60, 70, 80)
    branches = union_of(
        ring(50, 46, r, 4.5).intersected(rect(0, 46, 100, 60)) for r in (10, 20, 30)
    )
    candles = union_of(rect(x - 2.5, 22, 5, 26) for x in xs)
    flames = union_of(move(flame(0, 0, 6, 10), x, 20) for x in xs)
    return union(
        branches.intersected(rect(0, 46, 100, 32)),
        candles,
        flames,
        rect(47.5, 46, 5, 30),
        poly((34, 88), (42, 78), (58, 78), (66, 88)),
    )


def leadership() -> QPainterPath:
    """A crown."""
    crown = poly((22, 70), (22, 34), (36, 52), (50, 26), (64, 52), (78, 34), (78, 70))
    return crown.united(rect(22, 74, 56, 6))


def legerdemain() -> QPainterPath:
    """Cups and balls: the middle cup lifted from its ball."""

    def cup(x: float, y: float) -> QPainterPath:
        return union(
            poly((x - 12, y), (x + 12, y), (x + 8, y - 32), (x - 8, y - 32)),
            rrect(x - 14, y - 4, 28, 5, 2),
        )

    return union(
        cup(20, 84), cup(50, 62), cup(80, 84), circle(50, 78, 6), rect(4, 86, 92, 4)
    )


def living_language() -> QPainterPath:
    """A rolled letter tied with a ribbon: every Living Language."""
    body = rrect(18, 36, 64, 26, 4)
    roll = circle(20, 49, 13)
    tie = poly((52, 62), (46, 82), (52, 78), (56, 84), (58, 62))
    return (
        union(body, roll, tie)
        .subtracted(ring(20, 49, 7, 2.6))
        .subtracted(circle(20, 49, 2))
    )


def music() -> QPainterPath:
    """A lyre: two curving arms, a yoke, a sound box and its strings."""
    arm = stroke(curve((40, 74), (20, 50), (30, 30), (38, 18), (30, 12)), 7)
    box = QPainterPath()
    box.moveTo(32, 70)
    box.lineTo(68, 70)
    box.quadTo(70, 88, 50, 88)
    box.quadTo(30, 88, 32, 70)
    box.closeSubpath()
    yoke = bar(24, 26, 76, 26, 6)
    strings = union_of(bar(x, 26, x, 74, 1.8) for x in (42, 48, 54, 60))
    return union(arm, mirror(arm), box, yoke, strings)


def mystery_cult_lore() -> QPainterPath:
    """A keyhole escutcheon."""
    hole = union(circle(50, 40, 9), poly((45, 44), (55, 44), (60, 70), (40, 70)))
    return rrect(24, 14, 52, 72, 10).subtracted(hole)


def organization_lore() -> QPainterPath:
    """A banner on its staff."""
    staff = union(bar(26, 12, 26, 88, 5), circle(26, 12, 4.5))
    return union(staff, poly((28, 18), (80, 18), (70, 34), (80, 50), (28, 50)))


def profession() -> QPainterPath:
    """A coin purse."""
    bag = QPainterPath()
    bag.moveTo(40, 34)
    bag.cubicTo(18, 46, 16, 84, 50, 84)
    bag.cubicTo(84, 84, 82, 46, 60, 34)
    bag.closeSubpath()
    neck = union(poly((40, 34), (60, 34), (66, 22), (34, 22)), bar(34, 34, 66, 34, 4))
    return union(bag, neck).subtracted(ring(50, 62, 9, 3))


def ride() -> QPainterPath:
    """A horseshoe with its nail holes."""
    outer, inner = [], []
    for i in range(61):
        ang = math.radians(130 + i * 280 / 60)
        outer.append((50 + 30 * math.cos(ang), 48 - 30 * math.sin(ang)))
        inner.append((50 + 19 * math.cos(ang), 48 - 19 * math.sin(ang)))
    shoe = poly(*outer, *reversed(inner))
    holes = union_of(
        circle(
            50 + 24.5 * math.cos(math.radians(a)),
            48 - 24.5 * math.sin(math.radians(a)),
            2.2,
        )
        for a in (150, 115, 65, 30, -10, -170)
    )
    return shoe.subtracted(holes)


def stealth() -> QPainterPath:
    """A crescent moon."""
    return circle(48, 50, 28).subtracted(circle(60, 44, 24))


def survival() -> QPainterPath:
    """A campfire: a flame over two crossed logs."""
    logs = union(bar(20, 82, 80, 66, 9), bar(20, 66, 80, 82, 9))
    return union(flame(50, 68, 40, 54), logs)


def swim() -> QPainterPath:
    """Three waves."""

    def wave(y: float) -> QPainterPath:
        points = [
            (16 + 68 * i / 40, y + 6 * math.sin(i / 40 * 4 * math.pi))
            for i in range(41)
        ]
        return line(*points, w=7)

    return union(wave(30), wave(50), wave(70))


def teaching() -> QPainterPath:
    """A lectern with a large open book on its sloping desk."""
    left = QPainterPath()
    left.moveTo(48, 36)
    left.quadTo(34, 26, 16, 30)
    left.lineTo(20, 52)
    left.quadTo(36, 48, 48, 56)
    left.closeSubpath()
    book = left.united(mirror(left))
    desk = poly((22, 56), (78, 56), (74, 62), (26, 62))
    post = rect(45, 62, 10, 18)
    foot = poly((30, 88), (36, 80), (64, 80), (70, 88))
    return union(book, desk, post, foot)


# -- Academic --


def art_of_memory() -> QPainterPath:
    """A memory palace: an arcade of three arches."""
    front = rect(14, 30, 72, 54)
    arches = union_of(
        union(rect(x, 50, 16, 34), circle(x + 8, 50, 8)) for x in (20, 42, 64)
    )
    roof = poly((10, 32), (50, 12), (90, 32))
    return union(front, roof).subtracted(arches).subtracted(rect(10, 30, 80, 3))


def artes_liberales() -> QPainterPath:
    """A seven-pointed star, one point for each of the seven arts."""
    return star(7, 32, 14).subtracted(circle(50, 50, 6))


def civil_and_canon_law() -> QPainterPath:
    """A closed codex with a cross on its cover."""
    return book_closed(union(rect(46, 26, 8, 44), rect(36, 36, 28, 8)))


def common_law() -> QPainterPath:
    """A closed codex sealed with a crown."""
    return book_closed(
        poly((36, 58), (36, 38), (43, 48), (50, 34), (57, 48), (64, 38), (64, 58))
    )


def dead_language() -> QPainterPath:
    """A quill: every Dead Language."""
    feather = vesica(50, 50, 70, 22).subtracted(bar(18, 50, 82, 50, 2.5))
    return rotate(union(feather, bar(14, 50, 30, 50, 4)), -50)


def islamic_law() -> QPainterPath:
    """A closed codex with a crescent on its cover."""
    return book_closed(circle(48, 50, 14).subtracted(circle(54, 46, 12)))


def medicine() -> QPainterPath:
    """A mortar and pestle."""
    bowl = (
        circle(50, 52, 26)
        .intersected(rect(20, 52, 60, 30))
        .subtracted(circle(50, 52, 18).intersected(rect(30, 52, 40, 20)))
        .united(rect(24, 50, 52, 5))
    )
    return union(bowl, bar(46, 48, 72, 18, 7), rect(40, 78, 20, 5))


def philosophiae() -> QPainterPath:
    """An armillary sphere on its stand."""
    belt = ellipse(22, 34, 56, 16).subtracted(ellipse(25, 37, 50, 10))
    return union(
        ring(50, 42, 28, 4),
        rotate(belt, -25, 50, 42),
        rect(47, 16, 6, 54),
        circle(50, 42, 5),
        poly((34, 86), (44, 72), (56, 72), (66, 86)),
    )


def rabbinic_law() -> QPainterPath:
    """A scroll open between its two rollers."""
    rollers = union(rrect(16, 14, 12, 72, 5), rrect(72, 14, 12, 72, 5))
    text = union_of(rect(32, 30 + 9 * i, 36, 3) for i in range(5))
    return union(rollers, rect(26, 22, 48, 56)).subtracted(text)


def theology_christian() -> QPainterPath:
    """The cross."""
    return union(rect(43, 12, 14, 76), rect(24, 28, 52, 14))


def theology_islam() -> QPainterPath:
    """The crescent and star."""
    return union(
        circle(44, 50, 32).subtracted(circle(54, 44, 27)), star(5, 13, 5.5, 70, 46)
    )


def theology_judaism() -> QPainterPath:
    """The two tablets of the Law."""
    tablet = union(rect(0, 12, 26, 52), circle(13, 12, 13))
    tablets = union(move(tablet, 22, 12), move(tablet, 52, 12))
    text = union_of(rect(x + 5, 34 + 9 * i, 16, 3) for x in (22, 52) for i in range(4))
    return tablets.subtracted(text)


def theology_pagan() -> QPainterPath:
    """The sun with its rays."""
    rays = union_of(
        rotate(poly((50, 8), (55, 26), (45, 26)), a) for a in range(0, 360, 30)
    )
    return union(rays, circle(50, 50, 20)).subtracted(ring(50, 50, 14, 3))


# -- Martial --


def bows() -> QPainterPath:
    """A bow and arrow: the bow's back bulges toward the target, the string
    behind it."""
    arc = ring(4, 50, 58, 7).intersected(rect(30, 6, 40, 88))
    string = bar(31, 12, 31, 88, 2.5)
    fletch = union(
        poly((14, 50), (8, 41), (20, 41), (26, 50)),
        poly((14, 50), (8, 59), (20, 59), (26, 50)),
    )
    arrow = union(bar(14, 50, 82, 50, 4), poly((92, 50), (80, 41), (80, 59)), fletch)
    return union(arc, string, arrow)


def cudgel() -> QPainterPath:
    """One upright cudgel: a thin grip with a knob, swelling to a heavy
    knotted head; drawn on the centre line, head up."""
    body = QPainterPath()
    body.moveTo(47.5, 84)
    body.lineTo(52.5, 84)
    body.quadTo(54, 62, 59, 36)
    body.quadTo(61, 16, 50, 12)
    body.quadTo(39, 16, 41, 36)
    body.quadTo(46, 62, 47.5, 84)
    body.closeSubpath()
    knots = union(circle(60, 28, 3.6), circle(40.5, 36, 3.4), circle(57.5, 46, 3))
    return union(body, knots, rrect(45, 82, 10, 6, 2.5))


def brawl() -> QPainterPath:
    """Two cudgels crossed, heads up and apart."""
    return union(rotate(cudgel(), 34, 50, 64), rotate(cudgel(), -34, 50, 64))


def great_weapon() -> QPainterPath:
    """A poleaxe: a crescent blade, a back spike and a top point."""
    pole = bar(46, 12, 46, 92, 6)
    blade = (
        circle(56, 36, 26)
        .subtracted(circle(36, 36, 24))
        .intersected(rect(48, 8, 40, 56))
    )
    spike = poly((44, 30), (22, 36), (44, 42))
    tip = poly((46, 2), (51, 14), (41, 14))
    return union(pole, blade, spike, tip)


def single_weapon() -> QPainterPath:
    """An arming sword, point up."""
    blade = poly((50, 14), (56, 24), (56, 64), (44, 64), (44, 24))
    return union(blade, rect(30, 64, 40, 7), rect(46, 71, 8, 12), circle(50, 87, 5))


def thrown_weapon() -> QPainterPath:
    """A throwing axe in flight."""
    head = (
        circle(60, 30, 22)
        .subtracted(circle(42, 30, 20))
        .intersected(rect(52, 6, 40, 48))
    )
    axe = rotate(union(bar(50, 90, 50, 30, 6), head), 35, 50, 50)
    trails = union(bar(8, 40, 26, 30, 3), bar(6, 56, 24, 46, 3), bar(10, 72, 28, 62, 3))
    return union(axe, trails)


# -- Arcane --


def concentration() -> QPainterPath:
    """Rings about a point."""
    return union(ring(50, 50, 32, 6), ring(50, 50, 20, 6), circle(50, 50, 6))


def dominion_lore() -> QPainterPath:
    """A church with its spire and cross."""
    nave = union(rect(16, 50, 46, 36), poly((12, 52), (39, 32), (66, 52)))
    tower = union(rect(60, 36, 22, 50), poly((56, 38), (71, 12), (86, 38)))
    cross = union(rect(69.5, 2, 3, 12), rect(66, 5, 10, 3))
    door = union(rect(66, 66, 10, 20), circle(71, 66, 5))
    windows = union(rect(26, 60, 6, 12), rect(42, 60, 6, 12))
    return union(nave, tower, cross).subtracted(door).subtracted(windows)


def enigmatic_wisdom() -> QPainterPath:
    """A labyrinth."""
    walls = union_of(ring(50, 50, r, 4.5) for r in (34, 24, 14))
    gaps = union(
        rect(46, 12, 8, 12), rect(46, 72, 8, 8), rect(68, 46, 10, 8), rect(22, 46, 8, 8)
    )
    return walls.subtracted(gaps).united(circle(50, 50, 5)).united(rect(48, 18, 4, 10))


def faerie_lore() -> QPainterPath:
    """A toadstool."""
    cap = (
        circle(50, 50, 34)
        .intersected(rect(10, 14, 80, 36))
        .united(rrect(16, 44, 68, 8, 4))
    )
    stem = poly((42, 52), (58, 52), (62, 86), (38, 86))
    spots = union(
        circle(36, 34, 5), circle(56, 26, 4), circle(68, 40, 4.5), circle(46, 42, 3)
    )
    return union(cap.subtracted(spots), stem)


def finesse() -> QPainterPath:
    """A threaded needle."""
    needle = union(poly((50, 90), (53, 30), (47, 30)), rrect(46, 10, 8, 22, 4))
    needle = rotate(needle.subtracted(rrect(48.5, 14, 3, 11, 1.5)), 30)
    thread = stroke(curve((60, 20), (84, 20), (74, 44), (62, 66), (30, 60)), 2.4)
    return union(needle, thread)


def infernal_lore() -> QPainterPath:
    """A pitchfork."""
    tines = union(
        bar(30, 14, 30, 42, 5),
        bar(50, 10, 50, 42, 5),
        bar(70, 14, 70, 42, 5),
        ring(50, 30, 22, 5).intersected(rect(26, 30, 48, 26)),
    )
    points = union_of(poly((x - 4, 16), (x, 6), (x + 4, 16)) for x in (30, 50, 70))
    return union(tines, points, bar(50, 50, 50, 90, 6))


def magic_lore() -> QPainterPath:
    """A Solomonic seal: a double ring of sigil marks round a drawn sigil
    of lines ending in circles and crossbars."""
    rings = union(ring(50, 50, 40, 3), ring(50, 50, 31, 3))
    glyphs = [
        rect(48.5, 13, 3, 8),
        circle(50, 15, 2.6),
        union(rect(48.5, 12, 3, 8), rect(46, 15, 8, 2.5)),
        poly((47, 20), (50, 12), (53, 20)),
        rect(48.5, 13, 3, 8),
        union(circle(50, 17, 2.6), rect(49, 12, 2, 4)),
    ] * 2
    marks = union_of(
        rotate(m, a) for a, m in zip(range(0, 360, 30), glyphs, strict=True)
    )
    sigil = union(
        bar(50, 28, 50, 72, 3),
        bar(34, 42, 66, 58, 3),
        bar(34, 58, 50, 50, 3),
        ring(50, 28, 4.5, 2.4),
        ring(50, 72, 4.5, 2.4),
        ring(66, 58, 4.5, 2.4),
        bar(28, 38, 40, 46, 2.6),
        bar(31, 36, 37, 48, 2.6),
        circle(50, 50, 4),
    )
    return union(rings, marks, sigil)


def magic_theory() -> QPainterPath:
    """Squares turned within a circle, the figure of a magical diagram."""
    frame = rect(32, 32, 36, 36).subtracted(rect(36, 36, 28, 28))
    return union(
        ring(50, 50, 34, 4),
        rotate(frame, 45),
        rect(36, 36, 28, 28).subtracted(rect(40, 40, 20, 20)),
        circle(50, 50, 4),
    )


def parma_magica() -> QPainterPath:
    """A shield with a boss."""
    shield = QPainterPath()
    shield.moveTo(24, 22)
    shield.lineTo(76, 22)
    shield.lineTo(76, 46)
    shield.quadTo(76, 72, 50, 84)
    shield.quadTo(24, 72, 24, 46)
    shield.closeSubpath()
    return shield.subtracted(scaled(shield, 0.72)).united(ring(50, 48, 11, 4))


def penetration() -> QPainterPath:
    """An arrow through a target."""
    target = ring(56, 50, 22, 6).subtracted(rect(20, 43, 70, 14))
    arrow = union(
        bar(12, 50, 80, 50, 5),
        poly((90, 50), (76, 41), (76, 59)),
        poly((12, 50), (4, 42), (10, 50), (4, 58)),
    )
    return rotate(union(target, arrow), -40)


# -- Supernatural --


def animal_ken() -> QPainterPath:
    """A stag's antlers."""
    main = stroke(curve((48, 80), (40, 50), (24, 18)), 5)
    tines = union(
        stroke(curve((38, 50), (24, 46), (18, 34)), 4),
        stroke(curve((32, 34), (38, 26), (40, 14)), 4),
    )
    antler = union(main, tines)
    skull = poly((42, 78), (58, 78), (54, 90), (46, 90))
    return union(antler, mirror(antler), skull)


def corpse_magic() -> QPainterPath:
    """A bone."""
    ends = union(
        circle(22, 72, 8), circle(28, 78, 8), circle(72, 22, 8), circle(78, 28, 8)
    )
    return union(bar(30, 70, 70, 30, 9), ends)


def crafters_healing() -> QPainterPath:
    """An anvil marked with a healer's cross."""
    anvil = QPainterPath()
    anvil.moveTo(12, 34)
    anvil.lineTo(80, 34)
    anvil.quadTo(90, 34, 90, 44)
    anvil.quadTo(76, 44, 70, 50)
    anvil.lineTo(66, 64)
    anvil.lineTo(78, 82)
    anvil.lineTo(22, 82)
    anvil.lineTo(34, 64)
    anvil.lineTo(30, 50)
    anvil.quadTo(18, 46, 12, 34)
    anvil.closeSubpath()
    return anvil.subtracted(union(rect(47, 42, 6, 18), rect(41, 48, 18, 6)))


def curse_throwing() -> QPainterPath:
    """A thunderbolt."""
    return poly((58, 8), (28, 52), (48, 52), (36, 92), (74, 40), (54, 40), (68, 8))


def dowsing() -> QPainterPath:
    """A forked dowsing rod."""
    return union(
        stroke(curve((50, 54), (36, 34), (20, 14)), 6),
        stroke(curve((50, 54), (64, 34), (80, 14)), 6),
        bar(50, 52, 50, 88, 6),
    )


def embitterment() -> QPainterPath:
    """A cracked heart."""
    crack = poly(
        (50, 34), (44, 46), (54, 54), (44, 66), (50, 82), (52, 82), (48, 66), (58, 54), (48, 46),
        (53, 34),
    )  # fmt: skip
    return heart().subtracted(crack)


def enchanting() -> QPainterPath:
    """A shepherd's pipe with a star of glamour."""
    pipe = rotate(
        union(rrect(46, 14, 8, 70, 3), poly((44, 84), (56, 84), (58, 92), (42, 92))), 35
    )
    holes = rotate(union_of(circle(50, 34 + 9 * i, 2) for i in range(5)), 35)
    return union(pipe.subtracted(holes), star(4, 14, 4, 26, 26))


def entrancement() -> QPainterPath:
    """A spiral."""
    points = []
    for i in range(160):
        t = i / 160 * 3.2 * 2 * math.pi
        r = 4 + 30 * i / 160
        points.append((50 + r * math.cos(t), 50 + r * math.sin(t)))
    return line(*points, w=6)


def faerie_magic() -> QPainterPath:
    """A faerie ring of toadstools."""
    stool = union(
        circle(50, 50, 10).intersected(rect(40, 40, 20, 10)), rect(47, 50, 6, 8)
    )
    stools = union_of(
        move(
            stool,
            32 * math.cos(math.radians(a)),
            30 * math.sin(math.radians(a)),
        )
        for a in range(0, 360, 45)
    )
    return union(stools, ring(50, 54, 30, 2), star(4, 9, 3))


def font_of_knowledge() -> QPainterPath:
    """A fountain basin with its springing jets."""
    basin = union(
        circle(50, 62, 30).intersected(rect(20, 62, 60, 14)), rect(16, 58, 68, 6)
    )
    stem = union(rect(46, 76, 8, 8), poly((34, 90), (40, 84), (60, 84), (66, 90)))
    jets = union(
        stroke(curve((50, 54), (50, 14), (28, 40)), 4),
        stroke(curve((50, 54), (50, 14), (72, 40)), 4),
        bar(50, 54, 50, 14, 4),
        circle(50, 12, 4),
    )
    return union(basin, stem, jets)


def heartbeast() -> QPainterPath:
    """A wolf's print: four clawed toes over a three-lobed pad."""
    pad = union(
        circle(38, 68, 11),
        circle(50, 64, 12),
        circle(62, 68, 11),
        rrect(30, 66, 40, 18, 9),
    )

    def toe(x: float, y: float, deg: float) -> QPainterPath:
        shape = union(
            ellipse(-6.5, -9, 13, 18), poly((-2.6, -12), (0, -21), (2.6, -12))
        )
        return QTransform().rotate(deg).map(shape).translated(x, y)

    return union(
        pad, toe(24, 46, -22), toe(40, 32, -7), toe(60, 32, 7), toe(76, 46, 22)
    )


def hex_() -> QPainterPath:
    """Three iron nails, crossed."""
    nail = union(
        poly((48, 84), (52, 84), (53, 26), (47, 26)),
        rrect(42, 20, 16, 7, 2),
        poly((48, 84), (52, 84), (50, 92)),
    )
    return union(nail, rotate(nail, 50), rotate(nail, -50))


def induction() -> QPainterPath:
    """Three linked chain links."""
    link = rrect(0, 0, 34, 20, 10).subtracted(rrect(6, 6, 22, 8, 4))
    return union(
        rotate(move(link, 8, 52), -30, 25, 62),
        rotate(move(link, 33, 40), -30, 50, 50),
        rotate(move(link, 58, 28), -30, 75, 38),
    )


def magic_sensitivity() -> QPainterPath:
    """A point sending out waves."""
    quarter = poly((30, 70), (30, 0), (100, 0), (100, 70))
    waves = union_of(ring(30, 70, r, 5).intersected(quarter) for r in (20, 34, 48))
    return union(waves, circle(30, 70, 9))


def persona() -> QPainterPath:
    """A hand mirror."""
    glass = ellipse(26, 10, 48, 54).subtracted(ellipse(32, 16, 36, 42))
    return union(
        glass, rrect(45, 62, 10, 28, 4), circle(50, 64, 7), bar(40, 26, 48, 22, 3)
    )


def premonitions() -> QPainterPath:
    """An hourglass."""
    glass = poly((28, 18), (72, 18), (52, 50), (72, 82), (28, 82), (48, 50))
    sand = union(poly((38, 34), (62, 34), (50, 48)), poly((50, 66), (64, 80), (36, 80)))
    frame = union(
        rect(20, 10, 60, 7),
        rect(20, 83, 60, 7),
        rect(22, 16, 4, 68),
        rect(74, 16, 4, 68),
    )
    return union(frame, glass.subtracted(scaled(glass, 0.78)), sand)


def second_sight() -> QPainterPath:
    """An eye beneath rays."""
    rays = union_of(rotate(bar(50, 6, 50, 22, 4), a) for a in (-50, -25, 0, 25, 50))
    return union(move(eye(), 0, 10), rays)


def sense_holiness() -> QPainterPath:
    """A disc half light and half dark, with rays."""
    rays = union_of(rotate(bar(50, 8, 50, 18, 4), a) for a in range(0, 360, 45))
    return union(
        rays, ring(50, 50, 26, 5), circle(50, 50, 22).intersected(rect(0, 0, 50, 100))
    )


def sense_passions() -> QPainterPath:
    """A heart giving off rays."""
    rays = union_of(
        rotate(bar(50, 6, 50, 16, 4), a, 50, 54) for a in range(-80, 100, 40)
    )
    return union(heart(50, 58, 0.8), rays)


def shapeshifter() -> QPainterPath:
    """The moon waxing: crescent, half, full."""
    return union(
        circle(20, 50, 13).subtracted(circle(26, 46, 11)),
        circle(50, 50, 13).intersected(rect(50, 30, 20, 40)),
        ring(50, 50, 13, 2),
        circle(80, 50, 13),
    )


def summon_animals() -> QPainterPath:
    """Birds rising."""

    def bird(x: float, y: float, k: float) -> QPainterPath:
        b = QPainterPath()
        b.moveTo(0, 0)
        b.quadTo(-8, -10, -18, -6)
        b.quadTo(-8, -4, 0, 6)
        b.quadTo(8, -4, 18, -6)
        b.quadTo(8, -10, 0, 0)
        b.closeSubpath()
        return QTransform().scale(k, k).translate(x / k, y / k).map(b)

    return union(bird(30, 74, 1.1), bird(54, 52, 1.3), bird(74, 28, 1.6))


def whistle_up_the_wind() -> QPainterPath:
    """Gusts of wind, curling."""

    def gust(y: float, length: float, curl: float) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(12, y)
        path.lineTo(12 + length, y)
        path.arcTo(12 + length - curl, y - 2 * curl, 2 * curl, 2 * curl, -90, 270)
        return stroke(path, 5)

    return union(gust(36, 54, 9), gust(56, 66, 8), move(mirror(gust(74, 44, 7)), -6, 0))


def wilderness_sense() -> QPainterPath:
    """Mountain peaks with snow on their summits."""
    peaks = union(
        poly((10, 84), (38, 26), (66, 84)), poly((40, 84), (66, 40), (92, 84))
    )
    snow = union(
        poly((31, 40), (38, 26), (45, 40), (41, 37), (38, 42), (35, 37)),
        poly((60, 50), (66, 40), (72, 50), (69, 48), (66, 52), (63, 48)),
    )
    return peaks.united(snow)


# -- Supernatural abilities of the Divine --


def adjuration() -> QPainterPath:
    """A church bell."""
    bell = QPainterPath()
    bell.moveTo(50, 16)
    bell.cubicTo(68, 16, 70, 34, 70, 50)
    bell.cubicTo(70, 62, 78, 70, 84, 74)
    bell.lineTo(16, 74)
    bell.cubicTo(22, 70, 30, 62, 30, 50)
    bell.cubicTo(30, 34, 32, 16, 50, 16)
    bell.closeSubpath()
    return union(bell, circle(50, 82, 7), ring(50, 12, 6, 3))


def blessing() -> QPainterPath:
    """A candle burning."""
    return union(
        rect(40, 40, 20, 42),
        poly((30, 88), (36, 82), (64, 82), (70, 88)),
        flame(50, 34, 16, 26),
        bar(50, 34, 50, 40, 2),
    )


def holy_music() -> QPainterPath:
    """An organ's pipes."""
    heights = (34, 48, 60, 70, 60, 48, 34)
    pipes = union_of(rect(14 + 10.5 * i, 84 - h, 8, h) for i, h in enumerate(heights))
    mouths = union_of(
        poly((15 + 10.5 * i, 70), (21 + 10.5 * i, 70), (18 + 10.5 * i, 66))
        for i in range(7)
    )
    return union(pipes, rect(10, 84, 80, 6)).subtracted(mouths)


def kabbalah() -> QPainterPath:
    """The Tree of Life: ten spheres and their paths."""
    spheres = [
        (50, 12), (72, 24), (28, 24), (72, 46), (28, 46), (50, 56), (72, 70), (28, 70), (50, 80),
        (50, 92),
    ]  # fmt: skip
    paths = [
        (0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5), (3, 6),
        (4, 7), (5, 6), (5, 7), (6, 7), (6, 8), (7, 8), (5, 8), (8, 9), (0, 5),
    ]  # fmt: skip
    lines = union_of(bar(*spheres[a], *spheres[b], 2) for a, b in paths)
    return union(lines, *(circle(x, y, 6) for x, y in spheres))


def mechanica_of_heron() -> QPainterPath:
    """A toothed gear."""
    teeth = union_of(rotate(rect(45, 10, 10, 14), a) for a in range(0, 360, 30))
    holes = union_of(rotate(circle(50, 34, 6), a) for a in range(0, 360, 90))
    return (
        union(circle(50, 50, 32), teeth)
        .subtracted(circle(50, 50, 10))
        .subtracted(holes)
    )


def merkavah() -> QPainterPath:
    """The chariot's wheel, winged."""
    wheel = union(
        ring(50, 56, 22, 5),
        *(rotate(bar(50, 56, 50, 36, 3.5), a, 50, 56) for a in range(0, 360, 45)),
        circle(50, 56, 5),
    )
    wing = QPainterPath()
    wing.moveTo(30, 46)
    wing.cubicTo(16, 30, 8, 22, 6, 12)
    wing.cubicTo(20, 18, 32, 26, 38, 38)
    wing.closeSubpath()
    return union(wheel, wing, mirror(wing))


def mythic_herbalism() -> QPainterPath:
    """A sprig of three leaves on a stem."""
    leaf = vesica(0, 0, 30, 13)
    leaves = union(
        QTransform().translate(50, 22).rotate(-90).map(leaf),
        QTransform().translate(34, 46).rotate(-140).map(leaf),
        QTransform().translate(66, 58).rotate(-40).map(leaf),
    )
    return union(leaves, stroke(curve((50, 90), (48, 60), (50, 34)), 4))


# -- Hedge Arts --


def elementalist_air() -> QPainterPath:
    return outline_triangle(True, True)


def elementalist_earth() -> QPainterPath:
    return outline_triangle(False, True)


def elementalist_fire() -> QPainterPath:
    return outline_triangle(True)


def elementalist_water() -> QPainterPath:
    return outline_triangle(False)


def medicinal_divining() -> QPainterPath:
    """The physician's urine flask, held up to the light."""
    flask = union(circle(50, 60, 26), rect(43, 18, 14, 24), rrect(38, 14, 24, 7, 3))
    return flask.subtracted(circle(50, 60, 20).intersected(rect(0, 40, 100, 14)))


# -- Categories, for an ability without its own mark --


def general() -> QPainterPath:
    """A ring and a centre point."""
    return union(ring(50, 50, 32, 7), circle(50, 50, 9))


def academic() -> QPainterPath:
    """A closed book with bands across its cover."""
    return book_closed(
        union(
            rect(34, 30, 32, 5),
            rect(34, 64, 32, 5),
            poly((50, 40), (58, 50), (50, 60), (42, 50)),
        )
    )


def martial() -> QPainterPath:
    """Two swords crossed."""
    sword = union(
        poly((50, 8), (54, 16), (54, 62), (46, 62), (46, 16)),
        rect(38, 62, 24, 5),
        rect(47, 67, 6, 12),
        circle(50, 82, 4),
    )
    return union(rotate(sword, 35), rotate(sword, -35))


def arcane() -> QPainterPath:
    """A pentacle in a ring."""
    corners = [
        (
            50 + 30 * math.cos(math.radians(-90 + i * 144)),
            50 + 30 * math.sin(math.radians(-90 + i * 144)),
        )
        for i in range(6)
    ]
    return union(ring(50, 50, 36, 4), line(*corners, w=4))


def supernatural() -> QPainterPath:
    """An eight-pointed star."""
    return union(star(8, 34, 14), circle(50, 50, 10)).subtracted(circle(50, 50, 5))


def hedge_art() -> QPainterPath:
    """A cauldron over its fire."""
    pot = union(
        circle(50, 46, 28).intersected(rect(20, 40, 60, 34)),
        rrect(18, 36, 64, 8, 3),
        bar(30, 70, 26, 80, 4),
        bar(70, 70, 74, 80, 4),
    )
    fire = union(
        move(flame(0, 0, 10, 14), 40, 92),
        move(flame(0, 0, 12, 16), 50, 92),
        move(flame(0, 0, 10, 14), 60, 92),
    )
    return union(pot, fire)


Charge = Callable[[], QPainterPath]

#: Each ability's charge, by its name (a templated ability by the part
#: before its ":" or "(", so every Craft shares the hammer).
MARKS: dict[str, Charge] = {
    "Animal Handling": animal_handling,
    "Area Lore": area_lore,
    "Athletics": athletics,
    "Awareness": awareness,
    "Bargain": bargain,
    "Brawl": brawl,
    "Carouse": carouse,
    "Charm": charm,
    "Chirurgy": chirurgy,
    "Concentration": concentration,
    "Craft": craft,
    "Etiquette": etiquette,
    "Folk Ken": folk_ken,
    "Guile": guile,
    "Hunt": hunt,
    "Intrigue": intrigue,
    "Judaic Lore": judaic_lore,
    "Leadership": leadership,
    "Legerdemain": legerdemain,
    "Living Language": living_language,
    "Music": music,
    "Mystery Cult Lore": mystery_cult_lore,
    "Organization Lore": organization_lore,
    "Profession": profession,
    "Ride": ride,
    "Stealth": stealth,
    "Survival": survival,
    "Swim": swim,
    "Teaching": teaching,
    "Art of Memory": art_of_memory,
    "Artes Liberales": artes_liberales,
    "Civil and Canon Law": civil_and_canon_law,
    "Common Law": common_law,
    "Dead Language": dead_language,
    "Islamic Law": islamic_law,
    "Medicine": medicine,
    "Philosophiae": philosophiae,
    "Rabbinic Law": rabbinic_law,
    "Theology: Christian": theology_christian,
    "Theology: Islam": theology_islam,
    "Theology: Judaism": theology_judaism,
    "Theology: Pagan": theology_pagan,
    "Bows": bows,
    "Great Weapon": great_weapon,
    "Single Weapon": single_weapon,
    "Thrown Weapon": thrown_weapon,
    "Dominion Lore": dominion_lore,
    "Enigmatic Wisdom": enigmatic_wisdom,
    "Faerie Lore": faerie_lore,
    "Finesse": finesse,
    "Infernal Lore": infernal_lore,
    "Magic Lore": magic_lore,
    "Magic Theory": magic_theory,
    "Parma Magica": parma_magica,
    "Penetration": penetration,
    "Animal Ken": animal_ken,
    "Corpse Magic": corpse_magic,
    "Crafter's Healing": crafters_healing,
    "Curse-Throwing": curse_throwing,
    "Dowsing": dowsing,
    "Embitterment": embitterment,
    "Enchanting": enchanting,
    "Entrancement": entrancement,
    "Faerie Magic": faerie_magic,
    "Font of Knowledge": font_of_knowledge,
    "Heartbeast": heartbeast,
    "Hex": hex_,
    "Induction": induction,
    "Magic Sensitivity": magic_sensitivity,
    "Persona": persona,
    "Premonitions": premonitions,
    "Second Sight": second_sight,
    "Sense Holiness and Unholiness": sense_holiness,
    "Sense Passions": sense_passions,
    "Shapeshifter": shapeshifter,
    "Summon Animals": summon_animals,
    "Whistle Up The Wind": whistle_up_the_wind,
    "Wilderness Sense": wilderness_sense,
    "Adjuration": adjuration,
    "Blessing": blessing,
    "Holy Music": holy_music,
    "Kabbalah": kabbalah,
    "Mechanica of Heron": mechanica_of_heron,
    "Merkavah": merkavah,
    "Mythic Herbalism": mythic_herbalism,
    "Elementalist Air": elementalist_air,
    "Elementalist Earth": elementalist_earth,
    "Elementalist Fire": elementalist_fire,
    "Elementalist Water": elementalist_water,
    "Medicinal Divining": medicinal_divining,
}

#: The mark of each category, for an ability without its own.
CATEGORIES: dict[str, Charge] = {
    "General": general,
    "Academic": academic,
    "Martial": martial,
    "Arcane": arcane,
    "Supernatural": supernatural,
    "Hedge Art": hedge_art,
}

#: Marks taken from a released emblem rather than drawn: the Order of
#: Hermes's sigil, the same artwork as the app icon.
IMAGES = {"Code of Hermes": artwork.SIGIL}

#: Charges built from lines, or too slender, for the engraved second line
#: a large mark draws just inside a broad charge's edge.
PLAIN = {
    "Animal Handling", "Animal Ken", "Arcane", "Bargain", "Brawl", "Chirurgy", "Code of Hermes",
    "Dowsing", "Elementalist Air", "Elementalist Earth", "Elementalist Fire",
    "Elementalist Water", "Enigmatic Wisdom", "Entrancement", "Faerie Magic", "Finesse",
    "Font of Knowledge", "Great Weapon", "Heartbeast", "Hex", "Hunt", "Induction", "Intrigue",
    "Judaic Lore", "Kabbalah", "Legerdemain", "Magic Lore", "Magic Sensitivity", "Merkavah",
    "Music", "Mythic Herbalism", "Persona", "Premonitions", "Sense Holiness and Unholiness",
    "Shapeshifter", "Summon Animals", "Swim", "Thrown Weapon", "Whistle Up The Wind",
}  # fmt: skip


def _brawl_detail() -> QPainterPath:
    """Each cudgel's bound grip and the grain of its head."""
    one = union(
        line((46.5, 74), (53.5, 74), w=1.2),
        line((46.5, 78), (53.5, 78), w=1.2),
        line((48, 22), (49, 44), w=1.1),
        line((53, 26), (52.5, 40), w=1.1),
    )
    return union(rotate(one, 34, 50, 64), rotate(one, -34, 50, 64))


#: Lines engraved back into a charge in the block's colour, drawn only on
#: a large mark: a quill's barbs, a book's text, a crown's jewels.
DETAILS: dict[str, Charge] = {
    "Adjuration": lambda: union(
        line((32, 62), (68, 62), w=1.4), line((31, 56), (69, 56), w=1.2)
    ),
    "Blessing": lambda: line((44, 46), (44, 78), w=1.1),
    "Bows": lambda: union(line((14, 46), (20, 46)), line((14, 54), (20, 54))),
    "Brawl": _brawl_detail,
    "Carouse": lambda: line((28, 32), (72, 32), w=1.2),
    "Charm": lambda: union_of(
        rotate(line((50, 43), (50, 30), w=1.3), a) for a in range(0, 360, 72)
    ),
    "Corpse Magic": lambda: line((36, 64), (64, 36), w=1.3),
    "Craft": lambda: union(line((34, 24), (34, 40)), line((66, 24), (66, 40))),
    "Dead Language": lambda: rotate(
        union_of(
            line((26 + 8 * i, 50), (32 + 8 * i, 44 if i % 2 else 56), w=1.4)
            for i in range(6)
        ),
        -50,
    ),
    "Faerie Lore": lambda: union(
        line((44, 56), (46, 82), w=1.2), line((56, 56), (54, 82), w=1.2)
    ),
    "Folk Ken": lambda: line((58, 22), (58, 38), w=1.2),
    "Leadership": lambda: union(
        circle(36, 63, 3), circle(50, 63, 3), circle(64, 63, 3)
    ),
    "Living Language": lambda: union(
        line((52, 36), (52, 62), w=2.4),
        line((58, 36), (58, 62), w=2.4),
        line((36, 36), (36, 62), w=1.2),
    ),
    "Medicine": lambda: line((30, 62), (70, 62)),
    "Organization Lore": lambda: union(
        line((36, 26), (64, 26), w=1.2), line((36, 42), (60, 42), w=1.2)
    ),
    "Parma Magica": lambda: line((30, 34), (70, 34)),
    "Single Weapon": lambda: line((50, 26), (50, 60), w=1.6),
    "Survival": lambda: flame(50, 66, 16, 26).subtracted(flame(50, 66, 10, 16)),
    "Teaching": lambda: union(
        *(line((22, 37 + 5 * i), (44, 39 + 5 * i), w=1.1) for i in range(3)),
        *(line((56, 39 + 5 * i), (78, 37 + 5 * i), w=1.1) for i in range(3)),
    ),
}
