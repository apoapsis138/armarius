"""The season medallions on the desktop's pages: the headpiece band, the
Seasons page, Ahead, the covenant's header and Seasons chapter, a
character's This Season and the calendars each draw the season through
gui.medallions, in the saga's own set, and none of them clips any set."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtCore import QPoint, QPointF
from PySide6.QtGui import QImage, QPainter, QRegion
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget
from support import everything_saga

from ars_magica_manager import medallions, storage
from ars_magica_manager.gui import medallions as drawn
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.figures import FigureSeal, Seal, SeasonSeal
from ars_magica_manager.gui.medallions import Medallion, SeasonHeadpiece
from ars_magica_manager.gui.themes import PALETTES
from ars_magica_manager.gui.timeline import SeasonHeader
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import SEASONS, Saga, SeasonRecord

SET = "enamel"
#: The radius a season seal draws its medallion at.
SEAL_RADIUS = Seal.DISC.height() / 2 / 1.06


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window() -> tuple[MainWindow, Saga]:
    saga = everything_saga()
    saga.medallions = SET
    saga.season_records.append(SeasonRecord(1219, "Winter", []))
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.resize(1400, 900)
    window.show()
    assert window.saga is not None
    return window, window.saga


def _shown(window: MainWindow) -> list[Medallion]:
    """The medallions on the page and chapter on show."""
    QApplication.processEvents()
    page = window.page()
    assert page is not None
    return [m for m in page.findChildren(Medallion) if m.isVisibleTo(window)]


def _chapter(window: MainWindow, name: str) -> None:
    page = window.page()
    assert page is not None
    page.codex.open_chapter(name)  # type: ignore[attr-defined]
    QApplication.processEvents()


def _now(saga: Saga) -> tuple[str, int]:
    return saga.current_season, saga.current_year


def test_the_seasons_page_title_chapters_and_ahead(app):
    window, saga = _window()
    window.open_seasons()
    title = [m for m in _shown(window) if m.radius == 24]
    assert [(m.season, m.year, m.now) for m in title] == [(*_now(saga), True)]
    winter = next(n for n in window.page().chapters() if n.startswith("Winter 1219"))  # type: ignore[union-attr]
    _chapter(window, winter)
    heading = [m for m in _shown(window) if m.radius == 20]
    assert [(m.season, m.year, m.now) for m in heading] == [("Winter", 1219, False)]
    _chapter(window, "Ahead")
    ahead = [m for m in _shown(window) if m.radius == 16]
    assert ahead, "each season in Ahead has its medallion"
    assert [(m.season, m.year) for m in ahead if m.now] == [_now(saga)]
    assert all(m.saga is saga for m in _shown(window))


def test_the_covenant_header_and_seasons_chapter(app):
    window, saga = _window()
    window.open_covenant("cov1")
    # The header shows the covenant's own season as a seal named under it,
    # the same size as the aura and Loyalty seals and level with them.
    covenant = saga.covenant("cov1")
    assert covenant is not None
    QApplication.processEvents()
    page = window.page()
    assert page is not None
    seals = [s for s in page.findChildren(Seal) if s.isVisibleTo(window)]
    season = [s for s in seals if isinstance(s, SeasonSeal)]
    assert [(s.season, s.caption) for s in season] == [
        (covenant.covenant_season, covenant.covenant_season)
    ]
    others = [s for s in seals if not isinstance(s, SeasonSeal)]
    assert {s.caption for s in others} >= {"Loyalty"}
    assert all(isinstance(s, FigureSeal) for s in others)
    for seal in others:
        assert seal.size() == season[0].size()
        top = seal.mapTo(window, QPoint()).y()
        assert top == season[0].mapTo(window, QPoint()).y(), seal.caption
    _chapter(window, "Seasons")
    radii = sorted({m.radius for m in _shown(window)})
    assert 20 in radii and 16 in radii, "the chapter's title and its Ahead"
    title = next(m for m in _shown(window) if m.radius == 20)
    assert (title.season, title.year, title.now) == (*_now(saga), True)


def test_this_season_keeps_its_buttons_level_with_its_title(app):
    window, saga = _window()
    window.show_character("mag1")
    _chapter(window, "Planning")
    medallion = next(m for m in _shown(window) if m.radius == 20)
    assert (medallion.season, medallion.now) == (saga.current_season, True)
    page = window.page()
    assert page is not None
    title = next(
        label
        for label in page.findChildren(QLabel)
        if label.text().startswith("This Season (")
    )
    centre = title.mapTo(window, title.rect().center()).y()
    buttons = [
        b
        for b in title.parentWidget().parentWidget().findChildren(QPushButton)  # type: ignore[union-attr]
        if b.isVisibleTo(window)
    ]
    assert buttons
    for button in buttons:
        middle = button.mapTo(window, button.rect().center()).y()
        assert abs(middle - centre) <= 8, (button.text(), middle, centre)


@pytest.mark.parametrize(
    ("open_record", "chapter"),
    [
        (lambda w: w.show_character("mag1"), "Diary"),
        (lambda w: w.open_laboratory("lab1"), "Seasons"),
    ],
    ids=["character", "laboratory"],
)
def test_a_calendar_heads_its_columns_with_medallions(app, open_record, chapter):
    window, saga = _window()
    open_record(window)
    _chapter(window, chapter)
    page = window.page()
    header = page.calendar.view.horizontalHeader()  # type: ignore[union-attr]
    assert isinstance(header, SeasonHeader)
    assert header.saga is saga
    assert header.sizeHint().height() == 2 * SeasonHeader.RADIUS + 26


def test_every_placement_draws_in_the_saga_set(app, monkeypatch):
    window, saga = _window()
    drew: list[tuple[str, float, str]] = []

    def recorder(key: str):
        def painter(_g, _c, r, season, _year, _p) -> None:
            drew.append((key, r, season))

        return painter

    for key in medallions.KEYS:
        monkeypatch.setitem(drawn.PAINTERS, key, recorder(key))

    def drawn_on(show) -> set[float]:
        show()
        QApplication.processEvents()
        drew.clear()
        window.grab()
        assert {key for key, _r, _s in drew} == {SET}
        return {r for _key, r, _s in drew}

    assert drawn_on(lambda: window.open_seasons()) >= {17, 24, 16}
    assert drawn_on(lambda: window.open_covenant("cov1")) >= {17, SEAL_RADIUS}
    assert drawn_on(lambda: _chapter(window, "Seasons")) >= {20, 16}
    window.show_character("mag1")
    assert drawn_on(lambda: _chapter(window, "Planning")) >= {20}
    assert drawn_on(lambda: _chapter(window, "Diary")) >= {16}
    # Another set chosen: the next paint uses it.
    saga.medallions = "wax_seal"
    window.redraw()
    QApplication.processEvents()
    drew.clear()
    window.grab()
    assert {key for key, _r, _s in drew} == {"wax_seal"}


def test_the_headpiece_carries_the_present_season(app):
    window, saga = _window()
    assert isinstance(window.headpiece, SeasonHeadpiece)
    assert window.headpiece.height() == SeasonHeadpiece.HEIGHT == 46
    assert window.headpiece.saga is saga
    answering(window, True)
    window.advance.click()
    QApplication.processEvents()
    advanced = window.saga
    assert advanced is not None and advanced.current_season == SEASONS[1]
    assert window.headpiece.saga is advanced
    title = next(m for m in _shown(window) if m.radius == 24)
    assert (title.season, title.now) == (SEASONS[1], True)
    window._shelf_again()
    assert window.headpiece.saga is None


def _opaque_on_edge(image: QImage) -> list[tuple[int, int]]:
    w, h = image.width(), image.height()
    edge = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
    edge += [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    return [(x, y) for x, y in edge if image.pixelColor(x, y).alpha() > 8]


@pytest.mark.parametrize("key", medallions.KEYS)
def test_no_set_clips_in_the_headpiece_or_a_medallion(app, key):
    saga = everything_saga()
    saga.medallions = key
    for p in PALETTES:
        # The headpiece: inside the band's height, and inside its dots.
        band = QImage(
            2 * SeasonHeadpiece.INNER - 6,
            SeasonHeadpiece.HEIGHT,
            QImage.Format.Format_ARGB32,
        )
        for season in SEASONS:
            band.fill(0)
            g = QPainter(band)
            drawn.paint_season(
                g,
                saga,
                QPointF(band.width() / 2, band.height() / 2),
                SeasonHeadpiece.RADIUS,
                season,
                1220,
                p,
            )
            g.end()
            assert _opaque_on_edge(band) == [], (key, season, "headpiece")
        # A Medallion widget, glowing, at the smallest and largest sizes.
        for radius in (16, 31):
            widget = Medallion(saga, "Spring", 1220, p, radius=radius, now=True)
            image = QImage(widget.size(), QImage.Format.Format_ARGB32)
            image.fill(0)
            widget.render(image, QPoint(), QRegion(), QWidget.RenderFlag.DrawChildren)
            assert _opaque_on_edge(image) == [], (key, radius)
            assert image.pixelColor(image.width() // 2, image.height() // 2).alpha()
            widget.deleteLater()
        # The covenant header's season seal.
        for season in SEASONS:
            widget = SeasonSeal(saga, season, "", p)
            image = QImage(widget.size(), QImage.Format.Format_ARGB32)
            image.fill(0)
            widget.render(image, QPoint(), QRegion(), QWidget.RenderFlag.DrawChildren)
            assert _opaque_on_edge(image) == [], (key, season, "seal")
            widget.deleteLater()
        # A figure (an aura, a Loyalty) drawn as a medallion in one colour.
        widget = FigureSeal(saga, "+2", "Loyalty", p["text-success"], "", p)
        image = QImage(widget.size(), QImage.Format.Format_ARGB32)
        image.fill(0)
        widget.render(image, QPoint(), QRegion(), QWidget.RenderFlag.DrawChildren)
        assert _opaque_on_edge(image) == [], (key, "figure")
        widget.deleteLater()


def test_a_medallion_widget_names_its_season(app):
    saga = everything_saga()
    widget: QWidget = Medallion(saga, "Autumn", 1221, PALETTES[0], now=True)
    assert widget.toolTip() == "Autumn 1221 (now)"
    captioned = Medallion(saga, "Autumn", 1221, PALETTES[0], caption=True)
    assert captioned.height() == captioned.width() + 20
