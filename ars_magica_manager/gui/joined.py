"""The window's side of Joined games: join one, sign in again, leave it,
open it through the host (saga_store.RemoteStore), and connect again when
the connection drops.

Kept apart from window.py so the window only names each step. The Remote
seat's code (the network and keychain libraries) is imported when a
Player first joins or rejoins, not when the app opens.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from .. import joined_games, picture_files
from ..joined_games import JoinedGame
from ..saga_store import LocalStore, RemoteStore
from .forms import ConfirmDialog

if TYPE_CHECKING:
    from ..remote.seat_session import SeatSession
    from .window import MainWindow


def join_game(window: MainWindow) -> None:
    """Join a Saga: the first join, then the saga opens."""
    # start-up: the Remote seat's network and keychain code, on first use.
    from .join import JoinWindow

    dialog = JoinWindow(window.palette_, window)
    if window.ask(dialog) == QDialog.DialogCode.Accepted and dialog.session:
        open_joined(window, dialog.session)


def rejoin(window: MainWindow, game: JoinedGame) -> None:
    """Sign in again to a Joined game with the passcode, and open it."""
    # start-up: as join_game.
    from ..remote.seat_session import SeatSession
    from .join import PasscodeWindow

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
    signed = next((p for p in saga.players if p.name == session.player_name), None)
    window.load(saga, signed)


def end_joined(window: MainWindow) -> None:
    """Close a Joined game's connection and go back to the data folder."""
    session = window.session
    window.session = None
    window.store = LocalStore()
    window.unsent = False
    picture_files.use_host(None)
    if session is not None:
        session.close()


def reconnect(window: MainWindow) -> None:
    """The host stopped answering: try again (each tick until it answers),
    with the key kept for the session."""
    # start-up: as join_game.
    from ..remote.seat_session import NeedsPasscode, SeatEnded
    from ..remote.secure import ChannelError

    session = window.session
    if session is None:
        return
    window.note.say("Connection lost; trying again…", window.palette_)
    try:
        session.reconnect()
    except ChannelError, ConnectionError, TimeoutError:
        return  # the next tick tries again
    except NeedsPasscode:
        window.end_joined()
        window.shelf_again()
        window.tell(
            "Sign In Again",
            "Your passcode changed on the host. Open the game from the shelf "
            "to sign in with the new one.",
        )
        return
    except SeatEnded:
        game = next(
            (g for g in joined_games.listed() if g.pin == session.pin),
            JoinedGame("", "this game", session.url, session.pin),
        )
        window.end_joined()
        window.shelf_again()
        _ended(window, game)
        return
    window.note.say("Connected again.", window.palette_)
    if window.unsent:
        window.save_saga()
