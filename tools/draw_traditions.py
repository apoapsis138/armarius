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
from collections.abc import Callable, Sequence
from itertools import pairwise
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QPainterPath, QTransform
from PySide6.QtWidgets import QApplication

from ars_magica_manager import artwork
from ars_magica_manager.gui.mark_charges import RUNES, _rune
from ars_magica_manager.gui.mark_shapes import (
    Point,
    bar,
    circle,
    curve,
    ellipse,
    flame,
    mirror,
    move,
    outline_triangle,
    over,
    poly,
    rect,
    ring,
    rotate,
    rough,
    rrect,
    scaled,
    star,
    stroke,
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


# -- The faerie traditions (Realms of Power: Faerie) --


def _path(*points: Point, closed: bool = False) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    if closed:
        path.closeSubpath()
    return path


def ollamhain() -> QPainterPath:
    """The poets' harp: its curved neck, pillar and strings."""
    frame = union(
        stroke(curve((26, 86), (22, 40), (30, 16)), 8),
        stroke(curve((30, 16), (56, 30), (80, 24)), 8),
        stroke(curve((80, 24), (70, 56), (30, 84)), 7),
    )
    strings = union_of(
        bar(30 + 7 * i, 22 + 1.5 * i, 30 + 7 * i, 80 - 6 * i, 2) for i in range(7)
    )
    return union(frame, strings.intersected(poly((26, 20), (80, 26), (30, 84))))


def volkhvy() -> QPainterPath:
    """A pagan idol: a carved pillar under a round cap, its faces turned
    to the four winds."""
    cap = union(
        circle(50, 22, 14).intersected(rect(30, 6, 40, 16)), rect(34, 20, 32, 6)
    )
    pillar = rect(38, 26, 24, 64)
    face = union(
        circle(45, 36, 2.6),
        circle(55, 36, 2.6),
        rect(44, 44, 12, 3),
        bar(50, 54, 40, 62, 3),
        bar(50, 54, 60, 62, 3),
        rect(40, 72, 20, 3),
    )
    return union(cap, pillar.subtracted(face), rect(32, 88, 36, 6))


def wise_folk() -> QPainterPath:
    """The cunning folk's sieve and shears, for turning the sieve to find
    a thief."""
    sieve = ring(50, 44, 30, 7)
    mesh = union_of(rect(20 + 8 * i, 14, 2, 60) for i in range(8)).united(
        union_of(rect(20, 18 + 8 * i, 60, 2) for i in range(8))
    )
    shears = union(
        bar(30, 86, 70, 30, 5),
        bar(70, 86, 30, 30, 5),
        ring(26, 88, 6, 3),
        ring(74, 88, 6, 3),
    )
    return over(shears, union(sieve, mesh.intersected(circle(50, 44, 24))))


def borrowers() -> QPainterPath:
    """A goblet held out, a star of borrowed glamour above it."""
    cup = union(
        circle(50, 46, 22).intersected(rect(28, 46, 44, 22)),
        rect(28, 42, 44, 6),
        rect(47, 66, 6, 16),
        poly((34, 90), (42, 80), (58, 80), (66, 90)),
    )
    return union(cup, star(4, 16, 4, 50, 22))


def faerie_doctors() -> QPainterPath:
    """An elf-shot: the flint arrowhead the faerie doctor draws from the
    sick, beside the bottle of their cure."""
    head = poly((34, 10), (48, 40), (40, 72), (28, 72), (20, 40))
    knaps = union_of(
        poly((22 + 4 * (i % 2), 30 + 10 * i), (30, 34 + 10 * i), (24, 36 + 10 * i))
        for i in range(4)
    )
    bottle = union(
        circle(66, 70, 18),
        rect(61, 34, 10, 22),
        rrect(58, 28, 16, 6, 2),
    ).subtracted(circle(66, 70, 12).intersected(rect(0, 70, 100, 30)))
    return union(head.subtracted(knaps), bottle)


def homunculus_wizards() -> QPainterPath:
    """A flask, and the little man grown in it."""
    flask = (
        circle(50, 60, 30).united(rect(42, 12, 16, 30)).united(rrect(36, 8, 28, 7, 3))
    )
    hollow = circle(50, 60, 24).united(rect(46, 16, 8, 30))
    figure = union(
        circle(50, 48, 6),
        rrect(44, 54, 12, 16, 4),
        bar(46, 58, 38, 66, 3),
        bar(54, 58, 62, 66, 3),
        bar(47, 68, 44, 80, 3.5),
        bar(53, 68, 56, 80, 3.5),
    )
    return union(flask.subtracted(hollow), figure)


def caerflorons_line() -> QPainterPath:
    """A crowned rose, for a line of faerie blood."""
    petals = union_of(
        circle(
            50 + 13 * math.cos(math.radians(a)), 60 + 13 * math.sin(math.radians(a)), 11
        )
        for a in range(-90, 270, 72)
    )
    rose = petals.subtracted(ring(50, 60, 8, 2)).united(circle(50, 60, 4))
    crown = union(
        rect(32, 30, 36, 6),
        poly((32, 30), (32, 12), (41, 22), (50, 8), (59, 22), (68, 12), (68, 30)),
    )
    return union(
        rose,
        crown.subtracted(
            union(circle(41, 30, 2), circle(50, 30, 2), circle(59, 30, 2))
        ),
    )


def wordsmiths() -> QPainterPath:
    """A quill writing on a scroll: the word made a working."""
    scroll = (
        union(
            rect(14, 56, 64, 26),
            circle(14, 69, 13),
            circle(78, 69, 13),
        )
        .subtracted(circle(14, 69, 7))
        .subtracted(union_of(rect(26, 62 + 6 * i, 40, 2.4) for i in range(3)))
    )
    quill = union(
        rotate(vesica(64, 30, 60, 16), -50, 64, 30),
        bar(48, 52, 40, 64, 2.6),
    ).subtracted(rotate(rect(44, 29, 40, 2), -50, 64, 30))
    return over(quill, scroll)


# -- The holy traditions (Realms of Power: The Divine and others) --


def ascetics() -> QPainterPath:
    """A stylite's pillar, its ascetic standing on the top."""
    pillar = union(rect(40, 36, 20, 52), rect(34, 30, 32, 6), rect(32, 86, 36, 8))
    flutes = union(rect(45, 40, 2, 44), rect(53, 40, 2, 44))
    figure = union(circle(50, 12, 6), rrect(45, 18, 10, 12, 3))
    return union(pillar.subtracted(flutes), figure)


def cantores() -> QPainterPath:
    """Square notes of chant on a four-line staff."""
    staff = union_of(rect(10, 30 + 12 * i, 80, 2.4) for i in range(4))
    notes = union(
        rect(18, 40, 10, 9), rect(36, 28, 10, 9), rect(54, 52, 10, 9), rect(72, 40, 10, 9),
        rect(80, 40, 2.4, 30),
    )  # fmt: skip
    clef = union(rect(10, 22, 3, 46), rect(10, 22, 8, 3), rect(10, 65, 8, 3))
    return union(staff, notes, clef)


def sufis() -> QPainterPath:
    """The reed flute of the dervishes, its song turning in a spiral."""
    spiral = QPainterPath()
    for i in range(140):
        t = i / 14
        r = 2 + 3.2 * t
        x, y = 50 + r * math.cos(t), 50 + r * math.sin(t)
        if i == 0:
            spiral.moveTo(x, y)
        else:
            spiral.lineTo(x, y)
    flute = rotate(rrect(46, 4, 8, 92, 3), 45).subtracted(
        rotate(union_of(circle(50, 60 + 7 * i, 1.8) for i in range(5)), 45)
    )
    return over(flute, stroke(spiral, 4))


def baal_shem() -> QPainterPath:
    """A shofar, the ram's horn blown on the holy days."""
    upper, lower = [], []
    for i in range(41):
        t = i / 40
        a = math.radians(200 - 150 * t)
        r = 30 + 6 * t
        x, y = 52 + r * math.cos(a), 56 + r * math.sin(a)
        w = 2.5 + 10 * t**1.5
        upper.append((x - w * math.cos(a), y - w * math.sin(a)))
        lower.append((x + w * math.cos(a), y + w * math.sin(a)))
    horn = poly(*upper, *reversed(lower))
    bands = union_of(rotate(rect(50, 6, 2.4, 30), a, 52, 56) for a in (-30, 0, 30))
    mouth = ellipse(70, 42, 26, 32).subtracted(ellipse(76, 48, 14, 20))
    return union(horn.subtracted(bands), mouth)


def kabbalists() -> QPainterPath:
    """The Tree of the Sefirot: ten spheres and the paths between them."""
    spheres = [
        (50, 10), (28, 24), (72, 24), (28, 46), (72, 46), (50, 56), (28, 70), (72, 70),
        (50, 78), (50, 94),
    ]  # fmt: skip
    paths = [
        (0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 5), (3, 6), (4, 7),
        (5, 6), (5, 7), (6, 7), (6, 8), (7, 8), (5, 8), (8, 9), (0, 5),
    ]  # fmt: skip
    lines = union_of(bar(*spheres[a], *spheres[b], 2.4) for a, b in paths)
    balls = union_of(circle(x, y, 6) for x, y in spheres)
    return union(lines, balls)


def sol_invictus() -> QPainterPath:
    """The unconquered sun, a cross at its heart."""
    rays = star(8, 46, 20)
    disc = ring(50, 50, 22, 5)
    cross = union(rect(46, 32, 8, 36), rect(32, 46, 36, 8))
    return union(rays.subtracted(circle(50, 50, 25)), disc, cross)


def priory_of_saint_nerius() -> QPainterPath:
    """A priory's hand bell."""
    bell = QPainterPath()
    bell.moveTo(24, 76)
    bell.cubicTo(30, 70, 30, 36, 50, 30)
    bell.cubicTo(70, 36, 70, 70, 76, 76)
    bell.closeSubpath()
    return union(
        bell,
        rect(18, 74, 64, 6),
        circle(50, 86, 6),
        rect(46, 12, 8, 20),
        rrect(42, 8, 16, 8, 4),
    ).subtracted(rect(30, 60, 40, 3))


def zoroastrians() -> QPainterPath:
    """The sacred fire on its stepped altar."""
    altar = union(
        rect(26, 84, 48, 8), rect(32, 76, 36, 8), rect(40, 58, 20, 18),
        rect(32, 50, 36, 8), rect(28, 44, 44, 6),
    )  # fmt: skip
    fire = union(flame(50, 44, 30, 40), flame(38, 44, 14, 20), flame(62, 44, 14, 20))
    return union(altar, fire.subtracted(flame(50, 44, 12, 18)))


def karaites() -> QPainterPath:
    """The scroll of the written Law, open between its two rollers."""
    sheet = rect(26, 22, 48, 56).subtracted(
        union_of(rect(32, 30 + 7 * i, 36, 2.4) for i in range(7))
    )

    def roller(x: float) -> QPainterPath:
        return union(
            rrect(x - 7, 18, 14, 64, 6),
            rect(x - 2, 8, 4, 84),
            circle(x, 8, 4),
            circle(x, 92, 4),
        )

    return union(sheet, roller(22), roller(78))


def celi_de() -> QPainterPath:
    """The ringed cross of the Irish churches."""
    cross = union(rect(42, 8, 16, 88), rect(14, 32, 72, 16), rect(36, 84, 28, 10))
    ring_ = ring(50, 40, 24, 6)
    return union(cross, ring_).subtracted(circle(50, 40, 4))


def mobeds() -> QPainterPath:
    """The winged disc of the Zoroastrian priests."""
    wing = union_of(rrect(12 + 2 * i, 36 + 8 * i, 34 - 4 * i, 6, 3) for i in range(4))
    tail = union_of(rrect(42 + 2 * i, 66 + 6 * i, 16 - 4 * i, 5, 2) for i in range(3))
    return union(wing, mirror(wing), tail, ring(50, 46, 12, 5), circle(50, 46, 3))


def hesychasts() -> QPainterPath:
    """A prayer rope of knots, with its tassel and cross."""
    knots = union_of(
        circle(
            50 + 30 * math.cos(math.radians(a)), 44 + 30 * math.sin(math.radians(a)), 5
        )
        for a in range(-60, 241, 20)
    )
    cord = ring(50, 44, 31, 2.4)
    cross = union(rect(47, 76, 6, 20), rect(41, 81, 18, 5))
    return union(knots, cord, cross)


def society_of_cyprian_and_justina() -> QPainterPath:
    """A book of sorcery laid open under the cross, as Cyprian turned from
    magic to the saints."""
    book = (
        union(
            poly((10, 50), (48, 58), (48, 92), (10, 84)),
            poly((90, 50), (52, 58), (52, 92), (90, 84)),
        )
        .subtracted(union_of(bar(16, 60 + 7 * i, 42, 66 + 7 * i, 2) for i in range(3)))
        .subtracted(union_of(bar(84, 60 + 7 * i, 58, 66 + 7 * i, 2) for i in range(3)))
    )
    cross = union(rect(46, 6, 8, 42), rect(34, 16, 32, 8))
    return union(book, cross)


def kassalan_exorcists() -> QPainterPath:
    """An aspergillum shaking holy water."""
    head = circle(50, 30, 16).subtracted(
        union_of(
            circle(
                50 + 8 * math.cos(math.radians(a)),
                30 + 8 * math.sin(math.radians(a)),
                2.4,
            )
            for a in range(0, 360, 60)
        )
    )
    handle = union(rect(46, 44, 8, 46), rrect(42, 44, 16, 6, 2))
    drops = union_of(
        union(circle(x, y, 3), poly((x - 2.6, y - 1), (x, y - 7), (x + 2.6, y - 1)))
        for x, y in ((22, 30), (78, 30), (28, 54), (72, 54), (50, 6))
    )
    return union(head, handle, drops)


def baal_ov() -> QPainterPath:
    """A skull raised from the pit, for those who speak with the dead."""
    cranium = union(circle(50, 38, 25), rrect(34, 46, 32, 18, 6))
    sockets = union(
        poly((34, 38), (46, 36), (47, 46), (40, 50), (34, 46)),
        poly((66, 38), (54, 36), (53, 46), (60, 50), (66, 46)),
    )
    nose = poly((50, 50), (46, 58), (50, 60), (54, 58))
    brow = stroke(curve((32, 33), (50, 28), (68, 33)), 1.6)
    crack = stroke(_path((58, 14), (54, 20), (58, 24), (55, 30)), 1.4)
    cheeks = union(rect(30, 52, 6, 2), rect(64, 52, 6, 2))
    jaw = rrect(37, 64, 26, 12, 4).subtracted(rect(37, 64, 26, 3))
    teeth = union_of(rect(40 + 5 * i, 62, 1.6, 10) for i in range(4))
    pit = rrect(14, 82, 72, 10, 5)
    skull = cranium.subtracted(union(sockets, nose, brow, crack, cheeks))
    return union(skull, jaw).subtracted(teeth).united(pit)


# -- The infernal traditions (Realms of Power: The Infernal and others) --


def luciferans() -> QPainterPath:
    """The morning star falling, its light trailing behind."""
    head = star(5, 20, 8, 66, 66, -72)

    def tail(offset: float, length: float, width: float) -> QPainterPath:
        # a wedge along the line of the fall, narrowing away from the star
        ux, uy = -math.sqrt(0.5), -math.sqrt(0.5)
        nx, ny = -uy, ux
        sx, sy = 54 + nx * offset, 54 + ny * offset
        return poly(
            (sx + nx * width, sy + ny * width),
            (sx - nx * width, sy - ny * width),
            (sx + ux * length, sy + uy * length),
        )

    trail = union(tail(0, 52, 5), tail(13, 36, 3.4), tail(-13, 36, 3.4))
    return union(head, trail.subtracted(circle(66, 66, 21)))


def strigae() -> QPainterPath:
    """The strix, the screech owl whose shape the witch takes."""
    body = union(
        ellipse(22, 20, 56, 68),
        poly((24, 28), (28, 6), (40, 22)),
        poly((76, 28), (72, 6), (60, 22)),
    )
    eyes = union(ring(38, 40, 10, 3.4), ring(62, 40, 10, 3.4))
    beak = poly((46, 50), (54, 50), (50, 60))
    breast = union_of(
        poly((36 + 9 * i, 66 + (i % 2) * 4), (40 + 9 * i, 72), (32 + 9 * i, 72))
        for i in range(4)
    )
    talons = union(rect(36, 86, 10, 6), rect(54, 86, 10, 6))
    return union(
        body.subtracted(union(eyes, beak, breast)),
        circle(38, 40, 3),
        circle(62, 40, 3),
        talons,
    )


def witch_hammers() -> QPainterPath:
    """A war hammer, the witch-hunters' Malleus."""
    head = union(rect(22, 16, 30, 18), poly((52, 18), (84, 25), (52, 32)))
    face = union_of(rect(22, 18 + 5 * i, 4, 2) for i in range(3))
    shaft = union(rect(34, 34, 8, 56), rrect(31, 82, 14, 10, 3))
    return union(head.subtracted(face), shaft)


def dark_gnostics() -> QPainterPath:
    """The serpent devouring its own tail."""
    body = ring(50, 50, 34, 9).subtracted(poly((50, 50), (72, 4), (90, 20)))
    head = union(ellipse(66, 8, 22, 16), poly((86, 16), (94, 10), (92, 22)))
    scales = union_of(rotate(rect(48, 18, 4, 9), a) for a in range(60, 330, 20))
    return union(body.subtracted(scales), head.subtracted(circle(78, 13, 2.2)))


def dread_host() -> QPainterPath:
    """The antlered skull of the Wild Hunt's leader."""
    skull = union(circle(50, 52, 16), rrect(40, 58, 20, 24, 6))
    holes = union(
        ellipse(39, 46, 9, 10),
        ellipse(52, 46, 9, 10),
        poly((50, 60), (47, 66), (53, 66)),
    )
    antler = union(
        stroke(curve((40, 40), (26, 30), (20, 10)), 5),
        stroke(curve((28, 32), (16, 30), (8, 20)), 4),
        stroke(curve((24, 22), (28, 14), (32, 6)), 4),
    )
    return union(skull.subtracted(holes), antler, mirror(antler))


def mulhidun() -> QPainterPath:
    """A dagger under the crescent, for the hidden heretics."""
    moon = circle(50, 34, 26).subtracted(circle(58, 28, 22))
    dagger = union(
        poly((47, 40), (53, 40), (52, 82), (50, 92), (48, 82)),
        rrect(36, 34, 28, 6, 2),
        rect(46, 16, 8, 18),
        circle(50, 14, 5),
    )
    return over(dagger, moon)


def damhadh_duidsan() -> QPainterPath:
    """Smoke rising in curls from a fire."""
    fire = union(flame(50, 90, 30, 30), flame(36, 90, 16, 18), flame(64, 90, 16, 18))
    smoke = union(
        stroke(curve((50, 58), (34, 48), (50, 38), (66, 28), (50, 16)), 6),
        stroke(curve((36, 56), (24, 46), (32, 34)), 4),
        stroke(curve((64, 56), (76, 46), (68, 34)), 4),
    )
    return union(fire.subtracted(flame(50, 90, 12, 14)), smoke)


def ordo_vagorum() -> QPainterPath:
    """The wandering scholars' dice and cup."""
    die = rrect(0, 0, 26, 26, 4)

    def placed(
        x: float, y: float, deg: float, pips: list[tuple[float, float]]
    ) -> QPainterPath:
        face = die.subtracted(union_of(circle(px, py, 3) for px, py in pips))
        return rotate(move(face, x, y), deg, x + 13, y + 13)

    dice = union(
        placed(14, 60, -15, [(7, 7), (13, 13), (19, 19)]),
        placed(42, 66, 12, [(7, 7), (19, 7), (7, 19), (19, 19)]),
    )
    cup = union(
        poly((52, 12), (86, 12), (80, 52), (58, 52)),
        rect(48, 8, 42, 6),
    ).subtracted(rect(58, 22, 22, 3))
    return union(dice, cup)


def witches_of_thessaly() -> QPainterPath:
    """The moon drawn down into a bowl."""
    moon = circle(50, 26, 20).subtracted(circle(60, 20, 16))
    bowl = union(
        circle(50, 62, 30).intersected(rect(20, 62, 60, 30)),
        rect(18, 58, 64, 6),
        rect(40, 88, 20, 6),
    )
    drops = union_of(
        circle(50 + dx, 50 - dy, 2.4) for dx, dy in ((0, 0), (-4, 8), (2, 14))
    )
    return union(moon, bowl, drops)


def cailleach_phiseogach() -> QPainterPath:
    """A piseog: the rotten egg hidden in a neighbour's field, cracked."""
    egg = QPainterPath()
    egg.moveTo(50, 10)
    egg.cubicTo(76, 10, 82, 60, 76, 74)
    egg.cubicTo(68, 92, 32, 92, 24, 74)
    egg.cubicTo(18, 60, 24, 10, 50, 10)
    egg.closeSubpath()
    crack = poly(
        (22, 50),
        (34, 44),
        (42, 54),
        (52, 42),
        (62, 54),
        (72, 44),
        (80, 50),
        (80, 54),
        (72, 48),
        (62, 58),
        (52, 46),
        (42, 58),
        (34, 48),
        (22, 54),
    )
    return egg.subtracted(crack)


def stringla() -> QPainterPath:
    """A bat, the night shape of the Balkan witch."""
    wing = QPainterPath()
    wing.moveTo(50, 42)
    wing.lineTo(42, 36)
    wing.cubicTo(30, 26, 14, 26, 4, 34)
    wing.quadTo(14, 38, 14, 50)
    wing.quadTo(20, 42, 28, 50)
    wing.quadTo(34, 42, 40, 54)
    wing.quadTo(44, 48, 50, 54)
    wing.closeSubpath()
    bones = union(
        bar(44, 38, 14, 49, 1.4), bar(44, 39, 28, 49, 1.4), bar(46, 40, 40, 53, 1.4)
    )
    body = union(
        ellipse(45, 36, 10, 24),
        poly((45, 38), (43, 28), (49, 35)),
        poly((55, 38), (57, 28), (51, 35)),
    )
    wings = union(wing, mirror(wing)).subtracted(union(bones, mirror(bones)))
    return union(wings, body)


def paulicians() -> QPainterPath:
    """Light and darkness, the two principles of the dualists: the sun
    and the moon set either side of a dividing line."""
    sun = union(
        circle(26, 50, 12),
        union_of(
            bar(
                26 + 16 * math.cos(math.radians(a)),
                50 + 16 * math.sin(math.radians(a)),
                26 + 22 * math.cos(math.radians(a)),
                50 + 22 * math.sin(math.radians(a)),
                3.4,
            )
            for a in range(0, 360, 45)
        ),
    )
    moon = circle(74, 50, 18).subtracted(circle(82, 44, 15))
    line = rect(48, 12, 4, 76)
    return union(sun, moon, line, star(4, 5, 1.4, 86, 72))


# -- The Hermetic traditions of Ex Miscellanea (Houses of Hermes: Societates) --


def beast_masters() -> QPainterPath:
    """A bull's head, horned, for the masters of beasts."""
    face = poly((30, 36), (70, 36), (62, 80), (50, 92), (38, 80))
    horn = stroke(curve((32, 38), (10, 34), (12, 10)), 8)
    ears = poly((30, 40), (14, 46), (30, 50))
    holes = union(
        ellipse(36, 48, 8, 6),
        ellipse(56, 48, 8, 6),
        circle(44, 82, 2.6),
        circle(56, 82, 2.6),
    )
    tuft = union(circle(44, 36, 5), circle(50, 33, 5), circle(56, 36, 5))
    return union(face.subtracted(holes), horn, mirror(horn), ears, mirror(ears), tuft)


def tempestaria() -> QPainterPath:
    """A cord tied in three knots of wind, as the weather-witches sold
    them to sailors."""
    cord = stroke(curve((6, 70), (28, 20), (50, 50), (72, 80), (94, 30)), 7)
    spots = ((26, 40), (50, 50), (74, 60))
    knots = union_of(
        union(circle(x, y, 10), bar(x - 13, y + 6, x + 13, y - 6, 5)) for x, y in spots
    )
    holes = union_of(circle(x, y, 3.4) for x, y in spots)
    return union(cord, knots.subtracted(holes))


def scinnfolk() -> QPainterPath:
    """A hooded shade, a face of darkness under its cowl."""
    cloak = QPainterPath()
    cloak.moveTo(50, 8)
    cloak.cubicTo(76, 8, 78, 40, 76, 56)
    cloak.lineTo(88, 92)
    cloak.lineTo(12, 92)
    cloak.lineTo(24, 56)
    cloak.cubicTo(22, 40, 24, 8, 50, 8)
    cloak.closeSubpath()
    face = vesica(50, 40, 24, 34).united(ellipse(38, 24, 24, 34))
    folds = union(
        bar(40, 66, 32, 90, 2.4), bar(60, 66, 68, 90, 2.4), bar(50, 70, 50, 90, 2.4)
    )
    eyes = union(circle(44, 40, 2.4), circle(56, 40, 2.4))
    return union(cloak.subtracted(union(face, folds)), eyes)


def columbae() -> QPainterPath:
    """A dove in flight."""
    body = QPainterPath()
    body.moveTo(84, 30)
    body.cubicTo(74, 24, 66, 30, 62, 38)
    body.cubicTo(50, 50, 30, 56, 12, 70)
    body.lineTo(26, 70)
    body.lineTo(18, 80)
    body.cubicTo(40, 72, 60, 64, 70, 50)
    body.cubicTo(76, 42, 80, 36, 92, 34)
    body.closeSubpath()
    wing = QPainterPath()
    wing.moveTo(62, 44)
    wing.cubicTo(50, 30, 40, 18, 22, 10)
    wing.cubicTo(30, 26, 36, 38, 48, 52)
    wing.closeSubpath()
    feathers = union_of(
        bar(30 + 6 * i, 14 + 5 * i, 40 + 6 * i, 30 + 5 * i, 1.6) for i in range(3)
    )
    return union(body, wing.subtracted(feathers)).subtracted(circle(76, 32, 1.8))


def donatores_requietis_aeternae() -> QPainterPath:
    """A funeral candle on its stand, burning for the dead."""
    stand = union(
        rect(40, 82, 20, 4),
        poly((30, 94), (40, 86), (60, 86), (70, 94)),
        rect(32, 46, 36, 4),
    )
    candle = rect(42, 30, 16, 52).subtracted(union(rect(46, 36, 3, 40)))
    fire = flame(50, 28, 14, 24).subtracted(flame(50, 28, 6, 10))
    return union(stand, candle, fire)


def pharmacopoeians() -> QPainterPath:
    """An apothecary's jar, with its label and lid."""
    jar = QPainterPath()
    jar.moveTo(30, 22)
    jar.lineTo(70, 22)
    jar.cubicTo(78, 40, 78, 70, 70, 88)
    jar.lineTo(30, 88)
    jar.cubicTo(22, 70, 22, 40, 30, 22)
    jar.closeSubpath()
    lid = union(rrect(28, 12, 44, 8, 3), circle(50, 10, 4))
    label = rrect(32, 44, 36, 22, 3).subtracted(
        union(rect(38, 50, 24, 2.4), rect(38, 57, 18, 2.4))
    )
    return union(jar.subtracted(rrect(30, 42, 40, 26, 4)), label, lid)


def lineage_of_pralix() -> QPainterPath:
    """A torch held high, Pralix's challenge to the Order."""
    torch = union(poly((44, 44), (56, 44), (54, 92), (46, 92)), rrect(40, 38, 20, 8, 3))
    bands = union(rect(45, 56, 10, 2.4), rect(45, 70, 10, 2.4))
    fire = union(flame(50, 38, 30, 34), flame(38, 40, 12, 16), flame(62, 40, 12, 16))
    return union(torch.subtracted(bands), fire.subtracted(flame(50, 38, 10, 14)))


def rustic_magi() -> QPainterPath:
    """A sheaf of wheat bound, and the sickle that cut it."""
    stalks = union_of(bar(50, 90, 50 + d, 30, 3) for d in (-16, -8, 0, 8, 16))
    ears = union_of(
        rotate(vesica(50 + d, 22, 20, 8), 90 + d * 0.8, 50 + d, 22)
        for d in (-18, -9, 0, 9, 18)
    )
    band = rect(38, 62, 24, 6)
    sickle = union(
        ring(62, 40, 26, 6).intersected(rect(36, 10, 60, 30)),
        rect(84, 36, 6, 24),
    )
    return union(stalks, ears, band, sickle)


def hermetic_sahirs() -> QPainterPath:
    """The oil lamp a jinni is bound in, its smoke rising."""
    lamp = union(
        ellipse(18, 56, 56, 24),
        poly((70, 64), (92, 58), (90, 64), (72, 72)),
        stroke(curve((22, 64), (8, 60), (12, 74)), 5),
        rrect(38, 50, 18, 8, 3),
        rect(36, 78, 22, 6),
    )
    smoke = stroke(curve((88, 56), (76, 40), (86, 28), (96, 16), (80, 8)), 5)
    return union(lamp, smoke)


def seirenes() -> QPainterPath:
    """A lyre, for the Seirenes' songs."""
    arms = union(
        stroke(curve((34, 82), (16, 52), (30, 26), (36, 16), (26, 10)), 7),
        stroke(curve((66, 82), (84, 52), (70, 26), (64, 16), (74, 10)), 7),
    )
    yoke = rect(24, 22, 52, 6)
    body = union(
        circle(50, 80, 14).intersected(rect(30, 68, 40, 30)), rect(34, 76, 32, 6)
    )
    strings = union_of(rect(41 + 6 * i, 28, 2, 50) for i in range(4))
    return union(arms, yoke, body, strings)


def hermetic_sorginak() -> QPainterPath:
    """The lauburu, the Basque cross of four comma heads, in a ring."""

    def head() -> QPainterPath:
        return (
            circle(50, 30, 16)
            .subtracted(circle(58, 26, 8))
            .united(rect(46, 30, 8, 20))
            .intersected(rect(30, 10, 40, 40))
        )

    blade = union_of(rotate(head(), a) for a in (0, 90, 180, 270))
    return union(blade, circle(50, 50, 6))


def gorgiastic_cathars() -> QPainterPath:
    """The Gorgon's head, its hair of serpents."""
    face = circle(50, 52, 22)
    features = union(
        ellipse(39, 44, 8, 6),
        ellipse(53, 44, 8, 6),
        poly((50, 50), (46, 60), (54, 60)),
        rect(42, 64, 16, 3),
    )
    snakes = union_of(
        rotate(
            union(
                stroke(curve((50, 30), (46, 20), (50, 12), (54, 4), (50, 0)), 4),
                circle(50, 0, 3.5),
            ),
            a,
            50,
            52,
        )
        for a in range(-100, 101, 25)
    )
    return union(face.subtracted(features), snakes)


def sahirs() -> QPainterPath:
    """Solomon's signet ring, its seal a five-pointed star."""
    band = ring(50, 62, 26, 7)
    bezel = circle(50, 30, 20)
    seal = star(5, 14, 6, 50, 31)
    return union(band, bezel.subtracted(seal).subtracted(ring(50, 30, 17, 1.6)))


def nizari_mustajibs() -> QPainterPath:
    """A castle on its crag, the eagle's nest of Alamut."""
    crag = poly(
        (6, 94), (20, 66), (30, 72), (42, 54), (58, 60), (70, 50), (84, 70), (94, 94)
    )
    keep = union(rect(36, 30, 28, 30), *(rect(36 + 8 * i, 24, 5, 7) for i in range(4)))
    tower = union(
        rect(64, 18, 14, 40), rect(64, 12, 4, 7), rect(69, 12, 4, 7), rect(74, 12, 4, 7)
    )
    door = rrect(46, 44, 8, 16, 4)
    return union(crag, keep.subtracted(door), tower.subtracted(rect(69, 26, 4, 8)))


def soban_alchemists() -> QPainterPath:
    """A retort over its fire, its long neck bent down."""
    retort = union(
        circle(36, 52, 22),
        poly((50, 38), (92, 66), (88, 72), (46, 48)),
    ).subtracted(circle(36, 52, 15).intersected(rect(0, 54, 100, 20)))
    stand = union(rect(16, 76, 40, 4), bar(20, 80, 16, 94, 3), bar(52, 80, 56, 94, 3))
    fire = union(flame(36, 94, 10, 14), flame(28, 94, 7, 10), flame(44, 94, 7, 10))
    return union(retort, stand, fire)


def cult_of_dedun() -> QPainterPath:
    """A censer of the incense god, its smoke rising."""
    censer = union(
        circle(50, 56, 22).intersected(rect(28, 56, 44, 22)),
        rect(26, 52, 48, 6),
        rect(46, 76, 8, 10),
        rect(36, 86, 28, 6),
    )
    holes = union_of(circle(38 + 8 * i, 64, 2) for i in range(4))
    smoke = union(
        stroke(curve((50, 50), (40, 38), (50, 28), (60, 18), (50, 6)), 5),
        stroke(curve((40, 50), (30, 40), (36, 28)), 3.4),
        stroke(curve((60, 50), (70, 40), (64, 28)), 3.4),
    )
    return union(censer.subtracted(holes), smoke)


def lector_priests() -> QPainterPath:
    """The ankh, the sign of life the lector priests read over."""
    loop = ellipse(32, 6, 36, 42).subtracted(ellipse(41, 14, 18, 26))
    return union(loop, rect(14, 42, 72, 10), rect(44, 42, 12, 50))


def settuten_berber() -> QPainterPath:
    """Yaz, the Tifinagh letter of the free man."""
    return union(
        stroke(_path((28, 12), (36, 30), (50, 40), (64, 30), (72, 12)), 7),
        stroke(_path((28, 88), (36, 70), (50, 60), (64, 70), (72, 88)), 7),
        rect(46, 12, 8, 76),
    )


def settuten_tuareg() -> QPainterPath:
    """The Tuareg's Agadez cross: a horned ring over a lozenge, its arms
    ending in points."""
    top = union(
        ring(50, 26, 13, 6),
        poly((40, 16), (32, 6), (44, 12)),
        poly((60, 16), (68, 6), (56, 12)),
    )
    lozenge = poly((50, 40), (74, 64), (50, 94), (26, 64))
    arms = union(poly((12, 64), (26, 56), (26, 72)), poly((88, 64), (74, 56), (74, 72)))
    return union(
        top, lozenge.subtracted(poly((50, 52), (62, 64), (50, 80), (38, 64))), arms
    )


def imhergi() -> QPainterPath:
    """A Tuareg noble's leather shield, its spear behind it."""
    spear = union(bar(14, 90, 86, 10, 4), poly((86, 10), (74, 14), (82, 22)))
    shield = rrect(26, 18, 48, 64, 8)
    pattern = union(
        rect(48, 22, 4, 56), rect(30, 48, 40, 4), ring(50, 50, 10, 3),
        circle(36, 30, 3), circle(64, 30, 3), circle(36, 70, 3), circle(64, 70, 3),
    )  # fmt: skip
    return over(shield.subtracted(pattern), spear)


def inenden() -> QPainterPath:
    """The smiths' anvil and hammer."""
    anvil = union(
        poly((14, 30), (86, 30), (86, 40), (70, 46), (30, 46), (14, 38)),
        poly((40, 46), (60, 46), (64, 76), (36, 76)),
        rect(28, 76, 44, 10),
    )
    hammer = rotate(union(rect(52, 4, 30, 12), rect(64, 16, 6, 22)), 20, 66, 16)
    return union(anvil, hammer)


def bouda() -> QPainterPath:
    """A hyena's print, the shape the bouda go abroad in."""
    pad = vesica(50, 66, 34, 30).united(ellipse(33, 56, 34, 30))
    toes = union(
        ellipse(26, 30, 14, 18),
        ellipse(40, 18, 14, 18),
        ellipse(56, 18, 14, 18),
        ellipse(70, 30, 14, 18),
    )
    claws = union(
        poly((30, 30), (33, 18), (36, 30)),
        poly((44, 18), (47, 6), (50, 18)),
        poly((60, 18), (63, 6), (66, 18)),
        poly((74, 30), (77, 18), (80, 30)),
    )
    return union(pad, toes, claws)


def bedouin_hakima() -> QPainterPath:
    """A date palm, the desert's shade and food."""
    trunk = union_of(rect(46 - i * 0.2, 40 + 8 * i, 8, 7) for i in range(7))
    fronds = union_of(
        rotate(stroke(curve((50, 36), (64, 20), (88, 30)), 5), a, 50, 36)
        for a in (-40, 0, 40, 100, 140, 180)
    )
    dates = union(circle(44, 44, 3), circle(56, 44, 3), circle(50, 48, 3))
    return union(trunk, fronds, dates)


def murabitin() -> QPainterPath:
    """The domed tomb of a holy man."""
    dome = circle(50, 46, 22).intersected(rect(28, 22, 44, 24))
    finial = union(rect(48, 12, 4, 12), circle(50, 12, 3))
    walls = rect(22, 46, 56, 44)
    door = rrect(42, 62, 16, 28, 8)
    return union(dome, finial, walls.subtracted(door), rect(18, 44, 64, 5))


def sorginak() -> QPainterPath:
    """The eguzkilore, the sun-thistle nailed on Basque doors against
    the witches."""
    petals = union_of(
        rotate(poly((48, 4), (52, 4), (54, 30), (46, 30)), a) for a in range(0, 360, 15)
    )
    return union(
        petals,
        circle(50, 50, 24).subtracted(circle(50, 50, 18)),
        circle(50, 50, 14).subtracted(
            union_of(
                circle(
                    50 + 7 * math.cos(math.radians(a)),
                    50 + 7 * math.sin(math.radians(a)),
                    2,
                )
                for a in range(0, 360, 45)
            )
        ),
    )


def forest_paths() -> QPainterPath:
    """A path winding between the trees."""

    def tree(x: float, y: float, k: float) -> QPainterPath:
        return union(
            poly((x, y - 34 * k), (x + 14 * k, y - 12 * k), (x - 14 * k, y - 12 * k)),
            poly((x, y - 22 * k), (x + 18 * k, y), (x - 18 * k, y)),
            rect(x - 3 * k, y, 6 * k, 10 * k),
        )

    trees = union(tree(22, 56, 1.1), tree(78, 50, 1.0), tree(50, 34, 0.8))
    path = poly(
        (44, 94), (56, 94), (54, 80), (60, 70), (52, 62), (50, 62), (54, 70), (48, 80)
    )
    return union(trees, path)


def branchidae() -> QPainterPath:
    """The laurel wreath of Apollo's oracle at Didyma."""

    def branch() -> QPainterPath:
        stem = stroke(curve((48, 88), (14, 70), (22, 20)), 3)
        leaves = union_of(
            rotate(vesica(x, y, 16, 7), deg, x, y)
            for x, y, deg in (
                (30, 82, 160),
                (18, 66, 120),
                (16, 48, 100),
                (20, 32, 80),
                (36, 76, 20),
                (26, 58, 30),
                (24, 40, 40),
            )
        )
        return union(stem, leaves)

    return union(branch(), mirror(branch()))


def corrguineach() -> QPainterPath:
    """The crane, standing on one leg as the corrguinech curses."""
    body = union(ellipse(30, 36, 44, 22), poly((32, 44), (8, 52), (36, 52)))
    neck = stroke(curve((70, 42), (80, 28), (72, 18), (66, 10), (74, 6)), 5)
    head = union(circle(74, 7, 5), poly((77, 5), (96, 10), (77, 10)))
    leg = union(rect(48, 56, 3, 36), rect(40, 90, 18, 3))
    tucked = bar(50, 58, 40, 70, 3)
    return union(body, neck, head, leg, tucked).subtracted(circle(74, 6, 1.4))


def children_of_olympos() -> QPainterPath:
    """Zeus's thunderbolt, forked at both ends."""

    def fork() -> QPainterPath:
        return union(
            poly((46, 50), (54, 50), (52, 24), (50, 4), (48, 24)),
            poly((48, 40), (40, 30), (30, 8), (36, 30), (44, 46)),
            poly((52, 40), (60, 30), (70, 8), (64, 30), (56, 46)),
        )

    grip = union(ellipse(40, 42, 20, 16), rect(38, 46, 24, 8))
    bolt = union(fork(), rotate(fork(), 180), grip)
    return rotate(bolt, 30)


def amazon_sorceresses() -> QPainterPath:
    """The labrys, the double axe."""
    blade = QPainterPath()
    blade.moveTo(46, 22)
    blade.cubicTo(30, 22, 14, 14, 10, 8)
    blade.cubicTo(4, 24, 4, 48, 10, 60)
    blade.cubicTo(14, 52, 30, 46, 46, 46)
    blade.closeSubpath()
    return union(blade, mirror(blade), rect(46, 6, 8, 88), circle(50, 6, 5))


def augustan_brotherhood() -> QPainterPath:
    """A Roman standard: its wreath, discs and banner on the pole."""
    pole = rect(47, 8, 6, 86)
    wreath = ring(50, 16, 10, 4)
    discs = union_of(circle(50, 38 + 12 * i, 6) for i in range(3))
    bar_ = rect(30, 30, 40, 4)
    banner = rect(32, 70, 36, 18).subtracted(rect(36, 76, 28, 2.4))
    return union(pole, wreath, discs, bar_, banner)


def muspelli() -> QPainterPath:
    """Surtr's sword, its blade wrapped in fire."""
    blaze = union(
        ellipse(22, 46, 56, 32),
        _tongue([(32, 56), (16, 46), (30, 30), (18, 14)], 10),
        _tongue([(68, 56), (84, 46), (70, 30), (82, 14)], 10),
        _tongue([(40, 50), (30, 34), (44, 22), (36, 4)], 8),
        _tongue([(60, 50), (70, 34), (56, 22), (64, 4)], 8),
        _tongue([(26, 64), (10, 60), (12, 44), (6, 34)], 6),
        _tongue([(74, 64), (90, 60), (88, 44), (94, 34)], 6),
    )
    sword = union(
        poly((46, 76), (54, 76), (54, 18), (50, 4), (46, 18)),
        rect(30, 74, 40, 7),
        rect(46, 81, 8, 11),
        circle(50, 94, 4.5),
    )
    return over(sword, blaze, 2.4)


def soqotran_sorcerers() -> QPainterPath:
    """The dragon's blood tree of Soqotra."""
    crown = union(ellipse(10, 14, 80, 30), rect(10, 28, 80, 4))
    branches = union(
        bar(50, 66, 50, 30, 7),
        bar(50, 54, 30, 32, 5),
        bar(50, 54, 70, 32, 5),
        bar(36, 40, 22, 30, 4),
        bar(64, 40, 78, 30, 4),
    )
    trunk = poly((42, 92), (58, 92), (54, 60), (46, 60))
    drops = union(circle(44, 74, 2.4), circle(58, 80, 2.4))
    return union(
        crown.subtracted(rect(10, 28, 80, 2)), branches, trunk.subtracted(drops)
    )


def canaanite_necromancers() -> QPainterPath:
    """The sign of Tanit: a disc for the head, arms raised and a
    triangle for the body, on a base."""
    head = ring(50, 22, 11, 4)
    arms = union(
        rect(20, 36, 60, 6),
        stroke(curve((22, 39), (12, 34), (14, 14)), 5),
        stroke(curve((78, 39), (88, 34), (86, 14)), 5),
    )
    body = outline_tri(50, 40, 30, 82, 6)
    base = rect(18, 84, 64, 9)
    return union(head, arms, body, base)


def defixio_cults() -> QPainterPath:
    """A lead curse tablet, written over and pierced with a nail."""
    tablet = rotate(rect(22, 26, 56, 56), -8).subtracted(
        rotate(
            union_of(rect(28, 36 + 8 * i, 44 - 6 * (i % 2), 2.4) for i in range(5)), -8
        )
    )
    nail = union(poly((47, 20), (53, 20), (50, 92)), rrect(38, 10, 24, 8, 3))
    return over(nail, tablet)


def heronic_mechanici() -> QPainterPath:
    """Hero's aeolipile: a sphere spun by its jets of steam."""
    sphere = circle(50, 40, 22).subtracted(rect(28, 39, 44, 2.4))
    jets = union(
        rect(22, 36, 6, 8), rect(16, 26, 6, 18),
        rect(72, 36, 6, 8), rect(78, 36, 6, 18),
    )  # fmt: skip
    stand = union(rect(46, 62, 8, 10), poly((22, 72), (78, 72), (72, 92), (28, 92)))
    steam = union(
        stroke(curve((19, 22), (14, 12), (20, 6)), 3),
        stroke(curve((81, 58), (86, 66), (80, 72)), 3),
    )
    return union(sphere, jets, stand, steam)


def hyperborean_hymnists() -> QPainterPath:
    """Apollo's swan from the north, gliding on the water."""
    body = QPainterPath()
    body.moveTo(22, 64)
    body.cubicTo(22, 84, 70, 88, 88, 68)
    body.lineTo(94, 52)
    body.cubicTo(80, 62, 56, 60, 22, 64)
    body.closeSubpath()
    pts = [(28, 66), (14, 50), (16, 22), (36, 16), (30, 26)]
    neck = union_of(circle(*_bez(pts, t / 40), 6 - 2.6 * t / 40) for t in range(36))
    head = union(ellipse(18, 12, 18, 11), poly((20, 18), (8, 24), (20, 22)))
    wing = QPainterPath()
    wing.moveTo(40, 64)
    wing.cubicTo(42, 46, 62, 36, 86, 42)
    wing.cubicTo(80, 50, 80, 58, 70, 64)
    wing.closeSubpath()
    quills = union_of(bar(48 + 9 * i, 64, 58 + 9 * i, 46, 1.6) for i in range(3))
    water = union(rect(14, 88, 72, 3), rect(26, 94, 48, 3))
    swan = union(body, neck, head).subtracted(circle(22, 16, 1.6))
    return union(over(wing.subtracted(quills), swan, 1.6), water)


def storm_wizards() -> QPainterPath:
    """A thundercloud splitting with lightning."""
    cloud = union(
        circle(34, 34, 14),
        circle(54, 26, 18),
        circle(72, 36, 12),
        rrect(16, 32, 70, 18, 9),
    )
    bolt = poly((52, 52), (38, 74), (50, 74), (40, 96), (68, 66), (54, 66), (62, 52))
    return union(cloud.subtracted(stroke(bolt, 6)), bolt)


def hunters() -> QPainterPath:
    """Two boar spears crossed, their lugs below the blades."""
    spear = union(
        rect(48, 22, 4, 74),
        poly((50, 2), (58, 18), (50, 26), (42, 18)),
        rect(40, 28, 20, 4),
    ).subtracted(rect(49, 8, 2, 14))
    return union(rotate(spear, -30, 50, 56), rotate(spear, 30, 50, 56))


def fectores() -> QPainterPath:
    """An open shackle and its chain."""
    shackle = union(
        ring(36, 40, 20, 7).subtracted(rect(10, 40, 52, 30)),
        rect(16, 40, 7, 22),
        rect(49, 40, 7, 22),
        rrect(12, 60, 48, 10, 4),
    )
    chain = union(
        rrect(52, 64, 18, 10, 5).subtracted(rrect(56, 67, 10, 4, 2)),
        rrect(66, 66, 10, 18, 5).subtracted(rrect(69, 70, 4, 10, 2)),
        rrect(70, 80, 18, 10, 5).subtracted(rrect(74, 83, 10, 4, 2)),
    )
    return union(shackle, chain)


def _bez(points: Sequence[Point], t: float) -> Point:
    """A point along the smooth curve the points outline (de Casteljau)."""
    pts = list(points)
    while len(pts) > 1:
        pts = [
            (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            for a, b in pairwise(pts)
        ]
    return pts[0]


def outline_tri(
    cx: float, top: float, half: float, bottom: float, w: float
) -> QPainterPath:
    outer = poly((cx, top), (cx + half, bottom), (cx - half, bottom))
    inner = poly(
        (cx, top + 2.4 * w),
        (cx + half - 1.7 * w, bottom - w),
        (cx - half + 1.7 * w, bottom - w),
    )
    return outer.subtracted(inner)


def _tongue(points: Sequence[Point], w: float) -> QPainterPath:
    """A tongue of flame: a band along the curve, tapering to its tip."""
    return union_of(
        circle(*_bez(points, t / 40), w * (1 - t / 40) + 0.4) for t in range(41)
    )


#: Each tradition's figure, by its tradition_catalog.json id.
FIGURES: dict[str, Callable[[], QPainterPath]] = {
    "trad_elementalists": elementalists,
    "trad_folk_witches": folk_witches,
    "trad_gruagachan": gruagachan,
    "trad_learned_magicians": learned_magicians,
    "trad_nightwalkers": nightwalkers,
    "trad_vitkir": vitkir,
    "trad_ollamhain": ollamhain,
    "trad_volkhvy": volkhvy,
    "trad_wise_folk": wise_folk,
    "trad_borrowers": borrowers,
    "trad_faerie_doctors": faerie_doctors,
    "trad_homunculus_wizards": homunculus_wizards,
    "trad_caerflorons_line": caerflorons_line,
    "trad_wordsmiths": wordsmiths,
    "trad_ascetics": ascetics,
    "trad_cantores": cantores,
    "trad_sufis": sufis,
    "trad_baal_shem": baal_shem,
    "trad_kabbalists": kabbalists,
    "trad_sol_invictus": sol_invictus,
    "trad_priory_of_saint_nerius": priory_of_saint_nerius,
    "trad_zoroastrians": zoroastrians,
    "trad_karaites": karaites,
    "trad_celi_de": celi_de,
    "trad_mobeds": mobeds,
    "trad_hesychasts": hesychasts,
    "trad_society_of_cyprian_and_justina": society_of_cyprian_and_justina,
    "trad_kassalan_exorcists": kassalan_exorcists,
    "trad_baal_ov": baal_ov,
    "trad_luciferans": luciferans,
    "trad_strigae": strigae,
    "trad_witch_hammers": witch_hammers,
    "trad_dark_gnostics": dark_gnostics,
    "trad_dread_host": dread_host,
    "trad_mulhidun": mulhidun,
    "trad_damhadh_duidsan": damhadh_duidsan,
    "trad_ordo_vagorum": ordo_vagorum,
    "trad_witches_of_thessaly": witches_of_thessaly,
    "trad_cailleach_phiseogach": cailleach_phiseogach,
    "trad_stringla": stringla,
    "trad_paulicians": paulicians,
    "trad_beast_masters": beast_masters,
    "trad_tempestaria": tempestaria,
    "trad_scinnfolk": scinnfolk,
    "trad_columbae": columbae,
    "trad_donatores_requietis_aeternae": donatores_requietis_aeternae,
    "trad_pharmacopoeians": pharmacopoeians,
    "trad_lineage_of_pralix": lineage_of_pralix,
    "trad_rustic_magi": rustic_magi,
    "trad_hermetic_sahirs": hermetic_sahirs,
    "trad_seirenes": seirenes,
    "trad_hermetic_sorginak": hermetic_sorginak,
    "trad_gorgiastic_cathars": gorgiastic_cathars,
    "trad_sahirs": sahirs,
    "trad_nizari_mustajibs": nizari_mustajibs,
    "trad_soban_alchemists": soban_alchemists,
    "trad_cult_of_dedun": cult_of_dedun,
    "trad_lector_priests": lector_priests,
    "trad_settuten_berber": settuten_berber,
    "trad_settuten_tuareg": settuten_tuareg,
    "trad_imhergi": imhergi,
    "trad_inenden": inenden,
    "trad_bouda": bouda,
    "trad_bedouin_hakima": bedouin_hakima,
    "trad_murabitin": murabitin,
    "trad_sorginak": sorginak,
    "trad_forest_paths": forest_paths,
    "trad_branchidae": branchidae,
    "trad_corrguineach": corrguineach,
    "trad_children_of_olympos": children_of_olympos,
    "trad_amazon_sorceresses": amazon_sorceresses,
    "trad_augustan_brotherhood": augustan_brotherhood,
    "trad_muspelli": muspelli,
    "trad_soqotran_sorcerers": soqotran_sorcerers,
    "trad_canaanite_necromancers": canaanite_necromancers,
    "trad_defixio_cults": defixio_cults,
    "trad_heronic_mechanici": heronic_mechanici,
    "trad_hyperborean_hymnists": hyperborean_hymnists,
    "trad_storm_wizards": storm_wizards,
    "trad_hunters": hunters,
    "trad_fectores": fectores,
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
