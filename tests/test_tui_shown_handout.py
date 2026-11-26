"""The terminal reads a shown written Handout's copy under its
Stationery's name (tui/screens/handout_reading.py), laid out only through
the tag parser: never a raw tag, its pictures by their place."""

from __future__ import annotations

from typing import Any

from textual.app import App
from textual.widgets import Button, Static

from ars_magica_manager import handouts, paths, shows
from ars_magica_manager.forms import handouts as handout_forms
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.models import SEALED_LETTER, Handout, HandoutPicture, Saga
from ars_magica_manager.tui.screens.handout_reading import HandoutReading
from ars_magica_manager.tui.screens.steps import run_steps


def _words(widget: Static) -> str:
    drawn = widget.render()
    return getattr(drawn, "plain", str(drawn))


async def test_a_written_copy_is_read_under_its_stationerys_name() -> None:
    shown = shows.Shown(
        "A letter",
        "[heading] Hail\n[script] fetch\n[picture 1]",
        stationery=SEALED_LETTER,
        pictures=(None,),
    )
    ended: list[object] = []
    app: App[Any] = App()
    async with app.run_test() as pilot:
        run_steps(app, show_forms.copy_form(shown), ended.append)
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, HandoutReading)
        read = [_words(s) for s in screen.query(Static)]
        screen.query_one("#btn-close", Button).press()
        await pilot.pause()

    assert read[0] == "— A sealed letter —"
    assert "Hail" in read and "[script] fetch" in read
    assert "(picture 1: shown with it)" in read
    assert not any("[heading]" in r for r in read)
    assert ended == [None]


async def test_a_preview_names_each_picture_in_place() -> None:
    """The storyguide's Preview from the Handouts list reads the same way,
    each placed picture by its own name."""
    saga = Saga(id="quiet", name="Quiet")
    saga.handouts = [
        Handout(
            "letter",
            "The Count's Letter",
            stationery=SEALED_LETTER,
            text="[heading] Hail\n[picture 1]",
            pictures=[HandoutPicture(paths.HANDOUTS, "seal.png")],
        )
    ]
    handouts.choose_story(saga, "")
    name = handouts.picture_name(saga, saga.handouts[0].pictures[0])
    app: App[Any] = App()
    async with app.run_test() as pilot:
        run_steps(app, handout_forms.preview_handout(saga, 0), lambda _e: None)
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, HandoutReading)
        read = [_words(s) for s in screen.query(Static)]

    assert read[0] == "— A sealed letter —"
    assert "The Count's Letter" in read and "Hail" in read
    assert f"(picture 1: {name})" in read
    assert not any("[heading]" in r for r in read)
