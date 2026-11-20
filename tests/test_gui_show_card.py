"""The desktop's Show card (gui/chronicle_pane.py): it never opens by
itself; Open opens the copy as it was shown (a picture in its own window),
and "Open the live record" is offered only to one who may read it now."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QToolButton
from test_shows import _begun, _hilda_ref, _show

from ars_magica_manager import chronicle, commands, references, shows, viewing
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.chronicle_pane import ChroniclePane, ShownPicture
from ars_magica_manager.gui.themes import SCRIPTORUM

HOST = viewing.HOST


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _click(pane: ChroniclePane, name: str) -> None:
    found = pane.card_list()[-1].findChild(QToolButton, name)
    assert isinstance(found, QToolButton)
    found.click()


def _marks(pane: ChroniclePane) -> list[str]:
    card = pane.card_list()[-1]
    return [b.objectName() for b in card.findChildren(QToolButton)]


@pytest.mark.usefixtures("app")
def test_a_show_card_opens_its_copy_and_never_by_itself() -> None:
    saga, session, book = _begun()
    ran: list[commands.Command] = []
    pane = ChroniclePane(SCRIPTORUM, ran.append)
    opened: list[references.Ref] = []
    pane.open_record = opened.append
    pane.attach(saga, session, book, "ana")

    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",)))

    assert pane.lines()[-1] == "The storyguide shows: Hilda (to Ana)"
    assert ran == []  # told, never popped open
    assert _marks(pane) == ["open-show", "open-live"]
    _click(pane, "open-show")
    [copy] = ran
    assert isinstance(copy, commands.Form)
    assert "SHOWN-SECRET" in str(copy.fields()[0].value)
    _click(pane, "open-live")
    assert opened == [_hilda_ref()]


@pytest.mark.usefixtures("app")
def test_no_live_record_for_one_the_player_may_not_read_now() -> None:
    saga, session, book = _begun()
    saga.characters[2].known = False
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ana")

    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))

    assert _marks(pane) == ["open-show"]


@pytest.mark.usefixtures("app")
def test_a_shown_picture_opens_in_its_own_window() -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ben")

    _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png"), to=("ben",)),
    )
    _click(pane, "open-show")

    shown = pane.shown_picture
    assert isinstance(shown, ShownPicture)
    assert shown.windowTitle() == "The Rhine"
    shown.close()


@pytest.mark.usefixtures("app")
def test_a_small_picture_is_drawn_at_its_own_size_a_large_one_fits(
    tmp_path: Path,
) -> None:
    def drawn(width: int, height: int) -> tuple[int, int]:
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(0)
        file = tmp_path / f"{width}x{height}.png"
        assert image.save(str(file))
        window = ShownPicture(shows.Shown("A picture", picture=file.read_bytes()))
        found = window.picture.pixmap()
        window.close()
        return found.width(), found.height()

    assert drawn(150, 200) == (150, 200)
    assert drawn(1800, 700) == (900, 350)
