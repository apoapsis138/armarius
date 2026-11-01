"""A printed sheet (print_layout.Document) drawn to a PDF: real text in the
app's faces on textured Scriptorum parchment (or plain white, to save
ink), each page framed with a gilt rule, a
fleuron at each corner and a red band down the binding edge.

Each block is measured at the column width with the PDF's own font
metrics, print_layout.paginate decides the pages, and each block is drawn
where it was placed, so nothing is drawn past the page's printed area.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import cache
from pathlib import Path

from PySide6.QtCore import QByteArray, QMarginsF, QPointF, QRectF, QSizeF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetricsF,
    QPageLayout,
    QPageSize,
    QPainter,
    QPdfWriter,
    QPen,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer

from .. import artwork
from .. import print_layout as pl
from . import marks, pictures
from .style.paper import paper
from .themes import SCRIPTORUM, Palette

#: The palette a sheet is printed in.
PARCHMENT: Palette = SCRIPTORUM

#: The page's printed area, in points from its edges: room for the frame
#: and the band on the binding (left) side.
LEFT, RIGHT, TOP, BOTTOM = 62.0, 50.0, 58.0, 58.0
#: The frame's outer and inner rules, in points from the page's edges.
OUTER, INNER = 22.0, 26.0
#: The space after each kind of block.
GAP = 8.0

Align = Qt.AlignmentFlag
LEFT_ALIGN, RIGHT_ALIGN, CENTRE = Align.AlignLeft, Align.AlignRight, Align.AlignHCenter
ALIGN = {"l": LEFT_ALIGN, "c": CENTRE, "r": RIGHT_ALIGN}


def _font(
    size: float,
    *,
    bold: bool = False,
    italic: bool = False,
    caps: bool = False,
    family: str = pictures.SERIF,
) -> QFont:
    font = QFont(family)
    font.setPointSizeF(size)
    font.setBold(bold)
    font.setItalic(italic)
    if caps:
        font.setCapitalization(QFont.Capitalization.SmallCaps)
    return font


def _shade(colour: str, alpha: int) -> QColor:
    shaded = QColor(colour)
    shaded.setAlpha(alpha)
    return shaded


#: The side, in pixels, an Art's symbol is drawn at for paper: sharp at
#: the size a table row shows it.
SYMBOL_PIXELS = 96


@cache
def _art_picture(art: str, colour: str) -> QPixmap:
    svg = artwork.art_symbol(art).read_text(encoding="utf-8")
    renderer = QSvgRenderer(
        QByteArray(svg.replace("currentColor", colour).encode("utf-8"))
    )
    picture = QPixmap(SYMBOL_PIXELS, SYMBOL_PIXELS)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, SYMBOL_PIXELS, SYMBOL_PIXELS))
    painter.end()
    return picture


class Sheet:
    """Draws one Document onto a PDF."""

    def __init__(self, path: Path, doc: pl.Document, options: pl.PrintOptions) -> None:
        self.doc = doc
        self.p = PARCHMENT
        self.textured = options.textured
        #: The page's colour where the frame's corners clear it.
        self.page_colour = QColor(
            PARCHMENT["background"] if options.textured else "white"
        )
        width, height = pl.PAPER_POINTS[options.paper]
        self.page_size = QSizeF(width, height)
        self.writer = QPdfWriter(str(path))
        self.writer.setTitle(doc.title)
        self.writer.setCreator("Armarius")
        self.writer.setResolution(72)
        size = (
            QPageSize.PageSizeId.Letter
            if options.paper == pl.LETTER
            else QPageSize.PageSizeId.A4
        )
        self.writer.setPageLayout(
            QPageLayout(
                QPageSize(size),
                QPageLayout.Orientation.Portrait,
                QMarginsF(0, 0, 0, 0),
            )
        )
        self.width = width - LEFT - RIGHT
        self.height = height - TOP - BOTTOM
        self.painter: QPainter | None = None
        self.ink = QColor(self.p["foreground"])
        self.red = QColor(self.p["heading"])
        self.gold = QColor(self.p["accent"])
        self.rule = QColor(self.p["rule"])
        self.label = QColor(self.p["label"])
        self.tint = _shade(self.p["panel"], 90)
        self.band = _shade(self.p["panel"], 45)
        self._measures: dict[type, Callable] = {
            pl.Title: self._title_h,
            pl.Heading: self._heading_h,
            pl.ScoreBoxes: self._boxes_h,
            pl.Facts: self._facts_h,
            pl.Paragraph: self._paragraph_h,
            pl.Table: self._table_h,
            pl.Entry: self._entry_h,
            pl.Columns: self._columns_h,
            pl.Condition: self._condition_h,
            pl.CombatSummary: lambda b, w: 64.0,
            pl.Weapons: lambda b, w: 46.0 + len(b.rows) * 15,
            pl.Equipment: lambda b, w: 24.0 + b.lines * 14,
            pl.GrimoireTitle: lambda b, w: 62.0,
            pl.Spell: self._spell_h,
            pl.NewPage: lambda b, w: 0.0,
        }
        self._painters: dict[type, Callable] = {
            pl.Title: self._title,
            pl.Heading: self._heading,
            pl.ScoreBoxes: self._boxes,
            pl.Facts: self._facts,
            pl.Paragraph: self._paragraph,
            pl.Table: self._table,
            pl.Entry: self._entry,
            pl.Columns: self._columns,
            pl.Condition: self._condition,
            pl.CombatSummary: self._combat,
            pl.Weapons: self._weapons,
            pl.Equipment: self._equipment,
            pl.GrimoireTitle: self._grimoire_title,
            pl.Spell: self._spell,
            pl.NewPage: lambda *args: None,
        }

    # ------------------------------------------------------------ text

    @property
    def qp(self) -> QPainter:
        assert self.painter is not None
        return self.painter

    def text_height(self, words: str, font: QFont, width: float) -> float:
        metrics = QFontMetricsF(font, self.writer)
        flags = int(Qt.TextFlag.TextWordWrap)
        return metrics.boundingRect(QRectF(0, 0, width, 100000), flags, words).height()

    def text(
        self,
        rect: QRectF,
        words: str,
        font: QFont,
        colour: QColor | None = None,
        align: Qt.AlignmentFlag = LEFT_ALIGN,
    ) -> None:
        self.qp.setFont(font)
        self.qp.setPen(colour or self.ink)
        self.qp.drawText(rect, int(align | Qt.TextFlag.TextWordWrap), words)

    def line(
        self, colour: QColor, width: float, x1: float, y1: float, x2: float, y2: float
    ) -> None:
        self.qp.setPen(QPen(colour, width))
        self.qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def blank(self, x: float, y: float, width: float) -> None:
        """A line to pencil something in on."""
        self.line(self.label, 0.4, x, y, x + width, y)

    def box(self, x: float, y: float, filled: bool = False, side: float = 9) -> None:
        self.qp.setPen(QPen(self.ink, 0.7))
        self.qp.setBrush(self.ink if filled else Qt.BrushStyle.NoBrush)
        self.qp.drawRect(QRectF(x, y, side, side))
        self.qp.setBrush(Qt.BrushStyle.NoBrush)

    def symbol(
        self, symbol: pl.Symbol, rect: QRectF, colour: str | None = None
    ) -> None:
        """An Art's symbol or an Ability's mark, drawn once as a picture and
        reused, so a sheet with fifty of them stays small."""
        ink = colour or self.p["foreground"]
        if symbol.kind == "art":
            picture = _art_picture(symbol.name, ink)
        else:
            picture = marks.pixmap(symbol.name, symbol.category, ink, 40, 2.0)
        self.qp.drawPixmap(rect, picture, QRectF(picture.rect()))

    def panel(self, x: float, y: float, w: float, h: float, title: str) -> QRectF:
        """A ruled box with its title, as the printed sheet boxes each part;
        the area inside it."""
        self.qp.setPen(QPen(self.gold, 0.9))
        self.qp.setBrush(QColor(255, 250, 240, 70))
        self.qp.drawRoundedRect(QRectF(x, y, w, h), 3, 3)
        self.qp.setBrush(Qt.BrushStyle.NoBrush)
        self.text(
            QRectF(x + 8, y + 4, w, 18),
            title,
            _font(12, bold=True, caps=True),
            self.red,
        )
        return QRectF(x + 8, y + 24, w - 16, h - 28)

    # ------------------------------------------------------------ measures

    def measure(self, block: pl.Block, width: float) -> float:
        return self._measures[type(block)](block, width)

    def _title_h(self, block: pl.Title, width: float) -> float:
        return 64.0

    def _heading_h(self, block: pl.Heading, width: float) -> float:
        return 30.0 if block.level == 1 else 18.0

    def _boxes_h(self, block: pl.ScoreBoxes, width: float) -> float:
        return 42.0

    def _fact_rows(self, block: pl.Facts) -> list[tuple[tuple[str, str], ...]]:
        n = block.columns
        return [block.facts[i : i + n] for i in range(0, len(block.facts), n)]

    def _fact_row_h(self, row: tuple[tuple[str, str], ...], cell: float) -> float:
        return 10 + max(self.text_height(v, _font(10), cell - 6) for _, v in row)

    def _facts_h(self, block: pl.Facts, width: float) -> float:
        cell = width / block.columns
        return sum(self._fact_row_h(r, cell) + 3 for r in self._fact_rows(block))

    def _paragraph_font(self, block: pl.Paragraph) -> QFont:
        size = 8.5 if block.size == "small" else 10.5
        return _font(size, italic=block.style == "italic")

    def _paragraph_h(self, block: pl.Paragraph, width: float) -> float:
        return self.text_height(block.text, self._paragraph_font(block), width)

    ROW, HEAD, GROUP = 16.0, 15.0, 13.0

    def _row_heights(self, block: pl.Table) -> list[float]:
        groups = dict(block.groups)
        return [
            self.ROW + (self.GROUP if i in groups else 0)
            for i in range(len(block.rows))
        ]

    def _table_h(self, block: pl.Table, width: float) -> float:
        return self.HEAD + sum(self._row_heights(block))

    def _entry_h(self, block: pl.Entry, width: float) -> float:
        return 15 + self.text_height(block.summary, _font(9), width - 8)

    def _run_h(self, blocks: tuple[pl.Block, ...], width: float) -> float:
        return sum(self.measure(b, width) + GAP for b in blocks)

    def _columns_h(self, block: pl.Columns, width: float) -> float:
        left = (width - 16) * block.split
        right = width - 16 - left
        return max(self._run_h(block.left, left), self._run_h(block.right, right)) - GAP

    def _condition_h(self, block: pl.Condition, width: float) -> float:
        return 28.0 + max(len(block.fatigue.rows), len(block.wounds.rows) + 1) * 13

    def _spell_h(self, block: pl.Spell, width: float) -> float:
        extra = 0.0
        if block.description:
            extra = 4 + self.text_height(block.description, _font(9.5), width - 10)
        return 43.0 + extra

    # ------------------------------------------------------------ painters

    def paint(
        self,
        block: pl.Block,
        x: float,
        y: float,
        w: float,
        part: pl.Placement | None = None,
    ) -> None:
        if isinstance(block, pl.Table):
            self._table(block, x, y, w, part)
        else:
            self._painters[type(block)](block, x, y, w)

    def _title(self, block: pl.Title, x: float, y: float, w: float) -> None:
        self.text(
            QRectF(x, y, w, 40),
            block.name,
            _font(30, family=pictures.DISPLAY),
            self.red,
        )
        self.text(
            QRectF(x + 2, y + 40, w, 16),
            block.subtitle,
            _font(11.5, italic=True),
            self.label,
        )
        self.line(self.gold, 1, x, y + 62, x + w, y + 62)

    def _heading(self, block: pl.Heading, x: float, y: float, w: float) -> None:
        if block.symbol is not None:
            self.symbol(block.symbol, QRectF(x, y + 1, 13, 13), self.p["heading"])
            x, w = x + 18, w - 18
        if block.level == 1:
            self.text(
                QRectF(x, y, w, 22),
                block.text,
                _font(16, bold=True, caps=True),
                self.red,
            )
            self.line(self.gold, 0.8, x, y + 23, x + w, y + 23)
            self.line(self.rule, 0.4, x, y + 25, x + w, y + 25)
            return
        font = _font(11.5, bold=True, caps=True)
        self.text(QRectF(x, y, w, 16), block.text, font)
        advance = QFontMetricsF(font, self.writer).horizontalAdvance(block.text)
        self.line(self.rule, 0.6, x + advance + 8, y + 10, x + w, y + 10)

    def _boxes(self, block: pl.ScoreBoxes, x: float, y: float, w: float) -> None:
        gap = 5.0
        n = len(block.items)
        side = (w - gap * (n - 1)) / n
        for i, (label, value) in enumerate(block.items):
            bx = x + i * (side + gap)
            self.qp.setPen(QPen(self.gold, 0.8))
            self.qp.setBrush(self.tint)
            self.qp.drawRoundedRect(QRectF(bx, y, side, 38), 3, 3)
            self.qp.setBrush(Qt.BrushStyle.NoBrush)
            colour = self.red if value.startswith("−") else self.ink
            self.text(
                QRectF(bx, y + 2, side, 22), value, _font(15, bold=True), colour, CENTRE
            )
            self.text(
                QRectF(bx, y + 24, side, 12),
                label,
                _font(7, caps=True),
                self.label,
                CENTRE,
            )

    def _facts(self, block: pl.Facts, x: float, y: float, w: float) -> None:
        cell = w / block.columns
        for row in self._fact_rows(block):
            h = self._fact_row_h(row, cell)
            for i, (label, value) in enumerate(row):
                cx = x + i * cell
                self.text(
                    QRectF(cx, y, cell - 6, 10),
                    label,
                    _font(7.5, caps=True),
                    self.label,
                )
                self.text(QRectF(cx, y + 9, cell - 6, h), value, _font(10))
            y += h + 3

    def _paragraph(self, block: pl.Paragraph, x: float, y: float, w: float) -> None:
        colour = self.label if block.style == "italic" else self.ink
        self.text(
            QRectF(x, y, w, 100000), block.text, self._paragraph_font(block), colour
        )

    def _cell(self, cell: pl.Cell, rect: QRectF, align: str) -> None:
        font = _font(9.5, bold=cell.style == "bold", italic=cell.style == "italic")
        if cell.symbol is not None:
            side = rect.height() - 4
            self.symbol(cell.symbol, QRectF(rect.x() + 3, rect.y() + 2, side, side))
            rect = rect.adjusted(side + 3, 0, 0, 0)
        self.qp.setFont(font)
        self.qp.setPen(self.ink)
        flags = int(ALIGN[align] | Align.AlignVCenter)
        self.qp.drawText(rect.adjusted(3, 0, -3, 0), flags, cell.text)

    def _table(
        self,
        block: pl.Table,
        x: float,
        y: float,
        w: float,
        part: pl.Placement | None = None,
    ) -> None:
        first, last = (
            (part.first, part.last) if part and part.last else (0, len(block.rows))
        )
        xs, at = [], x
        for column in block.columns:
            xs.append(at)
            at += column.width * w
        self.qp.fillRect(QRectF(x, y, w, self.HEAD - 1), self.tint)
        self.line(self.gold, 0.8, x, y + self.HEAD - 1, x + w, y + self.HEAD - 1)
        head = _font(7.5, bold=True, caps=True)
        for cx, column in zip(xs, block.columns, strict=True):
            rect = QRectF(cx + 3, y, column.width * w - 6, self.HEAD - 1)
            self.qp.setFont(head)
            self.qp.setPen(self.label)
            self.qp.drawText(
                rect, int(ALIGN[column.align] | Align.AlignVCenter), column.title
            )
        y += self.HEAD
        groups = dict(block.groups)
        for i in range(first, last):
            if i in groups:
                self.text(
                    QRectF(x + 3, y, w, self.GROUP),
                    groups[i],
                    _font(8.5, bold=True, caps=True),
                    self.red,
                )
                y += self.GROUP
            if i % 2:
                self.qp.fillRect(QRectF(x, y, w, self.ROW), self.band)
            for cx, column, cell in zip(xs, block.columns, block.rows[i], strict=True):
                self._cell(
                    cell, QRectF(cx, y, column.width * w, self.ROW), column.align
                )
            self.line(
                _shade(self.p["rule"], 140), 0.4, x, y + self.ROW, x + w, y + self.ROW
            )
            y += self.ROW

    def _entry(self, block: pl.Entry, x: float, y: float, w: float) -> None:
        h = self._entry_h(block, w)
        self.line(self.gold, 1.2, x, y + 2, x, y + h - 1)
        self.text(QRectF(x + 6, y, w, 14), block.name, _font(10.5, bold=True))
        self.text(
            QRectF(x, y + 1, w, 14),
            block.note,
            _font(7.5, caps=True),
            self.label,
            RIGHT_ALIGN,
        )
        self.text(QRectF(x + 6, y + 15, w - 8, h), block.summary, _font(9), self.label)

    def _run(self, blocks: tuple[pl.Block, ...], x: float, y: float, w: float) -> None:
        for block in blocks:
            self.paint(block, x, y, w)
            y += self.measure(block, w) + GAP

    def _columns(self, block: pl.Columns, x: float, y: float, w: float) -> None:
        left = (w - 16) * block.split
        self._run(block.left, x, y, left)
        self._run(block.right, x + left + 16, y, w - 16 - left)

    def _condition(self, block: pl.Condition, x: float, y: float, w: float) -> None:
        h = self._condition_h(block, w)
        left = w * 0.38
        inside = self.panel(x, y, left, h, "Fatigue Levels")
        small = _font(7.5)
        for i, row in enumerate(block.fatigue.rows):
            ry = inside.y() + i * 13
            self.box(inside.x(), ry + 2, row.ticked)
            self.text(
                QRectF(inside.x() + 14, ry, 22, 13),
                row.penalty,
                _font(9.5),
                None,
                RIGHT_ALIGN,
            )
            self.text(
                QRectF(inside.x() + 40, ry + 1.5, 40, 13),
                row.recovery,
                small,
                self.label,
            )
            self.text(
                QRectF(inside.x() + 80, ry, inside.width() - 80, 13),
                row.name,
                _font(9.5),
            )
        inside = self.panel(x + left + 10, y, w - left - 10, h, "Wounds")
        ix, iw = inside.x(), inside.width()
        at = (0.0, 0.32, 0.50, 0.74, 0.88)
        for title, share in zip(
            ("", "Range", "Number", "Penalty", "Notes"), at, strict=True
        ):
            self.text(
                QRectF(ix + share * iw, inside.y() - 2, 60, 10),
                title,
                _font(7.5, caps=True),
                self.label,
            )
        for i, row in enumerate(block.wounds.rows):
            ry = inside.y() + 10 + i * 13
            name = f"{row.name} Wounds" if row.boxes > 1 else row.name
            self.text(QRectF(ix, ry, iw * 0.32, 13), name, _font(9.5))
            self.text(QRectF(ix + at[1] * iw, ry, 50, 13), row.range, _font(9.5))
            for k in range(row.boxes):
                self.box(ix + at[2] * iw + k * 11, ry + 2, k < row.ticked)
            self.text(QRectF(ix + at[3] * iw, ry, 30, 13), row.penalty, _font(9.5))
            self.blank(ix + at[4] * iw, ry + 11, iw * 0.12)

    def _combat(self, block: pl.CombatSummary, x: float, y: float, w: float) -> None:
        inside = self.panel(x, y, w, 64, "Combat")
        ix, iy, iw = inside.x(), inside.y(), inside.width()
        label = _font(7.5, caps=True)
        for k, (title, value) in enumerate(
            (("Armor Worn", block.armour), ("Modifiers", ""))
        ):
            ry = iy + k * 18
            self.text(QRectF(ix, ry, 70, 12), title, label, self.label)
            if value:
                self.text(QRectF(ix + 70, ry - 2, iw * 0.5, 13), value, _font(9.5))
            self.blank(ix + 70, ry + 10, iw * 0.5)
        for k, (title, value) in enumerate(
            (
                ("Soak", block.soak),
                ("Load", block.load),
                ("Encumbrance", block.encumbrance),
            )
        ):
            bx, bw = ix + iw * 0.66 + k * iw * 0.115, iw * 0.11
            self.text(QRectF(bx, iy - 2, bw, 12), title, label, self.label, CENTRE)
            self.text(
                QRectF(bx, iy + 10, bw, 16), value, _font(13, bold=True), None, CENTRE
            )
            self.blank(bx + 6, iy + 28, bw - 12)

    #: The Weapons table's columns: the weapon, the four sums, Load, Range.
    WEAPON_SHARES = (0.22, 0.17, 0.17, 0.17, 0.13, 0.07, 0.07)

    def _weapons(self, block: pl.Weapons, x: float, y: float, w: float) -> None:
        h = self.measure(block, w)
        inside = self.panel(x, y, w, h, "Weapons")
        ix, iy, iw = inside.x(), inside.y(), inside.width()
        xs, at = [], ix
        for share in self.WEAPON_SHARES:
            xs.append(at)
            at += share * iw
        titles = (
            [("Weapon", "")]
            + [(t, s) for t, s, _ in pl.WEAPON_SUMS]
            + [("Load", ""), ("Range", "")]
        )
        for cx, share, (title, sums) in zip(
            xs, self.WEAPON_SHARES, titles, strict=True
        ):
            self.text(
                QRectF(cx, iy - 2, share * iw, 10),
                title,
                _font(8, bold=True, caps=True),
                None,
                CENTRE,
            )
            self.text(
                QRectF(cx, iy + 7, share * iw, 9), sums, _font(6.5), self.label, CENTRE
            )
        value = _font(10, bold=True)
        for r, row in enumerate(block.rows):
            ry = iy + 22 + r * 15
            if row.name:
                self.text(
                    QRectF(xs[0], ry, self.WEAPON_SHARES[0] * iw, 13),
                    row.name,
                    _font(9.5),
                )
                totals = (row.initiative, row.attack, row.defence, row.damage, row.load)
                for i, total in enumerate(totals, start=1):
                    self.text(
                        QRectF(xs[i], ry, self.WEAPON_SHARES[i] * iw, 13),
                        total,
                        value,
                        None,
                        CENTRE,
                    )
                continue
            self.blank(xs[0], ry + 11, self.WEAPON_SHARES[0] * iw - 6)
            for i, (_, _, ops) in enumerate(pl.WEAPON_SUMS, start=1):
                step = self.WEAPON_SHARES[i] * iw / (len(ops) + 1.6)
                for k, op in enumerate(ops):
                    rect = QRectF(xs[i] + (k + 0.6) * step, ry, step, 13)
                    self.text(rect, op, _font(8), self.label, CENTRE)
                self.blank(xs[i] + (len(ops) + 0.5) * step, ry + 11, step * 1.1)
            for i in (5, 6):
                self.blank(xs[i] + 4, ry + 11, self.WEAPON_SHARES[i] * iw - 8)

    def _equipment(self, block: pl.Equipment, x: float, y: float, w: float) -> None:
        inside = self.panel(x, y, w, self.measure(block, w), "Equipment")
        half = (inside.width() - 16) / 2
        for k in range(block.lines * 2):
            column, row = divmod(k, block.lines)
            gx, gy = inside.x() + column * (half + 16), inside.y() + row * 14
            if k < len(block.items):
                self.text(QRectF(gx, gy - 1, half, 13), block.items[k], _font(9.5))
            self.blank(gx, gy + 11, half)

    def _grimoire_title(
        self, block: pl.GrimoireTitle, x: float, y: float, w: float
    ) -> None:
        self.text(
            QRectF(x, y, w, 30),
            "Grimoire",
            _font(22, family=pictures.DISPLAY),
            self.red,
            CENTRE,
        )
        words = f"the formulaic spells of {block.owner}"
        self.text(
            QRectF(x, y + 30, w, 14),
            words,
            _font(10.5, italic=True),
            self.label,
            CENTRE,
        )
        self.text(QRectF(x, y + 44, w, 16), "❧  ✠  ☙", _font(12), self.gold, CENTRE)

    def _spell(self, block: pl.Spell, x: float, y: float, w: float) -> None:
        self.text(QRectF(x, y, w, 16), block.name, _font(11.5, bold=True, caps=True))
        self.text(
            QRectF(x, y, w, 16),
            block.arts,
            _font(10.5, bold=True),
            self.red,
            RIGHT_ALIGN,
        )
        self.text(QRectF(x + 10, y + 16, w - 10, 13), block.parameters, _font(9.5))
        self.text(
            QRectF(x + 10, y + 29, w - 10, 13),
            block.casting,
            _font(9, italic=True),
            self.label,
        )
        if block.description:
            self.text(
                QRectF(x + 10, y + 44, w - 10, 100000), block.description, _font(9.5)
            )

    # ------------------------------------------------------------ pages

    def frame(self, number: int) -> None:
        """The page's paper, its edge and its foot; from the second page,
        the name at its head."""
        qp = self.qp
        page = QRectF(0, 0, self.page_size.width(), self.page_size.height())
        if self.textured:
            qp.drawTiledPixmap(page, paper(self.p))
        else:
            qp.fillRect(page, QColor("white"))
        outer = page.adjusted(OUTER, OUTER, -OUTER, -OUTER)
        inner = page.adjusted(INNER, INNER, -INNER, -INNER)
        qp.setPen(QPen(self.gold, 1.4))
        qp.drawRect(outer)
        qp.setPen(QPen(self.rule, 0.5))
        qp.drawRect(inner)
        band = QRectF(outer.left() + 6, inner.top() + 30, 9, inner.height() - 60)
        qp.fillRect(band, self.red)
        for k in range(int(band.top()) + 8, int(band.bottom()) - 4, 14):
            self.line(self.gold, 0.6, band.left() + 1.5, k, band.right() - 1.5, k + 5)
        for cx, cy in (
            (outer.left(), outer.top()),
            (outer.right(), outer.top()),
            (outer.left(), outer.bottom()),
            (outer.right(), outer.bottom()),
        ):
            qp.fillRect(QRectF(cx - 6, cy - 6, 12, 12), self.page_colour)
            self.text(
                QRectF(cx - 8, cy - 9, 16, 18),
                "❦",
                _font(13),
                self.gold,
                Align.AlignCenter,
            )
        foot = QRectF(LEFT, page.height() - 46, self.width, 12)
        self.text(
            foot,
            f"{self.doc.title}  ·  {self.doc.subtitle}",
            _font(8, italic=True),
            self.label,
        )
        self.text(foot, str(number), _font(8.5), self.label, RIGHT_ALIGN)
        if number > 1:
            head = QRectF(LEFT, 34, self.width, 16)
            self.text(
                head,
                self.doc.title,
                _font(10, family=pictures.DISPLAY),
                self.red,
                RIGHT_ALIGN,
            )

    def pieces(self) -> list[pl.Piece]:
        pieces = []
        for block in self.doc.blocks:
            if isinstance(block, pl.NewPage):
                pieces.append(pl.Piece(0, new_page=True))
            elif isinstance(block, pl.Table):
                pieces.append(
                    pl.Piece(
                        self._table_h(block, self.width),
                        GAP,
                        header=self.HEAD,
                        rows=tuple(self._row_heights(block)),
                    )
                )
            else:
                keep = isinstance(block, pl.Heading)
                gap = 3.0 if keep else GAP
                pieces.append(pl.Piece(self.measure(block, self.width), gap, keep))
        return pieces

    def print(self) -> int:
        """Draw the document; how many pages it took."""
        pages = pl.paginate(self.pieces(), self.height)
        self.painter = QPainter(self.writer)
        self.qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        try:
            for number, page in enumerate(pages, start=1):
                if number > 1:
                    self.writer.newPage()
                self.frame(number)
                for place in page:
                    block = self.doc.blocks[place.index]
                    self.paint(block, LEFT, TOP + place.top, self.width, place)
        finally:
            self.qp.end()
            self.painter = None
        return len(pages)


def print_document(
    doc: pl.Document, path: Path, options: pl.PrintOptions = pl.DEFAULT_OPTIONS
) -> int:
    """Print `doc` to the PDF at `path`; how many pages it took."""
    if pictures.DISPLAY not in QFontDatabase.families():
        pictures.register_fonts()
    return Sheet(path, doc, options).print()
