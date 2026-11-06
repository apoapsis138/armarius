"""Advance Season on the desktop: the panel at the foot of a page's chapter
rail, and the dial shown in the middle of the window once the season has
moved on.

The panel is a card as the page's clickable cards are, round the
present season's medallion and its date, and the whole card is the
Advance Season button, so the season can be ended from whichever page
is on show. Creation
Worksheets, Fights and Sieges have no rail, and so no panel.

The dial is four medallions on a wheel. It turns a quarter to bring the
new season to the top, then gives way to the new season's medallion,
large, with its name and year under it, and fades. It moves only while
motion is on (motion.moving); a click or a key ends it at once.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QAbstractButton, QVBoxLayout, QWidget

from ..models import Saga
from ..models.common import SEASONS
from ..models.seasons import next_season
from . import motion, sounds
from .medallions import ROOM, Medallion, paint_season
from .style import gilding
from .style.ornaments import corner_flourishes
from .style.paper import lift, shade
from .style.pieces import serif, text
from .themes import Palette

#: The panel's width: the chapter rail's.
WIDTH = 180


class SeasonPanel(QAbstractButton):
    """The present season at the foot of the chapter rail, drawn as the
    page's clickable cards are (a troupe covenant's, with a flourish in
    each corner): its medallion, glowing as the present season does, its
    name and year, and the words Advance Season under them. The whole card
    is the button: a click, Space or Enter advances the season (after
    asking first); under the mouse its border lights, as a card's does."""

    #: The medallion's radius.
    RADIUS = 22

    def __init__(self, saga: Saga, p: Palette, advance: Callable[[], None]) -> None:
        super().__init__()
        self.p = p
        self.setFixedWidth(WIDTH)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        season, year = saga.current_season, saga.current_year
        self.setAccessibleName("Advance Season")
        self.setToolTip(
            f"Advance Season: end {season} {year} and move the saga on,"
            " after asking first"
        )
        lift(self, p)
        column = QVBoxLayout(self)
        column.setContentsMargins(12, 8, 12, 12)
        column.setSpacing(0)
        self.medallion = Medallion(saga, season, year, p, radius=self.RADIUS, now=True)
        # The card's own tooltip and click, not the medallion's.
        self.medallion.setToolTip("")
        column.addWidget(self.medallion, 0, Qt.AlignmentFlag.AlignHCenter)
        self.date = text(f"{season} {year}", p["heading"], serif(12.5, caps=True))
        self.date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(self.date)
        self.words = text("Advance Season", p["label"], serif(11, italic=True))
        self.words.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(self.words)
        for part in (self.medallion, self.date, self.words):
            part.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.clicked.connect(advance)

    def sizeHint(self) -> QSize:
        layout = self.layout()
        return layout.sizeHint() if layout is not None else super().sizeHint()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.click()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        lit = self.underMouse() or self.hasFocus()
        fill = QColor(self.p["surface"])
        fill.setAlpha(215)
        edge = QColor(self.p["accent"] if lit else self.p["rule"])
        if not lit:
            edge.setAlpha(150)
        painter.setBrush(fill)
        painter.setPen(QPen(edge, 1))
        painter.drawRoundedRect(rect, 6, 6)
        if self.isDown():
            painter.setBrush(shade(self.p["shadow"], 30))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 6, 6)
        corner_flourishes(painter, rect.adjusted(0.5, 0.5, -0.5, -0.5), self.p, 12)
        painter.end()

    def event(self, e: QEvent) -> bool:
        handled = super().event(e)
        if e.type() in (
            QEvent.Type.HoverEnter,
            QEvent.Type.HoverLeave,
            QEvent.Type.FocusIn,
            QEvent.Type.FocusOut,
        ):
            # The words take the heading's red while the card is lit.
            lit = e.type() in (QEvent.Type.HoverEnter, QEvent.Type.FocusIn) or (
                self.hasFocus() or self.underMouse()
            )
            colour = self.p["heading"] if lit else self.p["label"]
            self.words.setStyleSheet(f"color:{colour}; background:transparent")
            self.update()
        return handled


