"""The terminal's Religion tab (The Church pp. 33-38, 46-48): Faith first,
then a Christian's Petitions, where Add makes his first petition."""

from screen_helpers import (
    _sample_saga_with_covenant,
    _select_character,
    _show_tab,
    _wait_for_screen,
)
from support import build_all_tabs, wait_until
from textual.widgets import Input, Select

from ars_magica_manager import storage
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import FieldsDialog
from ars_magica_manager.tui.screens.widgets import SelectableList, SheetSection


async def test_a_first_petition_is_added_on_the_religion_tab():
    storage.save_saga(_sample_saga_with_covenant())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view  # type: ignore[attr-defined]
        assert "tab-religion" in view.tab_ids
        await build_all_tabs(pilot, view)
        await _show_tab(pilot, app, "tab-religion")
        view.query_one("#section-char-petitions", SheetSection).focus_section()
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        dialog = app.screen
        dialog.query_one("#fld-ask", Input).value = "A marriage blessing"
        dialog.query_one("#fld-example", Select).value = "A marriage blessing"
        await pilot.pause()
        dialog.query_one("#btn-save").press()

        def listed() -> bool:
            rows = view.query_one("#char-petitions-list", SelectableList)
            return bool(rows._rows) and "A marriage blessing" in rows._rows[0][1]

        assert await wait_until(pilot, listed)
    saved = storage.load_saga("test_saga").characters[0].church.petitions
    assert [p.ask for p in saved] == ["A marriage blessing"]
