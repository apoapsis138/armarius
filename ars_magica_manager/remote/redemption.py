"""The two messages of the public door that matter: redeeming an Invite and
asking how the request went.

Before anyone has signed in, the host answers `hello`, `redeem` and
`request_status`, and nothing else. Whatever is wrong with a code (unknown,
used, expired) or a secret, the sender gets the one uniform refusal; the
reason goes to the host's own log only.
"""

from __future__ import annotations

from collections.abc import Callable

from .invites import InviteBook, InviteError
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

CODE_MAX = 64
DEVICE_MAX = 40
SECRET_MAX = 64


def redemption_specs(
    book: InviteBook, name_of: Callable[[str], str]
) -> list[MessageSpec]:
    """The messages, tied to `book`. `name_of` turns a player id into the
    name the player's app shows (and the Storyguide sees)."""

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
        try:
            request = book.status(str(body["secret"]))
        except InviteError:
            raise Refused from None
        return Reply("state", {"state": request.state})

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
    max_bytes: int, book: InviteBook, name_of: Callable[[str], str]
) -> Registry:
    """What the public door answers: hello, redeem and request_status."""
    registry = public_registry(max_bytes)
    for spec in redemption_specs(book, name_of):
        registry.register(spec)
    return registry
