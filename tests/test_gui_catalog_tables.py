"""The desktop draws a catalog entry's table on its reading page as a
ruled table: a header row, then a row for each of the table's rows."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

from ars_magica_manager import entry_reading
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.handout_page import HandoutPage

RUNES = "| Meaning | Tree | Art |\n|---|---|---|\n| Health | Birch | Creo |"


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


@pytest.mark.usefixtures("app")
def test_the_reading_page_draws_a_table_as_a_ruled_table() -> None:
    reading = entry_reading.reading("Elder Runes", "Minor Virtue", "", "", RUNES, "")

    page = HandoutPage(reading.laid)

    [table] = page.findChildren(QLabel, "handout-table")
    html = table.text()
    assert html.count("<tr") == 2 and "<th" in html
    assert "Birch" in html and "Meaning" in html
