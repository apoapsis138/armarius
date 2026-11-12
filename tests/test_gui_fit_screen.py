"""Windows fit the screen they open on (frame.fit_to_screen): a 4K screen
at 300% scale leaves about 1280 x 680 to lay out in, and the drawn frame
gives no system title bar to drag a window back from off the screen. The
title page shrinks (title.COMPACT) so the window's minimum fits."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QApplication, QWidget
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager import title_page as tp
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.style.frame import (
    MAXIMISE,
    SCREEN_SHARE,
    fit_to_screen,
    fitted,
)
from ars_magica_manager.gui.title import FULL
from ars_magica_manager.gui.window import MainWindow

#: The free area of a 3840 x 2160 screen at 300% scale, in Qt's pixels.
SMALL = QSize(1280, 680)
#: The most buttons the title page shows at once.
FOUR = (
    tp.TitleChoice(tp.OPEN, "Open Saga", "The Limits of Magic"),
    tp.TitleChoice(tp.SAGAS, "All Sagas", "Choose one to open"),
    tp.TitleChoice(tp.JOIN, "Join a Saga", "Hosted by your storyguide"),
    tp.LEARN_CHOICE,
)


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _fits(size: QSize, room: QSize = SMALL) -> bool:
    return size.width() <= room.width() and size.height() <= room.height()


def _least(window: QWidget) -> QSize:
    layout = window.layout()
    assert layout is not None
    layout.activate()
    return window.minimumSizeHint().expandedTo(window.minimumSize())


def test_a_large_window_is_shrunk_to_the_screen_and_centred():
    available = QRect(QPoint(0, 0), SMALL)
    place = fitted(available, QSize(1400, 900), QSize(600, 400))
    assert place is not None
    assert place.size() == QSize(
        int(SMALL.width() * SCREEN_SHARE), int(SMALL.height() * SCREEN_SHARE)
    )
    assert available.contains(place)
    assert abs(place.center().x() - available.center().x()) <= 1
    assert abs(place.center().y() - available.center().y()) <= 1


def test_a_window_that_fits_keeps_its_size_and_stays_inside_the_screen():
    available = QRect(100, 40, 1280, 680)  # a second screen, under a taskbar
    place = fitted(available, QSize(640, 460), QSize(), QPoint(1300, 680))
    assert place is not None
    assert place.size() == QSize(640, 460)
    assert available.contains(place)


def test_a_window_never_shrinks_under_its_minimum():
    available = QRect(QPoint(0, 0), SMALL)
    place = fitted(available, QSize(1400, 900), QSize(1200, 650))
    assert place is not None
    assert place.size() == QSize(1200, 650)
    assert available.contains(place)


def test_a_window_whose_minimum_cannot_fit_is_maximised(app):
    assert fitted(QRect(QPoint(0, 0), SMALL), QSize(1400, 900), QSize(954, 791)) is None
    window = QWidget()
    screen = window.screen().availableGeometry()
    window.setMinimumSize(screen.width() + 10, 100)
    fit_to_screen(window, 1400, 900)
    assert window.windowState() & Qt.WindowState.WindowMaximized


def test_the_window_opens_within_its_screen(app):
    window = MainWindow(saga_ids=[])
    window.show_title()
    fit_to_screen(window, 1400, 900)
    screen = window.screen().availableGeometry()
    assert screen.contains(window.geometry())
    assert not window.isMaximized()
    window.close()


def test_the_title_page_fits_a_highly_scaled_4k_screen(app):
    window = MainWindow(saga_ids=[])
    window.show_title()
    title = window.title
    assert title is not None
    for choices in (FOUR, (*tp.LEARN_CHOICE.then, tp.BACK_CHOICE)):
        title.show_choices(choices)
        assert _fits(title.minimumSizeHint(), QSize(900, 620)), choices
        assert _fits(_least(window)), choices
    window.resize(SMALL)
    window.show()
    QApplication.processEvents()
    # The window keeps the size asked for, and the page all fits inside it.
    assert window.size() == SMALL
    need = title.column.minimumSize()
    assert need.width() <= title.width() and need.height() <= title.height()
    assert title.share is not None and title.share < 1
    window.close()


def test_the_title_page_looks_as_it_did_where_there_is_room(app):
    window = MainWindow(saga_ids=[])
    window.show_title()
    title = window.title
    assert title is not None
    title.show_choices(FOUR)
    window.resize(1600, 1000)
    window.show()
    QApplication.processEvents()
    assert title.share == 1.0
    assert title.initial.side == FULL.initial
    assert title.name.font().pointSize() == FULL.name
    assert {b.size().toTuple() for b in title.buttons.values()} == {(250, 74)}
    window.close()


def test_every_page_fits_a_highly_scaled_4k_screen(app):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    assert window.saga is not None
    magus = next(c for c in window.saga.characters if c.type == "magus")
    covenant = window.saga.covenants[0]
    pages = {
        "saga": lambda: None,
        "covenant": lambda: window.open_covenant(covenant.id),
        "character": lambda: window.show_character(magus.id),
        "title": window.show_title,
    }
    for name, show in pages.items():
        show()
        QApplication.processEvents()
        assert _fits(_least(window)), (name, _least(window))
    window.close()


def test_maximise_and_restore_on_a_small_screen(app):
    window = MainWindow(saga_ids=[])
    window.show_title()
    fit_to_screen(window, 1400, 900)
    window.show()
    QApplication.processEvents()
    restored = window.geometry()
    window.controls.buttons[MAXIMISE].click()
    QApplication.processEvents()
    assert window.isMaximized()
    window.controls.buttons[MAXIMISE].click()
    QApplication.processEvents()
    assert not window.isMaximized()
    assert window.geometry().size() == restored.size()
    window.close()
