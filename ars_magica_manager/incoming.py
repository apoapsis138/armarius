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
        if info.file_size > most:
            raise ValueError(too_big)
        with source.open(info) as file:
            data = file.read(most + 1)
    else:
        if source.stat().st_size > most:
            raise ValueError(too_big)
        with source.open("rb") as file:
            data = file.read(most + 1)
    if len(data) > most:
        raise ValueError(too_big)
    return data


def text(data: bytes) -> str:
    """`data` as text; ValueError if it isn't UTF-8."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as problem:
        raise ValueError(f"not UTF-8 text ({problem.reason})") from None


def loads(found: str) -> Any:
    """The JSON in `found`; ValueError if it isn't JSON, or is nested too
    deeply to read."""
    try:
        return json.loads(found)
    except json.JSONDecodeError as problem:
        raise ValueError(f"not a JSON file ({problem.msg})") from None
    except RecursionError:
        raise ValueError("not a file this app can read (nested too deeply)") from None


def read_text(path: Path) -> str:
    """The text of the file at `path`, read within MAX_JSON."""
    return text(read_bounded(path))


def read_json(path: Path) -> Any:
    """The JSON in the file at `path`, read within MAX_JSON."""
    return loads(read_text(path))
