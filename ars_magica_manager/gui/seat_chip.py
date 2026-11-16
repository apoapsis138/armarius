"""The title bar's Playing and seat buttons: one control in two parts.

While the reader plays a character, the button splits. Its name part runs
one command (open My sheet) and a ▾ beside it another (a menu of their
characters and the button's own choices); otherwise it is one button with
one command, as it always was.

Pattern: Composite. The window treats the chip as a single control (its
words, tooltip, icon, shown or hidden), while each of its two parts runs
its own command.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ..markup import fit

#: How many characters of a name the chip shows; the tooltip has it whole.
NAME_WIDTH = 16


def cut(name: str, width: int = NAME_WIDTH) -> str:
    """`name` cut to `width` characters with an ellipsis if it is longer."""
    return fit(name, width).rstrip()


class SeatChip(QWidget):
    """A flat button (`part`) and, while split, a ▾ (`arrow`) beside it.
    `whole` runs when the chip isn't split; split, the part runs `main`
    and the arrow `menu`."""

    def __init__(self, name: str, whole: Callable[[], object]) -> None:
        super().__init__()
        self._whole = whole
        self._main: Callable[[], object] | None = None
        self._menu: Callable[[], object] | None = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.part = QPushButton()
        self.part.setFlat(True)
        self.part.setAccessibleName(name)
        self.part.clicked.connect(self._part_clicked)
        layout.addWidget(self.part)
        self.arrow = QPushButton("▾")
        self.arrow.setFlat(True)
        self.arrow.setObjectName("chip-arrow")
        self.arrow.setAccessibleName(f"{name} menu")
        self.arrow.clicked.connect(self._arrow_clicked)
        self.arrow.hide()
        layout.addWidget(self.arrow)

    # -- one control --

    def split(
        self, main: Callable[[], object] | None, menu: Callable[[], object] | None
    ) -> None:
        """Split the chip (the part runs `main`, the ▾ `menu`), or with
        None join it again (the part runs `whole`)."""
        self._main, self._menu = main, menu
        self.arrow.setVisible(main is not None and menu is not None)

    def is_split(self) -> bool:
        return self._main is not None and self._menu is not None

    def setText(self, text: str) -> None:
        self.part.setText(text)

    def text(self) -> str:
        return self.part.text()

    def setToolTip(self, tip: str) -> None:
        self.part.setToolTip(tip)

    def toolTip(self) -> str:
        return self.part.toolTip()

    def set_arrow_tip(self, tip: str) -> None:
        self.arrow.setToolTip(tip)

    def setIcon(self, icon: QIcon) -> None:
        self.part.setIcon(icon)

    def setCheckable(self, on: bool) -> None:
        self.part.setCheckable(on)

    def setChecked(self, on: bool) -> None:
        self.part.setChecked(on)

    def isChecked(self) -> bool:
        return self.part.isChecked()

    def under(self) -> QPoint:
        """Where a menu dropped from the chip opens: under its left edge."""
        return self.mapToGlobal(self.rect().bottomLeft())

    # -- each part's own command --

    def _part_clicked(self) -> None:
        if self._main is not None and self._menu is not None:
            self._main()
        else:
            self._whole()

    def _arrow_clicked(self) -> None:
        if self._menu is not None:
            self._menu()
