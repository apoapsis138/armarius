"""The desktop's movements (gui/motion.py): still under test and with
Reduce motion, and each one asked for where it belongs."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QTableView, QWidget
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import creation, settings, storage
from ars_magica_manager.gui import motion, pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet, XpTable
from ars_magica_manager.gui.season_panel import SeasonDial, wheel_place
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.widgets import XP_FROM, Spread
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.gui.worksheet import WorksheetPage
from ars_magica_manager.models import Character


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


class _Moves:
    """A player that writes down each movement asked for, then ends it at
    once (as Still does) so a test needn't wait."""

    def __init__(self) -> None:
        self.names: list[str] = []

    def tween(self, owner, step, ms, *, name, start, end, done) -> None:
        self.names.append(name)
        step(start)
        step(end)
        if done is not None:
            done()

    def hold(self, owner, ms, then) -> None:
        then()


@pytest.fixture
def moves(monkeypatch) -> _Moves:
    moves = _Moves()
    monkeypatch.setattr(motion, "_player", moves)
    return moves


def _window(saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    return window


def _sheet(window: MainWindow, character: Character) -> CharacterSheet:
    window.show_character(character.id)
    sheet = window.sheet_area.findChild(CharacterSheet)
    assert sheet is not None
    QApplication.processEvents()  # the page is shown once events run
    return sheet


def test_nothing_moves_under_test_and_reduce_motion_is_remembered(monkeypatch):
    monkeypatch.setattr(motion, "_player", None)
    assert isinstance(motion._chosen(), motion.Still)
    assert not motion.moving()
    monkeypatch.delenv(motion.ENV_VAR)
    monkeypatch.setattr(motion, "windows_animates", lambda: True)
    assert not motion.reduced()
    assert isinstance(motion._chosen(), motion.Moving)
    motion.set_reduced(True)
    assert settings.load_settings()["reduce_motion"] is True
    assert isinstance(motion._chosen(), motion.Still)


def test_reduce_motion_follows_windows_until_it_is_set(monkeypatch):
    monkeypatch.setattr(motion, "windows_animates", lambda: False)
    assert motion.reduced()
    motion.set_reduced(False)
    assert not motion.reduced()


def test_a_movement_eases_to_its_end_and_a_new_one_of_its_name_replaces_it(
    app, monkeypatch
):
    monkeypatch.setattr(motion, "_player", motion.Moving())
    owner = QObject()
    first: list[float] = []
    second: list[float] = []
    ended: list[str] = []
    motion.tween(owner, first.append, 400, name="ink", done=lambda: ended.append("1"))
    motion.tween(owner, second.append, 40, name="ink", done=lambda: ended.append("2"))
    for _ in range(100):
        QTest.qWait(10)
        if ended:
            break
    assert ended == ["2"]
    assert second[0] == 0.0 and second[-1] == pytest.approx(1.0)
    assert second == sorted(second)
    assert first[-1] < 1.0


def test_with_no_motion_a_movement_ends_at_once(app):
    seen: list[float] = []
    motion.tween(QObject(), seen.append, 200, start=0.0, end=0.6)
    assert seen == [0.6]


def test_the_inspector_inks_in_and_the_title_settles(app, moves):
    saga = _sample_saga_with_covenant()
    window = _window(saga)
    sheet = _sheet(window, saga.characters[0])
    inspector = sheet.codex.inspector
    inspector.show_item("Creo", "Technique", "Making things.")
    assert "ink" in moves.names
    assert not inspector.ink.isVisible()
    margins = inspector.title.contentsMargins()
    assert (margins.top(), margins.bottom()) == (0, inspector.DRIFT)
    window.close()


def test_a_chapter_fades_in_with_a_small_slide(app, moves):
    saga = _sample_saga_with_covenant()
    window = _window(saga)
    sheet = _sheet(window, saga.characters[0])
    moves.names.clear()
    sheet.codex.open_chapter("Abilities")
    assert {"fade", "slide"} <= set(moves.names)
    window.close()


def test_a_newly_chosen_row_spreads_its_wash_and_others_stay_washed(app, moves):
    view = QTableView()
    model = QStandardItemModel(3, 2)
    for row in range(3):
        model.setItem(row, 0, QStandardItem(f"Row {row}"))
    view.setModel(model)
    spread = Spread(view)
    view.setCurrentIndex(model.index(1, 0))
    assert spread.reach(model.index(0, 0)) == 1.0
    assert spread.reach(model.index(1, 1)) == 1.0
    assert moves.names == ["spread"]
    spread.reach(model.index(1, 0))
    assert moves.names == ["spread"]  # the same row doesn't spread again


def _xp_table(memory: str, xp: int) -> XpTable:
    table = XpTable(
        ["Art", "Score", "Experience"], SCRIPTORUM, lambda _key: None, memory=memory
    )
    cells = [QStandardItem("Creo"), QStandardItem("1")]
    table.add(None, "Creo", cells, xp / 10, "")
    table.finish()
    return table


def test_an_xp_line_that_moved_grows_from_where_it_was_when_next_shown(app, moves):
    memory = "grower:Technique"
    assert not _xp_table(memory, 3).grows
    assert not _xp_table(memory, 3).grows
    grown = _xp_table(memory, 7)
    assert grown.grows
    assert grown.bars[0][1].data(XP_FROM) == pytest.approx(0.3)
    grown.show()
    assert "grow" in moves.names and not grown.grows
    assert grown.xp_bars.at == 1.0
    # A score that went up starts its new line from nothing.
    up = _xp_table(memory, 2)
    assert up.bars[0][1].data(XP_FROM) == 0.0
    grown.close()


def test_a_table_with_no_memory_never_grows(app):
    _xp_table("", 3)
    assert not _xp_table("", 8).grows


def test_advance_season_turns_the_seasons_dial(app, moves):
    window = _window(_sample_saga_with_covenant())
    ended: list[str] = []
    window._turn_the_dial(lambda: ended.append("then"))
    # The quarter turn, the new season shown large, then the fade; and
    # only once it has gone does the window go on.
    assert moves.names[-3:] == ["turn", "reveal", "fade"]
    assert ended == ["then"]
    assert not any(d.isVisible() for d in window.stack.findChildren(SeasonDial))
    window.close()


def test_without_motion_no_dial_turns(app):
    window = _window(_sample_saga_with_covenant())
    ended: list[str] = []
    window._turn_the_dial(lambda: ended.append("then"))
    assert ended == ["then"]
    assert window.stack.findChildren(SeasonDial) == []
    window.close()


def test_the_dial_brings_the_new_season_to_the_top(app):
    saga = _sample_saga_with_covenant()
    saga.current_season, saga.current_year = "Spring", 1221
    host = QWidget()
    dial = SeasonDial(host, saga, SCRIPTORUM, lambda: None)
    # The wheel starts at the season just ended (Winter of the year
    # before), and a quarter turn brings the present one to the top.
    assert dial.wheel[:2] == [("Winter", 1220), ("Spring", 1221)]
    assert wheel_place(0, 0.0) == (0.0, 1.0)
    angle, near = wheel_place(1, 1.0)
    assert (angle, near) == (0.0, 1.0)
    assert wheel_place(2, 1.0)[1] < 1e-9


def test_a_click_ends_the_dial_at_once(app):
    saga = _sample_saga_with_covenant()
    ended: list[str] = []
    host = QWidget()
    dial = SeasonDial(host, saga, SCRIPTORUM, lambda: ended.append("done"))
    QTest.mouseClick(dial, Qt.MouseButton.LeftButton)
    QTest.mouseClick(dial, Qt.MouseButton.LeftButton)
    assert ended == ["done"]


def test_no_seal_is_pressed_without_motion(app):
    assert motion.press_seal(QWidget(), lambda g, c, r: None) is None


def test_a_finished_character_is_sealed(app, moves):
    saga = _sample_saga_with_covenant()
    character = creation.add_character(saga, "Brother Anselm", "companion", "cov1")
    window = _window(saga)
    window.open_worksheet(character.id)
    page = window.sheet_area.findChild(WorksheetPage)
    assert page is not None
    moves.names.clear()
    window._finished(character.id)
    assert "press" in moves.names
    window.close()


def test_the_settings_window_turns_reduce_motion_on_and_off(app, monkeypatch):
    monkeypatch.setattr(motion, "windows_animates", lambda: True)
    window = MainWindow(saga_ids=[])
    window.settings.click()
    shown = window._settings
    assert shown is not None
    box = shown.motion
    assert box.text() == "Reduce motion" and not box.isChecked()
    box.click()
    assert motion.reduced() and box.isChecked()
    box.click()
    assert not motion.reduced() and not box.isChecked()
    shown.close()
    window.close()
