"""Device credentials, the passcode proof, lockout, expiry, revoking, rotating
and the audit log: the host's rules and the whole path over a real connection."""

from __future__ import annotations

import asyncio
import dataclasses
import json
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from test_remote_redeem import Spy

from ars_magica_manager import players
from ars_magica_manager.lockout import LOCK_STEPS
from ars_magica_manager.models import Player, Saga
from ars_magica_manager.remote import audit
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.audit import AuditLog
from ars_magica_manager.remote.client import (
    NoCredential,
    RemoteClient,
    SignInError,
    new_device_secret,
)
from ars_magica_manager.remote.control import revoke_device, rotate_host_key
from ars_magica_manager.remote.devices import DAY, DeviceBook
from ars_magica_manager.remote.host import PATH, RemoteHost
from ars_magica_manager.remote.invites import InviteBook, Request
from ars_magica_manager.remote.limits import Limits
from ars_magica_manager.remote.passcodes import RemotePasscodes
from ars_magica_manager.remote.proof import make_proof, proof_is_good
from ars_magica_manager.remote.protocol import member_registry
from ars_magica_manager.remote.redemption import door_registry
from ars_magica_manager.remote.secure import ChannelError
from ars_magica_manager.remote.serve import watch
from ars_magica_manager.remote.vault import DeviceVault, NoKeychainError

IDENTITY = ident.build(ident.ec.generate_private_key(ident.ec.SECP256R1()))
PASSCODE = "correct horse battery"


class Clock:
    def __init__(self) -> None:
        self.now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


# -- the passcode rules ---------------------------------------------------------


def test_a_passcode_needs_fourteen_characters() -> None:
    assert players.MIN_PASSCODE == 14
    assert players.passcode_problem("a" * 13)
    assert players.passcode_problem("a" * 14) is None


def _set(saga: Saga, book: RemotePasscodes, name: str, passcode: str) -> Player:
    """Add or change a player's passcode as the Players form does."""
    found = players.find(saga, name)
    if found is None:
        found = players.add(saga, {"name": name, "passcode": passcode})
    else:
        players.update(found, {"name": name, "passcode": passcode})
    book.note(found, passcode)
    return found


def test_only_a_long_passcode_may_sign_in_remotely(tmp_path: Path) -> None:
    saga = Saga(id="s", name="S")
    book = RemotePasscodes(tmp_path / "passcodes.json")
    short = _set(saga, book, "Short", "short")
    long = _set(saga, book, "Long", PASSCODE)
    assert (book.allows(short), book.allows(long)) == (False, True)
    assert players.sign_in(saga, "Short", "short") is short  # still fine at the table
    _set(saga, book, "Short", PASSCODE)
    assert book.allows(short)
    _set(saga, book, "Long", "tiny")
    assert not book.allows(long)


def test_the_note_is_kept_outside_the_saga(tmp_path: Path) -> None:
    saga = Saga(id="s", name="S")
    book = RemotePasscodes(tmp_path / "passcodes.json")
    anna = _set(saga, book, "Anna", PASSCODE)
    assert dataclasses.asdict(anna).keys() == {
        "id",
        "name",
        "role",
        "passcode_hash",
        "covenant_rights",
    }
    # Read again, as the listener (another process) does.
    assert RemotePasscodes(tmp_path / "passcodes.json").allows(anna)


def test_a_passcode_changed_elsewhere_is_not_allowed_until_set_here(
    tmp_path: Path,
) -> None:
    saga = Saga(id="s", name="S")
    book = RemotePasscodes(tmp_path / "passcodes.json")
    anna = _set(saga, book, "Anna", PASSCODE)
    players.set_passcode(anna, "short")  # a fresh salt, not noted here
    assert not book.allows(anna)
    players.set_passcode(anna, PASSCODE)  # long, but still not noted
    assert not book.allows(anna)


def test_a_deleted_player_is_forgotten(tmp_path: Path) -> None:
    saga = Saga(id="s", name="S")
    book = RemotePasscodes(tmp_path / "passcodes.json")
    anna = _set(saga, book, "Anna", PASSCODE)
    book.forget(anna.id)
    assert not RemotePasscodes(tmp_path / "passcodes.json").allows(anna)


def test_a_damaged_passcodes_file_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "passcodes.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="passcodes file"):
        RemotePasscodes(path)


# -- the proof ------------------------------------------------------------------


