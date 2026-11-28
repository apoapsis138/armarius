"""The desktop's Preview for a written Handout: a Preview button on Saga
Content's Handouts chapter, beside Edit, opens the chosen Handout on its
Stationery in the window a player's shown copy opens in, its pictures
from the saga's own files; it writes nothing."""

from __future__ import annotations

import copy
import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import assert_framed
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QTableView
from test_shows import _begun

from ars_magica_manager import commands, handouts, paths, virtual_tabletop
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import step_dialog
from ars_magica_manager.gui.handout_page import HandoutWindow
from ars_magica_manager.gui.saga_content import SagaContentPage
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.models import PROCLAMATION, Handout, HandoutPicture, Saga

LETTER = "[heading] To the Covenant\n[initial] Greetings.\n[picture 1]\n[picture 2]"


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _letter(saga: Saga) -> None:
    saga.handouts = [
        Handout(
            "letter",
            "The Count's Letter",
            stationery=PROCLAMATION,
            text=LETTER,
            pictures=[
                HandoutPicture(paths.MAPS, "rhine.png"),
                HandoutPicture(paths.HANDOUTS, "gone.png"),
            ],
        )
    ]
    handouts.choose_story(saga, "")


def _page(saga: Saga, ran: list[commands.Command]) -> SagaContentPage:
    page = SagaContentPage(saga, SCRIPTORUM, ran.append)
    page.codex.open_chapter("Handouts")
    return page


def _button(page: SagaContentPage, words: str) -> QPushButton:
    [button] = [b for b in page.findChildren(QPushButton) if b.text().strip() == words]
    return button


def _choose_first(page: SagaContentPage) -> None:
    for view in page.findChildren(QTableView):
        if view.model().headerData(1, Qt.Orientation.Horizontal) == "Stationery":
            view.selectRow(0)
            return
    raise AssertionError("No Handouts table")


@pytest.mark.usefixtures("app")
def test_preview_opens_the_chosen_handout_on_its_stationery() -> None:
    virtual_tabletop.set_on(True)
    saga, _session, book = _begun()
    _letter(saga)
    rhine = QImage(40, 30, QImage.Format.Format_RGB32)
    rhine.fill(0)
    assert rhine.save(str(paths.data_dir() / paths.MAPS / "rhine.png"))
    before, entries = copy.deepcopy(saga), len(book.entries)
    ran: list[commands.Command] = []
    page = _page(saga, ran)
    buttons = [b.text().strip() for b in page.findChildren(QPushButton)]
    button = _button(page, "Preview")

    assert buttons.index("Edit") < buttons.index("Preview") < buttons.index("Show")
    _choose_first(page)
    assert button.isEnabled()
    button.click()

    [form] = ran
    assert isinstance(form, commands.Form)
    window = step_dialog(form, SCRIPTORUM, None)
    assert isinstance(window, HandoutWindow)
    assert_framed(window)
    assert window.handout.laid.title == "The Count's Letter"
    assert window.handout.laid.stationery.name == PROCLAMATION
    assert window.handout.findChild(QLabel, "handout-picture") is not None
    placeholder = window.handout.findChild(QLabel, "handout-placeholder")
    assert isinstance(placeholder, QLabel)
    gone = handouts.picture_name(saga, saga.handouts[0].pictures[1])
    assert placeholder.text() == f"Picture 2: {gone}"
    window.close()

    book.refresh()
    assert len(book.entries) == entries and saga == before


@pytest.mark.usefixtures("app")
def test_preview_is_offered_with_the_tabletop_off_and_no_session() -> None:
    virtual_tabletop.set_on(False)
    saga = Saga(id="quiet", name="Quiet")
    _letter(saga)
    page = _page(saga, [])

    _choose_first(page)

    assert _button(page, "Preview").isEnabled()
    assert not [b for b in page.findChildren(QPushButton) if b.text().strip() == "Show"]
