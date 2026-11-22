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

import asyncio
import secrets
from collections.abc import Callable, Coroutine
from typing import Any

from .. import chronicle, players, references, shows, table_rolls
from ..models import Saga
from ..saga_store import NotSaved
from ..undo_season import Undo
from .bridge import LoopThread
from .client import (
    ChangeNotSaved,
    MessageRefused,
    NoCredential,
    RemoteClient,
    RollRefused,
    SceneRefused,
    ShowRefused,
    SignInError,
    UnreadableReply,
    new_device_secret,
)
from .secure import ChannelError
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


#: Seconds before a dropped Chronicle connection is tried again.
CHRONICLE_RETRY = 3.0
#: The longest a roll may hold the window.
ROLL_WAIT = 8.0
#: The longest opening a Show's copy may hold the window: a map may be
#: large, but a lost host must not freeze the seat for long.
OPEN_WAIT = 12.0


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
        #: The Chronicle's events connection, while it runs (on the loop).
        self._follow_task: asyncio.Task[None] | None = None

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
        self.stop_chronicle()
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

    def undo_offer(self) -> Undo | None:
        """What the host can undo (undo_season.HostUndo), or None."""
        found = self._loop.run(self._talk().undo_offer())
        if found is None:
            return None
        back_to, now, lost = found
        return Undo(0, back_to, now, tuple(lost))

    def undo_season(self, now: str) -> str:
        """Ask the host to undo the advance that reached `now`."""
        return self._loop.run(self._talk().undo_season(now), timeout=60)

    def switched(self, *, playing: bool) -> None:
        """Tell the host a storyguide switched to Playing or to their
        storyguide role, for its log (ADR 0015)."""
        self._loop.run(self._talk().switched(playing))

    def here(self, record: str) -> list[str]:
        """Say which record this seat has open; who else has it open."""
        return self._loop.run(self._talk().here(record))

    def picture(self, folder: str, name: str) -> bytes | None:
        """A picture the saga names, asked for while a page is drawn: a few
        seconds at most, so a slow or lost host never holds the window (the
        page shows none; ConnectionError or TimeoutError)."""
        return self._loop.run(self._talk().picture(folder, name), timeout=PICTURE_WAIT)

    # -- the Chronicle (protocol 2, ADR 0019) -------------------------------------

    def _key(self, salt: bytes) -> bytes:
        """The passcode's key kept for this session, under the host's salt."""
        if salt not in self._keys:
            raise NeedsPasscode("The passcode changed on the host.")
        return self._keys[salt]

    def roll(self, request: chronicle.RollRequest) -> str | None:
        """Ask the host to roll `request`; None once it is in the
        Chronicle, else the host's reason (or why it can't be asked). It
        goes on a short connection of its own, so it never crosses the
        game's own talk with the host, and waits a few seconds at most."""
        try:
            self._loop.run(self._own(lambda c: c.roll(request)), timeout=ROLL_WAIT)
        except RollRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to roll."
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        return None

    def say(
        self,
        words: str,
        to: tuple[str, ...],
        links: tuple[references.Ref, ...],
    ) -> str | None:
        """Ask the host to write a Message (to `to`, none: the Table); None
        once it is in the Chronicle, else the host's reason (as `roll`)."""
        try:
            self._loop.run(
                self._own(lambda c: c.say(words, to, links)), timeout=ROLL_WAIT
            )
        except MessageRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to send a Message."
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        return None

    def show(self, call: chronicle.ShowCall) -> str | None:
        """Ask the host to make Show `call`; None once it is in the
        Chronicle, else the host's reason (as `roll`)."""
        try:
            self._loop.run(self._own(lambda c: c.show(call)), timeout=ROLL_WAIT)
        except ShowRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to show something."
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        return None

    def withdraw(self, number: int) -> str | None:
        """Ask the host to withdraw Show `number` (as `show`)."""
        try:
            self._loop.run(self._own(lambda c: c.withdraw(number)), timeout=ROLL_WAIT)
        except ShowRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to withdraw a Show."
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        return None

    def set_scene(self, call: chronicle.SceneCall) -> str | None:
        """Ask the host to set the Scene `call` names; None once its banner
        is in the Chronicle, else the host's reason (as `roll`)."""
        return self._scene_move(lambda c: c.set_scene(call))

    def end_scene(self) -> str | None:
        """Ask the host to end the Scene playing (as `set_scene`)."""
        return self._scene_move(lambda c: c.end_scene())

    def _scene_move(
        self, work: Callable[[RemoteClient], Coroutine[Any, Any, int]]
    ) -> str | None:
        try:
            self._loop.run(self._own(work), timeout=ROLL_WAIT)
        except SceneRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to run the Scene."
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        return None

    def open_show(self, entry: chronicle.Entry) -> shows.Shown | str:
        """Show `entry`'s copy, from the host (its picture too), which sends
        it only while this seat's Player sees the Show; else why not."""
        show_id = str(entry.body.get("show", ""))
        name = str(entry.body.get("picture", ""))

        async def fetch(client: RemoteClient) -> shows.Shown:
            kept = await client.show_copy(show_id)
            picture = await client.picture(shows.FOLDER, name) if name else None
            if name and picture is None:
                raise ShowRefused("This Show's picture can't be fetched.")
            return shows.from_copy(kept, picture)

        try:
            return self._loop.run(self._own(fetch), timeout=OPEN_WAIT)
        except ShowRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to open it."
        # UnreadableReply is a ChannelError.
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."

    async def _own[T](
        self, work: Callable[[RemoteClient], Coroutine[Any, Any, T]]
    ) -> T:
        """`work` on a short connection of its own, signed in with the key
        kept, closed after."""
        client = await self._connect_own()
        try:
            return await work(client)
        finally:
            await client.close()

    def spend_confidence(self, number: int, points: int) -> str | None:
        """Ask the host to spend `points` Confidence on roll `number`; None
        once it is in the Chronicle, else the host's reason (as `roll`)."""
        try:
            self._loop.run(
                self._own(lambda c: c.confidence(number, points)), timeout=ROLL_WAIT
            )
        except RollRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to spend Confidence."
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        return None

    def answer(
        self, request: int, character_id: str, specialty: bool = False
    ) -> str | None:
        """Ask the host to answer Roll request `request` for
        `character_id`; None once it is in the Chronicle, else the host's
        reason (as `roll`)."""
        try:
            self._loop.run(
                self._own(lambda c: c.answer(request, character_id, specialty)),
                timeout=ROLL_WAIT,
            )
        except RollRefused as refused:
            return refused.why
        except NeedsPasscode, NoCredential:
            return "Sign in again to roll."
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        return None

    def open_form_roll(self, opening: table_rolls.Opening) -> SeatFormRoll:
        """A Table roll made from a form at this seat: its dice drawn from
        the host one at a time."""
        return SeatFormRoll(self, opening)

    def table(self, held: chronicle.HasEntries) -> SeatTable:
        """The table as this seat acts at it, its Chronicle being `held`."""
        return SeatTable(self, held)

    async def _connect_own(self) -> RemoteClient:
        """A new connection of its own, signed in with the key kept."""
        client = await RemoteClient.connect(self.url, self.pin)
        try:
            await client.sign_in_with(self._key, self.vault)
        except BaseException:
            await client.close()
            raise
        return client

    def follow_chronicle(
        self,
        deliver: Callable[[str, chronicle.Entry], None],
        held: Callable[[], tuple[str, int]],
    ) -> None:
        """Keep a second connection open for the Chronicle's events, signed
        in with the key kept in memory: each entry the host sends goes to
        `deliver` (called on the connection's thread: the caller hands it
        to its own). After a dropped connection it asks again from what
        `held` says the seat holds (its Session, its last entry)."""
        if self._follow_task is not None and not self._follow_task.done():
            return
        self._loop.run(self._spawn(deliver, held))

    async def _spawn(
        self,
        deliver: Callable[[str, chronicle.Entry], None],
        held: Callable[[], tuple[str, int]],
    ) -> None:
        self._follow_task = asyncio.create_task(self._follow(deliver, held))

    def stop_chronicle(self) -> None:
        """End the Chronicle's connection, waiting for it to close."""
        if self._follow_task is not None:
            try:
                self._loop.run(self._end_follow(), timeout=5)
            except TimeoutError:
                pass  # left to the loop's own end
            self._follow_task = None

    async def _end_follow(self) -> None:
        task = self._follow_task
        if task is None:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass  # ended as asked

    async def _follow(
        self,
        deliver: Callable[[str, chronicle.Entry], None],
        held: Callable[[], tuple[str, int]],
    ) -> None:
        while True:
            try:
                client = await RemoteClient.connect(self.url, self.pin)
                try:
                    await client.sign_in_with(self._key, self.vault)
                    session_id, last = held()
                    async for found, entry in client.events(last, session_id):
                        deliver(found, entry)
                finally:
                    await client.close()
            except NeedsPasscode, NoCredential, SignInError:
                # Refused or locked out: the game's own connection says so
                # and asks for the passcode; asking again here would only
                # add to a lock-out.
                return
            except ChannelError, ConnectionError, TimeoutError:
                pass  # dropped for now: try again shortly
            await asyncio.sleep(CHRONICLE_RETRY)


