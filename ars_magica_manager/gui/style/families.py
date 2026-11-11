"""How a theme paints a page: Scriptorum's look, and the three House
families' forms that the House themes are built on.

`Look.paint_page` is a Template Method: it lays down the steps every page
is painted in (the paper with its texture, the margins, the shading
toward the edges, the frame and its corners) and each step is a method a
family or a House fills in; `Look.tailpiece` is another, closing each
chapter on the House's sign between the family's rules (`tail_flank`).
Scriptorum's own look is the base class and paints as the app always
has. A House family (True Lineage, Mystery Cult, Societas) gives its
Houses one form: the frame, its corners, the rules under headings, the
headpiece, the rules flanking the sign and the heading type. A House theme is a family's subclass that adds only its
texture, and is given its colours (a Palette, data in style.palettes) and
its mark.

Everything is drawn here in code: rules, squares, rings and chevrons, and
a texture from a seeded random, so it is the same every time.

Text keeps its contrast on a House's texture: the texture is drawn
fainter behind the text, as faint as it must be for every text colour to
stand READABLE against the darkest of the page (vellum.worst_ground), and
whole in the margins round the page.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from functools import cache
from pathlib import Path

from PySide6.QtCore import QByteArray, QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
    QRegion,
)
from PySide6.QtSvg import QSvgRenderer

from ...style import fonts
from ...style.palettes import (
    EX_MISCELLANEA_MOTLEY,
    MERCERE_COIN,
    MERCERE_POTSHERD,
    READABLE,
    TEXT,
    VERDITIUS_GEM,
    VERDITIUS_GEM_DEEP,
    Palette,
    contrast,
    mixed,
)
from . import flourish
from .flourish import alpha, corners_of, fading, lozenge
from .vellum import TILE, laid_paper, shade, worst_ground

#: The kinds of page: the main window's body, a dialog's sheet, and a
#: page with no frame (a card's, a picture's).
WINDOW, DIALOG, PLAIN = "window", "dialog", "plain"
#: How far in from a page's edge its frame is drawn, and how wide the
#: margin a texture is kept whole in.
FRAME_INSET, MARGIN = 4.0, 30
#: The House's sign closing a chapter: the side it is drawn at, and how far
#: down the tailpiece its centre sits, in pixels.
MARK_SIDE, TAIL_Y = 30, 24
#: The Inspector's watermark: its widest side in pixels, and the most it
#: is let through (0 to 1).
WATERMARK_SIDE, WATERMARK = 220, 0.35


def watermark_ink(p: Palette) -> str:
    """The colour a watermark is drawn in on `p`'s page: the paper's sheen
    on a light page, its shade on a dark one, away from the text's ink."""
    return p["shadow"] if p.dark else p["paper-sheen"]


@cache
def _mark(path: Path, colour: str, side: int, ratio: float) -> QPixmap:
    """The SVG mark at `path` in `colour`, `side` pixels square."""
    svg = path.read_text(encoding="utf-8").replace("currentColor", colour)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    full = round(side * ratio)
    picture = QPixmap(full, full)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, full, full))
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return picture


@cache
def _sign(path: Path, colour: str, side: int, ratio: float) -> QPixmap:
    """The sign cut into the SVG mark at `path`, without the stone it is
    cut from, in `colour`, `side` pixels square. Each House's mark is a
    tile with its sign cut through it; the watermark wants only the sign,
    so the tile's ground goes and its holes are filled: the transparent
    pixels the outside cannot reach (a flood from the edge through every
    pixel short of solid) are the sign, less a border round the tile's
    edge and a ground lying along it."""
    tile = (
        _mark(path, colour, side, ratio)
        .toImage()
        .convertToFormat(QImage.Format.Format_ARGB32)
    )
    width, height = tile.width(), tile.height()
    # ARGB32 rows hold four bytes a pixel, blue first and alpha last.
    stride, raw = tile.bytesPerLine(), bytes(tile.constBits())
    alphas = [raw[y * stride + 4 * x + 3] for y in range(height) for x in range(width)]
    outside = bytearray(width * height)
    reach = [i for i in range(width * height) if _on_edge(i, width, height)]
    for i in reach:
        outside[i] = 1
    while reach:
        i = reach.pop()
        x, y = i % width, i // width
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height:
                j = ny * width + nx
                if not outside[j] and alphas[j] < 250:
                    outside[j] = 1
                    reach.append(j)
    # A border cut round the tile's edge (Criamon's square) is the stone's
    # edging, not its sign: a cut-out piece lying wholly in the band round
    # the tile's edge goes.
    inset_x, inset_y = width * 0.2, height * 0.2
    # Most marks are a solid tile with the sign cut out; Mercere's is drawn
    # the other way, in dark lines on a light tile, mostly unfilled.
    line_drawn = sum(1 for a in alphas if a >= 250) < width * height * 0.5
    for start in range(width * height):
        if outside[start] or alphas[start] >= 250:
            continue
        piece, reach = [start], [start]
        outside[start] = 2
        while reach:
            i = reach.pop()
            x, y = i % width, i // width
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    j = ny * width + nx
                    if not outside[j] and alphas[j] < 250:
                        outside[j] = 2
                        piece.append(j)
                        reach.append(j)
        central = any(
            inset_x <= i % width <= width - inset_x
            and inset_y <= i // width <= height - inset_y
            for i in piece
        )
        # On a mark drawn in dark lines on a light tile (Mercere's), a
        # piece lying largely along the tile's edge is the ground the sign
        # is drawn on, parted by the sign, not the sign.
        edging = sum(
            1
            for i in piece
            if not (
                inset_x <= i % width <= width - inset_x
                and inset_y <= i // width <= height - inset_y
            )
        )
        ground = line_drawn and edging > len(piece) * 0.3
        for i in piece:
            outside[i] = 3 if central and not ground else 1
    ink = QColor(colour)
    blue, green, red = ink.blue(), ink.green(), ink.red()
    pixels = bytearray(4 * width * height)
    for i, a in enumerate(alphas):
        if outside[i] != 1 and a < 255:
            pixels[4 * i : 4 * i + 4] = bytes((blue, green, red, 255 - a))
    sign = QImage(bytes(pixels), width, height, 4 * width, QImage.Format.Format_ARGB32)
    picture = QPixmap.fromImage(sign.copy())
    picture.setDevicePixelRatio(ratio)
    return picture


#: How far in from a mark's edge the frame scored round its tile reaches,
#: as a fraction of its side: a mark drawn in ink loses all it draws there.
TILE_FRAME = 0.065


@cache
def _drawn_sign(path: Path, colour: str, side: int, ratio: float) -> QPixmap:
    """The sign drawn in ink on the light tile of the SVG mark at `path`
    (Merinita's oak in its round, Verditius's ringed hand), without the
    frame scored round the tile: the ink as drawn, less every stroke within
    TILE_FRAME of the tile's edge, in `colour`, `side` pixels square."""
    tile = (
        _mark(path, colour, side, ratio)
        .toImage()
        .convertToFormat(QImage.Format.Format_ARGB32)
    )
    width, height = tile.width(), tile.height()
    band = TILE_FRAME * min(width, height)
    ink = QColor(colour)
    blue, green, red = ink.blue(), ink.green(), ink.red()
    stride, raw = tile.bytesPerLine(), bytes(tile.constBits())
    pixels = bytearray(4 * width * height)
    alphas = [raw[y * stride + 4 * x + 3] for y in range(height) for x in range(width)]

    def edge_distance(i: int) -> int:
        x, y = i % width, i // width
        return min(x, y, width - 1 - x, height - 1 - y)

    # The frame: its strokes near the edge, and all the ink joined to them
    # within reach of the edge (where the hand's wrist meets the frame).
    # Only solid ink joins: Merinita's round all but touches the frame,
    # parted from it by a soft pixel or two.
    solid = 235
    reach = [
        i
        for i in range(width * height)
        if alphas[i] >= solid and edge_distance(i) < band * 0.9
    ]
    frame = set(reach)
    while reach:
        i = reach.pop()
        x, y = i % width, i // width
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            j = ny * width + nx
            if (
                0 <= nx < width
                and 0 <= ny < height
                and j not in frame
                and alphas[j] >= solid
                and edge_distance(j) < band * 0.9
            ):
                frame.add(j)
                reach.append(j)
    # And the frame's soft edge, a pixel round it.
    for i in list(frame):
        x, y = i % width, i // width
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height:
                frame.add(ny * width + nx)
    for i in frame:
        alphas[i] = 0
    # The frame's corner pieces and its inner rule reach further in where
    # the tile is not square-cut: a stroke lying wholly near the edge goes
    # too.
    corner = 2.4 * band
    for start in range(width * height):
        if alphas[start] <= 0:
            continue
        piece, reach = [start], [start]
        alphas[start] = -alphas[start]
        while reach:
            i = reach.pop()
            x, y = i % width, i // width
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                j = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and alphas[j] > 0:
                    alphas[j] = -alphas[j]
                    piece.append(j)
                    reach.append(j)
        cornered = all(edge_distance(i) < corner for i in piece)
        for i in piece:
            if not cornered:
                pixels[4 * i : 4 * i + 4] = bytes((blue, green, red, -alphas[i]))
    sign = QImage(bytes(pixels), width, height, 4 * width, QImage.Format.Format_ARGB32)
    picture = QPixmap.fromImage(sign.copy())
    picture.setDevicePixelRatio(ratio)
    return picture


#: The least side a sign is cut out at: smaller, a mark's thin edges blur
#: into gaps the cut leaks through, so a small sign is cut at this size
#: and scaled down.
CUT_SIDE = 120


