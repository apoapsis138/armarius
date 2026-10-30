"""The lists several desktop pages share: raw vis, a Diary, and Virtues &
Flaws on a familiar and a laboratory, answered without showing the
dialogs."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QScrollArea
from screen_helpers import _sample_saga_with_covenant
from support import aeolus

from ars_magica_manager import familiars as fam
from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.editing import Section, place_for
from ars_magica_manager.gui.familiar import FamiliarPage
from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog, FieldsDialog
from ars_magica_manager.gui.laboratory import LaboratoryPage
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Neighbour, VirtueFlawInstance


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.load(saga)
    return window


def _magus(saga):
    return next(c for c in saga.characters if c.type == "magus")


def test_a_magus_adds_and_deletes_raw_vis(app):
    saga = _sample_saga_with_covenant()
    magus = _magus(saga)
    magus.raw_vis = {}
    window = _window(saga)
    window.show_character(magus.id)
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Inventory")
    answering(window, {"art": "ignem", "pawns": "3"})
    section_buttons(page, "Raw Vis")["Add"].click()
    assert _magus(storage.load_saga(saga.id)).raw_vis == {"ignem": 3}
    page = window.page()
    assert isinstance(page, CharacterSheet)
    asked = answering(window, True)
    section_buttons(page, "Raw Vis")["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Delete Ignem vis?"
    assert _magus(storage.load_saga(saga.id)).raw_vis == {}


def test_a_character_and_a_laboratory_add_to_their_diaries(app):
    saga = _sample_saga_with_covenant()
    magus = _magus(saga)
    magus.diary = []
    window = _window(saga)
    window.show_character(magus.id)
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Diary")
    answering(window, {"name": "Studied the Ignem summa"})
    section_buttons(page, "Diary")["Add"].click()
    diary = _magus(storage.load_saga(saga.id)).diary
    assert [entry.name for entry in diary] == ["Studied the Ignem summa"]
    window.open_laboratory(saga.laboratories[0].id)
    lab_page = window.page()
    assert isinstance(lab_page, LaboratoryPage)
    before = len(saga.laboratories[0].diary)
    answering(window, {"name": "Cleaned the alembics"})
    section_buttons(lab_page, "Diary")["Add"].click()
    lab_diary = storage.load_saga(saga.id).laboratories[0].diary
    assert len(lab_diary) == before + 1
    assert lab_diary[-1].name == "Cleaned the alembics"


def test_a_laboratory_virtue_is_deleted_and_adding_offers_the_catalog(app):
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    lab.virtues_flaws = [VirtueFlawInstance("labvf_auspicious_shape", id="a1")]
    window = _window(saga)
    window.open_laboratory(lab.id)
    page = window.page()
    assert isinstance(page, LaboratoryPage)
    page.codex.open_chapter("Virtues & Flaws")
    asked = answering(window, None)
    virtues = section_buttons(page, "Virtues  ·  1 points")
    virtues["Add"].click()
    assert isinstance(asked[0], ChooseDialog)
    assert asked[0].windowTitle() == "Add a Laboratory Virtue"
    # A laboratory's steps open as windows over the page.
    assert not asked[0].inline
    asked = answering(window, True)
    virtues["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog) and not asked[0].inline
    assert asked[0].question.startswith("Delete Auspicious Shape?")
    assert storage.load_saga(saga.id).laboratories[0].virtues_flaws == []


def test_a_familiar_adds_a_virtue_from_the_catalog(app):
    saga = _sample_saga_with_covenant()
    familiar = fam.bind_familiar(saga, _magus(saga), "Nox")
    familiar.virtues_flaws = []
    window = _window(saga)
    window.open_familiar(familiar.id)
    page = window.page()
    assert isinstance(page, FamiliarPage)
    page.codex.open_chapter("Virtues & Flaws")
    offered: list[str] = []

    def ask(dialog):
        # A familiar's steps open as windows over the page.
        assert isinstance(dialog, ChooseDialog) and not dialog.inline
        offered.extend(dialog.shown())
        dialog.choose(offered[0])
        dialog.try_save()
        return dialog.result()

    window.ask = ask
    section_buttons(page, "Virtues  ·  0 points")["Add"].click()
    assert offered
    assert len(storage.load_saga(saga.id).familiars[0].virtues_flaws) == 1


def test_a_creature_and_a_neighbour_open_their_steps_as_windows(app):
    """Every button on a creature's or a neighbour's page opens its steps
    as windows, not in place."""
    saga = _sample_saga_with_covenant()
    saga.creatures = [aeolus()]
    saga.neighbours = [Neighbour(id="n1", name="The Bishop")]
    window = _window(saga)
    for name, show in (
        ("creature", lambda: window.open_creature("aeolus")),
        ("neighbour", lambda: window.open_neighbour("n1")),
    ):
        show()
        page = window.page()
        assert page is not None
        assert place_for(None, page) is None, name
        asked = answering(window, None)
        section_buttons(page, "Diary" if name == "neighbour" else "Abilities")[
            "Add"
        ].click()
        assert asked and not getattr(asked[0], "inline", True), name


def test_no_chapter_scrolls_sideways_at_1280_wide(app):
    """Every page's chapters, buttons included, fit a 1280-wide window
    beside the inspector."""
    saga = _sample_saga_with_covenant()
    magus = _magus(saga)
    familiar = fam.bind_familiar(saga, magus, "Nox")
    window = _window(saga)
    window.resize(1280, 900)
    window.show()
    wide: list[str] = []
    for show in (
        lambda: window.show_character(magus.id),
        lambda: window.open_familiar(familiar.id),
        lambda: window.open_laboratory(saga.laboratories[0].id),
        lambda: window.open_covenant(saga.covenants[0].id),
        window.open_content,
    ):
        show()
        page = window.page()
        codex = getattr(page, "codex", None)
        assert codex is not None
        for name in codex.chapters():
            codex.open_chapter(name)
            app.processEvents()
            area = codex.pages.currentWidget()
            if isinstance(area, QScrollArea) and area.horizontalScrollBar().maximum():
                wide.append(f"{type(page).__name__}: {name}")
    window.close()
    assert wide == []


def test_a_step_opens_in_place_in_its_section_and_closes_after(app):
    """Without a test answering it, Add's form opens inside its section,
    in place of the list, and the page's other buttons wait until it is
    saved."""
    saga = _sample_saga_with_covenant()
    magus = _magus(saga)
    magus.personality_traits = []
    window = _window(saga)
    window.show()
    window.show_character(magus.id)
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Description")
    window.ask = window._present  # the real one, not a test's
    seen = {}

    def answer() -> None:
        form = next(d for d in window.findChildren(FieldsDialog) if d.isVisible())
        section = form.parentWidget()
        seen["in section"] = isinstance(section, Section)
        seen["window"] = form.isWindow()
        seen["list hidden"] = all(w.isHidden() for w in section.body)
        seen["others wait"] = not section_buttons(page, "Reputations")[
            "Add"
        ].isEnabled()
        form.set_value("name", "Proud")
        form.set_value("score", "1")
        form.try_save()

    QTimer.singleShot(0, answer)
    section_buttons(page, "Personality Traits")["Add"].click()
    assert seen == {
        "in section": True,
        "window": False,
        "list hidden": True,
        "others wait": True,
    }
    saved = _magus(storage.load_saga(saga.id)).personality_traits
    assert [(t.name, t.score) for t in saved] == [("Proud", 1)]
    page = window.page()
    assert isinstance(page, CharacterSheet)
    assert section_buttons(page, "Reputations")["Add"].isEnabled()
    window.close()
