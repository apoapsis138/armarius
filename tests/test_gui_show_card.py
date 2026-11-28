"""The desktop's Show card (gui/chronicle_pane.py): it never opens by
itself; Open opens the copy as it was shown (a picture in its own window),
and "Open the live record" is offered only to one who may read it now."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, assert_framed, section_buttons
from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, QScreen
from PySide6.QtWidgets import QApplication, QLabel, QToolButton
from test_shows import _begun, _hilda_ref, _show

from ars_magica_manager import (
    chronicle,
    commands,
    references,
    shows,
    storage,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.chronicle_pane import (
    ChroniclePane,
    ShownCopy,
    ShownPicture,
)
from ars_magica_manager.gui.forms import ChooseDialog
from ars_magica_manager.gui.themes import SCRIPTORUM, SCRIPTORUM_DARK
from ars_magica_manager.gui.window import MainWindow

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
    copy = pane.shown_copy
    assert isinstance(copy, ShownCopy)
    assert copy.windowTitle() == "Hilda"
    assert_framed(copy)
    assert "SHOWN-SECRET" in copy.text.toPlainText()
    copy.close()
    _click(pane, "open-live")
    assert opened == [_hilda_ref()]


@pytest.mark.usefixtures("app")
def test_a_copy_opens_under_its_heading_without_its_name_line_twice() -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ana")
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",)))

    _click(pane, "open-show")

    copy = pane.shown_copy
    assert isinstance(copy, ShownCopy)
    assert copy.column.itemAt(0).widget().text() == "Hilda"
    first = copy.text.document().firstBlock()
    assert not (first.text() == "Hilda" and first.blockFormat().headingLevel() == 1)
    copy.close()


@pytest.mark.usefixtures("app")
def test_a_viewer_opened_after_a_theme_change_wears_the_new_paper() -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ana")
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",)))

    pane.set_palette(SCRIPTORUM_DARK)
    _click(pane, "open-show")

    copy = pane.shown_copy
    assert isinstance(copy, ShownCopy)
    assert copy.p is SCRIPTORUM_DARK and copy.page.p is SCRIPTORUM_DARK
    copy.close()


@pytest.mark.usefixtures("app")
def test_a_withdrawn_show_reads_withdrawn_and_its_open_copy_closes() -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ana")
    shown = _show(
        book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",))
    )
    _click(pane, "open-show")
    copy = pane.shown_copy
    assert isinstance(copy, ShownCopy) and copy.isVisible()

    shows.withdraw(book, saga, session, shown.number, by=HOST)

    assert not copy.isVisible()
    show = next(
        c for c in pane.card_list() if c.line.startswith("The storyguide shows")
    )
    marks = [b.objectName() for b in show.findChildren(QToolButton)]
    assert "open-show" not in marks and "open-live" not in marks
    note = show.findChild(QLabel, "show-withdrawn")
    assert isinstance(note, QLabel) and note.text() == "Withdrawn"
    assert pane.lines()[-1] == "The storyguide withdraws: Hilda"


@pytest.mark.usefixtures("app")
def test_the_storyguide_still_opens_a_withdrawn_show_from_its_card() -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, HOST)
    shown = _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    shows.withdraw(book, saga, session, shown.number, by=HOST)

    show = next(
        c for c in pane.card_list() if c.line.startswith("The storyguide shows")
    )
    marks = [b.objectName() for b in show.findChildren(QToolButton)]
    assert "open-show" in marks and "withdraw-show" not in marks
    assert show.findChild(QLabel, "show-withdrawn") is not None


@pytest.mark.usefixtures("app")
def test_a_redraw_works_out_the_withdrawn_shows_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ana")
    for title in ("One", "Two", "Three"):
        _show(book, saga, session, chronicle.ShowCall(title, _hilda_ref()))
    asked: list[int] = []
    real = shows.withdrawn

    def counted(found: chronicle.HasEntries) -> set[int]:
        asked.append(1)
        return real(found)

    monkeypatch.setattr(shows, "withdrawn", counted)
    pane._redraw_cards()  # pyright: ignore[reportPrivateUsage]

    assert len(asked) == 1


@pytest.mark.usefixtures("app")
def test_a_copy_shows_markup_in_it_as_words_never_as_html() -> None:
    shown = shows.Shown("Hilda", '<span style="font-size:72pt">big</span> words')
    window = ShownCopy(shown, SCRIPTORUM)
    words = window.text.toPlainText()
    window.close()
    assert '<span style="font-size:72pt">big</span>' in words


@pytest.mark.usefixtures("app")
def test_the_storyguide_withdraws_from_the_card() -> None:
    saga, session, book = _begun()
    ran: list[commands.Command] = []
    pane = ChroniclePane(SCRIPTORUM, ran.append)
    pane.attach(saga, session, book, HOST)
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))

    assert "withdraw-show" in _marks(pane)
    _click(pane, "withdraw-show")
    [asked] = ran
    assert isinstance(asked, commands.Confirm) and asked.yes_label == "Withdraw"

    reader = ChroniclePane(SCRIPTORUM, lambda _c: None)
    reader.attach(saga, session, book, "ana")
    assert "withdraw-show" not in _marks(reader)


@pytest.mark.usefixtures("app")
def test_no_live_record_for_one_the_player_may_not_read_now() -> None:
    saga, session, book = _begun()
    saga.characters[2].known = False
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ana")

    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))

    assert _marks(pane) == ["open-show"]


@pytest.mark.usefixtures("app")
def test_a_character_a_player_plays_has_a_handouts_card_on_its_diary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    virtual_tabletop.set_on(True)
    saga, session, book = _begun()
    aelfric = saga.characters[0]
    aelfric.background.player_ids = ["ana"]
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    storage.save_saga(saga)
    monkeypatch.setattr(chronicle, "here", lambda: "ana")
    window = MainWindow(saga_ids=[saga.id])
    window.load(saga)
    window.show_character(aelfric.id)
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Diary")

    asked = answering(window, None)
    section_buttons(page, "Handouts")["Open Handouts"].click()

    [chooser] = asked
    assert isinstance(chooser, ChooseDialog)
    window.show_character(saga.characters[1].id)  # Brigit, Ben's
    other = window.page()
    assert isinstance(other, CharacterSheet)
    other.open_chapter("Diary")
    with pytest.raises(AssertionError, match="Handouts"):
        section_buttons(other, "Handouts")


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
    assert_framed(shown)
    shown.close_button.click()
    assert not shown.isVisible()


@pytest.mark.usefixtures("app")
def test_a_withdrawn_shows_open_picture_closes() -> None:
    saga, session, book = _begun()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, book, "ben")
    shown = _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png"), to=("ben",)),
    )
    _click(pane, "open-show")
    picture = pane.shown_picture
    assert isinstance(picture, ShownPicture) and picture.isVisible()

    shows.withdraw(book, saga, session, shown.number, by=HOST)

    assert not picture.isVisible()


def _work_area(monkeypatch: pytest.MonkeyPatch, width: int, height: int) -> None:
    """Every screen's free area (less the taskbar) is `width` x `height`."""
    monkeypatch.setattr(
        QScreen, "availableGeometry", lambda _screen: QRect(0, 0, width, height)
    )