# -- the dial --

#: How long each part of the dial takes, in milliseconds: the wheel's
#: quarter turn, the pause on the new season, the change to its large
#: medallion, the pause on that, and the fade.
TURN = 1100
SETTLE = 350
REVEAL = 600
SHOW = 1300
FADE = 400


def seasons_from(season: str, year: int) -> list[tuple[str, int]]:
    """The four seasons from (season, year) on, in order."""
    out = [(season, year)]
    while len(out) < len(SEASONS):
        out.append(next_season(*out[-1]))
    return out


def season_before(season: str, year: int) -> tuple[str, int]:
    """The season before (season, year): the one just ended."""
    index = SEASONS.index(season)
    if index == 0:
        return SEASONS[-1], year - 1
    return SEASONS[index - 1], year


def wheel_place(index: int, turned: float) -> tuple[float, float]:
    """Where the `index`th season from the old one sits on the wheel once
    it has `turned` (0 to 1) of its quarter: its angle in degrees, 0 at
    the top and clockwise, and how near the top it is (1 there, 0 a
    quarter or more away)."""
    angle = 90.0 * (index - turned)
    near = max(0.0, math.cos(math.radians(angle)))
    return angle, near


class SeasonDial(QWidget):
    """The season's wheel laid over `host` (the window's pages), dimming
    them: it turns from `saga`'s previous season to its present one, then
    shows the present one large, and fades. `done` is called once it has
    gone, or at once when motion is off (no dial is shown then)."""

    #: The wheel's radius, and its medallions' at the side and at the top.
    WHEEL = 104
    SMALL = 26
    LARGE = 40
    #: The present season's medallion once the wheel gives way to it.
    FEATURED = 62

    def __init__(
        self, host: QWidget, saga: Saga, p: Palette, done: Callable[[], None]
    ) -> None:
        super().__init__(host)
        self.saga, self.p, self._done = saga, p, done
        self.season, self.year = saga.current_season, saga.current_year
        self.wheel = seasons_from(*season_before(self.season, self.year))
        self.turned = 0.0
        self.revealed = 0.0
        self.shown = 1.0
        self._ended = False
        self.setGeometry(host.rect())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        scale = max(1.0, host.devicePixelRatioF())
        self._small = {
            season: self._render(season, year, self.LARGE, scale, now=False)
            for season, year in self.wheel
        }
        self._featured = self._render(
            self.season, self.year, self.FEATURED, scale, now=True
        )

    def _render(
        self, season: str, year: int, radius: float, scale: float, *, now: bool
    ) -> QPixmap:
        """A season's medallion drawn once, to be scaled as the wheel turns."""
        side = math.ceil(radius * ROOM)
        art = QPixmap(math.ceil(side * scale), math.ceil(side * scale))
        art.setDevicePixelRatio(scale)
        art.fill(Qt.GlobalColor.transparent)
        g = QPainter(art)
        paint_season(
            g,
            self.saga,
            QPointF(side / 2, side / 2),
            radius,
            season,
            year,
            self.p,
            now=now,
        )
        g.end()
        return art

    def play(self) -> None:
        """Show the dial and turn it; with no motion, `done` at once."""
        if not motion.moving():
            self._finish()
            return
        self.show()
        self.raise_()
        self.setFocus()
        motion.tween(self, self._turn, TURN, name="turn", done=self._settled)

    def _turn(self, value: float) -> None:
        self.turned = value
        self.update()

    def _settled(self) -> None:
        sounds.play("seal")
        motion.hold(self, SETTLE, self._reveal)

    def _reveal(self) -> None:
        motion.tween(self, self._show_featured, REVEAL, name="reveal", done=self._hold)

    def _show_featured(self, value: float) -> None:
        self.revealed = value
        self.update()

    def _hold(self) -> None:
        motion.hold(self, SHOW, self._fade_out)

    def _fade_out(self) -> None:
        if self._ended:
            return
        motion.tween(
            self, self._fade, FADE, name="fade", start=1.0, end=0.0, done=self._finish
        )

    def _fade(self, value: float) -> None:
        self.shown = value
        self.update()

    def _finish(self) -> None:
        """Gone, once: tell the window."""
        if self._ended:
            return
        self._ended = True
        self.hide()
        self.deleteLater()
        self._done()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._finish()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self._finish()

    # -- drawing --

    def card(self) -> QRectF:
        """The gilt leaf the dial sits on, in the middle of the window."""
        width = min(440.0, self.width() - 32.0)
        height = min(470.0, self.height() - 32.0)
        centre = QRectF(self.rect()).center()
        return QRectF(centre.x() - width / 2, centre.y() - height / 2, width, height)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.shown)
        painter.fillRect(self.rect(), shade(self.p["shadow"], 110))
        card = self.card()
        gilding.gilt_leaf(painter, card, self.p)
        centre = QPointF(card.center().x(), card.top() + card.height() * 0.45)
        painter.setOpacity(self.shown * (1 - self.revealed))
        self._paint_wheel(painter, centre)
        painter.setOpacity(self.shown * self.revealed)
        self._paint_featured(painter, centre, card)
        painter.end()

    def _paint_wheel(self, painter: QPainter, centre: QPointF) -> None:
        gilt = QColor(self.p["accent"])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(gilt, 1.2))
        painter.drawEllipse(centre, self.WHEEL, self.WHEEL)
        faint = QColor(gilt)
        faint.setAlpha(110)
        painter.setPen(QPen(faint, 0.6))
        painter.drawEllipse(centre, self.WHEEL - 6, self.WHEEL - 6)
        # A notch at the top, where the season in focus comes to rest.
        top = QPointF(centre.x(), centre.y() - self.WHEEL - self.LARGE * 1.25)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gilt)
        painter.drawPolygon(
            [top + QPointF(-7, -6), top + QPointF(7, -6), top + QPointF(0, 5)]
        )
        # The farther medallions first, so the one at the top lies over them.
        placed = [
            (wheel_place(i, self.turned), season)
            for i, (season, _year) in enumerate(self.wheel)
        ]
        for (angle, near), season in sorted(placed, key=lambda item: item[0][1]):
            radius = self.SMALL + (self.LARGE - self.SMALL) * near
            spot = centre + QPointF(
                self.WHEEL * math.sin(math.radians(angle)),
                -self.WHEEL * math.cos(math.radians(angle)),
            )
            art = self._small[season]
            side = radius * ROOM
            painter.save()
            painter.setOpacity(painter.opacity() * (0.55 + 0.45 * near))
            painter.drawPixmap(
                QRectF(spot.x() - side / 2, spot.y() - side / 2, side, side),
                art,
                QRectF(art.rect()),
            )
            painter.restore()

    def _paint_featured(self, painter: QPainter, centre: QPointF, card: QRectF) -> None:
        if self.revealed <= 0:
            return
        grow = 0.85 + 0.15 * self.revealed
        side = self.FEATURED * ROOM * grow
        art = self._featured
        painter.drawPixmap(
            QRectF(centre.x() - side / 2, centre.y() - side / 2, side, side),
            art,
            QRectF(art.rect()),
        )
        painter.setPen(QColor(self.p["heading"]))
        painter.setFont(serif(24, bold=True, caps=True))
        painter.drawText(
            QRectF(card.left(), card.bottom() - 96, card.width(), 40),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.season} {self.year}",
        )
        painter.setPen(QColor(self.p["label"]))
        painter.setFont(serif(12.5, italic=True))
        painter.drawText(
            QRectF(card.left(), card.bottom() - 58, card.width(), 26),
            Qt.AlignmentFlag.AlignCenter,
            "The season turns",
        )


def turn_the_dial(
    host: QWidget, saga: Saga, p: Palette, done: Callable[[], None]
) -> SeasonDial:
    """Lay the season's dial over `host` and play it; `done` once it has
    gone (at once with no motion)."""
    dial = SeasonDial(host, saga, p, done)
    dial.play()
    return dial
