"""The desktop's Enchanted Devices sections (character, laboratory and
covenant): adding a device with a component, instilling an effect,
editing and deleting a row, and using a charge, answered without showing
the dialogs (gui_steps.answering)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, list_add, section_buttons
from PySide6.QtWidgets import QApplication, QListWidget
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.forms import ConfirmDialog, FieldsDialog
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import CHARGED, EnchantedDevice, InstilledEffect


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    return MainWindow(saga_ids=[saga.id])


def _devices(window: MainWindow) -> dict:
    return section_buttons(window.page(), "Enchanted Devices")


def _choose(window: MainWindow, row: int) -> None:
    """Click row `row` of the Enchanted Devices list."""
    buttons = _devices(window)
    holder = next(iter(buttons.values())).parentWidget()
    section = holder.parentWidget() if holder is not None else None
    assert section is not None
    view = section.findChild(QListWidget)
    assert view is not None
    view.setCurrentRow(row)


def test_a_magus_adds_a_device_with_a_component_then_instills_an_effect(app):
    saga = _sample_saga_with_covenant()
    window = _window(saga)
    window.show_character("char1")
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Inventory")
    buttons = _devices(window)
    assert list(buttons) == ["Add", "Edit", "Delete", "Instill", "Use Charge"]
    assert not buttons["Instill"].isEnabled()  # no row yet
    asked = answering(
        window,
        {"name": "Wand of Flames", "type": "Invested Device", "components": list_add},
        {"description": "oak wand", "material": "wood", "size": "small"},
    )
    buttons["Add"].click()
    assert [type(d) for d in asked] == [FieldsDialog, FieldsDialog]
    assert asked[0].windowTitle() == "Add an Enchanted Device"
    device = storage.load_saga(saga.id).enchanted_devices[-1]
    assert (device.name, device.holder_kind, device.holder_id) == (
        "Wand of Flames",
        "character",
        "char1",
    )
    assert [c.description for c in device.components] == ["oak wand"]
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Inventory")
    _choose(window, 0)
    asked = answering(window, {"name": "Pilum of Fire", "level": "20"})
    _devices(window)["Instill"].click()
    assert asked[0].windowTitle() == "Instill an Effect in Wand of Flames"
    effects = storage.load_saga(saga.id).enchanted_devices[-1].effects
    assert [(e.name, e.level) for e in effects] == [("Pilum of Fire", 20)]


def test_an_effect_row_is_edited_and_deleted(app):
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    saga.enchanted_devices.append(
        EnchantedDevice(
            id="d1",
            name="Brazier",
            holder_kind="laboratory",
            holder_id=lab.id,
            effects=[InstilledEffect(id="e1", name="Warmth", level=5)],
        )
    )
    window = _window(saga)
    window.open_laboratory(lab.id)
    window.page().codex.open_chapter("Stores")
    _choose(window, 1)  # the effect, under its device
    answering(window, {"level": "10"})
    _devices(window)["Edit"].click()
    assert storage.load_saga(saga.id).enchanted_devices[-1].effects[0].level == 10
    window.page().codex.open_chapter("Stores")
    _choose(window, 1)
    asked = answering(window, True)
    _devices(window)["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Delete Warmth from Brazier?"
    assert storage.load_saga(saga.id).enchanted_devices[-1].effects == []


def test_a_covenants_charged_item_uses_a_charge(app):
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    saga.enchanted_devices.append(
        EnchantedDevice(
            id="d1",
            name="Healing Salve",
            type=CHARGED,
            holder_kind="covenant",
            holder_id=covenant.id,
            charges_made=3,
            charges_left=3,
        )
    )
    window = _window(saga)
    window.open_covenant(covenant.id)
    window.page().codex.open_chapter("Possessions")
    _choose(window, 0)
    buttons = _devices(window)
    assert buttons["Use Charge"].isEnabled()
    asked = answering(window, True)
    buttons["Use Charge"].click()
    assert asked[0].question == "Use a charge of Healing Salve? It has 3 left."
    assert storage.load_saga(saga.id).enchanted_devices[-1].charges_left == 2
