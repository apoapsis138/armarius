"""The desktop's Host for Players window (gui/hosting.py): one place to host
the saga either way, and to issue Invites, approve requests and revoke
seats for Remote seats."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog, QPushButton

from ars_magica_manager import hosting, players, storage
from ars_magica_manager.forms.remote_seats import SeatsDesk
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import ConfirmDialog, FieldsDialog, NoticeDialog
from ars_magica_manager.gui.hosting import HostingWindow, InviteDialog
from ars_magica_manager.gui.pages import SagaPage
from ars_magica_manager.gui.themes import PALETTES
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Saga
from ars_magica_manager.remote.client import new_device_secret
from ars_magica_manager.remote.identity import MemoryStore
from ars_magica_manager.remote.invites import decode_invite
from ars_magica_manager.remote.plan import RemotePlan

LONG = "a passcode long enough"


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application  # pyright: ignore[reportReturnType]


@pytest.fixture(autouse=True)
def fresh_host(monkeypatch: pytest.MonkeyPatch) -> hosting.Host:
    fresh = hosting.Host()
    monkeypatch.setattr(hosting, "HOST", fresh)
    return fresh


def _desk() -> SeatsDesk:
    saga = Saga(id="host_saga", name="Host Saga")
    desk = SeatsDesk(saga, MemoryStore())
    for name, passcode in (("Anna", LONG), ("Bruno", "short")):
        player = players.add(saga, {"name": name, "passcode": passcode})
        desk.passcodes().note(player, passcode)
    RemotePlan(saga.id, saga.name, "https://saga.example.com").remember()
    return desk


class Answers:
    """Answers each window the Host for Players window opens: saves a form
    as it stands, says yes to a question, and keeps what it was shown."""

    def __init__(self) -> None:
        self.shown: list[QDialog] = []

    def __call__(self, dialog: QDialog) -> int:
        self.shown.append(dialog)
        if isinstance(dialog, FieldsDialog):
            dialog.try_save()
            return dialog.result()
        return QDialog.DialogCode.Accepted

    def last(self, kind: type[QDialog]) -> QDialog:
        return next(d for d in reversed(self.shown) if isinstance(d, kind))


def _window(desk: SeatsDesk, answers: Answers) -> HostingWindow:
    window = HostingWindow(desk, PALETTES[0], ask=answers)
    window.show()
    return window


@pytest.mark.usefixtures("app")
def test_saga_management_has_one_host_for_players_row_that_opens_the_window() -> None:
    desk = _desk()
    storage.save_saga(desk.saga)
    main = MainWindow(saga_ids=[desk.saga.id])
    main.show()
    main.open_saga(desk.saga.id)
    page = main.page()
    assert isinstance(page, SagaPage)
    page.codex.open_chapter("Saga Management")
    rows = [
        b
        for b in page.findChildren(QPushButton)
        if b.text().strip() in ("Host for Players", "Stop Hosting")
    ]
    assert [b.text().strip() for b in rows] == ["Host for Players"]
    rows[0].click()
    assert main._hosting is not None and main._hosting.isVisible()


@pytest.mark.usefixtures("app")
def test_the_players_are_in_saga_management_and_invite_from_there() -> None:
    from PySide6.QtWidgets import QTableView

    from ars_magica_manager.gui.saga_content import CHAPTERS

    desk = _desk()
    storage.save_saga(desk.saga)
    main = MainWindow(saga_ids=[desk.saga.id])
    answers = Answers()
    main.ask = answers  # type: ignore[assignment]
    main.show()
    main.open_saga(desk.saga.id)
    assert "Players" not in [name for name, _ in CHAPTERS]  # not Saga Content's
    page = main.page()
    assert isinstance(page, SagaPage)
    page.codex.open_chapter("Saga Management")
    tables = [
        t
        for t in page.findChildren(QTableView)
        if t.model() is not None
        and t.model().headerData(3, t.horizontalHeader().orientation()) == "Remote seat"
    ]
    assert len(tables) == 1
    tables[0].selectRow(0)  # Anna, ready
    QApplication.processEvents()
    [invite] = [
        b for b in page.findChildren(QPushButton) if b.text().strip() == "Issue Invite"
    ]
    invite.click()
    assert main._hosting is not None and main._hosting.isVisible()
    assert answers.last(InviteDialog).issued.player == "Anna"  # type: ignore[attr-defined]


@pytest.mark.usefixtures("app")
def test_the_window_follows_the_theme() -> None:
    """Opened again after the theme changed, it is drawn in the new one."""
    desk = _desk()
    storage.save_saga(desk.saga)
    main = MainWindow(saga_ids=[desk.saga.id])
    main.show()
    main.open_saga(desk.saga.id)
    main.open_hosting()
    first = main._hosting
    assert first is not None and first.p == main.palette_
    main.choose_theme(PALETTES[1].name)
    assert main._hosting is not first  # drawn again, as it was open
    assert main._hosting is not None and main._hosting.p == main.palette_


@pytest.mark.usefixtures("app")
def test_the_window_shows_the_six_words_and_waits_for_requests() -> None:
    desk = _desk()
    window = _window(desk, Answers())
    assert window.remote_choice.isChecked()
    assert len(window.words.text().split()) == 6
    assert window.tabs.currentIndex() == 0  # Requests first
    assert window.no_requests.isVisible() and not window.requests.isVisible()
    assert window.start.isVisible() and not window.stop.isVisible()
    window.browser_choice.setChecked(True)
    assert not window.remote.isVisible()


@pytest.mark.usefixtures("app")
def test_issuing_an_invite_shows_the_line_once_with_the_words() -> None:
    desk = _desk()
    answers = Answers()
    window = _window(desk, answers)
    window.issue.click()
    shown = answers.last(InviteDialog)
    assert isinstance(shown, InviteDialog)
    assert (
        decode_invite(shown.line.toPlainText()).url == "wss://saga.example.com/remote"
    )
    assert answers.last(FieldsDialog).windowTitle() == "Issue Invite"
    shown.copy.click()
    assert QApplication.clipboard().text() == shown.issued.line


@pytest.mark.usefixtures("app")
def test_a_request_is_approved_after_the_words_are_asked_about() -> None:
    desk = _desk()
    anna = players.find(desk.saga, "Anna")
    assert anna is not None
    book = desk.invites()
    book.redeem(book.issue(anna.id), "Anna's laptop", new_device_secret())
    answers = Answers()
    window = _window(desk, answers)
    assert window.requests.rowCount() == 1 and "1 waiting" in window.windowTitle()
    window.approve_button.click()
    question = answers.last(ConfirmDialog)
    assert isinstance(question, ConfirmDialog)
    assert "Approve only if Anna read you these words" in question.question
    assert window.requests.rowCount() == 0
    assert isinstance(answers.shown[-1], NoticeDialog)


@pytest.mark.usefixtures("app")
def test_a_seat_is_revoked_from_the_seats_tab() -> None:
    desk = _desk()
    anna = players.find(desk.saga, "Anna")
    assert anna is not None
    book = desk.invites()
    request = book.redeem(book.issue(anna.id), "Anna's laptop", new_device_secret())
    desk.devices().enrol(book.approve(request.id))
    answers = Answers()
    window = _window(desk, answers)
    assert window.seats.rowCount() == 1 and window.revoke.isEnabled()
    window.revoke.click()
    assert not desk.seats()[0].live
    assert not window.revoke.isEnabled()
    assert window.log.rowCount() >= 4  # issued, redeemed, approved, enrolled, revoked


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize("width", [820, 680])
def test_the_window_fits_at_its_size_and_at_its_narrowest(width: int) -> None:
    desk = _desk()
    window = _window(desk, Answers())
    window.resize(width, 680)
    QApplication.processEvents()
    assert window.width() == width
    buttons = (
        window.issue,
        window.approve_button,
        window.new_passcode,
        window.reject_button,
    )
    for button in buttons:
        assert button.geometry().right() <= window.tabs.pages.width()