def test_the_proof_is_bound_to_the_host_key_and_the_nonce() -> None:
    digest = players.passcode_digest(PASSCODE, b"s" * 16)
    nonce, pin = b"n" * 32, "ab" * 32
    proof = make_proof(digest, nonce, pin)
    assert proof_is_good(proof, digest, nonce, pin)
    assert not proof_is_good(proof, digest, nonce, "cd" * 32)  # another host
    assert not proof_is_good(proof, digest, b"m" * 32, pin)  # another challenge
    other = players.passcode_digest("wrong horse battery", b"s" * 16)
    assert not proof_is_good(make_proof(other, nonce, pin), digest, nonce, pin)
    assert PASSCODE not in proof


# -- the devices ----------------------------------------------------------------


def make_request(book: InviteBook, player_id: str = "p1", secret: str = "ab" * 16):
    return book.redeem(book.issue(player_id), "laptop", secret)


@pytest.fixture
def clock() -> Clock:
    return Clock()


def test_the_host_keeps_only_a_hash_of_the_credential(
    tmp_path: Path, clock: Clock
) -> None:
    devices = DeviceBook(tmp_path / "devices.json", clock)
    request = make_request(InviteBook(tmp_path / "invites.json", clock))
    credential = devices.enrol(request)
    assert len(credential) == 32
    assert credential not in (tmp_path / "devices.json").read_text(encoding="utf-8")
    device = devices.find(credential)
    assert device is not None and device.id == request.id
    last = "1" if credential[-1] == "0" else "0"
    assert devices.find(credential[:-1] + last) is None
    assert DeviceBook(tmp_path / "devices.json", clock).find(credential) is not None


def test_a_device_idle_too_long_stops_working(tmp_path: Path, clock: Clock) -> None:
    devices = DeviceBook(tmp_path / "d.json", clock)
    credential = devices.enrol(make_request(InviteBook(tmp_path / "i.json", clock)))
    assert devices.idle_days == 90
    clock.now += 89 * DAY
    device = devices.find(credential)
    assert device is not None
    devices.signed_in(device)  # use refreshes "last seen"
    clock.now += 89 * DAY
    assert devices.find(credential) is not None
    clock.now += 2 * DAY
    assert devices.find(credential) is None
    assert devices.devices()[0].end_reason == "expired"


def test_the_idle_setting_is_per_saga_and_checked(tmp_path: Path, clock: Clock) -> None:
    devices = DeviceBook(tmp_path / "d.json", clock)
    devices.set_idle_days(30)
    assert DeviceBook(tmp_path / "d.json", clock).idle_days == 30
    for bad in (0, -1, 4000):
        with pytest.raises(ValueError):
            devices.set_idle_days(bad)


def test_failures_slow_a_device_down(tmp_path: Path, clock: Clock) -> None:
    devices = DeviceBook(tmp_path / "d.json", clock)
    credential = devices.enrol(make_request(InviteBook(tmp_path / "i.json", clock)))
    device = devices.find(credential)
    assert device is not None
    assert [devices.failed(device) for _ in range(2)] == [0, 0]  # three are free
    waits = []
    for step in LOCK_STEPS + (LOCK_STEPS[-1],):
        waits.append(devices.failed(device))
        clock.now += waits[-1] + 1
    assert waits == [int(s) for s in LOCK_STEPS + (LOCK_STEPS[-1],)]
    devices.signed_in(device)
    assert devices.lock_remaining(device) == 0 and device.failures == 0


def test_revoking_ends_a_device_once(tmp_path: Path, clock: Clock) -> None:
    devices = DeviceBook(tmp_path / "d.json", clock)
    credential = devices.enrol(make_request(InviteBook(tmp_path / "i.json", clock)))
    device = devices.find(credential)
    assert device is not None
    devices.revoke(device.id)
    assert devices.find(credential) is None and not devices.is_live(device.id)
    with pytest.raises(LookupError):
        devices.revoke(device.id)


def test_a_damaged_devices_file_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "d.json"
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="cannot be read"):
        DeviceBook(path)


# -- the audit log --------------------------------------------------------------


