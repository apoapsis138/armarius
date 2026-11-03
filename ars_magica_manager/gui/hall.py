"""The grand hall on the desktop: the meeting's hemicycle of seats, each a
small shield with its magus's House, coloured by how its vote went; the
covenants' pennants round it; the Praeco between the case's two
speakers; and the scales of the vote under it. Calling the vote fills
the hall bloc by bloc. The opening card plays once over the page as a
meeting opens: a one-shot presentation, keeping nothing."""

from __future__ import annotations

import math
from collections.abc import Callable

from PySide6.QtCore import (
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QCloseEvent,
    QColor,
    QFont,
    QFontMetricsF,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from .. import artwork, hall, meeting
from ..models import Case, Saga, Tribunal
from . import motion, pictures, shields
from .themes import OPENING_CARD, Palette
from .widgets import serif, text

#: How long the Praeco takes over each covenant when calling the vote,
#: and how long each arms takes to be hung on the opening card (ms).
CALL_STEP = 450
HANG_STEP = 160
#: How long the opening card takes to fade in (ms).
FADE_MS = 600


#: Room above the hemicycle for the pennants (px), and the hall's height
#: as a multiple of its radius: the pennants, the seats, the speakers and
#: the scales under them.
_TOP = 46
_TALL = 2.25


def _side_colours(p: Palette) -> dict[str, QColor]:
    return {
        meeting.FOR: QColor(p["text-error"]),
        meeting.AGAINST: QColor(p["text-success"]),
        meeting.UNDECIDED: QColor(p["rule"]),
    }


def _display(size: float) -> QFont:
    font = QFont(pictures.DISPLAY)
    font.setPointSizeF(size)
    return font


class GrandHall(QWidget):
    """The hall for `case` (None: the meeting's seats, every vote yet
    undecided)."""

    def __init__(
        self, saga: Saga, tribunal: Tribunal, case: Case | None, p: Palette
    ) -> None:
        super().__init__()
        self.saga, self.tribunal, self.case, self.p = saga, tribunal, case, p
        self.record = meeting.record(saga, tribunal)
        #: How many covenants the Praeco has called (None: all of them).
        self.called: int | None = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._call_next)
        self.setMinimumHeight(360)

    def sizeHint(self) -> QSize:
        return QSize(760, 520)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return max(360, int(_TOP + width * 0.40 * _TALL))

    def benches(self) -> list[hall.Bench]:
        return hall.benches(
            self.saga, self.tribunal, self.record, self.case, self.called
        )

    # -- calling the vote --

    def call_the_vote(self) -> None:
        """Call the covenants one by one, the hall filling as each votes."""
        self.called = 0
        self.timer.start(CALL_STEP)
        self.update()

    def _call_next(self) -> None:
        members = len(self.benches())
        if self.called is None or self.called >= members:
            self.timer.stop()
            self.called = None
        else:
            self.called += 1
        self.update()

    def calling(self) -> str:
        """What the Praeco is doing, under the scales."""
        benches = self.benches()
        if self.called is None or self.called >= len(benches):
            votes = hall.tally_so_far(benches)
            if self.case is None:
                return f"{sum(votes)} votes in the hall"
            undecided = f"{votes[2]} undecided" if votes[2] else "none undecided"
            return undecided
        now = benches[self.called].covenant.name if self.called < len(benches) else ""
        left = benches[self.called :]
        to_come = sum(len(b.seats) for b in left)
        return (
            f"Calling {now} · {len(left)} covenant{'' if len(left) == 1 else 's'}, "
            f"{to_come} vote{'' if to_come == 1 else 's'} to come"
        )

    # -- drawing --

    def paintEvent(self, event: QPaintEvent) -> None:
        p = self.p
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = self.width(), self.height()
        radius = min(width * 0.40, (height - _TOP) / _TALL)
        centre = QPointF(width / 2, _TOP + radius * 1.2)
        benches = self.benches()
        self._paint_bands(painter, centre, radius)
        seats = [(b, s) for b in benches for s in b.seats]
        places = hall.seat_places(len(seats))
        size = max(9.0, min(22.0, radius * 1.9 / max(8, math.sqrt(len(seats) * 7))))
        colours = _side_colours(p)
        spans: dict[str, list[float]] = {}
        for (bench, seat), (angle, r) in zip(seats, places):
            x = centre.x() + math.cos(angle) * r * radius
            y = centre.y() - math.sin(angle) * r * radius
            self._paint_seat(painter, QPointF(x, y), size, seat, bench.called, colours)
            spans.setdefault(bench.covenant.id, []).append(angle)
        for index, bench in enumerate(benches):
            angles = spans.get(bench.covenant.id)
            if angles:
                # Every other pennant hangs further out, so neighbours'
                # never overlap.
                out = 1.08 if index % 2 == 0 else 1.17
                self._paint_pennant(
                    painter, centre, radius * out, bench, sum(angles) / len(angles)
                )
        self._paint_speakers(painter, centre, radius)
        self._paint_scales(painter, centre, radius, hall.tally_so_far(benches))
        painter.end()

    def _paint_bands(self, painter: QPainter, centre: QPointF, radius: float) -> None:
        p = self.p
        floor = QRadialGradient(centre, radius)
        gold = QColor(p["accent"])
        floor.setColorAt(0, QColor(gold.red(), gold.green(), gold.blue(), 50))
        floor.setColorAt(1, QColor(gold.red(), gold.green(), gold.blue(), 12))
        path = QPainterPath()
        path.moveTo(centre)
        path.arcTo(
            QRectF(centre.x() - radius, centre.y() - radius, 2 * radius, 2 * radius),
            0,
            180,
        )
        path.closeSubpath()
        painter.fillPath(path, floor)
        pen = QPen(QColor(p["accent"]), max(1.5, radius / 120))
        painter.setPen(pen)
        for fraction in (hall.INNER - 0.06, 1.0):
            r = radius * fraction
            painter.drawArc(
                QRectF(centre.x() - r, centre.y() - r, 2 * r, 2 * r), 0, 180 * 16
            )
        painter.drawLine(
            QPointF(centre.x() - radius, centre.y()),
            QPointF(centre.x() + radius, centre.y()),
        )

    def _paint_seat(
        self,
        painter: QPainter,
        at: QPointF,
        size: float,
        seat: hall.Seat,
        called: bool,
        colours: dict[str, QColor],
    ) -> None:
        rect = QRectF(at.x() - size / 2, at.y() - size * 0.6, size, size)
        outline = shields.shield_path(rect)
        fill = QColor(colours[seat.side if called else meeting.UNDECIDED])
        if not called:
            fill.setAlpha(90)
        painter.fillPath(outline, fill)
        edge = QColor(self.p["accent"]) if called else QColor(self.p["rule"])
        painter.strokePath(outline, QPen(edge, max(0.8, size / 14)))
        symbol = artwork.house_symbol(seat.house_id)
        if symbol is not None and size >= 12:
            mark = int(size * 0.62)
            shade = (
                self.p["background"]
                if called and seat.side != meeting.UNDECIDED
                else self.p["label"]
            )
            painter.drawPixmap(
                QPointF(at.x() - mark / 2, at.y() - size * 0.6 + size * 0.18),
                pictures.pixmap(symbol, shade, mark, 2.0),
            )
        elif seat.proxy:
            painter.setPen(QPen(QColor(self.p["background"]), max(0.8, size / 12)))
            painter.drawLine(
                QPointF(at.x() - size * 0.22, at.y() - size * 0.1),
                QPointF(at.x() + size * 0.22, at.y() - size * 0.1),
            )

    def _paint_pennant(
        self,
        painter: QPainter,
        centre: QPointF,
        radius: float,
        bench: hall.Bench,
        angle: float,
    ) -> None:
        p = self.p
        r = radius
        x = centre.x() + math.cos(angle) * r
        y = centre.y() - math.sin(angle) * r
        painter.save()
        painter.translate(x, y)
        painter.rotate(90 - math.degrees(angle))
        name = bench.covenant.name
        font = serif(9.5, caps=True)
        painter.setFont(font)
        metrics = QFontMetricsF(font)
        wide = metrics.horizontalAdvance(name) + 14
        banner = QRectF(-wide / 2, -9, wide, 18)
        painter.fillPath(_ribbon(banner), QColor(p["panel"]))
        painter.strokePath(_ribbon(banner), QPen(QColor(p["accent"]), 1.0))
        painter.setPen(QColor(p["heading"] if bench.called else p["dim"]))
        painter.drawText(banner, Qt.AlignmentFlag.AlignCenter, name)
        if bench.arms is not None:
            shield = 20.0
            shields.paint(
                painter,
                bench.arms,
                QRectF(
                    -shield / 2,
                    -9 - shield * shields.HEIGHT - 4,
                    shield,
                    shield * shields.HEIGHT,
                ),
                p["accent"],
            )
        painter.restore()

    def _paint_speakers(
        self, painter: QPainter, centre: QPointF, radius: float
    ) -> None:
        p = self.p
        case = self.case
        praeco = self.saga.character(self.tribunal.praeco_id)
        spots = [(0.0, praeco.name if praeco else "The Praeco", "Praeco", p["heading"])]
        if case is not None:
            spots += [
                (
                    -0.55,
                    case.prosecutor or "Its speaker",
                    "prosecutes" if case.kind != "motion" else "speaks for",
                    p["text-error"],
                ),
                (
                    0.55,
                    case.defender or "None",
                    "defends" if case.kind != "motion" else "speaks against",
                    p["text-success"],
                ),
            ]
        for offset, name, role, colour in spots:
            at = QPointF(centre.x() + offset * radius, centre.y() + radius * 0.1)
            size = radius * (0.17 if offset == 0 else 0.11)
            disc = QRadialGradient(at, size)
            disc.setColorAt(0, QColor(p["panel"]))
            disc.setColorAt(1, QColor(colour))
            painter.setBrush(disc)
            painter.setPen(QPen(QColor(p["accent"]), 2))
            painter.drawEllipse(at, size, size)
            symbol = artwork.house_symbol(self._house_of(name))
            if symbol is not None:
                mark = int(size * 1.1)
                painter.drawPixmap(
                    QPointF(at.x() - mark / 2, at.y() - mark / 2),
                    pictures.pixmap(symbol, p["background"], mark, 2.0),
                )
            painter.setPen(QColor(colour))
            painter.setFont(
                serif(12 if offset == 0 else 11.5, italic=offset != 0, caps=offset == 0)
            )
            words = f"{name}, {role}" if offset == 0 else f"{name} {role}"
            painter.drawText(
                QRectF(at.x() - 140, at.y() + size + 4, 280, 22),
                Qt.AlignmentFlag.AlignHCenter,
                words,
            )

    def _house_of(self, name: str) -> str | None:
        wanted = name.strip().casefold()
        found = next(
            (c for c in self.saga.characters if c.name.casefold() == wanted), None
        )
        return found.hermetic.house if found is not None else None

    def _paint_scales(
        self,
        painter: QPainter,
        centre: QPointF,
        radius: float,
        votes: tuple[int, int, int],
    ) -> None:
        if self.case is None:
            return
        p = self.p
        yes, no, _undecided = votes
        beam_y = centre.y() + radius * 0.62
        half = radius * 0.42
        total = max(1, yes + no)
        tilt = (yes - no) / total * 0.22
        left = QPointF(centre.x() - half, beam_y + tilt * half)
        right = QPointF(centre.x() + half, beam_y - tilt * half)
        pivot = QPointF(centre.x(), beam_y)
        gold = QColor(p["accent"])
        painter.setPen(QPen(gold, 3))
        painter.drawLine(left, right)
        painter.drawLine(pivot, QPointF(pivot.x(), pivot.y() + radius * 0.16))
        painter.drawLine(
            QPointF(pivot.x() - radius * 0.07, pivot.y() + radius * 0.16),
            QPointF(pivot.x() + radius * 0.07, pivot.y() + radius * 0.16),
        )
        painter.setBrush(gold)
        painter.drawEllipse(pivot, 5, 5)
        for end, count, label, colour in (
            (left, yes, "For", p["text-error"]),
            (right, no, "Against", p["text-success"]),
        ):
            pan = QPainterPath()
            pan_rect = QRectF(
                end.x() - radius * 0.13, end.y() + 4, radius * 0.26, radius * 0.08
            )
            pan.moveTo(pan_rect.topLeft())
            pan.lineTo(pan_rect.topRight())
            pan.arcTo(
                QRectF(
                    pan_rect.left(),
                    pan_rect.top() - pan_rect.height(),
                    pan_rect.width(),
                    pan_rect.height() * 2,
                ),
                0,
                -180,
            )
            fill = QColor(colour)
            fill.setAlpha(110)
            painter.fillPath(pan, fill)
            painter.strokePath(pan, QPen(gold, 2))
            painter.setPen(QColor(colour))
            painter.setFont(_display(20))
            painter.drawText(
                QRectF(end.x() - 60, end.y() - 34, 120, 36),
                Qt.AlignmentFlag.AlignCenter,
                str(count),
            )
            painter.setFont(serif(10.5, caps=True))
            painter.setPen(QColor(p["label"]))
            painter.drawText(
                QRectF(end.x() - 80, end.y() + radius * 0.09 + 6, 160, 18),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )
        painter.setPen(QColor(p["label"]))
        painter.setFont(serif(11.5, italic=True))
        painter.drawText(
            QRectF(centre.x() - radius, beam_y + radius * 0.34, 2 * radius, 22),
            Qt.AlignmentFlag.AlignCenter,
            self.calling(),
        )


