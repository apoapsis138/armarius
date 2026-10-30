"""The desktop's season planning: the character's This Season, the
covenant's Seasons lists and the laboratory's Planning list, answered
without showing the dialogs. Each saves the saga, so the saved copy is
checked."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, buttons, section_buttons
from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import seasons, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog, FieldsDialog
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.rules import lab_seasons


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window() -> MainWindow:
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    return window


def _plans() -> list:
    saga = storage.load_saga("test_saga")
    return [(p.character_id, p.activity) for p in saga.season_plans]


def test_planning_and_clearing_a_characters_season(app):
    window = _window()
    window.show_character("char1")
    controls = section_buttons(window.page(), "This Season")
    # The supplements' season-long work is in A Season's Work below.
    assert list(controls) == ["Plan", "Edit", "Clear"]
    assert not controls["Edit"].isEnabled()  # nothing planned yet
    asked = answering(window, {"activity": "other", "details": "Hunting"})
    controls["Plan"].click()
    assert isinstance(asked[0], FieldsDialog)
    assert asked[0].windowTitle() == "Plan Leandro's Season (Spring 1220)"
    assert _plans() == [("char1", "other")]
    controls = section_buttons(window.page(), "This Season")
    assert list(controls) == ["Edit", "Clear"]
    assert controls["Clear"].isEnabled()
    asked = answering(window, True)
    controls["Clear"].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Clear Leandro's plan for Spring 1220 (Other: Hunting)?"
    assert _plans() == []


def test_planning_from_the_covenants_seasons(app):
    window = _window()
    window.open_covenant("cov1")
    controls = section_buttons(window.page(), "Magi")
    assert list(controls) == ["Plan", "Clear"]
    asked = answering(window, {"activity": "practice"})
    controls["Plan"].click()
    # Practice needs a subject: refused, nothing saved.
    assert asked[0].error.text()
    assert _plans() == []
    answering(window, {"activity": "other", "details": "Hunting"})
    section_buttons(window.page(), "Magi")["Plan"].click()
    assert _plans() == [("char1", "other")]
    answering(window, True)
    section_buttons(window.page(), "Magi")["Clear"].click()
    assert _plans() == []


def test_lab_work_and_a_new_spell_from_the_laboratory(app):
    window = _window()
    window.open_laboratory("lab1")
    controls = section_buttons(window.page(), "Planning")
    # Bind Familiar is in A Season's Work below, while its owner has none.
    assert list(controls) == ["New Spell", "Plan", "Clear"]
    assert len(buttons(window.page(), "Bind Familiar")) == 1
    answering(window, {"activity": lab_seasons.EXTRACT})
    controls["Plan"].click()
    assert _plans() == [("char1", lab_seasons.EXTRACT)]
    # New Spell in the chosen season (none chosen: the current one).
    asked = answering(
        window,
        "A new spell (a blank design)",
        {"name": "Spark", "technique": "Creo", "form": "Ignem", "base_level": "5"},
    )
    section_buttons(window.page(), "Planning")["New Spell"].click()
    assert isinstance(asked[0], ChooseDialog) and isinstance(asked[1], FieldsDialog)
    saga = storage.load_saga("test_saga")
    plan = seasons.plan_for(saga, saga.characters[0])
    assert plan is not None and plan.design is not None
    assert plan.design.name == "Spark"
