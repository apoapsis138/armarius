"""The terminal's Church tab (The Church pp. 33-38, 46-48): a character's
first petition, made from More, brings the tab, which then lists it."""

from screen_helpers import (
    _sample_saga_with_covenant,
    _select_character,
    _wait_for_screen,
)
from support import build_all_tabs, wait_until
from textual.widgets import Input, Select

from ars_magica_manager import storage
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import FieldsDialog
from ars_magica_manager.tui.screens.widgets import SelectableList


async def test_a_first_petition_brings_the_church_tab():
    storage.save_saga(_sample_saga_with_covenant())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_character(pilot, app)
        workspace = app.screen
        view = workspace._character_sheet_view  # type: ignore[attr-defined]
        assert "tab-church" not in view.tab_ids
        workspace.action_petition_church()  # type: ignore[attr-defined]
        await _wait_for_screen(pilot, app, FieldsDialog)
        dialog = app.screen
        dialog.query_one("#fld-ask", Input).value = "A marriage blessing"
        dialog.query_one("#fld-example", Select).value = "A marriage blessing"
        await pilot.pause()
        dialog.query_one("#btn-save").press()

        def shown_again() -> bool:
            now = workspace._character_sheet_view  # type: ignore[attr-defined]
            return now is not view and now is not None and "tab-church" in now.tab_ids

        assert await wait_until(pilot, shown_again)
        view = workspace._character_sheet_view  # type: ignore[attr-defined]
        await build_all_tabs(pilot, view)
        rows = view.query_one("#char-petitions-list", SelectableList)
        assert "A marriage blessing" in rows._rows[0][1]
    saved = storage.load_saga("test_saga").characters[0].church.petitions
    assert [p.ask for p in saved] == ["A marriage blessing"]
