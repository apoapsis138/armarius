"""Per-record changes: what a signed-in Remote seat sends to change the
saga, and how the host takes it.

A change is one record, as the seat's Seat view had it and as the Player
left it (seat_changes.py, ADR 0010), sent as compressed JSON. It goes in
one `change` message, or, when it is larger than one message holds, in
`change` and then `change_part` messages, each carrying the next piece,
with the whole one's size and SHA-256 announced first. Once the last piece
is in, the host checks it, merges it onto its saga, saves, and answers
`saved` with the places where the Player's edit overlapped one made
meanwhile. A change the Player may not make gets the one uniform refusal,
which counts as a strike on the connection, and is logged.

Pattern: Command, one record at a time, through the Protection Proxy
(players.guard_changes, inside apply_change).
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import zlib
from dataclasses import dataclass, field
from typing import Any, cast

from .. import players, storage
from ..models import Saga
from ..saga_delta import DeltaRefused, fold
from ..seat_changes import CHANGEABLE, ChangeRefused, apply_change
from . import audit
from .protocol import Body, Field, MessageSpec, Refused, Reply, Session

#: A signed-in seat's messages may be this large: room for a part of a
#: change, inside the secure channel's 64 KB a message.
MEMBER_MESSAGE = 60 * 1024
#: Raw bytes of a change in one message (base64 makes it about 4/3 more).
CHANGE_PART = 40_000
#: The most a change may be, packed and unpacked.
MAX_CHANGE = 2 * 1024 * 1024
MAX_PARTS = -(-MAX_CHANGE // CHANGE_PART)
KEY_MAX = 200
#: The kind of a storyguide's change to the whole saga (saga_delta.py).
SAGA = "saga"


@dataclass
class Upload:
    """A change arriving in parts."""

    kind: str
    key: str
    size: int
    sha256: str
    parts: int
    received: bytearray = field(default_factory=bytearray)
    next_index: int = 1


def pack_change(before: dict[str, Any] | None, after: dict[str, Any] | None) -> bytes:
    text = json.dumps({"before": before, "after": after}, separators=(",", ":"))
    return zlib.compress(text.encode(), 6)


def unpack_change(packed: bytes) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """The two versions a change carries, or Refused for anything else:
    over MAX_CHANGE unpacked, not JSON, or not two records (or none)."""
    unpacker = zlib.decompressobj()
    try:
        text = unpacker.decompress(packed, MAX_CHANGE)
    except zlib.error:
        raise Refused from None
    if unpacker.unconsumed_tail or not unpacker.eof:
        raise Refused
    try:
        data = json.loads(text)
    except UnicodeDecodeError, ValueError, RecursionError:
        raise Refused from None
    if not isinstance(data, dict) or set(data) != {"before", "after"}:
        raise Refused
    found = cast(dict[str, object], data)
    before, after = found["before"], found["after"]
    for version in (before, after):
        if version is not None and not isinstance(version, dict):
            raise Refused
    return cast(dict[str, Any] | None, before), cast(dict[str, Any] | None, after)


class SeatChanges:
    """Takes changes into one hosted saga."""

    def __init__(self, saga_id: str, log: audit.AuditLog | None = None) -> None:
        self._saga_id = saga_id
        self._log = log

    def _note(self, event: str, session: Session, record: str) -> None:
        if self._log is not None:
            self._log.record(
                event,
                player_id=session.player_id,
                device_id=session.device_id,
                record=record,
            )

    def take(self, session: Session, kind: str, key: str, packed: bytes) -> list[str]:
        """Merge the change onto the saga and save it; the overlaps. Refused
        (and logged) when it can't be read or isn't the Player's to make."""
        record = f"{kind}:{key}"
        try:
            before, after = unpack_change(packed)
            saga: Saga = storage.load_saga(self._saga_id)
            player = players.player_by_id(saga, session.player_id)
            if player is None:
                raise ChangeRefused("The Player is gone.")
            applied = apply_change(saga, player, kind, key, before, after)
        except ChangeRefused as refused:
            # Which field, for a change of the wrong shape: the record's
            # structure, never what it held.
            shape = f" {refused.field}" if refused.field else ""
            self._note(audit.CHANGE_REFUSED, session, record + shape)
            raise Refused from None
        except Refused, OSError, ValueError:
            self._note(audit.CHANGE_REFUSED, session, record)
            raise Refused from None
        # Saved in the Player's name, with no further guard: the change was
        # checked above (apply_change). Named here rather than taken from
        # this process's own reader, which isn't the listener's to use.
        storage.save_saga(applied.saga, storage.Saver(player.name))
        self._note(audit.RECORD_CHANGED, session, record)
        return applied.overlaps

    def take_saga(self, session: Session, packed: bytes) -> list[str]:
        """A storyguide's change to the whole saga (saga_delta.py), folded
        in and saved, the saga backed up first when it advances the season;
        the overlaps. DeltaRefused (with `advanced`) when another advanced
        first; Refused (and logged) for anything else it can't take."""
        try:
            before, after = unpack_change(packed)
            if before is None or after is None:
                raise Refused
            saga: Saga = storage.load_saga(self._saga_id)
            player = players.player_by_id(saga, session.player_id)
            if player is None or player.role != players.STORYGUIDE:
                raise Refused
            # Never another storyguide's records (ADR 0015).
            folded = fold(saga, before, after, by=player.id)
        except DeltaRefused as refused:
            if refused.advanced:
                raise
            self._note(audit.CHANGE_REFUSED, session, SAGA)
            raise Refused from None
        except Refused, OSError, ValueError:
            self._note(audit.CHANGE_REFUSED, session, SAGA)
            raise Refused from None
        if folded.advanced:
            storage.backup_saga(saga)
        storage.save_saga(folded.saga, storage.Saver(player.name))
        if folded.advanced:
            # Beside the backup, so the advance can be undone (undo_season.py).
            storage.remember_after(folded.saga)
        self._note(
            audit.SEASON_ADVANCED if folded.advanced else audit.RECORD_CHANGED,
            session,
            SAGA,
        )
        return folded.overlaps


