"""The desktop version's Character sheet builds, offscreen, from a sample
saga, and shows the same core text as the terminal sheet."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import character_sheet as cs
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.figures import Dial
from ars_magica_manager.gui.markup_html import plain, to_html
from ars_magica_manager.gui.pages import CovenantPage, SagaPage
from ars_magica_manager.gui.themes import PALETTES, SCRIPTORUM
from ars_magica_manager.gui.timeline import SEASON
from ars_magica_manager.gui.widgets import XP_BAR, ClickableCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import DiaryEntry, SeasonPlan


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _texts(widget) -> str:
    return "\n".join(plain(label.text()) for label in widget.findChildren(QLabel))


def _sheet(saga=None) -> CharacterSheet:
    window = MainWindow(saga_ids=[])
    saga = saga or _sample_saga_with_covenant()
    window.load(saga)
    window.show_character(saga.characters[0].id)
    sheet = window.sheet_area.findChild(CharacterSheet)
    assert sheet is not None
    sheet.window_ = window  # keep the window alive with the sheet
    return sheet


def test_the_window_shows_the_first_characters_sheet_with_every_chapter(app):
    sheet = _sheet()
    assert sheet.chapters() == [
        "Description",
        "Abilities",
        "Virtues & Flaws",
        "Hermetic Magic",
        "Inventory",
        "Planning",
        "Diary",
    ]
    shown = _texts(sheet)
    assert "Test Covenant" in shown
    assert "Fresh" in shown and "Unhurt" in shown


def test_the_arts_tables_show_each_arts_score_and_experience(app):
    sheet = _sheet()
    techniques = sheet.technique_view.model()
    assert techniques.index(0, 0).data() == "Creo"
    assert techniques.index(0, 1).data() == "10"
    assert techniques.index(0, 2).data(XP_BAR) == (0.0, "55 / 66 xp")
    assert sheet.form_view.model().rowCount() == 10


def test_choosing_an_art_shows_it_in_the_inspector(app):
    sheet = _sheet()
    view = sheet.technique_view
    view.setCurrentIndex(view.model().index(0, 0))
    assert sheet.inspector.title.text() == "Creo"


def test_the_dials_wind_up_to_the_points_toward_the_next_score(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].aging.warping_score = 2
    saga.characters[0].aging.warping_points = 9
    sheet = _sheet(saga)
    warping = next(d for d in sheet.findChildren(Dial) if d.caption == "Warping")
    assert (warping.dial.score, warping.dial.points, warping.dial.span) == (2, 9, 15)
    assert warping.wind.endValue() == pytest.approx(0.6)


def test_choosing_a_casting_score_shows_its_terms_in_the_inspector(app):
    sheet = _sheet()
    view = sheet.casting_view
    view.clicked.emit(view.model().index(0, 5))  # Creo Ignem
    assert sheet.inspector.title.text() == "Creo Ignem"
    assert "Casting Score" in plain(sheet.inspector.body.text())


def test_the_spell_filter_hides_spells_whose_names_dont_match(app):
    sheet = _sheet()
    assert sheet.spell_view.model().rowCount() == 1
    sheet.spell_filter.setText("abysmal")
    assert sheet.spell_view.model().rowCount() == 1
    sheet.spell_filter.setText("pilum")
    assert sheet.spell_view.model().rowCount() == 0


def test_the_theme_toggle_redraws_the_sheet_in_the_other_palette(app):
    window = MainWindow(saga_ids=[])
    saga = _sample_saga_with_covenant()
    window.load(saga)
    window.show_character(saga.characters[0].id)
    window.toggle_theme()
    assert window.palette_ is PALETTES[1]
    assert window.character_id == saga.characters[0].id
    assert window.sheet_area.findChild(CharacterSheet) is not None


def test_a_saga_opens_at_its_covenants_and_the_trail_leads_back(app):
    window = MainWindow(saga_ids=[])
    saga = _sample_saga_with_covenant()
    window.load(saga)
    assert window.sheet_area.findChild(SagaPage) is not None
    assert window.crumb_names() == ["Sagas", saga.name]
    covenant = next(c for c in window.findChildren(ClickableCard))
    covenant.clicked()
    assert window.crumb_names() == ["Sagas", saga.name, "Test Covenant"]
    page = window.sheet_area.findChild(CovenantPage)
    assert page is not None
    assert page.codex.chapters() == ["People", "Laboratories", "Seasons"]
    people = page.codex.pages.widget(0)
    person = next(
        card
        for card in people.findChildren(ClickableCard)
        if saga.characters[0].name in _texts(card)
    )
    person.clicked()
    assert window.character_id == saga.characters[0].id
    window.go(window.trail[:2])  # the saga's crumb
    assert window.sheet_area.findChild(SagaPage) is not None


def test_the_covenant_timeline_shows_each_persons_seasons(app):
    saga = _sample_saga_with_covenant()
    character = saga.characters[0]
    character.diary.append(DiaryEntry(1219, "Winter", "", "", "Read a book"))
    saga.season_plans.append(SeasonPlan(character.id, 1220, "Spring", "invent_spell"))
    window = MainWindow(saga_ids=[])
    window.load(saga)
    window.open_covenant(saga.covenants[0].id)
    page = window.sheet_area.findChild(CovenantPage)
    assert page is not None
    view = page.timeline
    current = view.timeline.current
    assert view.model().index(0, current).data(SEASON).label == "Invent a spell"
    view.setCurrentIndex(view.model().index(0, current - 1))
    assert page.codex.inspector.subtitle.text() == "Winter 1219"
    assert "Read a book" in plain(page.codex.inspector.body.text())


def test_the_diary_opens_with_a_calendar_of_the_characters_seasons(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].diary.append(DiaryEntry(1219, "Autumn", "", "", "Practice"))
    sheet = _sheet(saga)
    model = sheet.calendar.view.model()
    assert model.headerData(1, Qt.Orientation.Vertical) == "1219"
    assert model.index(1, 2).data(SEASON).kind == "Study"


def test_markup_becomes_spans_in_the_palettes_colours():
    html = to_html("[b]Name:[/] [$label]x \\[y][/]", SCRIPTORUM)
    assert html == (
        '<span style="font-weight:600">Name:</span> '
        f'<span style="color:{SCRIPTORUM["label"]}">x [y]</span>'
    )
    assert plain("[i $label]1220[/]") == "1220"


def test_an_art_row_carries_its_score_and_experience():
    character = _sample_saga_with_covenant().characters[0]
    row = cs.art_row(character, "Creo")
    assert (row.abbreviation, row.score, row.xp) == ("Cr", "10", 55)
    assert (row.level_xp, row.next_xp, row.fraction) == (55, 66, 0.0)
