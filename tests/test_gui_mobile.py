"""The desktop's Whereabouts: on a covenant's Overview with a stop or a
Mobile Hook, with Add, Edit, Delete and Plan Route; no Add a Stop on a
covenant that isn't mobile; and Detach and Rejoin on the Ships list."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from gui_steps import buttons as find_buttons
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
)
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.forms import ConfirmDialog
from ars_magica_manager.gui.ships import ShipEntry
from ars_magica_manager.gui.style.pieces import TIER_BADGE, tier_badge
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import (
    CovenantStop,
    Neighbour,
    Possession,
    Ship,
    VirtueFlawInstance,
)
from ars_magica_manager.sections import WHEREABOUTS_SECTION


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(*, stop: bool = True) -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    saga.neighbours.append(
        Neighbour("sound", "The Sound", kind="place", details={"aura": 2})
    )
    covenant = saga.covenants[0]
    covenant.possessions.append(
        Possession(id="cog", kind="ship", name="Cog", ship=Ship())
    )
    if stop:
        covenant.stops.append(
            CovenantStop(saga.current_year, saga.current_season, "sound")
        )
    storage.save_saga(saga)
    return _window_of(saga.id)


def _window_of(saga_id: str) -> tuple[MainWindow, str]:
    window = MainWindow(saga_ids=[saga_id])
    window.open_covenant("cov1")
    return window, saga_id


def _page(window: MainWindow) -> CovenantPage:
    page = window.page()
    assert isinstance(page, CovenantPage)
    return page


def test_whereabouts_shows_with_a_stop_and_plans_a_route(app):
    window, saga_id = _window()
    page = _page(window)
    buttons = section_buttons(page, "Whereabouts")
    assert list(buttons) == ["Add", "Edit", "Delete", "Plan Route"]
    assert "Add a Stop" not in section_buttons(page, "The Covenant")
    asked = answering(window, {"leg_0": "sound", "circuit": True})
    buttons["Plan Route"].click()
    assert len(asked) == 1
    covenant = storage.load_saga(saga_id).covenants[0]
    assert [leg.place_id for leg in covenant.route] == ["sound"] and covenant.circuit


def test_a_covenant_that_isnt_mobile_has_no_whereabouts_or_add_a_stop(app):
    window, _ = _window(stop=False)
    page = _page(window)
    assert not page.findChildren(QWidget, WHEREABOUTS_SECTION)
    for name in ("Hooks", "The Covenant"):
        assert "Add a Stop" not in section_buttons(page, name)


def test_detach_and_rejoin_are_ship_buttons(app):
    window, saga_id = _window()
    page = _page(window)
    page.codex.open_chapter("Inventory")
    page.codex.chapter(page.codex.chapters().index("Inventory")).findChildren(
        ShipEntry
    )[0].clicked()
    buttons = section_buttons(page, "Ships")
    assert buttons["Detach"].isEnabled() and not buttons["Rejoin"].isEnabled()
    answering(window, {"where": "sound"})
    buttons["Detach"].click()
    ship = storage.load_saga(saga_id).covenants[0].possessions[-1].ship
    assert [s.place_id for s in ship.stops] == ["sound"]


def test_a_ship_apart_says_so_on_her_entry(app):
    window, saga_id = _window()
    saga = storage.load_saga(saga_id)
    ship = saga.covenants[0].possessions[-1].ship
    ship.stops.append(CovenantStop(saga.current_year, saga.current_season, "sound"))
    storage.save_saga(saga)
    window, _ = _window_of(saga_id)
    page = _page(window)
    page.codex.open_chapter("Inventory")
    entry = page.codex.chapter(page.codex.chapters().index("Inventory")).findChildren(
        ShipEntry
    )[0]
    words = [label.text() for label in entry.findChildren(QLabel)]
    assert any("Apart from the fleet: at The Sound" in w for w in words)


def test_a_long_question_scrolls_so_its_buttons_stay_on_the_screen(app):
    words = "\n".join(f"Line {n}" for n in range(300))
    dialog = ConfirmDialog(words, SCRIPTORUM, None, yes_label="Import")
    assert dialog.minimumSizeHint().height() < 800
    assert dialog.findChildren(QScrollArea)


def test_suggest_a_story_leaves_the_hooks_title_row_and_its_cards_stay_level(app):
    saga = _sample_saga_with_covenant()
    saga.covenants[0].boons_hooks.extend(
        [
            VirtueFlawInstance("covbh_boon_minor_aura"),
            VirtueFlawInstance("covbh_hook_minor_rival"),
        ]
    )
    storage.save_saga(saga)
    window, _ = _window_of(saga.id)
    page = _page(window)
    assert "Suggest a Story" not in section_buttons(page, "Hooks")
    story = find_buttons(page, "Suggest a Story")[0]
    line = story.parentWidget()
    assert line is not None and any(
        label.text().endswith("provided") for label in line.findChildren(QLabel)
    )
    window.resize(1400, 1000)
    window.show()
    QApplication.processEvents()
    tops = {
        label.mapToGlobal(QPoint()).y()
        for label in page.findChildren(QLabel)
        if label.text() == "Minor" and label.isVisible()
    }
    assert len(tops) == 1


@pytest.mark.parametrize("tier", ["Free", "Minor", "Major"])
def test_a_tier_pill_is_one_size_whatever_its_word_or_card(app, tier):
    row = QWidget()
    layout = QHBoxLayout(row)
    tall = QLabel("A name\nthat wraps\nover three lines")
    pill = tier_badge(tier, SCRIPTORUM["accent"], SCRIPTORUM)
    layout.addWidget(tall, 1)
    layout.addWidget(pill, 0, Qt.AlignmentFlag.AlignTop)
    row.show()
    QApplication.processEvents()
    assert pill.size() == TIER_BADGE
