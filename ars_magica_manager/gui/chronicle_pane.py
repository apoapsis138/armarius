"""The Chronicle pane (the Virtual Tabletop preview): docked on the right
of the saga window while a Session is Under way, it shows the Chronicle as
whoever sits here may see it, on a gilt leaf like the Inspector's, in the
theme's own frame. Each roll is a card: who rolled (the character, and its
player in smaller type), what for, the dice as ten-sided dice with their
faces, and the outcome, set largest. A Free Roll button sits at its foot.

The Session's storyguide strikes a roll with the Strike beside its dice,
or Strike on the dice's menu. A struck roll keeps its card, quietly:
the card faded, a fine rule struck through its dice and its total, and
"Struck" with the reason beneath in small italic.

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

from .. import (
    artwork,
    at_table,
    chronicle,
    dice_text,
    host_table,
    references,
    settings,
    table_rules,
)
from ..commands import Command, Refuse
from ..forms import free_roll, roll_request
from ..forms import message as message_forms
from ..markup import escape
from ..models import Saga, Session
from ..rules import dice as dice_rules
from ..style import fonts
from . import motion, pictures, sounds
from .figures import linked_value
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


def margin_mark(name: str, label: str, tip: str, p: Palette, hover: str) -> QToolButton:
    """A quiet word in a card's margin that acts when clicked (Strike,
    Confidence): italic, unframed, underlined in `hover` under the pointer."""
    mark = QToolButton()
    mark.setObjectName(name)
    mark.setText(label)
    mark.setToolTip(tip)
    mark.setAutoRaise(True)
    mark.setCursor(Qt.CursorShape.PointingHandCursor)
    mark.setFont(serif(11, italic=True))
    mark.setStyleSheet(
        f"QToolButton#{name} {{ color:{p['label']}; border:none;"
        " background:transparent; padding:0 2px; }"
        f" QToolButton#{name}:hover {{ color:{hover};"
        " text-decoration:underline; }"
    )
    return mark


def _dice_of(
    body: dict[str, object], *, form: bool
) -> list[tuple[list[int], bool, list[int]]]:
    """A roll's dice to draw, each as its faces thrown, whether a stress
    die, and its botch dice: a sheet or Free roll's one die; a form roll's
    (`form`) whole dice (a face drawn outside the die helpers on its own),
    or, written before whole dice were kept, every face as drawn."""
    if not form:
        stress = bool(body.get("stress"))
        faces = _wholes(body, "faces") if stress else [_whole(body, "die")]
        return [(faces, stress, _wholes(body, "botch_faces"))]
    kept = body.get("dice")
    if not isinstance(kept, list):
        return [(_wholes(body, "faces"), False, [])]
    found: list[tuple[list[int], bool, list[int]]] = []
    for die in kept:
        if not isinstance(die, dict):
            continue
        if "face" in die:
            found.append(([_whole(die, "face")], False, []))
            continue
        whole = dice_text.whole_die(die)
        if whole.stress:
            found.append((list(whole.faces), True, list(whole.botch_faces)))
        else:  # a simple die, or botch dice rolled on their own
            shown = [whole.value] if whole.faces else []
            found.append((shown, False, list(whole.botch_faces)))
    return found


class DiceRow(QWidget):
    """A roll's dice: the die's throws, then any botch dice. A struck
    roll's are faded and struck through. `strike` (the Session's
    storyguide only) is a Strike beside them, and on the dice's menu;
    `spend` (whoever may spend Confidence on it) a Confidence beside them,
    and on the menu too."""

    def __init__(
        self,
        body: dict[str, object],
        p: Palette,
        struck: bool,
        strike: Callable[[], None] | None,
        spend: Callable[[], None] | None = None,
        *,
        form: bool = False,
    ) -> None:
        super().__init__()
        self.p, self.struck, self._strike = p, struck, strike
        self._spend = spend
        self.setObjectName("dice")
        rows = QVBoxLayout(self)
        rows.setContentsMargins(0, 4, 0, 4)
        rows.setSpacing(2)
        row = QHBoxLayout()
        row.setSpacing(2)
        rows.addLayout(row)
        for index, (faces, stress, botch) in enumerate(_dice_of(body, form=form)):
            if index:
                row.addSpacing(10)
            row = self._draw_die(rows, row, faces, stress, botch)
        row.addStretch(1)
        #: Strike, for the Session's storyguide on a roll still counting, and
        #: Confidence, for whoever may spend it: quiet words in the margin,
        #: not framed buttons.
        self.confidence_mark = margin_mark(
            "confidence",
            "Confidence",
            "Spend Confidence: +3 a point",
            p,
            p["foreground"],
        )
        self.confidence_mark.clicked.connect(self.spend)
        self.confidence_mark.setVisible(self.can_spend)
        row.addWidget(self.confidence_mark, 0, Qt.AlignmentFlag.AlignBottom)
        self.strike_mark = margin_mark(
            "strike",
            "Strike",
            "Strike this roll from the count, with a reason",
            p,
            p["text-error"],
        )
        self.strike_mark.clicked.connect(self.strike)
        self.strike_mark.setVisible(self.can_strike)
        row.addWidget(self.strike_mark, 0, Qt.AlignmentFlag.AlignBottom)

    def _draw_die(
        self,
        rows: QVBoxLayout,
        row: QHBoxLayout,
        faces: list[int],
        stress: bool,
        botch: list[int],
    ) -> QHBoxLayout:
        """One die's throws on `row`, each doubling marked, then its botch
        dice (on a line of their own when there are many): the row the
        next die goes on."""
        p, struck = self.p, self.struck
        for index, face in enumerate(faces):
            shown = face if index == 0 or face or not stress else 10
            zero = stress and index == 0 and shown == 0
            exploded = stress and index < len(faces) - 1 and face == 1
            colour = (
                p["dim"] if struck else (p["text-error"] if zero else p["foreground"])
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
        if not botch:
            return row
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
                    p["dim"] if struck else colour,
                    BOTCH_DIE,
                    "botch",
                    marked=face == 0,
                    paper=p["background"],
                )
            )
        return row

    @property
    def can_strike(self) -> bool:
        return self._strike is not None and not self.struck

    @property
    def can_spend(self) -> bool:
        return self._spend is not None and not self.struck

    def strike(self) -> None:
        if self._strike is not None and not self.struck:
            self._strike()

    def spend(self) -> None:
        if self._spend is not None and not self.struck:
            self._spend()

    def menu(self) -> QMenu:
        """The dice's menu: Spend Confidence, for whoever may; Strike this
        roll, for the Session's storyguide."""
        found = QMenu(self)
        if self._spend is not None:
            confidence = found.addAction("Spend Confidence…")
            confidence.setEnabled(self.can_spend)
            confidence.triggered.connect(self.spend)
        action = found.addAction("Strike this roll…")
        action.setEnabled(self.can_strike)
        action.triggered.connect(self.strike)
        return found

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        if self.can_strike or self.can_spend:
            self.menu().exec(event.globalPos())

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        if not self.struck:
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


