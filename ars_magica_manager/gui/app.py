"""Start the desktop version: the Qt application, its fonts and the main
window."""

from __future__ import annotations

import sys


def main() -> int:
    # start-up: the data folder is settled before the app's modules load.
    from .. import crash_log, paths

    # As main.py: the data folder is settled, then kept to.
    renamed = paths.move_old_default_folder()
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
    if problem or renamed:
        window.statusBar().showMessage(problem or renamed or "")
    fit_to_screen(window, 1400, 900)
    window.show()
    return app.exec()
