"""How a theme paints a page: Scriptorum's look, and the three House
families' forms that the House themes are built on.

`Look.paint_page` is a Template Method: it lays down the steps every page
is painted in (the paper with its texture, the margins, the shading
toward the edges, the frame, its corners and the House's mark) and each
step is a method a family or a House fills in. Scriptorum's own look is
the base class and paints as the app always has. A House family (True
Lineage, Mystery Cult, Societas) gives its Houses one form: the frame,
its corners, the rules under headings, the headpiece and tailpiece and
the heading type. A House theme is a family's subclass that adds only its
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

from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt
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
from ...style.palettes import READABLE, TEXT, Palette, contrast, mixed
from . import flourish
from .flourish import alpha, corners_of, fading, lozenge
from .vellum import TILE, laid_paper, shade, worst_ground

#: The kinds of page: the main window's body, a dialog's sheet, and a
#: page with no frame (a card's, a picture's).
WINDOW, DIALOG, PLAIN = "window", "dialog", "plain"
#: How far in from a page's edge its frame is drawn, and how wide the
#: margin a texture is kept whole in.
FRAME_INSET, MARGIN = 4.0, 30
#: The House's seal at the foot of the frame: its radius, and the side of
#: the mark inside it, in pixels.
SEAL_RADIUS, MARK_SIDE = 22, 28
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
    pixel short of solid) are the sign."""
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
        for i in piece:
            outside[i] = 3 if central else 1
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
    #: Whether the form's own pieces (its frame) are drawn on the window.
    frames_window = False

    def __init__(self, mark: Path | None = None) -> None:
        #: The House's mark, drawn on the frame, or None.
        self.mark = mark
        self._tiles: dict[str, QPixmap] = {}
        self._margins: dict[str, QPixmap] = {}
        self._watermarks: dict[str, float] = {}

    # -- the template method -------------------------------------------------

    def paint_page(
        self, painter: QPainter, rect: QRectF, p: Palette, kind: str
    ) -> None:
        """Paint a page of `kind` (WINDOW, DIALOG or PLAIN) filling `rect`:
        the paper, its margins, the shade toward its edges, then (unless
        it is PLAIN) the frame, its corners and the mark."""
        painter.drawTiledPixmap(rect.toRect(), self.tile(p))
        self.paint_margins(painter, rect, p)
        self.paint_edges(painter, rect, p)
        if kind == PLAIN or (kind == WINDOW and not self.frames_window):
            return
        inside = rect.adjusted(FRAME_INSET, FRAME_INSET, -FRAME_INSET, -FRAME_INSET)
        self.frame(painter, inside, p)
        self.corners(painter, inside, p, 18)
        self.paint_mark(painter, inside, p)

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

    def paint_mark(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        """The House's seal at the foot of the frame, wholly inside the
        page: its mark on a round of the page's surface in a gilt ring,
        the frame's rules breaking round it."""
        if self.mark is None:
            return
        radius = SEAL_RADIUS
        centre = QPointF(rect.center().x(), rect.bottom() - radius + 1)
        # The rules stop short of the seal: the page's paper shows round it.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.tile(p)))
        painter.drawEllipse(centre, radius + 5, radius + 5)
        painter.setPen(QPen(QColor(p["accent"]), 1.8))
        painter.setBrush(QColor(p["surface"]))
        painter.drawEllipse(centre, radius, radius)
        painter.setPen(QPen(alpha(p["accent"], 170), 0.7))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(centre, radius - 3.5, radius - 3.5)
        side = MARK_SIDE
        painter.drawPixmap(
            centre - QPointF(side / 2, side / 2),
            _mark(self.mark, p["heading"], side, 2.0),
        )

    def inspector_mark(self, painter: QPainter, rect: QRectF, p: Palette) -> None:
        """The House's mark watermarked large at the foot of the Inspector
        (`rect` inside its frame), as a watermark shows in a sheet held to
        the light: paler than the page on a light theme, deeper on a dark
        one, so text over it only stands out the more. Scriptorum has no
        mark."""
        if self.mark is None:
            return
        side = round(min(rect.width() * 0.6, WATERMARK_SIDE))
        opacity = self.watermark_opacity(p)
        if side < 60 or opacity <= 0:
            return
        corner = QPointF(rect.center().x() - side / 2, rect.bottom() - side - 26)
        painter.save()
        painter.setOpacity(opacity)
        painter.drawPixmap(corner, _sign(self.mark, watermark_ink(p), side, 2.0))
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
        """The ornament closing a chapter."""
        flourish.tailpiece(painter, width, p)


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

    def tailpiece(self, painter: QPainter, width: float, p: Palette) -> None:
        gilt = p["accent"]
        cx, top = width / 2, 14
        for side in (-1, 1):
            painter.setPen(fading(gilt, cx + side * 30, cx + side * 150, 1.0))
            painter.drawLine(
                QPointF(cx + side * 30, top), QPointF(cx + side * 150, top)
            )
            _square(painter, cx + side * 18, top, 2.6, gilt)
        _square(painter, cx, top, 5, gilt)
        _square(painter, cx, top + 16, 3, gilt)
        _square(painter, cx, top + 28, 1.6, gilt)


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

    def tailpiece(self, painter: QPainter, width: float, p: Palette) -> None:
        gilt = QColor(p["accent"])
        cx, top = width / 2, 14
        for side in (-1, 1):
            painter.setPen(fading(p["accent"], cx + side * 30, cx + side * 150, 1.0))
            painter.drawLine(
                QPointF(cx + side * 30, top), QPointF(cx + side * 150, top)
            )
        _loop(painter, cx, top, 16, gilt)
        _ring(painter, cx, top + 18, 4, gilt, 1.1)
        _ring(painter, cx, top + 30, 2, gilt, 1.0)


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
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gilt)
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
                ink = p[self.livery[i % len(self.livery)]]
                _pennant(painter, x, top, alpha(ink, int(255 * left**1.2)))
                x += side * PENNANT_STEP
                i += 1

    def tailpiece(self, painter: QPainter, width: float, p: Palette) -> None:
        gilt = QColor(p["accent"])
        cx, top = width / 2, 14
        for side in (-1, 1):
            painter.setPen(fading(p["accent"], cx + side * 26, cx + side * 150, 1.0))
            painter.drawLine(
                QPointF(cx + side * 26, top), QPointF(cx + side * 150, top)
            )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gilt)
        for dx, dy, r in (
            (-12, 0, 3.5),
            (0, 0, 5),
            (12, 0, 3.5),
            (0, 14, 3.5),
            (0, 26, 2),
        ):
            lozenge(painter, cx + dx, top + dy, r)


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
    rings for the circle of time, and small spirals, all faint, pale on
    the dark."""

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(13)
        ink = p["paper-sheen"]
        for _ in range(28):
            centre = QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE))
            kind = chance.choice(("loop", "rings", "spiral"))
            size = chance.uniform(10, 34) if kind != "rings" else chance.uniform(30, 90)
            opacity = round(chance.randint(14, 26) * strength)
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
    """House Tytalus: Fudarus's storm-slate sky, rain driven slantwise
    across it, and the House's spira of four turns struck again and
    again, some in Buliste's violet turning one way, some in Harpax's green
    turning the other, contending across the page."""

    quartered_initials = True

    def texture(self, painter: QPainter, p: Palette, strength: float) -> None:
        chance = random.Random(17)
        # The storm: fine rain driven slantwise.
        for _ in range(70):
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
        # The spirae: violet clockwise, green against it.
        for i in range(12):
            centre = QPointF(chance.uniform(0, TILE), chance.uniform(0, TILE))
            radius = chance.uniform(14, 40)
            violet = i % 2 == 0
            ink = p["heading"] if violet else p["accent"]
            pen = QPen(shade(ink, round(chance.randint(18, 30) * strength)), 0.9)

            def spira(
                at_painter: QPainter,
                at: QPointF,
                radius: float = radius,
                pen: QPen = pen,
                way: int = 1 if violet else -1,
            ) -> None:
                at_painter.setPen(pen)
                _spiral(at_painter, at, radius, 4, way)

            wrapped(painter, centre, spira)


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
