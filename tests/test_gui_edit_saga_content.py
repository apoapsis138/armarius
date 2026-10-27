"""The desktop Saga Content page's Add, Edit and Delete buttons."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import house_rules as hr
from ars_magica_manager import spells as spl
from ars_magica_manager import storage
from ars_magica_manager.forms import saga_content as scf
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.markup_html import plain
from ars_magica_manager.gui.saga_content import SagaContentPage
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _content(chapter: str) -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_content()
    _page(window).codex.open_chapter(chapter)
    return window, saga.id


def _page(window: MainWindow) -> SagaContentPage:
    page = window.page()
    assert isinstance(page, SagaContentPage)
    return page


def test_a_saga_source_is_added_edited_and_refused_while_cited(app):
    window, saga_id = _content("Books")
    asked = answering(window, {"abbreviation": "HR", "title": "Ours"})
    controls = section_buttons(_page(window), "Saga Sources")
    assert not controls["Edit"].isEnabled()
    controls["Add"].click()
    assert asked[0].windowTitle() == "Add a Saga Source"
    assert [s.abbreviation for s in storage.load_saga(saga_id).sources] == ["HR"]
    # The page is drawn again at the same chapter, the one row chosen.
    assert _page(window).codex.rail.currentItem().text() == "Books"
    answering(window, {"title": "Our rules"})
    section_buttons(_page(window), "Saga Sources")["Edit"].click()
    assert storage.load_saga(saga_id).sources[0].title == "Our rules"
    saga = window.saga
    assert saga is not None
    hr.add(
        saga,
        hr.CHARACTER,
        {"name": "X", "type": "Virtue", "tier": "Minor", "source": "HR"},
    )
    answering(window)
    section_buttons(_page(window), "Saga Sources")["Delete"].click()
    assert [why for _title, why in window.told] == [
        "HR is cited by X: change them first."
    ]
    assert saga.sources


def test_a_saga_spell_is_added_and_deleted(app):
    window, saga_id = _content("Spells")
    answering(
        window,
        {
            "name": "Spark",
            "technique": "Creo",
            "form": "Ignem",
            "level": "5",
            "range": "Touch",
            "duration": "Momentary",
            "target": "Individual",
        },
    )
    section_buttons(_page(window), "Spells")["Add"].click()
    before = [s.name for s in storage.load_saga(saga_id).spells]
    assert "Spark" in before
    page = _page(window)
    page.spell_source.setCurrentIndex(page.spell_source.findData(spl.OWN_SOURCE))
    page.spell_search.setText("Spark")
    controls = section_buttons(page, "Spells")
    assert controls["Delete"].isEnabled()  # the only spell shown
    asked = answering(window, True)
    controls["Delete"].click()
    assert asked[0].question == "Delete Spark?"  # type: ignore[attr-defined]
    after = [s.name for s in storage.load_saga(saga_id).spells]
    assert after == [name for name in before if name != "Spark"]


def test_a_catalog_entry_is_hidden_by_catalog_then_entry(app):
    window, saga_id = _content("Catalogs")
    entry = scf.hideable(window.saga, "abilities")[0]
    label = plain(scf.entry_choice(entry).label)
    answering(window, {"catalog": "abilities"}, label)
    section_buttons(_page(window), "Hidden Entries")["Hide"].click()
    assert storage.load_saga(saga_id).hidden_entries == {"abilities": [entry.id]}
    asked = answering(window, True)
    section_buttons(_page(window), "Hidden Entries")["Offer again"].click()
    assert len(asked) == 1
    assert storage.load_saga(saga_id).hidden_entries == {}


def test_a_cult_its_degree_and_its_script_are_added(app):
    """The Mystery Cults chapter: Add a cult, a degree of it, then the
    degree's Script (Add on its Script, while it has none); Experiment on a
    Script is offered only for a degree with no Script."""
    window, saga_id = _content("Mystery Cults")
    answering(window, {"name": "The Thread", "lore": "Thread Lore"})
    section_buttons(_page(window), "The Saga's Mystery Cults")["Add"].click()
    assert [c.name for c in storage.load_saga(saga_id).custom_cults] == ["The Thread"]
    assert _page(window).codex.rail.currentItem().text() == "Mystery Cults"

    answering(window, {"name": "Spinner", "virtue_id": "vf_second_sight"})
    section_buttons(_page(window), "Degrees")["Add"].click()
    degrees = storage.load_saga(saga_id).custom_cults[0].degrees
    assert [(d.name, d.virtue_id) for d in degrees] == [("Spinner", "vf_second_sight")]
    controls = section_buttons(_page(window), "Degrees")
    assert "Experiment on a Script" in controls

    answering(window, {"name": "The Silk Hall", "place": True, "quests": 1})
    section_buttons(_page(window), "Spinner: no Script yet")["Add"].click()
    script = storage.load_saga(saga_id).custom_cults[0].degrees[0].script
    assert script is not None and (script.name, script.bonus) == ("The Silk Hall", 6)
    assert "The Silk Hall: +6" in [
        label.text() for label in _page(window).findChildren(QLabel)
    ]
