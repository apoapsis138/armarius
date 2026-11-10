"""The desktop's Find: Ctrl+F or the top bar's Find drops the finder
under its button; typing narrows the matches, Down and Enter or a click
open one, and Esc closes it."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant
from support import everything_saga

from ars_magica_manager import saga_index, storage, stores, viewing
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.finder import FinderPanel
from ars_magica_manager.gui.stores import StorePage
from ars_magica_manager.gui.widgets import Codex
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Book, EnchantedDevice, KnownSpell, Spell


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(app) -> MainWindow:
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.resize(1400, 900)
    window.show()
    window.activateWindow()
    QTest.qWaitForWindowActive(window)
    return window


def _open_finder(window: MainWindow) -> FinderPanel:
    QTest.keyClick(
        QApplication.focusWidget() or window,
        Qt.Key.Key_F,
        Qt.KeyboardModifier.ControlModifier,
    )
    finder = window.finder
    assert finder is not None and finder.isVisible()
    return finder


def test_ctrl_f_finds_a_character_and_enter_opens_their_page(app):
    window = _window(app)
    assert window.saga is not None
    magus = next(c for c in window.saga.characters if c.type == "magus")
    finder = _open_finder(window)
    # It hangs under Find, its right edge on the button's.
    button = window.find_button
    corner = button.mapToGlobal(button.rect().bottomRight())
    assert abs(finder.geometry().right() - corner.x()) <= 3
    assert QApplication.focusWidget() is finder.field
    QTest.keyClicks(finder.field, magus.name[:4].lower())
    assert finder.shown()[0] == magus.name
    QTest.keyClick(finder.field, Qt.Key.Key_Return)
    assert not finder.isVisible()
    page = window.page()
    assert isinstance(page, CharacterSheet)
    assert page.character.id == magus.id
    window.close()


def test_a_click_on_find_and_on_a_match_opens_it_and_esc_closes(app):
    window = _window(app)
    assert window.saga is not None
    covenant = window.saga.covenants[0]
    window.find_button.click()
    finder = window.finder
    assert finder is not None and finder.isVisible()
    QTest.keyClicks(finder.field, covenant.name)
    rows = finder.shown()
    assert covenant.name in rows
    item = finder.matches.item(rows.index(covenant.name))
    finder.matches.itemClicked.emit(item)
    assert isinstance(window.page(), CovenantPage)

    finder = _open_finder(window)
    QTest.keyClicks(finder.field, "no such record anywhere")
    assert finder.shown() == []
    assert finder.more.text() == "No record has that name."
    QTest.keyClick(finder.field, Qt.Key.Key_Escape)
    assert not finder.isVisible()
    assert isinstance(window.page(), CovenantPage)  # Esc only closed Find
    window.close()


def test_find_is_shown_only_while_a_saga_is_open(app):
    window = _window(app)
    assert window.find_button.isVisible()
    # Find, Help, a rule, then the settings gear: Advance Season is under
    # the chapters, away from them all.
    order = [window.find_button, window.help, window.bar_rule, window.settings]
    lefts = [w.mapTo(window, w.rect().topLeft()).x() for w in order]
    assert lefts == sorted(lefts)
    assert window.bar_rule.width() >= 16
    window.go(window.trail[:1])  # back to the Sagas
    assert not window.find_button.isVisible()
    window.open_finder()
    assert window.finder is None
    window.close()


@pytest.mark.parametrize(
    ("name", "after"),
    [
        ("The Spinner", "Creature · The Spinner's Hollow"),
        ("Dame Haspel of the Ashen Spur", "Creature · The Spinner's Hollow"),
        (
            "The Whispering Well",
            "Place · The Spinner's Hollow, Level 1: The Whispering Well",
        ),
        ("A name far too long " * 8, "Book · Dammërstein"),
    ],
)
def test_a_rows_name_is_whole_and_its_kind_never_overlaps_it(app, name, after):
    from PySide6.QtGui import QFont, QFontMetrics

    from ars_magica_manager.gui.finder import WIDTH, row_layout

    font = QFont(pictures.UI, 10)
    italic = QFont(font)
    italic.setItalic(True)
    names, afters = QFontMetrics(font), QFontMetrics(italic)
    width = WIDTH - 60
    row = row_layout(names, afters, width, name, after)
    gap = 2 * names.horizontalAdvance("M")
    assert row.name_x + row.name_width <= width
    if names.horizontalAdvance(name) < width - gap:
        assert row.name == name  # the place is cut short first
    if row.after:
        assert row.after_x >= row.name_x + row.name_width + gap
        assert row.after_x + row.after_width <= width
        assert afters.horizontalAdvance(row.after) <= row.after_width
        assert row.after == after or row.after.endswith("…")


def test_a_book_device_or_spell_opens_at_its_chapter_and_row(app):
    """As a player finds them, each opens its holder's page at the chapter
    that lists it, its row chosen (shown in the inspector): each second in
    its list, so the row is not just the first."""
    saga = everything_saga()
    magus = saga.character("mag1")
    assert magus is not None
    second = Spell(
        id="own-ward", name="Ward of Quills", technique="Rego", form="Herbam"
    )
    magus.invented_spells.append(second)
    magus.spells_known.append(KnownSpell(spell_id=second.id))
    saga.enchanted_devices.append(
        EnchantedDevice(
            id="dev-cov-2", name="Quillstaff", holder_kind="covenant", holder_id="cov1"
        )
    )
    saga.books += [
        Book(
            id=f"b-{kind}-2",
            name=f"Quires of {kind}",
            type="Art Summa",
            owner_kind=kind,
            owner_id=owner,
        )
        for kind, owner in (
            ("character", "mag1"),
            ("laboratory", "lab1"),
            ("covenant", "cov1"),
        )
    ]
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.resize(1400, 900)
    window.show()
    # A player's Find: the storyguide's opens the stores (below).
    viewing.use(viewing.TABLE_VIEWER, saga)
    found = {e.name: e for e in saga_index.entries(saga)}
    viewing.use(viewing.STORYGUIDE_VIEWER, saga)
    for name, chapter in (
        ("Ward of Quills", "Hermetic Magic"),
        ("Quillstaff", "Inventory"),
        ("Quires of character", "Inventory"),
        ("Quires of laboratory", "Stores"),
        ("Quires of covenant", "Library"),
        ("Wand", "Stores"),
    ):
        window.open_entry(found[name])
        codex = getattr(window.page(), "codex", None)
        assert isinstance(codex, Codex), name
        assert codex.rail.currentItem().text() == chapter, name
        assert codex.inspector.title.text() == name, name
    window.close()


def test_the_storyguides_find_opens_a_book_or_device_in_its_store(app):
    """Every book opens the Armarium and every device the Custodia, held
    or unassigned, at its row: a filter that hides the row is cleared."""
    saga = everything_saga()
    saga.books.append(Book(id="b-lost", name="Quires Lost", type="Art Summa"))
    saga.enchanted_devices.append(EnchantedDevice(id="d-lost", name="Quillwand"))
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.resize(1400, 900)
    window.show()
    StorePage.remembered["armarium"] = stores.Filter(kind="Tractatus")
    found = {e.name: e for e in saga_index.entries(saga)}
    for name, title in (
        ("Quires Lost", "The Armarium"),
        ("Summa", "The Armarium"),
        ("Quillwand", "The Custodia Mirabilium"),
        ("Wand", "The Custodia Mirabilium"),
    ):
        window.open_entry(found[name])
        page = window.page()
        assert isinstance(page, StorePage), name
        assert page.store.title == title
        assert page.codex.inspector.title.text() == name, name
    StorePage.remembered.clear()
    window.close()
