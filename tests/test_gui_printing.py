"""Print to PDF from a record's Manage chapter: its options, then where to
save it; a character prints as a sheet laid out for paper, other records
as their page in the parchment palette."""

from __future__ import annotations

import os
import re

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtWidgets import QApplication, QFileDialog, QPushButton
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import settings, storage
from ars_magica_manager.gui import printing
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _manage_button(window: MainWindow, words: str) -> QPushButton:
    page = window.page()
    assert page is not None
    page.codex.open_chapter("Manage")  # type: ignore[attr-defined]
    return next(b for b in page.findChildren(QPushButton) if b.text().strip() == words)


def test_manage_prints_the_record_to_a_pdf(app, tmp_path):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show_character("char1")
    target = tmp_path / "Leandro.pdf"
    asked = answering(window, {"paper": "A4", "background": "white"}, target)
    _manage_button(window, "Print to PDF").click()
    assert isinstance(asked[0], FieldsDialog)
    assert isinstance(asked[1], QFileDialog)
    assert asked[1].acceptMode() == QFileDialog.AcceptMode.AcceptSave
    data = target.read_bytes()
    assert data.startswith(b"%PDF")
    (box,) = set(re.findall(rb"/MediaBox \[\s*0 0 ([\d.]+) ([\d.]+)\s*\]", data))
    assert tuple(round(float(n)) for n in box) == (595, 842)  # A4
    assert window.told and "saved to" in window.told[0][1]
    # The choices are kept for next time.
    kept = settings.load_settings()["print_options"]
    assert kept == {"paper": "A4", "spells": "short", "background": "white"}


def test_a_covenant_is_asked_only_its_paper(app, tmp_path):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant("cov1")
    target = tmp_path / "cov.pdf"
    asked = answering(window, {"paper": "Letter"}, target)
    _manage_button(window, "Print to PDF").click()
    assert isinstance(asked[0], FieldsDialog)
    assert [f.key for f in asked[0].fields] == ["paper"]
    assert target.read_bytes().startswith(b"%PDF")
    # The window goes back to its own colours.
    assert window._printing is None


def test_a_covenant_prints_every_chapter_but_manage_and_seasons(app, tmp_path):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant("cov1")
    pages = window.print_to(tmp_path / "cov.pdf", "Test Covenant")
    assert int(pages[0].split()[0]) >= 3


def test_breaks_keep_a_section_title_with_what_is_under_it():
    breaks = printing._Breaks(tops=[100, 300, 520, 560, 900], sections=[520])
    # 600 of room from 0 would cut at 560, just under the title at 520.
    assert breaks.cut(0, 600) == 520
    assert breaks.cut(0, 1000) == 900


def test_file_names_lose_what_windows_refuses():
    assert printing.file_stem('Leandro: "the Red"?') == "Leandro the Red"
    assert printing.file_stem("///") == "Untitled"
