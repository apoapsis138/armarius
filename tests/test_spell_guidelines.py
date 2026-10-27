"""The Hermetic spell-guideline catalog (HoH:S pp. 34-129, MoH pp. 31-139):
its entries, which a saga offers by the books in play, and the spell
design's Guideline field filling in the Arts and base level on both
front-ends."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from screen_helpers import _sample_saga_with_covenant
from support import wait_until
from test_lab_one_season import _find
from textual.widgets import Button, Input, Select, Tree

from ars_magica_manager import catalog, commands, sourcebooks, storage
from ars_magica_manager.arts import FORMS, TECHNIQUES
from ars_magica_manager.commands import Picked
from ars_magica_manager.forms import spell_guideline as guideline_forms
from ars_magica_manager.forms.lab_plan import LabPlanForm, level_text
from ars_magica_manager.models import SpellDesign, SpellGuidelineDef
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules import spell_guidelines as sg
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.invent_spell import InventSpellScreen
from ars_magica_manager.tui.screens.steps import ChooseScreen

REPAIR = "gl_moh_crte_repair"  # CrTe 15, MoH p. 31 (DE p. 359 too)
ANAMORPH = "gl_hohs_crim_anamorph"  # CrIm 1, HoH:S p. 66 only
MUTO_ANAMORPH = "gl_hohs_muim_anamorph"  # MuIm 1, HoH:S p. 66 only
SUSTAIN = "gl_hohs_revi_sustain_suppress"  # ReVi General, HoH:S p. 129
CRAFT_STONE = "gl_hohs_rego_craft_stone"  # ReTe 4, HoH:S p. 61 only
BODY_PARTS = "gl_moh_muco_body_parts"  # MuCo 5, Target Part


def _entry(**changed: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "id": "gl_x",
        "name": "X",
        "technique": "Creo",
        "form": "Terram",
        "level": 5,
        "summary": "Something.",
        "source": "MoH",
        "page": 31,
    }
    entry.update(changed)
    return entry


# -- the catalog -----------------------------------------------------------


def test_every_guideline_loads_with_a_book_and_page():
    found = sg.guidelines()
    assert len(found) == 37
    assert len({g.id for g in found}) == len(found)
    problems = [
        g.id
        for g in found
        if g.source not in sourcebooks.SOURCEBOOKS
        or g.source not in ("HoH:S", "MoH")
        or g.technique not in TECHNIQUES
        or g.form not in FORMS
    ]
    assert problems == []
    # HoH:S's are from pp. 34-38, 61-70, 100 and 129, MoH's from its New
    # Guideline boxes.
    assert {g.page for g in found if g.source == "HoH:S"} <= {
        34,
        36,
        37,
        38,
        100,
        129,
        *range(61, 71),
    }
    assert {g.page for g in found if g.source == "MoH"} == {31, 49, 92, 113, 139}


def test_the_books_levels():
    by_id = catalog.load_spell_guideline_catalog_by_id()
    levels = {
        gid: (sg.arts(g), g.level) for gid, g in by_id.items() if g.source == "MoH"
    }
    assert levels == {
        "gl_moh_crte_repair": ("CrTe", 15),
        "gl_moh_muco_body_parts": ("MuCo", 5),
        "gl_moh_rete_transport": ("ReTe", 4),
        "gl_moh_crvi_preserve_1": ("CrVi", 5),
        "gl_moh_crvi_preserve_2": ("CrVi", 10),
        "gl_moh_crvi_preserve_3": ("CrVi", 15),
        "gl_moh_crhe_restore_wood": ("CrHe", 15),
    }
    assert (sg.arts(by_id[ANAMORPH]), by_id[ANAMORPH].level) == ("CrIm", 1)
    assert (sg.arts(by_id[MUTO_ANAMORPH]), by_id[MUTO_ANAMORPH].level) == ("MuIm", 1)
    emotions = [g.level for g in by_id.values() if g.id.startswith("gl_hohs_crme_")]
    assert sorted(emotions) == [4, 5, 5, 5]
    assert by_id[BODY_PARTS].target == "Part"


def test_societates_other_guidelines():
    by_id = catalog.load_spell_guideline_catalog_by_id()
    found = {
        g.id: (sg.arts(g), g.level, g.page, g.de_page)
        for g in by_id.values()
        if g.source == "HoH:S" and g.page not in range(61, 71)
    }
    assert found == {
        "gl_hohs_craq_ice": ("CrAq", 3, 34, 320),
        "gl_hohs_muau_gas_light": ("MuAu", 4, 36, 328),
        "gl_hohs_muau_gas_medium": ("MuAu", 5, 36, 328),
        "gl_hohs_pete_aspect": ("PeTe", 5, 37, 361),
        "gl_hohs_rete_projectile_5": ("ReTe", 5, 38, 362),
        "gl_hohs_rete_projectile_10": ("ReTe", 10, 38, 362),
        "gl_hohs_rete_projectile_15": ("ReTe", 15, 38, 362),
        "gl_hohs_crco_improve_wounds": ("CrCo", 25, 100, 331),
        SUSTAIN: ("ReVi", 0, 129, 370),
    }
    # The Rego craft table (p. 61), its Range Personal by Errata p. 59.
    craft = {
        g.id.removeprefix("gl_hohs_rego_craft_"): (sg.arts(g), g.level)
        for g in by_id.values()
        if g.id.startswith("gl_hohs_rego_craft_")
    }
    assert craft == {
        "bone": ("ReAn", 3),
        "gemstone": ("ReTe", 4),
        "glass": ("ReTe", 3),
        "leather": ("ReAn", 1),
        "metal": ("ReTe", 4),
        "stone": ("ReTe", 4),
        "timber": ("ReHe", 1),
        "wood": ("ReHe", 5),
        "wool_prepared": ("ReAn", 1),
        "wool_raw": ("ReAn", 3),
    }
    assert all(by_id[f"gl_hohs_rego_craft_{k}"].de_page is None for k in craft)


def test_a_general_guideline_leaves_the_base_level_typed():
    general = sg.find(SUSTAIN)
    assert general is not None and general.general
    assert sg.label(general) == "ReVi Gen Sustain or suppress magic of a type"
    values = sg.design_values(general)
    assert "base_level" not in values
    assert (values["technique"], values["form"]) == ("Rego", "Vim")
    assert "(ReVi Gen, HoH:S p. 129; DE p. 370)" in values["base_effect"]
    assert sg.matching(values["base_effect"]) is general
    # A General entry carries no level; any other needs one.
    levelless = {k: v for k, v in _entry().items() if k != "level"}
    assert SpellGuidelineDef.from_dict({**levelless, "general": True}).level == 0
    with pytest.raises(ValueError, match="gl_x.*General one has no level"):
        SpellGuidelineDef.from_dict(_entry(general=True))
    with pytest.raises(ValueError, match="gl_x.*level"):
        SpellGuidelineDef.from_dict(levelless)


@pytest.mark.parametrize(
    ("changed", "why"),
    [
        ({"technique": "Vim"}, "Technique and Form"),
        ({"form": "Creo"}, "Technique and Form"),
        ({"level": 0}, "level"),
        ({"level": "5"}, "level"),
        ({"summary": ""}, "summary"),
        ({"page": None}, "page"),
        ({"de_page": "12"}, "de_page"),
        ({"target": 3}, "target"),
    ],
)
def test_a_bad_entry_is_reported_by_name(changed: dict[str, object], why: str):
    with pytest.raises(ValueError, match=f"gl_x.*{why}"):
        SpellGuidelineDef.from_dict(_entry(**changed))


def test_a_catalog_file_reads_through_the_loader(tmp_path: Path):
    path = tmp_path / "guidelines.json"
    path.write_text(json.dumps({"entries": [_entry()]}), encoding="utf-8")
    [found] = catalog.load_spell_guideline_catalog(path)
    assert (found.name, found.level, found.de_page, found.target) == ("X", 5, None, "")


# -- which a saga offers ---------------------------------------------------


def test_a_saga_without_the_supplements_keeps_the_ones_the_de_prints():
    saga = _sample_saga_with_covenant()
    saga.books_in_play = []
    offered = {g.id for g in sg.offered(saga)}
    assert REPAIR in offered and ANAMORPH not in offered
    assert {g.id for g in sg.not_offered(saga)} == {
        "gl_hohs_crim_anamorph",
        "gl_hohs_muim_anamorph",
        "gl_hohs_crme_undirected_emotion",
        "gl_hohs_crme_class_emotion",
    } | {g.id for g in sg.guidelines() if g.id.startswith("gl_hohs_rego_craft_")}
    assert CRAFT_STONE not in offered and SUSTAIN in offered
    saga.books_in_play = ["HoH:S"]
    assert ANAMORPH in {g.id for g in sg.offered(saga)}
    assert sg.not_offered(saga) == []


def test_offered_narrows_to_the_arts():
    found = sg.offered(None, technique="Creo", form="Vim")
    assert [g.level for g in found] == [5, 10, 15]


def test_the_picker_lists_by_form_and_marks_out_of_play_books():
    saga = _sample_saga_with_covenant()
    saga.books_in_play = []
    step = guideline_forms.choose_guideline(saga)
    choices = step.choices()
    forms = [commands.facet(c, guideline_forms.FORM) for c in choices]
    assert forms == sorted(forms, key=FORMS.index)
    assert ANAMORPH not in {c.value for c in choices}
    assert step.others is not None
    others = step.others()
    assert {c.value for c in others} >= {ANAMORPH}
    assert step.apply(REPAIR) == Picked(REPAIR)
    repair = next(c for c in choices if c.value == REPAIR)
    assert "CrTe 15" in repair.label and "MoH p. 31; DE p. 359" in repair.detail


# -- the spell design ------------------------------------------------------


def _form(design: SpellDesign | None = None) -> LabPlanForm:
    saga = _sample_saga_with_covenant()
    form = LabPlanForm(
        saga,
        saga.characters[0],
        saga.laboratories[0],
        saga.current_season,
        saga.current_year,
        None,
        design=design,
        activity=lab_seasons.INVENT,
    )
    return form


def test_the_guideline_fills_the_arts_and_base_level():
    form = _form()
    field = next(f for f in form.fields() if f.key == "guideline")
    assert field.kind == "picker" and field.choose is not None
    assert field.fills is not None and field.display is not None
    assert field.display(None) == guideline_forms.NONE_CHOSEN
    filled = field.fills({"guideline": REPAIR})
    assert filled == {
        "technique": "Creo",
        "form": "Terram",
        "base_level": 15,
        "base_effect": "Repair a crafted item (CrTe 15, MoH p. 31; DE p. 359)",
    }
    assert field.fills({"guideline": BODY_PARTS})["target"] == "Part"
    # Clearing it leaves what was filled in.
    assert field.fills({"guideline": None}) == {}


def test_a_design_from_a_guideline_reopens_with_it_and_works_out_its_level():
    form = _form()
    values = {f.key: f.value for f in form.fields()}
    values.update(activity=lab_seasons.INVENT, name="Mend the Plough")
    values.update(guideline_forms.guideline_values({"guideline": REPAIR}))
    values.update(range="Touch")
    design = form.design_of(values)
    assert (design.technique, design.form, design.base_level) == ("Creo", "Terram", 15)
    assert "Level 20" in level_text(design)
    again = next(f for f in _form(design).fields() if f.key == "guideline")
    assert again.value == REPAIR
    typed = SpellDesign(key="k", name="Own", base_effect="my own base")
    assert next(f for f in _form(typed).fields() if f.key == "guideline").value is None


def test_starting_from_a_spell_clears_the_guideline():
    form = _form()
    assert form.design_values({"start_from": None})["guideline"] is None


async def test_the_terminal_guideline_button_fills_the_design():
    saga = _sample_saga_with_covenant()
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
        await wait_until(pilot, lambda: bool(screen.query("#inv-guideline")))
        screen.query_one("#inv-guideline", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        app.screen.query_one("#picker-search", Input).value = "Repair a crafted"
        await pilot.pause()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: app.screen is screen)
        await pilot.pause()
        assert screen.query_one("#inv-base", Input).value == "15"
        assert screen.query_one("#inv-technique", Select).value == "Creo"
        assert screen.query_one("#inv-form", Select).value == "Terram"
        assert "CrTe 15" in str(screen.query_one("#inv-guideline", Button).label)
        assert screen.values()["guideline"] == REPAIR


def test_the_desktop_guideline_fills_the_design():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLineEdit

    from ars_magica_manager.gui.forms import FieldsDialog
    from ars_magica_manager.gui.themes import SCRIPTORUM

    QApplication.instance() or QApplication([])
    form = _form().form()
    dialog = FieldsDialog(form.title, form.fields(), SCRIPTORUM)
    picker = dialog.inputs["guideline"]
    picker._set(REPAIR)
    base = dialog.inputs["base_level"]
    assert isinstance(base, QLineEdit) and base.text() == "15"
    effect = dialog.inputs["base_effect"]
    assert isinstance(effect, QLineEdit) and "Repair a crafted item" in effect.text()
