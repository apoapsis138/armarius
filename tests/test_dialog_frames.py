"""Every modal dialog is drawn in the shared dialog frame (ModalDialog's
.dialog-box rule): a border and its own background, not bare text on the
dimmed screen."""

import pytest
from support import wait_until

from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.forms.importing import DuplicateBookScreen
from ars_magica_manager.tui.screens.prompts import ConfirmScreen


@pytest.mark.parametrize(
    "make",
    [
        lambda: ConfirmScreen("Delete [b]Summa[/]?"),
        lambda: DuplicateBookScreen("Summa", 2),
    ],
    ids=["confirm", "duplicate book"],
)
async def test_the_dialog_is_framed(make):
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = make()
        app.push_screen(screen)
        assert await wait_until(pilot, lambda: app.screen is screen)
        await pilot.pause()
        box = screen.query_one(".dialog-box")
        assert box.styles.border.top[0] == "round"
        assert box.styles.background.a > 0


async def test_escape_still_gives_the_safe_answer():
    app = ArsMagicaManagerApp()
    answers = []
    async with app.run_test(size=(120, 45)) as pilot:
        for screen in (
            ConfirmScreen("Delete it?"),
            ConfirmScreen("Leave without saving?", safe_answer=True),
            DuplicateBookScreen("Summa", 0),
        ):
            app.push_screen(screen, answers.append)
            assert await wait_until(pilot, lambda s=screen: app.screen is s)
            await pilot.press("escape")
            assert await wait_until(pilot, lambda s=screen: app.screen is not s)
    assert answers == [False, True, "skip"]
