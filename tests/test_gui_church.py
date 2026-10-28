"""The desktop's Religion chapter (The Church pp. 33-38, 46-48; RoP: The
Divine): after Virtues & Flaws while the faiths' books are in play, or for
one with a Church career; Faith with Edit Religion and the faith's
actions (no longer on Personality Traits); Holy Orders' facts and
buttons; ordinations, petitions and cases as ledger entries, the chosen
one in the inspector; and a first petition added on Petitions (answered
without showing the dialogs, gui_steps.answering)."""

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


def _window(
    *, cleric: bool = True, books: list[str] | None = None
) -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    if books is not None:
        saga.books_in_play = books
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


def test_the_religion_chapter_follows_virtues_and_flaws(app):
    window, _ = _window(cleric=False)
    chapters = _page(window).chapters()
    assert chapters.index("Religion") == chapters.index("Virtues & Flaws") + 1
    assert "Church" not in chapters


def test_without_the_books_of_the_faiths_only_a_cleric_has_it(app):
    window, _ = _window(cleric=False, books=["HoH:S"])
    assert "Religion" not in _page(window).chapters()
    window, _ = _window(books=["HoH:S"])
    assert "Religion" in _page(window).chapters()


def test_holy_orders_and_the_ledgers(app):
    window, _ = _window()
    page = _page(window)
    page.open_chapter("Religion")
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


def test_the_faith_actions_are_in_faith_not_on_personality_traits(app):
    window, _ = _window(cleric=False)
    page = _page(window)
    faith = list(section_buttons(page, "Faith"))
    assert faith[0] == "Edit Religion"
    assert "Invoke a Saint" in faith
    traits = section_buttons(page, "Personality Traits")
    for moved in ("Invoke a Saint", "Petition the Church", "Holy Orders"):
        assert moved not in traits
    # A layman has no Holy Orders until he takes a clerical status.
    assert "Holy Orders" not in _words(page)


def test_a_first_petition_is_added_on_petitions(app):
    window, saga_id = _window(cleric=False)
    page = _page(window)
    asked = answering(
        window,
        {"ask": "A marriage blessing", "example": "A marriage blessing"},
    )
    section_buttons(page, "Petitions")["Add"].click()
    assert len(asked) == 1
    saved = storage.load_saga(saga_id).characters[0].church.petitions
    assert [p.ask for p in saved] == ["A marriage blessing"]
