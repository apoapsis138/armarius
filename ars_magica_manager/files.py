"""Writing the app's files safely."""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

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
