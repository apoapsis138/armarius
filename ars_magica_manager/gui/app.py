"""Start the desktop version: the Qt application, its fonts and the main
window."""

from __future__ import annotations

import os
import sys
from collections.abc import MutableMapping

#: Qt's variable naming the display system it draws on.
QT_PLATFORM = "QT_QPA_PLATFORM"
#: X11 first, through GNOME's XWayland, with Wayland if X11 won't load.
X11_FIRST = "xcb;wayland"


def choose_display(env: MutableMapping[str, str], platform: str = sys.platform) -> None:
    """Draw on X11 under GNOME on Linux. On Wayland, Qt asks GNOME for an
    activation token whenever focus moves between its windows, without the
    click that caused it; GNOME refuses the token but shows its busy cursor
    for it until a 15-second timeout. X11 windows ask for no tokens. A
    display the user chose (QT_QPA_PLATFORM) is kept, and so is Wayland
    when there is no X11 server to fall back to."""
    if platform != "linux" or env.get(QT_PLATFORM):
        return
    desktops = env.get("XDG_CURRENT_DESKTOP", "").lower().split(":")
    if "gnome" in desktops and env.get("WAYLAND_DISPLAY") and env.get("DISPLAY"):
        env[QT_PLATFORM] = X11_FIRST


def main() -> int:
    # Before Qt starts: it reads the display to draw on once.
    choose_display(os.environ)
    # start-up: the data folder is settled before the app's modules load.
    from .. import crash_log, paths

    # As main.py: the data folder is settled, then kept to.
    paths.keep_old_default_folder()
    problem = paths.settle_data_dir()
    paths.use_data_dir(paths.data_dir())
    crash_log.start()
    from PySide6.QtWidgets import QApplication

    # start-up: the icon is drawn with Qt, once it is loaded.
    from .icon import app_icon, claim_taskbar_identity

    # Before any window exists: the taskbar reads the id when one opens.
    claim_taskbar_identity()

    # start-up: the window and its pictures load once Qt is up.
    from . import pictures
    from .style.frame import fit_to_screen
    from .window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Armarius")
    app.setWindowIcon(app_icon())
    pictures.register_fonts()
    window = MainWindow()
    window.show_title()
    if problem:
        window.statusBar().showMessage(problem)
    fit_to_screen(window, 1400, 900)
    window.show()
    return app.exec()
