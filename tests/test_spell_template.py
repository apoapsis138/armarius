"""Inventing from an existing spell as a template: any spell, the magus's
own known spells first, from New Spell and from the lab work form's Start
from on both front-ends; a known spell must be changed to be invented."""

from __future__ import annotations

import os

import pytest
from screen_helpers import _sample_saga_with_covenant
from support import wait_until
from test_lab_one_season import _find
from textual.widgets import Button, Input, OptionList, Tree

from ars_magica_manager import commands, storage
from ars_magica_manager.commands import Choose, Form, Picked
from ars_magica_manager.forms import lab_plan as lab_plan_forms
from ars_magica_manager.forms.lab_plan import LabPlanForm
from ars_magica_manager.models import Spell
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.invent_spell import InventSpellScreen
from ars_magica_manager.tui.screens.steps import ChooseScreen

KNOWN = "spell1"  # Ball of Abysmal Flame, CrIg 20, known to Leandro


def _saga():
    saga = _sample_saga_with_covenant()
    saga.spells.append(
        Spell(
            id="spell2",
            name="Pilum of Fire",
            technique="Creo",
            form="Ignem",
            level=20,
            base_level=10,
            range="Voice",
            duration="Momentary",
            target="Individual",
        )
    )
    return saga, saga.characters[0], saga.laboratories[0]


def _form(saga, magus, lab) -> LabPlanForm:
    return LabPlanForm(
        saga, magus, lab, saga.current_season, saga.current_year, None,
        activity=lab_seasons.INVENT,
    )  # fmt: skip


def test_the_template_list_puts_the_known_spells_first():
    saga, magus, _ = _saga()
    step = lab_plan_forms.choose_template(saga, magus)
    choices = step.choices()
    assert choices[0].value is None
    headings = list(dict.fromkeys(commands.heading(step, c) for c in choices[1:]))
    assert headings == ["Known to Leandro", lab_plan_forms.OTHER_SPELLS]
    known = [c.value for c in choices if commands.heading(step, c) == headings[0]]
    assert known == [KNOWN]
    assert "spell2" in {c.value for c in choices}
    assert step.apply(KNOWN) == Picked(KNOWN)


def test_new_spell_offers_the_known_spells_too():
    saga, _, lab = _saga()
    step = lab_plan_forms.new_spell(saga, lab, None)
    assert isinstance(step, Choose)
    assert KNOWN in {c.value for c in step.choices()}
    form = step.apply(KNOWN)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["start_from"] == KNOWN
    assert values["name"] == "Ball of Abysmal Flame"


def test_start_from_fills_the_design_in():
    saga, magus, lab = _saga()
    form = _form(saga, magus, lab)
    start = next(f for f in form.fields() if f.key == "start_from")
    assert start.fills is not None and start.choose is not None
    filled = start.fills({"start_from": "spell2"})
    assert (filled["name"], filled["technique"], filled["form"]) == (
        "Pilum of Fire",
        "Creo",
        "Ignem",
    )
    assert (filled["base_level"], filled["range"]) == (10, "Voice")
    blank = start.fills({"start_from": None})
    assert (blank["name"], blank["technique"], blank["range"]) == ("", None, "Personal")


def _values(form: LabPlanForm, spell_id: str, **changed):
    values = {f.key: f.value for f in form.fields()}
    values.update(form.design_values({"start_from": spell_id}))
    values.update(activity=lab_seasons.INVENT, start_from=spell_id, **changed)
    return values


def test_the_design_remembers_the_spell_it_started_from():
    saga, magus, lab = _saga()
    form = _form(saga, magus, lab)
    design = form.design_of(_values(form, "spell2"))
    assert design.source_spell_id == "spell2"
    assert design.name == "Pilum of Fire"


def test_a_known_spell_must_be_changed_to_be_invented():
    saga, magus, lab = _saga()
    form = _form(saga, magus, lab)
    unchanged = form.plan_of(_values(form, KNOWN))
    assert "already knows Ball of Abysmal Flame" in (
        form.problem(_values(form, KNOWN)) or ""
    )
    found, _ = lab_seasons.work(saga, magus, unchanged)
    assert "change the design" in found[0]
    variant = form.plan_of(_values(form, KNOWN, name="Ball of Lesser Flame"))
    found, work = lab_seasons.work(saga, magus, variant)
    assert found == [] and work is not None


async def test_the_terminal_start_from_lists_known_spells_first():
    saga, _, _ = _saga()
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        ws = app.screen
        tree = ws.query_one("#nav-tree", Tree)
        tree.select_node(_find(tree, ("laboratory", "lab1")))
        await wait_until(pilot, lambda: ws._laboratory_sheet_view is not None)
        view = ws._laboratory_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await wait_until(pilot, lambda: ws._active_section() == "tab-lab-planning")
        await pilot.press("a")
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, InventSpellScreen)
        )
        screen = app.screen
        await wait_until(pilot, lambda: bool(screen.query("#inv-start")))
        screen.query_one("#inv-start", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        picker = app.screen
        await pilot.pause()
        options = picker.query_one("#choose-list", OptionList)
        prompts = [
            str(options.get_option_at_index(i).prompt)
            for i in range(options.option_count)
        ]
        assert any("Known to Leandro" in p for p in prompts[:3])
        picker.query_one("#picker-search", Input).value = "Abysmal"
        await pilot.pause()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: app.screen is screen)
        await pilot.pause()
        assert screen.query_one("#inv-name", Input).value == "Ball of Abysmal Flame"
        assert "Ball of Abysmal Flame" in str(
            screen.query_one("#inv-start", Button).label
        )


def test_the_desktop_form_fills_from_start_from():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLineEdit

    from ars_magica_manager.gui.forms import FieldsDialog
    from ars_magica_manager.gui.themes import SCRIPTORUM

    QApplication.instance() or QApplication([])
    saga, magus, lab = _saga()
    form = _form(saga, magus, lab).form()
    dialog = FieldsDialog(form.title, form.fields(), SCRIPTORUM)
    picker = dialog.inputs["start_from"]
    picker._set("spell2")
    name = dialog.inputs["name"]
    assert isinstance(name, QLineEdit) and name.text() == "Pilum of Fire"
