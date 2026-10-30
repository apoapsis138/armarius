"""Every modal dialog is drawn in the shared dialog frame (ModalDialog's
.dialog-box rule): a border and its own background, not bare text on the
dimmed screen."""

import pytest
from support import wait_until

from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.fields import FieldsDialog
from ars_magica_manager.tui.screens.prompts import ConfirmScreen


@pytest.mark.parametrize(
    "make",
    [
        lambda: ConfirmScreen("Delete [b]Summa[/]?"),
        lambda: ConfirmScreen("Leave without saving?", safe_answer=True),
    ],
    ids=["confirm", "safe confirm"],
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
        ):
            app.push_screen(screen, answers.append)
            assert await wait_until(pilot, lambda s=screen: app.screen is s)
            await pilot.press("escape")
            assert await wait_until(pilot, lambda s=screen: app.screen is not s)
    assert answers == [False, True]


async def test_cancelling_a_form_with_changes_asks_first():
    app = ArsMagicaManagerApp()
    answers = []
    async with app.run_test(size=(120, 45)) as pilot:
        dialog = FieldsDialog("A Form", [DialogField("a", "A", "text", value="old")])
        app.push_screen(dialog, answers.append)
        assert await wait_until(pilot, lambda: app.screen is dialog)
        await pilot.pause()
        dialog.query_one("Input").value = "new"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("n")
        assert await wait_until(pilot, lambda: app.screen is dialog)
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: answers == [None])


async def test_cancelling_a_form_with_no_changes_just_leaves():
    app = ArsMagicaManagerApp()
    answers = []
    async with app.run_test(size=(120, 45)) as pilot:
        dialog = FieldsDialog("A Form", [DialogField("a", "A", "text", value="old")])
        app.push_screen(dialog, answers.append)
        assert await wait_until(pilot, lambda: app.screen is dialog)
        await pilot.pause()
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: answers == [None])
