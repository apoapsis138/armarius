"""A shown written Handout's copy on the desktop: drawn on its Stationery
in the same window a storyguide's Preview opens (handout_page), from a
Reading the core laid out through its one tag parser
(handout_layout.reading, handout_markup.blocks).

The pictures are the bytes the copy holds (fetched by the picture request
at a seat); one that isn't there, or isn't a picture, is drawn as a
placeholder.

Pattern: the desktop's half of the Bridge handout_layout describes."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from ..handout_layout import Reading
from .handout_page import HandoutWindow
from .themes import Palette


def pixmaps(pictures: Sequence[bytes | None]) -> list[QPixmap | None]:
    """Each picture's bytes as a pixmap, by number less one (None for one
    not to hand, or not a picture)."""
    found: list[QPixmap | None] = []
    for data in pictures:
        picture = QPixmap()
        drawn = data is not None and picture.loadFromData(data)
        found.append(picture if drawn and not picture.isNull() else None)
    return found


def copy_window(
    reading: Reading, p: Palette, parent: QWidget | None = None
) -> HandoutWindow:
    """The window a shown written Handout's copy opens in: its page on its
    Stationery, on the theme's paper, with Close."""
    window = HandoutWindow(reading.laid, p, pixmaps(reading.pictures), parent)
    window.setObjectName("shown-handout")
    return window
