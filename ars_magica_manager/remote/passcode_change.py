"""A player changes their own passcode from their Remote seat (ADR 0013).

The player's app signs in afresh with the old passcode (signin.py, so a
wrong one counts toward the lock-out as any sign-in does), then sends
`change_passcode` with the new passcode's scrypt digest under a salt it
chose. The passcode itself never leaves the player's computer. The host
stores the digest and salt as the player's passcode, saves the saga in the
player's name, and allows it for Remote seats: the 14-character rule was
checked by the player's app, since the host can't see the passcode.

Pattern: one more Command in the member registry's table (protocol.py).
"""

from __future__ import annotations

from .. import players, storage
from . import audit
from .passcodes import RemotePasscodes
from .protocol import Body, Field, MessageSpec, Refused, Reply, Session

#: A salt is 16 bytes and a digest 64 (scrypt's default), both as hex.
SALT_HEX = 32
DIGEST_HEX = 128


def _hex(text: str, length: int) -> str:
    try:
        bytes.fromhex(text)
    except ValueError:
        raise Refused from None
    if len(text) != length:
        raise Refused
    return text.lower()


def passcode_specs(
    saga_id: str, passcodes: RemotePasscodes, log: audit.AuditLog | None = None
) -> list[MessageSpec]:
    """`change_passcode`, for a signed-in seat of the saga `saga_id`."""

    def change(session: Session, body: Body) -> Reply:
        salt = _hex(str(body["salt"]), SALT_HEX)
        digest = _hex(str(body["digest"]), DIGEST_HEX)
        try:
            saga = storage.load_saga(saga_id)
        except (OSError, ValueError) as gone:
            raise Refused from gone
        player = players.player_by_id(saga, session.player_id)
        if player is None:
            raise Refused
        player.passcode_hash = f"scrypt${salt}${digest}"
        storage.save_saga(saga, storage.Saver(player.name))
        passcodes.allow(player)
        if log is not None:
            log.record(
                audit.PASSCODE_CHANGED,
                player_id=session.player_id,
                device_id=session.device_id,
            )
        return Reply("passcode_changed")

    return [
        MessageSpec(
            "change_passcode",
            {
                "salt": Field(str, max_length=SALT_HEX),
                "digest": Field(str, max_length=DIGEST_HEX),
            },
            change,
        )
    ]
