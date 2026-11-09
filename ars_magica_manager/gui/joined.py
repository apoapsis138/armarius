"""The window's side of Joined games: join one, sign in again, leave it,
open it through the host (saga_store.RemoteStore), and connect again when
the connection drops.

Kept apart from window.py so the window only names each step. The Remote
seat's code (the network and keychain libraries) is imported when a
Player first joins or rejoins, not when the app opens.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QDialog

from .. import joined_games, picture_files, players
from ..joined_games import JoinedGame
from ..models import Player, Saga
from ..saga_store import LocalStore, Refreshed, RemoteStore, Saved
from .forms import ConfirmDialog

if TYPE_CHECKING:
    from ..remote.seat_session import SeatSession
    from .window import MainWindow

#: How often a Joined game asks the host what changed (seconds); a change
#: of the Player's goes at the next tick instead.
ASK_EVERY = 5.0
#: How long a talk with the host may run before the window says so.
SLOW = 4.0


@dataclass(frozen=True)
class Synced:
    """What one talk with the host brought back: what the Player's changes
    met (None when there were none to send) and the host's saga, as
    `seat.read` gives it."""

    saved: Saved | None
    read: tuple[str, Saga | None]
    #: The record the window had open when the talk began, and who else
    #: has it open (presence.py).
    record: str | None = None
    others: tuple[str, ...] = ()


@dataclass
class Talk:
    """One talk with the host, under way on a thread of its own so the
    window never waits on the network (Active Object: the window starts it
    and handles its result when it is done).

    `kind` is "sync" (send the Player's changes, then read what changed)
    or "reconnect". `edits` is the window's count of edits when it began:
    a snapshot is taken only if nothing was edited since."""

    kind: str
    future: Future[Any]
    session: SeatSession
    edits: int
    started: float
    said_slow: bool = False


def _in_background(work: Callable[[], Any]) -> Future[Any]:
    """Run `work` on a daemon thread; its result (or error) in the Future.
    A daemon, so a talk the host never answers doesn't keep the app from
    closing."""
    future: Future[Any] = Future()

    def run() -> None:
        try:
            future.set_result(work())
        # Every error is handed to the window, which says it or re-raises it.
        except BaseException as problem:  # noqa: BLE001
            future.set_exception(problem)

    threading.Thread(target=run, name="talk with the host", daemon=True).start()
    return future


def join_game(window: MainWindow) -> None:
    """Join a Saga: the first join, then the saga opens."""
    # start-up: the Remote seat's network and keychain code, on first use.
    from .join import JoinWindow

    dialog = JoinWindow(window.palette_, window)
    if window.ask(dialog) == QDialog.DialogCode.Accepted and dialog.session:
        open_joined(window, dialog.session)


def rejoin(window: MainWindow, game: JoinedGame) -> None:
    """Open a Joined game: at once if this window is still signed in to it
    (back from the shelf: the seat stays signed in until the app closes,
    the game is left, or the seat ends), else after the passcode."""
    # start-up: as join_game.
    from ..remote.seat_session import SeatSession
    from .join import PasscodeWindow

    still = window.session
    if (
        still is not None
        and still.pin == game.pin
        and window.saga is not None
        and window.saga.id == game.saga_id
    ):
        window.load(window.saga, window.player)
        return
    session = SeatSession(game.url, game.pin)
    if not session.has_credential():
        session.close()
        _ended(window, game)
        return
    dialog = PasscodeWindow(game.saga_name, session, window.palette_, window)
    if window.ask(dialog) == QDialog.DialogCode.Accepted:
        open_joined(window, session)
    else:
        session.close()


def _ended(window: MainWindow, game: JoinedGame) -> None:
    """The device's seat for `game` is gone: say so, and offer to forget it."""
    question = ConfirmDialog(
        f"Your seat for {game.saga_name} has ended: the storyguide revoked it, "
        "it went unused too long, or the host's key changed. Ask your "
        "storyguide for a new invite.\n\nForget this saga here?",
        window.palette_,
        window,
        yes_label="Forget It",
        title="Seat Ended",
    )
    if window.ask(question) == QDialog.DialogCode.Accepted:
        joined_games.forget(game)
        window.shelf_again()


def leave_game(window: MainWindow, game: JoinedGame) -> None:
    """Leave Saga: after asking, the credential goes from the keychain and
    the game from the shelf."""
    # start-up: as join_game.
    from ..remote.vault import DeviceVault

    question = ConfirmDialog(
        f"Leave {game.saga_name}?\n\nThis computer's seat is forgotten: to join "
        "again you'll need a new invite from your storyguide.",
        window.palette_,
        window,
        yes_label="Leave Saga",
        title="Leave Saga",
    )
    if window.ask(question) != QDialog.DialogCode.Accepted:
        return
    DeviceVault().forget(game.pin)
    joined_games.forget(game)
    window.shelf_again()


def change_passcode(window: MainWindow, game: JoinedGame) -> None:
    """Change Passcode, from the game's card: with the game open, through
    its session, so the key kept for reconnecting becomes the new one's;
    else on a session of its own, closed once done."""
    # start-up: as join_game.
    from ..remote.seat_session import SeatSession
    from .join import ChangePasscodeWindow

    open_one = window.session
    session = (
        open_one
        if open_one is not None and open_one.pin == game.pin
        else SeatSession(game.url, game.pin)
    )
    if session is not open_one and not session.has_credential():
        session.close()
        _ended(window, game)
        return
    dialog = ChangePasscodeWindow(game.saga_name, session, window.palette_, window)
    try:
        if window.ask(dialog) == QDialog.DialogCode.Accepted:
            window.tell(
                "Change Passcode",
                "Your passcode is changed. Use the new one from now on, on "
                "every computer you join this saga from.",
            )
    finally:
        if session is not open_one:
            session.close()


def open_joined(window: MainWindow, session: SeatSession) -> None:
    """Open the Joined game `session` is signed in to: its saga from the
    host, read as the Player, its pictures from the host."""
    store = RemoteStore(session)
    try:
        saga = store.load()
    except (ValueError, ConnectionError, TimeoutError) as problem:
        # ValueError: a saga of the wrong shape, named by field (shapes.py).
        session.close()
        window.tell("Can't Open the Saga", str(problem) or "The host can't be reached.")
        return
    joined_games.remember(JoinedGame(saga.id, saga.name, session.url, session.pin))
    window.end_joined()
    window.store, window.session = store, session
    picture_files.use_host(session.picture)
    signed = signed_in_as(saga, session)
    store.whole = is_storyguide(signed)
    window.load(saga, signed)


def signed_in_as(saga: Saga, session: SeatSession) -> Player | None:
    """The Player a seat signed in as, as the host's saga has them now."""
    return next((p for p in saga.players if p.name == session.player_name), None)


def is_storyguide(player: Player | None) -> bool:
    return player is not None and player.role == players.STORYGUIDE


def role_changed(window: MainWindow, saga: Saga) -> bool:
    """After a new snapshot `saga`, before the window seats its reader:
    the seat's Player as the host has them now, and whether the host
    changed their role. If so the window reads and saves as the new role
    from now on, and says so."""
    session, store = window.session, window.store
    if session is None or not isinstance(store, RemoteStore):
        return False
    signed = signed_in_as(saga, session)
    was = window.player.role if window.player is not None else ""
    if signed is None:
        return False
    window.player = signed
    if signed.role == was:
        return False
    store.whole = is_storyguide(signed)
    return True


def end_joined(window: MainWindow) -> None:
    """Close a Joined game's connection and go back to the data folder."""
    session = window.session
    window.session = None
    window.store = LocalStore()
    window.unsent = False
    # A talk still under way is left to end on its own; its result is
    # dropped (tick checks it is the open game's).
    window.talk = None
    window.connection_lost = False
    window.last_asked = time.monotonic()
    picture_files.use_host(None)
    if session is not None:
        session.close()


def tick(window: MainWindow) -> None:
    """A Joined game's tick: see to the talk under way, or start the next
    one (the Player's changes sent, then what changed asked for) when one
    is due. Never waits on the network."""
    session, store = window.session, window.store
    if session is None or not isinstance(store, RemoteStore):
        return
    talk = window.talk
    if talk is not None and talk.session is not session:
        window.talk = talk = None  # from a game since closed
    if talk is not None:
        if not talk.future.done():
            if not talk.said_slow and time.monotonic() - talk.started > SLOW:
                talk.said_slow = True
                window.note.say("The host is slow to answer…", window.palette_)
            return
        window.talk = None
        _finished(window, talk)
        return
    due = time.monotonic() - window.last_asked >= ASK_EVERY
    if window.connection_lost:
        if due:
            _start(window, "reconnect", session.reconnect)
        return
    if window.unsent or due:
        saga = window.saga
        now = asdict(saga) if window.unsent and saga is not None else None
        record = window.open_record_key()

        def sync() -> Synced:
            saved = store.send(now) if now is not None else None
            read = store.seat.read(store.revision)
            others = tuple(session.here(record or ""))
            return Synced(saved, read, record, others)

        _start(window, "sync", sync)


def _start(window: MainWindow, kind: str, work: Callable[[], Any]) -> None:
    session = window.session
    assert session is not None  # tick checked
    window.last_asked = time.monotonic()
    window.talk = Talk(
        kind, _in_background(work), session, window.edits, window.last_asked
    )


def _finished(window: MainWindow, talk: Talk) -> None:
    """A talk is done: show what it brought, or what went wrong."""
    # start-up: as join_game.
    from ..remote.client import AlreadyAdvanced
    from ..remote.seat_session import NeedsPasscode, SeatEnded

    problem = talk.future.exception()
    if isinstance(problem, AlreadyAdvanced):
        _advanced_first(window, problem)
        return
    if talk.kind == "reconnect":
        if problem is None:
            window.connection_lost = False
            window.note.say("Connected again.", window.palette_)
        elif isinstance(problem, NeedsPasscode):
            _needs_passcode(window)
        elif isinstance(problem, SeatEnded):
            _seat_ended(window, talk.session)
        elif not isinstance(problem, ConnectionError | TimeoutError):
            raise problem
        return
    if isinstance(problem, ConnectionError | TimeoutError):
        _lost(window)
        return
    if isinstance(problem, ValueError):
        window.unreadable(problem)
        return
    if problem is not None:
        raise problem
    synced: Synced = talk.future.result()
    window.also_here(synced.record, synced.others)
    edited_since = window.edits != talk.edits
    if synced.saved is not None:
        window.unsent = edited_since
        if synced.saved.refused:
            window.refused(synced.saved.refused)
    if edited_since:
        return  # the Player changed more meanwhile: sent, then read, next tick
    store = window.store
    assert isinstance(store, RemoteStore)  # tick checked
    found: Refreshed | None = store.take(*synced.read)
    if found is not None:
        window.picked_up(found)


def _advanced_first(window: MainWindow, problem: Exception) -> None:
    """Another storyguide advanced the season first: this window's changes
    since its last read weren't made. It takes the host's saga again."""
    store = window.store
    assert isinstance(store, RemoteStore)  # tick checked
    store.start_again()
    window.unsent = False
    window.last_asked = 0.0  # read at the next tick
    window.tell(
        "Already Advanced",
        f"{problem} Your changes since then weren't made: the saga shows the "
        "host's now. Look before advancing again.",
    )


def _lost(window: MainWindow) -> None:
    """The host stopped answering: said at once, and tried again each tick
    (in the background) until it answers, with the key kept for the
    session. Changes made meanwhile wait."""
    window.connection_lost = True
    window.last_asked = 0.0  # try again at the next tick
    window.note.say("Connection lost; trying again…", window.palette_)


def reconnect(window: MainWindow) -> None:
    """The host stopped answering a talk the window made itself."""
    _lost(window)


def _needs_passcode(window: MainWindow) -> None:
    window.end_joined()
    window.shelf_again()
    window.tell(
        "Sign In Again",
        "Your passcode changed on the host. Open the saga from the shelf "
        "to sign in with the new one.",
    )


def _seat_ended(window: MainWindow, session: SeatSession) -> None:
    game = next(
        (g for g in joined_games.listed() if g.pin == session.pin),
        JoinedGame("", "this saga", session.url, session.pin),
    )
    window.end_joined()
    window.shelf_again()
    _ended(window, game)
