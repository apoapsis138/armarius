"""The desktop's Sessions list with the Virtual Tabletop (Preview): Begin
Session, End Session and the Chronicle on the chosen row, and the switch
in the Settings window (gui/sessions_section.py, gui/settings_window.py)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from ars_magica_manager import virtual_tabletop
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.sessions_section import sessions_section
from ars_magica_manager.gui.settings_window import SettingsWindow
from ars_magica_manager.gui.style.liveries import THEMES
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.models import Saga, Session


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _buttons() -> set[str]:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.sessions = [Session("s1")]
    shown = sessions_section(saga, SCRIPTORUM, lambda _step: None, lambda *_: None)
    return {b.text().strip() for b in shown.findChildren(QPushButton)}


@pytest.mark.usefixtures("app")
def test_the_sessions_list_has_no_chronicle_buttons_with_the_preview_off() -> None:
    assert not {"Begin Session", "End Session", "Chronicle"} & _buttons()


@pytest.mark.usefixtures("app")
def test_the_preview_adds_begin_end_and_the_chronicle_to_the_row() -> None:
    virtual_tabletop.set_on(True)

    assert {"Begin Session", "End Session", "Chronicle"} <= _buttons()


@pytest.mark.usefixtures("app")
def test_the_settings_window_turns_the_preview_on_and_off() -> None:
    """The page on show is drawn again, to show or hide what it gates."""
    redrawn: list[bool] = []
    window = SettingsWindow(
        SCRIPTORUM, THEMES[0], lambda _name: None, redraw=lambda: redrawn.append(True)
    )
    assert not window.virtual_tabletop.isChecked()

    window.virtual_tabletop.click()
    assert virtual_tabletop.on() and redrawn == [True]
    window.virtual_tabletop.click()
    assert not virtual_tabletop.on() and len(redrawn) == 2
    window.close()
