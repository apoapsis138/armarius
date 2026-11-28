"""The desktop window's own frame (gui/frame.py): no system title bar,
minimise, maximise and close drawn on the paper, a strip that moves the
window, and grips that resize it."""

from __future__ import annotations

import gc
import os
import weakref

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import shiboken6
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QScrollArea

from ars_magica_manager import handout_layout, shows
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.chronicle_pane import ShownCopy, ShownPicture
from ars_magica_manager.gui.forms import (
    ChooseDialog,
    FieldsDialog,
    NoticeDialog,
    step_dialog,
)
from ars_magica_manager.gui.handout_page import HandoutWindow
from ars_magica_manager.gui.style.frame import CLOSE, GRIP, MAXIMISE, MINIMISE, TopStrip
from ars_magica_manager.gui.style.ornaments import FleuronRule
from ars_magica_manager.gui.style.window_frame import Window
from ars_magica_manager.gui.themes import PALETTES, SCRIPTORUM_DARK
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import VELLUM
from ars_magica_manager.paths import APP_NAME


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
    assert window.drag.title == APP_NAME


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
    from ars_magica_manager.gui.style import snapping

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
        assert popup.drag.title == APP_NAME
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


def _viewers() -> list:
    p = PALETTES[0]
    laid = handout_layout.lay_out("The Ford", VELLUM, "Words.")
    return [
        ShownPicture(shows.Shown("The Rhine", picture=b"x"), p),
        ShownCopy(shows.Shown("Hilda", "# Hilda"), p),
        HandoutWindow(laid, p),
    ]


def test_every_viewer_wears_the_apps_frame(app):
    for viewer in _viewers():
        assert viewer.windowFlags() & Qt.WindowType.FramelessWindowHint
        assert viewer.drag.title == APP_NAME
        assert CLOSE in viewer.window_buttons.buttons


def test_a_picture_and_a_copy_wear_their_title_as_heading(app):
    picture, copy, _handout = _viewers()
    for viewer, title in ((picture, "The Rhine"), (copy, "Hilda")):
        heading = viewer.column.itemAt(0).widget()
        assert heading.text() == title
        assert isinstance(viewer.column.itemAt(1).widget(), FleuronRule)


def test_a_handout_has_no_heading_its_stationery_draws_its_title(app):
    *_, handout = _viewers()
    assert isinstance(handout.column.itemAt(0).widget(), QScrollArea)
    assert handout.findChildren(FleuronRule) == []


def test_a_copy_s_own_name_line_gives_way_to_its_heading(app):
    words = "# Hilda\n\n*Magus of Bonisagus*\n\nWords."
    copy = ShownCopy(shows.Shown("Hilda", words), PALETTES[0])
    assert copy.text.toPlainText().split() == ["Magus", "of", "Bonisagus", "Words."]


def test_a_copy_keeps_a_first_line_that_is_not_its_name_line(app):
    words = "## Abilities\n\nWords."
    copy = ShownCopy(shows.Shown("Hilda", words), PALETTES[0])
    assert copy.text.toPlainText().split() == ["Abilities", "Words."]


def test_a_copy_shown_under_another_title_keeps_the_record_s_name(app):
    words = "# Hilda\n\nWords."
    copy = ShownCopy(shows.Shown("A stranger at the gate", words), PALETTES[0])
    assert copy.text.toPlainText().split() == ["Hilda", "Words."]


def test_a_copy_with_no_title_has_no_empty_heading(app):
    copy = ShownCopy(shows.Shown("", "Words."), PALETTES[0])
    assert copy.column.itemAt(0).widget() is copy.text


