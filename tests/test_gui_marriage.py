"""The desktop's Marriages chapter on a lord's page (Lords of Men pp.
10-11): after Manors, its marriages as ledger entries with End a Marriage
beside Add, Edit and Delete, and the terms of the one that stands, titled
for the couple (answered without showing the dialogs,
gui_steps.answering)."""

from __future__ import annotations

import html
import os
import re

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from test_marriage import _betrothal, _saga

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.region import LedgerRow
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _words(widget) -> str:
    return "\n".join(
        html.unescape(re.sub(r"<[^>]+>", "", label.text()))
        for label in widget.findChildren(QLabel)
    )


def test_the_marriages_chapter_lists_and_ends_a_marriage(app):
    saga = _saga()
    _betrothal(saga)
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_neighbour("jurgen")
    page = window.page()
    chapters = page.chapters()
    assert chapters.index("Marriages") == chapters.index("Manors") + 1
    page.codex.open_chapter("Marriages")
    chapter = page.codex.chapter(chapters.index("Marriages"))
    words = _words(chapter)
    assert "Karlotte and Wolfram: the Terms" in words
    assert "Karlotte Schönburg, 19, heiress" in words
    assert len(chapter.findChildren(LedgerRow)) == 1
    buttons = section_buttons(page, "Marriages")
    assert list(buttons) == ["Add", "Edit", "Delete", "End a Marriage"]
    chapter.findChildren(LedgerRow)[0].clicked()
    asked = answering(window, {"how": "part"}, None)
    section_buttons(window.page(), "Marriages")["End a Marriage"].click()
    assert isinstance(asked[0], FieldsDialog)
    assert storage.load_saga(saga.id).marriages[0].ended == "part"
