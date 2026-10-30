"""Where a crash of the app itself leaves its trace.

A Python error shows as a message, but a crash inside Qt ends the process
with nothing said, and the Windows report names no line of the app. With
this on, the Python stack of every thread at the crash is appended to
`crash.log` in the data folder, which stays empty until one happens.
"""

from __future__ import annotations

import faulthandler
from pathlib import Path
from typing import TextIO

from . import paths

#: Kept open for the life of the process: a crash can't open a file.
_log: TextIO | None = None


def log_path() -> Path:
    return paths.data_dir() / "crash.log"


def start() -> None:
    """Send the stack of any fatal crash from now on to the log. A log
    that can't be opened leaves the app running without one."""
    global _log
    try:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        _log = path.open("a", encoding="utf-8")
    except OSError:
        return
    faulthandler.enable(file=_log, all_threads=True)
