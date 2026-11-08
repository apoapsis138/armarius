"""A background thread with its own asyncio loop, for a front-end whose own
loop isn't asyncio's (the desktop's Qt loop).

The Remote seat's connection lives on this thread. The window hands it
one short request at a time (`run`), waiting at most `timeout` seconds, so
the window is never held longer than one round trip; anything that waits
on a person (the Storyguide's approval) is asked again on a timer instead
of waited for. No new library: the standard library's
run_coroutine_threadsafe does the crossing.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Coroutine
from typing import Any

#: The longest one request may hold the window.
TIMEOUT = 20.0


class LoopThread:
    """An asyncio loop running on a daemon thread of its own."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever, name="remote seat", daemon=True
        )
        self._thread.start()

    def run[T](self, work: Coroutine[Any, Any, T], timeout: float = TIMEOUT) -> T:
        """Run `work` on the loop and wait for its result. TimeoutError when
        it takes longer than `timeout` (the work is then cancelled)."""
        future = asyncio.run_coroutine_threadsafe(work, self._loop)
        try:
            return future.result(timeout)
        except TimeoutError:
            future.cancel()
            raise

    def stop(self) -> None:
        """End the loop and its thread."""
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