def message_card(
    line: str,
    p: Palette,
    fact: references.Fact,
    follow: Callable[[references.Ref], None],
) -> Card:
    """A Message: who it is from (and for a Whisper, to whom) in small
    type, then its words, each record named that the reader may open a
    link."""
    card = Card(line, p)
    card.column.addWidget(
        text(escape(fact.label), p["label"], serif(10.5, italic=True))
    )
    words = linked_value(fact, p, follow)
    # Rich text runs lines together: the line breaks written are kept.
    words.setText(words.text().replace("\n", "<br>"))
    words.setObjectName("message-words")
    card.column.addWidget(words)
    return card


#: One character of a Roll request, as its card shows it: the name,
#: what came of it so far, and the answers this reader may give (a label
#: and what it does).
RequestRow = tuple[str, str, list[tuple[str, Callable[[], None]]]]


def request_card(
    line: str,
    p: Palette,
    rows: list[RequestRow],
    kept: str,
    outcome: Callable[[], None] | None,
) -> Card:
    """A Roll request: what it asks, then each character with its answer
    as it comes in (the Roll buttons for whoever answers it), the Ease
    Factor kept from the players (`kept`, the storyguide's alone) and, for
    the storyguide, an outcome to note."""
    card = Card(line, p)
    asked = text(line, heading_ink(p), serif(12, italic=True), wrap=True)
    asked.setObjectName("asked")
    card.column.addWidget(asked)
    for name, result, rolls in rows:
        row = QHBoxLayout()
        row.setSpacing(6)
        who = text(name, p["foreground"], heading_font(11.5, p, caps=True))
        who.setObjectName("who")
        row.addWidget(who)
        row.addStretch(1)
        shown = text(result, p["label"], number_font(11, bold=False))
        shown.setObjectName("result")
        row.addWidget(shown)
        for label, act in rolls:
            button = margin_mark(
                "answer", label, f"{label}: rolled at the host", p, p["foreground"]
            )
            button.clicked.connect(lambda _checked=False, act=act: act())
            row.addWidget(button)
        card.column.addLayout(row)
    if kept:
        hidden = text(kept, p["label"], serif(10.5, italic=True), wrap=True)
        hidden.setObjectName("kept")
        card.column.addWidget(hidden)
    if outcome is not None:
        note = margin_mark(
            "outcome", "Outcome", "Note what came of it", p, p["foreground"]
        )
        note.clicked.connect(lambda _checked=False: outcome())
        card.column.addWidget(note, 0, Qt.AlignmentFlag.AlignLeft)
    return card


