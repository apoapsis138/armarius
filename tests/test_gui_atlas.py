"""The desktop's Atlas chapter (gui/atlas.py): a map's pins, opening a
pin's record and coming back, the Table view, New Map, Place on Map,
moving, hiding and making a pin secret, and Show on Map from a record's
Manage chapter, answered without showing the dialogs."""

from __future__ import annotations

import os
import struct
import zlib

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from ars_magica_manager import atlas, storage
from ars_magica_manager.gui import atlas as atlas_page
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Covenant, Laboratory, Neighbour, Saga, Tribunal
from ars_magica_manager.references import Ref


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


@pytest.fixture(autouse=True)
def fresh_atlas(monkeypatch):
    """Each test starts with nothing the Atlas remembers."""
    monkeypatch.setattr(atlas_page, "KEPT", atlas_page._Kept())


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = b"".join(b"\x00" + b"\xd0\xc0\xa0" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _saga(tmp_path) -> Saga:
    picture = tmp_path / "rhine.png"
    picture.write_bytes(_png(200, 100))
    saga = Saga(
        "atlas",
        "Atlas Saga",
        tribunals=[Tribunal("rhine", "The Rhine")],
        covenants=[Covenant("cov", "atlas", "Durenmar")],
        laboratories=[Laboratory("lab", "cov", "The Tower")],
        neighbours=[
            Neighbour("forest", "The Black Forest", kind="place"),
            Neighbour("town", "Basel", kind="town"),
        ],
    )
    name, width, height = atlas.store_picture(picture)
    m = atlas.add_map(
        saga, "The Rhine", "rhine", picture=name, width=width, height=height
    )
    atlas.place_pin(saga, m.id, "covenants", "cov", 0.5, 0.5)
    atlas.place_pin(saga, m.id, "neighbours", "forest", 0.25, 0.25).secret = True
    return saga


def _window(saga: Saga) -> MainWindow:
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.resize(1400, 900)
    window.show()
    window.open_saga(saga.id)
    return window


def _atlas(window: MainWindow) -> atlas_page.AtlasChapter:
    page = window.page()
    codex = getattr(page, "codex", None)
    assert codex is not None
    codex.open_chapter("The Atlas")
    chapter = codex.pages.currentWidget()
    assert isinstance(chapter, atlas_page.AtlasChapter)
    return chapter


def _names(chapter: atlas_page.AtlasChapter) -> list[list[str]]:
    assert chapter.view is not None
    return sorted([s.ref.name for s in item.here] for item in chapter.view.pins)


def _buttons(widget: QWidget) -> dict[str, QPushButton]:
    return {b.text().strip(): b for b in widget.findChildren(QPushButton)}


def test_the_atlas_shows_the_pins_and_a_pin_opens_its_record(app, tmp_path):
    window = _window(_saga(tmp_path))
    chapter = _atlas(window)
    # The laboratory shows at its covenant's pin.
    assert _names(chapter) == [["Durenmar", "The Tower"], ["The Black Forest"]]
    assert chapter.view is not None and chapter.view.size_ == (200, 100)
    forest = chapter.view.item_of("neighbours", "forest")
    assert forest is not None
    chapter.view.clicked(forest)
    assert window.crumb_names()[-1] == "The Black Forest"
    window.go(window.trail[:2])
    assert isinstance(
        window.page().codex.pages.currentWidget(), atlas_page.AtlasChapter
    )  # type: ignore[union-attr]


def test_the_table_view_leaves_off_the_secret_pin(app, tmp_path):
    window = _window(_saga(tmp_path))
    chapter = _atlas(window)
    chapter.table.setChecked(True)
    assert _names(chapter) == [["Durenmar", "The Tower"]]
    assert "secret pins are left off" in chapter.line.text()
    chapter.table.setChecked(False)
    assert len(_names(chapter)) == 2


def test_place_on_map_puts_a_record_where_the_map_is_clicked(app, tmp_path):
    saga = _saga(tmp_path)
    window = _window(saga)
    chapter = _atlas(window)
    view = chapter.view
    assert view is not None
    answering(window, "Basel")
    _buttons(chapter)["Place on Map"].click()
    assert view.picking is not None
    assert view.picking.record == ("neighbours", "town", "Basel")
    assert "Click where Basel is" in chapter.line.text()
    spot = view.mapFromScene(QPointF(150, 25))
    QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(spot))
    pin = atlas.pin_of(storage.load_saga(saga.id), "the_rhine", "neighbours", "town")
    assert pin is not None
    assert pin.x == pytest.approx(0.75, abs=0.02)
    assert pin.y == pytest.approx(0.25, abs=0.02)
    assert ["Basel"] in _names(chapter) and view.picking is None


