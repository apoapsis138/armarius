"""The app's icon: the title page's illuminated A, drawn in code, and the
identity that makes Windows show it rather than Python's."""

from __future__ import annotations

import sys

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap

from .style.illumination import paint_initial
from .themes import SCRIPTORUM

#: The app's own identity on the Windows taskbar.
APP_USER_MODEL_ID = "Armarius.Desktop"
INITIAL = "A"
SIZES = (16, 24, 32, 48, 64, 128, 256)


def icon_pixmap(size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    paint_initial(painter, QRectF(0, 0, size, size), INITIAL, SCRIPTORUM)
    painter.end()
    return pixmap


def app_icon() -> QIcon:
    icon = QIcon()
    for size in SIZES:
        icon.addPixmap(icon_pixmap(size))
    return icon


def claim_taskbar_identity() -> None:
    """Give the process its own AppUserModelID on Windows, so the taskbar
    groups its window as Armarius and shows the app's icon rather than
    Python's. Without one, Windows groups the window with python.exe, and
    whether its icon or the window's shows depends on that machine's
    taskbar settings. Called before any window exists: the taskbar reads
    the id when one opens."""
    if sys.platform != "win32":
        return
    import ctypes  # Windows only.

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
