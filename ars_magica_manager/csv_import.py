"""Reading records from a CSV file with a header row -- shared by the book
and spell imports, which each supply how one row becomes a record."""

from __future__ import annotations

import csv
import io
from collections.abc import Callable, Sequence
from pathlib import Path

from .markup import escape, problem


def read_text_any(path: Path) -> str:
    """A text file's contents: UTF-8 (with or without Excel's byte-order mark),
    falling back to Windows-1252 for older spreadsheets."""
    data = Path(path).read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252")


def parse_rows[T](
    text: str,
    required: Sequence[str],
    known: Sequence[str],
    from_row: Callable[[dict[str, str]], T],
    *,
    missing_joiner: str = ", ",
) -> tuple[list[T], list[str], list[str]]:
    """(records, skipped rows, unused columns) from CSV `text`. Column names
    match in any case and order; `from_row` gets each row keyed by lower-case
    column name and raises ValueError to skip it (the reason is reported).
    Raises ValueError if a `required` column is missing."""
    reader = csv.DictReader(io.StringIO(text))
    headers = [h.strip().lower() for h in reader.fieldnames or []]
    missing = [c for c in required if c not in headers]
    if missing:
        raise ValueError(f"no {missing_joiner.join(missing)} column in the header row")
    unused = [h for h in headers if h not in known]
    records: list[T] = []
    skipped: list[str] = []
    for line, raw in enumerate(reader, start=2):
        row = {
            (key or "").strip().lower(): (value or "")
            for key, value in raw.items()
            if not isinstance(value, list)  # extra cells beyond the header
        }
        if not any(v.strip() for v in row.values()):
            continue  # a blank line
        try:
            records.append(from_row(row))
        except ValueError as problem:
            name = row.get("name", "").strip()
            label = f"Row {line}" + (f" ({name})" if name else "")
            skipped.append(f"{label}: {problem}.")
    return records, skipped, unused


def skipped_preview(skipped: Sequence[str], shown: int = 5) -> list[str]:
    """The import confirmation's lines about rows that will be skipped (markup),
    or none."""
    if not skipped:
        return []
    lines = ["", problem(f"{len(skipped)} row(s) will be skipped:")]
    lines += [f"  {escape(s)}" for s in skipped[:shown]]
    if len(skipped) > shown:
        lines.append(f"  ...and {len(skipped) - shown} more.")
    return lines
