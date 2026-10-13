"""The desktop draws the core's tables (tables.py) as real tables: markup
cells in their colours, headings across the row that can't be chosen, and
choosing a row hands over its key."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QHeaderView, QTableView
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.themes import PALETTES
from ars_magica_manager.gui.widgets import table_view
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import DiaryEntry, Possession
from ars_magica_manager.tables import Table

P = PALETTES[0]


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def test_a_heading_spans_its_row_and_cant_be_chosen(app):
    chosen: list[int] = []
    table = Table(
        ["Name", "Points"],
        [["Boons", ""], ["[$text-error]Ruin[/]", "3"]],
        [None, 5],
        markup=True,
    )
    view = table_view(table, P, chosen.append)
    model = view.model()
    assert view.columnSpan(0, 0) == 2
    assert not model.flags(model.index(0, 0)) & Qt.ItemFlag.ItemIsSelectable
    cell = model.index(1, 0)
    assert cell.data() == "Ruin"
    assert cell.data(Qt.ItemDataRole.ForegroundRole).color() == QColor(P["text-error"])
    assert model.index(1, 1).data(Qt.ItemDataRole.TextAlignmentRole) == (
        Qt.AlignmentFlag.AlignCenter
    )
    view.selectRow(1)
    assert chosen == [5]


def test_the_stretch_column_takes_the_room(app):
    view = table_view(
        Table(["Year", "Entry"], [["1220", "A walk"]], stretch=1), P, lambda _: None
    )
    header = view.horizontalHeader()
    assert header.sectionResizeMode(1) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(0) == QHeaderView.ResizeMode.ResizeToContents


def test_the_sheet_draws_its_lists_as_tables(app):
    saga = _sample_saga_with_covenant()
    magus = saga.character("char1")
    assert magus is not None
    magus.inventory = [Possession("w1", "weapon", "Sword", gear_type="Long Sword")]
    magus.diary = [DiaryEntry(1220, "Spring", "A walk")]
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show_character(magus.id)
    page = window.page()
    assert isinstance(page, CharacterSheet)
    for chapter, first in (("Inventory", "Sword"), ("Diary", "1220")):
        page.open_chapter(chapter)
        page = window.page()
        assert isinstance(page, CharacterSheet)
        cells = [
            view.model().index(0, 0).data()
            for view in page.findChildren(QTableView)
            if view.model().rowCount()
        ]
        assert first in cells