def test_the_audit_log_takes_events_and_ids_only(tmp_path: Path, clock: Clock) -> None:
    log = AuditLog(tmp_path / "audit.jsonl", clock)
    log.record(audit.SIGNED_IN, player_id="p1", device_id="d1")
    with pytest.raises(ValueError):
        log.record("anything I like")
    [entry] = log.entries()
    assert (entry.event, entry.player_id, entry.device_id) == (
        audit.SIGNED_IN,
        "p1",
        "d1",
    )
    assert set(json.loads((tmp_path / "audit.jsonl").read_text())) == {
        "when",
        "event",
        "record",
        "player_id",
        "device_id",
    }


def test_the_audit_log_keeps_a_year(tmp_path: Path, clock: Clock) -> None:
    path = tmp_path / "audit.jsonl"
    AuditLog(path, clock).record(audit.INVITE_ISSUED, player_id="p1")
    clock.now += audit.KEEP - 10
    log = AuditLog(path, clock)
    log.record(audit.SIGNED_IN, player_id="p1")
    assert len(log.entries()) == 2
    clock.now += 20
    assert [e.event for e in AuditLog(path, clock).entries()] == [audit.SIGNED_IN]


def test_a_damaged_log_line_is_skipped(tmp_path: Path, clock: Clock) -> None:
    path = tmp_path / "audit.jsonl"
    log = AuditLog(path, clock)
    log.record(audit.SIGNED_IN)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("not json\n")
    log.record(audit.SIGNED_IN)
    assert len(log.entries()) == 2


# -- the whole path over a real connection -----------------------------------------


class Seat:
    """A hosted saga with one Player, an approved device and a vault."""

    def __init__(self, tmp_path: Path, clock: Clock) -> None:
        self.tmp_path, self.clock = tmp_path, clock
        self.saga = Saga(id="s", name="S")
        self.passcodes = RemotePasscodes(tmp_path / "passcodes.json")
        self.anna = _set(self.saga, self.passcodes, "Anna", PASSCODE)
        self.log = AuditLog(tmp_path / "audit.jsonl", clock)
        self.book = InviteBook(tmp_path / "invites.json", clock, self.log)
        self.devices = DeviceBook(tmp_path / "devices.json", clock, self.log)
        self.vault = DeviceVault(ident.MemoryStore())
        self.limits = dataclasses.replace(Limits(), max_strikes=50)
        self.host = RemoteHost(
            IDENTITY,
            door_registry(
                self.limits.max_message,
                self.book,
                self.devices,
                lambda pid: players.player_by_id(self.saga, pid),
                lambda: IDENTITY.pin,
                self.passcodes,
            ),
            self.limits,
            members=member_registry(self.limits.max_message),
        )
        self.port = 0

    async def client(self, pin: str | None = None) -> RemoteClient:
        url = f"ws://127.0.0.1:{self.port}{PATH}"
        return await RemoteClient.connect(url, pin or IDENTITY.pin)

    async def enrol(self) -> str:
        """Redeem an Invite, have the Storyguide approve, collect the
        credential; returns the device secret."""
        secret = new_device_secret()
        async with await self.client() as client:
            await client.redeem(
                self.book.issue(self.anna.id), "laptop", secret, self.vault
            )
            self.book.approve(self.book.pending()[0].id)
            await client.request_status(secret, self.vault)
        return secret


@pytest_asyncio.fixture
async def seat(tmp_path: Path, clock: Clock) -> AsyncIterator[Seat]:
    seat = Seat(tmp_path, clock)
    seat.port = await seat.host.start()
    yield seat
    await seat.host.stop()


async def test_a_player_signs_in_with_the_credential_and_the_passcode(
    seat: Seat,
) -> None:
    await seat.enrol()
    async with await seat.client() as client:
        assert await client.sign_in(PASSCODE, seat.vault) == "Anna"
        assert (await client.request("ping")).type == "pong"
    events = [e.event for e in seat.log.entries()]
    assert events == [
        audit.INVITE_ISSUED,
        audit.INVITE_REDEEMED,
        audit.REQUEST_APPROVED,
        audit.DEVICE_ENROLLED,
        audit.SIGNED_IN,
    ]


async def test_nothing_but_the_door_answers_before_sign_in(seat: Seat) -> None:
    await seat.enrol()
    async with await seat.client() as client:
        assert (await client.request("ping")).type == "refused"


async def test_a_device_without_a_credential_cannot_sign_in(seat: Seat) -> None:
    async with await seat.client() as client:
        with pytest.raises(NoCredential):
            await client.sign_in(PASSCODE, seat.vault)


