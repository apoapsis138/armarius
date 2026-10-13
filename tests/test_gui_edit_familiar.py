"""Editing a familiar on the desktop: its Edit buttons and its lists' Add,
Edit and Delete, answered without showing the dialogs."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, buttons, section_buttons
from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import familiars as fam
from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.familiar import FamiliarPage
from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import BondPower


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window():
    saga = _sample_saga_with_covenant()
    magus = next(c for c in saga.characters if c.type == "magus")
    familiar = fam.bind_familiar(saga, magus, "Nox")
    familiar.bond_powers = [
        BondPower("b1", "Silent Wings", 10, "Perdo", "Imaginem"),
        BondPower("b2", "Keen Sight", 5, "Intellego", "Imaginem"),
    ]
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    assert window.saga is not None
    window.open_familiar(familiar.id)
    return window, saga.id


def _page(window) -> FamiliarPage:
    page = window.page()
    assert isinstance(page, FamiliarPage)
    return page


def _saved(saga_id: str):
    return storage.load_saga(saga_id).familiars[0]


def test_the_header_edits_the_familiar_and_its_characteristics(app):
    window, saga_id = _window()
    page = _page(window)
    [edit] = [b for b in buttons(page, "Edit") if b.toolTip() == "Edit Familiar"]
    asked = answering(window, {"name": "Umbra", "magic_might": "12"})
    edit.click()
    assert asked[0].windowTitle() == "Edit Familiar"
    saved = _saved(saga_id)
    assert (saved.name, saved.magic_might) == ("Umbra", 12)
    asked = answering(window, {"quickness": "4", "base_soak": "3"})
    buttons(_page(window), "Characteristics")[0].click()
    saved = _saved(saga_id)
    assert (saved.characteristics.quickness, saved.base_soak) == (4, 3)


def test_the_bond_edits_binding_and_health_edits_wounds(app):
    window, saga_id = _window()
    answering(window, {"golden_cord": "2"})
    section_buttons(_page(window), "The Bond")["Edit"].click()
    assert _saved(saga_id).golden_cord == 2
    answering(window, {"light": "1"})
    section_buttons(_page(window), "Health")["Wounds"].click()
    assert _saved(saga_id).wounds.light == 1


def test_a_natural_weapon_is_added_and_a_trait_too(app):
    window, saga_id = _window()
    answering(window, {"name": "Bite", "weapon_attack": "3"})
    section_buttons(_page(window), "Natural Weapons & Attacks")["Add"].click()
    assert [w.name for w in _saved(saga_id).natural_weapons] == ["Bite"]
    page = _page(window)
    reputations = section_buttons(page, "Reputations")
    answering(window, {"name": "Fierce Protector", "score": "1"})
    reputations["Add"].click()
    assert [t.name for t in _saved(saga_id).reputations] == ["Fierce Protector"]


def test_an_ability_is_chosen_from_the_catalog_then_edited(app):
    window, saga_id = _window()
    asked = answering(window, "Athletics  [General]", {"xp": "5"})
    section_buttons(_page(window), "Abilities")["Add"].click()
    assert isinstance(asked[0], ChooseDialog)
    abilities = _saved(saga_id).abilities
    assert [(a.name, a.xp) for a in abilities] == [("Athletics", 5)]
    answering(window, {"xp": "15"})
    section_buttons(_page(window), "Abilities")["Edit"].click()
    assert _saved(saga_id).abilities[0].xp == 15


def test_the_bond_power_clicked_is_the_one_deleted(app):
    window, saga_id = _window()
    page = _page(window)
    controls = section_buttons(page, "Bond Powers")
    assert not controls["Delete"].isEnabled()
    cards = [c for c in page.findChildren(ClickableCard) if "Keen Sight" in _words(c)]
    cards[0].clicked()
    assert controls["Delete"].isEnabled()
    asked = answering(window, True)
    controls["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Delete Keen Sight?"
    assert [p.name for p in _saved(saga_id).bond_powers] == ["Silent Wings"]


def _words(widget) -> str:
    from PySide6.QtWidgets import QLabel

    return " ".join(label.text() for label in widget.findChildren(QLabel))
