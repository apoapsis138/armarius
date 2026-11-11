"""Where a portrait's or map's picture comes from: this computer's folders,
or, for a Joined game, the host (fetched by name when a page first needs
it and kept in memory for the session, never written to disk).

Pages ask `picture(folder, name)` for the bytes, so they don't know which.

A picture's name can come from someone else (an imported saga, a joined
game's host, a player asking the host), so every path that reads or
writes one by name asks `safe_name` first.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import PurePosixPath, PureWindowsPath

from . import storage

PORTRAITS, MAPS = "portraits", "maps"

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


#: The host's pictures while a Joined game is open: fetched by
#: (folder, name), None when the host hasn't it.
_fetch: Callable[[str, str], bytes | None] | None = None
_kept: dict[tuple[str, str], bytes | None] = {}


def use_host(fetch: Callable[[str, str], bytes | None] | None) -> None:
    """Take pictures from the host (`fetch`), or this computer's folders
    again (None). Either way what was kept is forgotten."""
    global _fetch
    _fetch = fetch
    _kept.clear()


def picture(folder: str, name: str) -> bytes | None:
    """The picture's bytes, or None when it isn't there."""
    if not safe_name(name):
        return None
    if _fetch is not None:
        key = (folder, name)
        if key not in _kept:
            try:
                _kept[key] = _fetch(folder, name)
            except ConnectionError, TimeoutError:
                return None  # the host can't be reached: asked again next time
        return _kept[key]
    root = storage.portraits_dir() if folder == PORTRAITS else storage.maps_dir()
    path = root / name
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError:
        return None
