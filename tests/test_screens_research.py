"""The terminal laboratory's Research tab: its owner's research under way,
shown while there is any."""

from screen_helpers import _saga_with_bare_laboratory, _select_laboratory, _show_tab
from support import strip_markup, wait_until
from textual.widgets import Static

from ars_magica_manager import storage
from ars_magica_manager.models import Breakthrough, ResearchAttempt
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.widgets import SelectableList


def _saga(started: bool):
    saga = _saga_with_bare_laboratory()
    goal = Breakthrough("Range: Horizon")
    if started:
        goal.log = [
            ResearchAttempt(
                1220,
                "Spring",
                "seek",
                "far glimpse",
                5,
                31,
                1,
                8,
                2,
                move=1,
                discovery=True,
            ),
        ]
        goal.pending_magnitude, goal.discovery_risk = 5, 1
    saga.characters[0].breakthroughs = [goal, Breakthrough("Parma Condensa")]
    return saga


async def test_a_lab_shows_its_owner_s_research_under_way():
    storage.save_saga(_saga(started=True))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        assert "tab-lab-research" in view.tab_ids
        await _show_tab(pilot, app, "tab-lab-research")
        # Only the goal begun: Parma Condensa isn't under way.
        rows = view.query_one("#lab-research-goals-list", SelectableList)
        assert rows.row_count == 1
        log = view.query_one("#lab-research-log-list", SelectableList)
        assert log.select_data_index(0)
        info = view.query_one("#lab-research-info", Static)
        assert await wait_until(
            pilot,
            lambda: (
                "die 8 + risk 1 = 9, moved +1 = 10" in strip_markup(str(info.content))
            ),
        )


async def test_a_lab_with_no_research_under_way_has_no_research_tab():
    storage.save_saga(_saga(started=False))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        assert "tab-lab-research" not in view.tab_ids
