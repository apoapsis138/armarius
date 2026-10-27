"""The desktop covenant's Ships, first in its Possessions: each ship a
ledger entry with her damage as a badge, the chosen one in the inspector,
and Add, Stress Check and Ship Combat as the Ships section's buttons
(answered without showing the dialogs, gui_steps.answering)."""

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
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.markup_html import plain
from ars_magica_manager.gui.ships import ShipEntry
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Possession, Ship


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window() -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    saga.covenants[0].possessions.append(
        Possession(
            id="grauwal",
            kind="ship",
            name="Grauwal",
            description="Aelfhere's best work.",
            ship=Ship(
                ship_type="buss",
                kind_name="Small cog",
                quality="Excellent",
                damage_lost=1,
            ),
        )
    )
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant("cov1")
    return window, saga.id


def _page(window: MainWindow) -> CovenantPage:
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("Possessions")
    return page


def _words(widget) -> str:
    return "\n".join(
        html.unescape(re.sub(r"<[^>]+>", "", label.text()))
        for label in widget.findChildren(QLabel)
    )


def _chapter(page: CovenantPage):
    return page.codex.chapter(page.codex.chapters().index("Possessions"))


def test_ships_come_first_in_possessions_as_ledger_entries(app):
    window, _ = _window()
    page = _page(window)
    chapter = _chapter(page)
    words = _words(chapter)
    assert words.index("Ships (1)") < words.index("Properties and Land")
    assert "7 of 8 damage" in words
    assert "Excellent; crew 8; captain (none)." in words
    entries = chapter.findChildren(ShipEntry)
    assert len(entries) == 1
    buttons = section_buttons(page, "Ships")
    assert list(buttons) == ["Add", "Edit", "Delete", "Stress Check", "Ship Combat"]
    entries[0].clicked()
    assert page.inspector.title.text() == "Grauwal"
    body = plain(page.inspector.body.text())
    assert "+2 to navigation and ship-handling rolls" in body
    assert buttons["Stress Check"].isEnabled()


def test_a_stress_check_from_the_desktop_writes_its_damage(app):
    window, saga_id = _window()
    page = _page(window)
    _chapter(page).findChildren(ShipEntry)[0].clicked()
    asked = answering(window, {"weather": "severe"})
    section_buttons(page, "Ships")["Stress Check"].click()
    assert [type(d) for d in asked] == [FieldsDialog]
    covenant = storage.load_saga(saga_id).covenants[0]
    assert covenant.diary[-1].name == "Stress Check: Grauwal"


def test_add_a_ship_from_the_desktop(app):
    window, saga_id = _window()
    page = _page(window)
    asked = answering(window, {"name": "Möwe", "kind_name": "Knarr"})
    section_buttons(page, "Ships")["Add"].click()
    assert [type(d) for d in asked] == [FieldsDialog]
    ships = [
        p.name
        for p in storage.load_saga(saga_id).covenants[0].possessions
        if p.kind == "ship"
    ]
    assert ships == ["Grauwal", "Möwe"]
