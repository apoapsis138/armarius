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

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STILL_LONG_FILE = Path(__file__).with_name("catalog_long_paragraphs.txt")

#: A paragraph longer than this is hard to read in a details panel.
PARAGRAPH_CAP = 750
#: An entry whose description is longer than this is "long" and needs a summary.
LONG_ENTRY = 750

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


def _over_cap(text: str) -> bool:
    return any(len(p) > PARAGRAPH_CAP for p in re.split(r"\n\s*\n", text))


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


def test_every_long_virtue_or_flaw_has_a_summary():
    missing = [
        entry_id
        for entry_id, entry in _virtues_and_flaws()
        if len(str(entry.get("description") or "")) > LONG_ENTRY
        and not str(entry.get("summary") or "").strip()
    ]
    assert not missing, "long entries with no summary:\n" + "\n".join(missing)


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


def test_the_checks_catch_what_they_look_for():
    assert split_ligatures("a specifi c rule, refl exes") == ["specifi c", "refl exes"]
    assert split_ligatures("Fi rst, the Fl ame") == ["Fi rst", "Fl ame"]
    assert split_ligatures("off their staff with Sufi traditions") == []
    assert split_ligatures("LFI p. 12") == []
    assert _over_cap("x" * (PARAGRAPH_CAP + 1))
    assert not _over_cap(("x" * PARAGRAPH_CAP + "\n\n") * 3)
