"""A Player's Remote seat end to end, as the desktop drives it: the session
on its own thread (seat_session.py) and the saga store over it
(saga_store.py), against a real listener. Each blocking call runs in a
worker thread here, so the listener (on the test's loop) can answer it."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest
import pytest_asyncio
from test_remote_records import Hosted, _bump_mtime
from test_seat_view import LEAKS, hidden_saga

from ars_magica_manager import players, storage
from ars_magica_manager.models import Character
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.seat_session import (
    InviteRefused,
    SeatEnded,
    SeatSession,
)
from ars_magica_manager.remote.vault import DeviceVault
from ars_magica_manager.saga_store import RemoteStore

PASSCODE = "a long enough passcode"


async def _off(call: Callable[..., Any], *args: Any) -> Any:
    return await asyncio.to_thread(call, *args)


@pytest_asyncio.fixture
async def hosted() -> AsyncIterator[Hosted]:
    saga = hidden_saga()
    anna = players.find(saga, "Anna")
    assert anna is not None
    saga.characters[0].background.player_ids = [anna.id]
    saga.characters.append(Character(id="other", name="Bertrand", type="magus"))
    hosted = Hosted(saga)
    hosted.port = await hosted.host.start()
    yield hosted
    await hosted.host.stop()


async def _joined(hosted: Hosted) -> SeatSession:
    """The whole first join: connect, redeem, approval, sign in."""
    session = SeatSession(
        f"ws://127.0.0.1:{hosted.port}{PATH}",
        hosted.pin,
        DeviceVault(ident.MemoryStore()),
    )
    await _off(session.connect)
    secret, words = await _off(
        session.redeem, hosted.book.issue(hosted.anna.id), "Anna's laptop"
    )
    assert len(words.split()) == 3
    assert await _off(session.request_state, secret) == "pending"
    hosted.book.approve(hosted.book.pending()[0].id)
    assert await _off(session.request_state, secret) == "approved"
    assert session.has_credential()
    assert await _off(session.sign_in, PASSCODE) == "Anna"
    return session


async def test_join_read_change_and_see_it_on_the_host(hosted: Hosted) -> None:
    session = await _joined(hosted)
    try:
        store = RemoteStore(session)
        saga = await _off(store.load)
        assert not [w for w in LEAKS.values() if w in str(saga)]
        saga.characters[0].name = "Leandro the Bold"
        saved = await _off(store.save, saga)
        assert saved.refused == [] and saved.overlaps == []
        assert (
            storage.load_saga(hosted.saga.id).characters[0].name == "Leandro the Bold"
        )
        # Someone else's character: refused, and listed.
        theirs = next(c for c in saga.characters if c.id == "other")
        theirs.name = "Not mine"
        saved = await _off(store.save, saga)
        assert saved.refused == ["characters:other"]
    finally:
        await _off(session.close)


async def test_another_copys_save_arrives_on_refresh(hosted: Hosted) -> None:
    session = await _joined(hosted)
    try:
        store = RemoteStore(session)
        saga = await _off(store.load)
        assert await _off(store.refresh, saga) is None
        host_saga = storage.load_saga(hosted.saga.id)
        host_saga.characters[0].name = "Renamed by the storyguide"
        storage.save_saga(host_saga)
        _later(hosted)
        fresh = await _off(store.refresh, saga)
        assert fresh is not None
        assert fresh.saga.characters[0].name == "Renamed by the storyguide"
        assert ("characters", hosted.saga.characters[0].id) in fresh.changed
    finally:
        await _off(session.close)


def _later(hosted: Hosted) -> None:
    _bump_mtime(hosted.saga)


async def test_a_dropped_connection_reconnects_without_the_passcode(
    hosted: Hosted,
) -> None:
    session = await _joined(hosted)
    try:
        await _off(session.close_connection)
        assert await _off(session.reconnect) == "Anna"
        revision, saga = await _off(session.read)
        assert saga is not None and revision
    finally:
        await _off(session.close)


async def test_a_revoked_seat_says_so_on_reconnect(hosted: Hosted) -> None:
    session = await _joined(hosted)
    try:
        await _off(session.close_connection)
        [device] = [d for d in hosted.devices.devices() if not d.ended]
        hosted.devices.revoke(device.id)
        with pytest.raises(SeatEnded):
            await _off(session.reconnect)
    finally:
        await _off(session.close)


async def test_a_spent_invite_is_refused_by_name(hosted: Hosted) -> None:
    session = SeatSession(
        f"ws://127.0.0.1:{hosted.port}{PATH}",
        hosted.pin,
        DeviceVault(ident.MemoryStore()),
    )
    try:
        await _off(session.connect)
        with pytest.raises(InviteRefused):
            await _off(session.redeem, "AAAA-BBBB-CCCC-DDDD", "laptop")
    finally:
        await _off(session.close)


def test_the_kept_key_goes_with_the_session() -> None:
    session = SeatSession(
        "ws://127.0.0.1:1/remote", "0" * 64, DeviceVault(ident.MemoryStore())
    )
    session._keys[b"salt"] = b"key"  # as a sign-in leaves it
    session.close()
    assert session._keys == {}