@pytest.mark.parametrize(
    "palette", [PALETTES[0], SCRIPTORUM_DARK], ids=["light", "dark"]
)
def test_a_copy_s_words_lie_on_the_window_s_paper_in_its_ink(app, palette):
    copy = ShownCopy(shows.Shown("Hilda", ""), palette)
    bare = Window("Hilda", palette, None)
    copy.show()
    bare.show()
    bare.resize(copy.size())
    app.processEvents()
    where = copy.text.geometry().center()
    where = copy.text.parentWidget().mapTo(copy, where)
    try:
        seen = copy.grab().toImage().pixelColor(where)
        assert seen == bare.grab().toImage().pixelColor(where)
        ink = copy.text.palette().color(QPalette.ColorRole.Text)
        assert ink.name() == QColor(palette["foreground"]).name()
    finally:
        copy.close()
        bare.close()


def test_esc_closes_each_viewer(app):
    for viewer in _viewers():
        viewer.show()
        QTest.keyClick(viewer, Qt.Key.Key_Escape)
        assert not viewer.isVisible()


def test_a_window_s_title_as_written_keeps_its_brackets(app):
    window = Window("A [i]Window[/i]", PALETTES[0], None, as_written=True)
    assert window.windowTitle() == "A [i]Window[/i]"
    assert window.add_heading("A [i]Window[/i]").text() == "A [i]Window[/i]"


def test_a_viewer_closes_from_its_bar_and_from_its_close_button(app):
    for viewer in _viewers():
        viewer.show()
        viewer.window_buttons.buttons[CLOSE].click()
        assert not viewer.isVisible()
        viewer.show()
        row = viewer.buttons_row
        assert row.itemAt(row.count() - 1).widget() is viewer.close_button
        assert viewer.close_button.text() == "Close"
        viewer.close_button.click()
        assert not viewer.isVisible()


def test_a_long_title_wraps_rather_than_widening_a_viewer(app):
    title = "Writ of the Tower Guard concerning the tithes of the mill and ford"
    long = ShownCopy(shows.Shown(title, "Words."), PALETTES[0])
    assert long.minimumSizeHint().width() < 300
    assert long.column.itemAt(0).widget().text() == title


def test_a_picture_with_no_title_has_no_empty_heading(app):
    picture = ShownPicture(shows.Shown("", picture=b"x"), PALETTES[0])
    assert picture.column.itemAt(0).widget() is picture.picture


def test_a_copy_and_a_handout_maximise_and_a_picture_does_not(app):
    picture, copy, handout = _viewers()
    assert set(picture.window_buttons.buttons) == {CLOSE}
    assert not picture.drag.maximises
    assert MAXIMISE in copy.window_buttons.buttons
    assert MAXIMISE in handout.window_buttons.buttons


class _Bare(Window):
    controls = (CLOSE,)


def test_a_bare_window_wears_the_apps_frame_and_closes(app):
    window = _Bare("A Window", PALETTES[0], None)
    window.show()
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint
    assert window.drag.title == APP_NAME
    assert set(window.window_buttons.buttons) == {CLOSE}
    window.window_buttons.buttons[CLOSE].click()
    assert not window.isVisible()


def test_a_windows_heading_reads_its_title_over_the_rule(app):
    window = Window("A [i]Window[/i]", PALETTES[0], None)
    heading = window.add_heading("A [i]Window[/i]")
    assert heading.text() == "A Window"
    assert window.column.indexOf(heading) == 0
    rule = window.column.itemAt(1).widget()
    assert isinstance(rule, FleuronRule)


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


def test_a_closed_window_stays_from_the_collector_until_qt_deletes_it(app):
    """The collector freeing a closed window crashed the app (a double
    delete of its buttons), most often as the shelf was rebuilt after
    deleting a saga."""
    window = _window(app)
    sheet = NoticeDialog("A Notice", "Words.", PALETTES[0], window)
    QTimer.singleShot(0, sheet.accept)
    sheet.exec()
    held = weakref.ref(sheet)
    del sheet
    gc.collect()
    assert held() is not None
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert not shiboken6.isValid(held())
    window.close()


def test_a_calculators_close_never_asks(app):
    form = _form("Close")
    form.ask = lambda _question: pytest.fail("asked")
    form.inputs["a"].setText("new")
    form.show()
    form.reject()
    assert not form.isVisible()
