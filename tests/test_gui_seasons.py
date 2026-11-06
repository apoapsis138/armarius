"""Advance Season on the desktop: the button under the chapters plays the season
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
from support import everything_saga, quiet

from ars_magica_manager import economics as eco
from ars_magica_manager import seasons, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import ConfirmDialog
from ars_magica_manager.gui.pages import SagaPage
from ars_magica_manager.gui.seasons import AHEAD, NEEDS_YOU, RESULTS, SeasonsPage
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
    assert window.season_panel is not None
    assert window.season_panel.date.text() == "Spring 1220"
    asked = answering(window, True)
    window.season_panel.click()
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
    assert page.chapters() == [RESULTS, AHEAD, NEEDS_YOU]
    assert window.season_panel is not None
    assert window.season_panel.date.text() == "Summer 1220"


def test_cancelling_leaves_the_date_alone(app):
    window = _window(_planned_saga())
    answering(window, False)
    window.season_panel.click()
    saved = storage.load_saga(window.saga.id)
    assert (saved.current_season, saved.current_year) == ("Spring", 1220)
    assert isinstance(window.page(), SagaPage)


def test_a_quiet_season_just_says_the_new_date(app):
    window = _window(quiet(everything_saga()))
    answering(window, True)
    window.season_panel.click()
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
    window.season_panel.click()
    assert "in deficit" in asked[1].question
    assert storage.load_saga(saga.id).current_season == "Winter"
    asked = answering(window, True, True, *([{}] * 2))
    window.season_panel.click()
    assert asked[1].question.startswith("The year ends with a covenant in deficit")
    saved = storage.load_saga(saga.id)
    assert (saved.current_season, saved.current_year) == ("Spring", 1221)


def test_the_saga_page_opens_the_seasons_kept(app):
    window = _window(_planned_saga())
    answering(window, True)
    window.season_panel.click()
    window.go(window.trail[:2])
    page = window.page()
    assert isinstance(page, SagaPage)
    page.seasons.clicked()
    page = window.page()
    assert isinstance(page, SeasonsPage)
    assert page.chapters() == [AHEAD, NEEDS_YOU, "Spring 1220 (2 people)"]


def test_advance_season_is_under_the_chapters_but_not_on_a_worksheet(app):
    from ars_magica_manager import creation

    saga = everything_saga()
    window = _window(saga)
    page = window.page()
    panel = window.season_panel
    assert panel is not None
    assert panel.parent() is page.codex.side
    window.open_covenant(saga.covenants[0].id)
    assert window.season_panel is not None
    character = creation.add_character(
        window.saga, "Brother Anselm", "companion", saga.covenants[0].id
    )
    window.open_worksheet(character.id)
    # A record is finished or left before the season ends.
    assert window.season_panel is None
    window.close()
