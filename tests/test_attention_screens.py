"""Needs You on screen: the terminal's Seasons sheet lists it and its
count, and Edit opens the chosen item's record; the desktop's Seasons
page has it as a chapter after Ahead."""

from __future__ import annotations

import os

import pytest
from support import wait_until
from test_attention import _saga
from test_list_flows import ListCase, _choose_row, _open
from textual.widgets import Static

from ars_magica_manager import storage
from ars_magica_manager.models import STORY_EVENT, CovenantDiaryEntry
from ars_magica_manager.sections import ATTENTION_SECTION
from ars_magica_manager.tui.app import ArsMagicaManagerApp

NEEDS_YOU = ListCase(("seasons",), ATTENTION_SECTION, "attention-list", lambda s: [])


async def test_the_terminal_lists_what_needs_you_and_e_opens_it():
    saga, covenant = _saga()
    covenant.diary.append(
        CovenantDiaryEntry(1219, "Spring", "Smoke", category=STORY_EVENT)
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, NEEDS_YOU)
        info = view.query_one("#seasons-info-right", Static)
        assert "Needs you" in str(info.content)
        await _choose_row(pilot, view, NEEDS_YOU, 0)
        panel = view.query_one("#season-record-text", Static)
        assert await wait_until(pilot, lambda: "Smoke" in str(panel.content))
        await pilot.press("e")
        assert await wait_until(
            pilot,
            lambda: (
                workspace.selected_covenant is not None
                and workspace.selected_covenant.id == covenant.id
            ),
        )


def test_the_desktop_seasons_page_has_a_needs_you_chapter():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.seasons import NEEDS_YOU as CHAPTER
    from ars_magica_manager.gui.seasons import SeasonsPage
    from ars_magica_manager.gui.themes import SCRIPTORUM

    QApplication.instance() or QApplication([])
    saga, covenant = _saga()
    covenant.diary.append(
        CovenantDiaryEntry(1219, "Spring", "Smoke", category=STORY_EVENT)
    )
    opened = []
    page = SeasonsPage(saga, SCRIPTORUM, run=opened.append)
    chapters = page.chapters()
    assert chapters.index(CHAPTER) == chapters.index("Ahead") + 1
