"""More's Disputatio on a character's sheet: the form, the exchanges shown,
and Keep writing both Diaries."""

from screen_helpers import (
    _confirm,
    _sample_saga_with_covenant,
    _select_character,
    _wait_for_screen,
)
from support import wait_until

from ars_magica_manager import storage
from ars_magica_manager.models import Character
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, FieldsDialog


async def test_more_s_disputatio_is_rolled_and_kept_in_both_diaries():
    saga = _sample_saga_with_covenant()
    saga.characters.append(Character(id="hugh", name="Hugh", type="companion"))
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_character(pilot, app)
        app.screen._run_more("disputatio")  # type: ignore[attr-defined]
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert "Hugh" in str(app.screen.query_one("#fields-live").render())
        await pilot.click("#btn-save")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await _confirm(pilot, app, "y")

    saved = storage.load_saga("test_saga")
    first, hugh = saved.characters[0], saved.character("hugh")
    assert hugh is not None
    assert first.diary[-1].name.startswith("Disputatio in ")
    assert hugh.diary[-1].name.endswith(f"with {first.name}")
