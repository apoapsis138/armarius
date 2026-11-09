"""Joining a hosted saga from the desktop, end to end: the Join a Saga
window's steps against a real listener (run on a loop of its own here, as
the host's process would), the game opened through the host, an edit
sent back, and leaving it."""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Iterator

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog
from test_remote_records import Hosted
from test_seat_view import LEAKS, hidden_saga

from ars_magica_manager import joined_games, picture_files, players, storage
from ars_magica_manager.gui import joined, pictures
from ars_magica_manager.gui.join import JoinWindow
from ars_magica_manager.gui.themes import PALETTES
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.bridge import LoopThread
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.invites import encode_invite
from ars_magica_manager.remote.seat_session import SeatSession
from ars_magica_manager.remote.vault import DeviceVault

PASSCODE = "a long enough passcode"


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application  # pyright: ignore[reportReturnType]


class Running:
    """A hosted saga served from a loop of its own."""

    def __init__(self) -> None:
        saga = hidden_saga()
        anna = players.find(saga, "Anna")
        assert anna is not None
        saga.characters[0].background.player_id = anna.id
        self.loop = LoopThread()
        self.hosted = Hosted(saga)
        self.hosted.port = self.loop.run(self.hosted.host.start())
        self.vault = DeviceVault(ident.MemoryStore())

    @property
    def url(self) -> str:
        return f"ws://127.0.0.1:{self.hosted.port}{PATH}"

    def invite(self) -> str:
        code = self.hosted.book.issue(self.hosted.anna.id)
        return encode_invite(self.url, self.hosted.pin, code)

    def session(self, url: str, pin: str) -> SeatSession:
        return SeatSession(url, pin, self.vault)

    def stop(self) -> None:
        self.loop.run(self.hosted.host.stop())
        self.loop.stop()


@pytest.fixture
def running() -> Iterator[Running]:
    serving = Running()
    yield serving
    serving.stop()


def _joined_window(running: Running) -> tuple[MainWindow, JoinWindow]:
    main = MainWindow(saga_ids=[])
    main.ask = lambda _dialog: QDialog.DialogCode.Accepted  # no window waits
    main.show()
    dialog = JoinWindow(PALETTES[0], main, make_session=running.session)
    dialog.invite.setPlainText(running.invite())
    dialog._read_invite()
    assert dialog.steps.currentIndex() == 1
    assert dialog.words.text() == dialog.session.host_words()  # type: ignore[union-attr]
    dialog._words_match()
    dialog.device.setText("Anna's laptop")
    dialog._ask_for_seat()
    assert dialog.steps.currentIndex() == 3
    assert len(dialog.device_words.text().split()) == 3
    dialog._ask()
    assert dialog.steps.currentIndex() == 3  # still waiting
    running.hosted.book.approve(running.hosted.book.pending()[0].id)
    dialog._ask()
    assert dialog.steps.currentIndex() == 4
    dialog.passcode.setText(PASSCODE)
    dialog._sign_in()
    assert dialog.result() == QDialog.DialogCode.Accepted
    return main, dialog


def _talk_done(main: MainWindow, seconds: float = 10.0) -> None:
    """Tick until the talk with the host it starts has finished."""
    end = time.monotonic() + seconds
    main.shared_tick()  # starts the talk
    while main.talk is not None and time.monotonic() < end:
        time.sleep(0.02)
        main.shared_tick()
    assert main.talk is None, "the talk with the host didn't finish"


@pytest.mark.usefixtures("app")
def test_a_player_joins_reads_and_changes_their_character(running: Running) -> None:
    main, dialog = _joined_window(running)
    assert dialog.session is not None
    joined.open_joined(main, dialog.session)
    saga = main.saga
    assert saga is not None and main.store.remote
    assert main.player is not None and main.player.name == "Anna"
    assert not [w for w in LEAKS.values() if w in str(saga)]
    assert [g.saga_name for g in joined_games.listed()] == [saga.name]
    saga.characters[0].name = "Leandro the Bold"
    main.save_saga()
    assert main.unsent  # sent by the tick, in the background
    _talk_done(main)
    assert not main.unsent
    assert storage.load_saga(running.hosted.saga.id).characters[0].name == (
        "Leandro the Bold"
    )
    main.end_joined()
    assert main.session is None and not main.store.remote


