"""Redeeming an Invite over the real connection, end to end."""

from __future__ import annotations

import asyncio
import dataclasses
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio

from ars_magica_manager.models import Player
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.client import RemoteClient, new_device_secret
from ars_magica_manager.remote.devices import DeviceBook
from ars_magica_manager.remote.host import PATH, RemoteHost
from ars_magica_manager.remote.invites import InviteBook
from ars_magica_manager.remote.limits import Limits
from ars_magica_manager.remote.passcodes import RemotePasscodes
from ars_magica_manager.remote.redemption import door_registry
from ars_magica_manager.remote.secure import ChannelError
from ars_magica_manager.remote.vault import DeviceVault
from ars_magica_manager.remote.words import device_words

IDENTITY = ident.build(ident.ec.generate_private_key(ident.ec.SECP256R1()))
PLAYERS = {"p1": Player(id="p1", name="Anna"), "p2": Player(id="p2", name="Bruno")}


class Door:
    def __init__(
        self,
        book: InviteBook,
        devices: DeviceBook,
        host: RemoteHost,
        port: int,
    ) -> None:
        self.book, self.devices, self.host, self.port = book, devices, host, port
        self.vault = DeviceVault(ident.MemoryStore())

    @property
    def url(self) -> str:
        return f"ws://127.0.0.1:{self.port}{PATH}"

    async def client(self) -> RemoteClient:
        return await RemoteClient.connect(self.url, IDENTITY.pin)


@pytest_asyncio.fixture
async def door(tmp_path: Path) -> AsyncIterator[Door]:
    book = InviteBook(tmp_path / "invites.json")
    devices = DeviceBook(tmp_path / "devices.json")
    limits = dataclasses.replace(Limits(), max_strikes=3)
    registry = door_registry(
        limits.max_message,
        book,
        devices,
        PLAYERS.get,
        lambda: IDENTITY.pin,
        RemotePasscodes(tmp_path / "passcodes.json"),
    )
    host = RemoteHost(IDENTITY, registry, limits)
    port = await host.start()
    yield Door(book, devices, host, port)
    await host.stop()


async def test_a_player_redeems_and_the_storyguide_approves(door: Door) -> None:
    code = door.book.issue("p1")
    secret = new_device_secret()
    async with await door.client() as client:
        reply = await client.redeem(code, "Anna's laptop", secret, door.vault)
        assert (reply.type, reply.body) == ("pending", {"player": "Anna"})
        status = await client.request_status(secret, door.vault)
        assert status.body == {"state": "pending"}

        [waiting] = door.book.pending()
        assert (waiting.device, waiting.player_id) == ("Anna's laptop", "p1")
        # The Storyguide sees the same three words the player's app computes.
        assert waiting.words == " ".join(device_words(secret))
        door.book.approve(waiting.id)

        # The credential comes with the first answer after approval, into the
        # keychain stand-in, and is never offered again.
        approved = await client.request_status(secret, door.vault)
        assert approved.body.keys() == {"state", "credential"}
        assert approved.body["state"] == "approved"
        assert door.vault.load(IDENTITY.pin) == approved.body["credential"]
        again = await client.request_status(secret, door.vault)
        assert again.body == {"state": "approved"}


async def test_a_rejection_reaches_the_player(door: Door) -> None:
    secret = new_device_secret()
    async with await door.client() as client:
        await client.redeem(door.book.issue("p2"), "laptop", secret, door.vault)
        door.book.reject(door.book.pending()[0].id)
        rejected = await client.request_status(secret, door.vault)
        assert rejected.body == {"state": "rejected"}
        assert door.vault.load(IDENTITY.pin) is None


async def test_a_used_code_is_refused_like_any_bad_one(door: Door) -> None:
    code = door.book.issue("p1")
    vault = door.vault
    async with await door.client() as client:
        first = await client.redeem(code, "a", new_device_secret(), vault)
        assert first.type == "pending"
        used = await client.redeem(code, "b", new_device_secret(), vault)
        unknown = await client.redeem("AAAA-AAAA-AAAA", "b", new_device_secret(), vault)
        assert used == unknown
        assert (used.type, used.body) == ("refused", {})


async def test_guessing_codes_ends_the_connection(door: Door) -> None:
    async with await door.client() as client:
        for _ in range(3):
            reply = await client.redeem(
                door.book.issue("p1")[::-1], "a", new_device_secret(), door.vault
            )
            assert reply.type == "refused"
        with pytest.raises(ChannelError):
            await client.redeem("AAAA", "a", new_device_secret(), door.vault)


async def test_someone_else_cannot_read_a_request_without_its_secret(
    door: Door,
) -> None:
    secret = new_device_secret()
    async with await door.client() as client:
        await client.redeem(door.book.issue("p1"), "laptop", secret, door.vault)
    async with await door.client() as stranger:
        guess = await stranger.request_status(new_device_secret(), door.vault)
        assert guess.type == "refused"
        assert (await stranger.request_status(secret[:-1], door.vault)).type == (
            "refused"
        )


async def test_a_blank_or_unprintable_device_name_is_refused(door: Door) -> None:
    for device in ("", "   ", "bad\x00name", "line\nbreak"):
        async with await door.client() as client:
            reply = await client.redeem(
                door.book.issue("p1"), device, new_device_secret(), door.vault
            )
            assert reply.type == "refused"
    assert door.book.pending() == []


async def test_only_the_public_messages_are_answered(door: Door) -> None:
    for name in ("approve", "list_requests", "read_record", "shell"):
        async with await door.client() as client:
            assert (await client.request(name, {})).type == "refused"


class Spy:
    """A TCP relay that records every byte the client sends the host."""

    def __init__(self, target_port: int) -> None:
        self.target_port = target_port
        self.seen = bytearray()
        self._server: asyncio.Server | None = None

    async def start(self) -> int:
        self._server = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        return self._server.sockets[0].getsockname()[1]

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        up_reader, up_writer = await asyncio.open_connection(
            "127.0.0.1", self.target_port
        )

        async def pump(
            source: asyncio.StreamReader, sink: asyncio.StreamWriter, record: bool
        ) -> None:
            try:
                while data := await source.read(4096):
                    if record:
                        self.seen += data
                    sink.write(data)
                    await sink.drain()
            except ConnectionError:
                pass
            finally:
                sink.close()

        await asyncio.gather(
            pump(reader, up_writer, True), pump(up_reader, writer, False)
        )


async def test_the_code_and_secret_never_appear_outside_the_private_session(
    door: Door,
) -> None:
    code, secret = door.book.issue("p1"), new_device_secret()
    spy = Spy(door.port)
    port = await spy.start()
    try:
        async with await RemoteClient.connect(
            f"ws://127.0.0.1:{port}{PATH}", IDENTITY.pin
        ) as client:
            await client.redeem(code, "Anna's laptop", secret, door.vault)
    finally:
        await spy.stop()
    sent = bytes(spy.seen)
    request_line = sent.split(b"\r\n", 1)[0]
    assert request_line == f"GET {PATH} HTTP/1.1".encode()  # no query, no token
    for secret_text in (code, code.replace("-", ""), secret, "Anna's laptop"):
        assert secret_text.encode() not in sent