def roll_card(
    entry: chronicle.Entry,
    line: str,
    p: Palette,
    who_rolled: str,
    reason: str | None,
    strike: Callable[[], None] | None,
    spend: Callable[[], None] | None = None,
) -> Card:
    """Who rolled, what for, how the total was made (a roll from the
    sheet), the dice and the outcome; `reason` when the roll was struck."""
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
    _mark_visibility(top, entry, p)
    card.column.addLayout(top)
    if body.get("for"):
        ink = p["dim"] if quiet else p["foreground"]
        what = text(str(body["for"]), ink, serif(12, italic=True), wrap=True)
        what.setObjectName("what")
        card.column.addWidget(what)
    terms = chronicle.terms_of(body)
    if not (len(terms) == 1 and terms[0][0] == "Modifier"):
        made = text(
            chronicle.terms_text(terms),
            p["dim"] if quiet else p["label"],
            serif(10.5),
            wrap=True,
        )
        made.setObjectName("terms")
        card.column.addWidget(made)
    card.column.addWidget(DiceRow(body, p, reason is not None, strike, spend))
    card.column.addWidget(_outcome(body, p, reason is not None))
    if reason is not None:
        why = text(f"Struck: {reason}", p["label"], serif(10.5, italic=True), wrap=True)
        why.setObjectName("reason")
        card.column.addWidget(why)
    return card


def _mark_visibility(top: QHBoxLayout, entry: chronicle.Entry, p: Palette) -> None:
    """A roll's Blind or Private mark, at the right of its card's top."""
    tag = chronicle.visibility_tag(entry.audience)
    if tag:
        mark = text(tag, p["label"], serif(10, caps=True))
        mark.setObjectName("visibility")
        top.addWidget(mark)


def form_roll_card(
    entry: chronicle.Entry,
    line: str,
    p: Palette,
    who_rolled: str,
    reason: str | None,
    strike: Callable[[], None] | None,
) -> Card:
    """A Table roll made from a form: who rolled, the form, every face the
    host drew, and the form's own result, word for word (or that it was
    drawn, then cancelled); `reason` when it was struck."""
    body = entry.body
    card = Card(line, p)
    quiet = reason is not None
    top = QHBoxLayout()
    top.setSpacing(6)
    character = str(body.get("character_name") or "") or "The storyguide"
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
    _mark_visibility(top, entry, p)
    card.column.addLayout(top)
    ink = p["dim"] if quiet else p["foreground"]
    what = text(str(body.get("form") or ""), ink, serif(12, italic=True), wrap=True)
    what.setObjectName("what")
    card.column.addWidget(what)
    card.column.addWidget(DiceRow(body, p, quiet, strike, form=True))
    kept = body.get("dice")
    wholes = (
        [d for d in kept if isinstance(d, dict) and "face" not in d]
        if isinstance(kept, list)
        else []
    )
    if wholes:  # faces drawn outside the die helpers are drawn, not said
        said = dice_text.dice_text(wholes)
        line_of_dice = text(said, p["dim"] if quiet else p["label"], serif(10.5))
        line_of_dice.setObjectName("dice-line")
        line_of_dice.setWordWrap(True)
        card.column.addWidget(line_of_dice)
    lines = [str(said) for said in _list(body, "lines")]
    if body.get("cancelled"):
        lines = ["Drawn, then cancelled."]
    for said in lines:
        shown = text(said, p["dim"] if quiet else p["label"], serif(11), wrap=True)
        shown.setObjectName("result")
        card.column.addWidget(shown)
    if reason is not None:
        why = text(f"Struck: {reason}", p["label"], serif(10.5, italic=True), wrap=True)
        why.setObjectName("reason")
        card.column.addWidget(why)
    return card


