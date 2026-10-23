"""A character's portrait: chosen from anywhere, copied into the save
folder, drawn in a frame beside the name; the House symbol while there is
none."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication, QFileDialog
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import portraits, storage
from ars_magica_manager.commands import ChooseFile
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Character


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _picture(folder, name="leandro.png", colour="#8b0000"):
    image = QImage(30, 40, QImage.Format.Format_ARGB32)
    image.fill(QColor(colour))
    path = folder / name
    assert image.save(str(path))
    return path


def test_a_chosen_picture_is_copied_into_the_save_folder(app, tmp_path):
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    assert portraits.path(magus) is None
    original = _picture(tmp_path)
    portraits.set_portrait(saga, magus, original)
    copy = portraits.path(magus)
    assert copy is not None and copy.parent == storage.portraits_dir()
    original.unlink()
    assert portraits.path(magus) == copy
    # Another picture replaces it, and the old copy goes.
    portraits.set_portrait(saga, magus, _picture(tmp_path, "new.jpg"))
    assert not copy.exists()
    assert portraits.path(magus) is not None
    portraits.remove_portrait(magus)
    assert magus.portrait == "" and portraits.path(magus) is None


def test_only_pictures_are_taken(tmp_path):
    saga = _sample_saga_with_covenant()
    notes = tmp_path / "notes.txt"
    notes.write_text("hello")
    with pytest.raises(ValueError):
        portraits.set_portrait(saga, saga.characters[0], notes)
    step = portraits.portrait(saga, saga.characters[0])
    assert isinstance(step, ChooseFile) and ".jpg" in step.suffixes


def test_an_older_save_or_a_missing_file_has_no_portrait():
    loaded = Character.from_dict({"id": "x", "name": "Old", "type": "grog"})
    assert loaded.portrait == ""
    loaded.portrait = "gone.png"
    assert portraits.path(loaded) is None


def test_the_sheet_frames_the_portrait_and_choosing_one_shows_it(app, tmp_path):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show_character("char1")
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    assert not sheet.portrait.has_picture()
    asked = answering(window, _picture(tmp_path))
    sheet.portrait.clicked()
    assert isinstance(asked[0], QFileDialog)
    page = window.page()
    assert isinstance(page, CharacterSheet) and page.portrait.has_picture()
    saved = storage.load_saga(saga.id).characters[0]
    assert saved.portrait and (storage.portraits_dir() / saved.portrait).is_file()
    # With one set, it can be taken off again.
    answering(window, "Remove the portrait")
    page.portrait.clicked()
    page = window.page()
    assert isinstance(page, CharacterSheet) and not page.portrait.has_picture()
    assert storage.load_saga(saga.id).characters[0].portrait == ""
