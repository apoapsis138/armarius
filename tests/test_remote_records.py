"""Read-only records over a real connection: a signed-in seat reads its
view of the saga and the pictures it names, and nothing else; a hostile
host's replies end the conversation, never the app."""

from __future__ import annotations

import hashlib
import os
import zlib
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from test_seat_view import LEAKS, hidden_saga

from ars_magica_manager import players, storage
from ars_magica_manager.models import Saga
from ars_magica_manager.remote import audit, protocol
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.audit import AuditLog, audit_path
from ars_magica_manager.remote.client import (
    RemoteClient,
    UnreadableReply,
    VersionMismatch,
    _unpacked,
    new_device_secret,
)
from ars_magica_manager.remote.host import PATH, RemoteHost
from ars_magica_manager.remote.invites import InviteBook, book_path
from ars_magica_manager.remote.passcodes import RemotePasscodes, passcodes_path
from ars_magica_manager.remote.plan import identity_name
from ars_magica_manager.remote.protocol import MessageSpec, Reply, member_registry
from ars_magica_manager.remote.records import (
    MAX_SNAPSHOT,
    PART_BYTES,
    in_parts,
    picture_from_disk,
)
from ars_magica_manager.remote.serve import build
from ars_magica_manager.remote.vault import DeviceVault

PASSCODE = "a long enough passcode"


class Hosted:
    """A saga on disk, hosted by the real listener, with Anna's device
    approved and signed in."""

    def __init__(self, saga: Saga) -> None:
        self.saga = saga
        anna = players.find(saga, "Anna")
        assert anna is not None
        self.anna = anna
        storage.save_saga(saga)
        RemotePasscodes(passcodes_path(saga.name)).note(anna, PASSCODE)
        self.store = ident.MemoryStore()
        self.host, self.devices = build(saga.id, store=self.store)
        self.pin = ident.load_or_create(self.store, identity_name(saga.id)).pin
        self.book = InviteBook(book_path(saga.name))
        self.vault = DeviceVault(ident.MemoryStore())
        self.port = 0

    async def client(self) -> RemoteClient:
        return await RemoteClient.connect(f"ws://127.0.0.1:{self.port}{PATH}", self.pin)

    async def signed_in(self) -> RemoteClient:
        secret = new_device_secret()
        async with await self.client() as client:
            await client.redeem(
                self.book.issue(self.anna.id), "laptop", secret, self.vault
            )
            self.book.approve(self.book.pending()[0].id)
            await client.request_status(secret, self.vault)
        client = await self.client()
        await client.sign_in(PASSCODE, self.vault)
        return client


@pytest_asyncio.fixture
async def hosted() -> AsyncIterator[Hosted]:
    saga = hidden_saga()
    hosted = Hosted(saga)
    hosted.port = await hosted.host.start()
    yield hosted
    await hosted.host.stop()


async def test_a_seat_reads_its_view_and_nothing_hidden(hosted: Hosted) -> None:
    client = await hosted.signed_in()
    try:
        assert await client.hello()
        revision, saga = await client.read_saga()
    finally:
        await client.close()
    assert saga is not None and saga.id == hosted.saga.id
    assert {c.name for c in saga.covenants} >= {"Keep"}
    text = str(saga)
    assert not [where for where, word in LEAKS.items() if word in text]
    assert all(not p.passcode_hash for p in saga.players)
    assert len(revision) == 64


async def test_unchanged_is_said_in_a_line_and_only_visible_changes_count(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    try:
        revision, _ = await client.read_saga()
        again, saga = await client.read_saga(revision)
        assert (again, saga) == (revision, None)
        # A change the players can't see: no new revision.
        hosted.saga.covenants[0].secrets[0].text = "LEAK-SECRET, rewritten"
        storage.save_saga(hosted.saga)
        _bump_mtime(hosted.saga)
        assert (await client.read_saga(revision))[1] is None
        # One they can: a new revision, and the saga with it.
        hosted.saga.covenants[0].name = "Keep Renamed"
        storage.save_saga(hosted.saga)
        _bump_mtime(hosted.saga)
        fresh, saga = await client.read_saga(revision)
        assert fresh != revision and saga is not None
        assert saga.covenants[0].name == "Keep Renamed"
    finally:
        await client.close()


def _bump_mtime(saga: Saga) -> None:
    """A save inside one clock tick keeps its time: move it on, as time does."""
    path = storage.saga_path(saga.id)
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))