@cache
def _small(sign: QPixmap, side: int) -> QPixmap:
    """`sign` scaled smoothly down to `side` pixels square."""
    ratio = sign.devicePixelRatio()
    full = round(side * ratio)
    small = sign.scaled(
        full,
        full,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    small.setDevicePixelRatio(ratio)
    return small


@cache
def _lit_sign(path: Path, colour: str, side: int, ratio: float) -> QPixmap:
    """The light parts of the picture at `path` (the Order's sigil: gold
    serpents on a dark ground) as one colour, `colour`, `side` pixels
    square: each pixel let through as far as it is light, so the dark
    ground and the outlines fall away and only the figure is left."""
    full = round(side * ratio)
    picture = (
        QImage(str(path))
        .scaled(
            full,
            full,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        .convertToFormat(QImage.Format.Format_ARGB32)
    )
    width, height = picture.width(), picture.height()
    stride, raw = picture.bytesPerLine(), bytes(picture.constBits())
    ink = QColor(colour)
    blue, green, red = ink.blue(), ink.green(), ink.red()
    pixels = bytearray(4 * width * height)
    for y in range(height):
        for x in range(width):
            b, g, r, a = raw[y * stride + 4 * x : y * stride + 4 * x + 4]
            light = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            lit = min(1.0, max(0.0, (light - 0.3) / 0.45))
            i = 4 * (y * width + x)
            pixels[i : i + 4] = bytes((blue, green, red, round(a * lit)))
    sign = QImage(bytes(pixels), width, height, 4 * width, QImage.Format.Format_ARGB32)
    result = QPixmap.fromImage(sign.copy())
    result.setDevicePixelRatio(ratio)
    return result


def _on_edge(i: int, width: int, height: int) -> bool:
    x, y = i % width, i // width
    return x in (0, width - 1) or y in (0, height - 1)


def wrapped(
    painter: QPainter, draw_at: QPointF, draw: Callable[[QPainter, QPointF], None]
) -> None:
    """Call `draw(painter, origin)` at `draw_at` and again a tile across
    each edge, so a texture's strokes meet seamlessly from tile to tile."""
    for dx in (-TILE, 0, TILE):
        for dy in (-TILE, 0, TILE):
            draw(painter, draw_at + QPointF(dx, dy))


class Look:
    """Scriptorum's look: laid paper and printer's ornaments in gilt, no
    frame on the window, a ruled edge and corner flourishes on a dialog.
    The base the House families vary step by step."""

    #: The section headings' typeface.
    heading_family: str = fonts.SERIF
    #: The big titles' typeface (a sheet's name, a dialog's title).
    title_family: str = fonts.SERIF
    #: Whether a heading asked for in small capitals is set in them (not
    #: blackletter, whose made-up small capitals are hard to read).
    small_caps = True
    #: Whether every section heading is set in small capitals, asked or not.
    always_small_caps = False
    #: The palette key a section heading is inked in.
    heading_ink = "foreground"
    #: Whether a name's or a passage's initial is painted as a small
    #: illuminated letter: burnished gold on a quartered ground in the
    #: House's pigments (palettes.HOUSE_PIGMENTS), not the rubric's colour
    #: with a gilt edge.
    quartered_initials = False
    #: Whether a name's or a passage's initial is a plain letter in the
    #: heading's ink, with no decoration at all.
    plain_initials = False
    #: Whether the form's own pieces (its frame) are drawn on the window.
    frames_window = False
    #: Whether the House's sign is drawn in ink on a light tile (and so is
    #: watermarked as drawn, less the tile's frame), not cut through a
    #: dark one.
    sign_drawn = False

    def __init__(self, mark: Path | None = None, watermark: Path | None = None) -> None:
        #: The House's mark (an SVG), closing each chapter and watermarked
        #: in the Inspector, or None.
        self.mark = mark
        #: A picture watermarked in the Inspector by its light parts when
        #: there is no House mark (Scriptorum's: the Order's sigil), or
        #: None.
        self.watermark = watermark
        self._tiles: dict[str, QPixmap] = {}
        self._margins: dict[str, QPixmap] = {}
        self._watermarks: dict[str, float] = {}

    # -- the template method -------------------------------------------------

    def paint_page(
        self, painter: QPainter, rect: QRectF, p: Palette, kind: str
    ) -> None:
        """Paint a page of `kind` (WINDOW, DIALOG or PLAIN) filling `rect`:
        the paper, its margins, the shade toward its edges, then (unless
        it is PLAIN) the frame and its corners. The House's sign is not on
        the frame: it closes each chapter, in the tailpiece."""
        painter.drawTiledPixmap(rect.toRect(), self.tile(p))
        self.paint_margins(painter, rect, p)
        self.paint_edges(painter, rect, p)
        if kind == PLAIN or (kind == WINDOW and not self.frames_window):
            return
        inside = rect.adjusted(FRAME_INSET, FRAME_INSET, -FRAME_INSET, -FRAME_INSET)
        self.frame(painter, inside, p)
        self.corners(painter, inside, p, 18)

    # -- the steps -----------------------------------------------------------

    def tile(self, p: Palette) -> QPixmap:
        """A tile of this look's paper in `p`, with its texture as strong
        as text allows (made once per palette)."""
        if p.name not in self._tiles:
            self._tiles[p.name] = QPixmap.fromImage(self.paper(p))
        return self._tiles[p.name]

    def paper(self, p: Palette) -> QImage:
        """The paper's image: laid paper, and the texture over it at the
        strongest that keeps every text colour readable on it."""
        base = laid_paper(p)
        if not self.textured():
            return base
        strength = 1.0
        while strength >= 0.05:
            image = base.copy()
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.texture(painter, p, strength)
            painter.end()
            if readable(image, p):
                return image
            strength *= 0.7
        # No strength is faint enough: the texture stays in the margins.
        return base

    def textured(self) -> bool:
        """Whether this look lays a texture over its paper."""
        return type(self).texture is not Look.texture

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        """The House's texture over one tile, at `strength` (1 whole, less
        fainter). Scriptorum has none."""

    def paint_margins(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        """The texture whole, in the margins round the page (where no
        text sits)."""
        if not self.textured():
            return
        if p.name not in self._margins:
            image = QImage(TILE, TILE, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(Qt.GlobalColor.transparent)
            margin_painter = QPainter(image)
            margin_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.texture(margin_painter, p, 1.0)
            margin_painter.end()
            self._margins[p.name] = QPixmap.fromImage(image)
        whole = rect.toRect()
        inner = whole.adjusted(MARGIN, MARGIN, -MARGIN, -MARGIN)
        painter.save()
        painter.setClipRegion(QRegion(whole).subtracted(QRegion(inner)))
        painter.drawTiledPixmap(whole, self._margins[p.name])
        painter.restore()

    def paint_edges(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        """The page darker toward its edges."""
        edges = QRadialGradient(rect.center(), max(rect.width(), rect.height()) * 0.75)
        edges.setColorAt(0.6, shade(p["shadow"], 0))
        edges.setColorAt(1.0, shade(p["shadow"], 120 if p.dark else 60))
        painter.fillRect(rect, edges)

    def frame(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        """The frame ruled round a page: one fine rule."""
        painter.setPen(QPen(QColor(p["rule"]), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect.adjusted(-3.5, -3.5, 3.5, 3.5))

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        """The ornament in each corner of `rect` (a frame's, a card's)."""
        flourish.corner_flourishes(painter, rect, p, arm)

    def worn(self, frame: QRectF) -> QRegion | None:
        """What a frame ruled on `frame` (the Inspector's, a page's) keeps
        of itself where the House's page is worn, as a clip; None, kept
        whole, unless the House's frames are scraped."""
        return None

    def sign(self, colour: str, side: int) -> QPixmap:
        """The House's sign alone, cut from its mark's tile (or, for a mark
        drawn in ink, without the tile's frame), in `colour`, `side` pixels
        square. Only a look with a mark has one."""
        assert self.mark is not None
        cut = _drawn_sign if self.sign_drawn else _sign
        if side >= CUT_SIDE:
            return cut(self.mark, colour, side, 2.0)
        return _small(cut(self.mark, colour, CUT_SIDE, 2.0), side)

    def inspector_mark(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        """The House's mark watermarked large at the foot of the Inspector
        (`rect` inside its frame), as a watermark shows in a sheet held to
        the light: paler than the page on a light theme, deeper on a dark
        one, so text over it only stands out the more. Scriptorum, with no
        House, shows the Order's sigil the same way."""
        if self.mark is None and self.watermark is None:
            return
        side = round(min(rect.width() * 0.6, WATERMARK_SIDE))
        opacity = self.watermark_opacity(p)
        if side < 60 or opacity <= 0:
            return
        if self.mark is not None:
            sign = self.sign(watermark_ink(p), side)
        else:
            assert self.watermark is not None
            sign = _lit_sign(self.watermark, watermark_ink(p), side, 2.0)
        corner = QPointF(rect.center().x() - side / 2, rect.bottom() - side - 26)
        painter.save()
        painter.setOpacity(opacity)
        painter.drawPixmap(corner, sign)
        painter.restore()

    def watermark_opacity(self, p: Palette) -> float:
        """How strongly the Inspector's watermark is drawn on `p`'s page:
        WATERMARK, or less if a text colour would fall short of READABLE
        over it (0 when even a trace would)."""
        if p.name not in self._watermarks:
            # The Inspector's leaf: the page's paper with the panel over it.
            ground = mixed(
                worst_ground(self.tile(p).toImage(), p.dark), p["panel"], 70 / 255
            )
            found = 0.0
            for step in range(round(WATERMARK * 100), 0, -1):
                under = mixed(ground, watermark_ink(p), step / 100)
                if all(contrast(p[key], under) >= READABLE for key in TEXT):
                    found = step / 100
                    break
            self._watermarks[p.name] = found
        return self._watermarks[p.name]

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        """The rule under a heading."""
        flourish.heading_rule(painter, width, cy, p)

    def short_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        """The short rule under a title."""
        flourish.short_rule(painter, width, cy, p)

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        """The headpiece's centre, when nothing (a medallion) sits there."""
        flourish.headpiece_centre(painter, width, cy, p)

    def band(
        self, painter: QPainter, width: float, cy: float, inner: float, p: Palette
    ) -> None:
        """The headpiece's band, running out from `inner` beside the centre."""
        flourish.band(painter, width, cy, inner, p)

    def tailpiece(self, painter: QPainter, width: float, p: Palette) -> None:
        """The ornament closing a chapter: the House's sign in its heading
        ink between the family's rules (tail_flank), or, with no House
        (Scriptorum), three leaves narrowing to a point."""
        if self.mark is None:
            flourish.tailpiece(painter, width, p)
            return
        cx = width / 2
        self.tail_flank(painter, cx, TAIL_Y, MARK_SIDE / 2 + 8, p)
        self.tail_sign(painter, QPointF(cx, TAIL_Y), p)

    def tail_flank(
        self, painter: QPainter, cx: float, cy: float, inner: float, p: Palette
    ) -> None:
        """The rules either side of the sign in the tailpiece, running out
        from `inner` beside its centre: fine rules fading."""
        for side in (-1, 1):
            near, far = cx + side * inner, cx + side * (inner + 130)
            painter.setPen(fading(p["accent"], near, far, 1.0))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))

    def tail_sign(self, painter: QPainter, centre: QPointF, p: Palette) -> None:
        """The House's sign closing a chapter, centred on `centre`."""
        side = MARK_SIDE
        painter.drawPixmap(
            centre - QPointF(side / 2, side / 2), self.sign(p["heading"], side)
        )


def readable(image: QImage, p: Palette) -> bool:
    """Whether every text colour of `p` stands READABLE against the worst
    ground of `image`."""
    ground = worst_ground(image, p.dark)
    return all(contrast(p[key], ground) >= READABLE for key in TEXT)


def _square(painter: QPainter, x: float, y: float, r: float, colour: str) -> None:
    """A small square block centred on (x, y), with a hollow at its heart."""
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(colour))
    painter.drawRect(QRectF(x - r, y - r, 2 * r, 2 * r))
    if r >= 3:
        painter.setBrush(alpha(colour, 70))
        painter.drawRect(QRectF(x - r / 3, y - r / 3, 2 * r / 3, 2 * r / 3))


class TrueLineage(Look):
    """The True Lineages' form: an unbroken line, as their magi are
    trained from master to apprentice back to the founder. Square-cut
    and Roman: a double rule framing the page with square blocks at its
    corners, a meander running through the headpiece, square ornaments in
    place of leaves, and headings in inscriptional capitals (Cinzel)."""

    heading_family = title_family = fonts.INSCRIPTION
    frames_window = True

    def frame(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        gilt = p["accent"]
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(gilt), 1.4))
        painter.drawRect(rect)
        painter.setPen(QPen(alpha(gilt, 170), 0.6))
        painter.drawRect(rect.adjusted(4, 4, -4, -4))

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        gilt = p["accent"]
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for x, y, sx, sy in corners_of(rect.adjusted(2, 2, -2, -2)):
            painter.setPen(QPen(QColor(gilt), 1.1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            bracket = QPainterPath(QPointF(x + sx * arm, y))
            bracket.lineTo(x, y)
            bracket.lineTo(x, y + sy * arm)
            painter.drawPath(bracket)
            _square(painter, x + sx * 3, y + sy * 3, 3.2, gilt)
            _square(painter, x + sx * (arm + 2), y, 1.4, gilt)
            _square(painter, x, y + sy * (arm + 2), 1.4, gilt)

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        _square(painter, 8, cy, 3.6, gilt)
        _square(painter, 17, cy, 1.6, gilt)
        start = 24
        painter.setPen(fading(gilt, start, width * 0.8, 1.4))
        painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))
        painter.setPen(fading(gilt, start, width * 0.55, 0.6))
        painter.drawLine(QPointF(start, cy + 3), QPointF(width * 0.55, cy + 3))

    def short_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        cx = width / 2
        _square(painter, cx, cy, 4, gilt)
        for side in (-1, 1):
            _square(painter, cx + side * 11, cy, 1.6, gilt)
            near, far = cx + side * 18, cx + side * 210
            painter.setPen(fading(gilt, near, far, 1.2))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        cx = width / 2
        _square(painter, cx, cy, 7, gilt)
        for side in (-1, 1):
            _square(painter, cx + side * 20, cy, 4, gilt)
            _square(painter, cx + side * 32, cy, 2, gilt)

    def band(
        self, painter: QPainter, width: float, cy: float, inner: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        cx = width / 2
        for side in (-1, 1):
            _square(painter, cx + side * inner, cy, 2.2, gilt)
            near, far = cx + side * (inner + 10), cx + side * (width / 2 - 6)
            painter.setPen(fading(gilt, near, far, 0.8))
            for dy in (-6, 6):
                painter.drawLine(QPointF(near, cy + dy), QPointF(far, cy + dy))
            # A meander between the rules: one key every 16 pixels.
            x = near
            painter.setBrush(Qt.BrushStyle.NoBrush)
            while (far - x) * side > 16:
                left = 1 - abs(x - near) / abs(far - near)
                painter.setPen(QPen(alpha(gilt, int(255 * left**1.2)), 1.1))
                key = QPainterPath(QPointF(x, cy + 3))
                for dx, dy in (
                    (0, -6),
                    (side * 10, -6),
                    (side * 10, 0),
                    (side * 5, 0),
                    (side * 5, -3),
                ):
                    key.lineTo(x + dx, cy + 3 + dy)
                key.moveTo(x + side * 10, cy + 3)
                key.lineTo(x + side * 16, cy + 3)
                painter.drawPath(key)
                x += side * 16

    def tail_flank(
        self, painter: QPainter, cx: float, cy: float, inner: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        for side in (-1, 1):
            _square(painter, cx + side * inner, cy, 2.6, gilt)
            near, far = cx + side * (inner + 8), cx + side * (inner + 130)
            painter.setPen(fading(gilt, near, far, 1.0))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))


def _ring(
    painter: QPainter, x: float, y: float, r: float, colour: QColor, width: float
) -> None:
    painter.setPen(QPen(colour, width))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QPointF(x, y), r, r)


def _loop(painter: QPainter, cx: float, cy: float, half: float, colour: QColor) -> None:
    """A loop of the infinite (a figure of eight on its side), `half`
    from its centre to each end."""
    path = QPainterPath()
    for i in range(65):
        t = math.tau * i / 64
        d = 1 + math.sin(t) ** 2
        x, y = half * math.cos(t) / d, half * math.sin(t) * math.cos(t) / d
        if i == 0:
            path.moveTo(cx + x, cy + y)
        else:
            path.lineTo(cx + x, cy + y)
    painter.setPen(QPen(colour, 1.2))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)


class MysteryCult(Look):
    """The Mystery Cults' form: the circle an initiate is brought inside.
    Round and closed: a frame with rounded corners and a ring at each,
    chains of linked rings through the headpiece, a loop of the infinite
    under a title, and headings in Uncial Antiqua."""

    heading_family = title_family = fonts.DISPLAY
    frames_window = True

    def frame(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(p["accent"]), 1.2))
        painter.drawRoundedRect(rect, 12, 12)
        painter.setPen(QPen(alpha(p["accent"], 110), 0.6))
        painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), 9, 9)

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        gilt = QColor(p["accent"])
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for x, y, sx, sy in corners_of(rect.adjusted(2, 2, -2, -2)):
            _ring(painter, x + sx * 6, y + sy * 6, 4, gilt, 1.1)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gilt)
            painter.drawEllipse(QPointF(x + sx * 6, y + sy * 6), 1.2, 1.2)
            painter.drawEllipse(QPointF(x + sx * (arm + 4), y + sy * 1), 1.1, 1.1)
            painter.drawEllipse(QPointF(x + sx * 1, y + sy * (arm + 4)), 1.1, 1.1)

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        _ring(painter, 9, cy, 4.5, QColor(gilt), 1.2)
        _ring(painter, 18, cy, 2.5, QColor(gilt), 1.0)
        start = 26
        painter.setPen(fading(gilt, start, width * 0.8, 1.2))
        painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))

    def short_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        cx = width / 2
        _loop(painter, cx, cy, 13, QColor(gilt))
        for side in (-1, 1):
            near, far = cx + side * 20, cx + side * 210
            painter.setPen(fading(gilt, near, far, 1.1))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        cx = width / 2
        _ring(painter, cx, cy, 11, gilt, 1.3)
        _loop(painter, cx, cy, 9, gilt)
        for side in (-1, 1):
            _ring(painter, cx + side * 24, cy, 5, gilt, 1.1)
            _ring(painter, cx + side * 35, cy, 3, gilt, 1.0)

    def band(
        self, painter: QPainter, width: float, cy: float, inner: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        cx = width / 2
        for side in (-1, 1):
            near, far = cx + side * inner, cx + side * (width / 2 - 6)
            x = near
            while (far - x) * side > 0:
                left = 1 - abs(x - near) / abs(far - near)
                _ring(painter, x, cy, 4.5, alpha(gilt, int(255 * left**1.2)), 1.0)
                x += side * 7

    def tail_flank(
        self, painter: QPainter, cx: float, cy: float, inner: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        for side in (-1, 1):
            _ring(painter, cx + side * inner, cy, 3, gilt, 1.0)
            near, far = cx + side * (inner + 7), cx + side * (inner + 130)
            painter.setPen(fading(p["accent"], near, far, 1.0))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))


