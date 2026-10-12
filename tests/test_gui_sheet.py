"""The desktop version's Character sheet builds, offscreen, from a sample
saga, and shows the same core text as the terminal sheet."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QTabWidget
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import character_sheet as cs
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.markup_html import plain, to_html
from ars_magica_manager.gui.themes import PALETTES, SCRIPTORUM
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _texts(widget) -> str:
    return "\n".join(plain(label.text()) for label in widget.findChildren(QLabel))


def test_the_window_shows_the_first_characters_sheet_with_every_tab(app):
    saga = _sample_saga_with_covenant()
    window = MainWindow(saga_ids=[])
    window.load(saga)
    tabs = window.sheet_area.findChild(QTabWidget)
    assert tabs is not None
    assert [tabs.tabText(i) for i in range(tabs.count())] == [
        "Description",
        "Abilities",
        "Virtues && Flaws",
        "Hermetic Magic",
        "Inventory",
        "Planning",
        "Diary",
    ]
    shown = _texts(window.sheet_area)
    assert "Test Covenant" in shown
    assert "Creo" in shown and "Vim" in shown


def test_the_theme_toggle_redraws_the_sheet_in_the_other_palette(app):
    window = MainWindow(saga_ids=[])
    window.load(_sample_saga_with_covenant())
    chosen = window.character_id
    window.toggle_theme()
    assert window.palette_ is PALETTES[1]
    assert window.character_id == chosen


def test_markup_becomes_spans_in_the_palettes_colours():
    html = to_html("[b]Name:[/] [$label]x \\[y][/]", SCRIPTORUM)
    assert html == (
        '<span style="font-weight:600">Name:</span> '
        f'<span style="color:{SCRIPTORUM["label"]}">x [y]</span>'
    )
    assert plain("[i $label]1220[/]") == "1220"


def test_an_art_row_carries_its_score_and_experience():
    character = _sample_saga_with_covenant().characters[0]
    row = cs.art_row(character, "Creo")
    assert (row.abbreviation, row.score, row.xp) == ("Cr", "10", 55)
