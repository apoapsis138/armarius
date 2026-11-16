"""A printed sheet drawn to a PDF by the desktop's renderer: the paper
chosen, text rather than pictures, and a size that stays small."""

from __future__ import annotations

import os
import re
from copy import deepcopy

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import print_layout as pl
from ars_magica_manager import print_records as pr
from ars_magica_manager.gui.print_sheet import print_book, print_document
from ars_magica_manager.pdf_outline import outline_titles
from ars_magica_manager.viewing import STORYGUIDE_VIEWER


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
    # Combat & Condition running on to the Virtues and Flaws, the Hermetic
    # page (on the Virtues' page where A4's taller page leaves room), the
    # story, the Grimoire.
    assert pages == (5 if paper == pl.LETTER else 4)
    assert _media_boxes(data) == {size}
    # Real text in embedded fonts, not a picture of the screen.
    assert b"/FontFile" in data
    assert len(data) < 1_000_000


def test_a_play_sheet_is_two_pages_for_a_magus_one_for_a_companion(app, tmp_path):
    saga = _sample_saga_with_covenant()
    options = pl.PrintOptions(sheet=pl.PLAY_SHEET)
    character = saga.characters[0]
    doc = pl.character_document(saga, character, options)
    assert print_document(doc, tmp_path / "magus.pdf", options) == 2
    character.type = "companion"
    doc = pl.character_document(saga, character, options)
    assert print_document(doc, tmp_path / "companion.pdf", options) == 1


def test_the_troupe_prints_as_one_pdf_with_a_bookmark_each(app, tmp_path):
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    magus.background.player = "Pat"
    companion = deepcopy(magus)
    companion.id, companion.name, companion.type = "char2", "Dammër Wulf", "companion"
    saga.characters.append(companion)
    options = pl.PrintOptions(sheet=pl.PLAY_SHEET)
    sheets = pr.troupe_sheets(saga, options, STORYGUIDE_VIEWER)
    assert [doc.title for doc, _ in sheets] == ["Leandro", "Dammër Wulf"]
    path = tmp_path / "troupe.pdf"
    starts = print_book("The Troupe", sheets, path, options)
    # Each from a fresh page: the magus's play sheet is two.
    assert starts == [0, 2]
    assert outline_titles(path) == ["Leandro", "Dammër Wulf"]
    assert path.read_bytes().rstrip().endswith(b"%%EOF")


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
