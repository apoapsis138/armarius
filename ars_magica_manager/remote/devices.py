"""Devices: the credentials the host has handed out, and what each may do.

When the Storyguide approves a request, the player's app is given a Device
credential once: 128 random bits it keeps in its keychain. The host keeps
only a SHA-256 of it, so a copy of the host's files does not let anyone in
(a bearer token with a server-side hash, as a session or API token is kept).
The credential only opens the way to sign-in; the player still proves their
passcode.

A device ends when the Storyguide revokes it, when it has been idle for
longer than the saga allows (90 days unless changed), or when the host key
is rotated. Failed passcode proofs slow a device down: three are free, then
the waits grow.

The file lives in the host's data folder, outside the saga.
"""

from __future__ import annotations

import hashlib
import json
import math
import secrets
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from .. import shapes
from ..files import write_atomic
from . import audit
from .folder import SharedFile, remote_file
from .invites import Request

DAY = 24 * 3600.0
DEFAULT_IDLE_DAYS = 90
MAX_IDLE_DAYS = 3650
#: Failed proofs allowed before the first wait.
FREE_FAILURES = 3
#: Seconds to wait after the third failure, then each further one (the last
#: repeats).
LOCK_STEPS = (30.0, 120.0, 600.0, 3600.0)
REVOKED, EXPIRED = "revoked", "expired"


@dataclass
class Device:
    """One player's device that may ask to sign in."""

    id: str  # the request's id: safe to show and to name in a list
    player_id: str
    name: str
    words: str
    credential_hash: str
    created: float
    last_seen: float
    failures: int = 0
    locked_until: float = 0.0
    ended: float = 0.0
    end_reason: str = ""


