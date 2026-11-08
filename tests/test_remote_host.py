"""The listener and client together, over real localhost sockets."""

from __future__ import annotations

import asyncio
import dataclasses
from collections.abc import AsyncIterator, Awaitable, Callable

import aiohttp
import pytest
import pytest_asyncio

from ars_magica_manager import __version__
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.client import RemoteClient
from ars_magica_manager.remote.host import PATH, RemoteHost
from ars_magica_manager.remote.limits import Limits
from ars_magica_manager.remote.secure import ChannelError, HostKeyMismatch

IDENTITY = ident.build(ident.ec.generate_private_key(ident.ec.SECP256R1()))
HELLO = {"protocol": 1}

Start = Callable[..., Awaitable[str]]


@pytest_asyncio.fixture
async def start() -> AsyncIterator[Start]:
    """Starts a host with the given limits and returns its address."""
    hosts: list[RemoteHost] = []

    async def _start(limits: Limits | None = None, **options: bool | str) -> str:
        host = RemoteHost(IDENTITY, limits=limits, **options)
        hosts.append(host)
        port = await host.start()
        return f"127.0.0.1:{port}"

    yield _start
    for host in hosts:
        await host.stop()


def url(address: str) -> str:
    return f"ws://{address}{PATH}"


def small(**changes: float) -> Limits:
    return dataclasses.replace(Limits(), **changes)  # pyright: ignore


async def wait_until(condition: Callable[[], bool], seconds: float = 3.0) -> None:
    async with asyncio.timeout(seconds):
        while not condition():
            await asyncio.sleep(0.02)


async def test_a_player_says_hello_and_is_welcomed(start: Start) -> None:
    address = await start()
    async with await RemoteClient.connect(url(address), IDENTITY.pin) as client:
        reply = await client.request("hello", HELLO)
    assert (reply.type, reply.body) == (
        "welcome",
        {"protocol": 1, "app": __version__},
    )


async def test_a_wrong_pin_is_refused(start: Start) -> None:
    address = await start()
    with pytest.raises(HostKeyMismatch):
        await RemoteClient.connect(url(address), "0" * 64)


async def test_an_unreachable_host_is_a_plain_error() -> None:
    with pytest.raises(ChannelError, match="Could not reach"):
        await RemoteClient.connect("ws://127.0.0.1:1/remote", IDENTITY.pin, timeout=3)


async def test_unknown_and_malformed_messages_are_refused_alike(start: Start) -> None:
    address = await start(small(max_strikes=100))
    async with await RemoteClient.connect(url(address), IDENTITY.pin) as client:
        for name, body in (("shell", {}), ("hello", {}), ("hello", {"protocol": "1"})):
            reply = await client.request(name, body)  # type: ignore[arg-type]
            assert (reply.type, reply.body) == ("refused", {})
        assert (await client.request("hello", HELLO)).type == "welcome"  # still usable


async def test_the_connection_is_closed_after_a_few_refusals(start: Start) -> None:
    address = await start(small(max_strikes=2))
    async with await RemoteClient.connect(url(address), IDENTITY.pin) as client:
        await client.request("shell")
        await client.request("shell")
        with pytest.raises(ChannelError):
            await client.request("hello", HELLO)


async def test_an_oversized_message_is_refused(start: Start) -> None:
    address = await start(small(max_message=200, max_strikes=100))
    async with await RemoteClient.connect(url(address), IDENTITY.pin) as client:
        reply = await client.request("hello", {"protocol": 1, "pad": "x" * 500})  # type: ignore[dict-item]
        assert reply.type == "refused"


async def test_a_flood_closes_the_connection(start: Start) -> None:
    address = await start(small(messages_per_window=3))
    async with await RemoteClient.connect(url(address), IDENTITY.pin) as client:
        for _ in range(3):
            await client.request("hello", HELLO)
        with pytest.raises(ChannelError):
            await client.request("hello", HELLO)


async def test_a_silent_connection_is_closed_after_the_idle_time(start: Start) -> None:
    address = await start(small(idle_timeout=0.3))
    async with await RemoteClient.connect(url(address), IDENTITY.pin) as client:
        await asyncio.sleep(0.6)
        with pytest.raises(ChannelError):
            await client.request("hello", HELLO)


async def test_a_connection_that_never_shakes_hands_is_closed(start: Start) -> None:
    address = await start(small(handshake_timeout=0.3))
    async with aiohttp.ClientSession() as http, http.ws_connect(url(address)) as ws:
        message = await asyncio.wait_for(ws.receive(), 3)
        assert message.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED)


