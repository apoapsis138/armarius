"""Catalog text stays clean of PDF-extraction leftovers, every long Virtue
or Flaw has a summary, and no new over-long paragraph joins the catalogs.

A ratchet: each rule is checked over every entry, and the entries still
over the paragraph cap are listed in `catalog_long_paragraphs.txt` (one id
per line, sorted, so batches that shorten different entries merge
cleanly). The list only shrinks: a restructured entry comes off it.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path

from ars_magica_manager import entry_reading, handout_markup
from ars_magica_manager.markup import LIST_LINE, plain

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STILL_LONG_FILE = Path(__file__).with_name("catalog_long_paragraphs.txt")

#: A paragraph longer than this is hard to read in a details panel.
PARAGRAPH_CAP = 750
#: The catalogs whose long entries (entry_reading.is_long) show a summary
#: and Read in full, so each long one needs a summary.
READABLE = {
    "virtue_flaw_catalog.json",
    "ability_catalog.json",
    "covenant_boon_hook_catalog.json",
}

#: A word the PDF split after its "fi" or "fl" ligature: "specifi c", "Fi rst".
#: (A word in capitals, such as a book's abbreviation "LFI", is left alone.)
SPLIT_LIGATURE = re.compile(r"\b([A-Z]?[a-z]*(?:fi|fl)|F[il]) ([a-z]+)\b")
#: Words that really end in "fi" or "fl" before another word.
WHOLE_WORDS = {"sufi"}
#: An underscore the extraction left in running text.
STRAY_UNDERSCORE = re.compile(r"_")


def _records(data: object) -> Iterator[dict[str, object]]:
    """Every record in a catalog, whatever its layout: a list of records, or
    records under one or more keys (`entries`, `spells`, `weapons`...)."""
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
    elif isinstance(data, dict):
        if "description" in data or "summary" in data:
            yield data
            return
        for value in data.values():
            yield from _records(value)


def _entries() -> Iterator[tuple[str, str, dict[str, object]]]:
    """(catalog file name, entry id or name, entry) for every entry of every
    catalog."""
    for path in sorted(DATA.glob("*_catalog.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in _records(data):
            yield path.name, str(entry.get("id") or entry.get("name") or "?"), entry


def test_every_catalog_yields_entries():
    counts = {path.name: 0 for path in DATA.glob("*_catalog.json")}
    for name, _id, _entry in _entries():
        counts[name] += 1
    empty = sorted(name for name, count in counts.items() if count == 0)
    assert not empty, "catalogs with no entries found (a new layout?):\n" + "\n".join(
        empty
    )


def _texts() -> Iterator[tuple[str, str]]:
    """(where, text) for every entry's description and summary."""
    for name, entry_id, entry in _entries():
        for field in ("description", "summary"):
            text = entry.get(field)
            if isinstance(text, str) and text:
                yield f"{name} {entry_id} {field}", text


def split_ligatures(text: str) -> list[str]:
    return [
        m.group(0)
        for m in SPLIT_LIGATURE.finditer(text)
        if m.group(1).lower() not in WHOLE_WORDS
    ]


def _virtues_and_flaws() -> Iterator[tuple[str, dict[str, object]]]:
    for name, entry_id, entry in _entries():
        if name == "virtue_flaw_catalog.json":
            yield entry_id, entry


def _drawn_pieces(text: str) -> Iterator[str]:
    """The pieces Read in full draws, as the reader parses them: each
    paragraph, each item of a list on its own, and each row of a table."""
    for block in handout_markup.blocks(text, tables=True):
        if block.kind == handout_markup.TABLE:
            yield from (" | ".join(map(plain, row)) for row in block.rows)
            continue
        item: list[str] = []
        for line in plain(block.text).split("\n"):
            if item and LIST_LINE.match(line):
                yield "\n".join(item)
                item = []
            item.append(line)
        yield "\n".join(item)


def _over_cap(text: str) -> bool:
    """Whether a paragraph, one item of a list or one row of a table runs
    over the cap."""
    return any(len(piece) > PARAGRAPH_CAP for piece in _drawn_pieces(text))


