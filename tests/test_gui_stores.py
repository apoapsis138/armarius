"""The desktop's Armarium and Custodia Mirabilium (gui/stores.py): their
cards on the saga page's Compendium, the storyguide's alone; the
filter over each store's table, kept while the page is drawn again; and
the row chosen shown in the inspector."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from support import everything_saga

from ars_magica_manager import storage, stores, viewing
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.pages import SagaPage
from ars_magica_manager.gui.stores import StorePage
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Book, EnchantedDevice


@pytest.fixture(scope="module")
def app() -> QApplication:
    found = QApplication.instance()
    application = found if isinstance(found, QApplication) else QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window() -> MainWindow:
    saga = everything_saga()
    saga.books.append(Book(id="b-lost", name="Quires Lost", type="Art Summa"))
    saga.enchanted_devices.append(EnchantedDevice(id="d-lost", name="Quillwand"))
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.resize(1400, 900)
    window.show()
    return window


def _compendium_words(page: SagaPage) -> set[str]:
    page.codex.open_chapter("Compendium")
    chapter = page.codex.pages.currentWidget()
    return {label.text() for label in chapter.findChildren(QLabel)}


def test_the_cards_are_the_storyguides_alone(app: QApplication) -> None:
    window = _window()
    page = window.page()
    assert isinstance(page, SagaPage)
    words = _compendium_words(page)
    assert set(page.store_cards) == {stores.ARMARIUM, stores.CUSTODIA}
    assert {"Compendium", "The Armarium", "The Bestiary"} <= words
    page.store_cards[stores.ARMARIUM].clicked()
    shown = window.page()
    assert isinstance(shown, StorePage) and shown.store.key == stores.ARMARIUM
    viewing.use(viewing.TABLE_VIEWER, window.saga)
    window.go(window.trail[:2])
    page = window.page()
    assert isinstance(page, SagaPage)
    # A player sees Saga Content's card (it is never on the storyguide's
    # Compendium) and the Bestiary, and no store.
    assert "Saga Content" not in words
    words = _compendium_words(page)
    assert page.store_cards == {} and "The Armarium" not in words
    assert {"Content in Play", "Saga Content", "The Bestiary"} <= words
    assert page.content is not None
    page.content.clicked()
    assert window.crumb_names()[-1] == "Saga Content"
    window.close()


def test_the_filter_narrows_the_table_and_is_kept(app: QApplication) -> None:
    window = _window()
    window.open_store(stores.ARMARIUM)
    page = window.page()
    assert isinstance(page, StorePage)
    every = len(page.shown)
    page.holder.setCurrentIndex(page.holder.findData(stores.UNASSIGNED))
    # The sample's own unassigned book, and this one.
    assert [b.name for b in page.shown] == ["Loose", "Quires Lost"]
    assert page.title is not None
    assert page.title.text() == f"Books (2 of {every})"
    # Drawn again (as after any change), the filter stays.
    window.redraw()
    page = window.page()
    assert isinstance(page, StorePage)
    assert [b.name for b in page.shown] == ["Loose", "Quires Lost"]
    page._inspect(1)
    assert page.codex.inspector.title.text() == "Quires Lost"
    words = {b.text().strip() for b in page.findChildren(QPushButton)}
    assert {"Add", "Edit", "Delete", "Give", "Change Owner"} <= words
    StorePage.remembered.clear()
    window.close()


def test_the_custodia_lists_every_device(app: QApplication) -> None:
    window = _window()
    window.open_store(stores.CUSTODIA)
    page = window.page()
    assert isinstance(page, StorePage)
    names = [d.name for d in page.shown]
    assert "Quillwand" in names and "Wand" in names
    page.holder.setCurrentIndex(page.holder.findData(stores.UNASSIGNED))
    assert [d.name for d in page.shown] == ["Quillwand"]
    StorePage.remembered.clear()
    window.close()
