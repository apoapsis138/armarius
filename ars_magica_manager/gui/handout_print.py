"""Any Handout a player holds, printed to a PDF on the desktop: the pages
print_handouts lays out, drawn by the printed sheet's renderer
(print_sheet). A record's copy and a picture are printed on its usual
Scriptorum page; a written Handout on its Stationery, each page drawn as
its window draws it (handout_page.paint_stationery): the paper, toned, its
creases and edge, with the title set as the Stationery sets it on the
first page and the seal at the foot of the last.

Pattern: the desktop's half of the Bridge handout_layout describes, and
a subclass of the renderer for the one thing that differs, the page under
the words (Template Method: Sheet.draw calls frame and the title's
painter, which StationerySheet overrides)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import QRectF
from PySide6.QtGui import QFont, QFontDatabase, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from .. import handout_layout as hl
from .. import print_layout as pl
from . import pictures
from .handout_page import SEAL, Banner, paint_stationery
from .print_sheet import CENTRE, Sheet, _font, print_document, rendered
from .style.ornaments import Headpiece, ShortRule
from .themes import SCRIPTORUM

#: The pixels a point a Stationery's page is drawn at, under its words:
#: its paper and edge print sharp without making the PDF large.
GROUND_PIXELS_PER_POINT = 2


class StationerySheet(Sheet):
    """A written Handout drawn on its Stationery: always on its paper, in
    the light Scriptorum palette, inside the Stationery's own margins, with
    no running head or foot (a letter has none)."""

    def __init__(self, path: Path, doc: pl.Document, options: pl.PrintOptions) -> None:
        super().__init__(path, doc, replace(options, textured=True), SCRIPTORUM.name)
        self.sheet = hl.stationery(doc.stationery)
        wide, tall = self.page_size.width(), self.page_size.height()
        side = wide * self.sheet.margin
        foot = side + (SEAL + 12 if self.sheet.seal else 0)
        self.left = self.top = side
        self.width = wide - 2 * side
        self.height = tall - side - foot
        self._measures[pl.Title] = self._stationery_title_h
        self._painters[pl.Title] = self._stationery_title
        #: The page under the words, drawn once each without and with its
        #: seal.
        self._grounds: dict[bool, QPixmap] = {}

    # -- the title, as its Stationery sets it --

    def _heading_font(self) -> QFont:
        return _font(20, family=pictures.DISPLAY)

    def _stationery_title_h(self, block: pl.Title, width: float) -> float:
        where = self.sheet.title
        if where == hl.TITLE_BANNER:
            return Headpiece.HEIGHT + Banner(block.name, width).height() + 6
        if where == hl.TITLE_DOCKET:
            return self.text_height(block.name, _font(10.5, italic=True), width) + 8
        title = self.text_height(block.name, self._heading_font(), width)
        return title + ShortRule.HEIGHT

    def _stationery_title(self, block: pl.Title, x: float, y: float, w: float) -> None:
        where = self.sheet.title
        if where == hl.TITLE_DOCKET:
            self.text(
                QRectF(x, y, w, 1000), block.name, _font(10.5, italic=True), self.label
            )
            return
        if where == hl.TITLE_BANNER:
            self._ornament(Headpiece(self.p), x, y, w, Headpiece.HEIGHT)
            banner = Banner(block.name, w)
            self._ornament(banner, x, y + Headpiece.HEIGHT, w, banner.height())
            return
        font = self._heading_font()
        tall = self.text_height(block.name, font, w)
        self.text(QRectF(x, y, w, tall), block.name, font, self.red, CENTRE)
        self._ornament(ShortRule(self.p), x, y + tall, w, ShortRule.HEIGHT)

    def _ornament(
        self, widget: QWidget, x: float, y: float, w: float, h: float
    ) -> None:
        picture = rendered(widget, w, h)
        self.qp.drawPixmap(QRectF(x, y, w, h), picture, QRectF(picture.rect()))

    # -- the page under the words --

    def _ground(self, sealed: bool) -> QPixmap:
        found = self._grounds.get(sealed)
        if found is None:
            wide, tall = self.page_size.width(), self.page_size.height()
            found = QPixmap(
                round(wide * GROUND_PIXELS_PER_POINT),
                round(tall * GROUND_PIXELS_PER_POINT),
            )
            found.setDevicePixelRatio(GROUND_PIXELS_PER_POINT)
            painter = QPainter(found)
            paint_stationery(
                painter, QRectF(0, 0, wide, tall), self.sheet, sealed=sealed
            )
            painter.end()
            self._grounds[sealed] = found
        return found

    def frame(self, number: int) -> None:
        """The page's Stationery; its seal on the last page alone."""
        ground = self._ground(number == self.page_count)
        page = QRectF(0, 0, self.page_size.width(), self.page_size.height())
        self.qp.drawPixmap(page, ground, QRectF(ground.rect()))


def print_handout(
    doc: pl.Document, path: Path, options: pl.PrintOptions = pl.DEFAULT_OPTIONS
) -> int:
    """Print a Handout's pages (print_handouts.document) to the PDF at
    `path`: a written one on its Stationery, any other in Scriptorum; how
    many pages it took."""
    if not doc.stationery:
        return print_document(doc, path, options, SCRIPTORUM.name)
    if pictures.DISPLAY not in QFontDatabase.families():
        pictures.register_fonts()
    return StationerySheet(path, doc, options).print()
