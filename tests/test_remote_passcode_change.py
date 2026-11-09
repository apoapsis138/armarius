"""A player changes their own passcode from their Remote seat, and asks
for a new one when they've forgotten it (ADR 0013), over a real connection."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from test_remote_records import PASSCODE, Hosted
from test_seat_view import hidden_saga

from ars_magica_manager import players, storage
from ars_magica_manager.remote import audit
from ars_magica_manager.remote.audit import AuditLog, audit_path
from ars_magica_manager.remote.client import ChangeNotSaved, SignInError
from ars_magica_manager.remote.devices import DeviceBook, devices_path
from ars_magica_manager.remote.host import _bucket
from ars_magica_manager.remote.passcodes import RemotePasscodes, passcodes_path

NEW = "grey owl over the mill"


@pytest_asyncio.fixture
async def hosted() -> AsyncIterator[Hosted]:
    serving = Hosted(hidden_saga())
    serving.port = await serving.host.start()
    yield serving
    await serving.host.stop()


def _anna(hosted: Hosted) -> players.Player:
    found = players.player_by_id(storage.load_saga(hosted.saga.id), hosted.anna.id)
    assert found is not None
    return found


async def test_a_player_sets_a_new_passcode_sending_only_its_digest(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    salt = bytes(range(16))
    try:
        await client.change_passcode(salt, players.passcode_digest(NEW, salt))
    finally:
        await client.close()
    anna = _anna(hosted)
    assert players.passcode_matches(anna, NEW)
    assert not players.passcode_matches(anna, PASSCODE)
    assert RemotePasscodes(passcodes_path(hosted.saga.name)).allows(anna)
    events = [e.event for e in AuditLog(audit_path(hosted.saga.name)).entries()]
    assert audit.PASSCODE_CHANGED in events
    # The new one signs in; the old one no longer does.
    async with await hosted.client() as again:
        assert await again.sign_in(NEW, hosted.vault) == "Anna"
    async with await hosted.client() as old:
        with pytest.raises(SignInError):
            await old.sign_in(PASSCODE, hosted.vault)


@pytest.mark.parametrize(
    ("salt", "digest"),
    [("zz" * 16, "00" * 64), ("00" * 15, "00" * 64), ("00" * 16, "00" * 63)],
)
async def test_a_digest_of_the_wrong_shape_is_refused(
    hosted: Hosted, salt: str, digest: str
) -> None:
    client = await hosted.signed_in()
    try:
        reply = await client.request(
            "change_passcode", {"salt": salt, "digest": digest}
        )
    finally:
        await client.close()
    assert reply.type == "refused"
    assert players.passcode_matches(_anna(hosted), PASSCODE)


async def test_a_change_is_taken_only_straight_after_a_proof(hosted: Hosted) -> None:
    """A seat signed in earlier (a borrowed computer) can't take the
    passcode over: the change must follow a fresh proof."""
    client = await hosted.signed_in()
    salt = bytes(16)
    try:
        await client.read_saga()  # any message in between
        with pytest.raises(ChangeNotSaved):
            await client.change_passcode(salt, players.passcode_digest(NEW, salt))
    finally:
        await client.close()
    assert players.passcode_matches(_anna(hosted), PASSCODE)


async def test_a_new_passcode_ends_the_sign_ins_made_with_the_old(
    hosted: Hosted,
) -> None:
    """A storyguide's reset (or the player's own change) cuts off a seat
    still signed in with the old passcode."""
    client = await hosted.signed_in()
    try:
        await client.read_saga()
        saga = storage.load_saga(hosted.saga.id)
        anna = players.player_by_id(saga, hosted.anna.id)
        assert anna is not None
        players.set_passcode(anna, NEW)
        storage.save_saga(saga)
        with pytest.raises(ConnectionError):
            await client.read_saga()
    finally:
        await client.close()


async def test_a_proof_that_isnt_hex_is_refused_not_crashed_on(hosted: Hosted) -> None:
    await (await hosted.signed_in()).close()  # the seat
    async with await hosted.client() as client:
        credential = hosted.vault.load(hosted.pin)
        assert credential
        await client.request("begin_signin", {"credential": credential})
        reply = await client.request("prove", {"proof": "é" * 64})
    assert reply.type == "refused"


async def test_the_door_never_changes_a_passcode(hosted: Hosted) -> None:
    async with await hosted.client() as client:
        salt = bytes(16)
        with pytest.raises(ChangeNotSaved):
            await client.change_passcode(salt, players.passcode_digest(NEW, salt))
    assert players.passcode_matches(_anna(hosted), PASSCODE)


async def test_a_seated_device_asks_for_a_new_passcode(hosted: Hosted) -> None:
    await (await hosted.signed_in()).close()  # the seat is made
    async with await hosted.client() as client:
        await client.ask_reset(hosted.vault)
    book = DeviceBook(devices_path(hosted.saga.name))
    [asking] = book.resets()
    assert asking.player_id == hosted.anna.id
    book.reset_done(hosted.anna.id)
    assert book.resets() == []


async def test_an_unknown_device_cannot_ask(hosted: Hosted) -> None:
    async with await hosted.client() as client:
        reply = await client.request("ask_reset", {"credential": "0" * 32})
    assert reply.type == "refused"
    assert DeviceBook(devices_path(hosted.saga.name)).resets() == []


def test_ipv6_addresses_count_by_their_network() -> None:
    """One person hands out IPv6 addresses by the billion: the limits count
    them by /64, so a fresh one doesn't win a fresh place."""
    assert _bucket("2001:db8::1") == _bucket("2001:db8::ffff") == "2001:db8::/64"
    assert _bucket("2001:db8:0:1::1") != _bucket("2001:db8::1")
    assert _bucket("203.0.113.7") == "203.0.113.7"


def test_an_older_devices_file_reads_with_no_one_asking(tmp_path: Path) -> None:
    older = {
        "idle_days": 90,
        "devices": [
            {
                "id": "r1",
                "player_id": "p1",
                "name": "laptop",
                "words": "a b c",
                "credential_hash": "0" * 64,
                "created": 1.0,
                "last_seen": 1.0,
            }
        ],
    }
    path = tmp_path / "devices.json"
    path.write_text(json.dumps(older), encoding="utf-8")
    book = DeviceBook(path, clock=lambda: 2.0)
    assert book.resets() == []
    assert [d.reset_asked for d in book.devices()] == [0.0]