class SeatTable:
    """The table as a Remote seat acts at it (at_table.Table): each verb
    asked of the host over the seat's connection, the Chronicle as the
    host sent it. Pattern: the seat's Adapter at the Table's seam."""

    def __init__(self, seat: SeatSession, held: chronicle.HasEntries) -> None:
        self.seat, self._held = seat, held

    def roll(self, request: chronicle.RollRequest) -> str | None:
        return self.seat.roll(request)

    def spend(self, number: int, points: int) -> str | None:
        return self.seat.spend_confidence(number, points)

    def answer(self, number: int, character_id: str, specialty: bool) -> str | None:
        return self.seat.answer(number, character_id, specialty)

    def say(
        self, words: str, to: tuple[str, ...], links: tuple[references.Ref, ...]
    ) -> str | None:
        return self.seat.say(words, to, links)

    def open_form_roll(self, opening: table_rolls.Opening) -> SeatFormRoll:
        return self.seat.open_form_roll(opening)

    def show(self, call: chronicle.ShowCall) -> str | None:
        return self.seat.show(call)

    def open_show(self, entry: chronicle.Entry) -> shows.Shown | str:
        return self.seat.open_show(entry)

    def withdraw(self, number: int) -> str | None:
        return self.seat.withdraw(number)

    def set_scene(self, call: chronicle.SceneCall) -> str | None:
        return self.seat.set_scene(call)

    def end_scene(self) -> str | None:
        return self.seat.end_scene()

    def held(self) -> chronicle.HasEntries | None:
        return self._held


class SeatFormRoll:
    """A Table roll made from a form at a Remote seat (Remote Proxy): the
    form takes `dice` as any source of chance, but each die is drawn by
    the host, on a connection of its own kept open for this roll, so the
    host can write the dice drawn as cancelled if the seat drops."""

    def __init__(self, seat: SeatSession, opening: table_rolls.Opening) -> None:
        self._seat, self.opening = seat, opening
        self._client: RemoteClient | None = None
        self.dice = _HostDice(self)

    def _run[T](self, work: Callable[[RemoteClient], Coroutine[Any, Any, T]]) -> T:
        """Run `work` on this roll's connection, opened at its first die."""

        async def go() -> T:
            if self._client is None:
                self._client = await self._seat._connect_own()
            return await work(self._client)

        return self._seat._loop.run(go(), timeout=ROLL_WAIT)

    def draw(self, start: int, stop: int, step: int) -> int:
        """One die from the host. DiceUnavailable says why it can't be."""
        try:
            return self._run(lambda c: c.form_die(self.opening, start, stop, step))
        except RollRefused as refused:
            raise table_rolls.DiceUnavailable(refused.why) from None
        except NeedsPasscode, NoCredential:
            raise table_rolls.DiceUnavailable("Sign in again to roll.") from None
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            raise table_rolls.DiceUnavailable(
                "The host can't be reached just now."
            ) from None

    def finish(self, lines: list[str]) -> str | None:
        if self._client is None:
            return None  # no die drawn: nothing to write
        try:
            self._run(lambda c: c.form_done(lines))
        except RollRefused as refused:
            return refused.why
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            return "The host can't be reached just now."
        finally:
            self._close()
        return None

    def cancel(self) -> None:
        if self._client is None:
            return
        try:
            self._run(lambda c: c.form_cancel())
        except ChannelError, SignInError, ConnectionError, TimeoutError:
            pass  # the host writes it as cancelled when the connection closes
        finally:
            self._close()

    def _close(self) -> None:
        client, self._client = self._client, None
        if client is not None:
            try:
                self._seat._loop.run(client.close(), timeout=5)
            except ConnectionError, TimeoutError:
                pass  # already gone


class _HostDice(table_rolls.DrawnDice):
    """The source of chance a seat's form roll takes: every die the host's."""

    def __init__(self, roll: SeatFormRoll) -> None:
        super().__init__()
        self._roll = roll

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        if stop is None:
            start, stop = 0, start
        return self._roll.draw(start, stop, step)

    def randint(self, a: int, b: int) -> int:
        return self.randrange(a, b + 1)
