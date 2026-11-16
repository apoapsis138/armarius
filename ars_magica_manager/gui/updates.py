"""The App update notice on the desktop: the title page's line, the gear's
badge and the Update row at the top of the Settings window.

All three listen to one UpdateNotices (an Observer, through Qt's signals):
it holds the notice the core describes (updates.Notice), runs the check
in a thread of its own so the window never waits for GitHub, and tells
each listener when the notice changes. The core decides what to say;
this module only draws it. Release notes are untrusted text, so every
label here shows plain text only.
"""

from __future__ import annotations

import math
import threading
from collections.abc import Callable

from PySide6.QtCore import QObject, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QIcon,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__, updates
from . import motion, pictures
from .style.gilding import worked
from .style.paper import shade
from .style.pieces import heading as heading_font
from .style.pieces import serif
from .themes import Palette

#: How long the title page's line glows when it first appears (ms).
GLOW_MS = 1400


def plain_label(words: str, colour: str, font: QFont, *, wrap: bool = False) -> QLabel:
    """A label that shows `words` as plain text, whatever they hold (Qt
    would otherwise draw text that looks like HTML as HTML)."""
    label = QLabel()
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setText(words)
    label.setStyleSheet(f"color:{colour}; background:transparent")
    label.setFont(font)
    label.setWordWrap(wrap)
    return label


def notice_colour(notice: updates.Notice, p: Palette) -> str:
    """The theme's warning colour for a security App update or a Version
    mismatch, else its accent."""
    return p["text-warning"] if notice.kind != updates.UPDATE else p["accent"]


# -- the seal --


def paint_seal(painter: QPainter, centre: QPointF, radius: float, p: Palette) -> None:
    """A small gilded seal with "!" on it: a disc in the theme's metal,
    ringed in the accent, the mark in the page's ink."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    box = QRectF(centre.x() - radius, centre.y() - radius, 2 * radius, 2 * radius)
    painter.setPen(QPen(shade(p["accent"], 230), max(0.8, radius / 7)))
    painter.setBrush(worked(box, p))
    painter.drawEllipse(box)
    mark = QFont(pictures.SERIF)
    mark.setBold(True)
    mark.setPixelSize(max(6, round(radius * 1.45)))
    painter.setFont(mark)
    painter.setPen(QColor(p["foreground"]))
    painter.drawText(box, Qt.AlignmentFlag.AlignCenter, "!")
    painter.restore()


def badged_gear_icon(
    colour: str, p: Palette, size: int = 20, ratio: float = 2.0
) -> QIcon:
    """The settings gear with a small "!" seal at its top right: an App
    update notice waits."""
    gear = pictures.gear_icon(colour, size, ratio).pixmap(QSize(size, size))
    side = round(size * ratio)
    picture = QPixmap(side, side)
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.drawPixmap(0, 0, side, side, gear)
    radius = side * 0.24
    paint_seal(painter, QPointF(side - radius - 0.5, radius + 0.5), radius, p)
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return QIcon(picture)


# -- the notice, for every listener --


class UpdateNotices(QObject):
    """The notice the window shows (an App update, or a Version mismatch
    with the host of a Joined game), and the check that finds it.
    `changed` carries the notice now (None for none) to every listener;
    `checked` carries what Check now found, in words."""

    changed = Signal(object)
    checked = Signal(str)
    #: From the check's own thread to this object's (queued by Qt).
    _arrived = Signal(object, bool)

    def __init__(
        self,
        copy: updates.Copy,
        fetch: updates.Fetch | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.copy = copy
        self.fetch = fetch
        self._update = updates.notice(copy)
        self._mismatch: updates.Notice | None = None
        self._arrived.connect(self._done)
        #: The check's thread, while one runs.
        self.thread: threading.Thread | None = None

    @property
    def notice(self) -> updates.Notice | None:
        """The notice to show: a Joined game's Version mismatch first."""
        return self._mismatch or self._update

    @property
    def update_notice(self) -> updates.Notice | None:
        """The App update notice alone (Settings' Update row)."""
        return self._update

    def refresh(self) -> None:
        """Read the notice again from what the last check found."""
        self._update = updates.notice(self.copy)
        self.changed.emit(self.notice)

    def set_mismatch(self, found: updates.Mismatch | None) -> None:
        """A Joined game's minor Version mismatch with its host (None when
        it matches, or on leaving it)."""
        minor = found if found is not None and not found.major else None
        self._mismatch = (
            updates.mismatch_notice(minor, self.copy) if minor is not None else None
        )
        self.changed.emit(self.notice)

    def check_at_start(self) -> None:
        """The check at start-up, if it is due: silent if it fails."""
        self._start(now_asked=False)

    def check_now(self) -> None:
        """Check now: whatever the day's limit, saying what it found."""
        self._start(now_asked=True)

    def _start(self, *, now_asked: bool) -> None:
        if self.thread is not None and self.thread.is_alive():
            return
        if not self.copy.checks:
            if now_asked:
                self.checked.emit(updates.outcome_text(updates.Result(False)))
            return

        def run() -> None:
            result = updates.check(self.copy, now_asked=now_asked, fetch=self.fetch)
            self._arrived.emit(result, now_asked)

        self.thread = threading.Thread(target=run, name="update-check", daemon=True)
        self.thread.start()

    def _done(self, result: updates.Result, now_asked: bool) -> None:
        if now_asked:
            self.checked.emit(updates.outcome_text(result))
        if result.ran and not result.problem:
            self.refresh()

    def skip(self) -> None:
        """Skip this App update's version (not a security one)."""
        shown = self._update
        if shown is not None and shown.can_skip:
            updates.skip(shown.version)
            self.refresh()

    def set_check_at_start(self, on: bool) -> None:
        updates.set_check_at_start(on)
        self.refresh()


