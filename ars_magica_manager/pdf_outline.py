"""Bookmarks (a PDF's outline) added to a PDF already written, so a reader
lists each sheet of a combined PDF by name and jumps to it.

Qt writes no outline, so this appends one as an incremental update, the
way the PDF format lets a file be added to without rewriting it: new
objects for the outline and a new catalog that points to it, then a cross
reference section for them and a trailer naming the one before. It reads
only what it needs of the file Qt wrote (its trailer, catalog and page
tree), and refuses with a ValueError a file it can't follow.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

_TRAILER = re.compile(rb"trailer\s*<<(.*?)>>\s*startxref\s*(\d+)", re.DOTALL)
_REF = re.compile(rb"(\d+)\s+0\s+R")


def _value(found: bytes, key: bytes) -> bytes | None:
    """A trailer's or dictionary's value for `key` (up to the next key)."""
    match = re.search(rb"/" + key + rb"\s+([^/]*)", found)
    return match.group(1).strip() if match else None


def _ref(found: bytes, key: bytes) -> int:
    value = _value(found, key)
    match = _REF.match(value or b"")
    if match is None:
        raise ValueError(f"The PDF's /{key.decode()} isn't a reference.")
    return int(match.group(1))


def _object(data: bytes, number: int) -> bytes:
    """The body of object `number`: what is between its obj and endobj."""
    match = re.search(rb"(?<!\d)%d 0 obj\s*(.*?)\s*endobj" % number, data, re.DOTALL)
    if match is None:
        raise ValueError(f"The PDF has no object {number}.")
    return match.group(1)


def _pages(data: bytes, number: int) -> list[int]:
    """The page objects under the page tree node `number`, in order."""
    node = _object(data, number)
    kids = re.search(rb"/Kids\s*\[(.*?)\]", node, re.DOTALL)
    if kids is None:
        return [number]
    found: list[int] = []
    for kid in (int(n) for n in _REF.findall(kids.group(1))):
        found += _pages(data, kid) if b"/Kids" in _object(data, kid) else [kid]
    return found


def _text(words: str) -> bytes:
    """`words` as a PDF text string: UTF-16 with its mark, in hex, so any
    name prints (Dammërstein)."""
    return b"<FEFF" + words.encode("utf-16-be").hex().upper().encode() + b">"


def add_outline(path: Path, entries: Sequence[tuple[str, int]]) -> None:
    """Add a bookmark for each of `entries` (its title, and the page it
    starts on, counted from 0) to the PDF at `path`, and have a reader
    show them when it opens the file."""
    if not entries:
        return
    data = path.read_bytes()
    trailers = list(_TRAILER.finditer(data))
    if not trailers:
        raise ValueError("The PDF has no trailer to add bookmarks after.")
    trailer, previous = trailers[-1].group(1), int(trailers[-1].group(2))
    size = int(_value(trailer, b"Size") or b"0")
    root = _ref(trailer, b"Root")
    catalog = _object(data, root)
    pages = _pages(data, _ref(catalog, b"Pages"))
    outline = size
    items = list(range(size + 1, size + 1 + len(entries)))
    objects: dict[int, bytes] = {
        outline: b"<< /Type /Outlines /First %d 0 R /Last %d 0 R /Count %d >>"
        % (items[0], items[-1], len(items))
    }
    for k, (title, start) in enumerate(entries):
        if not 0 <= start < len(pages):
            raise ValueError(f"No page {start + 1} for the bookmark {title!r}.")
        links = b""
        if k:
            links += b" /Prev %d 0 R" % items[k - 1]
        if k + 1 < len(items):
            links += b" /Next %d 0 R" % items[k + 1]
        objects[items[k]] = (
            b"<< /Title %s /Parent %d 0 R%s /Dest [%d 0 R /XYZ null null null] >>"
            % (_text(title), outline, links, pages[start])
        )
    body = catalog.strip()
    if not (body.startswith(b"<<") and body.endswith(b">>")):
        raise ValueError("The PDF's catalog isn't a dictionary.")
    body = re.sub(rb"/(Outlines|PageMode)\s+[^/>]*", b"", body[2:-2])
    objects[root] = b"<<%s /Outlines %d 0 R /PageMode /UseOutlines >>" % (
        body.rstrip(),
        outline,
    )
    _append(path, data, objects, trailer, previous, max(objects) + 1)


def _append(
    path: Path,
    data: bytes,
    objects: dict[int, bytes],
    trailer: bytes,
    previous: int,
    size: int,
) -> None:
    """Write `objects` after the file, with their cross references and a
    trailer that points back to the one before."""
    out = bytearray(data if data.endswith(b"\n") else data + b"\n")
    offsets: dict[int, int] = {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += b"%d 0 obj\n%s\nendobj\n" % (number, objects[number])
    xref = len(out)
    out += b"xref\n"
    numbers = sorted(offsets)
    run: list[int] = []
    for number in numbers + [-1]:
        if run and number != run[-1] + 1:
            out += b"%d %d\n" % (run[0], len(run))
            for n in run:
                out += b"%010d 00000 n \n" % offsets[n]
            run = []
        if number >= 0:
            run.append(number)
    extra = b""
    for key in (b"Info", b"ID"):
        value = _value(trailer, key)
        if value:
            extra += b"/%s %s\n" % (key, value)
    root = _ref(trailer, b"Root")
    out += (
        b"trailer\n<<\n/Size %d\n/Root %d 0 R\n%s/Prev %d\n>>\nstartxref\n%d\n%%%%EOF\n"
        % (
            size,
            root,
            extra,
            previous,
            xref,
        )
    )
    path.write_bytes(bytes(out))


def outline_titles(path: Path) -> list[str]:
    """The titles of the PDF's bookmarks, in order (for a check)."""
    data = path.read_bytes()
    found = re.findall(rb"/Title\s*<FEFF([0-9A-F]*)>", data)
    return [bytes.fromhex(h.decode()).decode("utf-16-be") for h in found]
