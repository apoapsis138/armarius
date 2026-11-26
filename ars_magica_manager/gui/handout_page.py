"""A written Handout drawn on its Stationery, on the desktop: the page a
storyguide's Preview opens, and a player's copy once Shown.

The page is laid out by the core (handout_layout.Laid: the blocks, where
each stands, the Stationery's proportions, margins, title, edge, seal
and folds); everything drawn here is the desktop's own look (ADR 0008),
in code from gui/style under the no-generative-art rule: the laid paper,
toned for each Stationery, a scribe's ruled frame or a gilt one with its
corner flourishes, a letter's creases, a wax seal, the illuminated
initial, a hedera flourish, and the text in the app's book face. A
Handout is drawn in the light Scriptorum palette on any theme, so it
looks the same on every desktop.

Pattern: the desktop's half of the Bridge handout_layout describes."""

from __future__ import annotations

import html
import math
import random
from collections.abc import Sequence

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import handout_layout as layout
from .. import handout_markup as hm
from ..handout_layout import Laid, Placed, Preview, Stationery
from ..models import PROCLAMATION, SEALED_LETTER, VELLUM
from ..style import fonts
from ..style.palettes import DRAWN, PIGMENTS
from .markup_html import to_html
from .style.gilding import gilt_frame, gilt_word
from .style.illumination import IlluminatedInitial
from .style.ornaments import Headpiece, ShortRule, corner_flourishes
from .style.paper import paper, shade
from .style.pieces import serif
from .themes import SCRIPTORUM, Palette

#: The palette every Handout is drawn in, whatever the app's theme.
INK: Palette = SCRIPTORUM

#: The page's width, in pixels; its height is the Stationery's aspect of
#: that, or more for a long text.
PAGE_WIDTH = 620

#: Each Stationery's tone over the laid paper, and how dark its edges
#: grow: a vellum's warm skin, a letter's fresh paper, a proclamation's
#: heavy parchment.
TONES: dict[str, tuple[str, int, int]] = {
    VELLUM: (DRAWN["vellum"], 46, 70),
    SEALED_LETTER: (DRAWN["letter-paper"], 70, 40),
    PROCLAMATION: (DRAWN["proclamation"], 60, 95),
}

#: The side of a seal, in pixels, and the room it takes at the foot.
SEAL = 64.0

#: The tallest a placed picture is drawn, in pixels.
PICTURE_TALLEST = 320

#: The illuminated initial's side, in pixels.
INITIAL_SIDE = 58


def _label(words: str, font: QFont, align: str, colour: str) -> QLabel:
    """A block's words (markup) as rich text, wrapped, set where it
    stands."""
    label = QLabel(to_html(words, INK))
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    label.setFont(font)
    label.setStyleSheet(f"color:{colour}; background:transparent")
    label.setAlignment(_ALIGN[align] | Qt.AlignmentFlag.AlignTop)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    return label


_ALIGN = {
    layout.LEFT: Qt.AlignmentFlag.AlignLeft,
    layout.CENTRE: Qt.AlignmentFlag.AlignHCenter,
    layout.RIGHT: Qt.AlignmentFlag.AlignRight,
}


#: The sizes a proclamation's title is set at: as large as fits on one
#: line, down to the smallest a long title wraps at.
BANNER_LARGEST, BANNER_WRAPS, BANNER_SMALLEST = 26.0, 18.0, 10.0


def _wrapped(words: str, metrics: QFontMetricsF, width: float) -> list[str] | None:
    """`words` broken into lines no wider than `width`, or None when one
    word alone is wider."""
    lines: list[str] = []
    for word in words.split():
        if metrics.horizontalAdvance(word) > width:
            return None
        joined = f"{lines[-1]} {word}" if lines else word
        if lines and metrics.horizontalAdvance(joined) <= width:
            lines[-1] = joined
        else:
            lines.append(word)
    return lines


class Banner(QWidget):
    """A proclamation's title: the words in the display face, red with a
    gilt edge to each letter, centred; as large as fits on one line, else
    wrapped over several, each within the page's measure."""

    def __init__(self, title: str, width: float) -> None:
        super().__init__()
        self.setObjectName("handout-title")
        self.title = title
        self.font_ = QFont(fonts.DISPLAY)
        room = width - 8
        size, lines = BANNER_LARGEST, None
        while lines is None and size >= BANNER_SMALLEST:
            self.font_.setPointSizeF(size)
            metrics = QFontMetricsF(self.font_)
            if metrics.horizontalAdvance(title) <= room:
                lines = [title]
            elif size <= BANNER_WRAPS:
                lines = _wrapped(title, metrics, room)
            size -= 1
        #: The title's lines as drawn.
        self.lines = lines or [title]
        metrics = QFontMetricsF(self.font_)
        self.setFixedHeight(round(metrics.lineSpacing() * len(self.lines)) + 10)
        self.setToolTip(html.escape(title))

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        metrics = QFontMetricsF(self.font_)
        for row, line in enumerate(self.lines):
            x = max(0.0, (self.width() - metrics.horizontalAdvance(line)) / 2)
            y = metrics.ascent() + 4 + row * metrics.lineSpacing()
            gilt_word(painter, line, self.font_, QPointF(x, y), INK)
        painter.end()


