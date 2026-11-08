"""Where a portrait's or map's picture comes from: this computer's folders,
or, for a Joined game, the host (fetched by name when a page first needs
it and kept in memory for the session, never written to disk).

Pages ask `picture(folder, name)` for the bytes, so they don't know which.
"""

from __future__ import annotations

from collections.abc import Callable

from . import storage

PORTRAITS, MAPS = "portraits", "maps"

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
    if not name:
        return None
    if _fetch is not None:
        key = (folder, name)
        if key not in _kept:
            _kept[key] = _fetch(folder, name)
        return _kept[key]
    root = storage.portraits_dir() if folder == PORTRAITS else storage.maps_dir()
    path = root / name
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError:
        return None