async def test_a_wrong_passcode_is_denied_and_then_slowed(seat: Seat) -> None:
    await seat.enrol()
    async with await seat.client() as client:
        for _ in range(2):
            with pytest.raises(SignInError) as denied:
                await client.sign_in("not the passcode!", seat.vault)
            assert (denied.value.kind, denied.value.seconds) == ("denied", 0)
        with pytest.raises(SignInError) as third:
            await client.sign_in("not the passcode!", seat.vault)
        assert (third.value.kind, third.value.seconds) == ("denied", 30)
        # Locked: even the right passcode must wait.
        with pytest.raises(SignInError) as locked:
            await client.sign_in(PASSCODE, seat.vault)
        assert locked.value.kind == "locked" and locked.value.seconds > 0
        seat.clock.now += 31
        assert await client.sign_in(PASSCODE, seat.vault) == "Anna"
    assert audit.DEVICE_LOCKED in [e.event for e in seat.log.entries()]


async def test_a_challenge_is_answered_once(seat: Seat) -> None:
    await seat.enrol()
    async with await seat.client() as client:
        credential = seat.vault.load(IDENTITY.pin)
        challenge = await client.request("begin_signin", {"credential": credential})
        assert challenge.type == "challenge"
        assert (await client.request("prove", {"proof": "0" * 64})).type == "denied"
        assert (await client.request("prove", {"proof": "0" * 64})).type == "refused"


async def test_a_short_passcode_is_told_so_after_the_credential_proves_the_device(
    seat: Seat,
) -> None:
    await seat.enrol()
    seat.passcodes.note(seat.anna, "too short")
    async with await seat.client() as client:
        with pytest.raises(SignInError) as error:
            await client.sign_in(PASSCODE, seat.vault)
        assert error.value.kind == "short_passcode"


async def test_an_unknown_or_ended_credential_gets_the_one_refusal(seat: Seat) -> None:
    await seat.enrol()
    credential = seat.vault.load(IDENTITY.pin)
    async with await seat.client() as client:
        stranger = await client.request("begin_signin", {"credential": "0" * 32})
        device = seat.devices.find(credential or "")
        assert device is not None
        seat.devices.revoke(device.id)
        revoked = await client.request("begin_signin", {"credential": credential})
    assert stranger == revoked and stranger.type == "refused"


async def test_revoking_cuts_a_live_connection_at_once(seat: Seat) -> None:
    await seat.enrol()
    async with await seat.client() as client:
        await client.sign_in(PASSCODE, seat.vault)
        assert (await client.request("ping")).type == "pong"
        [device] = seat.devices.devices()
        await revoke_device(seat.devices, seat.host, device.id)
        with pytest.raises(ChannelError):
            await client.request("ping")
    async with await seat.client() as again:
        with pytest.raises(SignInError):
            await again.sign_in(PASSCODE, seat.vault)
    assert audit.DEVICE_REVOKED in [e.event for e in seat.log.entries()]


async def test_a_signed_in_connection_ends_when_the_device_does_even_if_idle_open(
    seat: Seat,
) -> None:
    await seat.enrol()
    async with await seat.client() as client:
        await client.sign_in(PASSCODE, seat.vault)
        [device] = seat.devices.devices()
        seat.devices.revoke(device.id)  # no disconnect call: the next message fails
        with pytest.raises(ChannelError):
            await client.request("ping")


async def test_rotating_the_host_key_ends_everything(seat: Seat) -> None:
    await seat.enrol()
    pending_code = seat.book.issue(seat.anna.id)
    store = ident.MemoryStore()
    old = ident.load_or_create(store, "host")
    async with await seat.client() as client:
        await client.sign_in(PASSCODE, seat.vault)
        new = await rotate_host_key(
            store, "host", seat.book, seat.devices, seat.log, seat.host
        )
        with pytest.raises(ChannelError):
            await client.request("ping")
    assert new.pin != old.pin
    assert seat.devices.devices()[0].end_reason == "revoked"
    assert seat.book.pending() == []
    async with await seat.client() as fresh:
        reply = await fresh.redeem(pending_code, "x", new_device_secret(), seat.vault)
        assert reply.type == "refused"
    assert audit.HOST_KEY_ROTATED in [e.event for e in seat.log.entries()]


