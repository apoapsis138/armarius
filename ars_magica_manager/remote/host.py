"""The host's listener: a WebSocket on this computer that only a tunnel reaches.

It binds to the loopback address only, so nothing on the network (or the
internet) can connect to it directly; the storyguide's tunnel, running on
this computer, forwards players to it. It is off until something calls
`start`.

A connection goes through, in order: the limits (too many open, too many
recent), the secure handshake against a deadline, then a loop of messages,
each checked by the registry. The connection is closed after a few refused
messages, a long silence, or a flood. Anything that is not a WebSocket
request to `PATH` gets a plain 404.
"""

from __future__ import annotations

import asyncio
import ipaddress
from typing import cast

import aiohttp
from aiohttp import web

from .identity import HostIdentity
from .limits import ConnectionGate, Limits, RateLimiter
from .protocol import Registry, Session, encode, public_registry
from .secure import MAX_FRAME, ChannelClosed, ChannelError, SecureChannel

#: The one path that speaks the protocol.
PATH = "/remote"
#: A tunnel puts the player's real address here; trusted only when told to.
FORWARDED_HEADER = "CF-Connecting-IP"


class _ServerWire:
    """A server-side WebSocket as a Wire."""

    def __init__(self, ws: web.WebSocketResponse) -> None:
        self._ws = ws

    async def send(self, data: bytes) -> None:
        await self._ws.send_bytes(data)

    async def receive(self) -> bytes:
        message = await self._ws.receive()
        if message.type != aiohttp.WSMsgType.BINARY:
            raise ChannelClosed("The connection ended.")
        return cast(bytes, message.data)


class RemoteHost:
    """The listener. One per hosted saga."""

    def __init__(
        self,
        identity: HostIdentity,
        registry: Registry | None = None,
        limits: Limits | None = None,
        *,
        trust_forwarded_address: bool = False,
    ) -> None:
        self._identity = identity
        self._limits = limits or Limits()
        self._registry = registry or public_registry(self._limits.max_message)
        self._trust_forwarded = trust_forwarded_address
        self._connects = RateLimiter(
            self._limits.connects_per_window, self._limits.window
        )
        self._gate = ConnectionGate(
            self._limits.max_connections, self._limits.max_per_address
        )
        self._runner: web.AppRunner | None = None
        self._counter = 0

    async def start(self, port: int = 0, host: str = "127.0.0.1") -> int:
        """Begin listening on the loopback address and return the port."""
        if not _is_loopback(host):
            raise ValueError("The remote listener binds to this computer only.")
        app = web.Application()
        app.router.add_get(PATH, self._serve)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        self._runner = runner
        return int(runner.addresses[0][1])

    async def stop(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None

    def _address(self, request: web.Request) -> str:
        if self._trust_forwarded:
            forwarded = request.headers.get(FORWARDED_HEADER, "")
            if forwarded:
                return forwarded[:64]
        return request.remote or "unknown"

    async def _serve(self, request: web.Request) -> web.StreamResponse:
        if not web.WebSocketResponse().can_prepare(request).ok:
            return web.Response(status=404)
        address = self._address(request)
        if not self._connects.allow(address) or not self._gate.enter(address):
            return web.Response(status=429)
        try:
            ws = web.WebSocketResponse(max_msg_size=MAX_FRAME)
            await ws.prepare(request)
            self._counter += 1
            session = Session(label=f"c{self._counter}")
            try:
                await self._converse(ws, session)
            except ConnectionError, TimeoutError:
                pass  # the connection ended or stalled; nothing more to say
            finally:
                await ws.close()
            return ws
        finally:
            self._gate.leave(address)

    async def _converse(self, ws: web.WebSocketResponse, session: Session) -> None:
        limits = self._limits
        async with asyncio.timeout(limits.handshake_timeout):
            channel = await SecureChannel.accept(_ServerWire(ws), self._identity)
        pace = RateLimiter(limits.messages_per_window, limits.window)
        strikes = 0
        while True:
            async with asyncio.timeout(limits.idle_timeout):
                raw = await channel.receive()
            if not pace.allow("messages"):
                raise ChannelError("Too many messages.")
            reply, acceptable = self._registry.handle(session, raw)
            await channel.send(encode(reply))
            if not acceptable:
                strikes += 1
                if strikes >= limits.max_strikes:
                    raise ChannelError("Too many refused messages.")


def _is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False
