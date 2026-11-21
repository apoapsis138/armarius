"""The desktop's Scene banner (gui/chronicle_pane.py): its title and place
as the players know them, the aura only when the table was told it, and
"See the map" opening the Scene's map in its own window, read through the
window's picture source (the host's, for a Joined game)."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QToolButton
from test_scene_play import HOST, _begun, _set

from ars_magica_manager import commands, paths, references, scene_play
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.chronicle_pane import ChroniclePane, ShownPicture
from ars_magica_manager.gui.themes import SCRIPTORUM


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _png() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"ford" * 20


def _text(pane: ChroniclePane, name: str) -> str | None:
    found = pane.card_list()[-1].findChild(QLabel, name)
    return found.text() if isinstance(found, QLabel) else None


@pytest.mark.usefixtures("app")
def test_a_banner_names_the_scene_and_keeps_a_hidden_aura_hidden() -> None:
    saga, session, book = _begun()
    ran: list[commands.Command] = []
    pane = ChroniclePane(SCRIPTORUM, ran.append)
    pane.attach(saga, session, book, "ana")

    _set(book, saga, session, "u-hill")
    assert pane.lines()[-1] == "Scene: The hill, at an unknown place"
    assert _text(pane, "scene-title") == "The hill"
    assert _text(pane, "scene-place") == "At an unknown place"
    assert _text(pane, "scene-aura") is None
    _set(book, saga, session, "u-home", tell_aura=True)
    assert _text(pane, "scene-aura") == "Aura: Magic 4"
    assert ran == []  # told, never popped open


def _strip(pane: ChroniclePane) -> list[str]:
    return [
        b.text() for b in pane.now_strip.findChildren(QToolButton) if not b.isHidden()
    ]


@pytest.mark.usefixtures("app")
def test_now_playing_links_a_known_place_for_a_player() -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    opened: list[references.Ref] = []
    pane.open_record = opened.append
    pane.attach(saga, session, book, "ana")
    assert pane.now_strip.isHidden()

    _set(book, saga, session, "u-home")
    assert not pane.now_strip.isHidden()
    assert _strip(pane) == ["At Fengheld"]  # no storyguide's verbs
    place = pane.now_strip.findChild(QToolButton, "now-place")
    assert isinstance(place, QToolButton)
    place.click()
    assert opened == [references.Ref("covenants", "c", "Fengheld")]
    scene_play.end_scene(book, saga, session, by=HOST)
    assert pane.now_strip.isHidden()


@pytest.mark.usefixtures("app")
def test_now_playing_gives_the_storyguide_a_show_for_each_thing_and_end_scene() -> None:
    saga, session, book = _begun()
    saga.scenes[0].to_show = ["maps:m"]
    ran: list[commands.Command] = []
    pane = ChroniclePane(SCRIPTORUM, ran.append)
    pane.attach(saga, session, book, HOST)
    _set(book, saga, session, "u-ford")

    assert _strip(pane) == ["Show The Rhine", "End Scene"]
    shows_it = pane.now_strip.findChild(QToolButton, "now-show")
    assert isinstance(shows_it, QToolButton)
    shows_it.click()
    [form] = ran
    assert isinstance(form, commands.Form) and form.title == "Show"
    assert form.fields()[0].value == "picture:maps:rhine.png"


@pytest.mark.usefixtures("app")
def test_attaching_the_same_chronicle_again_redraws_now_playing() -> None:
    """An edit to the Scene playing shows when the window attaches again."""
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, HOST)
    _set(book, saga, session, "u-ford")
    assert _strip(pane) == ["End Scene"]
    saga.scenes[0].to_show = ["maps:m"]
    pane.attach(saga, session, book, HOST)
    assert _strip(pane) == ["Show The Rhine", "End Scene"]


@pytest.mark.usefixtures("app")
def test_see_the_map_opens_the_scenes_map_from_the_picture_source() -> None:
    saga, session, book = _begun()
    asked: list[tuple[str, str]] = []

    def read(folder: str, name: str) -> bytes | None:
        asked.append((folder, name))
        return _png()

    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.read_picture = read
    pane.attach(saga, session, book, "ana")
    _set(book, saga, session, "u-ford")
    button = pane.card_list()[-1].findChild(QToolButton, "scene-picture")
    assert isinstance(button, QToolButton)
    button.click()

    assert asked == [(paths.MAPS, "rhine.png")]
    assert isinstance(pane.shown_picture, ShownPicture)
    assert pane.shown_picture.windowTitle() == "The ford"
