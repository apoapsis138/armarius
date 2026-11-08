"""The message registry: only allowed types, only well-shaped bodies, one uniform refusal."""

from __future__ import annotations

import json

import pytest

from ars_magica_manager.remote.limits import ConnectionGate, RateLimiter
from ars_magica_manager.remote.protocol import (
    PROTOCOL_VERSION,
    REFUSED_TYPE,
    Body,
    Field,
    MessageSpec,
    Refused,
    Registry,
    Reply,
    Session,
    decode_reply,
    encode,
    public_registry,
)

MAX = 1000


def message(name: object, body: object) -> bytes:
    return json.dumps({"type": name, "body": body}).encode()


def registry() -> Registry:
    r = public_registry(MAX)
    r.register(
        MessageSpec(
            name="echo",
            fields={
                "text": Field(str, max_length=10),
                "count": Field(int, low=1, high=5),
                "loud": Field(bool, required=False),
            },
            handler=lambda session, body: Reply("echoed", body),
        )
    )
    return r


def test_hello_is_answered() -> None:
    reply, ok = public_registry(MAX).handle(
        Session(), message("hello", {"protocol": 1})
    )
    assert ok
    assert reply == Reply("welcome", {"protocol": PROTOCOL_VERSION})


def test_the_public_registry_holds_only_hello() -> None:
    assert public_registry(MAX).names() == ["hello"]


def test_a_type_cannot_be_registered_twice() -> None:
    with pytest.raises(ValueError):
        public_registry(MAX).register(
            MessageSpec("hello", {}, lambda session, body: Reply("x"))
        )


def test_a_good_message_reaches_its_handler_with_the_checked_body() -> None:
    reply, ok = registry().handle(
        Session(), message("echo", {"text": "hi", "count": 2, "loud": True})
    )
    assert ok and reply.body == {"text": "hi", "count": 2, "loud": True}


def test_an_optional_field_may_be_left_out() -> None:
    _, ok = registry().handle(Session(), message("echo", {"text": "hi", "count": 2}))
    assert ok


BAD: list[tuple[str, bytes]] = [
    ("unknown type", message("shell", {})),
    ("type is not text", message(5, {})),
    ("missing field", message("echo", {"text": "hi"})),
    ("extra field", message("echo", {"text": "hi", "count": 1, "path": "/etc"})),
    ("text too long", message("echo", {"text": "x" * 11, "count": 1})),
    ("number too big", message("echo", {"text": "hi", "count": 6})),
    ("number too small", message("echo", {"text": "hi", "count": 0})),
    ("text where number", message("echo", {"text": "hi", "count": "1"})),
    ("bool where number", message("echo", {"text": "hi", "count": True})),
    ("number where text", message("echo", {"text": 5, "count": 1})),
    ("number where bool", message("echo", {"text": "hi", "count": 1, "loud": 1})),
    ("nested body value", message("echo", {"text": ["a"], "count": 1})),
    ("body is a list", message("echo", [])),
    ("extra top-level key", json.dumps({"type": "hello", "body": {}, "x": 1}).encode()),
    ("missing body", json.dumps({"type": "hello"}).encode()),
    ("top level is a list", b"[]"),
    ("not json", b"hello"),
    ("not utf-8", b"\xff\xfe\x00"),
    ("empty", b""),
    ("too deep", b"[" * 200_000 + b"]" * 200_000),
    ("over the size limit", message("hello", {"protocol": 1}) + b" " * MAX),
    ("python object syntax", b"__import__('os').system('x')"),
]


@pytest.mark.parametrize("raw", [raw for _, raw in BAD], ids=[name for name, _ in BAD])
def test_a_bad_message_gets_the_one_uniform_refusal(raw: bytes) -> None:
    reply, ok = registry().handle(Session(), raw)
    assert not ok
    assert reply == Reply(REFUSED_TYPE, {})


def test_a_handler_may_refuse_too() -> None:
    def picky(session: Session, body: Body) -> Reply:
        raise Refused

    r = public_registry(MAX)
    r.register(MessageSpec("picky", {}, picky))
    reply, ok = r.handle(Session(), message("picky", {}))
    assert not ok and reply.type == REFUSED_TYPE


def test_a_host_reply_is_checked_when_it_arrives() -> None:
    assert decode_reply(encode(Reply("welcome", {"protocol": 1}))) == Reply(
        "welcome", {"protocol": 1}
    )
    for raw in (
        b"nope",
        b"[]",
        message("x", {"nested": {"a": 1}}),
        message("x" * 65, {}),
        message("x", {"k" * 65: 1}),
        message("x", {"k": None}),
        message("x", {"k": 1.5}),
    ):
        with pytest.raises(Refused):
            decode_reply(raw)


def test_a_rate_limit_counts_a_sliding_window() -> None:
    now = [0.0]
    limiter = RateLimiter(2, 10.0, clock=lambda: now[0])
    assert limiter.allow("a") and limiter.allow("a")
    assert not limiter.allow("a")
    assert limiter.allow("b")  # another key has its own allowance
    now[0] = 10.0
    assert limiter.allow("a")  # the window has moved on


def test_a_rate_limiter_forgets_quiet_keys() -> None:
    now = [0.0]
    limiter = RateLimiter(1, 1.0, clock=lambda: now[0])
    for i in range(1100):
        limiter.allow(f"k{i}")
    now[0] = 5.0
    limiter.allow("fresh")
    assert len(limiter._events) < 10  # pyright: ignore


def test_the_gate_counts_in_all_and_per_address() -> None:
    gate = ConnectionGate(max_total=3, max_per_key=2)
    assert gate.enter("a") and gate.enter("a")
    assert not gate.enter("a")  # that address is full
    assert gate.enter("b")
    assert not gate.enter("c")  # everyone is full
    gate.leave("a")
    assert gate.enter("c")
