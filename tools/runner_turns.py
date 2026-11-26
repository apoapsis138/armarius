"""Test runs on this computer take turns.

Several checkouts of the repo (git worktrees) may be worked in on one PC
at once, and each runs its tests across every core. Run together they compete for
the CPU: a slice run stops at its limit behind tests that pass in seconds
alone, and the full suite flakes. So `story_check.py` holds the computer's
turn while its tests run (`turn`); another run waits, saying whose turn it
is, and goes on when it's free. Lint, format and type checks don't wait.

The turn is an operating-system lock on a file in the repo's shared git
folder (the main checkout's `.git`), which every worktree has in common and
no process's temporary or home folder changes; a run that dies holding it
frees it.

Only story_check's test runs take the turn. A single test run on its own
(`pytest -p no:xdist tests/<file>.py::<test>`) doesn't wait: several may
run side by side.
"""

from __future__ import annotations

import contextlib
import datetime
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable, Generator
from pathlib import Path
from typing import IO


def _shared_lock() -> Path:
    """The lock file in the git folder every worktree of this repo shares
    (`git rev-parse --git-common-dir`), which no process's environment
    changes; the home folder when there is no git checkout."""
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except OSError, subprocess.CalledProcessError:
        return Path.home() / ".armarius-test-runner.lock"
    return Path(common) / "armarius-test-runner.lock"


#: The repo's one test-runner turn, shared by every worktree and process.
LOCK = _shared_lock()


def _try_lock(handle: IO[bytes]) -> bool:
    """Take the lock on `handle` if it's free; whether it was taken."""
    try:
        if sys.platform == "win32":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


def _unlock(handle: IO[bytes]) -> None:
    if sys.platform == "win32":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _holder_file() -> Path:
    return LOCK.with_suffix(".json")


def holder() -> str:
    """Whose turn it is, as the run holding it wrote it ("" if unknown)."""
    try:
        found = json.loads(_holder_file().read_text(encoding="utf-8"))
    except OSError, ValueError:
        return ""
    return f"{found.get('what', '?')} since {found.get('started', '?')}"


@contextlib.contextmanager
def turn(
    what: str, *, every: float = 5.0, say: Callable[[str], None] = print
) -> Generator[None]:
    """Wait for this computer's test-runner turn, then hold it while the
    block runs. While waiting, `say` once whose turn it is."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "a+b") as handle:
        waited = False
        while not _try_lock(handle):
            if not waited:
                say(f"wait  another test run has the turn: {holder() or 'unknown'}")
                waited = True
            time.sleep(every)
        started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        _holder_file().write_text(
            json.dumps({"what": what, "pid": os.getpid(), "started": started}),
            encoding="utf-8",
        )
        try:
            yield
        finally:
            _holder_file().unlink(missing_ok=True)
            _unlock(handle)
