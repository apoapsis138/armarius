"""The desktop Research chapter: a magus's goals as cards with the road
of their research, the Research Log, and the chosen season's roll on the
chart."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton, QTableView
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.markup_html import plain
from ars_magica_manager.gui.research import ChartStrip, RollCard, StepPath
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Breakthrough, ResearchAttempt


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _research_page():
    saga = _sample_saga_with_covenant()
    goal = Breakthrough("Range: Horizon", points=3, hidden_target=True)
    goal.pending_magnitude, goal.discovery_risk, goal.discovery_shift = 5, 1, 1
    goal.log = [
        ResearchAttempt(
            1221,
            "Winter",
            "stabilize",
            "far glimpse",
            5,
            31,
            1,
            6,
            2,
            move=1,
            result="8: complete failure.",
        ),
    ]
    saga.characters[0].breakthroughs = [goal]
    window = MainWindow(saga_ids=[])
    window.load(saga)
    window.show_character(saga.characters[0].id)
    sheet = window.sheet_area.findChild(CharacterSheet)
    assert sheet is not None
    sheet.open_chapter("Research")
    page = sheet.codex.pages.currentWidget()
    page.window_ = window  # keep the window alive with the page
    return sheet, page


def test_a_goal_shows_as_a_card_with_its_road_and_its_details(app):
    sheet, page = _research_page()
    card = next(c for c in page.findChildren(ClickableCard))
    road = card.findChild(StepPath)
    assert road is not None and road.current == 3  # Stabilize
    card.clicked()
    assert plain(sheet.inspector.title.text()) == "Range: Horizon"
    shown = plain(sheet.inspector.body.text())
    assert "target kept by the storyguide" in shown
    assert "Odds of stabilizing" in shown


def test_choosing_a_season_of_the_log_shows_its_roll_on_the_chart(app):
    sheet, page = _research_page()
    log = page.findChild(QTableView)
    assert log is not None
    log.selectRow(0)
    roll = page.findChild(RollCard)
    assert roll is not None
    assert "Die 6 + risk 1 = 7, moved +1 to 8" in roll.title.text()
    assert roll.findChild(ChartStrip).roll == 8
    assert "Winter 1221" in sheet.inspector.title.text()


def test_a_companion_has_no_research_chapter(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].type = "companion"
    window = MainWindow(saga_ids=[])
    window.load(saga)
    window.show_character(saga.characters[0].id)
    sheet = window.sheet_area.findChild(CharacterSheet)
    assert sheet is not None and "Research" not in sheet.chapters()


def test_a_lab_has_a_research_chapter_while_its_owner_s_research_is_under_way(app):
    from ars_magica_manager.gui.laboratory import LaboratoryPage
    from ars_magica_manager.gui.themes import SCRIPTORUM

    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    owner = saga.character(lab.owner_id)
    assert owner is not None
    begun = Breakthrough("Range: Horizon", insights=1)
    owner.breakthroughs = [begun, Breakthrough("Parma Condensa")]
    page = LaboratoryPage(saga, lab, SCRIPTORUM)
    assert "Research" in page.chapters()
    page.codex.open_chapter("Research")
    chapter = page.codex.pages.currentWidget()
    # Only the goal begun, and no buttons to change it: that's the magus's.
    assert len(chapter.findChildren(StepPath)) == 1
    assert not [b for b in chapter.findChildren(QPushButton) if b.text() == "Add"]
    begun.insights = 0
    assert "Research" not in LaboratoryPage(saga, lab, SCRIPTORUM).chapters()
