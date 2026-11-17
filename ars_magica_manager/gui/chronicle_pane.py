"""The Chronicle pane (the Virtual Tabletop preview): docked on the right
of the saga window while a Session is Under way, it shows the Chronicle as
whoever sits here may see it, on a gilt leaf like the Inspector's, in the
theme's own frame. Each roll is a card: who rolled (the character, and its
player in smaller type), what for, the dice as ten-sided dice with their
faces, and the outcome, set largest. A Free Roll button sits at its foot.

The Session's storyguide cancels a roll with the Cancel beside its dice,
or Cancel on the dice's menu. A canceled roll keeps its card, quietly:
the card faded, a fine rule struck through its dice and its total, and
"Canceled" with the reason beneath in small italic. (The
Chronicle calls it a Void.)

Collapsed, it is a thin strip on the right edge, its name running up it
and a count of entries come since; a click opens it again. A Blind result
or a line for you pulses the strip once (not with Reduce motion), and it
never opens by itself. Whether it is open or collapsed is remembered.

Pattern: Observer. The pane subscribes to the Chronicle (Chronicle.subscribe)
and is told of each new entry, as a Remote seat's event connection is; it
reads every entry through the core's audience filter."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QContextMenuEvent,
    QFont,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QFrame,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .. import artwork, chronicle, settings
from ..commands import Command
from ..forms import free_roll
from ..models import Saga, Session
from ..style import fonts
from . import motion, pictures, sounds
from .style import gilding
from .style.ornaments import ShortRule
from .style.paper import paper
from .style.pieces import heading as heading_font
from .style.pieces import heading_ink
from .themes import Palette
from .widgets import edit_button, serif, text

#: The setting that remembers a collapsed pane.
COLLAPSED = "chronicle_pane_collapsed"
WIDTH = 340
STRIP = 34
PULSE_MS = 900
#: A die's side, and a botch die's, in pixels.
DIE = 44
BOTCH_DIE = 34
#: More botch dice than this go on a line of their own.
MOST_ON_A_LINE = 4


def remembered_collapsed() -> bool:
    return settings.load_settings().get(COLLAPSED) is True


def number_font(size: float, *, bold: bool = True) -> QFont:
    """Numbers are set in the system's UI face (FEAT-16's type rules)."""
    font = QFont(fonts.UI)
    font.setPointSizeF(size)
    font.setBold(bold)
    return font


# -- a roll's body, read --


def _whole(body: dict[str, object], key: str) -> int:
    """A whole number of a roll's body (the app wrote it; 0 if not)."""
    value = body.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _wholes(body: dict[str, object], key: str) -> list[int]:
    value = body.get(key)
    if not isinstance(value, list):
        return []
    return [v for v in value if isinstance(v, int) and not isinstance(v, bool)]


# -- the dice --


#: The kite face turned to the viewer, on d10.svg's 256 square
#: (tools/draw_d10.py): top, left, lower point, right.
KITE = ((128, 22), (72, 140), (128, 176), (184, 140))


class Die(QWidget):
    """One ten-sided die (assets/drawn/d10.svg) with its face written on
    the kite turned to the viewer. A `marked` die (a zero: the botch check
    or a botch) has its kite filled solid and its face knocked out in
    `paper`; a `doubled` die (a 1 that exploded) has a second rim drawn
    just inside its kite. Each shows by its shape, not by colour alone."""

    def __init__(
        self,
        face: int,
        colour: str,
        side: int,
        kind: str,
        *,
        marked: bool = False,
        doubled: bool = False,
        paper: str,
    ) -> None:
        super().__init__()
        self.face, self.colour = face, colour
        self.marked, self.doubled, self.paper = marked, doubled, paper
        self.setObjectName(kind)
        self.setFixedSize(side, side)
        self.setToolTip(f"{face}")
        self._picture: QPixmap = pictures.pixmap(
            artwork.icon("d10"), colour, side, self.devicePixelRatioF() or 2.0
        )

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = self.width()
        painter.drawPixmap(0, 0, side, side, self._picture)
        if self.marked:
            kite = QPolygonF([QPointF(x * side / 256, y * side / 256) for x, y in KITE])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.colour))
            painter.drawPolygon(kite)
        if self.doubled:
            # A second rim, the kite drawn again a little inside the first.
            cx, cy = 128, 108
            inner = QPolygonF(
                [
                    QPointF(
                        (cx + (x - cx) * 0.72) * side / 256,
                        (cy + (y - cy) * 0.72) * side / 256,
                    )
                    for x, y in KITE
                ]
            )
            painter.setPen(QPen(QColor(self.colour), max(1.2, side / 30)))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolygon(inner)
        painter.setPen(QColor(self.paper if self.marked else self.colour))
        font = number_font(side * (0.15 if self.face >= 10 else 0.2))
        painter.setFont(font)
        # The kite face sits a little above the die's middle.
        painter.drawText(
            QRectF(0, side * 0.32, side, side * 0.34),
            Qt.AlignmentFlag.AlignCenter,
            str(self.face),
        )
        painter.end()


