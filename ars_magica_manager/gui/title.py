"""The title page the desktop window opens on (title_page.TitlePage): the
illuminated initial, the name in gilt-edged letters and the tagline, and a
button for each way on, inside a burnished gilt frame on the paper. It
fades in; Enter takes the first way on (the saga opened last, else every
saga). On a small or highly scaled screen its margins, initial, name and
buttons shrink (FULL to COMPACT) so the window still fits.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QFont,
    QFontMetricsF,
    QKeySequence,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QShortcut,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

from .. import title_page as tp
from . import motion, pictures
from .style import gilding
from .style.illumination import IlluminatedInitial
from .style.ornaments import (
    Headpiece,
    ShortRule,
    Tailpiece,
    corner_flourishes,
)
from .style.paper import Paper
from .themes import Palette, wash_style
from .widgets import serif, text

#: How long the page takes to fade in, in milliseconds.
FADE_MS = 700
BACK = tp.BACK_CHOICE


@dataclass(frozen=True)
class Measures:
    """How the title page is laid out, in pixels (the name in points)."""

    #: The margins left and right, over the headpiece and under the edition.
    side: int
    top: int
    bottom: int
    #: The illuminated initial's side, and the name's size.
    initial: int
    name: int
    #: The gaps under the initial, the name, its rule, the tagline and the
    #: buttons.
    gaps: tuple[int, int, int, int, int]
    #: A button's width, and the gap between two.
    button: int
    between: int

    def toward(self, other: Measures, share: float) -> Measures:
        """These measures moved `share` (0 to 1) of the way to `other`'s."""

        def mix(a: int, b: int) -> int:
            return round(a + (b - a) * share)

        return Measures(
            mix(self.side, other.side),
            mix(self.top, other.top),
            mix(self.bottom, other.bottom),
            mix(self.initial, other.initial),
            mix(self.name, other.name),
            (
                mix(self.gaps[0], other.gaps[0]),
                mix(self.gaps[1], other.gaps[1]),
                mix(self.gaps[2], other.gaps[2]),
                mix(self.gaps[3], other.gaps[3]),
                mix(self.gaps[4], other.gaps[4]),
            ),
            mix(self.button, other.button),
            mix(self.between, other.between),
        )


#: The page as it is drawn wherever there is room for it.
FULL = Measures(80, 54, 40, 210, 64, (10, 4, 6, 40, 16), 250, 22)
#: The least it shrinks to, for a small or highly scaled screen: the
#: margins, gaps, initial, name and buttons scale between the two.
COMPACT = Measures(44, 32, 24, 110, 40, (4, 2, 3, 14, 6), 190, 12)
#: A button's height when its lines fit it unwrapped.
BUTTON_HEIGHT = 74
#: The steps the page scales by, so dragging an edge relays it out only
#: now and then.
STEPS = 20


def _choice_button(choice: tp.TitleChoice, p: Palette, first: bool) -> QPushButton:
    """A way on: its name over a line saying where it goes. The first is
    edged in the rubric colour, as the one Enter takes."""
    button = QPushButton()
    button.setObjectName("titleChoice")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setFixedSize(FULL.button, BUTTON_HEIGHT)
    edge = p["heading"] if first else p["accent"]
    button.setStyleSheet(
        f"""
        QPushButton#titleChoice {{
            background: {p["surface"]};
            border: {2 if first else 1}px solid {edge};
            border-radius: 3px;
        }}
        QPushButton#titleChoice:hover, QPushButton#titleChoice:focus {{
            border: 2px solid {p["accent"]};
            background: {wash_style(p)};
        }}
        """
    )
    column = QVBoxLayout(button)
    column.setContentsMargins(10, 8, 10, 8)
    column.setSpacing(0)
    for words, colour, font in (
        (choice.label, p["heading"], serif(15)),
        (choice.detail, p["label"], serif(12, italic=True)),
    ):
        if not words:
            continue
        # A narrow button wraps its line rather than cut it off.
        label = text(words, colour, font, wrap=True)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        column.addWidget(label)
    return button


class GiltTitle(QLabel):
    """The book's name, every letter in the rubric's colour with a gilt
    edge (gilding.gilt_word). Its text is the name, so it reads as a
    plain label; only its painting is its own."""

    def __init__(self, name: str, p: Palette, font: QFont) -> None:
        super().__init__(name)
        self.p = p
        self.setFont(font)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    def paintEvent(self, _event: QPaintEvent) -> None:
        metrics = QFontMetricsF(self.font())
        box = QRectF(self.contentsRect())
        width = metrics.horizontalAdvance(self.text())
        height = metrics.ascent() + metrics.descent()
        baseline = QPointF(
            box.left() + (box.width() - width) / 2,
            box.top() + (box.height() - height) / 2 + metrics.ascent(),
        )
        painter = QPainter(self)
        gilding.gilt_word(painter, self.text(), self.font(), baseline, self.p)
        painter.end()


