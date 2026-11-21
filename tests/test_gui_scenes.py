"""The desktop's Scenes: the library in Saga Management and a Session
page's Scenes, each with the core's verbs (gui/scenes_section.py)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QTableView

from ars_magica_manager import commands, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.scenes_section import sessions_and_scenes
from ars_magica_manager.gui.session_page import SessionPage
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Character, Saga, Scene, SceneUse, Session


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.characters = [Character(id="gus", name="Gus", type="grog")]
    saga.scenes = [
        Scene(
            "sc1", title="The ford", place_name="A ford", regulars=["characters:gus"]
        ),
        Scene("sc2", title="The hill"),
    ]
    saga.sessions = [
        Session(
            "s1",
            real_date="2026-11-21",
            scenes=[SceneUse("u1", scene_id="sc1", present=["characters:gus"])],
        )
    ]
    return saga


def _buttons(widget) -> dict[str, QPushButton]:
    return {b.text().strip(): b for b in widget.findChildren(QPushButton)}


def _cells(widget) -> list[str]:
    found = []
    for view in widget.findChildren(QTableView):
        model = view.model()
        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                found.append(str(model.index(row, column).data()))
    return found


@pytest.mark.usefixtures("app")
def test_saga_management_lists_the_scenes_library_under_the_sessions() -> None:
    ran: list = []
    shown = sessions_and_scenes(_saga(), SCRIPTORUM, ran.append, lambda *_: None)
    words = " ".join(label.text() for label in shown.findChildren(QLabel))

    assert "Scenes (2)" in words
    assert {"The ford", "A ford", "Gus", "The hill"} <= set(_cells(shown))
    adds = [b for b in shown.findChildren(QPushButton) if b.text().strip() == "Add"]
    adds[-1].click()
    [step] = ran
    assert isinstance(step, commands.Form) and step.title == "Add a Scene"


@pytest.mark.usefixtures("app")
def test_a_sessions_page_lists_its_scenes_and_loads_one() -> None:
    storage.save_saga(_saga())
    window = MainWindow(saga_ids=["fengheld"])
    window.show()
    ran: list = []
    window.run = lambda command, *a, **k: ran.append(command)  # type: ignore[method-assign]
    window.open_session("s1")
    page = window.page()

    assert isinstance(page, SessionPage)
    assert {"The ford", "Prepared", "A ford", "Gus"} <= set(_cells(page))
    buttons = _buttons(page)
    assert {"Load a Scene", "Edit Scene", "Take Out"} <= set(buttons)
    buttons["Load a Scene"].click()
    [step] = ran
    assert isinstance(step, commands.Choose) and step.title == "Load a Scene"