class DiceRow(QWidget):
    """A roll's dice: the die's throws, then any botch dice. A canceled
    roll's are faded and struck through. `cancel` (the Session's
    storyguide only) is a Cancel beside them, and on the dice's menu."""

    def __init__(
        self,
        body: dict[str, object],
        p: Palette,
        canceled: bool,
        cancel: Callable[[], None] | None,
    ) -> None:
        super().__init__()
        self.p, self.canceled, self._cancel = p, canceled, cancel
        self.setObjectName("dice")
        rows = QVBoxLayout(self)
        rows.setContentsMargins(0, 4, 0, 4)
        rows.setSpacing(2)
        row = QHBoxLayout()
        row.setSpacing(2)
        rows.addLayout(row)
        stress = bool(body.get("stress"))
        faces = _wholes(body, "faces") if stress else [_whole(body, "die")]
        for index, face in enumerate(faces):
            shown = face if index == 0 or face or not stress else 10
            zero = stress and index == 0 and shown == 0
            exploded = stress and index < len(faces) - 1 and face == 1
            colour = (
                p["dim"] if canceled else (p["text-error"] if zero else p["foreground"])
            )
            row.addWidget(
                Die(
                    shown,
                    colour,
                    DIE,
                    "die",
                    marked=zero,
                    doubled=exploded,
                    paper=p["background"],
                )
            )
            if exploded:
                # The chain, left to right: what the next die is multiplied by.
                times = text(f"×{2 ** (index + 1)}", p["label"], number_font(10))
                times.setObjectName("doubled")
                times.setToolTip("A 1: roll again and double")
                row.addWidget(times)
        botch = _wholes(body, "botch_faces")
        if botch:
            row.addSpacing(8)
            if len(botch) > MOST_ON_A_LINE:
                row.addStretch(1)
                row = QHBoxLayout()
                row.setSpacing(2)
                rows.addLayout(row)
            for face in botch:
                colour = p["text-error"] if face == 0 else p["foreground"]
                row.addWidget(
                    Die(
                        face,
                        p["dim"] if canceled else colour,
                        BOTCH_DIE,
                        "botch",
                        marked=face == 0,
                        paper=p["background"],
                    )
                )
        row.addStretch(1)
        #: Cancel, for the Session's storyguide on a roll still counting: a
        #: quiet word in the margin, not a framed button.
        self.cancel_mark = QToolButton()
        self.cancel_mark.setObjectName("cancel")
        self.cancel_mark.setText("Cancel")
        self.cancel_mark.setToolTip("Cancel this roll, with a reason")
        self.cancel_mark.setAutoRaise(True)
        self.cancel_mark.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_mark.setFont(serif(11, italic=True))
        self.cancel_mark.setStyleSheet(
            f"QToolButton#cancel {{ color:{p['label']}; border:none;"
            " background:transparent; padding:0 2px; }"
            f" QToolButton#cancel:hover {{ color:{p['text-error']};"
            " text-decoration:underline; }"
        )
        self.cancel_mark.clicked.connect(self.cancel)
        self.cancel_mark.setVisible(self.can_cancel)
        row.addWidget(self.cancel_mark, 0, Qt.AlignmentFlag.AlignBottom)

    @property
    def can_cancel(self) -> bool:
        return self._cancel is not None and not self.canceled

    def cancel(self) -> None:
        if self._cancel is not None and not self.canceled:
            self._cancel()

    def menu(self) -> QMenu:
        """The dice's menu: Cancel this roll, for the Session's storyguide."""
        found = QMenu(self)
        action = found.addAction("Cancel this roll…")
        action.setEnabled(self.can_cancel)
        action.triggered.connect(self.cancel)
        return found

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        if self.can_cancel:
            self.menu().exec(event.globalPos())

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        if not self.canceled:
            return
        # A fine red rule through the dice, as a scribe strikes a line.
        dice = [w for w in self.findChildren(Die) if w.isVisible()]
        if not dice:
            return
        left = min(d.geometry().left() for d in dice) - 3
        right = max(d.geometry().right() for d in dice) + 3
        middle = dice[0].geometry().center().y()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(self.p["label"]), 1.2))
        painter.drawLine(QPointF(left, middle), QPointF(right, middle))
        painter.end()