async def test_with_no_keychain_the_invite_is_not_spent(seat: Seat) -> None:
    class NoKeychain:
        def get(self, name: str) -> str | None:
            raise NoKeychainError("no keychain")

        def set(self, name: str, value: str) -> None:
            raise NoKeychainError("no keychain")

        def delete(self, name: str) -> None:
            raise NoKeychainError("no keychain")

    code = seat.book.issue(seat.anna.id)
    async with await seat.client() as client:
        with pytest.raises(NoKeychainError):
            await client.redeem(
                code, "x", new_device_secret(), DeviceVault(NoKeychain())
            )
        # The same Invite still works once there is somewhere safe to keep it.
        reply = await client.redeem(code, "x", new_device_secret(), seat.vault)
        assert reply.type == "pending"


async def test_no_secret_is_written_to_the_data_folder(seat: Seat) -> None:
    secret = await seat.enrol()
    credential = seat.vault.load(IDENTITY.pin)
    assert credential
    async with await seat.client() as client:
        await client.sign_in(PASSCODE, seat.vault)
        with pytest.raises(SignInError):
            await client.sign_in("not the passcode!", seat.vault)
    written = "".join(
        p.read_text(encoding="utf-8") for p in seat.tmp_path.iterdir() if p.is_file()
    )
    for secret_text in (credential, secret, PASSCODE, "not the passcode!"):
        assert secret_text not in written


async def test_the_passcode_and_credential_never_leave_the_private_session(
    seat: Seat,
) -> None:
    await seat.enrol()
    credential = seat.vault.load(IDENTITY.pin)
    spy = Spy(seat.port)
    port = await spy.start()
    try:
        async with await RemoteClient.connect(
            f"ws://127.0.0.1:{port}{PATH}", IDENTITY.pin
        ) as client:
            await client.sign_in(PASSCODE, seat.vault)
    finally:
        await spy.stop()
    sent = bytes(spy.seen)
    assert credential and credential.encode() not in sent
    assert PASSCODE.encode() not in sent


async def test_a_seat_revoked_from_the_window_is_cut_off_by_the_watch(
    seat: Seat,
) -> None:
    """The window revokes through its own copy of the devices file; the
    listener's watch sees it and closes the connection without a message."""
    await seat.enrol()
    watching = asyncio.create_task(watch(seat.host, seat.devices, every=0.02))
    try:
        async with await seat.client() as client:
            await client.sign_in(PASSCODE, seat.vault)
            device = seat.devices.devices()[0]
            window = DeviceBook(seat.tmp_path / "devices.json", seat.clock)
            window.revoke(device.id)
            async with asyncio.timeout(3):
                while seat.host.connected():
                    await asyncio.sleep(0.02)
    finally:
        watching.cancel()


def test_two_copies_of_a_book_see_each_others_changes(
    tmp_path: Path, clock: Clock
) -> None:
    """The window and the listener each hold a DeviceBook on one file: a
    revoke in one is never written over by the other's older copy."""
    request = _approved_request(tmp_path, clock)
    listener = DeviceBook(tmp_path / "devices.json", clock)
    window = DeviceBook(tmp_path / "devices.json", clock)
    credential = listener.enrol(request)
    device = listener.find(credential)
    assert device is not None and window.is_live(device.id)
    window.revoke(device.id)
    listener.seen(device)  # the listener's copy still had it live
    assert not listener.is_live(device.id)
    assert listener.find(credential) is None


def test_an_invite_issued_in_the_window_is_redeemed_by_the_listener(
    tmp_path: Path, clock: Clock
) -> None:
    window = InviteBook(tmp_path / "invites.json", clock)
    listener = InviteBook(tmp_path / "invites.json", clock)
    code = window.issue("p1")
    secret = new_device_secret()
    request = listener.redeem(code, "laptop", secret)
    assert [r.id for r in window.pending()] == [request.id]
    window.approve(request.id)
    assert listener.status(secret).state == "approved"


def _approved_request(tmp_path: Path, clock: Clock) -> Request:
    book = InviteBook(tmp_path / "invites.json", clock)
    request = book.redeem(book.issue("p1"), "laptop", new_device_secret())
    return book.approve(request.id)


async def test_a_host_with_another_key_gets_nothing_usable(seat: Seat) -> None:
    """A fake host is refused before any message (the pin), and a proof made
    for one pin is not the proof for another."""
    await seat.enrol()
    other = ident.build(ident.ec.generate_private_key(ident.ec.SECP256R1()))
    with pytest.raises(ChannelError):
        await seat.client(pin=other.pin)