def _chevron(
    painter: QPainter, x: float, y: float, r: float, side: int, colour: QColor
) -> None:
    """A chevron at (x, y) pointing `side` (1 right, -1 left)."""
    painter.setPen(QPen(colour, 1.3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    path = QPainterPath(QPointF(x - side * r, y - r))
    path.lineTo(x, y)
    path.lineTo(x - side * r, y + r)
    painter.drawPath(path)


#: How far apart the Societates' pennants hang on their cord, in pixels.
PENNANT_STEP = 18.0


def _pennant(painter: QPainter, x: float, top: float, colour: QColor) -> None:
    """A small swallow-tailed pennant hanging from (x, top): a short
    banner with a notch cut up into its foot."""
    half, length, notch = 3.6, 13.0, 4.5
    path = QPainterPath(QPointF(x - half, top))
    path.lineTo(x + half, top)
    path.lineTo(x + half, top + length)
    path.lineTo(x, top + length - notch)
    path.lineTo(x - half, top + length)
    path.closeSubpath()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(colour)
    painter.drawPath(path)


class Societas(Look):
    """The Societates' form: a gathering of like minds who meet as
    equals and contend. Angular and cut: a frame whose corners are
    chamfered off with a lozenge at each cut, chevrons in place of leaves,
    a row of swallow-tailed pennants in the House's livery hung from a
    cord across the headpiece, as a tourney's lists are hung, big titles
    in blackletter (Manufacturing Consent) and section headings in the
    book face's small capitals, in the House's heading colour."""

    title_family = fonts.TITLE
    always_small_caps = True
    heading_ink = "heading"
    frames_window = True
    #: The palette keys the pennants are dyed in, in turn.
    livery: tuple[str, ...] = ("heading", "accent")

    def pennant(self, p: Palette, i: int) -> str:
        """The colour the `i`th pennant out from the centre is dyed: the
        livery's colours in turn."""
        return p[self.livery[i % len(self.livery)]]

    def frame(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        cut = 10.0
        path = QPainterPath(QPointF(rect.left() + cut, rect.top()))
        for x, y in (
            (rect.right() - cut, rect.top()),
            (rect.right(), rect.top() + cut),
            (rect.right(), rect.bottom() - cut),
            (rect.right() - cut, rect.bottom()),
            (rect.left() + cut, rect.bottom()),
            (rect.left(), rect.bottom() - cut),
            (rect.left(), rect.top() + cut),
        ):
            path.lineTo(x, y)
        path.closeSubpath()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(p["accent"]), 1.3))
        painter.drawPath(path)

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        gilt = QColor(p["accent"])
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for x, y, sx, sy in corners_of(rect.adjusted(2, 2, -2, -2)):
            painter.setPen(QPen(gilt, 1.1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            bracket = QPainterPath(QPointF(x + sx * arm, y))
            bracket.lineTo(x + sx * 6, y)
            bracket.lineTo(x, y + sy * 6)
            bracket.lineTo(x, y + sy * arm)
            painter.drawPath(bracket)
            self.corner_piece(painter, x, y, sx, sy, p)

    def corner_piece(
        self, painter: QPainter, x: float, y: float, sx: int, sy: int, p: Palette
    ) -> None:
        """The piece set at a corner's cut, (x, y) the corner and (sx, sy)
        the way into the page: a lozenge. It stays within the frame's
        margin, clear of any box on the page."""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["accent"]))
        lozenge(painter, x + sx * 6, y + sy * 6, 2.6)

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        _chevron(painter, 8, cy, 4, 1, QColor(gilt))
        _chevron(painter, 14, cy, 4, 1, QColor(gilt))
        start = 22
        painter.setPen(fading(gilt, start, width * 0.8, 1.4))
        painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))
        painter.setPen(fading(gilt, start, width * 0.55, 0.6))
        painter.drawLine(QPointF(start, cy + 3), QPointF(width * 0.55, cy + 3))

    def short_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        cx = width / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(gilt))
        lozenge(painter, cx, cy, 4.5)
        for side in (-1, 1):
            _chevron(painter, cx + side * 10, cy, 3.5, -side, QColor(gilt))
            near, far = cx + side * 18, cx + side * 210
            painter.setPen(fading(gilt, near, far, 1.2))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        cx = width / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gilt)
        lozenge(painter, cx, cy, 8)
        for side in (-1, 1):
            _chevron(painter, cx + side * 18, cy, 6, -side, gilt)
            _chevron(painter, cx + side * 28, cy, 6, -side, gilt)

    def band(
        self, painter: QPainter, width: float, cy: float, inner: float, p: Palette
    ) -> None:
        cx = width / 2
        top = cy - 7
        for side in (-1, 1):
            near, far = cx + side * (inner + 4), cx + side * (width / 2 - 6)
            # The cord, sagging a little between the points it is tied at.
            cord = QPainterPath(QPointF(near, top))
            x = near
            while (far - x) * side > 0:
                step = side * min(PENNANT_STEP, abs(far - x))
                cord.quadTo(x + step / 2, top + 5, x + step, top)
                x += step
            painter.setPen(fading(p["accent"], near, far, 1.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(cord)
            # A pennant at each tie, dyed in the livery's colours in turn.
            x, i = near + side * PENNANT_STEP, 0
            while (far - x) * side > PENNANT_STEP / 2:
                left = 1 - abs(x - near) / abs(far - near)
                ink = self.pennant(p, i)
                _pennant(painter, x, top, alpha(ink, int(255 * left**1.2)))
                x += side * PENNANT_STEP
                i += 1

    def tail_flank(
        self, painter: QPainter, cx: float, cy: float, inner: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        for side in (-1, 1):
            _chevron(painter, cx + side * inner, cy, 3.5, -side, gilt)
            near, far = cx + side * (inner + 7), cx + side * (inner + 130)
            painter.setPen(fading(p["accent"], near, far, 1.0))
            painter.drawLine(QPointF(near, cy), QPointF(far, cy))


# -- the House themes' own textures ------------------------------------------


def _spiral(
    painter: QPainter, at: QPointF, radius: float, turns: float, way: int = 1
) -> None:
    """A spiral from `at` out to `radius` in `turns` turns, clockwise on
    screen (`way` -1 the other way), in the painter's pen."""
    path = QPainterPath(at)
    steps = round(turns * 36)
    for i in range(1, steps + 1):
        t = i / steps
        angle = way * math.tau * turns * t
        path.lineTo(
            at + QPointF(radius * t * math.cos(angle), radius * t * math.sin(angle))
        )
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)


class Criamon(MysteryCult):
    """House Criamon: the dark of the Cave of Twisting Shadows, its walls
    marked as its magi mark their skin: loops of the infinite, rings within
    rings for the circle of time, and small spirals, worn so faint into the
    rock they are half lost in its dark."""

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(13)
        ink = p["paper-sheen"]
        for _ in range(28):
            centre = QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE))
            kind = chance.choice(("loop", "rings", "spiral"))
            size = chance.uniform(10, 34) if kind != "rings" else chance.uniform(30, 90)
            opacity = round(chance.randint(14, 26) * strength * 0.5)
            colour = shade(ink, opacity)

            def mark(
                at_painter: QPainter,
                at: QPointF,
                kind: str = kind,
                size: float = size,
                colour: QColor = colour,
            ) -> None:
                at_painter.setPen(QPen(colour, 0.9))
                at_painter.setBrush(Qt.BrushStyle.NoBrush)
                if kind == "loop":
                    _loop(at_painter, at.x(), at.y(), size, colour)
                elif kind == "rings":
                    for ring in (1.0, 0.72, 0.44):
                        at_painter.drawEllipse(at, size * ring, size * ring)
                else:
                    _spiral(at_painter, at, size, 2.5)

            wrapped(painter, centre, mark)