class TitleScreen(Paper):
    """The title page, calling `choose` with the key of the way on
    chosen (title_page.OPEN, SAGAS, NEW, JOIN, TUTORIAL or HELP; Learn
    opens onto Tutorials and General Help)."""

    def __init__(
        self, page: tp.TitlePage, p: Palette, choose: Callable[[str], None]
    ) -> None:
        super().__init__(p)
        self.page = page
        self.choose = choose
        #: How far the page is scaled from COMPACT (0) to FULL (1), and
        #: the least and most room it takes with the buttons on show.
        self.share: float | None = None
        self.span = (QSize(), QSize())
        self.column = column = QVBoxLayout(self)
        column.setContentsMargins(FULL.side, FULL.top, FULL.side, FULL.bottom)
        column.setSpacing(0)
        column.addWidget(Headpiece(p))
        column.addStretch(2)
        self.initial = IlluminatedInitial(page.name[0], p, FULL.initial)
        column.addWidget(self.initial, 0, Qt.AlignmentFlag.AlignHCenter)
        self.gaps: list[QSpacerItem] = []

        def gap() -> None:
            self.gaps.append(QSpacerItem(0, 0))
            column.addSpacerItem(self.gaps[-1])

        gap()
        #: The book's name in gilt-edged letters.
        self.name = GiltTitle(page.name, p, QFont(pictures.TITLE, FULL.name))
        column.addWidget(self.name)
        gap()
        column.addWidget(ShortRule(p))
        gap()
        tagline = text(page.tagline, p["label"], serif(20, italic=True, caps=True))
        tagline.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(tagline)
        gap()
        self.p = p
        self.row = QHBoxLayout()
        self.row.setSpacing(22)
        #: The buttons on show, by the key of their way on.
        self.buttons: dict[str, QPushButton] = {}
        #: The line saying what Enter takes: the first button on show.
        self.hint = text("", p["dim"], serif(11.5, italic=True))
        self.hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.show_choices(page.choices)
        column.addLayout(self.row)
        gap()
        column.addWidget(self.hint)
        column.addStretch(3)
        column.addWidget(Tailpiece(p))
        edition = text(page.edition, p["dim"], serif(11))
        edition.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(edition)
        for key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            QShortcut(
                QKeySequence(key),
                self,
                lambda: next(iter(self.buttons.values())).click(),
            )
        self._measure()

    # Fitting the window

    def _lay_out(self, m: Measures) -> None:
        """Lay the page out by `m`."""
        self.column.setContentsMargins(m.side, m.top, m.side, m.bottom)
        for spacer, height in zip(self.gaps, m.gaps, strict=True):
            spacer.changeSize(
                0, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
            )
        self.initial.set_side(m.initial)
        self.name.setFont(QFont(pictures.TITLE, m.name))
        self.row.setSpacing(m.between)
        tall = BUTTON_HEIGHT
        for button in self.buttons.values():
            inside = button.layout()
            if inside is not None and inside.hasHeightForWidth():
                tall = max(tall, inside.heightForWidth(m.button))
        for button in self.buttons.values():
            button.setFixedSize(m.button, tall)
        self.column.invalidate()

    def _measure(self) -> None:
        """Find the least and most room the page takes with the buttons on
        show; the least is the page's (and so the window's) minimum."""
        if len(self.gaps) < len(FULL.gaps):
            return  # still being built
        self._lay_out(COMPACT)
        least = self.column.minimumSize()
        self._lay_out(FULL)
        self.span = (least, self.column.minimumSize())
        self.setMinimumSize(least)
        self.share = None
        self._fit()

    def _fit(self) -> None:
        """Scale the page to the room it has, as large as fits."""
        if len(self.gaps) < len(FULL.gaps):
            return
        least, most = self.span

        def room(have: int, low: int, high: int) -> float:
            return 1.0 if high <= low else (have - low) / (high - low)

        share = min(
            room(self.width(), least.width(), most.width()),
            room(self.height(), least.height(), most.height()),
        )
        share = max(0.0, min(1.0, int(share * STEPS) / STEPS))
        if share == self.share:
            return
        self.share = share
        self._lay_out(COMPACT.toward(FULL, share))
        # The measures don't scale quite in a line: step down until it fits.
        while share > 0 and not self._fits():
            share = max(0.0, share - 1 / STEPS)
            self._lay_out(COMPACT.toward(FULL, share))

    def _fits(self) -> bool:
        need = self.column.minimumSize()
        return need.width() <= self.width() and need.height() <= self.height()

    def minimumSizeHint(self) -> QSize:
        return self.span[0] if self.span[0].isValid() else super().minimumSizeHint()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._fit()

    def show_choices(self, choices: tuple[tp.TitleChoice, ...]) -> None:
        """Lay out `choices` as the row of buttons, in place of those on
        show. A choice that opens onto choices of its own (Learn) shows
        them, with Back to return to the page's own."""
        for button in self.buttons.values():
            button.deleteLater()
        self.buttons = {}
        while self.row.count():
            self.row.takeAt(0)
        self.row.addStretch(1)
        for i, choice in enumerate(choices):
            button = _choice_button(choice, self.p, first=i == 0)
            if choice.then:
                ways = (*choice.then, BACK)
                button.clicked.connect(
                    lambda _checked=False, ways=ways: self.show_choices(ways)
                )
            elif choice.key == BACK.key:
                button.clicked.connect(
                    lambda _checked=False: self.show_choices(self.page.choices)
                )
            else:
                button.clicked.connect(
                    lambda _checked=False, key=choice.key: self.choose(key)
                )
            self.row.addWidget(button)
            self.buttons[choice.key] = button
        self.row.addStretch(1)
        next(iter(self.buttons.values())).setFocus()
        self.hint.setText(f"Enter: {choices[0].label}")
        self._measure()

    def fade_in(self) -> None:
        """Fade the page in from the paper."""
        if not motion.moving():
            return
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        # Drop the effect once faded in, so the page is drawn directly.
        motion.tween(
            self,
            effect.setOpacity,
            FADE_MS,
            name="fade",
            # Qt takes None to remove an effect; its stub asks for one.
            done=lambda: self.setGraphicsEffect(None),  # type: ignore[arg-type]
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        p = self.p
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        frame = QRectF(self.rect()).adjusted(28, 22, -28, -22)
        gilding.gilt_frame(painter, frame, p, gap=6)
        corner_flourishes(painter, frame.adjusted(10, 10, -10, -10), p, 34)
        painter.end()
