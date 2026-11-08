"""Read-only records: what a signed-in Remote seat may ask for, and how
it travels.

A seat asks for the saga with `snapshot`, giving the revision it already
holds. The host answers `unchanged`, or `snapshot` (the revision, the size
and a SHA-256 of what follows) and then the snapshot itself in `part`
replies, unasked. The snapshot is the seat's view of the saga (seat_view:
nothing the pages hide from that player), as the JSON a saga file holds,
compressed. A revision is a hash of that view, so a player learns that
something changed only when it is something they can see.

Pictures (portraits, maps) are asked for by name with `picture`, and only
a picture the seat's snapshot names is sent; never by a path.

Pattern: the host's half of a Remote Proxy. The player's app (client.py)
reads the saga through these messages as if it were a file.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import zlib
from collections.abc import Callable
from dataclasses import asdict, dataclass

from .. import storage, viewing
from ..models import Player, Saga
from ..seat_view import seat_view
from ..transfer import MAPS, PORTRAITS, pictures_named
from . import audit
from .changes import MEMBER_MESSAGE, SeatChanges, change_specs
from .protocol import (
    Body,
    Field,
    MessageSpec,
    Refused,
    Registry,
    Reply,
    Session,
    member_registry,
)

#: Raw bytes in one `part`: base64 makes it about 53 KB, inside the secure
#: channel's 64 KB a message.
PART_BYTES = 40_000
#: The most a snapshot (compressed or not) or a picture may be.
MAX_SNAPSHOT = 50 * 1024 * 1024
MAX_PICTURE = 5 * 1024 * 1024
REVISION_LENGTH = 64
PICTURE_NAME_MAX = 200


@dataclass(frozen=True)
class Snapshot:
    """One seat's view of the saga, ready to send."""

    revision: str
    packed: bytes  # the view's JSON, compressed
    pictures: frozenset[tuple[str, str]]  # (folder, file name) it names


def pack(data: dict[str, object]) -> tuple[str, bytes]:
    """A view's revision (the SHA-256 of its JSON) and its compressed JSON."""
    text = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(text).hexdigest(), zlib.compress(text, 6)


def in_parts(kind: str, blob: bytes, body: Body) -> Reply:
    """`blob` as a reply of `kind` (its size, SHA-256 and part count, with
    `body`) followed by its parts."""
    count = max(1, -(-len(blob) // PART_BYTES))
    parts = tuple(
        Reply(
            "part",
            {
                "index": i,
                "data": base64.b64encode(
                    blob[i * PART_BYTES : (i + 1) * PART_BYTES]
                ).decode(),
            },
        )
        for i in range(count)
    )
    head = {
        **body,
        "size": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "parts": count,
    }
    return Reply(kind, head, parts)


class SeatSnapshots:
    """The seats' views of one saga, each built once and kept until the
    saga file changes."""

    def __init__(
        self,
        saga_id: str,
        log: audit.AuditLog | None = None,
        load: Callable[[str], Saga] = storage.load_saga,
    ) -> None:
        self._saga_id = saga_id
        self._log = log
        self._load = load
        self._stamp = -1
        self._saga: Saga | None = None
        self._views: dict[str, Snapshot] = {}

    def _current(self) -> Saga:
        try:
            stamp = os.stat(storage.saga_path(self._saga_id)).st_mtime_ns
        except OSError as gone:
            raise LookupError("The saga is not there.") from gone
        if stamp != self._stamp or self._saga is None:
            self._saga = self._load(self._saga_id)
            self._stamp = stamp
            self._views.clear()
        return self._saga

    def for_player(self, player_id: str) -> Snapshot:
        """The seat's view, or LookupError once the player is gone."""
        saga = self._current()
        found = self._views.get(player_id)
        if found is not None:
            return found
        player = next((p for p in saga.players if p.id == player_id), None)
        if player is None:
            raise LookupError("No such player.")
        view = seat_view(saga, viewing.viewer_for(_as_player(player)))
        data = asdict(view)
        revision, packed = pack(data)
        if len(packed) > MAX_SNAPSHOT:
            raise ValueError("The saga is too large to send to a Remote seat.")
        snapshot = Snapshot(revision, packed, frozenset(pictures_named({"saga": data})))
        self._views[player_id] = snapshot
        return snapshot

    def noted(self, session: Session) -> None:
        """Log one read per sign-in."""
        if self._log is not None and not session.read_logged:
            self._log.record(
                audit.RECORDS_READ,
                player_id=session.player_id,
                device_id=session.device_id,
            )
            session.read_logged = True


def _as_player(player: Player) -> Player:
    """A seat always reads as a player: hosting rights stay with the
    storyguide's own window (a storyguide's seat is a later story)."""
    return Player(id=player.id, name=player.name, role="player")


def records_specs(
    snapshots: SeatSnapshots,
    picture_file: Callable[[str, str], bytes | None],
) -> list[MessageSpec]:
    """The read-only messages of a signed-in seat. `picture_file` reads a
    picture by folder and name from the host's own folders (None if it
    isn't there)."""

    def snapshot(session: Session, body: Body) -> Reply:
        try:
            found = snapshots.for_player(session.player_id)
        except LookupError, ValueError:
            raise Refused from None
        snapshots.noted(session)
        if body.get("since") == found.revision:
            return Reply("unchanged", {"revision": found.revision})
        return in_parts("snapshot", found.packed, {"revision": found.revision})

    def picture(session: Session, body: Body) -> Reply:
        folder, name = str(body["folder"]), str(body["name"])
        try:
            found = snapshots.for_player(session.player_id)
        except LookupError, ValueError:
            raise Refused from None
        if (folder, name) not in found.pictures:
            raise Refused  # one the seat's saga doesn't name: as if none
        blob = picture_file(folder, name)
        if blob is None or len(blob) > MAX_PICTURE:
            raise Refused
        return in_parts("picture", blob, {"folder": folder, "name": name})

    return [
        MessageSpec(
            "snapshot",
            {"since": Field(str, max_length=REVISION_LENGTH, required=False)},
            snapshot,
        ),
        MessageSpec(
            "picture",
            {
                "folder": Field(str, max_length=16),
                "name": Field(str, max_length=PICTURE_NAME_MAX),
            },
            picture,
        ),
    ]


def seat_registry(
    snapshots: SeatSnapshots,
    picture_file: Callable[[str, str], bytes | None],
    changes: SeatChanges,
    max_bytes: int = MEMBER_MESSAGE,
) -> Registry:
    """What a signed-in seat may send: hello, ping, the read-only messages
    and per-record changes."""
    registry = member_registry(max_bytes)
    for spec in [*records_specs(snapshots, picture_file), *change_specs(changes)]:
        registry.register(spec)
    return registry


def picture_from_disk(folder: str, name: str) -> bytes | None:
    """A picture from the host's own portraits or maps folder, by its file
    name only: a name with any path in it is never looked up."""
    if folder not in (PORTRAITS, MAPS) or not name or name != os.path.basename(name):
        return None
    if name in (".", "..") or "/" in name or "\\" in name:
        return None
    root = storage.portraits_dir() if folder == PORTRAITS else storage.maps_dir()
    path = root / name
    try:
        if path.stat().st_size > MAX_PICTURE:
            return None
        return path.read_bytes()
    except OSError:
        return None
