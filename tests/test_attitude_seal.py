"""The attitude seal as each front-end draws it."""

from __future__ import annotations

import os

import pytest
from support import screen_lines
from textual.app import App, ComposeResult

from ars_magica_manager.models import Attitude, Reason
from ars_magica_manager.tui.screens.widgets import AttitudeSeal

WARY = Attitude("arnhaven", 0, [Reason("Took the ford source", -1)])


class _SealApp(App[None]):
    def compose(self) -> ComposeResult:
        yield AttitudeSeal(WARY, id="seal")


async def test_the_terminal_draws_the_seal_on_one_line():
    app = _SealApp()
    async with app.run_test(size=(40, 3)) as pilot:
        assert "◉ −1 Wary" in screen_lines(app)[0]
        app.query_one("#seal", AttitudeSeal).show(None)
        await pilot.pause()
        assert "◉ 0 Neutral" in screen_lines(app)[0]


def test_the_desktop_draws_the_seal_with_its_reasons():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.figures import attitude_seal
    from ars_magica_manager.gui.themes import PALETTES

    QApplication.instance() or QApplication([])
    p = PALETTES[0]
    seal = attitude_seal(WARY, p)
    assert (seal.value, seal.caption) == ("−1", "Wary")
    assert seal.colour == p["text-warning"]
    assert seal.toolTip() == "Started at 0; −1 Took the ford source"
