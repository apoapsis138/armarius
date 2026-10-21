"""Planning a full year ahead: the character sheet's Seasons Ahead (the
three seasons after this one) and the Plan Season form's Season field,
which moves a plan within the year."""

from __future__ import annotations

import os

import pytest
from support import wait_until
from test_list_flows import ListCase, _choose_row, _open, _press
from textual.widgets import Select, Static

from ars_magica_manager import seasons, storage
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import Character, Saga, SeasonPlan
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.sections import CHAR_AHEAD_SECTION
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, FieldsDialog


def _saga() -> tuple[Saga, Character]:
    magus = Character(id="mag1", name="Leandro", type="magus")
    saga = Saga(
        id="test_saga",
        name="Flows",
        current_year=1220,
        current_season="Autumn",
        characters=[magus],
    )
    return saga, magus


def _plan(magus, season, year, activity=rules.PRACTICE):
    return SeasonPlan(magus.id, year, season, activity)


def test_the_seasons_ahead_run_to_a_full_year():
    saga, magus = _saga()
    assert seasons.seasons_ahead(saga) == [
        ("Winter", 1220),
        ("Spring", 1221),
        ("Summer", 1221),
    ]
    assert seasons.planning_year(saga)[0] == ("Autumn", 1220)
    assert seasons.ahead_title(saga) == "Seasons Ahead (Winter 1220 - Summer 1221)"
    seasons.set_plan(saga, _plan(magus, "Spring", 1221))
    rows = [text for _, text in seasons.ahead_rows(saga, magus)]
    assert rows[0].endswith("nothing planned")
    assert rows[1].startswith("Spring 1221") and "Practice" in rows[1]
    assert "as the seasons planned before it" in seasons.ahead_info(saga, magus, 1)


def test_the_ops_plan_change_and_clear_a_season_ahead():
    saga, magus = _saga()
    ops = season_forms.ahead_season_ops(saga, magus)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    form = ops.add()
    assert isinstance(form, Form) and "Winter 1220" in form.title
    values = {f.key: f.value for f in form.fields()}
    assert values[season_forms.WHEN] == "Winter 1220"
    values["activity"] = rules.EXPOSURE
    assert form.validate is not None
    form.apply(values)
    assert seasons.plan_for(saga, magus, "Winter", 1220) is not None
    # The first free season is the next one now.
    form = ops.add()
    assert isinstance(form, Form) and "Spring 1221" in form.title
    removed = ops.remove(0)
    assert isinstance(removed, Confirm) and "Winter 1220" in removed.question
    removed.apply()
    assert seasons.plan_for(saga, magus, "Winter", 1220) is None
    assert isinstance(ops.remove(0), Refuse)


def test_every_season_ahead_planned_leaves_nothing_to_add():
    saga, magus = _saga()
    for season, year in seasons.seasons_ahead(saga):
        seasons.set_plan(saga, _plan(magus, season, year))
    add = season_forms.ahead_season_ops(saga, magus).add
    assert add is not None and isinstance(add(), Refuse)


def test_the_season_field_moves_a_plan():
    saga, magus = _saga()
    seasons.set_plan(saga, _plan(magus, "Winter", 1220))
    form = season_forms.plan_season(saga, magus, when=("Winter", 1220))
    values = {f.key: f.value for f in form.fields()}
    options = [v for _, v in next(f for f in form.fields() if f.key == "when").options]
    assert options == ["Autumn 1220", "Winter 1220", "Spring 1221", "Summer 1221"]
    values.update(activity=rules.PRACTICE, when="Summer 1221")
    assert form.validate is not None
    assert form.validate(values) in (None, "Choose what the experience goes into.")
    values["subject_1"] = "ability:Latin"
    form.apply(values)
    assert seasons.plan_for(saga, magus, "Winter", 1220) is None
    moved = seasons.plan_for(saga, magus, "Summer", 1221)
    assert moved is not None and moved.activity == rules.PRACTICE


def test_a_season_already_planned_cant_be_chosen_for_another_plan():
    saga, magus = _saga()
    seasons.set_plan(saga, _plan(magus, "Spring", 1221))
    form = season_forms.plan_season(saga, magus, when=("Winter", 1220))
    values = {f.key: f.value for f in form.fields()}
    values.update(activity=rules.EXPOSURE, when="Spring 1221")
    assert form.validate is not None
    assert "Spring 1221 is already planned" in (form.validate(values) or "")


def test_the_current_season_is_still_planned_the_same_way():
    saga, magus = _saga()
    form = season_forms.plan_season(saga, magus)
    assert "Autumn 1220" in form.title
    values = {f.key: f.value for f in form.fields()}
    assert values["when"] == "Autumn 1220"
    plan = season_forms.season_plan_from(saga, magus, {"activity": rules.EXPOSURE})
    assert (plan.season, plan.year) == ("Autumn", 1220)


AHEAD = ListCase(
    ("character", "mag1"),
    CHAR_AHEAD_SECTION,
    "char-ahead-list",
    lambda s: s.season_plans,
)


async def test_the_terminal_list_plans_the_chosen_season():
    saga, magus = _saga()
    seasons.set_plan(saga, _plan(magus, "Spring", 1221))
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, AHEAD)
        info = view.query_one("#char-ahead-info", Static)
        await _choose_row(pilot, view, AHEAD, 1)
        assert await wait_until(pilot, lambda: "Practice" in str(info.content))
        await _press(pilot, app, "e", FieldsDialog)
        dialog = app.screen
        assert "Spring 1221" in str(dialog.title_text)
        assert dialog.query_one("#fld-when", Select).value == "Spring 1221"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        await _press(pilot, app, "d", ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: not storage.load_saga("test_saga").season_plans
        )
        await _press(pilot, app, "a", FieldsDialog)
        assert "Winter 1220" in str(app.screen.title_text)


def test_the_desktop_planning_chapter_has_seasons_ahead():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel

    from ars_magica_manager.gui.character_sheet import CharacterSheet
    from ars_magica_manager.gui.themes import SCRIPTORUM

    QApplication.instance() or QApplication([])
    saga, magus = _saga()
    sheet = CharacterSheet(saga, magus, SCRIPTORUM)
    page = sheet._planning()
    texts = [label.text() for label in page.findChildren(QLabel)]
    assert any("Seasons Ahead (Winter 1220" in t for t in texts)
