"""Start the desktop version: the Qt application, its fonts and the main
window."""

from __future__ import annotations

import sys

#: The app's own identity on the Windows taskbar.
APP_USER_MODEL_ID = "Armarius.Desktop"


def claim_taskbar_identity() -> None:
    """Give the process its own AppUserModelID on Windows, so the taskbar
    groups its window as Armarius and shows the app's icon rather than
    Python's. Without one, Windows groups the window with python.exe, and
    whether its icon or the window's shows depends on that machine's
    taskbar settings."""
    if sys.platform != "win32":
        return
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)


def main() -> int:
    from .. import paths

    # As main.py: the data folder is settled before storage reads it.
    renamed = paths.move_old_default_folder()
    problem = paths.settle_data_dir()
    from PySide6.QtWidgets import QApplication

    # Before any window exists: the taskbar reads the id when one opens.
    claim_taskbar_identity()

    from . import pictures
    from .window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Armarius")
    app.setWindowIcon(pictures.app_icon())
    pictures.register_fonts()
    window = MainWindow()
    window.show_title()
    if problem or renamed:
        window.statusBar().showMessage(problem or renamed or "")
    window.resize(1400, 900)
    window.show()
    return app.exec()