# -- the cards --


class Card(QFrame):
    """One entry of the feed. `line` is the Chronicle's own line for it,
    what the terminal shows."""

    def __init__(self, line: str, p: Palette) -> None:
        super().__init__()
        self.line = line
        self.setObjectName("chronicle-card")
        self.setStyleSheet(
            f"QFrame#chronicle-card {{ border:none;"
            f" border-bottom:1px solid {p['rule']}; background:transparent; }}"
        )
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(2, 8, 2, 8)
        self.column.setSpacing(2)


def note_card(line: str, p: Palette) -> Card:
    """A card for an entry that isn't a roll: one line, in italic."""
    card = Card(line, p)
    words = text(line, p["label"], serif(11.5, italic=True), wrap=True)
    card.column.addWidget(words)
    return card


def roll_card(
    entry: chronicle.Entry,
    line: str,
    p: Palette,
    who_rolled: str,
    reason: str | None,
    cancel: Callable[[], None] | None,
) -> Card:
    """Who rolled, what for, the dice and the outcome; `reason` when the
    roll was canceled."""
    body = entry.body
    card = Card(line, p)
    top = QHBoxLayout()
    top.setSpacing(6)
    character = str(body.get("character_name") or "") or "The storyguide"
    quiet = reason is not None
    if "total" not in body:
        return note_card(line, p)
    name = text(
        character,
        p["dim"] if quiet else heading_ink(p),
        heading_font(12.5, p, caps=True),
    )
    name.setObjectName("who")
    top.addWidget(name)
    if who_rolled:
        player = text(who_rolled, p["dim"], serif(10.5, italic=True))
        player.setObjectName("player")
        top.addWidget(player, 0, Qt.AlignmentFlag.AlignBottom)
    top.addStretch(1)
    if entry.audience.to != chronicle.TABLE:
        tag = "Blind" if entry.audience.to == chronicle.STORYGUIDE else "Private"
        mark = text(tag, p["label"], serif(10, caps=True))
        mark.setObjectName("visibility")
        top.addWidget(mark)
    card.column.addLayout(top)
    if body.get("for"):
        ink = p["dim"] if quiet else p["foreground"]
        what = text(str(body["for"]), ink, serif(12, italic=True), wrap=True)
        what.setObjectName("what")
        card.column.addWidget(what)
    card.column.addWidget(DiceRow(body, p, reason is not None, cancel))
    card.column.addWidget(_outcome(body, p, reason is not None))
    if reason is not None:
        why = text(
            f"Canceled: {reason}", p["label"], serif(10.5, italic=True), wrap=True
        )
        why.setObjectName("reason")
        card.column.addWidget(why)
    return card


def _outcome(body: dict[str, object], p: Palette, canceled: bool) -> QWidget:
    """The total, set largest, and against the Ease Factor what came of it."""
    box = QWidget()
    box.setObjectName("outcome")
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    botches = _whole(body, "botches")
    ink = p["dim"] if canceled else (p["text-error"] if botches else p["foreground"])
    font = number_font(20)
    font.setStrikeOut(canceled)
    total = text(str(_whole(body, "total")), ink, font)
    total.setObjectName("total")
    if canceled:
        # Struck through as rich text: the label's style sheet sets its font.
        total.setTextFormat(Qt.TextFormat.RichText)
        total.setText(f"<s>{_whole(body, 'total')}</s>")
    row.addWidget(total, 0, Qt.AlignmentFlag.AlignVCenter)
    modifier = _whole(body, "modifier")
    sign = "+" if modifier >= 0 else "−"
    faces = _wholes(body, "faces")
    doublings = sum(1 for f in faces[:-1] if f == 1) if body.get("stress") else 0
    value = _whole(body, "die")
    if doublings:
        last = faces[-1] or 10
        die = f"die {last} ×{2**doublings} = {value}"
    else:
        die = f"die {value}"
    said = [f"{die} {sign} {abs(modifier)}"]
    if botches:
        said.append(f"botch, {botches} zero{'s' if botches > 1 else ''}")
    if body.get("ease_factor") is not None:
        verdict = "succeeds" if body.get("succeeded") else "fails"
        margin = _whole(body, "margin")
        said.append(f"against {body['ease_factor']}: {verdict} by {abs(margin)}")
    words = text(" · ".join(said), p["label"], serif(11.5), wrap=True)
    words.setObjectName("verdict")
    row.addWidget(words, 1, Qt.AlignmentFlag.AlignVCenter)
    return box


