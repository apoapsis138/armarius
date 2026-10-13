"""The desktop's picker fields: a field whose value is chosen from a
searchable list (the book's spell, an Initiation's Virtue, which then
asks for the Art it names) and a field holding a small list (a known
spell's Mastery Abilities), each answered without showing the dialogs
(gui_steps.answering)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, list_add, list_delete, list_edit, pick, section_buttons
from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.forms import ChooseDialog, FieldsDialog
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Ability, MasteryAbility


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    return MainWindow(saga_ids=[saga.id])


def test_mastery_abilities_are_added_edited_and_deleted_in_the_form(app):
    saga = _sample_saga_with_covenant()
    known = saga.characters[0].spells_known[0]
    known.mastery_abilities = [MasteryAbility("Quiet Casting", 1, 5)]
    window = _window(saga)
    window.show_character(saga.characters[0].id)
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Hermetic Magic")
    page.spell_view.selectRow(0)
    asked = answering(
        window,
        {"mastery_abilities": list_add},
        {"name": "Fast Casting", "level": "1", "xp": "5"},
    )
    # The Mastery form opens; Add on its list asks for one ability.
    section_buttons(page, "Known Spells")["Edit"].click()
    assert [type(d) for d in asked] == [FieldsDialog, FieldsDialog]
    assert asked[1].windowTitle() == "Add a Mastery Ability"
    saved = storage.load_saga(saga.id).characters[0].spells_known[0]
    assert [(a.name, a.level, a.xp) for a in saved.mastery_abilities] == [
        ("Quiet Casting", 1, 5),
        ("Fast Casting", 1, 5),
    ]
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.spell_view.selectRow(0)
    answering(
        window,
        {"mastery_abilities": list_edit(1)},
        {"level": "2"},
    )
    section_buttons(page, "Known Spells")["Edit"].click()
    saved = storage.load_saga(saga.id).characters[0].spells_known[0]
    assert [a.level for a in saved.mastery_abilities] == [1, 2]
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.spell_view.selectRow(0)
    answering(window, {"mastery_abilities": list_delete(0)})
    section_buttons(page, "Known Spells")["Edit"].click()
    saved = storage.load_saga(saga.id).characters[0].spells_known[0]
    assert [a.name for a in saved.mastery_abilities] == ["Fast Casting"]


def test_a_lab_texts_spell_is_chosen_from_a_searchable_list(app):
    saga = _sample_saga_with_covenant()
    window = _window(saga)
    window.open_covenant(saga.covenants[0].id)
    asked = answering(
        window,
        {"name": "Notes on the Lance", "type": "Lab Text", "spell_id": pick},
        "Piercing Lance of Bone  CrAn 20  L&L",
    )
    section_buttons(window.page(), "Library")["Add"].click()
    assert isinstance(asked[1], ChooseDialog)
    assert asked[1].windowTitle() == "Choose the spell"
    book = storage.load_saga(saga.id).books[-1]
    assert book.name == "Notes on the Lance"
    assert book.spell_id is not None
    assert "Lance" in (asked[0].inputs["spell_id"].button.text())


def test_an_initiations_virtue_asks_for_what_it_names(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].abilities.append(Ability("Mercere Lore", "Arcane", 5))
    window = _window(saga)
    window.show_character("char1")
    asked = answering(
        window,
        {
            "activity": "undergo_initiation",
            "lore": "Mercere Lore",
            "mystery_virtue": pick,
        },
        "Affinity with {art}  [Minor Virtue, Hermetic]  (needs: art)",
        {"art": "ignem"},
    )
    section_buttons(window.page(), "This Season")["Plan"].click()
    assert [type(d) for d in asked] == [FieldsDialog, ChooseDialog, FieldsDialog]
    plan = storage.load_saga(saga.id).season_plans[0]
    assert (plan.activity, plan.effect_id, plan.effect_params) == (
        "undergo_initiation",
        "vf_affinity_with_art",
        {"art": "ignem"},
    )


def test_cancelling_a_pick_keeps_the_value_and_clear_blanks_it(app):
    saga = _sample_saga_with_covenant()
    window = _window(saga)
    window.show_character("char1")
    seen: dict[str, object] = {}

    def check(form: FieldsDialog, key: str) -> None:
        field = form.inputs[key]
        pick(form, key)  # cancelled below
        seen["after cancel"] = field.value  # type: ignore[attr-defined]
        field.clear.click()  # type: ignore[attr-defined]
        seen["after clear"] = field.value  # type: ignore[attr-defined]

    answering(
        window,
        {"activity": "undergo_initiation", "mystery_virtue": check},
        None,
    )
    section_buttons(window.page(), "This Season")["Plan"].click()
    assert seen == {"after cancel": None, "after clear": None}
