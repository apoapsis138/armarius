"""The bundled fonts in Qt."""

from __future__ import annotations

from PySide6.QtGui import QFontDatabase

from ...style.fonts import FONTS


def register_fonts() -> list[str]:
    """Register the bundled fonts with Qt; the families it couldn't load
    (the app falls back to a system serif for them)."""
    failed = []
    for family, paths in FONTS.items():
        for path in paths:
            if QFontDatabase.addApplicationFont(str(path)) < 0:
                failed.append(family)
    return sorted(set(failed))