@dataclass
class DevicesFile:
    """The devices file's shape, checked as it is read (shapes.build)."""

    idle_days: int
    devices: list[Device]


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class DeviceBook(SharedFile):
    """The devices of one hosted saga, kept in one file that the
    Storyguide's window and the listener both change (folder.SharedFile).
    A method given a Device works on the one of that id as the file holds
    it now."""

    def __init__(
        self,
        path: Path,
        clock: Callable[[], float] = time.time,
        log: audit.AuditLog | None = None,
    ) -> None:
        self._path = path
        self._clock = clock
        self._log = log
        self._idle_days = DEFAULT_IDLE_DAYS
        self._devices: dict[str, Device] = {}
        self._load()

    # -- the file ---------------------------------------------------------

    def _load(self) -> None:
        self._idle_days, self._devices = DEFAULT_IDLE_DAYS, {}
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            book = shapes.build(DevicesFile, data)
            self._idle_days = _valid_days(book.idle_days)
        except (OSError, ValueError) as exc:
            raise ValueError(
                f"The devices file {self._path.name} cannot be read ({exc})."
            ) from exc
        self._devices = {d.id: d for d in book.devices}

    def _save(self) -> None:
        data = {
            "idle_days": self._idle_days,
            "devices": [asdict(d) for d in self._devices.values()],
        }
        write_atomic(self._path, json.dumps(data, indent=1))

    def _note(self, event: str, device: Device) -> None:
        if self._log is not None:
            self._log.record(event, player_id=device.player_id, device_id=device.id)

    # -- the setting ------------------------------------------------------

    @property
    def idle_days(self) -> int:
        """Days a device may go unused before it stops working."""
        with self._fresh():
            return self._idle_days

    def set_idle_days(self, days: int) -> None:
        with self._fresh():
            self._idle_days = _valid_days(days)
            self._save()

    def _now(self, device: Device) -> Device:
        """`device` as the file holds it now, or LookupError if it is gone."""
        found = self._devices.get(device.id)
        if found is None:
            raise LookupError("No such device.")
        return found

    # -- enrolling --------------------------------------------------------

    def enrol(self, request: Request) -> str:
        """Make the credential for an approved request: returned once, never
        stored."""
        credential = secrets.token_hex(16)
        now = self._clock()
        device = Device(
            id=request.id,
            player_id=request.player_id,
            name=request.device,
            words=request.words,
            credential_hash=_hash(credential),
            created=now,
            last_seen=now,
        )
        with self._fresh():
            self._devices[device.id] = device
            self._save()
        self._note(audit.DEVICE_ENROLLED, device)
        return credential

    # -- using a credential -------------------------------------------------

    def find(self, credential: str) -> Device | None:
        """The live device `credential` belongs to, or None. A device left
        idle too long ends here, once."""
        wanted = _hash(credential)
        with self._fresh():
            for device in self._devices.values():
                if device.credential_hash != wanted or device.ended:
                    continue
                if self._expired(device):
                    self._end(device, EXPIRED)
                    return None
                return device
        return None

    def _expired(self, device: Device) -> bool:
        return self._clock() - device.last_seen > self._idle_days * DAY

    def get(self, device_id: str) -> Device | None:
        with self._fresh():
            return self._devices.get(device_id)

    def is_live(self, device_id: str) -> bool:
        with self._fresh():
            device = self._devices.get(device_id)
            return device is not None and not device.ended

    def lock_remaining(self, device: Device) -> int:
        """Whole seconds before `device` may try again; 0 if it may."""
        with self._fresh():
            device = self._now(device)
            return max(0, math.ceil(device.locked_until - self._clock()))

    def signed_in(self, device: Device) -> None:
        with self._fresh():
            device = self._now(device)
            device.last_seen = self._clock()
            device.failures = 0
            device.locked_until = 0.0
            self._save()
        self._note(audit.SIGNED_IN, device)

    def failed(self, device: Device) -> int:
        """Count a failed proof; the seconds `device` must now wait."""
        with self._fresh():
            device = self._now(device)
            device.failures += 1
            self._note(audit.SIGN_IN_FAILED, device)
            if device.failures >= FREE_FAILURES:
                step = min(device.failures - FREE_FAILURES, len(LOCK_STEPS) - 1)
                device.locked_until = self._clock() + LOCK_STEPS[step]
                self._note(audit.DEVICE_LOCKED, device)
            self._save()
            return self.lock_remaining(device)

    def seen(self, device: Device) -> None:
        """Note that `device` is still in use (a message arrived)."""
        with self._fresh():
            self._now(device).last_seen = self._clock()
            self._save()

    # -- ending ---------------------------------------------------------------

    def _end(self, device: Device, reason: str) -> None:
        device.ended = self._clock()
        device.end_reason = reason
        self._save()
        self._note(
            audit.DEVICE_REVOKED if reason == REVOKED else audit.DEVICE_EXPIRED,
            device,
        )

    def revoke(self, device_id: str) -> Device:
        """End a device at once, or LookupError if it is not a live one."""
        with self._fresh():
            device = self._devices.get(device_id)
            if device is None or device.ended:
                raise LookupError("No such live device.")
            self._end(device, REVOKED)
            return device

    def revoke_all(self) -> list[Device]:
        """End every live device (the host key was rotated)."""
        with self._fresh():
            live = [d for d in self._devices.values() if not d.ended]
            for device in live:
                self._end(device, REVOKED)
            return live

    def devices(self) -> list[Device]:
        """Every device, live first, most recently used first. One left idle
        too long is shown as expired, and ended here, once."""
        with self._fresh():
            for device in list(self._devices.values()):
                if not device.ended and self._expired(device):
                    self._end(device, EXPIRED)
            return sorted(
                self._devices.values(), key=lambda d: (bool(d.ended), -d.last_seen)
            )

    def expires_at(self, device: Device) -> float:
        """When `device` stops working if it goes on unused (clock time)."""
        with self._fresh():
            return device.last_seen + self._idle_days * DAY


def _valid_days(days: int) -> int:
    if not 1 <= days <= MAX_IDLE_DAYS:
        raise ValueError(f"Idle days must be from 1 to {MAX_IDLE_DAYS}.")
    return days


def devices_path(saga_name: str) -> Path:
    """Where a saga's devices live: the host's data folder, not the saga file."""
    return remote_file(saga_name, "devices.json")
