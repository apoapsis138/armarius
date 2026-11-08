"""The private session inside a pipe: pinned, encrypted, tamper- and replay-proof."""

from __future__ import annotations

import asyncio
import ssl

import pytest

from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.secure import (
    MAX_MESSAGE,
    CallableWire,
    ChannelClosed,
    ChannelError,
    HostKeyMismatch,
    SecureChannel,
    Wire,
    client_context,
)

IDENTITY = ident.build(ident.ec.generate_private_key(ident.ec.SECP256R1()))


class Pipe:
    """One end of an in-memory pipe that records what it sends and can alter it."""

    def __init__(
        self, inbox: asyncio.Queue[bytes | None], outbox: asyncio.Queue[bytes | None]
    ):
        self.inbox, self.outbox = inbox, outbox
        self.sent: list[bytes] = []
        self.alter = lambda data: data

    async def send(self, data: bytes) -> None:
        self.sent.append(data)
        await self.outbox.put(self.alter(data))

    async def receive(self) -> bytes:
        data = await self.inbox.get()
        if data is None:
            raise ChannelClosed("closed")
        return data


def pipes() -> tuple[Pipe, Pipe]:
    a: asyncio.Queue[bytes | None] = asyncio.Queue()
    b: asyncio.Queue[bytes | None] = asyncio.Queue()
    return Pipe(a, b), Pipe(b, a)  # the client's outbox is the server's inbox


async def pair(
    pin: str = IDENTITY.pin,
) -> tuple[SecureChannel, SecureChannel, Pipe, Pipe]:
    client_pipe, server_pipe = pipes()
    client, server = await asyncio.gather(
        SecureChannel.connect(client_pipe, pin),
        SecureChannel.accept(server_pipe, IDENTITY),
    )
    return client, server, client_pipe, server_pipe


async def test_both_ends_are_on_tls_1_3() -> None:
    client, server, _, _ = await pair()
    assert client.version() == "TLSv1.3"
    assert server.version() == "TLSv1.3"


async def test_a_pin_pasted_with_spaces_colons_or_capitals_still_matches() -> None:
    pin = IDENTITY.pin
    pasted = ":".join(pin[i : i + 2] for i in range(0, 64, 2)).upper()
    for text in (
        pasted,
        f"  {pin.upper()}\n",
        " ".join(pin[i : i + 8] for i in range(0, 64, 8)),
    ):
        client_pipe, server_pipe = pipes()
        client, _ = await asyncio.gather(
            SecureChannel.connect(client_pipe, text),
            SecureChannel.accept(server_pipe, IDENTITY),
        )
        assert client.version() == "TLSv1.3"


@pytest.mark.parametrize("typo", ["", "abc", "é" * 64, "g" * 64, "0" * 63, "0" * 65])
async def test_a_mistyped_pin_is_refused_plainly_not_a_crash(typo: str) -> None:
    client_pipe, _ = pipes()
    with pytest.raises(HostKeyMismatch, match="not a host fingerprint"):
        await SecureChannel.connect(client_pipe, typo)


async def test_a_message_goes_both_ways() -> None:
    client, server, _, _ = await pair()
    await client.send(b"hello")
    assert await server.receive() == b"hello"
    await server.send(b"and back")
    assert await client.receive() == b"and back"


async def test_nothing_readable_crosses_the_pipe() -> None:
    client, server, client_pipe, server_pipe = await pair()
    await client.send(b"secret record 42")
    await server.receive()
    wire = b"".join(client_pipe.sent + server_pipe.sent)
    assert b"secret record" not in wire
    assert IDENTITY.pin.encode() not in wire


async def test_a_wrong_pin_is_refused_before_anything_is_sent() -> None:
    client_pipe, server_pipe = pipes()
    results = await asyncio.gather(
        SecureChannel.connect(client_pipe, "0" * 64),
        SecureChannel.accept(server_pipe, IDENTITY),
        return_exceptions=True,
    )
    assert isinstance(results[0], HostKeyMismatch)


async def test_a_damaged_frame_ends_the_session() -> None:
    client, server, client_pipe, _ = await pair()
    client_pipe.alter = lambda data: data[:-1] + bytes([data[-1] ^ 1])
    await client.send(b"hello")
    with pytest.raises(ChannelError):
        await server.receive()


async def test_a_recorded_session_cannot_be_replayed_to_a_new_client() -> None:
    _, _, _, server_pipe = await pair()
    recorded = list(server_pipe.sent)
    assert recorded
    # A new client, answered only by what the host said last time.
    replay: asyncio.Queue[bytes | None] = asyncio.Queue()
    for frame in recorded:
        replay.put_nowait(frame)
    wire: Wire = CallableWire(send=_discard, receive=replay.get)  # pyright: ignore
    with pytest.raises(ChannelError):
        await asyncio.wait_for(SecureChannel.connect(wire, IDENTITY.pin), 5)


async def _discard(data: bytes) -> None:
    return None


async def test_an_old_tls_version_is_refused() -> None:
    client_pipe, server_pipe = pipes()
    old = client_context()
    old.minimum_version = ssl.TLSVersion.TLSv1_2
    old.maximum_version = ssl.TLSVersion.TLSv1_2
    weak = SecureChannel(client_pipe, old, server_side=False)

    async def server() -> None:
        try:
            await SecureChannel.accept(server_pipe, IDENTITY)
        finally:
            await server_pipe.outbox.put(
                None
            )  # the host hangs up, as the real one does

    results = await asyncio.wait_for(
        asyncio.gather(weak._handshake(), server(), return_exceptions=True),  # pyright: ignore
        5,
    )
    assert isinstance(results[1], ChannelError)


async def test_an_oversized_announcement_is_refused_before_it_is_read() -> None:
    client, server, _, _ = await pair()
    client._tls.write((MAX_MESSAGE + 1).to_bytes(4, "big"))  # pyright: ignore
    await client._flush()  # pyright: ignore
    with pytest.raises(ChannelError, match="oversized"):
        await server.receive()


async def test_sending_too_much_is_a_mistake_in_our_own_code() -> None:
    client, _, _, _ = await pair()
    with pytest.raises(ValueError):
        await client.send(b"x" * (MAX_MESSAGE + 1))


async def test_a_message_larger_than_one_frame_arrives_whole() -> None:
    client, server, _, _ = await pair()
    big = bytes(range(256)) * 200  # 51,200 bytes, several frames
    await client.send(big)
    assert await server.receive() == big
