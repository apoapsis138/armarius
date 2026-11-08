"""The audit log: what happened to Remote seats, and when.

One line per event in a file in the host's data folder, outside the saga.
An entry holds a time, an event name from a fixed list and up to two ids
(a player's and a device's). There is nowhere to put a passcode, a
credential, an Invite code or a message: `record` takes no free text, so
a secret cannot be logged by mistake. Entries older than a year are dropped.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .folder import remote_file

KEEP = 365 * 24 * 3600.0

INVITE_ISSUED = "invite_issued"
INVITE_REDEEMED = "invite_redeemed"
REQUEST_APPROVED = "request_approved"
REQUEST_REJECTED = "request_rejected"
DEVICE_ENROLLED = "device_enrolled"
SIGNED_IN = "signed_in"
SIGN_IN_FAILED = "sign_in_failed"
DEVICE_LOCKED = "device_locked"
DEVICE_REVOKED = "device_revoked"
DEVICE_EXPIRED = "device_expired"
HOST_KEY_ROTATED = "host_key_rotated"
EVENTS = frozenset(
    {
        INVITE_ISSUED,
        INVITE_REDEEMED,
        REQUEST_APPROVED,
        REQUEST_REJECTED,
        DEVICE_ENROLLED,
        SIGNED_IN,
        SIGN_IN_FAILED,
        DEVICE_LOCKED,
        DEVICE_REVOKED,
        DEVICE_EXPIRED,
        HOST_KEY_ROTATED,
    }
)


@dataclass(frozen=True)
class AuditEntry:
    when: float
    event: str
    player_id: str = ""
    device_id: str = ""


class AuditLog:
    """An append-only log of Remote seat events."""

    def __init__(self, path: Path, clock: Callable[[], float] = time.time) -> None:
        self._path = path
        self._clock = clock
        self._prune()

    def record(self, event: str, *, player_id: str = "", device_id: str = "") -> None:
        if event not in EVENTS:
            raise ValueError(f"Unknown audit event {event!r}.")
        entry = AuditEntry(self._clock(), event, player_id, device_id)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry.__dict__, separators=(",", ":")) + "\n")

    def entries(self) -> list[AuditEntry]:
        """Every entry kept, oldest first. A line that cannot be read is
        skipped: a damaged log must not stop the host."""
        if not self._path.exists():
            return []
        found: list[AuditEntry] = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            try:
                data = json.loads(line)
                found.append(
                    AuditEntry(
                        float(data["when"]),
                        str(data["event"]),
                        str(data.get("player_id", "")),
                        str(data.get("device_id", "")),
                    )
                )
            except ValueError, KeyError, TypeError:
                continue
        return found

    def _prune(self) -> None:
        kept = self.entries()
        fresh = [e for e in kept if self._clock() - e.when < KEEP]
        if len(fresh) != len(kept):
            lines = (json.dumps(e.__dict__, separators=(",", ":")) for e in fresh)
            self._path.write_text(
                "".join(line + "\n" for line in lines), encoding="utf-8"
            )


def audit_path(saga_name: str) -> Path:
    """Where a saga's log lives: the host's data folder, not the saga file."""
    return remote_file(saga_name, "audit.jsonl")
