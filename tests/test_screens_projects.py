"""The terminal covenant's Projects tab (Hermetic Projects): hidden until a
project is begun with More's Begin Project, after Possessions; gone again
once the last project is deleted."""

from screen_helpers import _fill, _save_dialog, _select_covenant, _wait_for_screen
from support import wait_until
from test_hermetic_projects import tower_saga
from textual.widgets import TabbedContent

from ars_magica_manager import storage
from ars_magica_manager.models import HermeticProject
from ars_magica_manager.models.menagerie import Beast
from ars_magica_manager.sections import PROJECTS_SECTION
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, FieldsDialog, SelectableList


def _tabs(app) -> list[str]:
    view = app.screen._covenant_sheet_view
    return [pane.id for pane in view.query_one(TabbedContent).query("TabPane")]


async def test_begin_project_shows_the_tab_and_deleting_the_last_hides_it():
    saga = tower_saga()
    saga.covenants[0].hermetic_projects = []
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app, "dam")
        assert "tab-cov-projects" not in _tabs(app)
        workspace = app.screen
        workspace.action_begin_project()
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, name="The Spire")
        await _save_dialog(pilot, app)
        assert await wait_until(
            pilot,
            lambda: (
                workspace._covenant_sheet_view is not None
                and "tab-cov-projects" in _tabs(app)
            ),
        )
        tabs = _tabs(app)
        assert tabs.index("tab-cov-projects") == tabs.index("tab-cov-possessions") + 1
        view = workspace._covenant_sheet_view
        await view.build_all_tabs()
        rows = view.query_one("#cov-projects-list", SelectableList)
        rows.select_data_index(0)
        assert await wait_until(pilot, lambda: rows.selected_data_index == 0)
        workspace._core_verb(PROJECTS_SECTION, "remove")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: "tab-cov-projects" not in _tabs(app))
    assert storage.load_saga(saga.id).covenants[0].hermetic_projects == []


async def test_show_project_of_another_kind_shows_its_sections():
    """Showing a Menagerie in place of the tower rebuilds the tab with the
    menagerie, its beasts and its breedings (Hermetic Projects p. 119)."""
    saga = tower_saga()
    saga.covenants[0].hermetic_projects.append(
        HermeticProject(
            id="spur",
            name="The Spur Menagerie",
            kind="Menagerie",
            beasts=[Beast(name="Bock", might=10, sex="male")],
        )
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app, "dam")
        workspace = app.screen
        view = workspace._covenant_sheet_view
        await view.build_all_tabs()
        assert view.query("#cov-tower-works-list")
        rows = view.query_one("#cov-projects-list", SelectableList)
        rows.select_data_index(1)
        assert await wait_until(pilot, lambda: rows.selected_data_index == 1)
        workspace.action_show_project()
        assert await wait_until(
            pilot, lambda: workspace._covenant_sheet_view is not view
        )
        shown = workspace._covenant_sheet_view
        await shown.build_all_tabs()
        assert shown.query("#cov-menagerie-beasts-list")
        assert not shown.query("#cov-tower-works-list")
    assert storage.load_saga(saga.id).covenants[0].project_shown == "spur"
