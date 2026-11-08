"""The messages a host will answer, and the checks every one must pass.

A `Registry` maps a message type's name to its `MessageSpec`: the shape
of its body and the function that handles it (the Strategy pattern as a
dictionary, like the activity registry). A message whose type is not in
the registry is refused, whatever else it says. There is no way to ask the
host to run anything: a handler is chosen by name from this table, never
built from the message.

A message is JSON: {"type": "...", "body": {...}}. Bodies hold only flat
text, whole numbers and true/false values, each with a limit, so nothing
nested or oversized reaches a handler. JSON is parsed by the standard
library, which builds plain data and runs nothing.

Whatever is wrong with a message (unknown type, bad shape, too long), the
answer is the same single refusal, so a sender learns nothing about which
check failed or what exists.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

#: Bumped when a message changes in a way an older app cannot read.
PROTOCOL_VERSION = 1

#: Replies and requests have this shape: type name, then a flat body.
Body = dict[str, str | int | bool]
Handler = Callable[["Session", Body], "Reply"]

REFUSED_TYPE = "refused"


class Refused(Exception):
    """A message failed a check. Carries no detail for the sender."""


@dataclass(frozen=True)
class Reply:
    """What a handler sends back."""

    type: str
    body: Body = field(default_factory=dict)


@dataclass
class Session:
    """What a handler knows about the connection it is answering."""

    #: An opaque label for log lines (never an address or a name).
    label: str = ""


@dataclass(frozen=True)
class Field:
    """One entry of a message body: its kind and its limit."""

    kind: type  # str, int or bool
    max_length: int = 256  # text: characters
    low: int = 0  # whole numbers: smallest allowed
    high: int = 2**31 - 1  # whole numbers: largest allowed
    required: bool = True

    def check(self, value: object) -> str | int | bool:
        # bool is a kind of int in Python; accept it only where asked for.
        if self.kind is bool and isinstance(value, bool):
            return value
        if (
            self.kind is int
            and isinstance(value, int)
            and not isinstance(value, bool)
            and self.low <= value <= self.high
        ):
            return value
        if (
            self.kind is str
            and isinstance(value, str)
            and len(value) <= self.max_length
        ):
            return value
        raise Refused


@dataclass(frozen=True)
class MessageSpec:
    """A message type the host answers."""

    name: str
    fields: Mapping[str, Field]
    handler: Handler


class Registry:
    """The message types one phase of a conversation allows."""

    def __init__(self, max_bytes: int) -> None:
        self._specs: dict[str, MessageSpec] = {}
        self._max_bytes = max_bytes

    def register(self, spec: MessageSpec) -> None:
        if spec.name in self._specs:
            raise ValueError(f"Message type {spec.name!r} is already registered.")
        self._specs[spec.name] = spec

    def names(self) -> list[str]:
        return sorted(self._specs)

    def parse(self, raw: bytes) -> tuple[MessageSpec, Body]:
        """The spec and checked body of `raw`, or Refused."""
        if len(raw) > self._max_bytes:
            raise Refused
        try:
            message = json.loads(raw.decode("utf-8"))
        except UnicodeDecodeError, ValueError, RecursionError:
            raise Refused from None
        if not isinstance(message, dict) or set(message) != {"type", "body"}:
            raise Refused
        name, body = message["type"], message["body"]
        if not isinstance(name, str) or not isinstance(body, dict):
            raise Refused
        spec = self._specs.get(name)
        if spec is None:
            raise Refused
        return spec, _check_body(spec, body)

    def handle(self, session: Session, raw: bytes) -> tuple[Reply, bool]:
        """The reply to `raw`, and whether the message was acceptable.

        A refused message gets the one uniform refusal. A handler that
        raises Refused is refused the same way.
        """
        try:
            spec, body = self.parse(raw)
            return spec.handler(session, body), True
        except Refused:
            return Reply(REFUSED_TYPE), False


def _check_body(spec: MessageSpec, body: dict[object, object]) -> Body:
    allowed = spec.fields
    if any(not isinstance(key, str) or key not in allowed for key in body):
        raise Refused
    checked: Body = {}
    for name, rule in allowed.items():
        if name not in body:
            if rule.required:
                raise Refused
            continue
        checked[name] = rule.check(body[name])
    return checked


def encode(reply: Reply) -> bytes:
    return json.dumps(
        {"type": reply.type, "body": reply.body}, separators=(",", ":")
    ).encode()


def encode_request(name: str, body: Body) -> bytes:
    return json.dumps({"type": name, "body": body}, separators=(",", ":")).encode()


def decode_reply(raw: bytes) -> Reply:
    """A host's reply, checked once as it arrives (the host may be hostile):
    a type name and a flat body of text, whole numbers and true/false."""
    try:
        message = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError, ValueError, RecursionError:
        raise Refused from None
    if not isinstance(message, dict) or set(message) != {"type", "body"}:
        raise Refused
    name, body = message["type"], message["body"]
    if not isinstance(name, str) or len(name) > 64 or not isinstance(body, dict):
        raise Refused
    flat: Body = {}
    for key, value in body.items():
        if not isinstance(key, str) or len(key) > 64:
            raise Refused
        if not isinstance(value, (str, int, bool)):
            raise Refused
        flat[key] = value
    return Reply(name, flat)


# -- The public phase: before anyone has signed in ---------------------------


def _hello(session: Session, body: Body) -> Reply:
    return Reply("welcome", {"protocol": PROTOCOL_VERSION})


HELLO = MessageSpec(
    name="hello",
    fields={"protocol": Field(int, low=0, high=1000)},
    handler=_hello,
)


def public_registry(max_bytes: int) -> Registry:
    """What the public endpoint answers: `hello` now; Invite redemption
    joins it in the next story. Nothing else, so no record, seat or file is
    reachable before sign-in."""
    registry = Registry(max_bytes)
    registry.register(HELLO)
    return registry
