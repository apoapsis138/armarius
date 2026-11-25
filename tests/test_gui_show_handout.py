"""The desktop's Show for a written Handout: a Show button on Saga
Content's Handouts chapter, beside Edit, opens Show on the chosen
Handout; its copy opens on its Stationery in the window its Preview
draws (gui/handout_copy.py), laid out only through the tag parser."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QTableView,
    QToolButton,
)
from test_shows import PICTURE, _begun

from ars_magica_manager import (
    chronicle,
    commands,
    paths,
    show_copy,
    shows,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.gui import handout_copy, pictures
from ars_magica_manager.gui.chronicle_pane import ChroniclePane
from ars_magica_manager.gui.forms import reply, step_dialog
from ars_magica_manager.gui.handout_page import HandoutWindow
from ars_magica_manager.gui.saga_content import SagaContentPage
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.models import PROCLAMATION, Handout, HandoutPicture, Saga

LETTER = "[heading] To the Covenant\n[initial] Greetings.\n[picture 1]\n[flourish]"


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
            pictures=[HandoutPicture(paths.MAPS, "rhine.png")],
        )
    ]


def _page(saga: Saga, ran: list[commands.Command]) -> SagaContentPage:
    page = SagaContentPage(saga, SCRIPTORUM, ran.append)
    page.codex.open_chapter("Handouts")
    return page


def _show_button(page: SagaContentPage) -> QPushButton:
    [button] = [b for b in page.findChildren(QPushButton) if b.text().strip() == "Show"]
    return button


def _choose_first(page: SagaContentPage) -> None:
    for view in page.findChildren(QTableView):
        if view.model().headerData(1, Qt.Orientation.Horizontal) == "Stationery":
            view.selectRow(0)
            return
    raise AssertionError("No Handouts table")


@pytest.mark.usefixtures("app")
def test_the_show_button_shows_the_chosen_handout() -> None:
    virtual_tabletop.set_on(True)
    saga, _session, book = _begun()
    _letter(saga)
    ran: list[commands.Command] = []
    page = _page(saga, ran)
    button = _show_button(page)

    _choose_first(page)
    assert button.isEnabled()
    button.click()

    [form] = ran
    assert isinstance(form, commands.Form) and form.title == "Show"
    form.apply({"what": "handout:letter", "title": "A letter", "to": []})
    book.refresh()
    entry = book.entries[-1]
    assert (entry.kind, entry.body["handout"]) == (chronicle.SHOW, "letter")
    copy = shows.opened(saga.id, entry)
    assert copy.pictures == (PICTURE,)


@pytest.mark.usefixtures("app")
def test_the_show_button_greys_out_once_the_tabletop_is_turned_off() -> None:
    virtual_tabletop.set_on(True)
    saga, _session, _book = _begun()
    _letter(saga)
    page = _page(saga, [])
    button = _show_button(page)
    virtual_tabletop.set_on(False)

    _choose_first(page)

    assert not button.isEnabled()


@pytest.mark.usefixtures("app")
def test_no_show_button_without_a_session_under_way() -> None:
    virtual_tabletop.set_on(True)
    saga, session, _book = _begun()
    _letter(saga)
    session.under_way = False
    page = _page(saga, [])
    _choose_first(page)

    assert not _show_button(page).isVisible()


def _png(folder: Path) -> bytes:
    image = QImage(40, 30, QImage.Format.Format_RGB32)
    image.fill(0)
    file = folder / "seal.png"
    assert image.save(str(file))
    return file.read_bytes()


def _words(window: HandoutWindow) -> list[str]:
    return [label.text() for label in window.page.findChildren(QLabel) if label.text()]


@pytest.mark.usefixtures("app")
def test_a_written_copy_opens_on_its_stationery_through_the_tag_parser(
    tmp_path: Path,
) -> None:
    shown = shows.Shown(
        "A letter",
        LETTER + "\n<b>not html</b>\n[script] x",
        stationery=PROCLAMATION,
        pictures=(_png(tmp_path),),
    )
    form = show_forms.copy_form(shown)

    window = step_dialog(form, SCRIPTORUM, None)

    assert isinstance(window, HandoutWindow)
    assert window.page.laid.stationery.name == PROCLAMATION
    assert reply(form, window) == {}
    kinds = [b.kind for b in window.page.laid.blocks]
    assert kinds == ["heading", "initial", "picture", "flourish", "text"]
    assert window.page.findChild(QLabel, "handout-picture") is not None
    assert window.page.findChild(QLabel, "handout-placeholder") is None
    words = " ".join(_words(window))
    assert "[heading]" not in words and "To the Covenant" in words
    assert "&lt;b&gt;not html&lt;/b&gt;" in words and "[script] x" in words
    window.close()


@pytest.mark.usefixtures("app")
def test_a_picture_not_to_hand_is_a_placeholder_naming_no_file() -> None:
    shown = shows.Shown(
        "A letter", "[picture 1]", stationery=PROCLAMATION, pictures=(None,)
    )
    window = handout_copy.copy_window(show_forms.copy_form(shown).reading)  # type: ignore[arg-type]

    placeholder = window.page.findChild(QLabel, "handout-placeholder")
    assert isinstance(placeholder, QLabel)
    assert placeholder.text() == "Picture 1: shown with it"
    window.close()


@pytest.mark.usefixtures("app")
def test_the_chronicle_card_opens_a_written_copy_on_its_stationery() -> None:
    saga, session, book = _begun()
    _letter(saga)
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ana")
    shows.show(
        book,
        saga,
        session,
        chronicle.ShowCall("A letter", handout="letter"),
        by=viewing.HOST,
        copier=show_copy.player_copy,
    )

    found = pane.card_list()[-1].findChild(QToolButton, "open-show")
    assert isinstance(found, QToolButton)
    marks = [b.objectName() for b in pane.card_list()[-1].findChildren(QToolButton)]
    assert "open-live" not in marks
    found.click()

    window = pane.shown_copy
    assert isinstance(window, HandoutWindow)
    assert window.page.laid.title == "A letter"
    window.close()