def test_a_pin_is_moved_made_secret_and_taken_off(app, tmp_path):
    saga = _saga(tmp_path)
    window = _window(saga)
    chapter = _atlas(window)
    view = chapter.view
    assert view is not None
    durenmar = view.item_of("covenants", "cov")
    assert durenmar is not None
    view.moved(durenmar.here[0], QPointF(20, 80))
    [own] = [s for s in durenmar.here if s.pin is not None]
    saved = storage.load_saga(saga.id).pins[0]
    assert (saved.x, saved.y) == (0.1, 0.8)
    chapter.set_secret(own, True)
    assert storage.load_saga(saga.id).pins[0].secret
    chapter.take_off(own)
    assert [p.record_id for p in storage.load_saga(saga.id).pins] == ["forest"]
    assert _names(chapter) == [["The Black Forest"]]


def test_new_map_adds_one_and_shows_it(app, tmp_path):
    saga = _saga(tmp_path)
    window = _window(saga)
    chapter = _atlas(window)
    city = tmp_path / "basel.png"
    city.write_bytes(_png(60, 60))
    answering(window, {"name": "Basel", "tribunal": "rhine", "picture": str(city)})
    _buttons(chapter)["New Map"].click()
    assert [m.name for m in storage.load_saga(saga.id).tribunals[0].maps] == [
        "The Rhine",
        "Basel",
    ]
    assert chapter.choice.currentText() == "Basel (The Rhine)"
    assert chapter.view is not None and chapter.view.pins == []


def test_a_map_with_its_picture_missing_shows_a_placeholder(app, tmp_path):
    saga = _saga(tmp_path)
    saga.tribunals[0].maps[0].picture = "gone.png"
    window = _window(saga)
    chapter = _atlas(window)
    # The placeholder keeps the missing picture's shape.
    assert chapter.view is not None and chapter.view.size_ == (2400, 1200)
    assert len(_names(chapter)) == 2


def test_a_saga_with_no_maps_offers_new_map(app, tmp_path):
    window = _window(Saga("bare", "Bare"))
    chapter = _atlas(window)
    assert list(_buttons(chapter)) == ["New Map"]
    assert chapter.view is None


def test_show_on_map_opens_the_atlas_at_the_records_pin(app, tmp_path):
    window = _window(_saga(tmp_path))
    window.open_ref(Ref("laboratories", "lab", "The Tower"))
    page = window.page()
    codex = getattr(page, "codex", None)
    assert codex is not None
    codex.open_chapter("Manage")
    _buttons(codex.pages.currentWidget())["Show on Map"].click()
    assert window.crumb_names() == ["Sagas", "Atlas Saga"]
    chapter = window.page().codex.pages.currentWidget()  # type: ignore[union-attr]
    assert isinstance(chapter, atlas_page.AtlasChapter)
    assert chapter.view is not None and chapter.view.chosen is not None
    assert "The Tower" in [s.ref.name for s in chapter.view.chosen.here]


def _click(view, x: float, y: float) -> None:
    spot = view.mapFromScene(QPointF(x, y))
    QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(spot))


def test_set_scale_from_the_bar_then_measure_between_pins(app, tmp_path):
    saga = _saga(tmp_path)
    window = _window(saga)
    chapter = _atlas(window)
    assert "Measure" not in _buttons(chapter)
    assert "No scale yet" in chapter.line.text()
    view = chapter.view
    assert view is not None
    _buttons(chapter)["Set Scale"].click()
    _click(view, 0, 90)
    assert "other end of the scale bar" in chapter.line.text()
    # The bar is a quarter of the map's 200-pixel width: 10 leagues.
    answering(window, {"length": "10", "unit": "leagues"})
    _click(view, 50, 90)
    rhine = storage.load_saga(saga.id).tribunals[0].maps[0]
    assert rhine.scale_miles == 30
    assert rhine.scale_bar == pytest.approx([0, 0.9, 0.25, 0.9], abs=0.01)
    # The chapter is drawn again, with Measure: let the new map settle.
    QApplication.processEvents()
    view = chapter.view
    assert view is not None
    assert "the bar is 10 leagues (30 miles)" in chapter.line.text()
    _buttons(chapter)["Measure"].click()
    # From the forest's pin (50, 25) to Durenmar's (100, 50): 55.9 pixels.
    _click(view, 51, 24)
    _click(view, 101, 51)
    assert "11 leagues (34 miles) in a straight line" in chapter.line.text()
    assert len(view.measured) == 3
    QTest.keyClick(view, Qt.Key.Key_Escape)
    assert view.measured == []
