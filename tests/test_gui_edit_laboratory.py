"""The desktop laboratory page's Edit buttons and each list's Add, Edit and
Delete, answered without showing the dialogs."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.forms import laboratory as lf
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import ConfirmDialog
from ars_magica_manager.gui.laboratory import LaboratoryPage
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import NamedDescription


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _open(saga) -> tuple[MainWindow, LaboratoryPage]:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.load(saga)
    window.open_laboratory(saga.laboratories[0].id)
    return window, _page(window)


def _page(window: MainWindow) -> LaboratoryPage:
    page = window.page()
    assert isinstance(page, LaboratoryPage)
    return page


def _lab():
    return storage.load_saga("test_saga").laboratories[0]


def test_editing_the_identity_and_the_characteristics(app):
    window, page = _open(_sample_saga_with_covenant())
    asked = answering(window, {"name": "The Tower", "aura_modifier": "1"})
    page.identity_button.click()
    assert asked[0].windowTitle() == "Edit Laboratory Identity"
    assert (_lab().name, _lab().aura_modifier) == ("The Tower", 1)
    assert "The Tower" in window.crumb_names()
    answering(window, {"safety": "3"})
    section_buttons(_page(window), "Characteristics")["Edit"].click()
    assert _lab().characteristics.safety == 3


def test_a_specialization_source_is_added_edited_and_deleted(app):
    window, page = _open(_sample_saga_with_covenant())
    answering(window, {"specialization": "Terram", "points": "2", "source": "Cave"})
    controls = section_buttons(page, "Specialization sources")
    assert not controls["Edit"].isEnabled()
    controls["Add"].click()
    assert [(e.specialization, e.points) for e in _lab().specialties] == [("Terram", 2)]
    asked = answering(window, {"points": "0"})
    section_buttons(_page(window), "Specialization sources")["Edit"].click()
    assert asked[0].error.text() == "Points can't be 0."
    asked = answering(window, True)
    section_buttons(_page(window), "Specialization sources")["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Delete Terram +2 (Cave)?"
    assert _lab().specialties == []


def test_adding_a_feature_takes_two_forms_and_a_confirmation(app):
    window, page = _open(_sample_saga_with_covenant())
    before = len(_lab().features)
    asked = answering(
        window,
        {
            "feature_type": "custom",
            "virtue": lf.NEW_FEATURE_VIRTUE + "labvf_lesser_feature",
        },
        True,
        {"name": "Brass Cauldron", "point0": "Ignem"},
    )
    section_buttons(page, "Features")["Add"].click()
    assert len(asked) == 3 and isinstance(asked[1], ConfirmDialog)
    assert asked[2].windowTitle() == "Add a Feature"
    assert [f.name for f in _lab().features][before:] == ["Brass Cauldron"]


def test_a_room_card_is_chosen_then_edited_and_deleted(app):
    saga = _sample_saga_with_covenant()
    saga.laboratories[0].rooms = [NamedDescription("Vault"), NamedDescription("Attic")]
    window, page = _open(saga)
    page.codex.rail.setCurrentRow(page.chapters().index("Specializations"))
    controls = section_buttons(page, "Rooms")
    assert not controls["Edit"].isEnabled()
    attic = next(
        card
        for card in page.findChildren(ClickableCard)
        if any(label.text() == "Attic" for label in card.findChildren(QLabel))
    )
    attic.clicked()
    assert controls["Edit"].isEnabled()
    answering(window, {"description": "Dusty"})
    controls["Edit"].click()
    assert [(r.name, r.description) for r in _lab().rooms] == [
        ("Vault", ""),
        ("Attic", "Dusty"),
    ]


def test_raw_vis_and_an_arcane_connection(app):
    saga = _sample_saga_with_covenant()
    saga.laboratories[0].raw_vis = {"vim": 2}
    window, page = _open(saga)
    answering(window, {"art": "vim", "pawns": "3"})
    section_buttons(page, "Raw Vis")["Add"].click()
    assert _lab().raw_vis == {"vim": 5}
    asked = answering(window, True)
    section_buttons(_page(window), "Raw Vis")["Delete"].click()  # the only row
    assert asked[0].question == "Delete Vim vis?"
    assert _lab().raw_vis == {}
    answering(window, {"to": "a lock of hair"})
    section_buttons(_page(window), "Arcane Connections")["Add"].click()
    assert [c.to for c in _lab().arcane_connections] == ["a lock of hair"]
    answering(window, {"name": "Silver Mirror"})
    section_buttons(_page(window), "Equipment & Stores")["Add"].click()
    assert [i.name for i in _lab().inventory_items] == ["Silver Mirror"]
