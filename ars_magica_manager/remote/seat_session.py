"""A Player's Remote seat as a front-end uses it: one call at a time, each
waiting for its answer, on the connection's own thread (bridge.py).

It joins (redeem an Invite, wait for the Storyguide, sign in), reads the
saga and sends changes, and connects again by itself when the connection
drops. To do that without asking for the passcode again it keeps the
passcode's derived key (its scrypt digest under the host's salt) in memory
for as long as this session lasts; it is never written anywhere, and the
passcode itself is not kept at all.

Pattern: Facade over the client's conversation (client.py), and the
player's half of the Remote Proxy (saga_store.py).
"""

from __future__ import annotations

import secrets
from typing import Any

from .. import players
from ..models import Saga
from ..saga_store import NotSaved
from .bridge import LoopThread
from .client import (
    ChangeNotSaved,
    RemoteClient,
    SignInError,
    UnreadableReply,
    new_device_secret,
)
from .vault import DeviceVault
from .words import device_words, host_words, two_lines

#: The longest a picture may be waited for while a page is drawn (seconds).
PICTURE_WAIT = 4.0


class InviteRefused(Exception):
    """The host didn't take the Invite: unknown, used or expired."""


class SeatEnded(Exception):
    """This device's seat has ended: revoked, expired, or the host key
    rotated. The Player needs a new Invite."""


class NeedsPasscode(Exception):
    """A reconnect needs the passcode again (it changed on the host)."""


