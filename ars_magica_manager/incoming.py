"""Reading a file that comes in from someone else -- a saga file, an
export, a content pack, a Mystery Cult file, a picture inside an export --
within limits, so one made too big, or nested too deep, is refused with a
ValueError saying so instead of filling the memory or crashing the app.

A plain file's size is looked at before it is read; a member of a zip, its
size as the zip records it, and then no more than that limit is unpacked
whatever the zip says. The limits suit a table's sagas: the largest real
save is about 2.5 MB.

Pattern: Facade. Every door a file comes in by reads it here, by one call,
and none of them sizes, unzips or parses it itself. Laid out like the
Remote seats' own limits (remote/limits.py), which guard the network.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

#: Bytes in any JSON file coming in: a saga file, export, pack or cult.
MAX_JSON = 50 * 1024 * 1024
#: Bytes in one picture inside an export (as a Remote seat's picture).
MAX_PICTURE = 5 * 1024 * 1024
#: Lists and records inside one another in a JSON file coming in. The
#: deepest shipped pack or real save nests 12; reading what the app writes
#: (shape check, from_dict) recurses once a level.
MAX_DEPTH = 100


def _megabytes(limit: int) -> str:
    return f"{limit // (1024 * 1024)} MB"


def read_bounded(
    source: Path | zipfile.ZipFile, member: str = "", *, limit: int | None = None
) -> bytes:
    """The bytes of the file at `source`, or of `member` of the zip
    `source`, if there are no more than `limit` of them (MAX_JSON by
    default); ValueError if there are. KeyError for a member the zip
    hasn't, OSError for a file that can't be read."""
    most = MAX_JSON if limit is None else limit
    too_big = f"the file is larger than {_megabytes(most)}"
    if isinstance(source, zipfile.ZipFile):
        info = source.getinfo(member)
        size = info.file_size
        if size > most:
            raise ValueError(too_big)
        with source.open(info) as file:
            # One byte past the size it says, so a zip that says less than
            # it holds is caught too.
            data = file.read(size + 1)
    else:
        size = source.stat().st_size
        if size > most:
            raise ValueError(too_big)
        with source.open("rb") as file:
            # Its size, not the limit: a read reserves what it asks for.
            data = file.read(size + 1)
    if len(data) > size:
        # Grown since it was looked at, or a zip that said less than it
        # holds: refused rather than read past what was allowed.
        raise ValueError(
            too_big if len(data) > most else "the file changed as it was read"
        )
    return data


def text(data: bytes) -> str:
    """`data` as text; ValueError if it isn't UTF-8."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as problem:
        raise ValueError(f"not UTF-8 text ({problem.reason})") from None


_TOO_DEEP = "not a file this app can read (nested too deeply)"


def loads(found: str) -> Any:
    """The JSON in `found`; ValueError if it isn't JSON, or nests lists and
    records more than MAX_DEPTH deep. Where the parser itself gives up
    first depends on the platform's stack, so the depth is measured too."""
    try:
        data = json.loads(found)
    except json.JSONDecodeError as problem:
        raise ValueError(f"not a JSON file ({problem.msg})") from None
    except RecursionError:
        raise ValueError(_TOO_DEEP) from None
    if _too_deep(data):
        raise ValueError(_TOO_DEEP)
    return data


def _too_deep(value: object) -> bool:
    """Whether `value` nests lists and records more than MAX_DEPTH deep,
    walked a level at a time (no recursion: that is what it guards)."""
    level = [value]
    for _ in range(MAX_DEPTH):
        inner: list[object] = []
        for item in level:
            if isinstance(item, dict):
                inner.extend(v for v in item.values() if isinstance(v, dict | list))
            elif isinstance(item, list):
                inner.extend(v for v in item if isinstance(v, dict | list))
        if not inner:
            return False
        level = inner
    return True


def read_text(path: Path) -> str:
    """The text of the file at `path`, read within MAX_JSON."""
    return text(read_bounded(path))


def read_json(path: Path) -> Any:
    """The JSON in the file at `path`, read within MAX_JSON."""
    return loads(read_text(path))
