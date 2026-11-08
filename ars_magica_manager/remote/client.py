"""The player's side: connect to a host, check its key, ask and be answered.

`RemoteClient.connect` opens the outer WebSocket (checked normally by the
tunnel's certificate), runs the private session inside it, and refuses the
host unless its key matches the Invite's pin before any message is sent.
Everything the host sends back is checked once as it arrives, because a
host may be hostile (see the threat model).
"""

from __future__ import annotations

import asyncio
import secrets
from typing import Self, cast

import aiohttp

from .protocol import Body, Refused, Reply, decode_reply, encode_request
from .secure import MAX_FRAME, ChannelClosed, ChannelError, SecureChannel


def new_device_secret() -> str:
    """A fresh 128-bit secret for one request, as 32 hex digits."""
    return secrets.token_hex(16)


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
    ) -> None:
        self._http = http
        self._ws = ws
        self._channel = channel

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
                ws = await http.ws_connect(url, max_msg_size=MAX_FRAME)
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
        return cls(http, ws, channel)

    async def request(self, name: str, body: Body | None = None) -> Reply:
        """Send one message and return the host's reply."""
        await self._channel.send(encode_request(name, body or {}))
        try:
            return decode_reply(await self._channel.receive())
        except Refused:
            raise ChannelError(
                "The host sent something that was not understood."
            ) from None

    async def redeem(self, code: str, device: str, secret: str) -> Reply:
        """Ask for a Remote seat with an Invite's code. `secret` is made
        by this app for the request (`new_device_secret`) and kept to ask
        how it went. Sent only inside the private session."""
        return await self.request(
            "redeem", {"code": code, "device": device, "secret": secret}
        )

    async def request_status(self, secret: str) -> Reply:
        """How the request made with `secret` stands."""
        return await self.request("request_status", {"secret": secret})

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
