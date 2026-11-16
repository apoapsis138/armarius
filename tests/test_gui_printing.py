"""Print to PDF from a record's Manage chapter: its options, then where to
save it; every kind prints as a sheet laid out for paper
(print_records.py)."""

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
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Familiar


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
    assert kept == {
        "paper": "A4",
        "sheet": "full",
        "background": "white",
        "theme": "house",
    }


def test_a_covenant_is_asked_its_copy_paper_and_background(app, tmp_path):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant("cov1")
    target = tmp_path / "cov.pdf"
    asked = answering(window, {"paper": "Letter"}, target)
    _manage_button(window, "Print to PDF").click()
    assert isinstance(asked[0], FieldsDialog)
    assert [f.key for f in asked[0].fields] == [
        "copy",
        "paper",
        "theme",
        "background",
    ]
    assert target.read_bytes().startswith(b"%PDF")


@pytest.mark.parametrize(
    ("open_it", "name"),
    [
        (lambda w: w.open_covenant("cov1"), "cov"),
        (lambda w: w.open_laboratory("lab1"), "lab"),
        (lambda w: w.open_familiar("fam1"), "familiar"),
    ],
)
def test_each_kind_prints_as_a_laid_out_sheet(app, tmp_path, open_it, name):
    saga = _sample_saga_with_covenant()
    saga.familiars.append(Familiar(id="fam1", character_id="char1", name="Ashwing"))
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    open_it(window)
    said = window.print_to(tmp_path / f"{name}.pdf")
    assert "saved to" in said[0]
    data = (tmp_path / f"{name}.pdf").read_bytes()
    # Real text in embedded fonts, not a picture of the screen.
    assert b"/FontFile" in data
