"""The saga page's Saga Settings chapter: sections of cards, a switch that
changes the saga at once, and the inspector that explains a card."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, buttons
from PySide6.QtWidgets import QApplication, QLabel, QListWidget
from support import everything_saga

from ars_magica_manager import medallions, ruling_templates, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.medallions import Medallion
from ars_magica_manager.gui.widgets import ClickableCard, TitledRows, ToggleSwitch
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.rules import options as rule_options


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _open() -> MainWindow:
    saga = everything_saga()
    saga.books_in_play = None
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_saga(saga.id)
    window.page().codex.open_chapter("Saga Settings")  # type: ignore[union-attr]
    return window


def _cards(window: MainWindow) -> dict[str, ClickableCard]:
    return window.page().settings.cards  # type: ignore[union-attr]


def _inspector_words(window: MainWindow) -> str:
    inspector = window.page().codex.inspector  # type: ignore[union-attr]
    return " ".join(label.text() for label in inspector.findChildren(QLabel))


def test_the_chapter_has_its_sections_and_edit_saga(app):
    window = _open()
    area = window.page().codex.pages.currentWidget()  # type: ignore[union-attr]
    column = area.widget().layout()
    parts = [column.itemAt(i).widget() for i in range(column.count())]
    firsts = [w.findChild(QLabel) for w in parts if w is not None]
    words = [label.text().casefold() for label in firsts if label is not None]
    headings = ("Saga Details", "Seasons", "Content in Play", "Optional Rules")
    assert [
        w for w in words if w in {h.casefold() for h in (*headings, "Tribunal")}
    ] == [h.casefold() for h in (*headings, "Tribunal")]
    assert buttons(window.page(), "Edit Saga")
    # Content in Play's card opens Saga Content.
    window.page().content.clicked()  # type: ignore[union-attr]
    assert window.crumb_names()[-1] == "Saga Content"


def test_edit_saga_asks_only_the_details(app):
    window = _open()
    saga = window.saga
    assert saga is not None
    answering(window, {"name": "Renamed", "storyguide": "Alex"})
    buttons(window.page(), "Edit Saga")[0].click()
    assert saga.name == "Renamed"


def test_clicking_a_card_shows_it_in_full_in_the_inspector(app):
    window = _open()
    _cards(window)["bruises"].clicked()
    assert "heals within hours" in _inspector_words(window)


def test_a_switch_saves_at_once_and_the_card_stays_in_the_inspector(app):
    window = _open()
    saga = window.saga
    assert saga is not None
    _cards(window)["bruises"].clicked()
    window.page().codex.inspector.action.click()  # type: ignore[union-attr]
    assert rule_options.is_on(saga, "bruises")
    assert storage.load_saga(saga.id).rule_options.get("bruises")
    assert "heals within hours" in _inspector_words(window)
    action = window.page().codex.inspector.action  # type: ignore[union-attr]
    assert isinstance(action, ToggleSwitch) and action.isChecked()


def test_the_medallions_card_shows_every_set_in_the_inspector(app):
    window = _open()
    _cards(window)["medallions"].clicked()
    inspector = window.page().codex.inspector  # type: ignore[union-attr]
    drawn = [m.drawn_as for m in inspector.extra.findChildren(Medallion)]
    assert drawn == list(medallions.KEYS)
    _cards(window)["keep_season_records"].clicked()
    assert inspector.extra is None


def test_the_ruling_templates_list_is_wide_and_long(app):
    window = _open()
    assert window.saga is not None
    field = ruling_templates.saga_field(window.saga)
    p = window.page().p  # type: ignore[union-attr]
    dialog = FieldsDialog("Ruling Templates", [field], p)
    shown = dialog.findChildren(QListWidget)[0]
    assert shown.minimumWidth() > 800
    assert shown.height() >= min(16, shown.count()) * 22


def test_a_list_rules_its_titles_up_in_a_column_of_their_own(app):
    window = _open()
    p = window.page().p  # type: ignore[union-attr]
    rows = TitledRows(QListWidget(), p)
    rows.measure(["Fined: pays", "Banished: leaves"])
    assert rows.column > TitledRows.GAP
    rows.measure(["Fined: pays", "Bonisagus"])
    assert rows.column == 0
