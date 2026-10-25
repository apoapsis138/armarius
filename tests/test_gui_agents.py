"""The desktop's Agents chapter: the limit and the ledger, the chosen
agent in the inspector, and Add, Impress, Spend Agency Experience and Set
a Task greyed out where the chosen agent can't take them (answered
without showing the dialogs, gui_steps.answering)."""

from __future__ import annotations

import html
import os
import re

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel, QTableView
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Agent


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _words(widget) -> str:
    """Every label's words under `widget`, tags left out."""
    return "\n".join(
        html.unescape(re.sub(r"<[^>]+>", "", label.text()))
        for label in widget.findChildren(QLabel)
    )


def _window() -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    character = saga.characters[0]
    character.agents = [
        Agent("Sir Konrad", resistance=0, impressed=True, bond_trait="Owes", bond=2),
        Agent("Magister Hartwig", status="minor_virtue", modifiers=["rival"]),
    ]
    character.agency_xp = 4
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show_character(character.id)
    return window, saga.id


def _page(window: MainWindow) -> CharacterSheet:
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Agents")
    return page


def _choose(window: MainWindow, row: int) -> None:
    holder = next(iter(section_buttons(window.page(), "Agents").values()))
    section = holder.parentWidget().parentWidget()
    view = section.findChild(QTableView)
    assert view is not None
    view.selectRow(row)


def test_the_agents_chapter_follows_inventory_and_shows_the_limit(app):
    window, _ = _window()
    page = _page(window)
    chapters = page.chapters()
    assert chapters.index("Agents") == chapters.index("Inventory") + 1
    shown = _words(page)
    assert "Agents: 1 of" in shown and "1 being recruited" in shown
    assert "Agency experience: 4 unspent" in shown
    assert "Hermetic magi" in shown  # who is not an agent
    buttons = section_buttons(page, "Agents")
    assert list(buttons) == [
        "Add",
        "Edit",
        "Delete",
        "Impress",
        "Spend Agency Experience",
        "Set a Task",
    ]
    assert not buttons["Set a Task"].isEnabled()  # no row yet


def test_the_row_buttons_follow_the_chosen_agent(app):
    window, _ = _window()
    page = _page(window)
    _choose(window, 0)
    buttons = section_buttons(page, "Agents")
    assert buttons["Set a Task"].isEnabled()
    assert not buttons["Impress"].isEnabled()
    assert "Tasks for Agents" in _words(page.inspector)
    _choose(window, 1)
    assert buttons["Impress"].isEnabled()
    assert not buttons["Set a Task"].isEnabled()
    assert not buttons["Spend Agency Experience"].isEnabled()  # not impressed


def test_an_agent_is_added_and_a_task_set(app):
    window, saga_id = _window()
    page = _page(window)
    asked = answering(window, {"name": "Udo the Miller", "status": "free"})
    section_buttons(page, "Agents")["Add"].click()
    assert [type(d) for d in asked] == [FieldsDialog]
    agents = storage.load_saga(saga_id).characters[0].agents
    assert [a.name for a in agents][-1] == "Udo the Miller"
    page = _page(window)
    _choose(window, 0)
    asked = answering(window, {"task": "common", "risk": "none"})
    section_buttons(page, "Agents")["Set a Task"].click()
    assert asked[0].windowTitle() == "Set a Task: Sir Konrad"
    assert any("against 3" in words for _title, words in window.told)
