"""The App update notice in the terminal app: the title page's Update row,
the Update screen, its What's new, and the short line a saga shows once."""

from __future__ import annotations

import time

import pytest
from support import everything_saga, screen_lines, wait_until
from textual.pilot import Pilot
from textual.screen import Screen
from textual.widgets import Button, Checkbox, OptionList, Static

from ars_magica_manager import settings, storage, updates
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen
from ars_magica_manager.tui.screens.title import UPDATE, TitleScreen
from ars_magica_manager.tui.screens.update import NotesScreen, UpdateLine, UpdateScreen

NOTES = "### Pagina\n\n- **My sheet.** [bold]stays[/] text.\n- Second."


@pytest.fixture
def found(monkeypatch: pytest.MonkeyPatch) -> None:
    # Checks on (conftest keeps GitHub itself out of reach).
    monkeypatch.delenv(updates.ENV_VAR, raising=False)
    settings.update_settings(
        **{
            updates.FOUND: {
                "version": "99.0.0",
                "date": "2026-12-01",
                "notes": NOTES,
                "url": updates.LATEST_URL,
            },
            # No check at start-up in a test: one ran just now.
            updates.LAST_CHECK: time.time(),
        }
    )


def _app() -> ArsMagicaManagerApp:
    app = ArsMagicaManagerApp()
    app.show_title = True
    app.update_copy = updates.Build()
    return app


async def _on(pilot: Pilot, app: ArsMagicaManagerApp, kind: type[Screen]) -> None:
    """Wait for a screen of `kind` on top, mounted: a screen is app.screen
    a beat before its widgets are."""
    assert await wait_until(
        pilot, lambda: isinstance(app.screen, kind) and app.screen.is_mounted
    ), f"{kind.__name__} never came up (on top: {type(app.screen).__name__})"


async def _shown(pilot: Pilot, app: ArsMagicaManagerApp, text: str) -> None:
    """Wait for `text` on the screen as drawn, which lags what was asked."""

    def drawn() -> str:
        return "\n".join(screen_lines(app))

    assert await wait_until(pilot, lambda: text in drawn()), drawn()


def _ids(listed: OptionList) -> list[str | None]:
    return [listed.get_option_at_index(i).id for i in range(listed.option_count)]


@pytest.mark.usefixtures("found")
async def test_the_title_page_lists_update_last_and_it_opens_the_update_screen() -> (
    None
):
    app = _app()
    async with app.run_test(size=(120, 45)) as pilot:
        await _on(pilot, app, TitleScreen)
        listed = app.screen.query_one(OptionList)
        assert await wait_until(pilot, lambda: _ids(listed)[-1:] == [UPDATE])
        await _shown(pilot, app, "Armarius 99.0.0 is available")
        listed.highlighted = listed.option_count - 1
        await pilot.press("enter")
        await _on(pilot, app, UpdateScreen)
        await _shown(pilot, app, "! Armarius 99.0.0 is available (2026-12-01)")
        await _shown(pilot, app, "My sheet. [bold]stays[/] text.")  # plain, not markup
        app.screen.query_one("#update-whats-new", Button).press()
        await _on(pilot, app, NotesScreen)
        await _shown(pilot, app, "### Pagina")
        await pilot.press("escape")
        await _on(pilot, app, UpdateScreen)
        app.screen.query_one("#update-skip", Button).press()
        assert await wait_until(
            pilot, lambda: settings.load_settings().get(updates.SKIPPED) == "99.0.0"
        )
        assert "skipped" in str(
            app.screen.query_one("#update-headline", Static).render()
        )
        await pilot.press("escape")
        await _on(pilot, app, TitleScreen)
        assert await wait_until(pilot, lambda: UPDATE not in _ids(listed))


async def test_no_update_row_without_a_notice() -> None:
    app = _app()
    app.update_copy = updates.Quiet()
    async with app.run_test(size=(120, 45)) as pilot:
        await _on(pilot, app, TitleScreen)
        listed = app.screen.query_one(OptionList)
        assert await wait_until(pilot, lambda: listed.option_count > 0)
        assert UPDATE not in _ids(listed)


@pytest.mark.usefixtures("found")
async def test_the_checkbox_turns_the_check_off_and_hides_the_notice() -> None:
    app = _app()
    async with app.run_test(size=(120, 45)) as pilot:
        assert await wait_until(pilot, lambda: isinstance(app.screen, TitleScreen))
        app.action_open_update()
        assert await wait_until(pilot, lambda: isinstance(app.screen, UpdateScreen))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#update-check")))
        app.screen.query_one("#update-check", Checkbox).toggle()
        assert await wait_until(pilot, lambda: app.update_notice is None)
        assert settings.load_settings()[updates.CHECK] is False


@pytest.mark.usefixtures("found")
async def test_a_saga_shows_the_short_line_once() -> None:
    storage.save_saga(everything_saga())
    app = _app()
    app.show_title = False
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await _on(pilot, app, WorkspaceScreen)
        line = app.screen.query_one(UpdateLine)
        assert await wait_until(pilot, lambda: line.display)
        await _shown(pilot, app, "Armarius 99.0.0 is available")
        # Once a sitting: another saga's line (here, a second one) stays
        # hidden.
        again = UpdateLine()
        await app.screen.mount(again)
        await pilot.pause()
        assert not again.display and line.display


async def test_a_copy_that_never_checks_offers_no_update_command() -> None:
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        titles = [c.title for c in app.get_system_commands(app.screen)]
        assert "Update" not in titles
        app.update_copy = updates.Build()
        titles = [c.title for c in app.get_system_commands(app.screen)]
        assert "Update" in titles
