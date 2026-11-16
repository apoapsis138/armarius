"""while_open: screen work that outlives its screen ends quietly, and only
then (closing.py)."""

from __future__ import annotations

import pytest
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Static

from ars_magica_manager.tui.screens.closing import OpenAwareScreen, while_open


class _Screen(OpenAwareScreen[None]):
    """A screen whose openness the test sets (the hook while_open asks)."""

    def __init__(self, *, is_open: bool) -> None:
        super().__init__()
        self.open_now = is_open

    @property
    def is_open(self) -> bool:
        return self.open_now

    @while_open
    def look(self) -> str:
        return self.query_one("#missing", Static).id or ""

    @while_open
    async def look_later(self) -> str:
        return self.query_one("#missing", Static).id or ""

    @while_open
    def fail(self) -> None:
        raise ValueError("not a missing widget")

    @while_open
    async def fail_later(self) -> None:
        raise ValueError("not a missing widget")

    @while_open
    def answer(self, value: int, *, plus: int = 0) -> int:
        return value + plus

    @while_open
    async def answer_later(self, value: int) -> int:
        return value


async def test_a_missing_widget_after_the_screen_closed_ends_the_work_quietly() -> None:
    screen = _Screen(is_open=False)
    assert screen.look() is None
    assert await screen.look_later() is None


async def test_a_missing_widget_while_the_screen_is_open_is_a_bug() -> None:
    screen = _Screen(is_open=True)
    with pytest.raises(NoMatches):
        screen.look()
    with pytest.raises(NoMatches):
        await screen.look_later()


@pytest.mark.parametrize("is_open", [True, False])
async def test_any_other_error_is_raised_open_or_closed(is_open: bool) -> None:
    screen = _Screen(is_open=is_open)
    with pytest.raises(ValueError):
        screen.fail()
    with pytest.raises(ValueError):
        await screen.fail_later()


async def test_the_method_runs_with_its_arguments_and_returns_its_result() -> None:
    screen = _Screen(is_open=True)
    assert screen.answer(2, plus=3) == 5
    assert await screen.answer_later(7) == 7
    assert screen.look.__name__ == "look"  # Textual counts its parameters


class _Page(OpenAwareScreen[None]):
    def compose(self) -> ComposeResult:
        yield Static("page")


class _Dialog(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        yield Static("dialog")


async def test_a_screen_is_open_until_dismissed_even_under_a_dialog() -> None:
    app = App[None]()
    async with app.run_test() as pilot:
        page = _Page()
        await app.push_screen(page)
        await pilot.pause()
        assert page.is_open
        await app.push_screen(_Dialog())
        await pilot.pause()
        assert page.is_open  # covered, not closed
        app.pop_screen()
        app.pop_screen()
        await pilot.pause()
        assert not page.is_open
