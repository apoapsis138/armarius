"""Whether another thread's checks are running in this folder.

    uv run python tools/folder_busy.py

Threads share this folder, so a stash, pull, branch switch or reset
changes the files under any check another thread is running, and its
result no longer means anything. `story_check.py` marks the folder busy
while it runs (`marked`); run this before any of those git commands. It
prints what is running and exits 1 while the folder is busy, and exits 0
when it's free (a mark left by a run that has ended is cleared).
"""

from __future__ import annotations

import contextlib
import datetime
import json
import os
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: The mark: what is running, its process and when it started (pytest's
#: own ignored cache folder).
MARK = ROOT / ".pytest_cache" / "folder_busy.json"


def alive(pid: int) -> bool:
    """Whether process `pid` is still running."""
    if sys.platform == "win32":
        found = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
            check=False,
            capture_output=True,
            text=True,
        )
        return f'"{pid}"' in found.stdout
    try:
        os.kill(pid, 0)  # signal 0 only asks whether the process exists
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@contextlib.contextmanager
def marked(what: str) -> Generator[None]:
    """Mark the folder busy with `what` while the block runs."""
    MARK.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    MARK.write_text(
        json.dumps({"what": what, "pid": os.getpid(), "started": started}),
        encoding="utf-8",
    )
    try:
        yield
    finally:
        MARK.unlink(missing_ok=True)


def busy() -> str:
    """What is running in the folder, or "" when nothing is."""
    try:
        mark = json.loads(MARK.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ""
    except ValueError:  # a mark cut short by a crash
        MARK.unlink(missing_ok=True)
        return ""
    pid = mark.get("pid")
    if not isinstance(pid, int) or not alive(pid):
        MARK.unlink(missing_ok=True)
        return ""
    return f"{mark.get('what', '?')} since {mark.get('started', '?')} (process {pid})"


def main() -> int:
    running = busy()
    if running:
        print(
            f"BUSY  {running}.\nWait for it to finish before a stash, pull, "
            "branch switch or reset: those change the files it is checking."
        )
        return 1
    print("free  nothing is checking this folder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
