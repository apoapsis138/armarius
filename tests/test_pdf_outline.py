"""Bookmarks added to a written PDF (pdf_outline.py), on a small PDF made
by hand: the outline objects, a new catalog, and a trailer back to the
old one, with no UI library."""

import re

import pytest

from ars_magica_manager.pdf_outline import add_outline, outline_titles


def _pdf(pages: int) -> bytes:
    """A small PDF of `pages` empty pages, its cross references right."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [%s] /Count %d >>"
        % (b" ".join(b"%d 0 R" % (3 + k) for k in range(pages)), pages),
        *(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",) * pages,
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for at in offsets:
        out += b"%010d 00000 n \n" % at
    out += b"trailer\n<<\n/Size %d\n/Root 1 0 R\n>>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return bytes(out)


def test_bookmarks_point_at_their_pages(tmp_path):
    path = tmp_path / "book.pdf"
    path.write_bytes(_pdf(4))
    add_outline(path, [("Corvinus", 0), ("Dammër Wulf", 3)])
    data = path.read_bytes()
    assert outline_titles(path) == ["Corvinus", "Dammër Wulf"]
    # Corvinus goes to the first page (object 3), Wulf to the fourth (6).
    dests = re.findall(rb"/Dest \[(\d+) 0 R", data)
    assert dests == [b"3", b"6"]
    # A new catalog shows the outline, and the trailer chains to the old.
    assert b"/Outlines" in data and b"/PageMode /UseOutlines" in data
    assert re.search(rb"/Prev \d+", data.rsplit(b"trailer", 1)[1])
    # Each new object's cross reference points at it, the catalog's too.
    lines = data.rsplit(b"\nxref\n", 1)[1].split(b"trailer", 1)[0].split(b"\n")
    checked, k = [], 0
    while lines[k].strip():
        first, count = map(int, lines[k].split())
        for n in range(count):
            at = int(lines[k + 1 + n].split()[0])
            assert data[at:].startswith(b"%d 0 obj" % (first + n))
            checked.append(first + n)
        k += 1 + count
    assert checked == [1, 7, 8, 9]


def test_a_page_past_the_end_is_refused(tmp_path):
    path = tmp_path / "book.pdf"
    path.write_bytes(_pdf(1))
    with pytest.raises(ValueError, match="No page 3"):
        add_outline(path, [("Nobody", 2)])


def test_no_bookmarks_leaves_the_file_alone(tmp_path):
    path = tmp_path / "book.pdf"
    path.write_bytes(_pdf(1))
    add_outline(path, [])
    assert path.read_bytes() == _pdf(1)