class Tytalus(Societas):
    """House Tytalus: Fudarus's storm-slate sky, the sea mist rolling over
    it in banks and fine rain driven slantwise through it: weather in the
    page itself, the conflict the House grows by."""

    quartered_initials = True

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(17)

        # The sea mist: broad, soft banks, darker and paler, drifting.
        def bank(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            reach = rng.uniform(80, 170)
            ink = p["paper-sheen"] if rng.random() < 0.6 else p["shadow"]
            glow = QRadialGradient(at, reach)
            glow.setColorAt(0, shade(ink, round(rng.randint(14, 24) * strength)))
            glow.setColorAt(1, shade(ink, 0))
            at_painter.setPen(Qt.PenStyle.NoPen)
            at_painter.setBrush(QBrush(glow))
            at_painter.drawEllipse(at, reach, reach * 0.4)

        _wrapped_marks(painter, chance, 9, bank)
        # The storm: fine rain driven slantwise.
        for _ in range(110):
            x, y = chance.uniform(0, TILE), chance.uniform(0, TILE)
            length = chance.uniform(18, 60)
            pen = QPen(
                shade(p["paper-sheen"], round(chance.randint(8, 16) * strength)), 0.6
            )

            def rain(
                at_painter: QPainter,
                at: QPointF,
                length: float = length,
                pen: QPen = pen,
            ) -> None:
                at_painter.setPen(pen)
                at_painter.drawLine(at, at + QPointF(length * 0.45, length))

            wrapped(painter, QPointF(x, y), rain)


class Bonisagus(TrueLineage):
    """House Bonisagus: a theorist's vellum, laid over with the faint
    construction lines of geometry, circles struck with compasses and the
    straight lines through their centres, as Bonisagus worked out the
    Hermetic theory of magic."""

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(11)
        ink = p["paper-fleck"]
        for _ in range(9):
            centre = QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE))
            radius = chance.uniform(40, 150)
            opacity = round(chance.randint(20, 34) * strength)
            pen = QPen(shade(ink, opacity), 0.8)

            def figure(
                at_painter: QPainter,
                at: QPointF,
                radius: float = radius,
                pen: QPen = pen,
            ) -> None:
                at_painter.setPen(pen)
                at_painter.setBrush(Qt.BrushStyle.NoBrush)
                at_painter.drawEllipse(at, radius, radius)
                # A diameter and the compass point's prick at the centre.
                at_painter.drawLine(at - QPointF(radius, 0), at + QPointF(radius, 0))
                at_painter.drawEllipse(at, 1.2, 1.2)

            wrapped(painter, centre, figure)
        # Long straight construction lines, struck across the sheet.
        for _ in range(5):
            y = chance.uniform(0, TILE)
            opacity = round(chance.randint(14, 24) * strength)
            painter.setPen(QPen(shade(ink, opacity), 0.6))
            painter.drawLine(QPointF(0, y), QPointF(TILE, y))


#: The strokes the incised letters on Guernicus's marble are built from,
#: as (x0, y0, x1, y1) in a letter's box of 1 by 1.4: stems, bars and
#: diagonals, put together at random so they read as Roman capitals
#: without ever spelling a word.
_INCISED = (
    (0.0, 0.0, 0.0, 1.4),
    (1.0, 0.0, 1.0, 1.4),
    (0.0, 0.0, 1.0, 0.0),
    (0.0, 0.7, 0.8, 0.7),
    (0.0, 1.4, 1.0, 1.4),
    (0.0, 0.0, 0.5, 1.4),
    (1.0, 0.0, 0.5, 1.4),
    (0.0, 1.4, 1.0, 0.0),
)


class Guernicus(TrueLineage):
    """House Guernicus: a Roman law tablet's marble, crossed by a few long,
    soft veins, with lines of incised capitals as on the tablets the Code
    might be cut on (invented letters, never words)."""

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(19)
        ink = p["paper-fleck"]
        # The veins: long curves wandering across the stone.
        for _ in range(6):
            start = QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE))
            points = [start]
            for _ in range(4):
                last = points[-1]
                points.append(
                    last + QPointF(chance.uniform(40, 110), chance.uniform(-50, 50))
                )
            pen = QPen(shade(ink, round(chance.randint(16, 28) * strength)), 0.9)

            def vein(
                at_painter: QPainter,
                at: QPointF,
                points: list[QPointF] = points,
                pen: QPen = pen,
            ) -> None:
                shift = at - points[0]
                path = QPainterPath(points[0] + shift)
                for a, b in zip(points[1::2], points[2::2], strict=False):
                    path.quadTo(a + shift, b + shift)
                at_painter.setPen(pen)
                at_painter.setBrush(Qt.BrushStyle.NoBrush)
                at_painter.drawPath(path)

            wrapped(painter, start, vein)
        # Lines of incised capitals.
        for _ in range(4):
            x, y = chance.uniform(0, TILE), chance.uniform(0, TILE)
            size = chance.uniform(7, 11)
            pen = QPen(shade(ink, round(chance.randint(20, 32) * strength)), 1.0)
            letters = [
                chance.sample(_INCISED, chance.randint(2, 3))
                for _ in range(chance.randint(6, 11))
            ]

            def inscription(
                at_painter: QPainter,
                at: QPointF,
                size: float = size,
                pen: QPen = pen,
                letters: list[list[tuple[float, ...]]] = letters,
            ) -> None:
                at_painter.setPen(pen)
                for i, strokes in enumerate(letters):
                    left = at.x() + i * size * 1.5
                    for x0, y0, x1, y1 in strokes:
                        at_painter.drawLine(
                            QPointF(left + x0 * size, at.y() + y0 * size),
                            QPointF(left + x1 * size, at.y() + y1 * size),
                        )

            wrapped(painter, QPointF(x, y), inscription)


#: Where the Redcap's coin sits on Mercere's mark, as fractions of its
#: side: its centre and radius (Houses of Hermes: True Lineages p. 78).
COIN_AT, COIN_RADIUS = (0.535, 0.75), 0.1


class Mercere(TrueLineage):
    """House Mercere: the letters the Redcaps carry, folded and opened
    again, their creases crossing the page, with drops of sealing wax in
    the cap's red and a road dotted from place to place. The sign closing
    a chapter shows the mark in its own colours: the cap red, the coin
    yellow, the triangle blue."""

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(23)
        fold = shade(p["paper-fleck"], round(22 * strength))
        sheen = shade(p["paper-sheen"], round(120 * strength))
        # The folds: a letter folded in three each way, crease and its
        # lit edge beside it.
        for step in range(3):
            at = TILE * step / 3 + TILE / 6
            for pen, offset in ((QPen(fold, 0.8), 0.0), (QPen(sheen, 0.8), 1.2)):
                painter.setPen(pen)
                painter.drawLine(QPointF(at + offset, 0), QPointF(at + offset, TILE))
                painter.drawLine(QPointF(0, at + offset), QPointF(TILE, at + offset))
        # Drops of wax.
        for _ in range(5):
            centre = QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE))
            radius = chance.uniform(4, 9)
            wax = shade(p["heading"], round(chance.randint(18, 30) * strength))

            def drop(
                at_painter: QPainter,
                at: QPointF,
                radius: float = radius,
                wax: QColor = wax,
            ) -> None:
                at_painter.setPen(Qt.PenStyle.NoPen)
                at_painter.setBrush(wax)
                at_painter.drawEllipse(at, radius, radius * 0.9)

            wrapped(painter, centre, drop)
        # A road, dotted from place to place.
        road = QPen(shade(p["accent"], round(40 * strength)), 1.4)
        road.setStyle(Qt.PenStyle.DotLine)
        start = QPointF(0, chance.uniform(0, TILE))
        path = QPainterPath(start)
        for i in range(1, 5):
            path.quadTo(
                QPointF(TILE * (i - 0.5) / 4, chance.uniform(0, TILE)),
                QPointF(TILE * i / 4, start.y() if i == 4 else chance.uniform(0, TILE)),
            )
        painter.setPen(road)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def tail_sign(self, painter: QPainter, centre: QPointF, p: Palette) -> None:
        # The cap in the heading's red, and on it the coin and the
        # triangle in the mark's own colours.
        super().tail_sign(painter, centre, p)
        side = MARK_SIDE
        corner = centre - QPointF(side / 2, side / 2)
        coin = corner + QPointF(COIN_AT[0] * side, COIN_AT[1] * side)
        radius = COIN_RADIUS * side
        painter.setPen(QPen(QColor(p["heading"]), 0.6))
        painter.setBrush(QColor(MERCERE_COIN))
        painter.drawEllipse(coin, radius, radius)
        # The triangle points down, as on the mark.
        r = radius * 0.55
        triangle = QPainterPath(coin + QPointF(-r, -r * 0.55))
        triangle.lineTo(coin + QPointF(r, -r * 0.55))
        triangle.lineTo(coin + QPointF(0, r * 0.9))
        triangle.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(MERCERE_POTSHERD))
        painter.drawPath(triangle)


