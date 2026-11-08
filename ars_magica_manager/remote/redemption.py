"""The two messages of the public door that matter: redeeming an Invite and
asking how the request went.

Before anyone has signed in, the host answers `hello`, `redeem` and
`request_status`, and nothing else. Whatever is wrong with a code (unknown,
used, expired) or a secret, the sender gets the one uniform refusal; the
reason goes to the host's own log only.
"""

from __future__ import annotations

from collections.abc import Callable

from ..models import Player
from .devices import DeviceBook
from .invites import InviteBook, InviteError
from .passcodes import RemotePasscodes
from .protocol import (
    Body,
    Field,
    MessageSpec,
    Refused,
    Registry,
    Reply,
    Session,
    public_registry,
)
from .signin import signin_specs

CODE_MAX = 64
DEVICE_MAX = 40
SECRET_MAX = 64


def redemption_specs(
    book: InviteBook, devices: DeviceBook, name_of: Callable[[str], str]
) -> list[MessageSpec]:
    """The messages, tied to `book` and `devices`. `name_of` turns a player
    id into the name the player's app shows (and the Storyguide sees)."""

    def redeem(session: Session, body: Body) -> Reply:
        device = str(body["device"]).strip()
        if not device or not device.isprintable():
            raise Refused
        try:
            request = book.redeem(str(body["code"]), device, str(body["secret"]))
        except InviteError:
            raise Refused from None
        return Reply("pending", {"player": name_of(request.player_id)})

    def request_status(session: Session, body: Body) -> Reply:
        secret = str(body["secret"])
        try:
            request = book.status(secret)
            first_time = book.collect(secret)
        except InviteError:
            raise Refused from None
        reply: Body = {"state": request.state}
        if first_time is not None:
            # Handed over once, here; the host keeps only a hash of it.
            reply["credential"] = devices.enrol(first_time)
        return Reply("state", reply)

    return [
        MessageSpec(
            name="redeem",
            fields={
                "code": Field(str, max_length=CODE_MAX),
                "device": Field(str, max_length=DEVICE_MAX),
                "secret": Field(str, max_length=SECRET_MAX),
            },
            handler=redeem,
        ),
        MessageSpec(
            name="request_status",
            fields={"secret": Field(str, max_length=SECRET_MAX)},
            handler=request_status,
        ),
    ]


def door_registry(
    max_bytes: int,
    book: InviteBook,
    devices: DeviceBook,
    player_of: Callable[[str], Player | None],
    pin: Callable[[], str],
    passcodes: RemotePasscodes,
) -> Registry:
    """What the public door answers: hello, redeem, request_status and the
    two steps of signing in. `passcodes` says whose passcode is long enough
    for a Remote seat."""

    def name_of(player_id: str) -> str:
        player = player_of(player_id)
        return player.name if player else ""

    registry = public_registry(max_bytes)
    for spec in [
        *redemption_specs(book, devices, name_of),
        *signin_specs(devices, player_of, pin, passcodes),
    ]:
        registry.register(spec)
    return registry
