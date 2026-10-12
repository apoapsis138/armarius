"""Start the desktop version: the Qt application, its fonts and the main
window."""

from __future__ import annotations

import sys


def main() -> int:
    from .. import paths

    # As main.py: the data folder is settled before storage reads it.
    problem = paths.settle_data_dir()
    from PySide6.QtWidgets import QApplication

    from . import pictures
    from .window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Ars Magica Manager")
    app.setWindowIcon(pictures.app_icon())
    pictures.register_fonts()
    window = MainWindow()
    if problem:
        window.statusBar().showMessage(problem)
    window.resize(1400, 900)
    window.show()
    return app.exec()
