"""A printed sheet drawn to a PDF by the desktop's renderer: the paper
chosen, text rather than pictures, and a size that stays small."""

from __future__ import annotations

import os
import re

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import print_layout as pl
from ars_magica_manager.gui.print_sheet import print_document


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _media_boxes(data: bytes) -> set[tuple[int, int]]:
    boxes = re.findall(rb"/MediaBox \[\s*0 0 ([\d.]+) ([\d.]+)\s*\]", data)
    return {(round(float(w)), round(float(h))) for w, h in boxes}


@pytest.mark.parametrize(
    ("paper", "size"), [(pl.LETTER, (612, 792)), (pl.A4, (595, 842))]
)
def test_a_magus_prints_on_the_paper_chosen(app, tmp_path, paper, size):
    saga = _sample_saga_with_covenant()
    options = pl.PrintOptions(paper=paper)
    path = tmp_path / "Leandro.pdf"
    pages = print_document(
        pl.character_document(saga, saga.characters[0], options), path, options
    )
    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    # The sheet, Combat & Condition, the Arts, the Grimoire, the story.
    assert pages == 5
    assert _media_boxes(data) == {size}
    # Real text in embedded fonts, not a picture of the screen.
    assert b"/FontFile" in data
    assert len(data) < 1_000_000


def test_full_spells_print_too(app, tmp_path):
    saga = _sample_saga_with_covenant()
    options = pl.PrintOptions(full_spells=True)
    path = tmp_path / "Leandro.pdf"
    doc = pl.character_document(saga, saga.characters[0], options)
    assert print_document(doc, path, options) >= 5


def test_without_texture_the_pages_are_plain_white(app, tmp_path):
    saga = _sample_saga_with_covenant()
    sizes = {}
    for textured in (True, False):
        options = pl.PrintOptions(textured=textured)
        path = tmp_path / f"{textured}.pdf"
        doc = pl.character_document(saga, saga.characters[0], options)
        print_document(doc, path, options)
        sizes[textured] = len(path.read_bytes())
    # The parchment is a picture on every page; white paper has none.
    assert sizes[False] < sizes[True]
