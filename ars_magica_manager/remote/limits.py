"""Limits on the public door: how many, how fast, how long, how many mistakes.

Each limit keeps one stranger, or one player with a broken app, from using
up the host. The clocks are passed in so tests need not wait.
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Limits:
    """The host's limits. The defaults suit a table of a few players."""

    #: Connections open at once, all addresses together.
    max_connections: int = 24
    #: Connections open at once from one address.
    max_per_address: int = 4
    #: New connections per address in `window` seconds.
    connects_per_window: int = 12
    #: Messages per connection in `window` seconds.
    messages_per_window: int = 60
    window: float = 60.0
    #: Seconds a new connection has to finish the secure handshake.
    handshake_timeout: float = 10.0
    #: Seconds a connection may stay silent before it is closed.
    idle_timeout: float = 120.0
    #: Refused messages tolerated on one connection before it is closed.
    max_strikes: int = 3
    #: Bytes in one message, before encryption.
    max_message: int = 16 * 1024


class RateLimiter:
    """At most `count` events per `window` seconds for each key (a sliding window)."""

    def __init__(
        self,
        count: int,
        window: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._count = count
        self._window = window
        self._clock = clock
        self._events: dict[str, deque[float]] = {}

    def allow(self, key: str) -> bool:
        """Record an event for `key` and say whether it is within the limit."""
        now = self._clock()
        self._forget_quiet_keys(now)
        events = self._events.setdefault(key, deque())
        while events and now - events[0] >= self._window:
            events.popleft()
        if len(events) >= self._count:
            return False
        events.append(now)
        return True

    def _forget_quiet_keys(self, now: float) -> None:
        # Keeps the table from growing with every address ever seen.
        if len(self._events) < 1024:
            return
        for key in [
            k
            for k, ev in self._events.items()
            if not ev or now - ev[-1] >= self._window
        ]:
            del self._events[key]


class ConnectionGate:
    """Counts open connections, in all and per address."""

    def __init__(self, max_total: int, max_per_key: int) -> None:
        self._max_total = max_total
        self._max_per_key = max_per_key
        self._total = 0
        self._per_key: dict[str, int] = {}

    def enter(self, key: str) -> bool:
        if (
            self._total >= self._max_total
            or self._per_key.get(key, 0) >= self._max_per_key
        ):
            return False
        self._total += 1
        self._per_key[key] = self._per_key.get(key, 0) + 1
        return True

    def leave(self, key: str) -> None:
        self._total -= 1
        left = self._per_key[key] - 1
        if left:
            self._per_key[key] = left
        else:
            del self._per_key[key]
