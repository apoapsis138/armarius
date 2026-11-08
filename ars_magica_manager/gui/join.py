"""Joining a hosted saga from the desktop: the first join, step by step,
and signing in again to a Joined game.

The first join, each step a page of one window:

1. Paste the invite line the storyguide sent.
2. The host's six words, as the app worked them out from the invite: they
   must match what the storyguide reads out on the call. If they don't,
   the invite may have been changed on its way: nothing is sent.
3. A name for this device (the computer's own, to start with).
4. The device's three words, to read back to the storyguide, while the
   app waits for them to approve (it asks again every few seconds).
5. The passcode.

Each step asks the host one short question at a time (seat_session.py),
so the window is never held for longer than one round trip.
"""

from __future__ import annotations

import socket
from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..remote.client import (
    NoCredential,
    SignInError,
    UnreadableReply,
    VersionMismatch,
)
from ..remote.identity import NoKeychainError
from ..remote.invites import decode_invite
from ..remote.seat_session import InviteRefused, SeatEnded, SeatSession
from ..remote.secure import ChannelError
from .forms import Sheet
from .themes import Palette
from .widgets import serif, text

#: What signing in can end with, each told in words (sign_in_problem).
SIGN_IN_ERRORS = (
    SignInError,
    SeatEnded,
    NoCredential,
    NoKeychainError,
    ChannelError,
    ConnectionError,
    TimeoutError,
)

#: How often the waiting step asks whether the storyguide has approved (ms).
ASK_EVERY = 2000
NARROWEST = 560


def sign_in_problem(error: Exception) -> str:
    """What to tell the Player when signing in didn't work."""
    if isinstance(error, SignInError):
        if error.kind == "denied":
            return "That passcode isn't right."
        if error.kind == "locked":
            return f"Too many wrong passcodes: try again in {error.seconds} seconds."
        if error.kind == "short_passcode":
            return (
                "Your passcode is too short for joining over the internet. Ask "
                "your storyguide to give you one of at least 14 characters."
            )
    if isinstance(error, SeatEnded | NoCredential):
        return (
            "Your seat for this game has ended. Ask your storyguide for a new invite."
        )
    return reach_problem(error)


def reach_problem(error: Exception) -> str:
    if isinstance(error, VersionMismatch | NoKeychainError | UnreadableReply):
        return str(error)
    if isinstance(error, ChannelError | ConnectionError | TimeoutError):
        return (
            "The host can't be reached. Check the storyguide is hosting, and try again."
        )
    return str(error)


def _busy[T](work: Callable[[], T]) -> T:
    """Run one short call with the wait cursor on."""
    QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    try:
        return work()
    finally:
        QGuiApplication.restoreOverrideCursor()