class _Placeholder(QLabel):
    """Where a picture this computer hasn't got would be: a ruled box
    naming it."""

    def __init__(self, block: Placed) -> None:
        super().__init__(f"Picture {block.picture}: {block.caption}")
        self.setObjectName("handout-placeholder")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(serif(11.5, italic=True))
        self.setMinimumHeight(90)
        self.setWordWrap(True)
        self.setStyleSheet(
            f"color:{INK['label']}; background:transparent;"
            f" border:1px dashed {INK['rule']}"
        )


class HandoutPage(QWidget):
    """A laid-out Handout on its Stationery: the page painted, the title
    and blocks set on it as its Stationery says. `pictures` are its
    pictures by number less one (None for one this computer hasn't got,
    drawn as a placeholder naming it)."""

    def __init__(self, laid: Laid, pictures: Sequence[QPixmap | None] = ()) -> None:
        super().__init__()
        self.setObjectName("handout-page")
        self.laid = laid
        self.pictures = list(pictures)
        sheet = laid.stationery
        self.setFixedWidth(PAGE_WIDTH)
        side = round(PAGE_WIDTH * sheet.margin)
        self.measure = PAGE_WIDTH - 2 * side
        foot = side + (round(SEAL) + 12 if sheet.seal else 0)
        column = QVBoxLayout(self)
        column.setContentsMargins(side, side, side, foot)
        column.setSpacing(10)
        #: What each block was drawn as, in order (for its tests).
        self.drawn: list[QWidget] = []
        self._title(column)
        for block in laid.blocks:
            widget = self._block(block)
            self.drawn.append(widget)
            column.addWidget(widget)
        column.addStretch(1)
        column.activate()
        # The height the words take wrapped at the page's own width, not
        # at the wider lines a label would choose for itself.
        tall = (
            column.heightForWidth(PAGE_WIDTH)
            if column.hasHeightForWidth()
            else column.sizeHint().height()
        )
        self.setMinimumHeight(max(round(PAGE_WIDTH * sheet.aspect), tall))

    # -- the words on it --

    def _title(self, column: QVBoxLayout) -> None:
        title, where = self.laid.title, self.laid.stationery.title
        if where == layout.TITLE_BANNER:
            column.addWidget(Headpiece(INK))
            column.addWidget(Banner(title, self.measure))
            column.addSpacing(6)
        elif where == layout.TITLE_DOCKET:
            docket = QLabel(title)
            docket.setTextFormat(Qt.TextFormat.PlainText)
            docket.setFont(serif(11, italic=True))
            docket.setWordWrap(True)
            docket.setStyleSheet(f"color:{INK['label']}; background:transparent")
            docket.setObjectName("handout-title")
            column.addWidget(docket)
            column.addSpacing(8)
            return
        else:
            heading = QLabel(title)
            # Plain: a title like "Letter <to the Abbot>" is words, not HTML.
            heading.setTextFormat(Qt.TextFormat.PlainText)
            heading.setFont(_display(20))
            heading.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            heading.setWordWrap(True)
            heading.setStyleSheet(f"color:{INK['heading']}; background:transparent")
            heading.setObjectName("handout-title")
            column.addWidget(heading)
            column.addWidget(ShortRule(INK))

    def _block(self, block: Placed) -> QWidget:
        ink = INK["foreground"]
        if block.kind == hm.HEADING:
            return _label(
                block.text, serif(16, bold=True, caps=True), block.align, INK["heading"]
            )
        if block.kind == hm.FLOURISH:
            return ShortRule(INK)
        if block.kind == hm.PICTURE:
            return self._picture(block)
        if block.kind == hm.INITIAL and block.initial:
            row = QWidget()
            line = QHBoxLayout(row)
            line.setContentsMargins(0, 0, 0, 0)
            line.setSpacing(4)
            initial = IlluminatedInitial(block.initial, INK, INITIAL_SIDE)
            initial.setObjectName("handout-initial")
            line.addWidget(initial, 0, Qt.AlignmentFlag.AlignTop)
            line.addWidget(_label(block.text, serif(13.5), block.align, ink), 1)
            return row
        return _label(block.text, serif(13.5), block.align, ink)

    def _picture(self, block: Placed) -> QWidget:
        found = (
            self.pictures[block.picture - 1]
            if block.picture <= len(self.pictures)
            else None
        )
        if found is None or found.isNull():
            return _Placeholder(block)
        if found.width() > self.measure or found.height() > PICTURE_TALLEST:
            found = found.scaled(
                round(self.measure),
                PICTURE_TALLEST,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        label = QLabel()
        label.setObjectName("handout-picture")
        label.setPixmap(found)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setToolTip(block.caption)
        return label

    # -- the page itself --

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        paint_stationery(painter, QRectF(self.rect()), self.laid.stationery)
        painter.end()


def paint_stationery(
    painter: QPainter, page: QRectF, sheet: Stationery, *, sealed: bool = True
) -> None:
    """A Stationery's page under its words: the paper, toned, its creases,
    its edge and, where it has one and `sealed`, its seal (on a printed
    Handout, only its last page's). The window's page and the printed
    pages are drawn by this alone, so they can't disagree."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _paper(painter, page, sheet.name)
    for fold in range(1, sheet.folds + 1):
        _crease(painter, page, page.top() + page.height() * fold / (sheet.folds + 1))
    inset = edge_inset(sheet, page.width())
    edge = page.adjusted(inset, inset, -inset, -inset)
    if sheet.edge == layout.EDGE_RULED:
        _ruled(painter, edge)
    elif sheet.edge == layout.EDGE_GILT:
        gilt_frame(painter, edge, INK)
        corner_flourishes(painter, edge.adjusted(6, 6, -6, -6), INK, 22)
    if sheet.seal and sealed:
        hanging = sheet.edge == layout.EDGE_GILT
        cx = page.center().x() if hanging else page.right() - inset - SEAL
        _seal(painter, QPointF(cx, page.bottom() - inset - SEAL / 2 - 4), hanging)


def edge_inset(sheet: Stationery, width: float) -> float:
    """How far a Stationery's edge is drawn in from a page `width` wide."""
    return width * sheet.margin * 0.45


def _display(size: float) -> QFont:
    font = QFont(fonts.DISPLAY)
    font.setPointSizeF(size)
    return font


def _paper(painter: QPainter, page: QRectF, name: str) -> None:
    """The laid paper, toned for its Stationery and darker toward its
    edges."""
    painter.drawTiledPixmap(page, paper(INK))
    tone, alpha, edges = TONES.get(name, TONES[VELLUM])
    painter.fillRect(page, shade(tone, alpha))
    reach = max(page.width(), page.height()) * 0.75
    vignette = QRadialGradient(page.center(), reach)
    vignette.setColorAt(0.55, shade(INK["paper-fleck"], 0))
    vignette.setColorAt(1.0, shade(INK["paper-fleck"], edges))
    painter.fillRect(page, vignette)


def _crease(painter: QPainter, page: QRectF, y: float) -> None:
    """Where a letter was folded: a fine shadow across the page with a
    lighter edge under it."""
    shadow = QLinearGradient(page.left(), y, page.right(), y)
    for stop, alpha in ((0.0, 10), (0.5, 55), (1.0, 10)):
        shadow.setColorAt(stop, shade(INK["shadow"], alpha))
    painter.setPen(QPen(shadow, 1.2))
    painter.drawLine(QPointF(page.left(), y), QPointF(page.right(), y))
    painter.setPen(QPen(shade(INK["paper-sheen"], 120), 1))
    painter.drawLine(QPointF(page.left(), y + 1.5), QPointF(page.right(), y + 1.5))


def _ruled(painter: QPainter, edge: QRectF) -> None:
    """A scribe's frame ruled in red, the lines run on past each corner,
    as pricked and ruled on a skin before it is written."""
    painter.setPen(QPen(shade(INK["heading"], 150), 0.9))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    over = 10.0
    for rect in (edge, edge.adjusted(5, 5, -5, -5)):
        painter.drawLine(
            QPointF(rect.left() - over, rect.top()),
            QPointF(rect.right() + over, rect.top()),
        )
        painter.drawLine(
            QPointF(rect.left() - over, rect.bottom()),
            QPointF(rect.right() + over, rect.bottom()),
        )
        painter.drawLine(
            QPointF(rect.left(), rect.top() - over),
            QPointF(rect.left(), rect.bottom() + over),
        )
        painter.drawLine(
            QPointF(rect.right(), rect.top() - over),
            QPointF(rect.right(), rect.bottom() + over),
        )


def _seal(painter: QPainter, centre: QPointF, hanging: bool) -> None:
    """A seal of red wax at `centre`, its rim uneven where it spread,
    pressed with a cross in a ring; `hanging` from two cords, as a
    proclamation's is."""
    radius = SEAL / 2
    if hanging:
        for side in (-1, 1):
            cord = QPainterPath(
                QPointF(centre.x() + side * 8, centre.y() - radius - 24)
            )
            cord.cubicTo(
                QPointF(centre.x() + side * 18, centre.y() - radius),
                QPointF(centre.x() + side * 4, centre.y()),
                QPointF(centre.x() + side * 16, centre.y() + radius + 10),
            )
            painter.setPen(QPen(QColor(PIGMENTS["vermilion-deep"]), 3.2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(cord)
    chance = random.Random(11)
    rim = QPainterPath()
    points = 28
    for k in range(points + 1):
        angle = math.tau * (k % points) / points
        reach = radius * (1 + chance.uniform(-0.06, 0.06))
        point = QPointF(
            centre.x() + reach * math.cos(angle), centre.y() + reach * math.sin(angle)
        )
        if k == 0:
            rim.moveTo(point)
        else:
            rim.lineTo(point)
    rim.closeSubpath()
    wax = QRadialGradient(centre - QPointF(radius * 0.3, radius * 0.3), radius * 1.3)
    wax.setColorAt(0.0, QColor(PIGMENTS["vermilion"]))
    wax.setColorAt(1.0, QColor(PIGMENTS["vermilion-deep"]))
    painter.setPen(QPen(shade(PIGMENTS["vermilion-deep"], 255), 1))
    painter.setBrush(wax)
    painter.drawPath(rim)
    pressed = shade(PIGMENTS["vermilion-deep"], 230)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(pressed, 2))
    painter.drawEllipse(centre, radius * 0.66, radius * 0.66)
    cross = QPen(pressed, 3)
    cross.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(cross)
    arm = radius * 0.4
    painter.drawLine(centre - QPointF(arm, 0), centre + QPointF(arm, 0))
    painter.drawLine(centre - QPointF(0, arm), centre + QPointF(0, arm))
    painter.setPen(QPen(shade(PIGMENTS["lead-white"], 70), 1.2))
    painter.drawArc(
        QRectF(
            centre.x() - radius * 0.8,
            centre.y() - radius * 0.8,
            radius * 1.6,
            radius * 1.6,
        ),
        100 * 16,
        70 * 16,
    )


def preview_pictures(preview: Preview) -> list[QPixmap | None]:
    """A Preview's pictures, read from this computer's files by number
    less one (None for one that isn't there, or isn't a picture)."""
    found: list[QPixmap | None] = []
    for file in preview.files:
        picture = QPixmap(str(file)) if file is not None else None
        found.append(picture if picture is not None and not picture.isNull() else None)
    return found


#: The most of the screen a Handout's window takes, in pixels.
WINDOW_TALLEST = 860


class HandoutWindow(QDialog):
    """A Handout drawn on its Stationery in a window of its own, the page
    scrolling when it is taller than the window, with Close under it."""

    def __init__(
        self,
        laid: Laid,
        pictures: Sequence[QPixmap | None] = (),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("handout-window")
        # Both parts are plain text already.
        self.setWindowTitle(f"{laid.title} ({laid.stationery.label})")
        self.page = HandoutPage(laid, pictures)
        area = QScrollArea()
        area.setWidget(self.page)
        area.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        area.setStyleSheet(f"QScrollArea {{ background:{INK['panel']}; border:none }}")
        column = QVBoxLayout(self)
        column.addWidget(area, 1)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        #: The buttons under the page (Save as PDF joins Close here).
        self.buttons_row = QHBoxLayout()
        self.buttons_row.addStretch(1)
        self.buttons_row.addWidget(self.close_button)
        column.addLayout(self.buttons_row)
        scrollbar = area.verticalScrollBar().sizeHint().width()
        self.resize(
            PAGE_WIDTH + scrollbar + 40,
            min(WINDOW_TALLEST, self.page.minimumHeight() + 70),
        )


def preview_window(preview: Preview, parent: QWidget | None = None) -> HandoutWindow:
    """The window a storyguide's Preview opens: the Handout as it stands,
    its pictures from this computer's files."""
    return HandoutWindow(preview.laid, preview_pictures(preview), parent)
