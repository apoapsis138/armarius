"""Redeeming an Invite over the real connection, end to end."""

from __future__ import annotations

import asyncio
import dataclasses
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio

from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.client import RemoteClient, new_device_secret
from ars_magica_manager.remote.host import PATH, RemoteHost
from ars_magica_manager.remote.invites import InviteBook
from ars_magica_manager.remote.limits import Limits
from ars_magica_manager.remote.redemption import door_registry
from ars_magica_manager.remote.secure import ChannelError
from ars_magica_manager.remote.words import device_words

IDENTITY = ident.build(ident.ec.generate_private_key(ident.ec.SECP256R1()))
NAMES = {"p1": "Anna", "p2": "Bruno"}


class Door:
    def __init__(self, book: InviteBook, host: RemoteHost, port: int) -> None:
        self.book, self.host, self.port = book, host, port

    @property
    def url(self) -> str:
        return f"ws://127.0.0.1:{self.port}{PATH}"

    async def client(self) -> RemoteClient:
        return await RemoteClient.connect(self.url, IDENTITY.pin)


@pytest_asyncio.fixture
async def door(tmp_path: Path) -> AsyncIterator[Door]:
    book = InviteBook(tmp_path / "invites.json")
    limits = dataclasses.replace(Limits(), max_strikes=3)
    host = RemoteHost(
        IDENTITY, door_registry(limits.max_message, book, NAMES.__getitem__), limits
    )
    port = await host.start()
    yield Door(book, host, port)
    await host.stop()


async def test_a_player_redeems_and_the_storyguide_approves(door: Door) -> None:
    code = door.book.issue("p1")
    secret = new_device_secret()
    async with await door.client() as client:
        reply = await client.redeem(code, "Anna's laptop", secret)
        assert (reply.type, reply.body) == ("pending", {"player": "Anna"})
        assert (await client.request_status(secret)).body == {"state": "pending"}

        [waiting] = door.book.pending()
        assert (waiting.device, waiting.player_id) == ("Anna's laptop", "p1")
        # The Storyguide sees the same three words the player's app computes.
        assert waiting.words == " ".join(device_words(secret))
        door.book.approve(waiting.id)

        assert (await client.request_status(secret)).body == {"state": "approved"}


async def test_a_rejection_reaches_the_player(door: Door) -> None:
    secret = new_device_secret()
    async with await door.client() as client:
        await client.redeem(door.book.issue("p2"), "laptop", secret)
        door.book.reject(door.book.pending()[0].id)
        assert (await client.request_status(secret)).body == {"state": "rejected"}


async def test_a_used_code_is_refused_like_any_bad_one(door: Door) -> None:
    code = door.book.issue("p1")
    async with await door.client() as client:
        assert (await client.redeem(code, "a", new_device_secret())).type == "pending"
        used = await client.redeem(code, "b", new_device_secret())
        unknown = await client.redeem("AAAA-AAAA-AAAA", "b", new_device_secret())
        assert used == unknown
        assert (used.type, used.body) == ("refused", {})


async def test_guessing_codes_ends_the_connection(door: Door) -> None:
    async with await door.client() as client:
        for _ in range(3):
            assert (
                await client.redeem(
                    door.book.issue("p1")[::-1], "a", new_device_secret()
                )
            ).type == "refused"
        with pytest.raises(ChannelError):
            await client.redeem("AAAA", "a", new_device_secret())


async def test_someone_else_cannot_read_a_request_without_its_secret(
    door: Door,
) -> None:
    secret = new_device_secret()
    async with await door.client() as client:
        await client.redeem(door.book.issue("p1"), "laptop", secret)
    async with await door.client() as stranger:
        assert (await stranger.request_status(new_device_secret())).type == "refused"
        assert (await stranger.request_status(secret[:-1])).type == "refused"


async def test_a_blank_or_unprintable_device_name_is_refused(door: Door) -> None:
    for device in ("", "   ", "bad\x00name", "line\nbreak"):
        async with await door.client() as client:
            reply = await client.redeem(
                door.book.issue("p1"), device, new_device_secret()
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
            await client.redeem(code, "Anna's laptop", secret)
    finally:
        await spy.stop()
    sent = bytes(spy.seen)
    request_line = sent.split(b"\r\n", 1)[0]
    assert request_line == f"GET {PATH} HTTP/1.1".encode()  # no query, no token
    for secret_text in (code, code.replace("-", ""), secret, "Anna's laptop"):
        assert secret_text.encode() not in sent
