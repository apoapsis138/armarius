"""The desktop version's Character sheet builds, offscreen, from a sample
saga, and shows the same core text as the terminal sheet."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGraphicsDropShadowEffect,
    QLabel,
    QPushButton,
    QScrollArea,
)
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import familiars as fam
from ars_magica_manager import storage
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.gui import choices, pictures, sounds
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.familiar import FamiliarPage
from ars_magica_manager.gui.figures import Bookcase, BookSpine, CordFigure, Dial, prose
from ars_magica_manager.gui.forms import ConfirmDialog, FieldsDialog
from ars_magica_manager.gui.laboratory import LaboratoryPage
from ars_magica_manager.gui.markup_html import plain, to_html
from ars_magica_manager.gui.ornaments import FleuronRule, Headpiece, Tailpiece
from ars_magica_manager.gui.pages import SagaPage
from ars_magica_manager.gui.paper import Paper, _paper, paper
from ars_magica_manager.gui.saga_content import SagaContentPage
from ars_magica_manager.gui.themes import PALETTES, SCRIPTORUM
from ars_magica_manager.gui.timeline import SEASON
from ars_magica_manager.gui.widgets import (
    XP_BAR,
    ClickableCard,
    GiltName,
    RuledRows,
    XpBarDelegate,
    level_box,
)
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import (
    BondPower,
    DiaryEntry,
    IncomeSource,
    Inhabitant,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.sheets import character as cs
from ars_magica_manager.sheets import covenant as cvs


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
        "Secrets",
        "Manage",
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


def test_the_pages_lie_on_paper_and_their_cards_cast_shadows(app):
    window = MainWindow(saga_ids=[])
    window.load(_sample_saga_with_covenant())
    body = window.stack.widget(0)
    assert isinstance(body, Paper) and body.p is PALETTES[0]
    card = window.findChildren(ClickableCard)[0]
    assert isinstance(card.graphicsEffect(), QGraphicsDropShadowEffect)
    window.toggle_theme()
    assert body.p is PALETTES[1]


def test_the_pages_are_set_with_printers_ornaments(app):
    window = MainWindow(saga_ids=[])
    saga = _sample_saga_with_covenant()
    window.load(saga)
    window.show_character(saga.characters[0].id)
    sheet = window.sheet_area.findChild(CharacterSheet)
    assert sheet is not None
    headpiece = window.findChild(Headpiece)
    assert headpiece is not None and headpiece.p is PALETTES[0]
    # Each heading's rule opens with a hedera leaf and each chapter ends
    # with a tailpiece.
    assert sheet.findChildren(FleuronRule)
    assert len(sheet.findChildren(Tailpiece)) >= len(sheet.chapters()) - 1
    window.resize(1400, 900)
    window.grab()  # the ornaments and the cards' corner flourishes paint
    window.toggle_theme()
    assert headpiece.p is PALETTES[1]


def test_the_tables_are_ruled_as_a_ledger_and_keep_their_own_cells(app):
    sheet = _sheet()
    sheet.codex.open_chapter("Abilities")
    table = sheet.ability_table
    # No stripes; each delegate is wrapped, the experience column's too.
    assert not table.alternatingRowColors()
    assert isinstance(table.itemDelegate(), RuledRows)
    last = table.itemDelegateForColumn(table.model().columnCount() - 1)
    assert isinstance(last, RuledRows) and isinstance(last.inner, XpBarDelegate)
    first = table.model().index(0, 0)
    table.setCurrentIndex(table.model().index(0, 0, first))
    sheet.window_.resize(1400, 900)
    sheet.window_.grab()  # the ruling, wash and ink lines paint


def test_selections_scroll_bars_and_the_inspector_are_gilded(app):
    sheet = _sheet()
    p = sheet.p
    palette = QApplication.instance().palette()
    # Whatever the platform draws itself is chosen in the theme's colours,
    # not the system's accent.
    assert palette.color(QPalette.ColorRole.Highlight) == QColor(p["selection"])
    assert palette.color(QPalette.ColorRole.Accent) == QColor(p["accent"])
    assert sheet.inspector.body.font().family() == pictures.SERIF
    # The record's name is drawn whole, its initial with a gilt edge.
    name = sheet.findChild(GiltName)
    assert name is not None and name.name == sheet.character.name
    sheet.inspect("Pilum of Fire", "Creo Ignem 20", "Notes. " * 400)
    sheet.window_.resize(1400, 900)
    sheet.window_.show()
    bar = sheet.inspector.findChild(QScrollArea).verticalScrollBar()
    assert bar.maximum() > 0
    # The rod is drawn in gold where the scroll bar's handle is.
    shot = bar.grab().toImage()
    middle = shot.pixelColor(shot.width() // 2, 20)
    assert middle.red() > middle.blue() + 100
    sheet.window_.close()


def test_a_form_draws_its_fields_and_refuses_what_does_not_parse(app):
    dialog = FieldsDialog(
        "Edit Something",
        [
            DialogField("name", "Name", "text", "Hilde", required=True),
            DialogField("age", "Age", "optint", 30),
            DialogField(
                "hand",
                "Hand",
                "select",
                "left",
                options=[("Left", "left"), ("Right", "right")],
            ),
            DialogField("dead", "Dead", "check", False),
            DialogField("notes", "Notes", "area", "Quiet."),
            DialogField("owner", "Owner", "info", "Leandro"),
            DialogField(
                "why", "Why", "text", "", show_if=lambda v: bool(v.get("dead"))
            ),
        ],
        PALETTES[0],
    )
    assert dialog.read(dialog.fields[2]) == "left"
    assert not dialog.rows["why"][1].isVisibleTo(dialog)
    dialog.set_value("age", "thirty")
    dialog.try_save()
    assert dialog.result() != dialog.DialogCode.Accepted
    assert "Age must be a whole number" in dialog.error.text()
    dialog.set_value("age", "")
    dialog.set_value("dead", True)
    assert dialog.rows["why"][1].isVisibleTo(dialog)
    dialog.set_value("why", "  a fall  ")
    dialog.try_save()
    assert dialog.result() == dialog.DialogCode.Accepted
    assert dialog.values == {
        "name": "Hilde",
        "age": None,
        "hand": "left",
        "dead": True,
        "notes": "Quiet.",
        "why": "a fall",
    }


def test_a_drop_down_is_an_inked_blank_with_a_purple_bookmark(app):
    window = MainWindow(saga_ids=[])
    dialog = FieldsDialog(
        "Pick",
        [
            DialogField(
                "hand",
                "Hand",
                "select",
                "left",
                options=[("Left", "left"), ("Right", "right"), ("Both", "both")],
            )
        ],
        PALETTES[0],
        window,
    )
    dialog.resize(400, 160)
    dialog.show()
    app.processEvents()
    combo = dialog.inputs["hand"]
    assert isinstance(combo, QComboBox)
    assert isinstance(combo.itemDelegate(), choices.InkSlipRows)
    closed = combo.grab().toImage()
    ribbon = closed.pixelColor(closed.width() - 12, closed.height() // 2)
    assert ribbon.blue() > ribbon.green() + 40 and ribbon.red() > ribbon.green()
    # Open, the chosen line is washed in purple and the others are not.
    combo.showPopup()
    app.processEvents()
    view = combo.view()
    lines = view.viewport().grab().toImage()

    def purple(row: int) -> int:
        y = view.visualRect(combo.model().index(row, 0)).center().y()
        colour = lines.pixelColor(choices.MARGIN + 4, y)
        return colour.blue() - colour.green()

    assert purple(0) > purple(2) + 8
    combo.hidePopup()
    dialog.close()
    window.close()


def test_a_spin_box_is_an_inked_blank_with_purple_steps(app):
    window = MainWindow(saga_ids=[])
    spin = level_box("Level")
    spin.setParent(window)
    spin.resize(160, 34)
    spin.show()
    app.processEvents()
    image = spin.grab().toImage()

    def purple_at(x: int) -> int:
        return max(
            image.pixelColor(x, y).blue() - image.pixelColor(x, y).green()
            for y in range(image.height())
        )

    # The up step is lit; at "any" (its lowest) the down step is faint.
    steps = image.width() - 10
    assert purple_at(steps) > 40
    window.close()


def test_editing_a_section_saves_the_saga_and_stays_on_its_chapter(app):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    character = window.saga.characters[0] if window.saga else None
    assert character is not None
    window.show_character(character.id)
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    sheet.open_chapter("Abilities")
    sheet.open_chapter("Description")
    asked: list[FieldsDialog] = []

    def answer(dialog):
        asked.append(dialog)
        dialog.set_value("hair", "Grey")
        dialog.try_save()
        return dialog.result()

    window.ask = answer
    section_buttons(sheet, "Biographical Detail")["Edit"].click()
    assert asked[0].windowTitle() == "Edit Biographical Detail"
    assert storage.load_saga(saga.id).characters[0].description.hair == "Grey"
    page = window.page()
    assert isinstance(page, CharacterSheet) and page is not sheet
    assert page.codex.rail.currentRow() == 0
    # Cancelling changes nothing.
    window.ask = lambda dialog: dialog.DialogCode.Rejected
    next(
        b for b in page.findChildren(QPushButton) if b.text().strip() == "Fatigue"
    ).click()
    assert window.page() is page


def test_paper_is_the_same_every_time_it_is_made(app):
    assert _paper(PALETTES[0]) == _paper(PALETTES[0])
    assert paper(PALETTES[0]) is paper(PALETTES[0])


def test_a_saga_opens_at_its_covenants_and_the_trail_leads_back(app):
    window = MainWindow(saga_ids=[])
    saga = _sample_saga_with_covenant()
    window.load(saga)
    assert window.sheet_area.findChild(SagaPage) is not None
    assert window.crumb_names() == ["Sagas", saga.name]
    # The World, the chapter on show, leads with the covenants.
    covenant = next(
        c for c in window.findChildren(ClickableCard) if c.isVisibleTo(window)
    )
    covenant.clicked()
    assert window.crumb_names() == ["Sagas", saga.name, "Test Covenant"]
    page = window.sheet_area.findChild(CovenantPage)
    assert page is not None
    assert page.codex.chapters() == [
        "Charter",
        "People",
        "Covenfolk",
        "Laboratories",
        "Possessions",
        "Treasury",
        "Library",
        "Seasons",
        "Diary",
        "Build",
        "Secrets",
        "Manage",
    ]
    people = _chapter(page, "People")
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


def _chapter(page, name: str):
    return page.codex.chapter(page.codex.chapters().index(name))


def _lab_page(window: MainWindow, saga) -> LaboratoryPage:
    window.load(saga)
    window.open_covenant(saga.covenants[0].id)
    covenant = window.sheet_area.findChild(CovenantPage)
    assert covenant is not None
    labs = _chapter(covenant, "Laboratories")
    next(iter(labs.findChildren(ClickableCard))).clicked()
    page = window.sheet_area.findChild(LaboratoryPage)
    assert page is not None
    return page


def test_a_laboratory_opens_from_its_covenants_card_with_every_chapter(app):
    window = MainWindow(saga_ids=[])
    saga = _sample_saga_with_covenant()
    page = _lab_page(window, saga)
    assert window.crumb_names() == [
        "Sagas",
        saga.name,
        "Test Covenant",
        "Leandro's Sanctum",
    ]
    assert page.chapters() == [
        "Lab Totals",
        "Virtues & Flaws",
        "Specializations",
        "Stores",
        "Seasons",
        "Manage",
    ]
    assert "Superior Construction" in _texts(page)


def test_choosing_a_lab_total_or_characteristic_shows_it_in_the_inspector(app):
    window = MainWindow(saga_ids=[])
    page = _lab_page(window, _sample_saga_with_covenant())
    view = page.totals_view
    assert view is not None
    view.clicked.emit(view.model().index(0, 5))  # Creo Ignem
    assert page.inspector.title.text() == "Creo Ignem"
    assert "Lab Total 26" in plain(page.inspector.body.text())
    safety = page.characteristic_cards[4]
    safety.clicked()
    assert page.inspector.title.text() == "Safety"


def test_a_laboratorys_calendar_shows_its_diary(app):
    saga = _sample_saga_with_covenant()
    saga.laboratories[0].diary.append(
        DiaryEntry(1219, "Autumn", "", "", "Invent a spell")
    )
    page = _lab_page(MainWindow(saga_ids=[]), saga)
    model = page.calendar.view.model()
    assert model.headerData(1, Qt.Orientation.Vertical) == "1219"
    assert model.index(1, 2).data(SEASON).kind == "Laboratory"


def _covenant_page(saga) -> CovenantPage:
    window = MainWindow(saga_ids=[])
    window.load(saga)
    window.open_covenant(saga.covenants[0].id)
    page = window.sheet_area.findChild(CovenantPage)
    assert page is not None
    page.window_ = window  # keep the window alive with the page
    return page


def test_the_unassigned_have_only_their_people_and_seasons(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].covenant_id = None
    window = MainWindow(saga_ids=[])
    window.load(saga)
    window.open_covenant(None)
    page = window.sheet_area.findChild(CovenantPage)
    assert page is not None
    assert page.chapters() == ["People", "Seasons"]


def test_choosing_a_boon_or_an_inhabitant_shows_it_in_the_inspector(app):
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    covenant.boons_hooks.append(VirtueFlawInstance("covbh_boon_major_wealth"))
    covenant.inhabitants.append(
        Inhabitant("i1", "turb", "The watch", quantity=6, responsibility="Walls")
    )
    page = _covenant_page(saga)
    boon = next(
        card
        for card in _chapter(page, "Charter").findChildren(ClickableCard)
        if "Wealth" in _texts(card)
    )
    boon.clicked()
    assert page.inspector.title.text() == "Wealth"
    assert "Major" in page.inspector.subtitle.text()
    turb = page.tables["turb"]
    turb.setCurrentIndex(turb.model().index(0, 0))
    assert page.inspector.title.text() == "The watch"
    assert "Walls" in plain(page.inspector.body.text())


def test_the_library_stands_the_books_on_shelves(app):
    page = _covenant_page(_sample_saga_with_covenant())
    spines = _chapter(page, "Library").findChildren(BookSpine)
    assert [s.spine.book.name for s in spines] == [
        "On the Theory of Magic",
        "Ball of Abysmal Flame",
    ]
    spines[0].clicked()
    assert page.inspector.title.text() == "On the Theory of Magic"


def test_a_narrower_bookcase_moves_books_down_a_shelf(app):
    saga = _sample_saga_with_covenant()
    spines = [s for _, shelf_ in cvs.shelves(saga, saga.covenants[0]) for s in shelf_]
    case = Bookcase(spines * 10, SCRIPTORUM)
    case.show()
    case.resize(1000, case.height())
    wide = len(case.rows)
    case.resize(300, case.height())
    assert len(case.rows) > wide
    assert all(book.geometry().right() < 300 for book in case.books)


def _with_familiar():
    saga = _sample_saga_with_covenant()
    magus = next(c for c in saga.characters if c.type == "magus")
    familiar = fam.bind_familiar(saga, magus, "Nox")
    familiar.bond_powers = [BondPower("b1", "Silent Wings", 10, "Perdo", "Imaginem")]
    return saga, magus, familiar


def test_a_familiar_opens_from_its_covenants_people_below_its_magus(app):
    saga, magus, _familiar = _with_familiar()
    page = _covenant_page(saga)
    window = page.window_
    cards = _chapter(page, "People").findChildren(ClickableCard)
    next(c for c in cards if "Nox" in _texts(c)).clicked()
    familiar_page = window.sheet_area.findChild(FamiliarPage)
    assert familiar_page is not None
    assert window.crumb_names() == [
        "Sagas",
        saga.name,
        "Test Covenant",
        magus.name,
        "Nox",
    ]
    assert familiar_page.chapters() == [
        "Identity & Cords",
        "Virtues & Flaws",
        "Combat & Health",
        "Abilities",
        "Bond Powers",
        "Manage",
    ]
    power = _chapter(familiar_page, "Bond Powers").findChildren(ClickableCard)[0]
    power.clicked()
    assert familiar_page.inspector.title.text() == "Silent Wings"


def test_each_cord_is_drawn_in_its_metal_with_a_knot_per_point(app):
    saga, _magus, familiar = _with_familiar()
    familiar.golden_cord, familiar.bronze_cord = 3, 1
    page = FamiliarPage(saga, familiar, SCRIPTORUM)
    cords = _chapter(page, "Identity & Cords").findChildren(CordFigure)
    assert [(c.score, c.metal) for c in cords] == [
        (3, SCRIPTORUM["cord-golden"]),
        (0, SCRIPTORUM["cord-silver"]),
        (1, SCRIPTORUM["cord-bronze"]),
    ]


def test_a_magus_sheet_shows_their_familiar(app):
    saga, magus, _familiar = _with_familiar()
    sheet = _sheet(saga)
    if sheet.character.id != magus.id:
        sheet.window_.show_character(magus.id)
        sheet = sheet.window_.sheet_area.findChild(CharacterSheet)
    cards = _chapter(sheet, "Description").findChildren(ClickableCard)
    assert any("Nox" in _texts(card) for card in cards)


def test_saga_content_opens_from_the_saga_page_with_its_chapters(app):
    saga = _sample_saga_with_covenant()
    window = MainWindow(saga_ids=[])
    window.load(saga)
    window.sheet_area.findChild(SagaPage).content.clicked()
    page = window.sheet_area.findChild(SagaContentPage)
    assert page is not None
    assert window.crumb_names() == ["Sagas", saga.name, "Saga Content"]
    assert page.chapters() == [
        "Books",
        "Catalogs",
        "House Rules",
        "Spells",
        "Players",
    ]


def test_the_spells_filter_as_on_the_terminal_and_show_in_the_inspector(app):
    page = SagaContentPage(_sample_saga_with_covenant(), SCRIPTORUM)
    every = page.spell_model.rowCount()
    assert every == len(page.all_spells) > 100
    page.spell_technique.setCurrentIndex(page.spell_technique.findData("Creo"))
    page.spell_form.setCurrentIndex(page.spell_form.findData("Ignem"))
    assert 0 < page.spell_model.rowCount() < every
    assert all(
        spell.technique == "Creo" or "Creo" in spell.requisites
        for spell in page.shown_spells
    )
    page.spell_view.selectRow(0)
    chosen = page.spell_view.model().index(0, 0).data()
    assert page.inspector.title.text() == chosen


def test_spells_sort_by_level_as_numbers(app):
    page = SagaContentPage(_sample_saga_with_covenant(), SCRIPTORUM)
    page.spell_view.sortByColumn(2, Qt.SortOrder.DescendingOrder)
    model = page.spell_view.model()
    levels = [model.index(r, 2).data() for r in range(5)]
    assert levels == sorted(
        levels, key=lambda v: -1 if v == "Gen" else int(v), reverse=True
    )


def test_the_treasury_shows_the_years_balance(app):
    saga = _sample_saga_with_covenant()
    saga.covenants[0].economics.income_sources = [IncomeSource("s1", "Mill", income=40)]
    page = _covenant_page(saga)
    shown = _texts(_chapter(page, "Treasury"))
    assert "40 £" in shown
    assert page.tables["income"].model().index(0, 0).data() == "Mill"


def test_markup_becomes_spans_in_the_palettes_colours():
    html = to_html("[b]Name:[/] [$label]x \\[y][/]", SCRIPTORUM)
    assert html == (
        '<span style="font-weight:700">Name:</span> '
        f'<span style="color:{SCRIPTORUM["label"]}">x [y]</span>'
    )
    assert plain("[i $label]1220[/]") == "1220"


def test_struck_text_and_list_lines_become_html():
    assert to_html("[s]gone[/s]", SCRIPTORUM) == (
        '<span style="text-decoration:line-through">gone</span>'
    )
    html = to_html("Found:\n• [b]Study[/b], sealed\n  • nested\n10. ten", SCRIPTORUM)
    # Each list line is a row: its bullet or number in one cell and its
    # words in the next, so a wrapped line hangs under the words.
    assert html.count("<table") == 3
    assert '<td width="18">•</td><td><span style="font-weight:700">Study' in html
    assert 'style="margin-left:22px"' in html  # the nested item sits in
    assert '<td width="30">10.</td><td>ten</td>' in html
    assert '<p style="margin:0">Found:</p>' in html


def test_prose_shows_its_formatting(app):
    shown = prose("- **Lead** words\n- *more*", SCRIPTORUM)
    # Opening with a list, it has no initial: the label is the body itself.
    assert isinstance(shown, QLabel)
    assert shown.textFormat() == Qt.TextFormat.RichText
    assert '<span style="font-weight:700">Lead</span>' in shown.text()
    assert "**" not in shown.text()
    opened = prose("Hidden **things**", SCRIPTORUM)
    letter, body = opened.findChildren(QLabel)
    assert letter.text() == "H"
    assert body.text() == 'idden <span style="font-weight:700">things</span>'


def test_an_art_row_carries_its_score_and_experience():
    character = _sample_saga_with_covenant().characters[0]
    row = cs.art_row(character, "Creo")
    assert (row.abbreviation, row.score, row.xp) == ("Cr", "10", 55)
    assert (row.level_xp, row.next_xp, row.fraction) == (55, 66, 0.0)


def test_adding_editing_and_deleting_a_personality_trait(app):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    assert window.saga is not None
    character = window.saga.characters[0]
    character.personality_traits = []
    window.show_character(character.id)
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    sheet.open_chapter("Description")
    asked = answering(window, {"name": "Brave", "score": "2"})
    controls = section_buttons(sheet, "Personality Traits")
    assert not controls["Edit"].isEnabled()
    controls["Add"].click()
    assert asked[0].windowTitle() == "Add a Personality Trait"
    saved = storage.load_saga(saga.id).characters[0]
    assert [(t.name, t.score) for t in saved.personality_traits] == [("Brave", 2)]
    # One row: Edit acts on it without choosing.
    page = window.page()
    assert isinstance(page, CharacterSheet)
    answering(window, {"score": "3"})
    section_buttons(page, "Personality Traits")["Edit"].click()
    saved = storage.load_saga(saga.id).characters[0]
    assert [(t.name, t.score) for t in saved.personality_traits] == [("Brave", 3)]
    page = window.page()
    assert isinstance(page, CharacterSheet)
    asked = answering(window, False, True)
    controls = section_buttons(page, "Personality Traits")
    controls["Delete"].click()
    assert storage.load_saga(saga.id).characters[0].personality_traits
    page = window.page()
    assert isinstance(page, CharacterSheet)
    section_buttons(page, "Personality Traits")["Delete"].click()
    assert isinstance(asked[0], ConfirmDialog)
    assert asked[0].question == "Delete Brave?"
    assert not storage.load_saga(saga.id).characters[0].personality_traits


class _Heard:
    """A player that writes down what it was asked to play."""

    def __init__(self) -> None:
        self.cues: list[str] = []

    def play(self, path) -> None:
        self.cues.append(path.stem)


def test_chapters_turn_a_page_and_the_inventory_opens_a_chest(app, monkeypatch):
    heard = _Heard()
    monkeypatch.setattr(sounds, "_player", heard)
    sheet = _sheet()
    sheet.window_.show()
    sheet.codex.open_chapter("Abilities")
    sheet.codex.open_chapter("Inventory")
    assert heard.cues[-2:] == ["page", "chest"]
    sheet.window_.close()


def test_a_refused_entry_knocks(app, monkeypatch):
    heard = _Heard()
    monkeypatch.setattr(sounds, "_player", heard)
    dialog = FieldsDialog("Test", [DialogField("n", "Number", "text")], SCRIPTORUM)
    dialog.refuse("Not a number")
    assert heard.cues == ["tock"]


def test_the_sounds_are_silent_under_test_and_remember_being_turned_off(monkeypatch):
    monkeypatch.setattr(sounds, "_player", None)
    assert isinstance(sounds._chosen(), sounds.Silent)
    assert sounds.enabled()
    sounds.set_enabled(False)
    assert not sounds.enabled()
    monkeypatch.delenv(sounds.ENV_VAR)
    assert isinstance(sounds._chosen(), sounds.Silent)


def test_a_save_writes_with_a_quill_and_the_treasury_counts_coins(app):
    page = _covenant_page(_sample_saga_with_covenant())
    window = page.window_
    page.codex.open_chapter("Treasury")
    assert window._saved_cue(page) == "coins"
    page.codex.open_chapter(page.codex.chapters()[0])
    assert window._saved_cue(page) == "quill"
