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


def _safe(saga_name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in saga_name)


def remote_folder() -> Path:
    return paths.data_dir() / "remote"


def remote_file(saga_name: str, kind: str) -> Path:
    """The file of `kind` (its suffix, such as "devices.json") for the saga
    called `saga_name`, with the name made safe for a file name."""
    return remote_folder() / f"{_safe(saga_name)}-{kind}"


def lock_of(path: Path) -> Path:
    """The lock file every reader and writer of `path` holds."""
    return path.with_name(f".{path.name}.lock")


#: Every kind of file a saga keeps here, as remote_file names them: its
#: Invites, devices, passcodes noted, Log, tunnel plan, and the browser
#: host's sign-in lockouts.
KINDS = (
    "invites.json",
    "devices.json",
    "passcodes.json",
    "audit.jsonl",
    "host.json",
    "signin.json",
)


def saga_remote_files(saga_name: str) -> list[Path]:
    """The files of KINDS the saga called `saga_name` has. Named one by
    one, not matched by the name's start: "Rhine-" also starts another
    saga's, "Rhine Gold"."""
    return [path for kind in KINDS if (path := remote_file(saga_name, kind)).is_file()]


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
        with held_lock(lock_of(self._path)):
            self._depth += 1
            try:
                self._load()
                yield
            finally:
                self._depth -= 1