# -- the title page's line --


class UpdateLine(QWidget):
    """The title page's "! Armarius X.Y.Z is available", beside the version
    line: the seal, then the words in the theme's accent (its warning
    colour for security fixes or a Version mismatch), the version line's
    type a little heavier. It glows softly once when it first appears, with
    motion on. A click calls `open`."""

    def __init__(self, p: Palette, open: Callable[[], None], size: float = 11) -> None:
        super().__init__()
        self.p = p
        self.open = open
        self.font_ = serif(size, bold=True)
        self.words = ""
        self.colour = p["accent"]
        self.glow = 0.0
        self._glowed = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName("App update")
        self.hide()

    def show_notice(self, notice: updates.Notice | None) -> None:
        if notice is None or not notice.shown:
            self.words = ""
            self.hide()
            return
        self.words = notice.headline
        self.colour = notice_colour(notice, self.p)
        self.setToolTip("Open Settings at its Update row")
        self.updateGeometry()
        self.show()
        self.update()
        if not self._glowed:
            self._glowed = True
            motion.tween(self, self._glow, GLOW_MS, name="glow")

    def _glow(self, value: float) -> None:
        # Up and back down once: brightest halfway.
        self.glow = math.sin(math.pi * value)
        self.update()

    def sizeHint(self) -> QSize:
        metrics = QFontMetricsF(self.font_)
        height = metrics.height()
        return QSize(
            round(height * 1.4 + metrics.horizontalAdvance(self.words)) + 8,
            round(height) + 6,
        )

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.open()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        metrics = QFontMetricsF(self.font_)
        height = metrics.height()
        radius = height * 0.42
        centre = QPointF(radius + 3, self.height() / 2)
        if self.glow > 0:
            halo = QRadialGradient(centre, radius * 3)
            light = QColor(self.colour)
            light.setAlpha(round(110 * self.glow))
            halo.setColorAt(0, light)
            light.setAlpha(0)
            halo.setColorAt(1, light)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(halo)
            painter.drawEllipse(centre, radius * 3, radius * 3)
        paint_seal(painter, centre, radius, self.p)
        painter.setFont(self.font_)
        painter.setPen(QColor(self.colour))
        painter.drawText(
            QRectF(centre.x() + radius + 6, 0, self.width(), self.height()),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.words,
        )
        painter.end()


# -- Settings' Update row --


