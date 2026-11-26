"""Any Handout printed to a PDF on the desktop (gui.handout_print): a
written one on its Stationery, a record's copy and a picture on the
printed sheet's page; real text, on the paper chosen, pages broken
between blocks."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QPushButton,
)
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import markdown_sheet, shows
from ars_magica_manager import print_handouts as ph
from ars_magica_manager import print_layout as pl
from ars_magica_manager.forms import printing
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.gui.chronicle_pane import ShownCopy, ShownPicture
from ars_magica_manager.gui.forms import (
    Ask,
    FieldsDialog,
    NoticeDialog,
    offer_pdf,
    step_dialog,
)
from ars_magica_manager.gui.handout_print import StationerySheet, print_handout
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.models import PROCLAMATION, SEALED_LETTER, VELLUM
from ars_magica_manager.shows import WITHDRAWN_NOTE


@pytest.fixture(scope="module")
def app() -> QCoreApplication:
    return QApplication.instance() or QApplication([])


def _png(folder: Path, width: int = 300, height: int = 200) -> bytes:
    """A picture's bytes, as a Show's copy holds them."""
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor("#7a5c3c"))
    path = folder / f"{width}x{height}.png"
    image.save(str(path))
    return path.read_bytes()


LETTER = """[heading] To the Abbot
[centre] Greetings from the Chapter
[initial] Know that the **bridge** at Cologne is down, and the road with it.

