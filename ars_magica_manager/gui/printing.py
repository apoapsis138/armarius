"""A record's page printed to a PDF: its header, then each chapter in
turn, drawn for paper in the parchment palette, with the buttons and the
inspector left off.

It adapts the page the window already draws rather than laying the
record out a second time, so the paper always says what the screen does.
Each chapter is laid out at the paper's width and cut into pages between
its sections where it can, else between its rows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QMarginsF, QPoint, QRect, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QPageLayout,
    QPageSize,
    QPainter,
    QPdfWriter,
    QPixmap,
    QRegion,
)
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import print_layout as pl
from . import pictures
from .editing import Section
from .paper import paper
from .themes import SCRIPTORUM, Palette, style_sheet
from .widgets import Codex, NewCard, serif

#: Dots per inch of the PDF's page units: an A4 page is then about as wide
#: as the page's chapters are on screen.
RESOLUTION = 120
#: How many dots each of the page's pixels is drawn with: about 300 dots
#: an inch on paper.
SHARPNESS = 2.5
#: The margin round each page, in millimetres.
MARGIN_MM = 12.0
#: Chapters left off the paper: managing the record as a file, and the
#: season's plans, which are for the screen.
LEFT_OFF = frozenset({"Manage", "Planning", "Seasons"})
#: A section's title is never left at the foot of a page with less than
#: this much of the section under it.
KEEP_WITH_TITLE = 90
#: The space above each chapter's title, and the title's height.
GAP, TITLE = 18, 34

#: The palette paper is printed in.
PARCHMENT: Palette = SCRIPTORUM


def file_stem(name: str) -> str:
    """`name` as a file name: without the characters Windows refuses."""
    return re.sub(r'[\\/:*?"<>|]', "", name).strip() or "Untitled"


def _hide_controls(page: QWidget) -> None:
    """Leave the buttons that act on the page off the paper."""
    for button in page.findChildren(QPushButton):
        if button.objectName() in ("edit", "crumb"):
            button.hide()
    for card in page.findChildren(NewCard):
        card.hide()


@dataclass(frozen=True)
class _Breaks:
    """Where a chapter can be cut between pages: the tops of the parts of
    it that run its full width (its sections, and their rows), so a cut
    never goes through one of two columns; and the tops of its sections,
    whose titles stay with what is under them."""

    tops: list[int]
    sections: list[int]

    @classmethod
    def of(cls, body: QWidget) -> _Breaks:
        width, height = body.width(), body.height()
        tops, sections = {height}, set()
        for child in body.findChildren(QWidget):
            if not child.isVisibleTo(body) or child.width() < width * 0.6:
                continue
            top = child.mapTo(body, QPoint(0, 0)).y()
            if 0 < top < height:
                tops.add(top)
                if isinstance(child, Section):
                    sections.add(top)
        return cls(sorted(tops), sorted(sections))

    def cut(self, start: int, room: int) -> int:
        """Where the slice starting at `start` should end, given `room` on
        the page: the last break that fits, if it leaves the page at least
        a third full, else as far as the page goes; moved up to a
        section's top rather than leave its title alone at the foot."""
        fits = [y for y in self.tops if start < y <= start + room]
        if fits and (fits[-1] - start >= room // 3 or fits[-1] == self.tops[-1]):
            stop = fits[-1]
        else:
            stop = start + room
        if stop == self.tops[-1]:
            return stop
        for top in self.sections:
            if stop - KEEP_WITH_TITLE < top < stop and top - start >= room // 3:
                return top
        return stop


class _Printer:
    """Draws onto the PDF a page at a time, keeping track of where the
    next part goes."""

    def __init__(self, path: Path, title: str, p: Palette, size: str = pl.A4) -> None:
        self.p = p
        self.writer = QPdfWriter(str(path))
        self.writer.setTitle(title)
        self.writer.setCreator("Armarius")
        self.writer.setResolution(RESOLUTION)
        self.writer.setPageLayout(
            QPageLayout(
                QPageSize(
                    QPageSize.PageSizeId.Letter
                    if size == pl.LETTER
                    else QPageSize.PageSizeId.A4
                ),
                QPageLayout.Orientation.Portrait,
                QMarginsF(MARGIN_MM, MARGIN_MM, MARGIN_MM, MARGIN_MM),
                QPageLayout.Unit.Millimeter,
            )
        )
        self.painter = QPainter(self.writer)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        whole = self.writer.pageLayout().fullRectPixels(RESOLUTION)
        self.area = self.writer.pageLayout().paintRectPixels(RESOLUTION)
        #: The page's paper, in the painter's coordinates (which start at
        #: the margin).
        self.sheet = QRect(whole).translated(-self.area.left(), -self.area.top())
        self.width = self.area.width()
        self.y = 0
        self.pages = 1
        self._paper()

    def _paper(self) -> None:
        self.painter.drawTiledPixmap(self.sheet, paper(self.p))

    def new_page(self) -> None:
        self.writer.newPage()
        self.pages += 1
        self.y = 0
        self._paper()

    def room(self) -> int:
        return self.area.height() - self.y

    def chapter(self, words: str, body: QWidget) -> None:
        """A chapter: its title, then `body`, starting on a new page when
        too little of it would fit under the title."""
        if self.y:
            room = self.room() - GAP - TITLE
            first = _Breaks.of(body).cut(0, room) if room > 0 else 0
            if first < min(body.height(), KEEP_WITH_TITLE * 2):
                self.new_page()
        self.title(words)
        self.body(body)

    def title(self, words: str) -> None:
        if self.y:
            self.y += GAP
        painter, p = self.painter, self.p
        font = serif(17, bold=True)
        font.setCapitalization(font.Capitalization.SmallCaps)
        painter.setFont(font)
        painter.setPen(QColor(p["heading"]))
        line = QRectF(0, self.y, self.width, TITLE - 6)
        painter.drawText(
            line, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, words
        )
        painter.setPen(QColor(p["rule"]))
        painter.drawLine(0, self.y + TITLE - 4, self.width, self.y + TITLE - 4)
        self.y += TITLE

    def body(self, widget: QWidget, top: int = 0, bottom: int | None = None) -> None:
        """Draw `widget` from `top` to `bottom`, onto as many pages as it
        takes."""
        end = widget.height() if bottom is None else bottom
        breaks = _Breaks.of(widget)
        start = top
        while start < end:
            if self.room() < 60:
                self.new_page()
            stop = min(breaks.cut(start, self.room()), end)
            if stop <= start:
                self.new_page()
                continue
            self._draw(widget, start, stop)
            self.y += stop - start
            start = stop
            if start < end:
                self.new_page()

    def _draw(self, widget: QWidget, start: int, stop: int) -> None:
        """Draw `widget`'s rows `start` to `stop` at the page's next place,
        as the screen draws it, at print sharpness."""
        width, height = widget.width(), stop - start
        picture = QPixmap(QSize(width, height) * SHARPNESS)
        picture.setDevicePixelRatio(SHARPNESS)
        picture.fill(Qt.GlobalColor.transparent)
        widget.render(
            picture,
            QPoint(0, 0),
            QRegion(0, start, width, height),
            QWidget.RenderFlag.DrawChildren,
        )
        self.painter.drawPixmap(
            QRectF(0, self.y, width, height), picture, QRectF(picture.rect())
        )

    def end(self) -> None:
        self.painter.end()


def _laid_out(body: QWidget, width: int) -> None:
    """Lay `body` out at `width`, as tall as it needs."""
    body.setFixedWidth(width)
    layout = body.layout()
    if layout is not None:
        layout.activate()
    height = body.heightForWidth(width)
    if height <= 0:
        height = body.sizeHint().height()
    body.setFixedHeight(height)
    QApplication.processEvents()


def print_page(
    page: QWidget,
    path: Path,
    title: str,
    p: Palette = PARCHMENT,
    size: str = pl.A4,
) -> int:
    """Print `page` (a record's page, built in palette `p`) to the PDF at
    `path` on paper `size` (print_layout's LETTER or A4); how many pages it
    took."""
    codex = page.findChild(Codex)
    host = QWidget()
    host.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
    host.setStyleSheet(style_sheet(p, pictures.SERIF))
    column = QVBoxLayout(host)
    column.setContentsMargins(0, 0, 0, 0)
    column.addWidget(page)
    printer = _Printer(path, title, p, size)
    host.resize(printer.width, 900)
    _hide_controls(page)
    host.show()
    QApplication.processEvents()
    try:
        if codex is not None:
            codex.rail.hide()
            codex.inspector.hide()
            header = codex.mapTo(page, QPoint(0, 0)).y()
            if header > 0:
                printer.body(page, 0, header)
            for index, name in enumerate(codex.chapters()):
                if name in LEFT_OFF:
                    continue
                codex.rail.setCurrentRow(index)
                chapter = codex.pages.widget(index)
                body = chapter.widget() if isinstance(chapter, QScrollArea) else chapter
                if body is None:
                    continue
                if isinstance(chapter, QScrollArea):
                    chapter.setWidgetResizable(False)
                _laid_out(body, printer.width)
                printer.chapter(name, body)
        else:
            _laid_out(page, printer.width)
            printer.body(page)
    finally:
        printer.end()
        host.close()
        host.deleteLater()
    return printer.pages