def _list(body: dict[str, object], key: str) -> list[object]:
    found = body.get(key)
    return list(found) if isinstance(found, list) else []


def _outcome(body: dict[str, object], p: Palette, struck: bool) -> QWidget:
    """The total, set largest, and against the Ease Factor what came of it."""
    box = QWidget()
    box.setObjectName("outcome")
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    botches = _whole(body, "botches")
    ink = p["dim"] if struck else (p["text-error"] if botches else p["foreground"])
    font = number_font(20)
    font.setStrikeOut(struck)
    total = text(str(_whole(body, "total")), ink, font)
    total.setObjectName("total")
    if struck:
        # Struck through as rich text: the label's style sheet sets its font.
        total.setTextFormat(Qt.TextFormat.RichText)
        total.setText(f"<s>{_whole(body, 'total')}</s>")
    row.addWidget(total, 0, Qt.AlignmentFlag.AlignVCenter)
    modifier = _whole(body, "modifier")
    sign = "+" if modifier >= 0 else "−"
    die = dice_rules.DieResult(
        value=_whole(body, "die"),
        faces=tuple(_wholes(body, "faces")),
        stress=body.get("stress") is True,
        botch_faces=tuple(_wholes(body, "botch_faces")),
    )
    said = [f"die {dice_text.doubled(die)} {sign} {abs(modifier)}"]
    if botches:
        said.append(f"botch, {botches} zero{'s' if botches > 1 else ''}")
    if body.get("ease_factor") is not None:
        verdict = "succeeds" if body.get("succeeded") else "fails"
        margin = _whole(body, "margin")
        said.append(f"vs {body['ease_factor']}: {verdict} by {abs(margin)}")
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
        #: The table as whoever sits here acts at it: the host's own
        #: Chronicle, or a Remote seat asking its host (at_table.Table).
        self.table: at_table.Table | None = None
        #: Opens a record a Message links (the window's open_ref).
        self.open_record: Callable[[references.Ref], None] = lambda _ref: None
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
        self.message_button = edit_button("Message", p, self.compose, "add")
        column.addWidget(self.message_button)
        #: The storyguide's Roll request, on the host's computer.
        self.request_button = edit_button("Roll Request", p, self.request_rolls, "add")
        self.request_button.setVisible(False)
        column.addWidget(self.request_button)
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
        self.message_button.setIcon(pictures.icon("add", p["label"], 14))
        self.request_button.setIcon(pictures.icon("add", p["label"], 14))
        self._redraw_cards()
        self.update()

    # -- what it shows --

    def attach(
        self,
        saga: Saga,
        session: Session,
        book: chronicle.Chronicle | chronicle.SeatChronicle,
        who: str,
        table: at_table.Table | None = None,
    ) -> None:
        """Show `book`, as `who` may see it, and listen for what comes. A
        Remote seat's book holds only what its host sent it, and its
        `table` asks the host for each roll, spend, answer and Message; on
        the host's own computer the table is its Chronicle."""
        if table is None and isinstance(book, chronicle.Chronicle):
            table = host_table.HostTable(saga, session, who)
        self.table = table
        self.request_button.setVisible(
            isinstance(book, chronicle.Chronicle)
            and who == chronicle.storyguide_of(session, saga)
        )
        same = self.book is book and self.who == who
        self.saga, self.session = saga, session
        self.roll_button.setEnabled(free_roll.may_roll(saga, session, who))
        self.message_button.setEnabled(who in chronicle.at_session(saga, session))
        if same:
            return
        self.detach()
        self.table = table
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
        self.table = None
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
        spec = chronicle.kind_of(entry)
        if spec is not None and spec.amends(entry):
            # It changes cards already drawn (a Strike, a Roll request's
            # answer or outcome, Confidence spent): all drawn again.
            self._redraw_cards()
            if self._reads(entry):
                if spec.sounds:
                    sounds.play("tock")
                if spec.card != chronicle.NO_CARD:
                    self._came_while_collapsed(entry)
            return
        if not self._reads(entry):
            return
        self._card(entry, chronicle.voided(book))
        if spec is not None and spec.sounds:
            sounds.play("tock")
        self._came_while_collapsed(entry)

    def _came_while_collapsed(self, entry: chronicle.Entry) -> None:
        """Count `entry` on a collapsed strip, and pulse it if the entry is
        for whoever reads (its kind's rule, or the host's word at a seat)."""
        if not self.collapsed:
            return
        self.unseen += 1
        self._draw_strip()
        reader = self._reader()
        if reader is not None and reader.calls_attention(entry):
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

    def _reader(self) -> chronicle.Reader | None:
        """The Chronicle as whoever sits here reads it (host or seat)."""
        book, session = self.book, self.session
        if book is None or session is None:
            return None
        return chronicle.Reader(book, self.who, session, self.saga)

    def _reads(self, entry: chronicle.Entry) -> bool:
        reader = self._reader()
        return reader is not None and reader.reads(entry)

    def _player_name(self, character_id: str) -> str:
        """Who plays `character_id` tonight, by name ("" for no one)."""
        saga, session = self.saga, self.session
        if saga is None or session is None or not character_id:
            return ""
        player = table_rules.player_of(session, character_id)
        return next((p.name for p in saga.players if p.id == player), "")

    def _card(self, entry: chronicle.Entry, struck: dict[int, str]) -> None:
        spec = chronicle.kind_of(entry)
        shown = spec.card if spec is not None else chronicle.NOTE
        if shown == chronicle.NO_CARD:
            return
        if shown == chronicle.REQUEST_CARD:
            self.cards.insertWidget(self.cards.count() - 1, self._request_card(entry))
            return
        line = chronicle.line(entry, struck)
        number = entry.number
        strike = (lambda: self.strike_roll(number)) if self._strikes() else None
        if shown == chronicle.FORM_ROLL_CARD:
            card = form_roll_card(
                entry,
                line,
                self.p,
                self._player_name(str(entry.body.get("character_id") or "")),
                struck.get(number),
                strike,
            )
            self.cards.insertWidget(self.cards.count() - 1, card)
            return
        if shown == chronicle.MESSAGE_CARD and self.saga is not None:
            viewer = chronicle.viewer_of(self.saga, self.who)
            fact = chronicle.message_fact(entry, self.saga, viewer)
            card = message_card(line, self.p, fact, lambda ref: self.open_record(ref))
            self.cards.insertWidget(self.cards.count() - 1, card)
            return
        if shown != chronicle.ROLL_CARD:
            self.cards.insertWidget(self.cards.count() - 1, note_card(line, self.p))
            return
        spend = (
            (lambda: self.spend_confidence(number)) if self._spends(number) else None
        )
        card = roll_card(
            entry,
            line,
            self.p,
            self._player_name(str(entry.body.get("character_id") or "")),
            struck.get(number),
            strike,
            spend,
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
        reader = self._reader()
        return reader is not None and reader.runs_the_session

    def _strikes(self) -> bool:
        """Strike is the host's: its computer keeps the Chronicle."""
        return self._runs_the_session() and isinstance(self.book, chronicle.Chronicle)

    def _request_card(self, entry: chronicle.Entry) -> Card:
        """Roll request `entry`'s card, its answers as this reader sees them."""
        book = self.book
        reader = self._reader()
        line = chronicle.line(entry, {})
        assert book is not None and reader is not None
        runs = reader.runs_the_session
        hidden = reader.kept_ease(entry)
        rows: list[RequestRow] = []
        for asked in entry.body.get("characters", []):
            cid = str(asked.get("id"))
            result = reader.answer_result(entry, cid)
            rolls: list[tuple[str, Callable[[], None]]] = []
            if reader.may_answer(entry, cid):
                rolls.append(("Roll", self._answers(entry.number, cid, False)))
                specialty = self._specialty(cid, str(entry.body.get("ability") or ""))
                if specialty:
                    rolls.append(
                        (f"Roll ({specialty})", self._answers(entry.number, cid, True))
                    )
            rows.append((str(asked.get("name") or ""), result, rolls))
        kept = (
            f"Ease Factor {hidden}, kept from the players."
            if hidden is not None
            else ""
        )
        outcome = (
            (lambda: self.note_outcome(entry.number))
            if runs and isinstance(book, chronicle.Chronicle)
            else None
        )
        return request_card(line, self.p, rows, kept, outcome)

    def _specialty(self, character_id: str, ability: str) -> str:
        saga = self.saga
        if saga is None or not ability:
            return ""
        character = next((c for c in saga.characters if c.id == character_id), None)
        held = (
            next((a for a in character.abilities if a.name == ability), None)
            if character is not None
            else None
        )
        return held.specialty or "" if held is not None else ""

    def _answers(
        self, number: int, character_id: str, specialty: bool
    ) -> Callable[[], None]:
        def act() -> None:
            self.answer(number, character_id, specialty=specialty)

        return act

    def answer(
        self, number: int, character_id: str, *, specialty: bool = False
    ) -> None:
        """Answer Roll request `number` for `character_id`: rolled at the
        host (sent there from a Remote seat)."""
        table = self.table
        if table is None:
            return
        refused = table.answer(number, character_id, specialty)
        if refused:
            self.run(Refuse("Roll", escape(refused)))

    def request_rolls(self) -> None:
        saga, session, book = self.saga, self.session, self.book
        if saga is None or session is None or not isinstance(book, chronicle.Chronicle):
            return
        self.run(roll_request.request_form(saga, session, self.who, book))

    def note_outcome(self, number: int) -> None:
        saga, session, book = self.saga, self.session, self.book
        if saga is None or session is None or not isinstance(book, chronicle.Chronicle):
            return
        self.run(roll_request.outcome_form(book, saga, session, number, self.who))

    def _spends(self, number: int) -> bool:
        """Whether whoever sits here may spend Confidence on roll `number`
        now (a point at least)."""
        saga, session, book = self.saga, self.session, self.book
        if saga is None or session is None or book is None:
            return False
        return chronicle.why_not_spend(book, saga, session, number, 1, self.who) is None

    def spend_confidence(self, number: int) -> None:
        """Spend Confidence on roll `number`, asking how much."""
        saga, session, book, table = self.saga, self.session, self.book, self.table
        if saga is None or session is None or book is None or table is None:
            return

        def spend(points: int) -> str | None:
            return table.spend(number, points)

        self.run(
            free_roll.confidence_form(book, saga, session, number, self.who, spend)
        )

    def strike_roll(self, number: int) -> None:
        """Strike roll `number` from the count, asking why."""
        saga, session, book = self.saga, self.session, self.book
        if saga is None or session is None or not isinstance(book, chronicle.Chronicle):
            return
        self.run(free_roll.strike_form(book, session, number, self.who, saga))

    def free_roll(self) -> None:
        saga, session, table = self.saga, self.session, self.table
        if saga is None or session is None or table is None:
            return
        self.run(free_roll.free_roll_form(saga, session, self.who, table.roll))

    def compose(self) -> None:
        """Write a Message: to the Table, or a Whisper."""
        saga, session, table = self.saga, self.session, self.table
        if saga is None or session is None or table is None:
            return
        self.run(message_forms.message_form(saga, session, self.who, table.say))


def dice_of(card: QWidget) -> DiceRow | None:
    """A roll card's dice (for tests and the window's own use)."""
    return card.findChild(DiceRow, "dice")