class Tremere(TrueLineage):
    """House Tremere: the dressed setts of a Roman road (the square in the
    House's mark is one of its flagstones), laid in staggered courses, worn
    and chisel-marked, pale on the iron dark."""

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(29)
        ink = p["paper-sheen"]
        course = TILE / 8
        for row in range(8):
            top = row * course
            # The course's stones fill the tile's width exactly, from a
            # staggered start, so the courses meet from tile to tile.
            widths = []
            while sum(widths) < TILE:
                widths.append(chance.uniform(48, 92))
            widths = [w * TILE / sum(widths) for w in widths]
            x = chance.uniform(0, 60)
            for width in widths:
                stone = QRectF(x + 1.5, top + 1.5, width - 3, course - 3)
                # Worn low: the joints and chisel marks only just show.
                painter.setPen(
                    QPen(
                        shade(ink, round(chance.randint(12, 22) * strength * 0.5)), 0.8
                    )
                )
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for dx in (-TILE, 0):
                    painter.drawRoundedRect(stone.translated(dx, 0), 3, 3)
                # A few chisel marks on some stones.
                if chance.random() < 0.4:
                    painter.setPen(
                        QPen(
                            shade(ink, round(chance.randint(14, 24) * strength * 0.5)),
                            0.7,
                        )
                    )
                    for _ in range(chance.randint(2, 4)):
                        cx = x + chance.uniform(8, width - 8)
                        cy = top + chance.uniform(8, course - 8)
                        painter.drawLine(QPointF(cx, cy), QPointF(cx + 4, cy - 3))
                x += width


# -- the Mystery Cults' ornaments --------------------------------------------


def _feather(
    painter: QPainter, base: QPointF, angle: float, length: float, colour: QColor
) -> None:
    """A feather from its quill at `base`, pointing `angle` (radians, on
    screen), `length` long: a vane swelling either side of the shaft and
    tapering to the tip, with a few barbs drawn across it."""
    painter.save()
    painter.translate(base)
    painter.rotate(math.degrees(angle))
    width = length * 0.17
    vane = QPainterPath(QPointF(length * 0.2, 0))
    vane.cubicTo(
        QPointF(length * 0.38, -width * 1.15),
        QPointF(length * 0.82, -width),
        QPointF(length, 0),
    )
    vane.cubicTo(
        QPointF(length * 0.8, width * 0.9),
        QPointF(length * 0.4, width * 1.1),
        QPointF(length * 0.2, 0),
    )
    fill = QColor(colour)
    fill.setAlphaF(colour.alphaF() * 0.3)
    painter.setPen(QPen(colour, 0.7))
    painter.setBrush(fill)
    painter.drawPath(vane)
    painter.setPen(QPen(colour, 0.9))
    painter.drawLine(QPointF(0, 0), QPointF(length * 0.96, 0))
    painter.setPen(QPen(colour, 0.5))
    for k in range(3, 9):
        x = length * k / 10
        reach = width * 0.9 * math.sin(math.pi * k / 10)
        painter.drawLine(QPointF(x, 0), QPointF(x + length * 0.07, -reach))
        painter.drawLine(QPointF(x, 0), QPointF(x + length * 0.07, reach))
    painter.restore()


def _oak_leaf(
    painter: QPainter,
    base: QPointF,
    angle: float,
    length: float,
    colour: QColor,
    filled: bool = True,
) -> None:
    """An oak leaf from its stalk at `base`, pointing `angle` (radians, on
    screen), `length` long: rounded lobes either side and a midrib."""
    painter.save()
    painter.translate(base)
    painter.rotate(math.degrees(angle))
    stalk = length * 0.12
    blade = length - stalk
    upper, lower = [], []
    for i in range(41):
        t = i / 40
        envelope = math.sin(math.pi * t) ** 0.7
        x = stalk + t * blade
        upper.append(QPointF(x, -length * 0.26 * envelope * _lobe(t, 0.0)))
        lower.append(QPointF(x, length * 0.26 * envelope * _lobe(t, 0.12)))
    outline = QPainterPath(QPointF(0, 0))
    outline.lineTo(QPointF(stalk, 0))
    for point in upper:
        outline.lineTo(point)
    for point in reversed(lower):
        outline.lineTo(point)
    outline.closeSubpath()
    fill = QColor(colour)
    fill.setAlphaF(colour.alphaF() * (0.35 if filled else 0.0))
    painter.setPen(QPen(colour, 0.7))
    painter.setBrush(fill)
    painter.drawPath(outline)
    painter.drawLine(QPointF(0, 0), QPointF(length * 0.92, 0))
    painter.restore()


def _lobe(t: float, phase: float) -> float:
    """How far out an oak leaf's edge reaches at `t` along it (0 to 1):
    three and a half rounded lobes from stalk to tip."""
    return 0.6 + 0.4 * abs(math.cos((t + phase) * math.pi * 3.5))


def _acorn(painter: QPainter, at: QPointF, size: float, colour: QColor) -> None:
    """An acorn hanging from `at`, `size` tall: its nut and its cup."""
    nut = QColor(colour)
    nut.setAlphaF(colour.alphaF() * 0.35)
    painter.setPen(QPen(colour, 0.7))
    painter.setBrush(nut)
    painter.drawEllipse(at + QPointF(0, size * 0.6), size * 0.28, size * 0.36)
    painter.setBrush(colour)
    cup = QPainterPath(at + QPointF(-size * 0.33, size * 0.42))
    cup.cubicTo(
        at + QPointF(-size * 0.33, size * 0.12),
        at + QPointF(size * 0.33, size * 0.12),
        at + QPointF(size * 0.33, size * 0.42),
    )
    cup.closeSubpath()
    painter.drawPath(cup)
    painter.drawLine(at, at + QPointF(0, size * 0.2))


def _hammer(
    painter: QPainter, at: QPointF, angle: float, size: float, colour: QColor
) -> None:
    """A smith's hammer, its handle's end at `at`, pointing `angle`."""
    painter.save()
    painter.translate(at)
    painter.rotate(math.degrees(angle))
    painter.setPen(QPen(colour, max(0.8, size * 0.06)))
    painter.drawLine(QPointF(0, 0), QPointF(size * 0.85, 0))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(colour)
    head = QPainterPath(QPointF(size * 0.78, -size * 0.3))
    head.lineTo(size * 0.98, -size * 0.3)
    head.lineTo(size * 0.98, size * 0.16)
    head.lineTo(size * 0.92, size * 0.34)
    head.lineTo(size * 0.84, size * 0.34)
    head.lineTo(size * 0.78, size * 0.16)
    head.closeSubpath()
    painter.drawPath(head)
    painter.restore()


def _tongs(
    painter: QPainter, at: QPointF, angle: float, size: float, colour: QColor
) -> None:
    """A smith's tongs, the ends of its reins at `at`, pointing `angle`:
    two arms crossing at a rivet and closing in jaws."""
    painter.save()
    painter.translate(at)
    painter.rotate(math.degrees(angle))
    painter.setPen(QPen(colour, max(0.7, size * 0.045)))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for way in (-1, 1):
        arm = QPainterPath(QPointF(0, way * size * 0.1))
        arm.lineTo(size * 0.62, -way * size * 0.02)
        arm.quadTo(
            QPointF(size * 0.82, -way * size * 0.14),
            QPointF(size, -way * size * 0.03),
        )
        painter.drawPath(arm)
    painter.setBrush(colour)
    painter.drawEllipse(QPointF(size * 0.6, 0), size * 0.035, size * 0.035)
    painter.restore()


def _gem(painter: QPainter, at: QPointF, r: float, setting: QColor) -> None:
    """A cut stone `r` across from its centre at `at`, set in a bezel of
    `setting`: eight facets, lit from above left."""
    facets = QPainterPath()
    for i in range(8):
        turn = math.tau * (i + 0.5) / 8
        point = at + QPointF(r * math.cos(turn), r * math.sin(turn))
        if i == 0:
            facets.moveTo(point)
        else:
            facets.lineTo(point)
    facets.closeSubpath()
    light = QRadialGradient(at + QPointF(-r * 0.35, -r * 0.35), r * 1.3)
    light.setColorAt(0, QColor(VERDITIUS_GEM))
    light.setColorAt(1, QColor(VERDITIUS_GEM_DEEP))
    painter.setPen(QPen(setting, 0.8))
    painter.setBrush(QBrush(light))
    painter.drawPath(facets)


def _wrapped_marks(
    painter: QPainter,
    chance: random.Random,
    count: int,
    draw: Callable[[QPainter, QPointF, random.Random], None],
) -> None:
    """`draw` `count` times at random over a tile, each wrapped across its
    edges; `draw` takes its own random choices from a generator seeded
    once per mark, so its copies across the edges match."""
    for _ in range(count):
        centre = QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE))
        seed = chance.random()

        def mark(at_painter: QPainter, at: QPointF, seed: float = seed) -> None:
            draw(at_painter, at, random.Random(seed))

        wrapped(painter, centre, mark)