class UpdateRow(QWidget):
    """The Update row at the top of the Settings window: the notice's
    version and date, the first lines of its notes, What's new, the
    Download page (or how a checkout updates) and Skip this version; then
    the setting to check at start-up and Check now. A skipped version shows
    faintly. `whats_new` shows a notice's whole notes; `download` opens its
    page."""

    def __init__(
        self,
        p: Palette,
        notices: UpdateNotices,
        whats_new: Callable[[updates.Notice], None],
        download: Callable[[str], None],
    ) -> None:
        super().__init__()
        self.p = p
        self.notices = notices
        self.whats_new_ = whats_new
        self.download_ = download
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(4)
        column.addWidget(plain_label("Update", p["heading"], heading_font(14, p)))
        self.headline = plain_label(
            "", p["foreground"], serif(12.5, bold=True), wrap=True
        )
        self.lines = plain_label("", p["label"], serif(12, italic=True), wrap=True)
        self.extra = plain_label("", p["label"], serif(12, italic=True), wrap=True)
        for label in (self.headline, self.lines, self.extra):
            column.addWidget(label)
        row = QHBoxLayout()
        self.whats_new = QPushButton("What's new")
        self.whats_new.clicked.connect(self._whats_new)
        self.download = QPushButton("Download page")
        self.download.clicked.connect(self._download)
        self.skip = QPushButton("Skip this version")
        self.skip.clicked.connect(notices.skip)
        for button in (self.whats_new, self.download, self.skip):
            row.addWidget(button)
        row.addStretch(1)
        column.addLayout(row)
        self.check = QCheckBox("Check for updates when Armarius starts")
        self.check.setChecked(updates.check_at_start())
        self.check.toggled.connect(notices.set_check_at_start)
        column.addWidget(self.check)
        column.addWidget(
            plain_label(
                "It asks GitHub for the latest Release, sending only this app's version.",
                p["dim"],
                serif(11.5, italic=True),
                wrap=True,
            )
        )
        checking = QHBoxLayout()
        self.check_now = QPushButton("Check now")
        self.check_now.clicked.connect(self._check_now)
        checking.addWidget(self.check_now)
        self.outcome = plain_label("", p["label"], serif(12, italic=True), wrap=True)
        checking.addWidget(self.outcome, 1)
        column.addLayout(checking)
        if not notices.copy.checks:
            for widget in (self.check, self.check_now):
                widget.setEnabled(False)
            self.outcome.setText(updates.outcome_text(updates.Result(False)))
        notices.changed.connect(self._show)
        notices.checked.connect(self._checked)
        self._show(notices.notice)

    def _show(self, _notice: object = None) -> None:
        notice = self.notices.notice
        p = self.p
        if notice is None:
            self.headline.setText(f"Armarius {__version__} is the version you have.")
            self.headline.setStyleSheet(
                f"color:{p['foreground']}; background:transparent"
            )
            for widget in (
                self.lines,
                self.extra,
                self.whats_new,
                self.download,
                self.skip,
            ):
                widget.hide()
            return
        faint = notice.skipped
        colour = p["dim"] if faint else notice_colour(notice, p)
        dated = f" ({notice.date})" if notice.date else ""
        skipped = ", skipped" if faint else ""
        self.headline.setText(f"! {notice.headline}{dated}{skipped}")
        self.headline.setStyleSheet(f"color:{colour}; background:transparent")
        self.lines.setText("\n".join(notice.lines))
        self.lines.setVisible(bool(notice.lines))
        extra = [line for line in (notice.remote,) if line]
        if not notice.download and notice.how_to_update:
            extra.append(notice.how_to_update)
        self.extra.setText("\n".join(extra))
        self.extra.setVisible(bool(extra))
        self.whats_new.setVisible(bool(notice.notes))
        self.download.setText(notice.download or "Download page")
        self.download.setVisible(bool(notice.download))
        self.skip.setVisible(notice.can_skip and not notice.skipped)

    def _whats_new(self) -> None:
        notice = self.notices.notice
        if notice is not None:
            self.whats_new_(notice)

    def _download(self) -> None:
        notice = self.notices.notice
        if notice is not None:
            self.download_(notice.url)

    def _check_now(self) -> None:
        self.outcome.setText("Checking…")
        self.notices.check_now()

    def _checked(self, words: str) -> None:
        self.outcome.setText(words)
