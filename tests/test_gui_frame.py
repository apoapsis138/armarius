"""The desktop window's own frame (gui/frame.py): no system title bar,
minimise, maximise and close drawn on the paper, a strip that moves the
window, and grips that resize it."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.frame import CLOSE, GRIP, MAXIMISE, MINIMISE, TopStrip
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(app) -> MainWindow:
    window = MainWindow(saga_ids=[])
    window.resize(1000, 700)
    window.show()
    app.processEvents()
    return window


def test_the_window_has_no_system_title_bar(app):
    window = _window(app)
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint
    assert window.drag.title == "Armarius"


def test_maximise_restores_when_pressed_again_and_close_closes(app):
    window = _window(app)
    buttons = window.controls.buttons
    buttons[MAXIMISE].click()
    app.processEvents()
    assert window.isMaximized()
    assert buttons[MAXIMISE].toolTip() == "Restore"
    buttons[MAXIMISE].click()
    app.processEvents()
    assert not window.isMaximized()
    buttons[MINIMISE].click()
    app.processEvents()
    assert window.windowState() & Qt.WindowState.WindowMinimized
    buttons[CLOSE].click()
    app.processEvents()
    assert not window.isVisible()


def test_double_clicking_the_bar_maximises(app):
    window = _window(app)
    QTest.mouseDClick(window.drag, Qt.MouseButton.LeftButton)
    app.processEvents()
    assert window.isMaximized()
    QTest.mouseDClick(window.drag, Qt.MouseButton.LeftButton)
    app.processEvents()
    assert not window.isMaximized()


def test_grips_line_every_edge_until_the_window_is_maximised(app):
    window = _window(app)
    grips = window.grips.grips
    assert len(grips) == 8
    right = next(g for g in grips if g.edges == Qt.Edge.RightEdge)
    assert right.geometry().right() == window.width() - 1
    assert right.width() == GRIP
    assert right.cursor().shape() == Qt.CursorShape.SizeHorCursor
    assert all(g.isVisible() for g in grips)
    window.showMaximized()
    app.processEvents()
    assert not any(g.isVisible() for g in grips)


def test_the_title_page_has_the_window_buttons_too(app):
    window = _window(app)
    window.show_title()
    assert window.title is not None
    strip = window.title.findChild(TopStrip)
    assert strip is not None
    assert strip.width() == window.title.width()
    assert set(strip.controls.buttons) == {MINIMISE, MAXIMISE, CLOSE}


def test_other_systems_leave_native_messages_to_qt(app):
    from ars_magica_manager.gui import snapping

    window = _window(app)
    # Snap's styles and frame are Windows's; elsewhere nothing is answered.
    assert snapping.native_event(window, b"xcb_generic_event_t", 0) is None
    snapping.make_snappable(window)
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint
