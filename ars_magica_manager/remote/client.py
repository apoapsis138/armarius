"""The player's side: connect to a host, check its key, ask and be answered.

`RemoteClient.connect` opens the outer WebSocket (checked normally by the
tunnel's certificate), runs the private session inside it, and refuses the
host unless its key matches the Invite's pin before any message is sent.
Everything the host sends back is checked once as it arrives, because a
host may be hostile (see the threat model).
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import secrets
import zlib
from collections.abc import AsyncIterator, Callable
from typing import Any, Self, cast

import aiohttp

from .. import (
    __version__,
    chronicle,
    handout_list,
    picture_files,
    players,
    references,
    shows,
    storage,
    table_rolls,
    updates,
)
from ..models import Saga
from .changes import SAGA, change_messages
from .events import CHRONICLE, EVENTS, MAX_LINES, entry_of
from .identity import normalise_pin
from .proof import NONCE_BYTES, make_proof

#: A passcode's salt is 16 bytes (players.hash_passcode).
SALT_BYTES = 16
from .protocol import (
    PROTOCOL_VERSION,
    UPDATE,
    Body,
    Refused,
    Reply,
    decode_reply,
    encode_request,
    major,
)
from .records import MAX_SNAPSHOT, PART_BYTES, REVISION_LENGTH
from .secure import MAX_FRAME, ChannelClosed, ChannelError, SecureChannel
from .vault import DeviceVault

#: Seconds between the connection's pings; with no answer within half that,
#: the connection is taken as lost.
HEARTBEAT = 5.0


def new_device_secret() -> str:
    """A fresh 128-bit secret for one request, as 32 hex digits."""
    return secrets.token_hex(16)


class NoCredential(Exception):
    """This device holds no credential for the host: it needs an Invite."""


class SignInError(Exception):
    """Signing in did not succeed. `kind` is "denied" (wrong passcode),
    "locked" (wait `seconds`), "short_passcode" (the Storyguide must set a
    longer one) or "refused"."""

    def __init__(self, kind: str, seconds: int = 0) -> None:
        super().__init__(kind)
        self.kind = kind
        self.seconds = seconds


def _seconds(reply: Reply) -> int:
    value = reply.body.get("seconds", 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


class UnreadableReply(ChannelError):
    """The host sent something this app can't read: the conversation ends."""

    def __init__(self, field: str = "") -> None:
        super().__init__(
            f"The host sent a saga this app can't read ({field})."
            if field
            else "The host sent something this app can't read."
        )


class ChangeNotSaved(Exception):
    """The host refused a change: not the Player's to make, or the record
    is gone."""

    def __init__(self) -> None:
        super().__init__("The host didn't save that change.")


class AlreadyAdvanced(Exception):
    """Another storyguide advanced the season first: nothing was changed.
    `who` advanced it; `now` is the saga's season ("Summer 1221")."""

    def __init__(self, said: str) -> None:
        who, _, now = said.partition("|")
        self.who, self.now = who or "Someone", now
        super().__init__(f"{self.who} has already advanced the saga to {now}.")


class RollRefused(Exception):
    """The host wouldn't roll it; the reason, as the host said it."""

    def __init__(self, why: str) -> None:
        super().__init__(why)
        self.why = why


class MessageRefused(Exception):
    """The host wouldn't write the Message; the reason, as the host said
    it."""

    def __init__(self, why: str) -> None:
        super().__init__(why)
        self.why = why


class ShowRefused(Exception):
    """The host wouldn't make the Show, or send its copy; the reason."""

    def __init__(self, why: str) -> None:
        super().__init__(why)
        self.why = why


class SceneRefused(Exception):
    """The host wouldn't set or end the Scene; the reason."""

    def __init__(self, why: str) -> None:
        super().__init__(why)
        self.why = why


class VersionMismatch(ChannelError):
    """The host runs another major version of the app."""

    def __init__(self, ours: str, theirs: str) -> None:
        found = updates.mismatch(ours, theirs)
        super().__init__(
            found.message
            if found is not None
            else f"The host runs Armarius {theirs} and this is {ours}."
        )
        self.ours, self.theirs = ours, theirs
        #: Whether this app is the older one, and so may update.
        self.older = found is not None and found.older


def _unpacked(packed: bytes) -> bytes:
    """A snapshot's JSON, decompressed, refused past MAX_SNAPSHOT however
    small it was packed (a "zip bomb" ends here)."""
    unpacker = zlib.decompressobj()
    try:
        text = unpacker.decompress(packed, MAX_SNAPSHOT)
    except zlib.error:
        raise UnreadableReply from None
    if unpacker.unconsumed_tail or not unpacker.eof:
        raise UnreadableReply
    return text


class _ClientWire:
    """A client-side WebSocket as a Wire."""

    def __init__(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        self._ws = ws

    async def send(self, data: bytes) -> None:
        await self._ws.send_bytes(data)

    async def receive(self) -> bytes:
        message = await self._ws.receive()
        if message.type != aiohttp.WSMsgType.BINARY:
            raise ChannelClosed("The connection ended.")
        return cast(bytes, message.data)


class RemoteClient:
    """An open conversation with a host."""

    def __init__(
        self,
        http: aiohttp.ClientSession,
        ws: aiohttp.ClientWebSocketResponse,
        channel: SecureChannel,
        pin: str,
    ) -> None:
        self._http = http
        self._ws = ws
        self._channel = channel
        self._pin = pin

    @classmethod
    async def connect(cls, url: str, pin: str, timeout: float = 15.0) -> RemoteClient:
        """Open a conversation with the host at `url` (ws:// or wss://),
        whose key must match `pin`. Raises ChannelError (HostKeyMismatch if
        the key is wrong or `pin` is not a fingerprint) when it cannot be done.

        `url` must carry nothing secret: the tunnel provider logs the
        upgrade request (path, query and headers). Secrets travel only
        inside the private session."""
        http = aiohttp.ClientSession()
        try:
            async with asyncio.timeout(timeout):
                # The heartbeat pings every few seconds and closes the
                # connection if no answer comes: a dropped network is noticed
                # in seconds, not when a request times out.
                ws = await http.ws_connect(
                    url, max_msg_size=MAX_FRAME, heartbeat=HEARTBEAT
                )
                try:
                    channel = await SecureChannel.connect(_ClientWire(ws), pin)
                except BaseException:
                    await ws.close()
                    raise
        except (aiohttp.ClientError, TimeoutError) as exc:
            await http.close()
            raise ChannelError("Could not reach the host.") from exc
        except BaseException:
            await http.close()
            raise
        return cls(http, ws, channel, normalise_pin(pin))  # valid: it matched

    async def request(self, name: str, body: Body | None = None) -> Reply:
        """Send one message and return the host's reply."""
        await self._channel.send(encode_request(name, body or {}))
        try:
            return decode_reply(await self._channel.receive())
        except Refused:
            raise ChannelError(
                "The host sent something that was not understood."
            ) from None

    async def redeem(
        self, code: str, device: str, secret: str, vault: DeviceVault
    ) -> Reply:
        """Ask for a Remote seat with an Invite's code. `secret` is made
        by this app for the request (`new_device_secret`) and kept to ask
        how it went. Sent only inside the private session.

        Raises NoKeychainError, before the Invite is spent, if `vault` has
        nowhere safe to keep the credential."""
        vault.ensure_available()
        return await self.request(
            "redeem", {"code": code, "device": device, "secret": secret}
        )

    async def request_status(self, secret: str, vault: DeviceVault) -> Reply:
        """How the request made with `secret` stands. When the Storyguide
        has approved it, the reply carries the Device credential (once),
        and it goes straight into `vault`."""
        reply = await self.request("request_status", {"secret": secret})
        credential = reply.body.get("credential")
        if isinstance(credential, str) and credential:
            vault.save(self._pin, credential)
        return reply

    async def sign_in(self, passcode: str, vault: DeviceVault) -> str:
        """Sign in as the player this device was approved for, proving the
        passcode without sending it. Returns the player's name.

        Raises NoCredential, SignInError (wrong passcode, locked out, or a
        passcode too short for a Remote seat) or ChannelError."""
        return await self.sign_in_with(
            lambda salt: players.passcode_digest(passcode, salt), vault
        )

    async def sign_in_with(
        self, digest_for: Callable[[bytes], bytes], vault: DeviceVault
    ) -> str:
        """sign_in, with the passcode's derived key worked out by
        `digest_for` from the host's salt: a reconnect gives the key kept
        in memory for the session, so the passcode isn't asked again."""
        credential = vault.load(self._pin)
        if not credential:
            raise NoCredential("This device has not been approved by the host.")
        challenge = await self.request("begin_signin", {"credential": credential})
        if challenge.type == "locked":
            raise SignInError("locked", _seconds(challenge))
        if challenge.type == "short_passcode":
            raise SignInError("short_passcode")
        salt, nonce = challenge.body.get("salt"), challenge.body.get("nonce")
        if challenge.type != "challenge" or not isinstance(salt, str):
            raise SignInError("refused")
        try:
            salt_bytes, nonce_bytes = bytes.fromhex(salt), bytes.fromhex(str(nonce))
        except ValueError:
            raise SignInError("refused") from None
        # A salt and nonce of the sizes the app makes, so a hostile host
        # can't hand every player the same short salt to guess them all at
        # once from one table.
        if len(salt_bytes) != SALT_BYTES or len(nonce_bytes) != NONCE_BYTES:
            raise SignInError("refused")
        digest = digest_for(salt_bytes)
        proof = make_proof(digest, nonce_bytes, self._pin)
        reply = await self.request("prove", {"proof": proof})
        if reply.type == "signed_in":
            return str(reply.body.get("player", ""))
        if reply.type in ("denied", "locked"):
            raise SignInError(reply.type, _seconds(reply))
        raise SignInError("refused")

    async def change_passcode(self, salt: bytes, digest: bytes) -> None:
        """Set the passcode to the one whose scrypt digest under `salt` is
        `digest` (signed in just now with the old one): only the digest
        goes, never the passcode. ChangeNotSaved if the host refuses."""
        reply = await self.request(
            "change_passcode", {"salt": salt.hex(), "digest": digest.hex()}
        )
        if reply.type != "passcode_changed":
            raise ChangeNotSaved

    async def ask_reset(self, vault: DeviceVault) -> None:
        """Ask the storyguide, from this approved device, for a new passcode.
        NoCredential with no seat here; SignInError("refused") when the host
        no longer knows this device."""
        credential = vault.load(self._pin)
        if not credential:
            raise NoCredential("This device has not been approved by the host.")
        reply = await self.request("ask_reset", {"credential": credential})
        if reply.type != "reset_asked":
            raise SignInError("refused")

    async def hello(self) -> str:
        """Greet the host; its app version. Raises VersionMismatch when the
        two apps' major versions differ, saying which should update."""
        reply = await self.request(
            "hello", {"protocol": PROTOCOL_VERSION, "app": __version__}
        )
        theirs = str(reply.body.get("app", ""))
        if reply.type == UPDATE:
            raise VersionMismatch(__version__, theirs or "a newer version")
        if reply.type != "welcome":
            raise ChannelError("The host did not answer as expected.")
        spoken = reply.body.get("protocol")
        if isinstance(spoken, int) and spoken < PROTOCOL_VERSION:
            # A host from before the Chronicle: it would refuse what this
            # app asks of it.
            raise VersionMismatch(__version__, theirs)
        ours_major, their_major = major(__version__), major(theirs)
        if (
            their_major is not None
            and ours_major is not None
            and their_major != ours_major
        ):
            raise VersionMismatch(__version__, theirs)
        return theirs

    async def _parts(self, head: Reply, cap: int) -> bytes:
        """What follows `head`: its parts, joined, checked against the size
        and SHA-256 it announced. A hostile host's lies end the
        conversation, not the app."""
        size, count, digest = (head.body.get(k) for k in ("size", "parts", "sha256"))
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or not 0 <= size <= cap
            or not isinstance(count, int)
            or isinstance(count, bool)
            or count != max(1, -(-size // PART_BYTES))
            or not isinstance(digest, str)
        ):
            raise UnreadableReply
        blob = bytearray()
        for index in range(count):
            part = await self._receive()
            data = part.body.get("data")
            if part.type != "part" or part.body.get("index") != index:
                raise UnreadableReply
            if not isinstance(data, str) or len(data) > 2 * PART_BYTES:
                raise UnreadableReply
            try:
                blob += base64.b64decode(data, validate=True)
            except binascii.Error:
                raise UnreadableReply from None
            if len(blob) > size:
                raise UnreadableReply
        if len(blob) != size or hashlib.sha256(blob).hexdigest() != digest:
            raise UnreadableReply
        return bytes(blob)

    async def _receive(self) -> Reply:
        try:
            return decode_reply(await self._channel.receive())
        except Refused:
            raise UnreadableReply from None

    async def read_saga(self, since: str = "") -> tuple[str, Saga | None]:
        """The saga as this seat may read it: its revision, and the saga
        itself, or None when it hasn't changed since `since`. Loaded as a
        saga file is, read-only and in memory only. Raises UnreadableReply
        if the host sends anything this app can't read."""
        body: Body = {"since": since} if since else {}
        head = await self.request("snapshot", body)
        revision = head.body.get("revision")
        if not isinstance(revision, str) or len(revision) != REVISION_LENGTH:
            raise UnreadableReply
        if head.type == "unchanged":
            return revision, None
        if head.type != "snapshot":
            raise UnreadableReply
        text = _unpacked(await self._parts(head, MAX_SNAPSHOT))
        if hashlib.sha256(text).hexdigest() != revision:
            raise UnreadableReply
        try:
            data = json.loads(text)
        except ValueError, RecursionError:
            raise UnreadableReply from None
        try:
            # The host's data: its shape checked before and after building
            # (shapes.py), strictly, as this app's own version wrote it.
            return revision, storage.saga_from_data(data, strict=True)
        except (ValueError, KeyError, RecursionError) as problem:
            raise UnreadableReply(str(problem)[:200]) from None

    async def picture(self, folder: str, name: str) -> bytes | None:
        """A portrait or map the seat's saga names, or None if the host
        hasn't it (or won't send it). One larger than its kind's limit is
        unreadable, as is any picture of a folder that isn't a kind. A
        Show's picture is asked for in the Show folder (shows.FOLDER)."""
        found_kind = picture_files.kind(folder)
        cap = found_kind.cap if found_kind else 0
        if folder == shows.FOLDER:
            cap = shows.PICTURE_CAP
        head = await self.request("picture", {"folder": folder, "name": name})
        if head.type == "refused":
            return None
        if head.type != "picture":
            raise UnreadableReply
        return await self._parts(head, cap)

    async def here(self, record: str) -> list[str]:
        """Say which record this seat has open ("" for none); who else has
        it open (presence.py), by name."""
        reply = await self.request("here", {"record": record})
        others = reply.body.get("others")
        if reply.type != "here" or not isinstance(others, str):
            raise UnreadableReply
        return [name for name in others.split("\n") if name]

    async def send_change(
        self,
        kind: str,
        key: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> list[str]:
        """Send one change: the record (`kind`, named `key`) as the seat
        view had it and as the Player left it (None: added, or deleted).
        Returns where it overlapped a change made meanwhile (the Player's
        was kept). Raises ChangeNotSaved when the host refused it."""
        messages = change_messages(kind, key, before, after)
        reply = Reply("refused")
        for index, (name, body) in enumerate(messages):
            reply = await self.request(name, body)
            last = index == len(messages) - 1
            if reply.type == "refused" or (not last and reply.type != "more"):
                raise ChangeNotSaved
        if reply.type != "saved":
            raise UnreadableReply
        overlaps = str(reply.body.get("overlaps", ""))
        return [o for o in overlaps.split("; ") if o]

    async def send_saga(
        self, before: dict[str, Any], after: dict[str, Any]
    ) -> list[str]:
        """A storyguide's change to the whole saga (saga_delta.py): what
        changed, as it was and as they left it. The overlaps with changes
        made meanwhile (theirs kept). AlreadyAdvanced when another advanced
        the season first; ChangeNotSaved when the host refused it."""
        messages = change_messages(SAGA, "", before, after)
        reply = Reply("refused")
        for index, (name, body) in enumerate(messages):
            reply = await self.request(name, body)
            last = index == len(messages) - 1
            if reply.type == "refused" or (not last and reply.type != "more"):
                raise ChangeNotSaved
        if reply.type == "advanced":
            raise AlreadyAdvanced(str(reply.body.get("now", ""))[:120])
        if reply.type != "saved":
            raise UnreadableReply
        overlaps = str(reply.body.get("overlaps", ""))
        return [o for o in overlaps.split("; ") if o]

    async def undo_offer(self) -> tuple[str, str, list[str]] | None:
        """What the host can undo (a storyguide's seat): the season it goes
        back to, the season it is now, and the records changed since; None
        when nothing can be."""
        reply = await self.request("undo_offer")
        if reply.type == "no_undo":
            return None
        back_to, now = reply.body.get("back_to"), reply.body.get("now")
        lost = reply.body.get("lost", "")
        if reply.type != "undo" or not isinstance(back_to, str):
            raise UnreadableReply
        names = [n for n in str(lost).split("\n") if n]
        return back_to[:40], str(now)[:40], names

    async def undo_season(self, now: str) -> str:
        """Ask the host to undo the advance that reached `now`; its line
        saying so, or "" when the saga moved on meanwhile."""
        reply = await self.request("undo_season", {"now": now})
        if reply.type == "no_undo":
            return ""
        if reply.type != "undone":
            raise UnreadableReply
        return str(reply.body.get("message", ""))[:400]

    async def switched(self, playing: bool) -> None:
        """Tell the host a storyguide switched to Playing or to their
        storyguide role (remote/switches.py), for its log."""
        reply = await self.request("switched", {"playing": playing})
        if reply.type != "noted":
            raise UnreadableReply

    async def roll(self, request: chronicle.RollRequest) -> int:
        """Ask the host to roll `request` (what to roll, never a number):
        the number of its Chronicle entry. RollRefused with the host's
        reason (not a character you play tonight, too many rolls...)."""
        body: Body = {
            "die": "stress" if request.stress else "simple",
            "modifier": request.modifier,
            "botch_dice": request.botch_dice,
            "for": request.for_what,
            "character_id": request.character_id,
            "visibility": request.visibility,
        }
        if request.ease_factor is not None:
            body["ease_factor"] = request.ease_factor
        if request.sheet is not None:
            body["characteristic"] = request.sheet.characteristic
            body["ability"] = request.sheet.ability
            body["specialty"] = request.sheet.specialty
            if request.sheet.aura_realm:
                body["aura"] = request.sheet.aura
                body["aura_realm"] = request.sheet.aura_realm
                body["aura_regio"] = request.sheet.in_regio
        reply = await self.request("roll", body)
        number = reply.body.get("number")
        if reply.type == "rolled" and isinstance(number, int):
            return number
        if reply.type == "roll_refused":
            raise RollRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def say(
        self,
        words: str,
        to: tuple[str, ...] = (),
        links: tuple[references.Ref, ...] = (),
    ) -> int:
        """Ask the host to write a Message: to the Table, or a Whisper to
        `to`, linking `links`. The number of its Chronicle entry;
        MessageRefused with the host's reason."""
        reply = await self.request(
            "say",
            {
                "words": words,
                "to": "\n".join(to),
                "links": "\n".join(f"{r.kind}:{r.id}:{r.name}" for r in links),
            },
        )
        number = reply.body.get("number")
        if reply.type == "said" and isinstance(number, int):
            return number
        if reply.type == "message_refused":
            raise MessageRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def show(self, call: chronicle.ShowCall) -> int:
        """Ask the host to make Show `call` (its copy made there): the
        number of its Chronicle entry. ShowRefused with the host's reason."""
        body: Body = {
            "title": call.title,
            "to": "\n".join(call.to),
            "story_id": call.story_id,
        }
        if call.secrets:
            body["secrets"] = "\n".join(f"{row}:{mark}" for row, mark in call.secrets)
        if call.reveal:
            body["reveal"] = True
        if call.record is not None:
            body |= {"kind": call.record.kind, "id": call.record.id}
        elif call.picture is not None:
            body |= {"folder": call.picture[0], "name": call.picture[1]}
        reply = await self.request("show", body)
        number = reply.body.get("number")
        if reply.type == "shown" and isinstance(number, int):
            return number
        if reply.type == "show_refused":
            raise ShowRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def handouts(self, player_id: str) -> list[handout_list.Kept]:
        """Player `player_id`'s Handouts, worked out by the host from every
        Session's Chronicle: sent only for this seat's own Player, or any
        Player's to a storyguide. ShowRefused when they aren't sent."""
        head = await self.request("handouts", {"player": player_id})
        if head.type == "refused":
            raise ShowRefused("Those Handouts can't be read just now.")
        if head.type == "show_refused":
            raise ShowRefused(str(head.body.get("why", ""))[:200])
        if head.type != "handouts":
            raise UnreadableReply
        try:
            found = json.loads(await self._parts(head, handout_list.LIST_CAP))
            return handout_list.from_data(found)
        except ValueError, RecursionError:
            raise UnreadableReply from None

    async def withdraw(self, number: int) -> int:
        """Ask the host to withdraw Show `number`: the number of the entry
        that says so. ShowRefused with the host's reason."""
        reply = await self.request("withdraw_show", {"number": number})
        written = reply.body.get("number")
        if reply.type == "withdrawn" and isinstance(written, int):
            return written
        if reply.type == "show_refused":
            raise ShowRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def set_scene(self, call: chronicle.SceneCall) -> int:
        """Ask the host to set the Scene `call` names (the banner written
        there): the number of its Chronicle entry. SceneRefused with the
        host's reason."""
        body: Body = {"use": call.use_id, "tell_aura": call.tell_aura}
        return await self._scene_move("set_scene", body)

    async def end_scene(self) -> int:
        """Ask the host to end the Scene playing: the number of its
        Chronicle entry. SceneRefused with the host's reason."""
        return await self._scene_move("end_scene", {})

    async def _scene_move(self, kind: str, body: Body) -> int:
        reply = await self.request(kind, body)
        number = reply.body.get("number")
        if reply.type == "scene_moved" and isinstance(number, int):
            return number
        if reply.type == "scene_refused":
            raise SceneRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def show_copy(self, show_id: str) -> dict[str, Any]:
        """Show `show_id`'s copy, as the host keeps it: sent only while this
        seat's Player sees the Show. ShowRefused when it isn't sent."""
        head = await self.request("show_copy", {"show": show_id})
        if head.type == "refused":
            raise ShowRefused("This Show can't be opened.")
        if head.type == "show_refused":
            raise ShowRefused(str(head.body.get("why", ""))[:200])
        if head.type != "show_copy":
            raise UnreadableReply
        try:
            found = json.loads(await self._parts(head, shows.COPY_CAP))
        except ValueError, RecursionError:
            raise UnreadableReply from None
        if not isinstance(found, dict):
            raise UnreadableReply
        return cast(dict[str, Any], found)

    async def confidence(self, number: int, points: int) -> int:
        """Ask the host to spend `points` Confidence on roll `number`: the
        number of the spend's Chronicle entry. RollRefused with the host's
        reason (a botch, more than the Confidence Score...)."""
        reply = await self.request("confidence", {"roll": number, "points": points})
        entry = reply.body.get("number")
        if reply.type == "rolled" and isinstance(entry, int):
            return entry
        if reply.type == "roll_refused":
            raise RollRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def answer(self, request: int, character_id: str, specialty: bool) -> int:
        """Ask the host to answer Roll request `request` for
        `character_id`: the number of the roll's Chronicle entry.
        RollRefused with the host's reason."""
        reply = await self.request(
            "answer",
            {"request": request, "character_id": character_id, "specialty": specialty},
        )
        entry = reply.body.get("number")
        if reply.type == "rolled" and isinstance(entry, int):
            return entry
        if reply.type == "roll_refused":
            raise RollRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def form_die(
        self, opening: table_rolls.Opening, start: int, stop: int, step: int = 1
    ) -> int:
        """Ask the host for one die of a Table roll made from a form (the
        first opens the roll on this connection): the face it drew, from
        `range(start, stop, step)`. RollRefused with the host's reason."""
        reply = await self.request(
            "form_die",
            {
                "form": opening.form[:120],
                "character_id": opening.character_id,
                "visibility": opening.visibility,
                "start": start,
                "stop": stop,
                "step": step,
            },
        )
        face = reply.body.get("face")
        if reply.type == "die" and isinstance(face, int):
            if face not in range(start, stop, step):
                raise UnreadableReply
            return face
        if reply.type == "roll_refused":
            raise RollRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def form_done(self, lines: list[str]) -> int:
        """Close this connection's form roll with the form's result lines:
        the number of its Chronicle entry. RollRefused with the host's
        reason."""
        said = "\n".join(line.replace("\n", " ") for line in lines)[:MAX_LINES]
        reply = await self.request("form_done", {"lines": said})
        entry = reply.body.get("number")
        if reply.type == "rolled" and isinstance(entry, int):
            return entry
        if reply.type == "roll_refused":
            raise RollRefused(str(reply.body.get("why", "")))
        raise UnreadableReply

    async def form_cancel(self) -> None:
        """Cancel this connection's form roll: the dice drawn stay in the
        Chronicle, as cancelled."""
        reply = await self.request("form_cancel")
        if reply.type != "noted":
            raise UnreadableReply

    async def events(
        self, since: int, session_id: str = ""
    ) -> AsyncIterator[tuple[str, chronicle.Entry]]:
        """Turn this connection (signed in, and used for nothing else) into
        the Chronicle's events: each entry after `since` of Session
        `session_id` (what the seat holds; "" for none) that the host sends,
        with its Session's id, until the connection ends."""
        reply = await self.request(
            "events_since", {"session": session_id, "since": since}
        )
        if reply.type != EVENTS:
            raise UnreadableReply
        while True:
            found = await self._receive()
            if found.type != CHRONICLE:
                raise UnreadableReply
            try:
                yield entry_of(found.body)
            except ValueError:
                raise UnreadableReply from None

    async def close(self) -> None:
        try:
            await self._channel.close()
        except ConnectionError:
            pass  # already gone
        await self._ws.close()
        await self._http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()
