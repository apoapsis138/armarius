"""The Bestiary on the desktop: the saga page's chapter of creature
cards, its New card, and a creature's page with its Edit buttons and its
lists' Add, Edit and Delete, answered without showing the dialogs."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, buttons, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from support import everything_saga

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.bestiary import CreaturePage
from ars_magica_manager.gui.forms import ConfirmDialog
from ars_magica_manager.gui.menus import NewCard
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window() -> tuple[MainWindow, str]:
    saga = everything_saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    assert window.saga is not None
    return window, saga.id


def _page(window) -> CreaturePage:
    page = window.page()
    assert isinstance(page, CreaturePage)
    return page


def _saved(saga_id: str):
    return storage.load_saga(saga_id).creatures[0]


def _words(widget) -> str:
    return " ".join(label.text() for label in widget.findChildren(QLabel))


def test_the_bestiary_chapter_opens_a_creature_and_makes_one(app):
    window, saga_id = _window()
    page = window.page()
    assert page is not None
    page.codex.open_chapter("The Bestiary")  # type: ignore[attr-defined]
    [card] = [c for c in page.findChildren(ClickableCard) if "Aeolus" in _words(c)]
    assert "Magic Might 8 (Animal)" in _words(card)
    card.clicked()
    assert window.crumb_names()[-1] == "Aeolus"
    assert _page(window).chapters()[:4] == [
        "Traits",
        "Combat",
        "Powers & Vis",
        "Description",
    ]
    window.go(window.trail[:2])
    page = window.page()
    assert page is not None
    page.codex.open_chapter("The Bestiary")  # type: ignore[attr-defined]
    [new] = [c for c in page.findChildren(NewCard) if c.words == "New Creature"]
    answering(window, {"name": "Boglin", "size": "-2"})
    new.on_click()
    assert window.crumb_names()[-1] == "Boglin"
    made = [c for c in storage.load_saga(saga_id).creatures if c.name == "Boglin"]
    assert [c.size for c in made] == [-2]


def test_the_header_edits_the_creature_and_its_characteristics(app):
    window, saga_id = _window()
    window.open_creature("aeolus")
    answering(window, {"might": "10"})
    buttons(_page(window), "Edit")[0].click()
    assert _saved(saga_id).might == 10
    answering(window, {"strength": "5", "soak": "4"})
    buttons(_page(window), "Characteristics")[0].click()
    saved = _saved(saga_id)
    assert (saved.characteristics.strength, saved.soak) == (5, 4)


def test_an_attack_is_added_and_the_chosen_power_deleted(app):
    window, saga_id = _window()
    window.open_creature("aeolus")
    answering(window, {"name": "Bite", "damage": "3"})
    section_buttons(_page(window), "Combat")["Add"].click()
    assert [a.name for a in _saved(saga_id).attacks] == ["Kick", "Bite"]
    page = _page(window)
    page.codex.open_chapter("Powers & Vis")
    powers = section_buttons(page, "Powers")
    asked = answering(window, True)
    powers["Delete"].click()  # the only row needs no choosing
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Delete From Nag to Charger?"
    assert _saved(saga_id).powers == []
