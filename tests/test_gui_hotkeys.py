"""The desktop's page-wide keys (hotkeys.py): ? and F1 open Help, Esc
cancels a form or goes back a page, q quits; ? and q never act while
typing in a field or with a form open."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import section_buttons
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLineEdit
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import hotkeys, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.help import HelpPage
from ars_magica_manager.gui.window import MainWindow

Shift = Qt.KeyboardModifier.ShiftModifier


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(app) -> MainWindow:
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    window.activateWindow()
    QTest.qWaitForWindowActive(window)
    return window


def _press(window: MainWindow, key: Qt.Key, modifiers=Qt.KeyboardModifier.NoModifier):
    target = QApplication.focusWidget() or window
    QTest.keyClick(target, key, modifiers)


def _magus_id(window: MainWindow) -> str:
    assert window.saga is not None
    return next(c.id for c in window.saga.characters if c.type == "magus")


def test_question_mark_and_f1_open_help_and_esc_goes_back(app):
    window = _window(app)
    window.show_character(_magus_id(window))
    for modifiers in (Qt.KeyboardModifier.NoModifier, Shift):
        # A ? arrives with Shift held or not, by keyboard and platform.
        _press(window, Qt.Key.Key_Question, modifiers)
        assert isinstance(window.page(), HelpPage)
        _press(window, Qt.Key.Key_Escape)
        assert isinstance(window.page(), CharacterSheet)
    _press(window, Qt.Key.Key_F1)
    assert isinstance(window.page(), HelpPage)
    window.close()


def test_esc_goes_back_up_the_trail_and_stops_at_the_top(app):
    window = _window(app)
    window.show_character(_magus_id(window))
    depth = len(window.trail)
    _press(window, Qt.Key.Key_Escape)
    assert len(window.trail) == depth - 1
    for _ in range(depth):
        _press(window, Qt.Key.Key_Escape)
    assert len(window.trail) == 1
    window.close()


def test_q_quits(app):
    window = _window(app)
    _press(window, Qt.Key.Key_Q)
    assert not window.isVisible()


def test_typed_keys_type_in_a_field(app):
    """? and q are typed into the help filter; Esc still goes back."""
    window = _window(app)
    window.open_help()
    page = window.page()
    assert isinstance(page, HelpPage)
    page.filter.setFocus()
    _press(window, Qt.Key.Key_Q)
    _press(window, Qt.Key.Key_Question, Shift)
    assert window.isVisible()
    assert isinstance(window.page(), HelpPage)
    assert isinstance(page.filter, QLineEdit)
    assert page.filter.text() == "q?"
    _press(window, Qt.Key.Key_Escape)
    assert not isinstance(window.page(), HelpPage)
    window.close()


def test_esc_cancels_a_form_window_and_q_waits(app):
    """A form is a window of its own, so it takes the keys: q off its
    fields quits nothing, and Esc cancels it, leaving the page as it was."""
    window = _window(app)
    window.show_character(_magus_id(window))
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Description")
    window.ask = window._present  # the real one, not a test's
    seen = {}

    def answer() -> None:
        form = next(d for d in window.findChildren(FieldsDialog) if d.isVisible())
        form.setFocus()  # off its fields, where q would type
        QTest.keyClick(form, Qt.Key.Key_Q)
        seen["open after q"] = form.isVisible() and window.isVisible()
        QTest.keyClick(form, Qt.Key.Key_Escape)

    QTimer.singleShot(0, answer)
    section_buttons(page, "Personality Traits")["Add"].click()
    assert seen == {"open after q": True}
    assert window._open is None
    assert window.page() is page  # still on the sheet: Esc only cancelled
    window.close()


def test_the_window_binds_every_key_in_the_table(app):
    window = _window(app)
    from PySide6.QtGui import QShortcut

    bound = {s.key().toString() for s in window.findChildren(QShortcut)}
    for hotkey in hotkeys.HOTKEYS:
        for key in hotkey.keys:
            assert key.upper() in {k.upper() for k in bound}, key
    window.close()


def test_on_the_title_page_question_mark_opens_help_and_esc_stays(app):
    window = _window(app)
    window.show_title()
    _press(window, Qt.Key.Key_Escape)
    assert window.title is not None
    _press(window, Qt.Key.Key_Question)
    assert window.title is None
    assert isinstance(window.page(), HelpPage)
    window.close()
