"""The picture a person is shown by on the desktop (pictures.person_picture):
their portrait when they have one, else their House's or tradition's
symbol, else the figure of a person."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication

from ars_magica_manager import artwork, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.models import Character

INK = "#123456"


@pytest.fixture
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    return application


def _same(a: QImage, b: QImage) -> bool:
    return a.size() == b.size() and a == b


def _person(kind: str, house: str = "") -> Character:
    person = Character(id="someone", name="Someone", type=kind)
    person.hermetic.house = house
    return person


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize(
    ("kind", "house", "shown"),
    [
        ("magus", "house_tremere", artwork.HOUSE_SYMBOLS["house_tremere"]),
        ("magus", "", artwork.icon("character")),
        ("companion", "", artwork.icon("character")),
        ("grog", "", artwork.icon("character")),
    ],
)
def test_without_a_portrait_a_person_is_their_house_or_the_figure(
    kind: str, house: str, shown: object
) -> None:
    person = _person(kind, house)
    assert artwork.person_mark(person) == shown
    drawn = pictures.person_picture(person, INK, 40).toImage()
    assert _same(
        drawn, pictures.pixmap(artwork.person_mark(person), INK, 40, 2.0).toImage()
    )


@pytest.mark.usefixtures("app")
def test_a_portrait_is_shown_first_cropped_square() -> None:
    portrait = QImage(60, 30, QImage.Format.Format_RGB32)
    portrait.fill(QColor("#C04020"))
    storage.portraits_dir().mkdir(parents=True, exist_ok=True)
    portrait.save(str(storage.portraits_dir() / "face.png"))
    person = _person("magus", "house_tremere")
    person.portrait = "face.png"
    drawn = pictures.person_picture(person, INK, 40).toImage()
    assert drawn.width() == drawn.height() == 80
    assert drawn.pixelColor(40, 40).name() == "#c04020"