def _saved(overlaps: list[str]) -> Reply:
    return Reply("saved", {"overlaps": "; ".join(overlaps)[:2000]})


def change_specs(changes: SeatChanges) -> list[MessageSpec]:
    """`change` and `change_part`. A change still arriving is held on the
    connection's own session, so it ends with the connection."""

    def piece(data: object) -> bytes:
        try:
            return base64.b64decode(str(data), validate=True)
        except binascii.Error:
            raise Refused from None

    def finish(session: Session, upload: Upload) -> Reply:
        session.upload = None
        blob = bytes(upload.received)
        if (
            len(blob) != upload.size
            or hashlib.sha256(blob).hexdigest() != upload.sha256
        ):
            raise Refused
        if upload.kind == SAGA:
            try:
                return _saved(changes.take_saga(session, blob))
            except DeltaRefused as refused:
                # Not a strike: another storyguide advanced first.
                return Reply("advanced", {"now": refused.advanced})
        return _saved(changes.take(session, upload.kind, upload.key, blob))

    def change(session: Session, body: Body) -> Reply:
        kind, key = str(body["kind"]), str(body["key"])
        size, parts = int(body["size"]), int(body["parts"])
        known = kind in CHANGEABLE or kind == SAGA
        if not known or parts != max(1, -(-size // CHANGE_PART)):
            raise Refused
        upload = Upload(kind, key, size, str(body["sha256"]), parts)
        upload.received += piece(body["data"])
        if len(upload.received) > size:
            raise Refused
        if parts == 1:
            return finish(session, upload)
        session.upload = upload
        return Reply("more", {"next": 1})

    def change_part(session: Session, body: Body) -> Reply:
        upload = session.upload
        if not isinstance(upload, Upload) or int(body["index"]) != upload.next_index:
            session.upload = None
            raise Refused
        upload.received += piece(body["data"])
        if len(upload.received) > upload.size:
            session.upload = None
            raise Refused
        upload.next_index += 1
        if upload.next_index == upload.parts:
            return finish(session, upload)
        return Reply("more", {"next": upload.next_index})

    data = Field(str, max_length=MEMBER_MESSAGE - 1024)
    return [
        MessageSpec(
            "change",
            {
                "kind": Field(str, max_length=32),
                "key": Field(str, max_length=KEY_MAX),
                "size": Field(int, low=0, high=MAX_CHANGE),
                "sha256": Field(str, max_length=64),
                "parts": Field(int, low=1, high=MAX_PARTS),
                "data": data,
            },
            change,
        ),
        MessageSpec(
            "change_part",
            {"index": Field(int, low=1, high=MAX_PARTS), "data": data},
            change_part,
        ),
    ]


def change_messages(
    kind: str,
    key: str,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> list[tuple[str, Body]]:
    """The messages a seat sends for one change, in order (the player's
    side, client.py)."""
    packed = pack_change(before, after)
    if len(packed) > MAX_CHANGE:
        raise ValueError("That change is too large to send.")
    pieces = [packed[i : i + CHANGE_PART] for i in range(0, len(packed), CHANGE_PART)]
    pieces = pieces or [b""]

    def text(chunk: bytes) -> str:
        return base64.b64encode(chunk).decode()

    first: Body = {
        "kind": kind,
        "key": key,
        "size": len(packed),
        "sha256": hashlib.sha256(packed).hexdigest(),
        "parts": len(pieces),
        "data": text(pieces[0]),
    }
    rest: list[tuple[str, Body]] = [
        ("change_part", {"index": i, "data": text(chunk)})
        for i, chunk in enumerate(pieces[1:], start=1)
    ]
    return [("change", first), *rest]
