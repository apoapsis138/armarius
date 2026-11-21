"""The desktop's written Handouts: Saga Content's Handouts chapter, its
table narrowed to one Story by the choice above it (handouts.py)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QTableView

from ars_magica_manager import handouts
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.saga_content import SagaContentPage
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.models import (
    STORY_EVENT,
    Covenant,
    CovenantDiaryEntry,
    Handout,
    Saga,
)


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _saga() -> Saga:
    saga = Saga(id="handout-gui", name="Fengheld")
    saga.covenants = [Covenant(id="c", saga_id=saga.id, name="Fengheld")]
    saga.covenants[0].diary = [
        CovenantDiaryEntry(
            1220, name="The Black Tower", category=STORY_EVENT, status="Open", id="st1"
        )
    ]
    saga.handouts = [
        Handout("h1", title="Of nothing"),
        Handout("h2", title="Of the tower", story_id="st1"),
    ]
    return saga


def _titles(page: SagaContentPage) -> list[str]:
    """The Handouts table's titles (the table whose second column is the
    Stationery)."""
    found = []
    for view in page.findChildren(QTableView):
        model = view.model()
        if model.headerData(1, Qt.Orientation.Horizontal) != "Stationery":
            continue
        found += [model.index(row, 0).data() for row in range(model.rowCount())]
    return found


def test_the_story_choice_narrows_the_handouts_table(app: QApplication) -> None:
    saga = _saga()
    page = SagaContentPage(saga, SCRIPTORUM)
    page.codex.open_chapter("Handouts")
    assert _titles(page) == ["Of nothing", "Of the tower"]
    (choice,) = [
        c for c in page.findChildren(QComboBox) if c.itemText(0) == "Every story"
    ]
    try:
        choice.setCurrentIndex(choice.findData("st1"))
        assert handouts.current_story(saga) == "st1"
        assert _titles(page) == ["Of the tower"]
        choice.setCurrentIndex(0)
        assert _titles(page) == ["Of nothing", "Of the tower"]
    finally:
        handouts.choose_story(saga, "")