# -- the strip --


class Strip(QAbstractButton):
    """The collapsed pane: its name running up a thin gilt strip, and the
    count of entries come since in a small seal at its head."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.count = 0
        #: 0-1: how far through a pulse it is (0: none).
        self.glow = 0.0
        self.setObjectName("chronicle-strip")
        self.setFixedWidth(STRIP)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Open the Chronicle")

    def set_count(self, count: int) -> None:
        self.count = count
        self.setAccessibleName(f"Chronicle, {count} new")
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        painter.drawTiledPixmap(rect.toRect(), paper(self.p))
        gilding.gilt_frame(painter, rect, self.p, gap=3)
        if self.glow:
            accent = QColor(self.p["accent"])
            accent.setAlpha(round(160 * (1 - abs(1 - 2 * self.glow))))
            painter.fillRect(rect.adjusted(3, 3, -3, -3), accent)
        top = 12.0
        if self.count:
            seal = QRectF(rect.center().x() - 11, top, 22, 22)
            painter.setBrush(QColor(self.p["primary"]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(seal)
            painter.setPen(QColor(self.p["background"]))
            painter.setFont(number_font(9))
            painter.drawText(seal, Qt.AlignmentFlag.AlignCenter, str(self.count))
            top += 34
        painter.save()
        painter.translate(rect.center().x(), top)
        painter.rotate(90)
        painter.setPen(QColor(heading_ink(self.p)))
        painter.setFont(heading_font(12, self.p, caps=True))
        painter.drawText(QPoint(0, 5), "Chronicle")
        painter.restore()
        painter.end()


# -- the pane --


class Leaf(QWidget):
    """The open pane's gilt leaf, framed in the theme's own way."""

    def __init__(self, p: Palette) -> None:
        super().__init__()
        self.p = p

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        gilding.gilt_leaf(painter, QRectF(self.rect()), self.p)
        painter.end()


class ChroniclePane(QWidget):
    """The pane; `run` runs a command's steps (the window's run)."""

    def __init__(self, p: Palette, run: Callable[[Command], None]) -> None:
        super().__init__()
        self.p = p
        self.run = run
        self.setObjectName("chronicle-pane")
        self.saga: Saga | None = None
        self.session: Session | None = None
        #: What the pane shows: the host's Chronicle, or what a Remote
        #: seat was sent (SeatChronicle).
        self.book: chronicle.Chronicle | chronicle.SeatChronicle | None = None
        #: Hands a roll to the host from a Remote seat (None: this is the
        #: host's computer, which rolls itself).
        self.send_roll: free_roll.Submit | None = None
        self.who = ""
        self._stop: Callable[[], None] | None = None
        self.collapsed = False
        #: Entries come while collapsed, shown on the strip.
        self.unseen = 0
        #: How many times the strip has pulsed (one per entry for you).
        self.pulses = 0
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 4, 4, 4)
        outer.setSpacing(0)
        self.strip = Strip(p)
        self.strip.clicked.connect(lambda: self.set_collapsed(False))
        outer.addWidget(self.strip)
        self.body = self._leaf()
        outer.addWidget(self.body)
        self._draw_strip()
        self.hide()

    def _leaf(self) -> Leaf:
        """The open pane: its title, the feed and Free Roll on a gilt leaf."""
        p = self.p
        leaf = Leaf(p)
        leaf.setFixedWidth(WIDTH)
        column = QVBoxLayout(leaf)
        column.setContentsMargins(26, 22, 26, 22)
        column.setSpacing(4)
        head = QHBoxLayout()
        self.title = text("Chronicle", heading_ink(p), heading_font(16, p, caps=True))
        head.addWidget(self.title, 1)
        self.hide_button = QPushButton("›")
        self.hide_button.setFlat(True)
        self.hide_button.setToolTip("Collapse the Chronicle to a strip")
        self.hide_button.clicked.connect(lambda: self.set_collapsed(True))
        head.addWidget(self.hide_button)
        column.addLayout(head)
        self.rule = ShortRule(p)
        column.addWidget(self.rule)
        self.feed = QWidget()
        self.feed.setStyleSheet("background:transparent")
        self.cards = QVBoxLayout(self.feed)
        self.cards.setContentsMargins(0, 0, 4, 0)
        self.cards.setSpacing(0)
        self.cards.addStretch(1)
        self.scroller = QScrollArea()
        self.scroller.setWidgetResizable(True)
        self.scroller.setFrameShape(QFrame.Shape.NoFrame)
        self.scroller.setStyleSheet("QScrollArea { background:transparent; }")
        self.scroller.viewport().setAutoFillBackground(False)
        self.scroller.setWidget(self.feed)
        #: Whether the feed keeps to its newest card as it grows.
        self.follow = True
        bar = self.scroller.verticalScrollBar()
        bar.rangeChanged.connect(self._grown)
        bar.valueChanged.connect(self._scrolled)
        column.addWidget(self.scroller, 1)
        self.roll_button = edit_button("Free Roll", p, self.free_roll, "add")
        column.addWidget(self.roll_button)
        return leaf

    def set_palette(self, p: Palette) -> None:
        """Draw the pane in a new theme (its House's frame and colours)."""
        self.p = p
        self.strip.p = p
        self.body.p = p
        self.title.setStyleSheet(f"color:{heading_ink(p)}; background:transparent")
        self.title.setFont(heading_font(16, p, caps=True))
        self.rule.p = p
        self.roll_button.setIcon(pictures.icon("add", p["label"], 14))
        self._redraw_cards()
        self.update()

    # -- what it shows --

    def attach(
        self,
        saga: Saga,
        session: Session,
        book: chronicle.Chronicle | chronicle.SeatChronicle,
        who: str,
        send_roll: free_roll.Submit | None = None,
    ) -> None:
        """Show `book`, as `who` may see it, and listen for what comes. A
        Remote seat's book holds only what its host sent it; `send_roll`
        sends its rolls to the host."""
        self.send_roll = send_roll
        same = self.book is book and self.who == who
        self.saga, self.session = saga, session
        self.roll_button.setEnabled(free_roll.may_roll(saga, session, who))
        if same:
            return
        self.detach()
        self.book, self.who = book, who
        self.follow = True
        self._redraw_cards()
        stops = [book.subscribe(self._told)]
        if isinstance(book, chronicle.SeatChronicle):
            stops.append(book.when_cleared(self._redraw_cards))

        def stop() -> None:
            for each in stops:
                each()

        self._stop = stop
        self.roll_button.setEnabled(free_roll.may_roll(saga, session, who))
        self.show()

    def detach(self) -> None:
        """Stop listening, and empty the feed."""
        if self._stop is not None:
            self._stop()
        self._stop = None
        self.book = None
        self._clear_cards()
        self.unseen = 0
        self._draw_strip()
        self.hide()

    def card_list(self) -> list[Card]:
        found: list[Card] = []
        for index in range(self.cards.count() - 1):
            item = self.cards.itemAt(index)
            card = item.widget() if item is not None else None
            if isinstance(card, Card):
                found.append(card)
        return found

    def lines(self) -> list[str]:
        """Each card's line, top to bottom (the Chronicle's own lines)."""
        return [card.line for card in self.card_list()]

    def _told(self, entry: chronicle.Entry) -> None:
        """A new entry (Observer): shown if `who` reads it."""
        book, session = self.book, self.session
        if book is None or session is None:
            return
        if entry.kind == chronicle.VOID:
            self._redraw_cards()
            return
        if not self._reads(entry):
            return
        self._card(entry, chronicle.voided(book))
        if entry.kind in (chronicle.ROLL, chronicle.ROLLED):
            sounds.play("tock")
        if self.collapsed:
            self.unseen += 1
            self._draw_strip()
            if chronicle.calls_attention(entry, self.who, session, self.saga):
                self._pulse()

    def _grown(self, _low: int, high: int) -> None:
        """The feed grew: keep to the newest card, once laid out."""
        if self.follow:
            self.scroller.verticalScrollBar().setValue(high)

    def _scrolled(self, value: int) -> None:
        bar = self.scroller.verticalScrollBar()
        self.follow = value >= bar.maximum() - 4

    def _clear_cards(self) -> None:
        while self.cards.count() > 1:
            item = self.cards.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _redraw_cards(self) -> None:
        book, session = self.book, self.session
        if book is None or session is None:
            return
        self._clear_cards()
        struck = chronicle.voided(book)
        for entry in book.entries:
            if self._reads(entry):
                self._card(entry, struck)

    def _reads(self, entry: chronicle.Entry) -> bool:
        """Whether this reader reads `entry`: on the host, through the
        audience filter; at a seat, what the host sent (already filtered
        there, and sent without the Players chosen)."""
        session = self.session
        if session is None:
            return False
        if isinstance(self.book, chronicle.SeatChronicle):
            return not (entry.kind == chronicle.ROLLED and self._runs_the_session())
        return chronicle.reads(entry, self.who, session, self.saga)

    def _player_name(self, character_id: str) -> str:
        """Who plays `character_id` tonight, by name ("" for no one)."""
        saga, session = self.saga, self.session
        if saga is None or session is None or not character_id:
            return ""
        player = next(
            (c.player_id for c in session.castings if c.character_id == character_id),
            "",
        )
        return next((p.name for p in saga.players if p.id == player), "")

    def _card(self, entry: chronicle.Entry, struck: dict[int, str]) -> None:
        if entry.kind == chronicle.VOID:
            return
        line = chronicle.line(entry, struck)
        if entry.kind != chronicle.ROLL:
            self.cards.insertWidget(self.cards.count() - 1, note_card(line, self.p))
            return
        number = entry.number
        cancel = (lambda: self.void(number)) if self._cancels() else None
        card = roll_card(
            entry,
            line,
            self.p,
            self._player_name(str(entry.body.get("character_id") or "")),
            struck.get(number),
            cancel,
        )
        self.cards.insertWidget(self.cards.count() - 1, card)

    # -- collapsing --

    def set_collapsed(self, collapsed: bool) -> None:
        """Collapse to the strip, or open again; remembered."""
        if collapsed != remembered_collapsed():
            settings.update_settings(**{COLLAPSED: collapsed})
        self.collapsed = collapsed
        if not collapsed:
            self.unseen = 0
            self.follow = True
        self._draw_strip()

    def toggle(self) -> None:
        self.set_collapsed(not self.collapsed)

    def _draw_strip(self) -> None:
        self.body.setVisible(not self.collapsed)
        self.strip.setVisible(self.collapsed)
        self.strip.set_count(self.unseen)

    def _pulse(self) -> None:
        """Pulse the strip once (nothing with Reduce motion)."""
        if not motion.moving():
            return
        self.pulses += 1
        strip = self.strip

        def step(value: float) -> None:
            strip.glow = value
            strip.update()

        def done() -> None:
            strip.glow = 0.0
            strip.update()

        motion.tween(strip, step, PULSE_MS, name="pulse", done=done)

    # -- rolling --

    def _runs_the_session(self) -> bool:
        session = self.session
        return session is not None and self.who == chronicle.storyguide_of(
            session, self.saga
        )

    def _cancels(self) -> bool:
        """Cancel is the host's: its computer keeps the Chronicle."""
        return self._runs_the_session() and isinstance(self.book, chronicle.Chronicle)

    def void(self, number: int) -> None:
        """Cancel roll `number` (a Void in the Chronicle), asking why."""
        saga, session, book = self.saga, self.session, self.book
        if saga is None or session is None or not isinstance(book, chronicle.Chronicle):
            return
        self.run(free_roll.void_form(book, session, number, self.who, saga))

    def free_roll(self) -> None:
        saga, session, book = self.saga, self.session, self.book
        if saga is None or session is None or book is None:
            return
        who = self.who

        def submit(request: chronicle.RollRequest) -> str | None:
            if not isinstance(book, chronicle.Chronicle):
                return "Rolls go to the host."
            try:
                chronicle.free_roll(book, saga, session, request, by=who)
            except ValueError as problem:
                return str(problem)
            return None

        sent = self.send_roll or submit
        self.run(free_roll.free_roll_form(saga, session, who, sent))


def dice_of(card: QWidget) -> DiceRow | None:
    """A roll card's dice (for tests and the window's own use)."""
    return card.findChild(DiceRow, "dice")
