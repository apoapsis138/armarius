"""Editing the desktop Character sheet beyond its Description chapter:
the header's Edit buttons, Abilities, Virtues & Flaws, the Arts, Known
Spells, Research Goals and Personal Gear, each answered without showing
its dialogs (gui_steps.answering)."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from gui_steps import answering, section_buttons
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import catalog, deeds, storage
from ars_magica_manager.forms import ability as ability_forms
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog
from ars_magica_manager.gui.markup_html import plain
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import VirtueFlawInstance
from ars_magica_manager.rules import vf_change as vc


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(prepare=None):
    """A window on the sample magus's sheet, `prepare` run on the saga
    before it is saved and opened."""
    saga = _sample_saga_with_covenant()
    if prepare is not None:
        prepare(saga)
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    assert window.saga is not None
    window.show_character(window.saga.characters[0].id)
    return window, saga.id


def _page(window) -> CharacterSheet:
    page = window.page()
    assert isinstance(page, CharacterSheet)
    return page


def _saved(saga_id: str):
    return storage.load_saga(saga_id).characters[0]


def test_the_header_edits_character_info_and_characteristics(app):
    window, saga_id = _window()
    asked = answering(window, {"name": "Leandro the Elder"})
    _page(window).info_edit.click()
    assert asked[0].windowTitle() == "Edit Character Info"
    assert _saved(saga_id).name == "Leandro the Elder"
    asked = answering(window, {"presence": "-1"})
    _page(window).characteristics_edit.click()
    assert asked[0].windowTitle() == "Edit Characteristics"
    assert _saved(saga_id).characteristics.presence == -1


def test_adding_a_templated_ability_then_editing_and_deleting_it(app):
    window, saga_id = _window()
    page = _page(window)
    page.open_chapter("Abilities")
    craft = catalog.load_ability_catalog_by_id()["ab_craft"]
    asked = answering(
        window,
        plain(ability_forms.ability_choice(craft).label),
        {"craft": "Smith"},
        {"xp": "5"},
    )
    section_buttons(page, "Abilities")["Add"].click()
    assert isinstance(asked[0], ChooseDialog)
    assert [d.windowTitle() for d in asked[1:]] == ["Craft: {craft}", "Craft: Smith"]
    names = [a.name for a in _saved(saga_id).abilities]
    assert "Craft: Smith" in names
    # Choosing its row, then Edit and Delete act on it.
    page = _page(window)
    page.open_chapter("Abilities")
    index = names.index("Craft: Smith")
    page.ability_table.on_choose(index)
    answering(window, {"xp": "15"})
    section_buttons(page, "Abilities")["Edit"].click()
    assert _saved(saga_id).abilities[index].xp == 15
    page = _page(window)
    page.ability_table.on_choose(index)
    asked = answering(window, True)
    section_buttons(page, "Abilities")["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Delete Craft: Smith?"
    assert "Craft: Smith" not in [a.name for a in _saved(saga_id).abilities]


def test_adding_and_deleting_a_flaw_from_its_card(app):
    def prepare(saga):
        saga.characters[0].virtues_flaws = [VirtueFlawInstance("vf_the_gift")]

    window, saga_id = _window(prepare)
    page = _page(window)
    page.open_chapter("Virtues & Flaws")
    flaws = section_buttons(page, "Flaws  ·  0 points")
    assert not flaws["Edit"].isEnabled() and not flaws["Delete"].isEnabled()
    answering(window, "Afflicted Tongue  [Minor Flaw, General]")
    flaws["Add"].click()
    saved = _saved(saga_id).virtues_flaws
    assert saved[-1].vf_id == "vf_afflicted_tongue"
    page = _page(window)
    asked = answering(window, True)
    controls = section_buttons(page, "Flaws  ·  1 points")
    # The only Flaw: Delete acts on it without choosing.
    controls["Delete"].click()
    assert asked[0].question == "Delete Afflicted Tongue?"
    assert _saved(saga_id).virtues_flaws == [VirtueFlawInstance("vf_the_gift")]


def test_editing_a_virtue_changes_what_it_names(app):
    def prepare(saga):
        saga.characters[0].virtues_flaws = [
            VirtueFlawInstance("vf_puissant_ability", {"ability": "magic theory"})
        ]

    window, saga_id = _window(prepare)
    page = _page(window)
    page.open_chapter("Virtues & Flaws")
    virtues = section_buttons(page, "Virtues  ·  1 points")
    answering(window, {"ability": "finesse"})
    # The only Virtue: Edit acts on it without choosing.
    virtues["Edit"].click()
    assert _saved(saga_id).virtues_flaws == [
        VirtueFlawInstance("vf_puissant_ability", {"ability": "finesse"})
    ]


def test_editing_the_arts_and_a_known_spells_mastery(app):
    window, saga_id = _window()
    page = _page(window)
    page.open_chapter("Hermetic Magic")
    answering(window, {"art_vim": "21"})
    section_buttons(page, "Magical Arts")["Edit"].click()
    assert _saved(saga_id).arts["vim"].xp == 21
    page = _page(window)
    spells = section_buttons(page, "Known Spells")
    assert set(spells) == {"Add", "Edit", "Delete"}
    assert set(section_buttons(page, "Current Location")) == {
        "Current Location",
        "Stay as Guest",
    }
    others = section_buttons(page, "Magic Outside the Lab")
    assert set(others) == {"Craft by Magic", "Cast in a Lacuna"}
    # Their forms open as windows over the page, not in place.
    asked = answering(window, None)
    others["Craft by Magic"].click()
    assert len(asked) == 1 and not getattr(asked[0], "inline", True)
    page = _page(window)
    spells = section_buttons(page, "Known Spells")
    if _saved(saga_id).spells_known:
        page.spell_view.selectRow(0)
        source = page.spell_view.model().index(0, 0)
        index = source.data(Qt.ItemDataRole.UserRole)  # the known spell's
        answering(window, {"mastery_score": "3"})
        spells["Edit"].click()
        assert _saved(saga_id).spells_known[index].mastery_score == 3


def test_adding_a_research_goal_and_an_item_of_personal_gear(app):
    window, saga_id = _window()
    page = _page(window)
    page.open_chapter("Research")
    answering(window, {"name": "Penetrating the Aegis"})
    section_buttons(page, "Research Goals")["Add"].click()
    assert _saved(saga_id).breakthroughs[-1].name == "Penetrating the Aegis"
    page = _page(window)
    page.open_chapter("Inventory")
    asked = answering(window, "Item", {"name": "Lantern"})
    section_buttons(page, "Personal Gear")["Add"].click()
    assert asked[1].windowTitle() == "Add a Item"
    assert _saved(saga_id).inventory[-1].name == "Lantern"


def test_gain_or_lose_in_play_sits_across_both_sides_and_keeps_the_diary(app):
    window, saga_id = _window()
    page = _page(window)
    page.open_chapter("Virtues & Flaws")
    strip = section_buttons(page, "During the Saga")
    assert list(strip) == ["Gain or Lose in Play"]
    virtues = next(t for t in _titles(page) if t.startswith("Virtues  ·"))
    flaws = next(t for t in _titles(page) if t.startswith("Flaws  ·"))
    assert set(section_buttons(page, virtues)) == set(section_buttons(page, flaws))
    answering(
        window,
        {
            "change": vc.GAIN_FLAW,
            "flaw_cause": vc.MISHAP,
            "flaw": VirtueFlawInstance("vf_missing_hand"),
            "story": "lost his hand at the ford",
        },
    )
    strip["Gain or Lose in Play"].click()
    saved = _saved(saga_id)
    assert saved.virtues_flaws[-1].vf_id == "vf_missing_hand"
    assert saved.diary[-1].name == "Gain a Flaw: Missing Hand"
    assert "lost his hand at the ford" in saved.diary[-1].details


def _titles(page) -> list[str]:
    return [label.text() for label in page.findChildren(QLabel)]


def test_the_deeds_chapter_sets_out_each_interest(app):
    window, _ = _window()
    page = _page(window)
    assert "Deeds" in page.chapters()
    page.open_chapter("Deeds")
    shown = page.codex.pages.currentWidget()
    titles = {label.text() for label in shown.findChildren(QLabel)}
    assert deeds.SESSION in titles
    buttons = {b.text().strip() for b in shown.findChildren(QPushButton)}
    assert "End of Session" in buttons
    page.open_chapter("Abilities")
    assert "Turbulence" not in section_buttons(page, "Abilities")
