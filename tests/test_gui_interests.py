"""The Interests window on the desktop: the form's ticks as cards beside
an inspector."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ars_magica_manager import action_books, deeds
from ars_magica_manager.forms import interests
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import CardsDialog, answer, step_dialog
from ars_magica_manager.gui.themes import PALETTES
from ars_magica_manager.models import Character


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _open(monkeypatch, off=(), books=("LoM",)) -> tuple:
    def allowed(action, _saga):
        needs = action_books.ACTION_BOOKS.get(action)
        return needs is None or bool(set(needs) & set(books))

    monkeypatch.setattr(interests.action_books, "book_allows", allowed)
    character = Character.from_dict({"id": "k", "name": "K", "type": "grog"})
    character.interests_off = list(off)
    form = interests.interests_form(None, character)
    dialog = step_dialog(form, PALETTES[0], None)
    assert isinstance(dialog, CardsDialog)
    return form, dialog, character


def test_a_card_for_every_interest_and_the_first_in_the_inspector(app, monkeypatch):
    _form, dialog, _c = _open(monkeypatch)
    assert list(dialog.cards) == list(deeds.INTERESTS)
    assert dialog.inspector.title.text() == deeds.SESSION
    assert deeds.SESSION not in dialog.switches


def test_clicking_a_card_shows_it_in_the_inspector(app, monkeypatch):
    _form, dialog, _c = _open(monkeypatch)
    dialog.cards[deeds.KNIGHTLY].clicked()
    assert dialog.inspector.title.text() == deeds.KNIGHTLY
    assert "Melee Event" in dialog.inspector.body.text()


def test_either_switch_turns_an_interest_off_and_both_follow(app, monkeypatch):
    form, dialog, character = _open(monkeypatch)
    dialog.cards[deeds.KNIGHTLY].clicked()
    dialog.inspector.action.click()
    assert not dialog.switches[deeds.KNIGHTLY].isChecked()
    dialog.switches[deeds.KNIGHTLY].click()
    assert dialog.inspector.action.isChecked()
    dialog.switches[deeds.KNIGHTLY].click()
    assert not dialog.inspector.action.isChecked()
    answer(form, dialog)
    assert character.interests_off == [deeds.KNIGHTLY]


def test_a_card_with_no_book_is_locked_and_keeps_the_choice(app, monkeypatch):
    form, dialog, character = _open(monkeypatch, off=[deeds.FAERIE])
    for name in (deeds.FAERIE, deeds.INFERNAL):
        assert not dialog.switches[name].isEnabled()
        assert not dialog.switches[name].isChecked()
    answer(form, dialog)
    assert character.interests_off == [deeds.FAERIE]