def test_no_split_ligatures():
    found = [
        f"{where}: {hit!r}" for where, text in _texts() for hit in split_ligatures(text)
    ]
    assert not found, "split ligatures (join the word):\n" + "\n".join(found)


def test_no_stray_underscores():
    found = [
        f"{where}: {text[max(0, m.start() - 20) : m.end() + 10]!r}"
        for where, text in _texts()
        for m in STRAY_UNDERSCORE.finditer(text)
    ]
    assert not found, "stray underscores from the PDF:\n" + "\n".join(found)


def _readable() -> Iterator[tuple[str, str, dict[str, object]]]:
    """Every entry of the catalogs that offer Read in full on a long entry:
    Virtues and Flaws, Abilities, and Boons and Hooks."""
    for name, entry_id, entry in _entries():
        if name in READABLE:
            yield name, entry_id, entry


def test_every_long_entry_has_a_summary():
    missing = [
        f"{name} {entry_id}"
        for name, entry_id, entry in _readable()
        if entry_reading.is_long(str(entry.get("description") or ""))
        and not str(entry.get("summary") or "").strip()
    ]
    assert not missing, "long entries with no summary:\n" + "\n".join(missing)


def test_the_summary_rule_covers_every_readable_catalog():
    names = {name for name, _id, _entry in _readable()}
    assert names == READABLE


def test_no_new_over_long_paragraph():
    listed = STILL_LONG_FILE.read_text(encoding="utf-8-sig").split()
    assert listed == sorted(set(listed)), (
        f"keep {STILL_LONG_FILE.name} sorted, one id per line"
    )
    over = {
        entry_id
        for entry_id, entry in _virtues_and_flaws()
        if _over_cap(str(entry.get("description") or ""))
    }
    new = sorted(over - set(listed))
    assert not new, (
        f"paragraphs over {PARAGRAPH_CAP} characters; break them up:\n" + "\n".join(new)
    )
    done = sorted(set(listed) - over)
    assert not done, (
        f"now short enough, take off {STILL_LONG_FILE.name}:\n" + "\n".join(done)
    )


def test_every_readable_entry_reads_as_blocks():
    """Read in full lays each description out through the Handout parser:
    every one gives at least one block, and none is read as a tag (a pipe
    table is a table)."""
    read_as = {handout_markup.TEXT, handout_markup.TABLE}
    empty = []
    for _name, entry_id, entry in _readable():
        text = str(entry.get("description") or "")
        found = handout_markup.blocks(text, tables=True)
        if text.strip() and not found:
            empty.append(entry_id)
        elif any(block.kind not in read_as for block in found):
            empty.append(f"{entry_id} (read as a tag)")
    assert not empty, "descriptions that don't read as text:\n" + "\n".join(empty)


def test_the_checks_catch_what_they_look_for():
    assert split_ligatures("a specifi c rule, refl exes") == ["specifi c", "refl exes"]
    assert split_ligatures("Fi rst, the Fl ame") == ["Fi rst", "Fl ame"]
    assert split_ligatures("off their staff with Sufi traditions") == []
    assert split_ligatures("LFI p. 12") == []
    assert _over_cap("x" * (PARAGRAPH_CAP + 1))
    assert not _over_cap(("x" * PARAGRAPH_CAP + "\n\n") * 3)
    # A list's items are read one by one, so each is measured on its own.
    assert not _over_cap("Lead-in:\n" + ("- " + "x" * 700 + "\n") * 3)
    assert not _over_cap(("1. " + "x" * 700 + "\n") * 3)
    assert _over_cap("- short\n- " + "x" * (PARAGRAPH_CAP + 1))
    # A table is drawn row by row, so each row is measured on its own.
    assert not _over_cap("| A | B |\n|---|---|\n" + ("| " + "x" * 300 + " | y |\n") * 5)
    assert _over_cap("| A |\n|---|\n| " + "x" * (PARAGRAPH_CAP + 1) + " |")
    # Only what is drawn as a list or a table is split: a year opening a
    # line, or rows with no rule under a header, stay one paragraph.
    assert _over_cap("x" * 400 + "\n1220. " + "x" * 400)
    assert _over_cap(("| " + "x" * 400 + " |\n") * 2)