def _picture_window(folder: Path, width: int, height: int) -> ShownPicture:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0)
    file = folder / f"{width}x{height}.png"
    assert image.save(str(file))
    return ShownPicture(shows.Shown("A picture", picture=file.read_bytes()), SCRIPTORUM)


@pytest.mark.usefixtures("app")
def test_a_small_picture_is_drawn_at_its_own_size_a_large_one_fits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _work_area(monkeypatch, 1920, 1040)

    def drawn(width: int, height: int) -> tuple[int, int]:
        window = _picture_window(tmp_path, width, height)
        found = window.picture.pixmap()
        window.close()
        return found.width(), found.height()

    assert drawn(150, 200) == (150, 200)
    assert drawn(1800, 700) == (900, 350)


@pytest.mark.usefixtures("app")
def test_a_large_picture_on_a_short_screen_fits_with_its_close_in_reach(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _work_area(monkeypatch, 1366, 728)
    window = _picture_window(tmp_path, 2000, 1500)
    window.show()
    try:
        least = window.minimumSizeHint()
        assert least.height() <= 728 and least.width() <= 1366
        assert window.frameGeometry().bottom() < 728
        assert window.picture.pixmap().height() < 700
        assert window.close_button.isVisible()
    finally:
        window.close()


@pytest.mark.usefixtures("app")
def test_a_picture_on_a_tiny_screen_is_still_drawn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _work_area(monkeypatch, 120, 90)
    window = _picture_window(tmp_path, 2000, 1500)
    drawn = window.picture.pixmap()
    window.close()
    assert not drawn.isNull() and drawn.height() > 0
