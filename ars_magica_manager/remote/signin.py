"""Signing in from a Remote seat: a Device credential, then the passcode proof.

Two messages, in order, on the public door:

1. `begin_signin` carries the Device credential. A credential the host does
   not know (unknown, revoked or expired) gets the one uniform refusal. A
   good one gets a challenge: the salt stored for the seat's player and a
   fresh nonce. (A device that is locked out, or whose passcode is too short
   for a Remote seat, is told so: the credential has shown it is a device the
   Storyguide approved.)
2. `prove` carries the answer. A right one opens the member phase for this
   connection; a wrong one counts against the device (see devices.py).

The device decides the seat: a credential belongs to one player, so there is
no name to type and none to guess.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable

from .. import players
from ..models import Player
from .devices import Device, DeviceBook
from .passcodes import RemotePasscodes
from .proof import NONCE_BYTES, proof_is_good
from .protocol import Body, Field, MessageSpec, Refused, Reply, Session

CREDENTIAL_MAX = 64
PROOF_MAX = 64


def signin_specs(
    devices: DeviceBook,
    player_of: Callable[[str], Player | None],
    pin: Callable[[], str],
    passcodes: RemotePasscodes,
) -> list[MessageSpec]:
    """The messages, tied to `devices`. `player_of` finds a player by id in
    the saga as it stands now; `pin` is the host key's current pin;
    `passcodes` says whose passcode is long enough for a Remote seat."""

    def begin(session: Session, body: Body) -> Reply:
        device = devices.find(str(body["credential"]))
        player = player_of(device.player_id) if device else None
        if device is None or player is None:
            raise Refused
        wait = devices.lock_remaining(device)
        if wait:
            return Reply("locked", {"seconds": wait})
        if not passcodes.allows(player):
            return Reply("short_passcode")
        try:
            salt, _ = players.stored_parts(player.passcode_hash)
        except ValueError:
            raise Refused from None
        session.challenge = secrets.token_bytes(NONCE_BYTES)
        session.challenged = device.id
        return Reply(
            "challenge", {"salt": salt.hex(), "nonce": session.challenge.hex()}
        )

    def prove(session: Session, body: Body) -> Reply:
        nonce, session.challenge = session.challenge, b""  # one answer per challenge
        device = devices.get(session.challenged)
        player = player_of(device.player_id) if device else None
        if not nonce or device is None or player is None or device.ended:
            raise Refused
        wait = devices.lock_remaining(device)
        if wait:
            return Reply("locked", {"seconds": wait})
        try:
            _, digest = players.stored_parts(player.passcode_hash)
        except ValueError:
            raise Refused from None
        if not proof_is_good(str(body["proof"]), digest, nonce, pin()):
            return Reply("denied", {"seconds": devices.failed(device)})
        devices.signed_in(device)
        session.player_id = player.id
        session.device_id = device.id
        session.still_allowed = lambda: _still_good(devices, device, player_of)
        return Reply("signed_in", {"player": player.name})

    def ask_reset(session: Session, body: Body) -> Reply:
        """A forgotten passcode: asked by a device the host knows, so only a
        seat the storyguide approved can ask; anything else gets the one
        refusal. The storyguide confirms by voice and sets a new one."""
        device = devices.find(str(body["credential"]))
        if device is None or player_of(device.player_id) is None:
            raise Refused
        devices.ask_reset(device)
        return Reply("reset_asked")

    return [
        MessageSpec(
            "ask_reset",
            {"credential": Field(str, max_length=CREDENTIAL_MAX)},
            ask_reset,
        ),
        MessageSpec(
            "begin_signin",
            {"credential": Field(str, max_length=CREDENTIAL_MAX)},
            begin,
        ),
        MessageSpec("prove", {"proof": Field(str, max_length=PROOF_MAX)}, prove),
    ]


def _still_good(
    devices: DeviceBook, device: Device, player_of: Callable[[str], Player | None]
) -> bool:
    """Whether a signed-in connection may carry on: the device is not ended
    and its player is still in the saga."""
    return devices.is_live(device.id) and player_of(device.player_id) is not None
