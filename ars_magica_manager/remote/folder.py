"""Where a hosted saga's Remote seat files live, and how two processes share
them.

The files sit in the host's data folder, never the saga file, so nothing in
them travels with the saga or an export of it. The Storyguide's window
(issuing, approving, revoking) and the listener, a process of its own
(redeeming, signing in), both change them, so each book reads its file
again under a lock before every use (`SharedFile`): neither works from a
copy the other has since changed, and a revoke is never written over.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .. import paths
from ..files import held_lock


def remote_file(saga_name: str, kind: str) -> Path:
    """The file of `kind` (its suffix, such as "devices.json") for the saga
    called `saga_name`, with the name made safe for a file name."""
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in saga_name)
    return paths.data_dir() / "remote" / f"{safe}-{kind}"


class SharedFile:
    """A book kept in one file that more than one process changes. A
    subclass sets `_path` and reads it in `_load` (all of it, from nothing:
    a missing file is an empty book); each public method runs inside
    `_fresh()`."""

    _path: Path
    _depth: int = 0

    def _load(self) -> None:
        raise NotImplementedError

    @contextmanager
    def _fresh(self) -> Iterator[None]:
        """Hold the file's lock with the file read again. A method that
        calls another inside it keeps the one lock."""
        if self._depth:
            yield
            return
        with held_lock(self._path.with_name(f".{self._path.name}.lock")):
            self._depth += 1
            try:
                self._load()
                yield
            finally:
                self._depth -= 1