def _ribbon(rect: QRectF) -> QPainterPath:
    """A banner with notched ends."""
    notch = rect.height() * 0.35
    path = QPainterPath()
    path.moveTo(rect.left() - notch, rect.top())
    path.lineTo(rect.right() + notch, rect.top())
    path.lineTo(rect.right(), rect.center().y())
    path.lineTo(rect.right() + notch, rect.bottom())
    path.lineTo(rect.left() - notch, rect.bottom())
    path.lineTo(rect.left(), rect.center().y())
    path.closeSubpath()
    return path


# ------------------------------------------------------- the opening card


class OpeningCard(QWidget):
    """Over the whole window as a meeting opens: the year, the Tribunal's
    name, where it is opened, each covenant's arms hung in turn and the
    hall's numbers. Enter the Hall, a click or any key closes it, and
    `then` (the meeting's next step) runs."""

    def __init__(
        self,
        window: QWidget,
        card: hall.OpeningCard,
        p: Palette,
        then: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(window)
        self.card, self.p, self.then = card, p, then
        self._opacity = 0.0
        self.hung = 0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setGeometry(window.rect())
        column = QVBoxLayout(self)
        column.addStretch(2)
        c = OPENING_CARD
        for words, colour, font in (
            (card.anno, c["gold"], serif(15, caps=True)),
            (card.title, c["gold"], _display(44)),
            (card.opened, c["parchment"], serif(19, italic=True)),
        ):
            label = text(words, colour, font, wrap=True)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            column.addWidget(label)
        column.addSpacing(16)
        self.shields = QWidget()
        self.shields.setMinimumHeight(64)
        column.addWidget(self.shields)
        numbers = text(card.numbers, c["numbers"], serif(12.5, caps=True), wrap=True)
        numbers.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(numbers)
        column.addStretch(3)
        row = QHBoxLayout()
        row.addStretch(1)
        enter = QPushButton("Enter the Hall")
        enter.setObjectName("enterHall")
        enter.setCursor(Qt.CursorShape.PointingHandCursor)
        enter.setStyleSheet(
            f"QPushButton#enterHall{{background:{c['button']};color:{c['button-text']};"
            f"border:1px solid {c['gold']};border-radius:4px;padding:10px 46px;"
            "font-size:15px;}"
        )
        enter.clicked.connect(self.close)
        row.addWidget(enter)
        row.addStretch(1)
        column.addLayout(row)
        column.addSpacing(48)
        self.hanging = QTimer(self)
        self.hanging.timeout.connect(self._hang_next)

    def _fade(self, value: float) -> None:
        self._opacity = value
        self.update()

    def play(self) -> None:
        """Fade the card in and hang the arms one by one; with no motion,
        all at once."""
        self.raise_()
        self.show()
        self.setFocus()
        motion.tween(self, self._fade, FADE_MS, name="fade")
        if motion.moving():
            self.hanging.start(HANG_STEP)
        else:
            self.hung = len(self.card.arms)
            self.update()

    def _hang_next(self) -> None:
        self.hung += 1
        if self.hung >= len(self.card.arms):
            self.hanging.stop()
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._opacity)
        vignette = QRadialGradient(
            QPointF(self.width() / 2, self.height() / 2),
            max(self.width(), self.height()) * 0.7,
        )
        middle, edge = QColor(OPENING_CARD["dark"]), QColor(OPENING_CARD["darker"])
        middle.setAlpha(225)
        edge.setAlpha(250)
        vignette.setColorAt(0, middle)
        vignette.setColorAt(1, edge)
        painter.fillRect(self.rect(), vignette)
        hung = self.card.arms[: self.hung]
        if hung:
            size = 40.0
            gap = 20.0
            row_width = len(self.card.arms) * (size + gap) - gap
            top = self.shields.geometry().top() + 6
            left = (self.width() - row_width) / 2
            for i, (_name, found) in enumerate(hung):
                shields.paint(
                    painter,
                    found,
                    QRectF(left + i * (size + gap), top, size, size * shields.HEIGHT),
                    OPENING_CARD["button"],
                )
        painter.end()

    def closeEvent(self, event: QCloseEvent) -> None:
        then, self.then = self.then, None
        if then is not None:
            QTimer.singleShot(0, then)
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.close()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.close()
