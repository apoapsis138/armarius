"""The desktop window's own frame (gui/frame.py): no system title bar,
minimise, maximise and close drawn on the paper, a strip that moves the
window, and grips that resize it."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from armarius_style.desktop.frame import CLOSE, GRIP, MAXIMISE, MINIMISE, TopStrip
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import (
    ChooseDialog,
    FieldsDialog,
    NoticeDialog,
    step_dialog,
)
from ars_magica_manager.gui.themes import PALETTES
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
    from armarius_style.desktop import snapping

    window = _window(app)
    # Snap's styles and frame are Windows's; elsewhere nothing is answered.
    assert snapping.native_event(window, b"xcb_generic_event_t", 0) is None
    snapping.make_snappable(window)
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint


def _popups() -> list:
    p = PALETTES[0]
    form = Form("A Form", lambda: [DialogField("a", "A", "text")], lambda _v: None)
    return [
        step_dialog(form, p, None),
        step_dialog(Confirm("Sure?", lambda: None), p, None),
        ChooseDialog("A List", [], p),
        NoticeDialog("A Notice", "Done.", p),
    ]


def test_every_popup_has_the_apps_title_bar(app):
    for popup in _popups():
        assert popup.windowFlags() & Qt.WindowType.FramelessWindowHint
        assert popup.drag.title == "Armarius"
        assert CLOSE in popup.window_buttons.buttons


def test_a_popups_close_button_cancels_it(app):
    popup = _popups()[0]
    popup.show()
    popup.window_buttons.buttons[CLOSE].click()
    assert popup.result() == 0 and not popup.isVisible()


def test_forms_and_lists_maximise_and_questions_do_not(app):
    form, confirm, choose, notice = _popups()
    assert MAXIMISE in form.window_buttons.buttons
    assert MAXIMISE in choose.window_buttons.buttons
    assert MAXIMISE not in confirm.window_buttons.buttons
    assert MAXIMISE not in notice.window_buttons.buttons
    assert not confirm.drag.maximises


def _form(cancel_label: str = "Cancel") -> FieldsDialog:
    fields = [DialogField("a", "A", "text", value="old")]
    return FieldsDialog("A Form", fields, PALETTES[0], cancel_label=cancel_label)


def test_a_form_asks_before_losing_changes_and_not_otherwise(app):
    form = _form()
    asked = []
    form.ask = lambda question: asked.append(question) or 0
    form.show()
    form.reject()
    assert asked == [] and not form.isVisible()

    form = _form()
    form.ask = lambda question: asked.append(question) or 0
    form.inputs["a"].setText("new")
    form.show()
    form.window_buttons.buttons[CLOSE].click()
    assert len(asked) == 1 and form.isVisible()
    form.ask = lambda _question: 1
    form.reject()
    assert not form.isVisible()


def test_a_forms_save_never_asks(app):
    form = _form()
    form.ask = lambda _question: pytest.fail("asked")
    form.inputs["a"].setText("new")
    form.show()
    form.try_save()
    assert form.values == {"a": "new"}


def test_a_calculators_close_never_asks(app):
    form = _form("Close")
    form.ask = lambda _question: pytest.fail("asked")
    form.inputs["a"].setText("new")
    form.show()
    form.reject()
    assert not form.isVisible()
