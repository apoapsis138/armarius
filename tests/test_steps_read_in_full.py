"""Read in full in the terminal's Add Virtue or Flaw list (ChooseScreen):
F4 opens a long entry's page over the list, and Esc comes back to it with
the search kept; a short entry has nothing to read."""

from __future__ import annotations

from typing import Any

from support import wait_until
from textual.app import App
from textual.widgets import Input

from ars_magica_manager import commands
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.models import Character, Saga
from ars_magica_manager.tui.screens.handout_reading import HandoutReading
from ars_magica_manager.tui.screens.steps import ChooseScreen, run_steps


def _add_virtue() -> commands.Choose:
    magus = Character(id="m", name="Magus", type="magus")
    saga = Saga(id="s", name="Saga", characters=[magus])
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.add is not None
    step = ops.add()
    assert isinstance(step, commands.Choose)
    return step


async def _picker(pilot: Any, app: App[Any], search: str) -> ChooseScreen:
    run_steps(app, _add_virtue(), lambda _end: None)
    assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
    picker = app.screen
    assert isinstance(picker, ChooseScreen)
    await pilot.pause()
    picker.query_one("#picker-search", Input).value = search
    await pilot.pause()
    return picker


async def test_f4_reads_a_long_entry_and_esc_returns_to_the_picker() -> None:
    app: App[Any] = App()
    async with app.run_test(size=(120, 45)) as pilot:
        picker = await _picker(pilot, app, "Elder Runes")
        hint = str(picker.query_one("#picker-details-text").render())

        await pilot.press("f4")
        opened = await wait_until(pilot, lambda: isinstance(app.screen, HandoutReading))
        reading = app.screen
        await pilot.press("escape")
        back = await wait_until(pilot, lambda: app.screen is picker)
        kept = picker.query_one("#picker-search", Input).value

    assert hint.rstrip().endswith("F4: Read in full shows all of it.")
    assert opened and isinstance(reading, HandoutReading)
    assert reading.laid.title == "Verditius Elder Runes"
    assert reading.help_id == virtue_forms.READ_HELP
    assert back and kept == "Elder Runes"


async def test_f4_on_a_short_entry_does_nothing() -> None:
    app: App[Any] = App()
    async with app.run_test(size=(120, 45)) as pilot:
        picker = await _picker(pilot, app, "Ablating")
        hint = str(picker.query_one("#picker-details-text").render())

        await pilot.press("f4")
        await pilot.pause()

        assert app.screen is picker
    assert "F4" not in hint


async def test_moving_the_highlight_never_rebuilds_the_keys(monkeypatch: Any) -> None:
    # F4 is named in the preview, not a Footer (a picker has none), so
    # moving between a short entry and a long one asks for no rebuild.
    app: App[Any] = App()
    async with app.run_test(size=(120, 45)) as pilot:
        picker = await _picker(pilot, app, "")
        choices = picker.choices
        short = next(i for i, c in enumerate(choices) if c.read is None)
        long = next(i for i, c in enumerate(choices) if c.read is not None)
        picker.highlight(f"choice-{short}")
        await pilot.pause()
        await pilot.pause()
        refreshed: list[bool] = []
        monkeypatch.setattr(picker, "refresh_bindings", lambda: refreshed.append(True))

        for entry in (long, short, long):
            picker.highlight(f"choice-{entry}")
            await pilot.pause()
        moved = list(refreshed)

    assert moved == []
