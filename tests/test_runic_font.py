"""The desktop draws runes in every catalog entry (Verditius Elder Runes'
table) from its own bundled Noto Sans Runic, not whatever the computer has:
every serif the desktop sets text in falls back to it."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QApplication

from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.style.pieces import serif
from ars_magica_manager.style import fonts

#: The Elder Runes table's runes.
RUNES = "ᛒᛇᚲᛁᚠᛚᚼᛄᚺᛋᛏᚹᛗᛃᚦ"


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


@pytest.mark.usefixtures("app")
def test_the_bundled_runic_font_has_every_rune() -> None:
    metrics = QFontMetrics(QFont(fonts.RUNIC))

    assert [r for r in RUNES if not metrics.inFontUcs4(ord(r))] == []


@pytest.mark.usefixtures("app")
def test_the_desktops_serif_falls_back_to_the_runic_font() -> None:
    assert serif(12).families()[:2] == [fonts.SERIF, fonts.RUNIC]
