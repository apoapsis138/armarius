"""The activity picker on both front-ends: the Plan Season form's
Activity field opens a searchable list headed by Type, narrowed by the
Type and Book filters, with the character's recent activities first."""

from __future__ import annotations

import os

import pytest
from support import wait_until
from test_seasons import _open_season, everything_saga
from textual.widgets import Button, OptionList, Select

from ars_magica_manager import storage
from ars_magica_manager.forms import activity as activity_forms
from ars_magica_manager.models import DiaryEntry
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import activity_groups as groups
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.fields import FieldsDialog
from ars_magica_manager.tui.screens.steps import ChooseScreen


def _prompts(screen: ChooseScreen) -> list[str]:
    options = screen.query_one("#choose-list", OptionList)
    return [
        str(options.get_option_at_index(i).prompt) for i in range(options.option_count)
    ]


async def test_the_activity_field_opens_the_picker_filtered_by_type():
    saga = everything_saga()
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_season(pilot, app)
        await pilot.press("e")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        dialog = app.screen
        dialog.query_one("#fld-activity", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        picker = app.screen
        assert isinstance(picker, ChooseScreen)
        await pilot.pause()
        # Grouped under each Type, Study first.
        prompts = _prompts(picker)
        assert "[b]Study[/]" in prompts[0]
        assert any("Work & trade" in p for p in prompts)

        # F2 steps the Type filter on to Study: only study is listed.
        await pilot.press("f2")
        assert await wait_until(
            pilot, lambda: picker.chosen[activity_forms.TYPE] == groups.STUDY
        )
        await pilot.pause()
        listed = [picker.value_of(i) for i in picker._by_item_id.values()]
        assert rules.PRACTICE in listed
        assert all(rules.ACTIVITIES[k].group == groups.STUDY for k in listed)

        # Search within it, then choose.
        picker.query_one("#picker-search").value = "practice"
        await pilot.pause()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: app.screen is dialog)
        assert dialog._picked["activity"] == rules.PRACTICE
        assert str(dialog.query_one("#fld-activity", Button).label) == "Practice"


async def test_recent_activities_head_the_list_until_a_filter_is_chosen():
    saga = everything_saga()
    character = saga.characters[0]
    character.diary.append(
        DiaryEntry(saga.current_year - 1, "Winter", activity="Read a book")
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_season(pilot, app)
        await pilot.press("e")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        app.screen.query_one("#fld-activity", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        picker = app.screen
        assert isinstance(picker, ChooseScreen)
        await pilot.pause()
        prompts = _prompts(picker)
        assert prompts[0] == "[b]Recent[/]"
        assert prompts[1] == "Read a book"
        picker.query_one("#choose-filter-1", Select).value = activity_forms.CORE_BOOK
        await pilot.pause()
        assert "Recent" not in " ".join(_prompts(picker))


def test_the_desktop_picker_has_the_same_filters_headings_and_recent():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.forms import ChooseDialog
    from ars_magica_manager.gui.themes import SCRIPTORUM

    QApplication.instance() or QApplication([])
    saga = everything_saga()
    character = saga.characters[0]
    character.diary.append(
        DiaryEntry(saga.current_year - 1, "Winter", activity="Practice")
    )
    step = activity_forms.choose_activity(saga, character)
    dialog = ChooseDialog(step.title, step.choices(), SCRIPTORUM, step=step)
    rows = [dialog.list.item(i).text() for i in range(dialog.list.count())]
    assert rows[:3] == ["Recent", "Practice", "Study"]
    assert dialog.shown()[0] == "Practice"

    dialog.filters[activity_forms.TYPE].setCurrentText(f"Type: {groups.TEACHING}")
    rows = [dialog.list.item(i).text() for i in range(dialog.list.count())]
    assert rows[0] == groups.TEACHING
    assert "Recent" not in rows
    assert all(
        rules.ACTIVITIES[k].group == groups.TEACHING
        for k in (
            next(a.key for a in rules.ACTIVITIES.values() if a.label == label)
            for label in dialog.shown()
        )
    )
    dialog.try_save()
    assert rules.ACTIVITIES[dialog.chosen].group == groups.TEACHING
