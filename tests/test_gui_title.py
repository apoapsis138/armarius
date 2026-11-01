"""The desktop's title page: shown over the window when the app starts,
and each way on from it."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from armarius_style.desktop.illumination import paint_initial
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication
from support import everything_saga

from ars_magica_manager import settings, storage
from ars_magica_manager import title_page as tp
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.help import HelpPage
from ars_magica_manager.gui.pages import SagaPage, SagaShelf
from ars_magica_manager.gui.themes import PALETTES
from ars_magica_manager.gui.title import GiltTitle, TitleScreen
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _titled(saga_ids: list[str]) -> MainWindow:
    window = MainWindow(saga_ids=saga_ids)
    window.show_title()
    assert isinstance(window.title, TitleScreen)
    assert window.stack.currentWidget() is window.title
    return window


def test_the_title_page_offers_the_ways_on(app):
    window = _titled([])
    title = window.title
    assert title is not None
    assert list(title.buttons) == [tp.SAGAS, tp.HELP]


def test_open_saga_opens_the_saga_opened_last(app):
    saga, other = everything_saga(), everything_saga()
    other.id = "another"
    storage.save_saga(saga)
    storage.save_saga(other)
    tp.remember_saga(saga.id)
    window = _titled([saga.id, other.id])
    title = window.title
    assert title is not None
    title.buttons[tp.OPEN].click()
    assert window.title is None
    assert window.stack.currentIndex() == 0
    assert isinstance(window.page(), SagaPage)
    assert window.saga is not None and window.saga.id == saga.id


def test_all_sagas_goes_to_the_shelf(app):
    saga = everything_saga()
    storage.save_saga(saga)
    window = _titled([saga.id])
    assert window.title is not None
    window.title.buttons[tp.SAGAS].click()
    assert isinstance(window.page(), SagaShelf)
    assert window.saga is None


def test_help_opens_help_on_the_shelf(app):
    window = _titled([])
    assert window.title is not None
    window.title.buttons[tp.HELP].click()
    assert isinstance(window.page(), HelpPage)


def test_opening_a_saga_remembers_it(app):
    saga = everything_saga()
    storage.save_saga(saga)
    MainWindow(saga_ids=[saga.id])  # the only saga opens at once
    assert settings.load_settings()[tp.LAST_SAGA] == saga.id


def test_the_initial_paints_gold_on_its_ground(app):
    image = QImage(240, 240, QImage.Format.Format_ARGB32)
    image.fill(QColor(PALETTES[0]["background"]))
    painter = QPainter(image)
    paint_initial(painter, QRectF(15, 15, 210, 210), "A", PALETTES[0])
    painter.end()
    # The outer rim is gold, and the knotwork band's ground is dark.
    rim = image.pixelColor(120, 17)
    assert rim.red() > rim.blue() + 60
    band = image.pixelColor(28, 120)
    assert band.lightness() < 120


def test_the_name_and_frame_are_gilt(app):
    window = _titled([])
    title = window.title
    assert title is not None
    title.resize(1400, 860)
    assert isinstance(title.name, GiltTitle)
    assert title.name.text() == "Armarius"
    name = title.name.grab().toImage()
    pixels = [
        name.pixelColor(x, y)
        for x in range(0, name.width(), 2)
        for y in range(0, name.height(), 2)
    ]
    # Rubric red letters, edged in gold.
    assert any(c.red() > 120 and c.green() < 40 for c in pixels)
    assert any(c.red() > 180 and c.green() > 140 and c.blue() < 110 for c in pixels)
    title.setGraphicsEffect(None)  # as once faded in
    page = title.grab().toImage()
    frame = page.pixelColor(28, page.height() // 2)
    assert frame.red() > frame.blue() + 60
