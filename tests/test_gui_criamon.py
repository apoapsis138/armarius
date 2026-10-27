"""The desktop's The Enigma chapter (Houses of Hermes: Mystery Cults pp.
50-73): there only for a Criamon magus, after Hermetic Magic; the path's
facts and buttons; the stations and stigmata as ledger entries, the
chosen one in the inspector; and Follow an Avenue planning the season
(answered without showing the dialog, gui_steps.answering)."""

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
from ars_magica_manager.models import Ability, Stigma, VirtueFlawInstance


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


def _window(*, criamon: bool = True) -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    if criamon:
        magus.hermetic.house = "house_criamon"
        magus.virtues_flaws += [
            VirtueFlawInstance("vf_the_enigma"),
            VirtueFlawInstance("vf_station_of_differentiation_of_seeming"),
        ]
        magus.abilities.append(Ability("Mystery Cult Lore: Criamon", xp=50))
        magus.enigma.stigmata = [Stigma("Eyelids", "A spiral", "station")]
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show_character(magus.id)
    return window, saga.id


def _page(window: MainWindow) -> CharacterSheet:
    page = window.page()
    assert isinstance(page, CharacterSheet)
    return page


def test_the_enigma_follows_hermetic_magic_only_for_a_criamon(app):
    window, _ = _window(criamon=False)
    assert "The Enigma" not in _page(window).chapters()
    window, _ = _window()
    chapters = _page(window).chapters()
    assert chapters.index("The Enigma") == chapters.index("Hermetic Magic") + 1


def test_the_path_stations_and_stigmata(app):
    window, _ = _window()
    page = _page(window)
    page.open_chapter("The Enigma")
    shown = _words(page)
    assert "of Seeming" in shown
    assert "True Sight" in shown
    # With no guide named, the House provides one (HoH:MC p. 60).
    assert "a guide the House provides" in shown
    assert list(section_buttons(page, "The Path of Seeming")) == [
        "Change Path",
        "Follow an Avenue",
    ]
    assert list(section_buttons(page, "Stigmata")) == ["Add", "Edit", "Delete"]
    entries = page.findChildren(LedgerEntry)
    assert len(entries) == 6  # five stations, one stigma
    entries[1].clicked()
    assert "Assaults the Modesty" in _words(page.inspector)
    entries[5].clicked()
    assert "Int + Enigmatic Wisdom against 6" in _words(page.inspector)


def test_follow_an_avenue_plans_the_season(app):
    window, saga_id = _window()
    page = _page(window)
    page.open_chapter("The Enigma")
    asked = answering(window, {"guide": "primus", "season": "Winter"})
    section_buttons(page, "The Path of Seeming")["Follow an Avenue"].click()
    assert len(asked) == 1
    plans = storage.load_saga(saga_id).season_plans
    assert [(p.season, p.effect_id) for p in plans] == [
        ("Winter", "vf_station_of_true_sight")
    ]