class JoinWindow(Sheet):
    """The first join (see the module's docstring). Accepted means the
    Player is signed in: `session` holds the conversation."""

    def __init__(
        self,
        p: Palette,
        parent: QWidget | None = None,
        *,
        make_session: Callable[[str, str], SeatSession] = SeatSession,
    ) -> None:
        super().__init__("Join a Saga", p, "Continue", parent)
        self.p = p
        self.make_session = make_session
        self.session: SeatSession | None = None
        self.code = ""
        self.secret = ""
        self.steps = QStackedWidget()
        self.column.addWidget(self.steps, 1)
        self._paste_page()
        self._words_page()
        self._device_page()
        self._waiting_page()
        self._passcode_page()
        self.timer = QTimer(self)
        self.timer.setInterval(ASK_EVERY)
        self.timer.timeout.connect(self._ask)
        self.save.clicked.connect(self._next)
        self.finish()
        self.setMinimumWidth(NARROWEST)
        self.resize(640, 460)

    # -- the pages ---------------------------------------------------------------

    def _page(self, *widgets: QWidget) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        column.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            column.addWidget(widget)
        column.addStretch(1)
        self.steps.addWidget(page)
        return page

    def _say(self, words: str) -> QWidget:
        return text(words, self.p["foreground"], serif(13), wrap=True)

    def _paste_page(self) -> None:
        self.invite = QPlainTextEdit()
        self.invite.setPlaceholderText("ARM1.…")
        self.invite.setFixedHeight(90)
        self._page(
            self._say(
                "Paste the invite line your storyguide sent you. It begins with "
                "ARM1 and works once, on this computer."
            ),
            self.invite,
        )

    def _words_page(self) -> None:
        self.words = text("", self.p["heading"], serif(17, bold=True))
        self.words.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.match = QPushButton("They match")
        self.match.clicked.connect(self._words_match)
        self.mismatch = QPushButton("They don't match")
        self.mismatch.clicked.connect(self._words_differ)
        row = QHBoxLayout()
        row.addWidget(self.match)
        row.addWidget(self.mismatch)
        row.addStretch(1)
        buttons = QWidget()
        buttons.setLayout(row)
        self._page(
            self._say(
                "Your storyguide will read six words out on your call. Do they "
                "match these?"
            ),
            self.words,
            buttons,
        )

    def _device_page(self) -> None:
        self.device = QLineEdit(socket.gethostname()[:40])
        self.device.setMaxLength(40)
        self._page(
            self._say(
                "A name for this computer, so your storyguide knows which "
                "device is asking (you can join from more than one)."
            ),
            self.device,
        )

    def _waiting_page(self) -> None:
        self.device_words = text("", self.p["heading"], serif(17, bold=True))
        self.waiting = text("", self.p["label"], serif(12.5, italic=True), wrap=True)
        self._page(
            self._say(
                "Read these three words to your storyguide. When they match "
                "what their screen shows, they will let you in."
            ),
            self.device_words,
            self.waiting,
        )

    def _passcode_page(self) -> None:
        self.passcode = QLineEdit()
        self.passcode.setEchoMode(QLineEdit.EchoMode.Password)
        self._page(
            self._say(
                "You're in. Now your passcode, the one your storyguide gave you."
            ),
            self.passcode,
        )

    # -- moving on ---------------------------------------------------------------

    def _step(self, index: int, button: str | None) -> None:
        self.steps.setCurrentIndex(index)
        self.error.hide()
        self.save.setVisible(button is not None)
        if button is not None:
            self.save.setText(button)

    def _next(self) -> None:
        handlers = {
            0: self._read_invite,
            2: self._ask_for_seat,
            4: self._sign_in,
        }
        handler = handlers.get(self.steps.currentIndex())
        if handler is not None:
            handler()

    def _read_invite(self) -> None:
        try:
            invite = decode_invite(self.invite.toPlainText())
        except ValueError as problem:
            self.refuse(str(problem))
            return
        session = self.make_session(invite.url, invite.pin)
        try:
            _busy(session.connect)
        except (ChannelError, ConnectionError, TimeoutError) as problem:
            session.close()
            self.refuse(reach_problem(problem))
            return
        self.session, self.code = session, invite.code
        self.words.setText(session.host_words())
        self._step(1, None)

    def _words_match(self) -> None:
        self._step(2, "Ask for a Seat")

    def _words_differ(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None
        self._step(0, "Continue")
        self.refuse(
            "Then don't go on: the invite may have been changed on its way to "
            "you. Nothing was sent. Ask your storyguide for a new one, by a "
            "different way if you can."
        )

    def _ask_for_seat(self) -> None:
        session = self.session
        name = " ".join(self.device.text().split())
        if session is None or not name:
            self.refuse("Give this computer a name.")
            return
        try:
            self.secret, words = _busy(lambda: session.redeem(self.code, name))
        except (InviteRefused, NoKeychainError) as problem:
            self.refuse(
                str(problem)
                if isinstance(problem, NoKeychainError)
                else "The host didn't take that invite: it may be used or out of "
                "date. Ask your storyguide for a new one."
            )
            return
        except (ChannelError, ConnectionError, TimeoutError) as problem:
            self.refuse(reach_problem(problem))
            return
        self.device_words.setText(words)
        self.waiting.setText("Waiting for your storyguide…")
        self._step(3, None)
        self.timer.start()

    def _ask(self) -> None:
        session = self.session
        if session is None:
            return
        try:
            state = session.request_state(self.secret)
        except ChannelError, ConnectionError, TimeoutError:
            self.waiting.setText("Lost the host for a moment; still waiting…")
            return
        if state == "approved":
            self.timer.stop()
            self._step(4, "Sign In")
        elif state in ("rejected", "gone"):
            self.timer.stop()
            self.waiting.setText(
                "Your storyguide turned this device away."
                if state == "rejected"
                else "The request lapsed. Ask your storyguide for a new invite."
            )

    def _sign_in(self) -> None:
        session = self.session
        if session is None:
            return
        try:
            _busy(lambda: session.sign_in(self.passcode.text()))
        except SIGN_IN_ERRORS as problem:
            self.refuse(sign_in_problem(problem))
            return
        self.accept()

    def reject(self) -> None:
        self.timer.stop()
        if self.session is not None:
            self.session.close()
            self.session = None
        super().reject()


class PasscodeWindow(Sheet):
    """Signing in again to a Joined game: the passcode only."""

    def __init__(
        self,
        game_name: str,
        session: SeatSession,
        p: Palette,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(f"Rejoin {game_name}", p, "Sign In", parent)
        self.session = session
        self.column.addWidget(
            text("Your passcode for this saga.", p["foreground"], serif(13), wrap=True)
        )
        self.passcode = QLineEdit()
        self.passcode.setEchoMode(QLineEdit.EchoMode.Password)
        self.column.addWidget(self.passcode)
        self.save.clicked.connect(self._sign_in)
        self.finish()
        self.setMinimumWidth(NARROWEST)

    def _sign_in(self) -> None:
        try:
            _busy(self.session.connect)
            _busy(lambda: self.session.sign_in(self.passcode.text()))
        except SIGN_IN_ERRORS as problem:
            self.refuse(sign_in_problem(problem))
            return
        self.accept()