[flourish]
[picture 1]
[right] Given at Cologne, in the year of Our Lord 1220"""


def _media_boxes(data: bytes) -> set[tuple[int, int]]:
    boxes = re.findall(rb"/MediaBox \[\s*0 0 ([\d.]+) ([\d.]+)\s*\]", data)
    return {(round(float(w)), round(float(h))) for w, h in boxes}


@pytest.mark.parametrize("stationery", [VELLUM, SEALED_LETTER, PROCLAMATION])
@pytest.mark.parametrize(
    ("paper", "size"), [(pl.LETTER, (612, 792)), (pl.A4, (595, 842))]
)
def test_a_written_handout_prints_on_its_stationery(
    app: QCoreApplication,
    tmp_path: Path,
    stationery: str,
    paper: str,
    size: tuple[int, int],
) -> None:
    pictures = (_png(tmp_path),)
    shown = shows.Shown("A letter", LETTER, stationery=stationery, pictures=pictures)
    path = tmp_path / "letter.pdf"

    pages = print_handout(ph.document(shown), path, pl.PrintOptions(paper=paper))

    data = path.read_bytes()
    assert pages == 1
    assert _media_boxes(data) == {size}
    # Its words are real text, not a picture of the window.
    assert b"/FontFile" in data
    assert len(data) < 3_000_000


def test_a_long_written_handout_runs_on_sealed_on_its_last_page(
    app: QCoreApplication, tmp_path: Path
) -> None:
    words = "\n\n".join(
        f"[initial] Item {n}: the brothers of the house ask that " + "word " * 120
        for n in range(12)
    )
    shown = shows.Shown("A long letter", words, stationery=SEALED_LETTER)
    doc = ph.document(shown)
    sheet = StationerySheet(tmp_path / "long.pdf", doc, pl.DEFAULT_OPTIONS)

    pages = sheet.print()

    assert pages > 1
    # Every page drawn on its Stationery; only the last carries the seal.
    assert set(sheet._grounds) == {False, True}


def test_a_passage_is_never_split_between_pages(
    app: QCoreApplication, tmp_path: Path
) -> None:
    words = "\n\n".join("word " * 90 for _ in range(10))
    doc = ph.document(shows.Shown("Words", words, stationery=VELLUM))
    sheet = StationerySheet(tmp_path / "w.pdf", doc, pl.DEFAULT_OPTIONS)

    pages = pl.paginate(sheet.pieces(), sheet.height)

    assert len(pages) > 1
    for page in pages:
        for place in page:
            # A whole block on each page: no part of a split one.
            assert place.first == place.last == 0 and not place.spans


def test_a_paragraph_longer_than_a_page_runs_on_between_its_lines(
    app: QCoreApplication, tmp_path: Path
) -> None:
    doc = ph.document(shows.Shown("Long", "word " * 4000, stationery=SEALED_LETTER))
    sheet = StationerySheet(tmp_path / "w.pdf", doc, pl.DEFAULT_OPTIONS)
    pieces = sheet.pieces()

    pages = pl.paginate(pieces, sheet.height)

    assert len(pages) > 2
    for page in pages:
        for place in page:
            piece = pieces[place.index]
            tall = (
                sum(piece.rows[place.first : place.last])
                if place.last
                else piece.height
            )
            # Nothing runs past the foot of the page, over the seal.
            assert place.top + tall <= sheet.height + 0.01
    assert sheet.print() == len(pages)


def test_a_picture_handout_prints_the_picture_under_its_title(
    app: QCoreApplication, tmp_path: Path
) -> None:
    picture = _png(tmp_path, 1600, 1200)
    shown = shows.Shown("The map", picture=picture, picture_name="ab.png")
    path = tmp_path / "map.pdf"

    pages = print_handout(ph.document(shown), path)

    assert pages == 1
    assert b"/Image" in path.read_bytes()


def test_a_picture_not_to_hand_prints_a_box_naming_it(
    app: QCoreApplication, tmp_path: Path
) -> None:
    shown = shows.Shown("A", "[picture 1]", stationery=VELLUM, pictures=(None,))

    assert print_handout(ph.document(shown), tmp_path / "a.pdf") == 1


def _save_with(target: Path, paper: str, told: list[str]) -> Ask:
    """An `ask` that chooses `paper`, saves to `target`, and notes what the
    window it ends on says."""

    def ask(dialog: QDialog) -> int:
        if isinstance(dialog, FieldsDialog):
            combo = dialog.inputs["paper"]
            assert isinstance(combo, QComboBox)
            combo.setCurrentIndex(combo.findData(paper))
            dialog.try_save()
            return dialog.result()
        if isinstance(dialog, QFileDialog):
            dialog.selectFile(str(target))
            return QDialog.DialogCode.Accepted
        assert isinstance(dialog, NoticeDialog)
        told.append(dialog.words)
        return QDialog.DialogCode.Accepted

    return ask


@pytest.mark.parametrize(
    "shown",
    [
        shows.Shown("A letter", LETTER, stationery=VELLUM, pictures=(None,)),
        shows.Shown("Hilda", "# Hilda\n\n*A grog*\n\nShe guards the gate."),
        shows.Shown("The map", picture=b"not a picture"),
    ],
    ids=["written", "record", "picture"],
)
def test_save_as_pdf_from_an_opened_handout_asks_the_paper_then_where(
    app: QCoreApplication, tmp_path: Path, shown: shows.Shown
) -> None:
    target = tmp_path / "kept.pdf"
    told: list[str] = []
    ask = _save_with(target, pl.A4, told)
    window = step_dialog(show_forms.copy_form(shown), SCRIPTORUM, None, ask=ask)
    assert window is not None
    button = window.findChild(QPushButton, "save-pdf")
    assert isinstance(button, QPushButton)

    button.click()

    assert _media_boxes(target.read_bytes()) == {(595, 842)}
    assert told == [f"1 page saved to {target}."]
    # The paper is kept for next time; nothing else is asked.
    assert printing.saved_options().paper == pl.A4


def test_a_show_withdrawn_while_saving_is_not_saved(
    app: QCoreApplication, tmp_path: Path
) -> None:
    target = tmp_path / "kept.pdf"
    told: list[str] = []
    shown = shows.Shown("Hilda", "# Hilda\n\nWords.")
    window = ShownCopy(shown)
    held = [True]

    def ask(dialog: QDialog) -> int:
        held[0] = False  # withdrawn while the paper is asked
        return _save_with(target, pl.LETTER, told)(dialog)

    button = offer_pdf(
        window,
        window.buttons_row,
        lambda: ph.document(shown),
        SCRIPTORUM,
        ask,
        still=lambda: held[0],
    )
    button.click()

    assert not target.exists()
    assert told == [WITHDRAWN_NOTE]


def test_a_handout_shown_in_the_chronicle_offers_save_as_pdf(
    app: QCoreApplication,
) -> None:
    for window in (
        ShownPicture(shows.Shown("Map", picture=b"x")),
        ShownCopy(shows.Shown("Hilda", "# Hilda")),
    ):
        offer_pdf(window, window.buttons_row, lambda: pl.Document("x", ""), SCRIPTORUM)
        assert window.findChild(QPushButton, "save-pdf") is not None


def test_a_record_copy_prints_on_the_printed_sheet(
    app: QCoreApplication, tmp_path: Path
) -> None:
    saga = _sample_saga_with_covenant()
    words = markdown_sheet.render(pl.character_document(saga, saga.characters[0]))
    path = tmp_path / "leandro.pdf"

    pages = print_handout(ph.document(shows.Shown("Leandro", words)), path)

    assert pages >= 2
    assert b"/FontFile" in path.read_bytes()
