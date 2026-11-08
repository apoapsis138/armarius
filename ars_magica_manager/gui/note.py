"""A short note at the foot of the window that fades by itself: what
another copy of a hosted saga just saved ("Anna changed Leandro;
reloaded."), as the terminal says it in a notification."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget

from .themes import Palette
from .widgets import serif

#: How long a note stays (ms).
NOTE_FOR = 5000


class NoteStrip(QLabel):
    """One line on a paper slip, centred at the foot of `parent`."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setFont(serif(12.5, italic=True))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def say(self, words: str, p: Palette) -> None:
        self.setStyleSheet(
            f"background:{p['panel']}; color:{p['foreground']};"
            f" border:1px solid {p['rule']}; padding:6px 16px;"
        )
        self.setText(words)
        self.adjustSize()
        holder = self.parentWidget()
        if holder is not None:
            self.move(
                (holder.width() - self.width()) // 2,
                holder.height() - self.height() - 24,
            )
        self.show()
        self.raise_()
        self._timer.start(NOTE_FOR)
