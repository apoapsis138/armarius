"""The terminal's Read in full on long Abilities and Boons and Hooks: the
details panel ends a long one's summary with the Read in full link, More's
Read in full (m, f) opens it full screen, and F4 reads it in the Add Boon
list."""

from __future__ import annotations

from typing import Any

from screen_helpers import (
    _open_cov_section,
    _open_section,
    _saga_with_bare_character,
    _saga_with_empty_covenant,
    _select_bh_row,
    _select_character,
    _select_covenant,
)
from support import wait_until
from textual.app import App
from textual.widgets import Input, OptionList, Static

from ars_magica_manager import catalog, storage
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.models import Ability, Saga, VirtueFlawInstance
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.handout_reading import HandoutReading
from ars_magica_manager.tui.screens.prompts import MenuScreen
from ars_magica_manager.tui.screens.steps import ChooseScreen, run_steps
from ars_magica_manager.tui.screens.workspace.screen import WorkspaceScreen


def _words(widget: Static) -> str:
    drawn = widget.render()
    return getattr(drawn, "plain", str(drawn))


async def _read_by_more(pilot: Any, app: Any) -> HandoutReading | None:
    await pilot.press("m")
    if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
        await pilot.press("f")
    if not await wait_until(pilot, lambda: isinstance(app.screen, HandoutReading)):
        return None
    reading = app.screen
    assert isinstance(reading, HandoutReading)
    await pilot.press("escape")
    await wait_until(pilot, lambda: not isinstance(app.screen, HandoutReading))
    return reading


async def test_more_reads_a_long_ability_in_full() -> None:
    saga = _saga_with_bare_character()
    hex_ = catalog.load_ability_catalog_by_id()["ab_hex"]
    saga.characters[0].abilities = [
        Ability(name="Athletics", category="General", xp=5),
        Ability(name=hex_.name, category=hex_.category, xp=5),
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")
        workspace = app.screen
        assert isinstance(workspace, WorkspaceScreen)
        abilities = workspace.query_one("#abilities-list", OptionList)
        abilities.focus()
        await pilot.pause()
        abilities.highlighted = next(
            i
            for i in range(abilities.option_count)
            if "Hex" in str(abilities.get_option_at_index(i).prompt)
        )
        await pilot.pause()
        details = _words(workspace.query_one("#ability-info", Static))
        reading = await _read_by_more(pilot, app)

    assert "Read in full" in details and "m, More" in details
    assert hex_.summary.split()[0] in details
    assert reading is not None and reading.laid.title == "Hex"


def _saga_with_boons() -> Saga:
    saga = _saga_with_empty_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_chase"),
    ]
    return saga


async def test_more_reads_a_long_boon_in_full() -> None:
    storage.save_saga(_saga_with_boons())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await _select_bh_row(pilot, app, "Boon", 1)
        workspace = app.screen
        assert isinstance(workspace, WorkspaceScreen)
        details = _words(workspace.query_one("#cov-bh-info", Static))
        reading = await _read_by_more(pilot, app)
        # The panel's link runs the same action.
        workspace.action_read_entry_in_full()
        linked = await wait_until(pilot, lambda: isinstance(app.screen, HandoutReading))
        await pilot.pause()

    assert "Read in full" in details and "A tamed royal" in details
    assert reading is not None and reading.laid.title == "Chase"
    assert linked


async def test_f4_reads_a_long_boon_in_the_add_boon_list() -> None:
    saga = _saga_with_boons()
    covenant = saga.covenants[0]
    app: App[Any] = App()
    async with app.run_test(size=(120, 45)) as pilot:
        run_steps(app, covenant_forms.add_boon_hook(saga, covenant, "Boon"), print)
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        picker = app.screen
        assert isinstance(picker, ChooseScreen)
        await pilot.pause()
        [chase] = [
            i
            for i, c in enumerate(picker.choices)
            if c.value.id == "covbh_boon_minor_chase"
        ]
        picker.highlight(f"choice-{chase}")
        await pilot.pause()
        hint = str(picker.query_one("#picker-details-text").render())
        await pilot.press("f4")
        opened = await wait_until(pilot, lambda: isinstance(app.screen, HandoutReading))
        reading = app.screen
        await pilot.press("escape")
        back = await wait_until(pilot, lambda: app.screen is picker)
        search = picker.query_one("#picker-search", Input).value

    assert hint.rstrip().endswith("F4: Read in full shows all of it.")
    assert opened and isinstance(reading, HandoutReading)
    assert reading.laid.title == "Chase"
    assert back and search == ""