class Bjornaer(MysteryCult):
    """House Bjornaer: a pale hide, its grain pricked with pores and
    softly creased, sewn along stitched seams in the ochre's thread; fur
    along the frame, and feathers hung from the family's rings and lying
    along its rules, for the heartbeasts."""

    def __init__(self, mark: Path | None = None) -> None:
        super().__init__(mark)
        self._fur: dict[tuple[int, int], list[QLineF]] = {}

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(37)
        fleck = p["paper-fleck"]
        # The grain: pores, scattered over the whole hide.
        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(700):
            painter.setBrush(shade(fleck, round(chance.randint(14, 30) * strength)))
            painter.drawEllipse(
                QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE)),
                chance.uniform(0.5, 1.1),
                chance.uniform(0.5, 1.0),
            )

        # Soft creases where the hide has been worked.
        def crease(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            reach = rng.uniform(30, 90)
            bend = QPointF(reach / 2, rng.uniform(-14, 14))
            path = QPainterPath(at)
            path.quadTo(at + bend, at + QPointF(reach, rng.uniform(-8, 8)))
            at_painter.setPen(
                QPen(shade(fleck, round(rng.randint(12, 22) * strength)), 0.7)
            )
            at_painter.setBrush(Qt.BrushStyle.NoBrush)
            at_painter.drawPath(path)

        _wrapped_marks(painter, chance, 26, crease)
        # The seams, one each way, running whole across the tile: the join
        # and a running stitch over it in the ochre's thread.
        # Faded thread, half sunk into the hide.
        thread = shade(p["accent"], round(32 * strength))
        join = shade(fleck, round(16 * strength))
        stitch = TILE / 64
        for along in (TILE * 0.31, TILE * 0.67):
            painter.setPen(QPen(join, 0.8))
            painter.drawLine(QPointF(0, along), QPointF(TILE, along))
            painter.drawLine(QPointF(along, 0), QPointF(along, TILE))
            painter.setPen(QPen(thread, 1.2))
            for i in range(64):
                at = i * stitch
                painter.drawLine(
                    QPointF(at + 1, along - 2.5), QPointF(at + stitch - 2, along + 2.5)
                )
                painter.drawLine(
                    QPointF(along - 2.5, at + 1), QPointF(along + 2.5, at + stitch - 2)
                )

    def frame(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        super().frame(painter, rect, p)
        key = (round(rect.width()), round(rect.height()))
        if key not in self._fur:
            self._fur[key] = _fur(rect.width(), rect.height())
        painter.save()
        painter.translate(rect.topLeft())
        painter.setPen(QPen(alpha(p["accent"], 150), 0.6))
        painter.drawLines(self._fur[key])
        painter.restore()

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        super().corners(painter, rect, p, arm)
        colour = alpha(p["accent"], 220)
        for x, y, sx, sy in corners_of(rect.adjusted(2, 2, -2, -2)):
            # Hung from the ring and lying along the side, inside the
            # frame's margin.
            angle = math.pi / 2 if sy > 0 else -math.pi / 2
            _feather(
                painter, QPointF(x + sx * 4, y + sy * 10), angle, arm * 1.1, colour
            )

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        _ring(painter, 9, cy, 4.5, QColor(gilt), 1.2)
        _feather(painter, QPointF(15, cy), -0.12, 24, QColor(gilt))
        start = 42
        painter.setPen(fading(gilt, start, width * 0.8, 1.2))
        painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        cx = width / 2
        _ring(painter, cx, cy, 11, gilt, 1.3)
        _loop(painter, cx, cy, 9, gilt)
        for side in (-1, 1):
            angle = 0.0 if side == 1 else math.pi
            _feather(painter, QPointF(cx + side * 15, cy), angle, 26, gilt)


def _fur(width: float, height: float) -> list[QLineF]:
    """The hairs of fur along a frame `width` by `height`: short strokes
    leaning inward from each side's rule, the corners left to the rings."""
    chance = random.Random(41)
    hairs: list[QLineF] = []
    clear = 22.0
    for (x0, y0), (x1, y1), (nx, ny) in (
        ((clear, 0), (width - clear, 0), (0, 1)),
        ((clear, height), (width - clear, height), (0, -1)),
        ((0, clear), (0, height - clear), (1, 0)),
        ((width, clear), (width, height - clear), (-1, 0)),
    ):
        span = math.hypot(x1 - x0, y1 - y0)
        tx, ty = (x1 - x0) / span, (y1 - y0) / span
        for i in range(int(span / 2.2)):
            t = (i + chance.random() * 0.6) * 2.2
            root = QPointF(x0 + tx * t, y0 + ty * t)
            length = chance.uniform(2.5, 6.5)
            lean = chance.uniform(-0.6, 0.6)
            tip = root + QPointF((nx + tx * lean) * length, (ny + ty * lean) * length)
            hairs.append(QLineF(root, tip))
    return hairs


class Merinita(MysteryCult):
    """House Merinita: the shadows of oak leaves and acorns on a moss-dark
    page at twilight, barely there; leaves sprung from the family's rings
    and lying along its rules, and an oak's vine through the headpiece."""

    sign_drawn = True

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(43)
        sheen = p["paper-sheen"]

        def leaf(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            colour = shade(sheen, round(rng.randint(16, 30) * strength * 0.5))
            _oak_leaf(
                at_painter,
                at,
                rng.uniform(0, math.tau),
                rng.uniform(26, 62),
                colour,
                filled=rng.random() < 0.5,
            )

        def acorn(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            colour = shade(sheen, round(rng.randint(18, 30) * strength * 0.5))
            _acorn(at_painter, at, rng.uniform(10, 16), colour)

        _wrapped_marks(painter, chance, 24, leaf)
        _wrapped_marks(painter, chance, 5, acorn)

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        super().corners(painter, rect, p, arm)
        leaf = alpha(p["heading"], 200)
        for x, y, sx, sy in corners_of(rect.adjusted(2, 2, -2, -2)):
            ring = QPointF(x + sx * 6, y + sy * 6)
            along = 0.0 if sx > 0 else math.pi
            down = math.pi / 2 if sy > 0 else -math.pi / 2
            # Lying close along the frame's two sides, inside its margin.
            _oak_leaf(
                painter,
                ring + QPointF(sx * 4, -sy * 2),
                along + sy * sx * 0.08,
                arm * 0.8,
                leaf,
            )
            _oak_leaf(
                painter,
                ring + QPointF(-sx * 2, sy * 4),
                down - sy * sx * 0.08,
                arm * 0.8,
                leaf,
            )

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        _ring(painter, 9, cy, 4.5, QColor(gilt), 1.2)
        _oak_leaf(painter, QPointF(14, cy), -0.1, 20, QColor(p["heading"]))
        start = 38
        painter.setPen(fading(gilt, start, width * 0.8, 1.2))
        painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        cx = width / 2
        _ring(painter, cx, cy, 11, QColor(p["accent"]), 1.3)
        _acorn(painter, QPointF(cx, cy - 8), 15, QColor(p["heading"]))
        for side in (-1, 1):
            angle = 0.0 if side == 1 else math.pi
            _oak_leaf(
                painter, QPointF(cx + side * 13, cy), angle, 24, QColor(p["heading"])
            )

    def band(
        self, painter: QPainter, width: float, cy: float, inner: float, p: Palette
    ) -> None:
        cx = width / 2
        for side in (-1, 1):
            near, far = cx + side * inner, cx + side * (width / 2 - 6)
            # The vine: a stem winding outward, a leaf at each turn,
            # springing up and down in turn.
            stem = QPainterPath(QPointF(near, cy))
            x, i = near, 0
            while (far - x) * side > 0:
                step = side * min(22.0, abs(far - x))
                stem.quadTo(
                    QPointF(x + step / 2, cy + (4 if i % 2 else -4)),
                    QPointF(x + step, cy),
                )
                left = 1 - abs(x - near) / abs(far - near)
                if abs(far - x) > 14:
                    up = -1 if i % 2 else 1
                    angle = math.atan2(up * 0.9, side)
                    _oak_leaf(
                        painter,
                        QPointF(x + step / 2, cy + up * -1),
                        angle,
                        12,
                        alpha(p["heading"], int(230 * left**1.2)),
                    )
                x += step
                i += 1
            painter.setPen(fading(p["accent"], near, far, 1.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(stem)


class Verditius(MysteryCult):
    """House Verditius: soot-dark metal at night, planished all over with
    faint dents and catching the forge's light in a few soft glints of
    polish; a stone set in each of the family's rings, and hammer and tongs
    crossed in the headpiece."""

    sign_drawn = True

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(47)
        sheen = p["paper-sheen"]

        # The planishing: each dent a crescent of light on its upper side.
        def dent(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            r = rng.uniform(5, 13)
            at_painter.setPen(
                QPen(shade(sheen, round(rng.randint(10, 20) * strength)), 0.8)
            )
            at_painter.setBrush(Qt.BrushStyle.NoBrush)
            box = QRectF(at.x() - r, at.y() - r * 0.8, 2 * r, 1.6 * r)
            at_painter.drawArc(box, 30 * 16, 120 * 16)

        # Where the metal is worn bright, a broad soft glint of the forge's
        # light, part of the surface rather than lying on it.
        def glint(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            reach = rng.uniform(50, 110)
            light = QRadialGradient(at, reach)
            light.setColorAt(
                0, shade(p["heading"], round(rng.randint(8, 14) * strength))
            )
            light.setColorAt(1, shade(p["heading"], 0))
            at_painter.setPen(Qt.PenStyle.NoPen)
            at_painter.setBrush(QBrush(light))
            at_painter.drawEllipse(at, reach, reach * 0.6)

        _wrapped_marks(painter, chance, 6, glint)
        _wrapped_marks(painter, chance, 240, dent)

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        super().corners(painter, rect, p, arm)
        setting = QColor(p["heading"])
        for x, y, sx, sy in corners_of(rect.adjusted(2, 2, -2, -2)):
            # The stone set in the ring itself, inside the frame's margin.
            _gem(painter, QPointF(x + sx * 6, y + sy * 6), 3.0, setting)

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        super().heading_rule(painter, width, cy, p)
        _gem(painter, QPointF(9, cy - 4.5), 2.2, QColor(p["heading"]))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        tool = QColor(p["heading"])
        cx = width / 2
        _hammer(painter, QPointF(cx - 10, cy + 10), -math.pi / 4, 22, tool)
        _tongs(painter, QPointF(cx + 10, cy + 10), -math.pi * 3 / 4, 24, tool)
        _gem(painter, QPointF(cx, cy + 1), 3.4, tool)
        for side in (-1, 1):
            _ring(painter, cx + side * 24, cy, 5, gilt, 1.1)
            _ring(painter, cx + side * 35, cy, 3, gilt, 1.0)


# -- the Societates' ornaments -----------------------------------------------


def _flame(
    painter: QPainter, base: QPointF, height: float, colour: QColor, lean: float = 0.0
) -> None:
    """A flame rising `height` from `base`, its tip leaning `lean` (a
    fraction of its height) to the right: a tall middle tongue licking up
    in an S between two shorter ones, and a smaller flame inside it."""
    for scale, fill in ((1.0, 0.45), (0.5, 0.9)):
        h, w = height * scale, height * scale * 0.38
        at = base + QPointF(0, -h * (1 - scale) * 0.1)

        def point(x: float, y: float, at: QPointF = at, h: float = h) -> QPointF:
            return at + QPointF(x + lean * h * -y / h, y)

        path = QPainterPath(point(-w * 0.55, -h * 0.05))
        # The left tongue, the dip, the middle tongue's S to its tip...
        path.quadTo(point(-w * 1.1, -h * 0.35), point(-w * 0.75, -h * 0.62))
        path.quadTo(point(-w * 0.45, -h * 0.42), point(-w * 0.28, -h * 0.4))
        path.cubicTo(
            point(-w * 0.55, -h * 0.65), point(w * 0.15, -h * 0.75), point(0, -h)
        )
        # ...down its right side to the right tongue, and round the foot.
        path.cubicTo(
            point(w * 0.5, -h * 0.75),
            point(w * 0.15, -h * 0.55),
            point(w * 0.4, -h * 0.42),
        )
        path.quadTo(point(w * 0.55, -h * 0.5), point(w * 0.7, -h * 0.58))
        path.quadTo(point(w * 1.05, -h * 0.25), point(w * 0.55, -h * 0.05))
        path.quadTo(at + QPointF(0, h * 0.08), point(-w * 0.55, -h * 0.05))
        inside = QColor(colour)
        inside.setAlphaF(colour.alphaF() * fill)
        painter.setPen(QPen(colour, 0.7))
        painter.setBrush(inside)
        painter.drawPath(path)


class Flambeau(Societas):
    """House Flambeau: a page that has been through the fire, scorched in
    soft dark blots with the heat still in it: a dull ember glow under the
    scorch and a few live embers caught in its grain. Flames in place of
    the family's lozenges, and a name's initial quartered crimson and flame
    as a knight's shield."""

    quartered_initials = True

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(53)
        flame = p["heading"]

        # The heat left in the page: a dull glow, broad and soft.
        def heat(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            reach = rng.uniform(60, 130)
            glow = QRadialGradient(at, reach)
            glow.setColorAt(0, shade(flame, round(rng.randint(10, 18) * strength)))
            glow.setColorAt(1, shade(flame, 0))
            at_painter.setPen(Qt.PenStyle.NoPen)
            at_painter.setBrush(QBrush(glow))
            at_painter.drawEllipse(at, reach, reach * 0.7)

        # Scorch: soft dark blots, a few embers still alive in each.
        def scorch(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            at_painter.setPen(Qt.PenStyle.NoPen)
            for _ in range(rng.randint(3, 6)):
                r = rng.uniform(10, 26)
                burn = QRadialGradient(
                    at + QPointF(rng.uniform(-20, 20), rng.uniform(-14, 14)), r
                )
                burn.setColorAt(
                    0, shade(p["paper-fleck"], round(rng.randint(22, 40) * strength))
                )
                burn.setColorAt(1, shade(p["paper-fleck"], 0))
                at_painter.setBrush(QBrush(burn))
                at_painter.drawEllipse(burn.center(), r, r * 0.7)
            for _ in range(rng.randint(2, 5)):
                at_painter.setBrush(shade(flame, round(rng.randint(18, 34) * strength)))
                r = rng.uniform(0.6, 1.4)
                at_painter.drawEllipse(
                    at + QPointF(rng.uniform(-18, 18), rng.uniform(-10, 10)), r, r
                )

        _wrapped_marks(painter, chance, 7, heat)
        _wrapped_marks(painter, chance, 16, scorch)

    def corner_piece(
        self, painter: QPainter, x: float, y: float, sx: int, sy: int, p: Palette
    ) -> None:
        # A small flame at the cut, rising from its foot.
        fire = alpha(p["heading"], 220)
        _flame(painter, QPointF(x + sx * 6, y + sy * 6 + 4.5), 9, fire, sx * 0.1)

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = p["accent"]
        _flame(painter, QPointF(8, cy + 5), 12, QColor(p["heading"]))
        _chevron(painter, 18, cy, 4, 1, QColor(gilt))
        start = 26
        painter.setPen(fading(gilt, start, width * 0.8, 1.4))
        painter.drawLine(QPointF(start, cy), QPointF(width * 0.8, cy))
        painter.setPen(fading(gilt, start, width * 0.55, 0.6))
        painter.drawLine(QPointF(start, cy + 3), QPointF(width * 0.55, cy + 3))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        cx = width / 2
        _flame(painter, QPointF(cx, cy + 9), 22, QColor(p["heading"]))
        for side in (-1, 1):
            _chevron(painter, cx + side * 16, cy, 6, -side, gilt)
            _chevron(painter, cx + side * 26, cy, 6, -side, gilt)


def _tessera(painter: QPainter, at: QPointF, side: float, rng: random.Random) -> None:
    """One small tile of a mosaic, a little out of square, at `at`, in the
    painter's brush."""
    half = side / 2
    corners = [
        at
        + QPointF(
            dx * half + rng.uniform(-0.8, 0.8), dy * half + rng.uniform(-0.8, 0.8)
        )
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]
    path = QPainterPath(corners[0])
    for corner in corners[1:]:
        path.lineTo(corner)
    path.closeSubpath()
    painter.drawPath(path)


def _mercury(painter: QPainter, at: QPointF, size: float, colour: QColor) -> None:
    """Mercury's sign centred on `at`, `size` tall: the horns over the
    circle and the cross beneath."""
    painter.setPen(QPen(colour, max(0.8, size * 0.09)))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    r = size * 0.2
    centre = at + QPointF(0, -size * 0.05)
    painter.drawEllipse(centre, r, r)
    horns = QRectF(centre.x() - r, centre.y() - r * 2.9, 2 * r, 2 * r)
    painter.drawArc(horns, 200 * 16, 140 * 16)
    painter.drawLine(centre + QPointF(0, r), centre + QPointF(0, size * 0.5))
    painter.drawLine(
        centre + QPointF(-r * 0.8, size * 0.36), centre + QPointF(r * 0.8, size * 0.36)
    )


class Jerbiton(Societas):
    """House Jerbiton: the fine arts of a Byzantine city: cream vellum with
    the faintest weave of a tapestry through it, its warp in the vellum's
    own ink and its weft in purple, now and then a thread of teal; a
    tessera at each of the frame's cuts, and over the headpiece the House's own pennant flown from its staff,
    marked with mercury's sign."""

    sign_drawn = True

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(59)
        # The weave, whole across the tile: threads every few pixels (a
        # spacing that divides the tile, so it meets from tile to tile),
        # each a little stronger or fainter, as hand-spun thread is.
        step = 4
        for k in range(TILE // step):
            at = k * step + 0.5
            warp = shade(p["paper-fleck"], round(chance.randint(5, 10) * strength))
            painter.setPen(QPen(warp, 0.5))
            painter.drawLine(QPointF(at, 0), QPointF(at, TILE))
            ink = p["accent"] if chance.random() < 0.08 else p["heading"]
            weft = shade(ink, round(chance.randint(5, 10) * strength))
            painter.setPen(QPen(weft, 0.5))
            painter.drawLine(QPointF(0, at), QPointF(TILE, at))

    def corner_piece(
        self, painter: QPainter, x: float, y: float, sx: int, sy: int, p: Palette
    ) -> None:
        # A purple tessera at the cut, set a little out of square.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["heading"]))
        _tessera(painter, QPointF(x + sx * 6, y + sy * 6), 4.4, random.Random(61))

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        gilt = QColor(p["accent"])
        cx = width / 2
        # The House's pennant flown from its staff, with mercury's sign.
        staff = cx - 9
        painter.setPen(QPen(gilt, 1.2))
        painter.drawLine(QPointF(staff, cy - 11), QPointF(staff, cy + 11))
        flag = QPainterPath(QPointF(staff, cy - 10))
        flag.lineTo(staff + 22, cy - 7)
        flag.lineTo(staff + 17, cy - 1)
        flag.lineTo(staff + 22, cy + 5)
        flag.lineTo(staff, cy + 3)
        flag.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["heading"]))
        painter.drawPath(flag)
        _mercury(painter, QPointF(staff + 8, cy - 3), 11, QColor(p["background"]))
        for side in (-1, 1):
            _chevron(painter, cx + side * 22, cy, 6, -side, gilt)


class ExMiscellanea(Societas):
    """House Ex Miscellanea: many parts made one whole, a patchwork of
    pages from the traditions it gathers, each ruled its own way and sewn
    to the next along stitched seams, with the mist of Cad Gadu's lake
    drifting over it; its pennants dyed one muted colour for each
    tradition."""

    sign_drawn = True

    def pennant(self, p: Palette, i: int) -> str:
        return EX_MISCELLANEA_MOTLEY[i % len(EX_MISCELLANEA_MOTLEY)]

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(71)
        # The patches fill the tile exactly, column by column, so they
        # meet from tile to tile.
        widths = []
        while sum(widths) < TILE:
            widths.append(chance.uniform(70, 150))
        widths = [w * TILE / sum(widths) for w in widths]
        x = 0.0
        for width in widths:
            heights = []
            while sum(heights) < TILE:
                heights.append(chance.uniform(60, 140))
            heights = [h * TILE / sum(heights) for h in heights]
            y = 0.0
            for height in heights:
                _patch(painter, QRectF(x, y, width, height), p, strength, chance)
                y += height
            x += width
        # The seams between the columns, sewn with a running stitch (the
        # tile's own edge twice, so it meets the next tile's).
        painter.setPen(QPen(shade(p["accent"], round(60 * strength)), 1.0))
        x = 0.0
        for width in [*widths, 0.0]:
            for k in range(TILE // 8):
                y = k * 8
                painter.drawLine(QPointF(x - 2, y + 1), QPointF(x + 2, y + 5))
            x += width

        # Mist off the lake.
        def mist(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            reach = rng.uniform(60, 120)
            glow = QRadialGradient(at, reach)
            glow.setColorAt(0, shade(p["paper-sheen"], round(110 * strength)))
            glow.setColorAt(1, shade(p["paper-sheen"], 0))
            at_painter.setPen(Qt.PenStyle.NoPen)
            at_painter.setBrush(QBrush(glow))
            at_painter.drawEllipse(at, reach, reach * 0.45)

        _wrapped_marks(painter, chance, 5, mist)


def _patch(
    painter: QPainter, rect: QRectF, p: Palette, strength: float, chance: random.Random
) -> None:
    """One patch of Ex Miscellanea's patchwork: a page ruled its own way
    (lines, columns, a grid, dots or hatching, or bare), faintly tinted,
    its edge sewn to its neighbours'."""
    fleck = p["paper-fleck"]
    tint = chance.choice(EX_MISCELLANEA_MOTLEY)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(shade(tint, round(chance.randint(8, 16) * strength)))
    painter.drawRect(rect)
    painter.setPen(QPen(shade(fleck, round(chance.randint(12, 22) * strength)), 0.6))
    kind = chance.choice(("lines", "columns", "grid", "dots", "hatch", "bare"))
    left, top, right, bottom = rect.left(), rect.top(), rect.right(), rect.bottom()
    gap = chance.uniform(6, 11)
    if kind in ("lines", "grid"):
        y = top + gap
        while y < bottom - 2:
            painter.drawLine(QPointF(left + 4, y), QPointF(right - 4, y))
            y += gap
    if kind in ("columns", "grid"):
        x = left + gap
        while x < right - 2:
            painter.drawLine(QPointF(x, top + 4), QPointF(x, bottom - 4))
            x += gap
    if kind == "dots":
        painter.setBrush(shade(fleck, round(chance.randint(16, 26) * strength)))
        painter.setPen(Qt.PenStyle.NoPen)
        y = top + gap
        while y < bottom - 2:
            x = left + gap
            while x < right - 2:
                painter.drawEllipse(QPointF(x, y), 0.8, 0.8)
                x += gap
            y += gap
    if kind == "hatch":
        painter.save()
        painter.setClipRect(rect.adjusted(3, 3, -3, -3))
        d = left - rect.height()
        while d < right:
            painter.drawLine(QPointF(d, bottom), QPointF(d + rect.height(), top))
            d += gap
        painter.restore()
    # The seam along its top, sewn to the patch above (and, along the
    # tile's top, again along its foot, so it meets the next tile's).
    painter.setPen(QPen(shade(p["accent"], round(60 * strength)), 1.0))
    for seam in (top, TILE) if top == 0 else (top,):
        x = left + 3
        while x < right - 4:
            painter.drawLine(QPointF(x, seam - 2), QPointF(x + 4, seam + 2))
            x += 8


# -- House Diedne, of no family ----------------------------------------------


#: How far apart the lines of Diedne's scraped-off writing run, and how far
#: they fall across the tile's width (a whole number of lines, so a line
#: leaving the tile's edge meets one entering the next tile).
SCRIPT_LEADING, SCRIPT_FALL = 16.0, 64.0


def _script_letter(rng: random.Random, at: QPointF, size: float) -> QPainterPath:
    """One letter of an invented book hand, `size` its x-height, its
    baseline's left end at `at`: two or three strokes chosen at random
    (slanting minims, ascenders, descenders, arches, wedges, hooks, curls),
    so it reads as writing without ever being a letter of any alphabet. No
    closed bowl, so no o, a, d or b, and no word of any language, forms."""
    path = QPainterPath()
    x, y = at.x(), at.y() - size

    def p(u: float, v: float) -> QPointF:
        # The hand leans backward, as no book hand of the Order does.
        return QPointF(x + (u + 0.25 * v) * size, y + v * size)

    for kind in rng.sample(
        ("minim", "ascender", "descender", "arch", "wedge", "hook", "curl"),
        rng.randint(2, 3),
    ):
        if kind == "minim":
            path.moveTo(p(0.1, 0))
            path.lineTo(p(0.05, 1))
        elif kind == "ascender":
            path.moveTo(p(0.15, -0.8))
            path.lineTo(p(0.1, 1))
        elif kind == "descender":
            path.moveTo(p(0.6, 0))
            path.lineTo(p(0.55, 1.7))
        elif kind == "arch":
            path.moveTo(p(0.1, 0.35))
            path.quadTo(p(0.45, -0.25), p(0.7, 0.3))
            path.lineTo(p(0.68, 1))
        elif kind == "wedge":
            path.moveTo(p(0.0, 0.1))
            path.lineTo(p(0.35, 1))
            path.lineTo(p(0.75, 0.05))
        elif kind == "hook":
            path.moveTo(p(0.05, 0.9))
            path.quadTo(p(0.4, 1.25), p(0.75, 0.55))
        else:
            path.moveTo(p(0.7, -0.3))
            path.quadTo(p(0.1, -0.1), p(0.45, 0.45))
    return path


class Diedne(Look):
    """House Diedne, Renounced and of no family: Scriptorum's own form,
    worn and scraped (its rules, the headpiece's band, its frames and the
    Inspector's broken off in places, two of its corner pieces gone), on a
    palimpsest. Older writing in an invented hand was scraped off the
    vellum and shows through as the ghost of a text, its lines falling
    across the page and faded where the knife went over them, the skin
    fine-scratched by the knife: the House erased from the Order's records
    and showing through anyway. Headings in Uncial Antiqua, initials plain,
    and its sign scraped all but away, closing each chapter in the
    watermark's dark."""

    heading_family = title_family = fonts.DISPLAY
    frames_window = True
    sign_drawn = True
    plain_initials = True

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(2253)
        ink = p["paper-sheen"]
        # Where the knife scraped hardest the old text is all but gone:
        # waves whose periods divide the tile, so they meet from tile to
        # tile.
        k1, k2 = chance.randint(1, 3), chance.randint(1, 3)
        p1, p2 = chance.uniform(0, math.tau), chance.uniform(0, math.tau)

        def kept(x: float, y: float) -> float:
            wave = math.sin(math.tau * k1 * x / TILE + p1) * math.cos(
                math.tau * k2 * y / TILE + p2
            )
            return max(0.12, min(1.0, 0.55 + 0.55 * wave))

        painter.setBrush(Qt.BrushStyle.NoBrush)
        rows = round(TILE / SCRIPT_LEADING)
        for row in range(rows):
            # Some lines are scraped clean away.
            if chance.random() < 0.45:
                continue
            x = chance.uniform(4, 60)
            while True:
                letters = chance.randint(2, 5)
                size = chance.uniform(5.5, 7.0)
                width = letters * size * 0.95
                if x + width > TILE - 6:
                    break
                y = row * SCRIPT_LEADING + x * SCRIPT_FALL / TILE
                opacity = round(chance.randint(14, 24) * kept(x, y) * strength)
                rng_seed = chance.random()

                def word(
                    at_painter: QPainter,
                    at: QPointF,
                    letters: int = letters,
                    size: float = size,
                    opacity: int = opacity,
                    rng_seed: float = rng_seed,
                ) -> None:
                    rng = random.Random(rng_seed)
                    at_painter.setPen(QPen(shade(ink, opacity), 0.7))
                    for i in range(letters):
                        # The baseline falls with the line as it runs.
                        dx = i * size * 0.95
                        at_painter.drawPath(
                            _script_letter(
                                rng,
                                at + QPointF(dx, dx * SCRIPT_FALL / TILE),
                                size,
                            )
                        )

                for dy in (-TILE, 0, TILE):
                    word(painter, QPointF(x, y + dy))
                x += width + chance.uniform(10, 40)

        # The knife's fine scratches in the grain, long and straight, all
        # slanting near the same way.
        def scratch(at_painter: QPainter, at: QPointF, rng: random.Random) -> None:
            reach = rng.uniform(50, 190)
            turn = math.radians(-28 + rng.uniform(-7, 7))
            end = at + QPointF(reach * math.cos(turn), reach * math.sin(turn))
            at_painter.setPen(
                QPen(shade(ink, round(rng.randint(8, 16) * strength)), 0.5)
            )
            at_painter.drawLine(at, end)

        _wrapped_marks(painter, chance, 34, scratch)

    def worn(self, frame: QRectF) -> QRegion | None:
        """The part of a frame ruled on `frame` the scraping left: all but
        short gaps along each of its four sides, spread evenly along them,
        the same each time for a frame of the same size."""
        chance = random.Random(round(frame.width()) * 7919 + round(frame.height()))
        whole = QRegion(frame.adjusted(-8, -8, 8, 8).toAlignedRect())
        corners = [frame.topLeft(), frame.topRight(), frame.bottomRight()]
        corners += [frame.bottomLeft()]
        for start, end in zip(corners, corners[1:] + corners[:1], strict=True):
            for gap in _gaps_along(start, end, 7.0, chance):
                whole = whole.subtracted(QRegion(gap.toAlignedRect()))
        return whole

    def frame(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        worn = self.worn(rect.adjusted(-3.5, -3.5, 3.5, 3.5))
        assert worn is not None
        painter.save()
        painter.setClipRegion(worn, Qt.ClipOperation.IntersectClip)
        super().frame(painter, rect, p)
        painter.restore()

    def corners(self, painter: QPainter, rect: QRectF, p: Palette, arm: float) -> None:
        """Scriptorum's corner flourishes, two of the four scraped away
        (the top right and the bottom left)."""
        reach = arm + 8
        kept = QRegion()
        for corner in (rect.topLeft(), rect.bottomRight()):
            box = QRectF(corner - QPointF(reach, reach), corner + QPointF(reach, reach))
            kept = kept.united(QRegion(box.toAlignedRect()))
        painter.save()
        painter.setClipRegion(kept, Qt.ClipOperation.IntersectClip)
        flourish.corner_flourishes(painter, rect, p, arm)
        painter.restore()

    def _worn_rule(
        self, painter: QPainter, width: float, cy: float, draw: Callable[[], None]
    ) -> None:
        """`draw` a level rule or band across `width` at `cy`, broken off
        in short gaps along it where it was scraped."""
        chance = random.Random(round(width) * 31 + round(cy))
        whole = QRegion(QRectF(0, cy - 40, width, 80).toAlignedRect())
        for gap in _gaps_along(QPointF(0, cy), QPointF(width, cy), 40.0, chance):
            whole = whole.subtracted(QRegion(gap.toAlignedRect()))
        painter.save()
        painter.setClipRegion(whole, Qt.ClipOperation.IntersectClip)
        draw()
        painter.restore()

    def heading_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        def draw() -> None:
            super(Diedne, self).heading_rule(painter, width, cy, p)

        self._worn_rule(painter, width, cy, draw)

    def short_rule(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        def draw() -> None:
            super(Diedne, self).short_rule(painter, width, cy, p)

        self._worn_rule(painter, width, cy, draw)

    def headpiece_centre(
        self, painter: QPainter, width: float, cy: float, p: Palette
    ) -> None:
        def draw() -> None:
            super(Diedne, self).headpiece_centre(painter, width, cy, p)

        self._worn_rule(painter, width, cy, draw)

    def band(
        self, painter: QPainter, width: float, cy: float, inner: float, p: Palette
    ) -> None:
        def draw() -> None:
            super(Diedne, self).band(painter, width, cy, inner, p)

        self._worn_rule(painter, width, cy, draw)

    def tail_flank(
        self, painter: QPainter, cx: float, cy: float, inner: float, p: Palette
    ) -> None:
        def draw() -> None:
            super(Diedne, self).tail_flank(painter, cx, cy, inner, p)

        self._worn_rule(painter, 2 * cx, cy, draw)

    def tail_sign(self, painter: QPainter, centre: QPointF, p: Palette) -> None:
        # In the watermark's dark, not the heading's ink: what is left of
        # the sign is pressed into the page, not written on it.
        side = MARK_SIDE
        painter.save()
        painter.setOpacity(0.8)
        painter.drawPixmap(
            centre - QPointF(side / 2, side / 2), self.sign(watermark_ink(p), side)
        )
        painter.restore()


def _gaps_along(
    start: QPointF, end: QPointF, reach: float, chance: random.Random
) -> list[QRectF]:
    """The gaps scraped in a straight rule from `start` to `end` (level or
    upright): runs of 25 to 110 pixels between gaps of 3 to 12, each gap a
    box `reach` either side of the rule, so a mark drawn along it is cut
    through."""
    length = QLineF(start, end).length()
    if length <= 0:
        return []
    ux, uy = (end.x() - start.x()) / length, (end.y() - start.y()) / length
    gaps: list[QRectF] = []
    along = chance.uniform(10, 60)
    while along < length:
        gap = chance.uniform(3, 12)
        a = start + QPointF(ux * along, uy * along)
        b = start + QPointF(ux * (along + gap), uy * (along + gap))
        gaps.append(
            QRectF(a, b)
            .normalized()
            .adjusted(
                -reach * abs(uy), -reach * abs(ux), reach * abs(uy), reach * abs(ux)
            )
        )
        along += gap + chance.uniform(25, 110)
    return gaps
