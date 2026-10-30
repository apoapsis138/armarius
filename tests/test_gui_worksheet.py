"""The desktop Creation Worksheet: opened from the More menu while a record
is In Creation, a step's list spent on and taken back, a step's button,
buying with a covenant's Build Points, and Move to In Play, answered
without showing the dialogs (gui_steps.answering)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QPushButton, QTableView
from screen_helpers import _sample_saga_with_covenant
from support import offer_only

from ars_magica_manager import creation, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog, FieldsDialog
from ars_magica_manager.gui.manage import ModeToggle
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.gui.worksheet import WorksheetPage
from ars_magica_manager.models import VirtueFlawInstance


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    return MainWindow(saga_ids=[saga.id])


def _open_worksheet(window: MainWindow) -> None:
    """Click Worksheet beside the record's mode in its header."""
    toggle = window.findChild(ModeToggle)
    assert toggle is not None and toggle.worksheet is not None
    toggle.worksheet.click()


def _worksheet(window: MainWindow) -> WorksheetPage:
    page = window.page()
    assert isinstance(page, WorksheetPage)
    return page


def _choose_row(page: WorksheetPage, title: str, row: int) -> None:
    """Click row `row` of the table in the step titled `title`."""
    buttons = section_buttons(page, title)
    holder = next(iter(buttons.values())).parentWidget()
    section = holder.parentWidget() if holder is not None else None
    assert section is not None
    view = section.findChild(QTableView)
    assert view is not None
    view.selectRow(row)


def _press(page: WorksheetPage, words: str) -> None:
    """Click the button `words` on the step on show."""
    chapter = page.codex.pages.currentWidget()
    assert chapter is not None
    for button in chapter.findChildren(QPushButton):
        if button.text().strip() == words:
            button.click()
            return
    raise AssertionError(f"No button {words!r} on this step")


def _new_companion(saga):
    character = creation.add_character(saga, "Brother Anselm", "companion", "cov1")
    character.background.year_born = saga.current_year - 25
    return character


def test_the_worksheet_spends_childhood_xp_and_takes_it_back(app):
    saga = _sample_saga_with_covenant()
    character = _new_companion(saga)
    window = _window(saga)
    window.show_character(character.id)
    _open_worksheet(window)
    page = _worksheet(window)
    assert window.crumb_names()[-2:] == ["Brother Anselm", "Creation Worksheet"]
    assert [name[2:] for name in page.chapters()] == [
        "Concept",
        "Virtues and Flaws",
        "Characteristics",
        "Early Childhood",
        "Later Life",
        "Equipment",
        "Review Interests",
        "Finishing Touches",
    ]
    page.open_step("childhood")
    asked = answering(window, {"language": "German"})
    _press(page, "Native Language")
    assert isinstance(asked[0], FieldsDialog)
    page = _worksheet(window)
    asked = answering(window, {"target": "Brawl", "xp": "15"})
    section_buttons(page, "Early Childhood")["Spend xp"].click()
    saved = storage.load_saga(saga.id).character(character.id)
    assert saved is not None
    assert [(x.step, x.target, x.xp) for x in saved.creation_xp] == [
        ("childhood", "Living Language: German", 75),
        ("childhood", "Brawl", 15),
    ]
    page = _worksheet(window)
    # The window stays on the step it was on.
    assert page.codex.rail.currentRow() == 3
    _choose_row(page, "Early Childhood", 1)
    assert "Brawl" in page.codex.inspector.title.text()
    asked = answering(window, True)
    section_buttons(page, "Early Childhood")["Take it back"].click()
    assert isinstance(asked[0], ConfirmDialog)
    saved = storage.load_saga(saga.id).character(character.id)
    assert saved is not None
    assert [x.target for x in saved.creation_xp] == ["Living Language: German"]


def test_a_rows_verbs_are_greyed_out_where_they_cant_act(app):
    saga = _sample_saga_with_covenant()
    character = _new_companion(saga)
    character.virtues_flaws = []
    window = _window(saga)
    window.open_worksheet(character.id)
    page = _worksheet(window)
    page.open_step("childhood")
    answering(window, {"language": "German"})
    _press(page, "Native Language")
    page = _worksheet(window)
    # The only row there is is the one they act on.
    assert section_buttons(page, "Early Childhood")["Change its xp"].isEnabled()
    answering(window, {"target": "Brawl", "xp": "15"})
    section_buttons(page, "Early Childhood")["Spend xp"].click()
    page = _worksheet(window)
    buttons = section_buttons(page, "Early Childhood")
    assert not buttons["Change its xp"].isEnabled()
    _choose_row(page, "Early Childhood", 0)
    assert buttons["Change its xp"].isEnabled()
    # The Virtues step has no Edit: its rows are only removed.
    assert "Edit" not in section_buttons(page, "Virtues and Flaws")


def test_a_new_covenant_buys_a_vis_source_with_its_build_points(app):
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    covenant.in_creation = True
    window = _window(saga)
    window.open_worksheet(covenant.id)
    page = _worksheet(window)
    page.open_step("build_points")
    asked = answering(
        window,
        "A vis source",
        {
            "name": "The Singing Spring",
            "art": "Aquam",
            "season": "Spring",
            "pawns": "4",
        },
    )
    section_buttons(page, "Resources")["Buy something"].click()
    assert isinstance(asked[0], ChooseDialog)
    saved = storage.load_saga(saga.id).covenant(covenant.id)
    assert saved is not None
    assert "The Singing Spring" in [p.name for p in saved.possessions]


def test_move_to_in_play_leaves_the_worksheet_for_the_record(app):
    saga = _sample_saga_with_covenant()
    character = _new_companion(saga)
    window = _window(saga)
    window.open_worksheet(character.id)
    page = _worksheet(window)
    page.open_step("finish")
    answering(window, True)
    _press(page, "Move to In Play")
    saved = storage.load_saga(saga.id).character(character.id)
    assert saved is not None and not saved.in_creation
    assert isinstance(window.page(), CharacterSheet)


def test_a_companion_joins_a_tradition_and_gains_its_training_step(app):
    saga = _sample_saga_with_covenant()
    offer_only(saga, "trad_vitkir")
    character = _new_companion(saga)
    character.virtues_flaws.append(VirtueFlawInstance("vf_the_gift"))
    window = _window(saga)
    window.show_character(character.id)
    _open_worksheet(window)
    page = _worksheet(window)
    asked = answering(window, "Vitkir")
    _press(page, "Choose tradition")
    assert isinstance(asked[0], ChooseDialog)
    page = _worksheet(window)
    assert "Tradition Training" in [name[2:] for name in page.chapters()]
    page.open_step("training")
    _press(page, "Open the Arts")
    saved = storage.load_saga(saga.id).character(character.id)
    assert saved is not None
    assert saved.traditions == ["trad_vitkir"]
    assert "Fehu" in {a.name for a in saved.abilities}
