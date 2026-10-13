"""Advance Season on the desktop: the top bar's button plays the season
out with the core's steps (advance_forms) and shows its results on the
Seasons page, which also lists the seasons kept; answered without
showing the dialogs (gui_steps.answering)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtWidgets import QApplication
from support import everything_saga

from ars_magica_manager import economics as eco
from ars_magica_manager import seasons, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import ConfirmDialog
from ars_magica_manager.gui.pages import SagaPage
from ars_magica_manager.gui.seasons import RESULTS, SeasonsPage
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import SeasonPlan, XpAllocation
from ars_magica_manager.rules import activities as rules


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    return MainWindow(saga_ids=[saga.id])


def _planned_saga():
    saga = everything_saga()
    seasons.set_plan(
        saga,
        SeasonPlan(
            "mag1", 1220, "Spring", rules.PRACTICE, [XpAllocation("ability:Latin")]
        ),
    )
    return saga


def test_advancing_plays_the_season_and_shows_its_results(app):
    window = _window(_planned_saga())
    assert not window.advance.isHidden()
    assert "Spring 1220" in window.advance.text()
    asked = answering(window, True)
    window.advance.click()
    assert isinstance(asked[0], ConfirmDialog)
    assert "to Summer 1220?" in asked[0].question
    assert "1 planned season(s) will be applied." in asked[0].question
    saved = storage.load_saga(window.saga.id)
    assert (saved.current_season, saved.current_year) == ("Summer", 1220)
    assert len(saved.season_records) == 1
    page = window.page()
    assert isinstance(page, SeasonsPage)
    assert window.crumb_names()[-1] == "Seasons"
    # The season just played out, not listed again under its own name.
    assert page.chapters() == [RESULTS]
    assert "Summer 1220" in window.advance.text()


def test_cancelling_leaves_the_date_alone(app):
    window = _window(_planned_saga())
    answering(window, False)
    window.advance.click()
    saved = storage.load_saga(window.saga.id)
    assert (saved.current_season, saved.current_year) == ("Spring", 1220)
    assert isinstance(window.page(), SagaPage)


def test_a_quiet_season_just_says_the_new_date(app):
    window = _window(everything_saga())
    answering(window, True)
    window.advance.click()
    assert window.told == [("Advance Season", "It is now Summer 1220.")]
    assert isinstance(window.page(), SagaPage)


def test_the_year_ends_in_deficit_only_if_told_to_advance_anyway(app):
    saga = everything_saga()
    saga.current_season = "Winter"
    covenant = saga.covenants[0]
    covenant.economics.tithes = 0
    covenant.economics.tithes = eco.summarize(saga, covenant).surplus_deficit + 36
    window = _window(saga)
    asked = answering(window, True, False)
    window.advance.click()
    assert "in deficit" in asked[1].question
    assert storage.load_saga(saga.id).current_season == "Winter"
    asked = answering(window, True, True, *([{}] * 2))
    window.advance.click()
    assert asked[1].question.startswith("The year ends with a covenant in deficit")
    saved = storage.load_saga(saga.id)
    assert (saved.current_season, saved.current_year) == ("Spring", 1221)


def test_the_saga_page_opens_the_seasons_kept(app):
    window = _window(_planned_saga())
    answering(window, True)
    window.advance.click()
    window.go(window.trail[:2])
    page = window.page()
    assert isinstance(page, SagaPage)
    page.seasons.clicked()
    page = window.page()
    assert isinstance(page, SeasonsPage)
    assert page.chapters() == ["Spring 1220 (2 people)"]
