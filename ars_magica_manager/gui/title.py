"""The title page the desktop window opens on (title_page.TitlePage): the
illuminated initial, the name in gilt-edged letters and the tagline, and a
button for each way on, inside a burnished gilt frame on the paper. It
fades in; Enter takes the first way on (the saga opened last, else every
saga).
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import (
    QFont,
    QFontMetricsF,
    QKeySequence,
    QPainter,
    QPaintEvent,
    QShortcut,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from .. import title_page as tp
from . import gilding, pictures
from .illumination import IlluminatedInitial
from .ornaments import Headpiece, ShortRule, Tailpiece, corner_flourishes
from .paper import Paper
from .themes import Palette, wash_style
from .widgets import serif, text

#: How long the page takes to fade in, in milliseconds.
FADE_MS = 700


def _choice_button(choice: tp.TitleChoice, p: Palette, first: bool) -> QPushButton:
    """A way on: its name over a line saying where it goes. The first is
    edged in the rubric colour, as the one Enter takes."""
    button = QPushButton()
    button.setObjectName("titleChoice")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setFixedSize(250, 74)
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
        label = text(words, colour, font)
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
    chosen (title_page.OPEN, SAGAS or HELP)."""

    def __init__(
        self, page: tp.TitlePage, p: Palette, choose: Callable[[str], None]
    ) -> None:
        super().__init__(p)
        self.page = page
        self.choose = choose
        column = QVBoxLayout(self)
        column.setContentsMargins(80, 54, 80, 40)
        column.setSpacing(0)
        column.addWidget(Headpiece(p))
        column.addStretch(2)
        column.addWidget(
            IlluminatedInitial(page.name[0], p), 0, Qt.AlignmentFlag.AlignHCenter
        )
        column.addSpacing(10)
        #: The book's name in gilt-edged letters.
        self.name = GiltTitle(page.name, p, QFont(pictures.DISPLAY, 64))
        column.addWidget(self.name)
        column.addSpacing(4)
        column.addWidget(ShortRule(p))
        column.addSpacing(6)
        tagline = text(page.tagline, p["label"], serif(20, italic=True, caps=True))
        tagline.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(tagline)
        column.addSpacing(40)
        row = QHBoxLayout()
        row.setSpacing(22)
        row.addStretch(1)
        #: The buttons, by the key of their way on.
        self.buttons: dict[str, QPushButton] = {}
        for i, choice in enumerate(page.choices):
            button = _choice_button(choice, p, first=i == 0)
            button.clicked.connect(
                lambda _checked=False, key=choice.key: self.choose(key)
            )
            row.addWidget(button)
            self.buttons[choice.key] = button
        row.addStretch(1)
        column.addLayout(row)
        column.addSpacing(16)
        first = page.choices[0]
        hint = text(f"Enter: {first.label}", p["dim"], serif(11.5, italic=True))
        hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(hint)
        column.addStretch(3)
        column.addWidget(Tailpiece(p))
        edition = text(page.edition, p["dim"], serif(11))
        edition.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(edition)
        for key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            QShortcut(QKeySequence(key), self, lambda: self.choose(first.key))

    def fade_in(self) -> None:
        """Fade the page in from the paper."""
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self._fade = QPropertyAnimation(effect, b"opacity", self)
        self._fade.setDuration(FADE_MS)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        # Drop the effect once faded in, so the page is drawn directly.
        self._fade.finished.connect(lambda: self.setGraphicsEffect(None))  # type: ignore[arg-type]
        self._fade.start()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        p = self.p
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        frame = QRectF(self.rect()).adjusted(28, 22, -28, -22)
        gilding.gilt_frame(painter, frame, p, gap=6)
        corner_flourishes(painter, frame.adjusted(10, 10, -10, -10), p, 34)
        painter.end()
