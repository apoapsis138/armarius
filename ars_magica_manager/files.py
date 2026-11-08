"""Writing the app's files safely."""

from __future__ import annotations

import os
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

#: How long held_lock waits for another program's turn to end, and after
#: how long a lock is taken to be left over from a program that died
#: holding it.
LOCK_WAIT = 10.0
LOCK_STALE = 30.0


@contextmanager
def held_lock(lock: Path) -> Iterator[None]:
    """Hold the lock file `lock` (made, then removed): two copies of the app,
    or the app and a process it started, never read-change-write the same
    file at once."""
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + LOCK_WAIT
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except FileExistsError:
            try:
                stale = time.time() - lock.stat().st_mtime > LOCK_STALE
            except OSError:
                continue  # just released: try again
            if stale or time.monotonic() > deadline:
                lock.unlink(missing_ok=True)
                continue
            time.sleep(0.02)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


#: How often to retry the final rename when Windows refuses it because
#: another program (a sync client, a virus scanner) briefly has the old file
#: open, and how long to wait between tries.
_REPLACE_TRIES = 5
_REPLACE_WAIT = 0.05


def write_atomic(path: Path, text: str) -> None:
    """Write `text` to `path` (UTF-8) so that a crash or a full disk mid-write
    leaves either the old file or the new one, never a truncated mix: the text
    goes to a temp file in the same folder, which then replaces `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        for attempt in range(_REPLACE_TRIES):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if attempt == _REPLACE_TRIES - 1:
                    raise
                time.sleep(_REPLACE_WAIT)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
