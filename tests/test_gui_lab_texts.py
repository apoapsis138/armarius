"""A laboratory's Lab Texts on the desktop: listed for the lab's owner,
narrowed by the filter bar (the terminal's / filter), which the page keeps
when it is drawn again, with Add making a Lab Text."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QTableView
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.laboratory import LaboratoryPage
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Book
from ars_magica_manager.models.books import TEXT_OTHER


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _lab_page(window: MainWindow) -> LaboratoryPage:
    page = window.page()
    assert isinstance(page, LaboratoryPage)
    return page


def _texts(page: LaboratoryPage) -> list[str]:
    """The Lab Texts table's rows, each its cells joined by spaces."""
    holder = page.lab_text_filter.parentWidget()
    assert holder is not None
    found = holder.findChild(QTableView)
    if found is None:
        return []
    model = found.model()
    return [
        " ".join(str(model.index(r, c).data()) for c in range(model.columnCount()))
        for r in range(model.rowCount())
    ]


def test_lab_texts_are_filtered_and_the_filter_is_kept(app):
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    for name, spell in (("Lamp", "Lamp Without Flame"), ("Notes", "")):
        saga.books.append(
            Book(
                id=name.lower(),
                name=f"Lab Text: {name}",
                type="Lab Text",
                spell_name=spell,
                level=10,
                owner_kind="laboratory",
                owner_id=lab.id,
            )
        )
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_laboratory(lab.id)
    page = _lab_page(window)
    page.codex.open_chapter("Stores")
    assert len(_texts(page)) == 2
    bar = page.lab_text_filter
    bar.kind.setCurrentIndex(bar.kind.findData("Spell"))
    assert [row.split()[0] for row in _texts(page)] == ["Lamp"]
    # Adding a text draws the page again: the filter stays.
    asked = answering(
        window, {"name": "Lab Text: Ward", "text_kind": TEXT_OTHER, "level": "15"}
    )
    section_buttons(page, "Lab Texts")["Add"].click()
    assert isinstance(asked[0], FieldsDialog)
    saved = storage.load_saga(saga.id)
    added = next(b for b in saved.books if b.name == "Lab Text: Ward")
    assert added.type == "Lab Text"
    page = _lab_page(window)
    assert page.lab_text_filter.wanted().kind == "Spell"