class SeatSession:
    """A Player's conversation with one host."""

    def __init__(
        self,
        url: str,
        pin: str,
        vault: DeviceVault | None = None,
        loop: LoopThread | None = None,
    ) -> None:
        self.url, self.pin = url, pin
        self.vault = vault or DeviceVault()
        self._loop = loop or LoopThread()
        self._client: RemoteClient | None = None
        #: The passcode's derived key under each salt the host has sent,
        #: for this session only.
        self._keys: dict[bytes, bytes] = {}
        self.host_version = ""
        #: Who this device signed in as, once it has.
        self.player_name = ""

    # -- the connection --------------------------------------------------------

    def _talk(self) -> RemoteClient:
        if self._client is None:
            raise ConnectionError("Not connected.")
        return self._client

    def connect(self) -> str:
        """Open the connection (the host's key checked against the pin) and
        greet; the host's app version. ChannelError (or VersionMismatch)
        when it can't."""
        self.close_connection()
        self._client = self._loop.run(RemoteClient.connect(self.url, self.pin))
        self.host_version = self._loop.run(self._talk().hello())
        return self.host_version

    def close_connection(self) -> None:
        if self._client is not None:
            client, self._client = self._client, None
            try:
                self._loop.run(client.close(), timeout=5)
            except ConnectionError, TimeoutError:
                pass  # already gone

    def close(self) -> None:
        """End the session: the connection, its thread and the key kept."""
        self.close_connection()
        self._keys.clear()
        self._loop.stop()

    def host_words(self) -> str:
        """The host's six words (two lines), from the pin."""
        return two_lines(host_words(self.pin))

    # -- joining -----------------------------------------------------------------

    def has_credential(self) -> bool:
        return bool(self.vault.load(self.pin))

    def redeem(self, code: str, device: str) -> tuple[str, str]:
        """Ask for a seat with an Invite's code; the request's secret and the
        device's three words to read to the Storyguide. NoKeychainError
        before anything is spent if this computer has no keychain;
        InviteRefused if the host won't take the code."""
        self.vault.ensure_available()
        secret = new_device_secret()
        reply = self._loop.run(self._talk().redeem(code, device, secret, self.vault))
        if reply.type != "pending":
            raise InviteRefused("The invite wasn't accepted.")
        return secret, " ".join(device_words(secret))

    def request_state(self, secret: str) -> str:
        """How the request stands: "pending", "approved" (the credential is
        now in the keychain), "rejected", or "gone" (lapsed or unknown)."""
        reply = self._loop.run(self._talk().request_status(secret, self.vault))
        state = reply.body.get("state")
        if reply.type != "state" or not isinstance(state, str):
            return "gone"
        return state

    def sign_in(self, passcode: str) -> str:
        """Sign in; the Player's name. Keeps the passcode's derived key for
        reconnecting. SignInError, NoCredential or ChannelError."""
        used: dict[bytes, bytes] = {}

        def key(salt: bytes) -> bytes:
            used[salt] = players.passcode_digest(passcode, salt)
            return used[salt]

        name = self._signed_in(key)
        self._keys.update(used)
        return name

    def _signed_in(self, key: Any) -> str:
        """Sign in with `key`; SeatEnded when the host no longer knows this
        device (the one refusal it gives a credential it won't take)."""
        try:
            self.player_name = self._loop.run(
                self._talk().sign_in_with(key, self.vault)
            )
            return self.player_name
        except SignInError as error:
            if error.kind == "refused":
                raise SeatEnded("This device's seat has ended.") from error
            raise

    def reconnect(self) -> str:
        """Connect and sign in again with the key kept in memory; the
        Player's name. NeedsPasscode if the host's salt changed (a new
        passcode); ChannelError while the host can't be reached."""
        self.connect()

        def key(salt: bytes) -> bytes:
            if salt not in self._keys:
                raise NeedsPasscode("The passcode changed on the host.")
            return self._keys[salt]

        return self._signed_in(key)

    def change_passcode(self, old: str, new: str) -> None:
        """Change this Player's passcode (ADR 0013): `new` checked here (the
        host never sees it), then, on a connection of its own so the
        game's own talks go on, a fresh sign-in with `old` and the new
        one's digest under a fresh salt sent. The key kept for reconnecting
        becomes the new one's. ValueError for a new passcode too short;
        SignInError (a wrong `old`, or a lock-out), SeatEnded, ChangeNotSaved
        or ChannelError otherwise."""
        problem = players.passcode_problem(new)
        if problem is not None:
            raise ValueError(problem)
        salt = secrets.token_bytes(16)

        async def change() -> bytes:
            client = await RemoteClient.connect(self.url, self.pin)
            async with client:
                await client.hello()
                try:
                    await client.sign_in(old, self.vault)
                except SignInError as error:
                    if error.kind == "refused":
                        raise SeatEnded("This device's seat has ended.") from error
                    raise
                digest = players.passcode_digest(new, salt)
                await client.change_passcode(salt, digest)
                return digest

        digest = self._loop.run(change(), timeout=60)
        self._keys = {salt: digest}

    def ask_reset(self) -> None:
        """Ask the storyguide for a new passcode, from this device's seat:
        connects first. SeatEnded when the host no longer knows the device;
        NoCredential or ChannelError otherwise."""
        self.connect()
        try:
            self._loop.run(self._talk().ask_reset(self.vault))
        except SignInError as error:
            raise SeatEnded("This device's seat has ended.") from error

    def forget_seat(self) -> None:
        """Leave the game: the credential goes from the keychain."""
        self.vault.forget(self.pin)

    # -- the saga ----------------------------------------------------------------

    def read(self, since: str = "") -> tuple[str, Saga | None]:
        """The saga, as the host's copy is: ValueError (naming the field)
        when it sends one this app can't read, which ends the conversation
        (the next read connects again)."""
        try:
            return self._loop.run(self._talk().read_saga(since), timeout=120)
        except UnreadableReply as problem:
            self.close_connection()
            raise ValueError(str(problem)) from None

    def send_change(
        self,
        kind: str,
        key: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> list[str]:
        try:
            return self._loop.run(self._talk().send_change(kind, key, before, after))
        except ChangeNotSaved as refused:
            raise NotSaved(f"{kind}:{key}") from refused

    def send_saga(self, before: dict[str, Any], after: dict[str, Any]) -> list[str]:
        """A storyguide's change to the whole saga; the overlaps. NotSaved
        when the host refused it; AlreadyAdvanced as client.send_saga."""
        try:
            return self._loop.run(self._talk().send_saga(before, after), timeout=120)
        except ChangeNotSaved as refused:
            raise NotSaved("saga") from refused

    def here(self, record: str) -> list[str]:
        """Say which record this seat has open; who else has it open."""
        return self._loop.run(self._talk().here(record))

    def picture(self, folder: str, name: str) -> bytes | None:
        """A picture the saga names, asked for while a page is drawn: a few
        seconds at most, so a slow or lost host never holds the window (the
        page shows none; ConnectionError or TimeoutError)."""
        return self._loop.run(self._talk().picture(folder, name), timeout=PICTURE_WAIT)
