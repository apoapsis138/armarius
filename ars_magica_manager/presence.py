"""Who has which record open, across the copies of a hosted app.

Every copy runs on the storyguide's computer, so each one keeps a small
file in the sagas folder (".presence/<session>.json") saying who is using
it, which saga and which record they have open, and when it last said so.
A copy that stops saying so (closed, or its browser tab gone) drops out
after FRESH seconds.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from . import storage
from .files import write_atomic

#: How long a copy counts as still there after it last noted itself.
FRESH = 10.0


def _folder() -> Path:
    return storage.sagas_dir() / ".presence"


def note(session: str, saga_id: str, who: str, record: str | None) -> None:
    """Say that `who`, in this copy (`session`), has `record` of the saga
    open (None: no record, e.g. the saga's own node)."""
    entry = {"saga": saga_id, "who": who, "record": record, "seen": time.time()}
    try:
        write_atomic(_folder() / f"{session}.json", json.dumps(entry))
    except OSError:
        pass  # presence is a courtesy: never stop the app over it


def leave(session: str) -> None:
    """This copy is closing its saga."""
    (_folder() / f"{session}.json").unlink(missing_ok=True)


def others_on(session: str, saga_id: str, record: str | None) -> list[str]:
    """Who else, in another copy, has `record` of the saga open now."""
    if record is None:
        return []
    names: list[str] = []
    now = time.time()
    for path in _folder().glob("*.json"):
        if path.stem == session:
            continue
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            continue
        if not isinstance(entry, dict):
            continue
        if now - float(entry.get("seen", 0)) > FRESH:
            continue
        if entry.get("saga") == saga_id and entry.get("record") == record:
            names.append(str(entry.get("who") or "The storyguide"))
    return sorted(set(names))