async def test_garbage_instead_of_a_handshake_is_dropped(start: Start) -> None:
    address = await start()
    async with aiohttp.ClientSession() as http, http.ws_connect(url(address)) as ws:
        await ws.send_bytes(b"GET / HTTP/1.0\r\n\r\n" + bytes(64))
        message = await asyncio.wait_for(ws.receive(), 3)
        assert message.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED)


async def test_anything_but_the_websocket_path_is_a_404(start: Start) -> None:
    address = await start()
    async with aiohttp.ClientSession() as http:
        for path in ("/", "/admin", "/remote/x", "/.git/config"):
            async with http.get(f"http://{address}{path}") as response:
                assert response.status == 404
        async with http.get(f"http://{address}{PATH}") as response:  # not an upgrade
            assert response.status == 404
        async with http.post(f"http://{address}{PATH}") as response:
            assert response.status == 405


async def test_the_host_will_not_listen_beyond_this_computer() -> None:
    for address in ("0.0.0.0", "192.168.1.5", "example.com", ""):
        with pytest.raises(ValueError, match="this computer only"):
            await RemoteHost(IDENTITY).start(host=address)


async def test_too_many_connections_from_one_address_are_turned_away(
    start: Start,
) -> None:
    address = await start(small(max_per_address=1, handshake_timeout=5))
    first = await RemoteClient.connect(url(address), IDENTITY.pin)
    try:
        with pytest.raises(ChannelError):
            await RemoteClient.connect(url(address), IDENTITY.pin)
    finally:
        await first.close()

    # A closed connection frees its place.
    async def can_connect() -> bool:
        try:
            await (await RemoteClient.connect(url(address), IDENTITY.pin)).close()
        except ChannelError:
            return False
        return True

    async with asyncio.timeout(3):
        while not await can_connect():
            await asyncio.sleep(0.05)


async def test_too_many_new_connections_in_a_minute_are_turned_away(
    start: Start,
) -> None:
    address = await start(small(connects_per_window=2))
    for _ in range(2):
        await (await RemoteClient.connect(url(address), IDENTITY.pin)).close()
    with pytest.raises(ChannelError):
        await RemoteClient.connect(url(address), IDENTITY.pin)


async def _held(
    http: aiohttp.ClientSession, address: str, ip: str
) -> aiohttp.ClientWebSocketResponse:
    return await http.ws_connect(url(address), headers={"CF-Connecting-IP": ip})


async def test_a_forwarded_address_is_ignored_unless_trusted(start: Start) -> None:
    address = await start(small(max_per_address=1, handshake_timeout=5))
    async with aiohttp.ClientSession() as http:
        first = await _held(http, address, "1.1.1.1")
        with pytest.raises(
            aiohttp.WSServerHandshakeError
        ):  # the header cannot dodge the limit
            await _held(http, address, "2.2.2.2")
        await first.close()


async def test_a_forwarded_address_counts_when_the_tunnel_is_trusted(
    start: Start,
) -> None:
    address = await start(
        small(max_per_address=1, handshake_timeout=5), trust_forwarded_address=True
    )
    async with aiohttp.ClientSession() as http:
        first = await _held(http, address, "1.1.1.1")
        second = await _held(http, address, "2.2.2.2")  # a different player
        with pytest.raises(aiohttp.WSServerHandshakeError):
            await _held(http, address, "1.1.1.1")  # the same player twice
        await first.close()
        await second.close()


async def test_a_list_header_counts_the_hop_the_tunnel_added(start: Start) -> None:
    """X-Forwarded-For may carry addresses the player wrote; the tunnel adds
    the real one last, so that one counts."""
    address = await start(
        small(max_per_address=1, handshake_timeout=5),
        trust_forwarded_address=True,
        forwarded_header="X-Forwarded-For",  # pyright: ignore[reportArgumentType]
    )

    async def held(
        http: aiohttp.ClientSession, chain: str
    ) -> aiohttp.ClientWebSocketResponse:
        return await http.ws_connect(url(address), headers={"X-Forwarded-For": chain})

    async with aiohttp.ClientSession() as http:
        first = await held(http, "9.9.9.9, 1.1.1.1")
        with pytest.raises(aiohttp.WSServerHandshakeError):
            await held(http, "8.8.8.8, 1.1.1.1")  # a forged first hop changes nothing
        await first.close()
