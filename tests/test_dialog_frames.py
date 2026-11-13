"""Every modal dialog is drawn in the shared dialog frame (ModalDialog's
.dialog-box rule): a border and its own background, not bare text on the
dimmed screen."""

import pytest
from support import wait_until
from textual.app import App

from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.fields import FieldsDialog
from ars_magica_manager.tui.screens.prompts import ConfirmScreen, MenuScreen


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


_OPENERS = {
    "confirm": lambda: ConfirmScreen("Delete it?"),
    "menu": lambda: MenuScreen("More", [("a", "add", "Add")]),
}


@pytest.mark.parametrize("name", sorted(_OPENERS))
async def test_a_dialog_closed_as_it_opens_does_not_crash(name):
    """Its Mount can be handled after the app has already emptied it (a
    window closed, or the app quit, the moment it opened): choosing what to
    focus then must not look for a widget that is gone."""
    app = App()
    async with app.run_test():
        app.push_screen(_OPENERS[name]())
        app.exit()


@pytest.mark.parametrize(
    ("make", "focused"),
    [
        (_OPENERS["confirm"], "btn-no"),
        (lambda: ConfirmScreen("Leave?", safe_answer=True), "btn-yes"),
        (_OPENERS["menu"], "menu-list"),
    ],
    ids=["confirm", "safe confirm", "menu"],
)
async def test_a_dialog_opens_with_its_own_focus(make, focused):
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = make()
        app.push_screen(screen)
        assert await wait_until(pilot, lambda: app.screen is screen)
        assert await wait_until(
            pilot, lambda: getattr(app.focused, "id", None) == focused
        )


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