async def test_a_read_is_logged_once_per_sign_in(hosted: Hosted) -> None:
    client = await hosted.signed_in()
    try:
        await client.read_saga()
        await client.read_saga()
    finally:
        await client.close()
    log = AuditLog(audit_path(hosted.saga.name))
    assert [e.event for e in log.entries()].count(audit.RECORDS_READ) == 1


async def test_only_a_picture_the_saga_names_is_sent(hosted: Hosted) -> None:
    portrait = bytes(range(256)) * 400  # 100 KB: three parts
    storage.portraits_dir().mkdir(parents=True, exist_ok=True)
    (storage.portraits_dir() / "anna.png").write_bytes(portrait)
    (storage.portraits_dir() / "secret.png").write_bytes(b"not named")
    hosted.saga.characters[0].portrait = "anna.png"
    storage.save_saga(hosted.saga)
    _bump_mtime(hosted.saga)
    client = await hosted.signed_in()
    try:
        assert await client.picture("portraits", "anna.png") == portrait
        assert await client.picture("portraits", "secret.png") is None
        assert await client.picture("portraits", "../sagas/host_saga.json") is None
        assert await client.picture("sagas", "anna.png") is None
    finally:
        await client.close()


def test_a_picture_is_never_looked_up_by_a_path() -> None:
    for name in ("../x.png", "..\\x.png", "/etc/passwd", "a/b.png", "..", ""):
        assert picture_from_disk("portraits", name) is None


async def test_another_major_version_is_refused_by_name(
    hosted: Hosted, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(protocol, "__version__", "9.0.0")
    client = await hosted.client()
    try:
        with pytest.raises(VersionMismatch, match="update this app"):
            await client.hello()
    finally:
        await client.close()


# -- a hostile host ------------------------------------------------------------------


def test_a_snapshot_that_unpacks_too_large_is_refused() -> None:
    bomb = zlib.compress(b"\0" * (MAX_SNAPSHOT + 1), 9)
    assert len(bomb) < PART_BYTES * 2  # tiny on the wire
    with pytest.raises(UnreadableReply):
        _unpacked(bomb)


def _liar(reply: Reply) -> RemoteHost:
    """A host whose `snapshot` always answers `reply`, signed in or not."""
    registry = member_registry(16 * 1024)
    registry.register(MessageSpec("snapshot", {}, lambda session, body: reply))
    return RemoteHost(
        ident.build(ident.ec.generate_private_key(ident.ec.SECP256R1())),
        registry,
        members=registry,
    )


@pytest.mark.parametrize(
    "lie",
    [
        "wrong hash",
        "too few parts",
        "oversized",
        "not a saga",
        "wrong revision",
    ],
)
async def test_a_lying_host_ends_the_conversation(lie: str) -> None:
    good = b'{"id": "s", "name": "S"}'
    packed = zlib.compress(good)
    revision = hashlib.sha256(good).hexdigest()
    reply = in_parts("snapshot", packed, {"revision": revision})
    if lie == "wrong hash":
        reply = Reply(reply.type, {**reply.body, "sha256": "0" * 64}, reply.then)
    elif lie == "too few parts":
        reply = Reply(reply.type, {**reply.body, "parts": 2}, reply.then)
    elif lie == "oversized":
        reply = Reply(reply.type, {**reply.body, "size": MAX_SNAPSHOT + 1}, reply.then)
    elif lie == "not a saga":
        notsaga = zlib.compress(b"[1, 2, 3]")
        reply = in_parts(
            "snapshot", notsaga, {"revision": hashlib.sha256(b"[1, 2, 3]").hexdigest()}
        )
    elif lie == "wrong revision":
        reply = in_parts("snapshot", packed, {"revision": "1" * 64})
    host = _liar(reply)
    port = await host.start()
    try:
        client = await RemoteClient.connect(
            f"ws://127.0.0.1:{port}{PATH}", host_pin(host)
        )
        try:
            with pytest.raises(UnreadableReply):
                await client.read_saga()
        finally:
            await client.close()
    finally:
        await host.stop()


def host_pin(host: RemoteHost) -> str:
    return host._identity.pin  # the test's own host