class _SilentHost:
    """A seat whose host goes quiet: each read waits until `answer` is set,
    then fails while `down`, as a dropped network does."""

    url, pin = "wss://example.test/remote", "pin"

    def __init__(self) -> None:
        self.answer = threading.Event()
        self.down = True
        self.sent: list[str] = []
        self.revision = ""

    def read(self, since: str = "") -> tuple[str, object]:
        self.answer.wait(10)
        if self.down:
            raise ConnectionError("lost")
        return since, None  # nothing new

    def send_change(
        self, kind: str, key: str, before: object, after: object
    ) -> list[str]:
        if self.down:
            raise ConnectionError("lost")
        self.sent.append(f"{kind}:{key}")
        return []

    def reconnect(self) -> str:
        if self.down:
            raise ConnectionError("lost")
        return "Anna"

    def close(self) -> None:
        self.answer.set()


@pytest.mark.usefixtures("app")
def test_a_host_that_stops_answering_never_holds_the_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ars_magica_manager.saga_store import RemoteStore

    saga = hidden_saga()
    storage.save_saga(saga)
    main = MainWindow(saga_ids=[saga.id])
    main.shared_timer.stop()
    host = _SilentHost()
    store = RemoteStore(host)  # type: ignore[arg-type]
    store._took("r1", main.saga)  # type: ignore[arg-type]
    main.store, main.session = store, host  # type: ignore[assignment]
    monkeypatch.setattr(joined, "SLOW", 0.0)
    main.last_asked = 0.0  # due now

    started = time.monotonic()
    main.shared_tick()  # asks the host, in the background
    main.shared_tick()  # the host hasn't answered: the window goes on
    assert time.monotonic() - started < 1.0
    assert main.talk is not None
    assert main.note.text() == "The host is slow to answer…"

    host.answer.set()  # the read fails: the connection is lost
    while main.talk is not None and not main.talk.future.done():
        time.sleep(0.01)
    main.shared_tick()
    assert main.connection_lost
    assert main.note.text() == "Connection lost; trying again…"

    assert main.saga is not None
    main.saga.characters[0].name = "Leandro the Bold"
    main.save_saga()  # kept, said, and sent once the host is back
    assert main.unsent and "Not sent yet" in main.note.text()

    host.down = False
    main.last_asked = 0.0
    _talk_done(main)  # reconnects
    assert not main.connection_lost and main.note.text() == "Connected again."
    _talk_done(main)  # sends, then reads
    assert host.sent and not main.unsent
    main.session = None
    main.close()


@pytest.mark.usefixtures("app")
def test_words_that_dont_match_send_nothing(running: Running) -> None:
    main = MainWindow(saga_ids=[])
    dialog = JoinWindow(PALETTES[0], main, make_session=running.session)
    dialog.invite.setPlainText(running.invite())
    dialog._read_invite()
    dialog._words_differ()
    assert dialog.session is None and dialog.steps.currentIndex() == 0
    assert "Nothing was sent" in dialog.error.text()
    assert running.hosted.book.pending() == []


@pytest.mark.usefixtures("app")
def test_a_bad_invite_line_is_refused_plainly(running: Running) -> None:
    main = MainWindow(saga_ids=[])
    dialog = JoinWindow(PALETTES[0], main, make_session=running.session)
    dialog.invite.setPlainText("not an invite")
    dialog._read_invite()
    assert dialog.steps.currentIndex() == 0
    assert "not an Armarius invite" in dialog.error.text()


@pytest.mark.usefixtures("app")
def test_the_shelf_offers_join_and_lists_joined_games(running: Running) -> None:
    joined_games.remember(
        joined_games.JoinedGame("s", "Elsewhere", running.url, running.hosted.pin)
    )
    main = MainWindow(saga_ids=[])
    main.show()
    texts = [b.text().strip() for b in main.findChildren(type(main.help))]
    assert "Join a Saga" in texts and "Leave Saga" in texts
    picture_files.use_host(None)
