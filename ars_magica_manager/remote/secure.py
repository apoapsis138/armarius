"""A private TLS 1.3 session carried inside any pipe that moves bytes.

The storyguide's tunnel ends the outer HTTPS connection, so its provider
could read what passes through. This second session runs inside the
WebSocket and ends only at the player and the host. Python's `ssl` is given
two in-memory queues (`MemoryBIO`) instead of a network socket; this module
only carries the bytes that come out of one queue to the other end's.

The client trusts the host by its *pin* (the hash of its public key, from
the Invite), not by a certificate authority, so a wrong key is refused.

Messages are length-prefixed: TLS is a stream, so each message says how long
it is, and the length is checked before any of the message is accepted.
"""

from __future__ import annotations

import secrets
import ssl
import tempfile
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Protocol

from cryptography.hazmat.primitives import serialization

from .identity import HostIdentity, normalise_pin, public_key_hash

#: The largest message either side will accept (bytes, before encryption).
MAX_MESSAGE = 64 * 1024
#: The largest chunk handed to the pipe at once, so the pipe's own size
#: limit can stay small.
CHUNK = 16 * 1024
#: The largest block a pipe should accept from the other end.
MAX_FRAME = 2 * CHUNK
_LENGTH_BYTES = 4


class ChannelError(ConnectionError):
    """The secure channel failed: a bad handshake, damaged or oversized data."""


class ChannelClosed(ChannelError):
    """The other end closed the channel."""


class HostKeyMismatch(ChannelError):
    """The host's key is not the one the Invite named."""


class Wire(Protocol):
    """A pipe that moves whole byte blocks, such as a WebSocket's binary frames."""

    async def send(self, data: bytes) -> None: ...

    async def receive(self) -> bytes:
        """The next block. Raises ChannelClosed when the pipe ends."""
        ...


class CallableWire:
    """A Wire made from two async functions."""

    def __init__(
        self,
        send: Callable[[bytes], Awaitable[None]],
        receive: Callable[[], Awaitable[bytes]],
    ) -> None:
        self._send = send
        self._receive = receive

    async def send(self, data: bytes) -> None:
        await self._send(data)

    async def receive(self) -> bytes:
        return await self._receive()


def server_context(identity: HostIdentity) -> ssl.SSLContext:
    """The host's side: TLS 1.3 only, with the identity's key and certificate.

    The TLS library can read a key only from a file, so it is written for
    an instant, encrypted under a one-off password, and deleted at once.
    """
    password = secrets.token_hex(16)
    sealed = identity.key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode()),
    )
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    with tempfile.TemporaryDirectory() as folder:
        cert_file = Path(folder) / "cert.pem"
        key_file = Path(folder) / "key.pem"
        cert_file.write_bytes(identity.cert_pem)
        key_file.write_bytes(sealed)
        context.load_cert_chain(cert_file, key_file, password=password)
    return context


def client_context() -> ssl.SSLContext:
    """The player's side: TLS 1.3 only. No certificate authority is asked
    to vouch for the host; `SecureChannel.connect` checks the pin instead
    and drops the connection if it does not match."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


class SecureChannel:
    """One end of a private session over a Wire."""

    def __init__(
        self, wire: Wire, context: ssl.SSLContext, *, server_side: bool
    ) -> None:
        self._wire = wire
        self._incoming = ssl.MemoryBIO()
        self._outgoing = ssl.MemoryBIO()
        self._tls = context.wrap_bio(
            self._incoming, self._outgoing, server_side=server_side
        )

    @classmethod
    async def accept(cls, wire: Wire, identity: HostIdentity) -> SecureChannel:
        """The host's end, after the handshake."""
        channel = cls(wire, server_context(identity), server_side=True)
        await channel._handshake()
        return channel

    @classmethod
    async def connect(cls, wire: Wire, pin: str) -> SecureChannel:
        """The player's end, after the handshake, once the host's key is
        known to match `pin`. Nothing is sent before that check."""
        try:
            wanted = normalise_pin(pin)
        except ValueError as exc:
            raise HostKeyMismatch(str(exc)) from exc
        channel = cls(wire, client_context(), server_side=False)
        await channel._handshake()
        der = channel._tls.getpeercert(binary_form=True)
        if der is None or not secrets.compare_digest(public_key_hash(der), wanted):
            raise HostKeyMismatch("The host's key does not match the Invite.")
        return channel

    async def _flush(self) -> None:
        data = self._outgoing.read()
        for start in range(0, len(data), CHUNK):
            await self._wire.send(data[start : start + CHUNK])

    async def _feed(self) -> None:
        self._incoming.write(await self._wire.receive())

    async def _handshake(self) -> None:
        try:
            while True:
                try:
                    self._tls.do_handshake()
                except ssl.SSLWantReadError:
                    await self._flush()
                    await self._feed()
                else:
                    await self._flush()  # TLS 1.3: the server's final flight
                    return
        except ssl.SSLError as exc:
            raise ChannelError("The secure handshake failed.") from exc

    async def _read_exact(self, count: int) -> bytes:
        got = bytearray()
        while len(got) < count:
            try:
                chunk = self._tls.read(count - len(got))
            except ssl.SSLWantReadError:
                await self._feed()
                continue
            except ssl.SSLZeroReturnError as exc:
                raise ChannelClosed("The other end closed the channel.") from exc
            except ssl.SSLError as exc:
                raise ChannelError("The secure channel was damaged.") from exc
            if not chunk:
                raise ChannelClosed("The other end closed the channel.")
            got += chunk
        return bytes(got)

    def version(self) -> str | None:
        """The TLS version in use, once the handshake is done."""
        return self._tls.version()

    async def send(self, message: bytes) -> None:
        if len(message) > MAX_MESSAGE:
            raise ValueError("Message too large to send.")
        try:
            self._tls.write(len(message).to_bytes(_LENGTH_BYTES, "big") + message)
        except ssl.SSLError as exc:
            raise ChannelError("The secure channel was damaged.") from exc
        await self._flush()

    async def receive(self) -> bytes:
        """The next whole message. The size it announces is checked before
        any of it is read."""
        size = int.from_bytes(await self._read_exact(_LENGTH_BYTES), "big")
        if size > MAX_MESSAGE:
            raise ChannelError("The other end announced an oversized message.")
        return await self._read_exact(size)

    async def close(self) -> None:
        try:
            self._tls.unwrap()
        except ssl.SSLWantReadError:
            pass  # our close notice is queued; the other end's reply is not awaited
        except ssl.SSLError:
            return
        await self._flush()
