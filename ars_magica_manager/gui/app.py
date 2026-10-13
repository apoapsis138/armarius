"""Start the desktop version: the Qt application, its fonts and the main
window."""

from __future__ import annotations

import sys


def main() -> int:
    from .. import paths

    # As main.py: the data folder is settled before storage reads it.
    renamed = paths.move_old_default_folder()
    problem = paths.settle_data_dir()
    from PySide6.QtWidgets import QApplication

    from . import pictures
    from .window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Armarius")
    app.setWindowIcon(pictures.app_icon())
    pictures.register_fonts()
    window = MainWindow()
    if problem or renamed:
        window.statusBar().showMessage(problem or renamed or "")
    window.resize(1400, 900)
    window.show()
    return app.exec()
