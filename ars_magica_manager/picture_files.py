"""A portrait's or map's picture: its kinds, safe names and this
computer's folders. Pages read pictures through the window's saga store
(saga_store.SagaStore.picture, a PictureSource): this computer's folders
(`local_picture`), or, for a Joined game, the host (fetched by name when a
page first needs it and kept in memory for the session, never written to
disk), so they don't know which.

A picture's name can come from someone else (an imported saga, a joined
game's host, a player asking the host), so every path that reads or
writes one by name asks `safe_name` first.

Each kind of Picture (a map, a portrait) is one entry in KINDS: its folder
and the most one may be. Everything that reads or sends a picture by its
folder asks `kind`, and a folder that isn't a kind is never read (ADR 0029).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath

from . import paths

PORTRAITS, MAPS = paths.PORTRAITS, paths.MAPS

_MB = 1024 * 1024


@dataclass(frozen=True)
class PictureKind:
    """One kind of Picture: the folder it is kept in (in the save folder,
    and in an export's zip), and the most one may be in bytes, coming in
    from an export or going between a host and a seat."""

    folder: str
    cap: int

    def directory(self) -> Path:
        """This computer's folder for the kind, in the save folder."""
        return paths.data_dir() / self.folder

    def megabytes(self) -> str:
        return f"{self.cap // _MB} MB"


#: Every kind of Picture, by folder. Pattern: Registry, so a new kind of
#: record with pictures (a handout) is one entry here. A hand-drawn map is
#: often far larger than a portrait.
KINDS: dict[str, PictureKind] = {
    found.folder: found
    for found in (PictureKind(PORTRAITS, 5 * _MB), PictureKind(MAPS, 25 * _MB))
}


def kind(folder: str) -> PictureKind | None:
    """The kind of Picture kept in `folder`, or None for any other name
    (one from someone else's file or a seat is never a path)."""
    return KINDS.get(folder)


#: The kinds of picture a portrait or map can be.
SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")

#: Names Windows keeps for devices, whatever follows the dot.
_DEVICES = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{n}" for n in range(10)}
    | {f"lpt{n}" for n in range(10)}
)


def safe_name(name: str) -> bool:
    """Whether `name` is a picture's bare file name, safe to join to the
    portraits or maps folder: no folder, no drive (`D:x.png` would leave
    it on Windows), no hidden stream (`x.png:more`), not hidden, not a
    device, and one of SUFFIXES."""
    if not name or len(name) > 255 or name.startswith("."):
        return False
    if any(c in name for c in ":/\\") or any(ord(c) < 32 for c in name):
        return False
    if PurePosixPath(name).name != name or PureWindowsPath(name).name != name:
        return False
    if name.split(".")[0].strip().lower() in _DEVICES:
        return False
    return PurePosixPath(name).suffix.lower() in SUFFIXES


#: Where a page reads a picture from, by (folder, name): None when it isn't
#: there. The window's saga store (saga_store.SagaStore.picture) is one:
#: this computer's folders, or a Joined game's host.
PictureSource = Callable[[str, str], bytes | None]


def local_picture(folder: str, name: str) -> bytes | None:
    """The picture's bytes from this computer's folders, or None when it
    isn't there."""
    found_kind = kind(folder)
    if found_kind is None or not safe_name(name):
        return None
    path = found_kind.directory() / name
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError:
        return None
