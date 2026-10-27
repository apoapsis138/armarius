"""The desktop's Church chapter (The Church pp. 33-38, 46-48): there only
for a character with a grade, a petition or a canon case; Holy Orders'
facts and buttons; ordinations, petitions and cases as ledger entries,
the chosen one in the inspector; and a first petition, made from the
Personality Traits' buttons, bringing the chapter (answered without showing the
dialogs, gui_steps.answering)."""

from __future__ import annotations

import html
import os
import re

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.church import LedgerEntry
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import CanonCase, Ordination, Petition


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


def _window(*, cleric: bool = True) -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    character = saga.characters[0]
    if cleric:
        church = character.church
        church.grade, church.diocese = "Lector", "Konstanz"
        church.ordinations = [
            Ordination(
                "Doorkeeper",
                "Spring",
                1205,
                "Church Lore",
                1,
                1,
                7,
                False,
                3,
                "learned",
            )
        ]
        church.petitions = [
            Petition("Access to the crypt", ease=6, characteristic=3, lore=3)
        ]
        church.cases = [CanonCase("Slander", "the miller", role="accuser")]
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show_character(character.id)
    return window, saga.id


def _page(window: MainWindow) -> CharacterSheet:
    page = window.page()
    assert isinstance(page, CharacterSheet)
    return page


def test_the_church_chapter_follows_agents_only_for_a_cleric(app):
    window, _ = _window(cleric=False)
    assert "Church" not in _page(window).chapters()
    window, _ = _window()
    chapters = _page(window).chapters()
    assert chapters.index("Church") == chapters.index("Agents") + 1


def test_holy_orders_and_the_ledgers(app):
    window, _ = _window()
    page = _page(window)
    page.open_chapter("Church")
    shown = _words(page)
    assert "Lector (minor orders)" in shown
    assert "Konstanz" in shown
    assert "Next: Exorcist" in shown
    assert list(section_buttons(page, "Holy Orders")) == [
        "Edit Holy Orders",
        "Perform an Exorcism",
    ]
    assert list(section_buttons(page, "Petitions")) == ["Add", "Edit", "Delete"]
    entries = page.findChildren(LedgerEntry)
    assert len(entries) == 3
    entries[1].clicked()
    assert "Access to the crypt" in _words(page.inspector)
    assert entries[1].chosen and not entries[0].chosen


def test_a_first_petition_brings_the_chapter(app):
    window, saga_id = _window(cleric=False)
    page = _page(window)
    asked = answering(
        window,
        {"ask": "A marriage blessing", "example": "A marriage blessing"},
    )
    section_buttons(page, "Personality Traits")["Petition the Church"].click()
    assert len(asked) == 1
    saved = storage.load_saga(saga_id).characters[0].church.petitions
    assert [p.ask for p in saved] == ["A marriage blessing"]
    assert "Church" in _page(window).chapters()
