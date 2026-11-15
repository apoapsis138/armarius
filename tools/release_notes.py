"""A release's notes: its version's section of CHANGELOG.md.

    python tools/release_notes.py 4.12.0 --out notes.md

writes the lines between the "## 4.12.0 — date" heading and the next
"## " heading (the heading itself left out, since the GitHub Release has
its own title), and fails if the changelog has no such version. Each
"### Feature" heading reads as the Features table's plain name first,
"### Help (Glossa)", as What's New shows it. The
release workflow (.github/workflows/release.yml) runs it for the tag it
publishes. It reads the file as plain text, with no import from the app,
so it runs before anything is installed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def plain_names(changelog: str) -> dict[str, str]:
    """Each feature's plain name, from a Features table with a "Plain
    name" column ({} without one)."""
    lines = changelog.splitlines()
    start = next((n for n, line in enumerate(lines) if line == "## Features"), None)
    if start is None:
        return {}
    rows = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("|") and not re.match(r"^\|\s*-", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    if not rows or len(rows[0]) < 3 or rows[0][1] != "Plain name":
        return {}
    return {row[0]: row[1] for row in rows[1:] if len(row) >= 3 and row[1]}


def _heading(line: str, plain: dict[str, str]) -> str:
    """A "### Feature" line with its plain name first."""
    feature = line[4:].strip()
    shown = plain.get(feature, "")
    if line.startswith("### ") and shown and shown != feature:
        return f"### {shown} ({feature})"
    return line


def notes(changelog: str, version: str) -> str:
    """`version`'s section of `changelog`, without its heading, each
    feature heading with its plain name first."""
    heading = re.compile(rf"^## {re.escape(version)} — \d{{4}}-\d{{2}}-\d{{2}}\s*$")
    lines = changelog.splitlines()
    start = next((n for n, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        raise LookupError(f"CHANGELOG.md has no '## {version} — date' heading")
    end = next(
        (n for n in range(start + 1, len(lines)) if lines[n].startswith("## ")),
        len(lines),
    )
    plain = plain_names(changelog)
    body = "\n".join(_heading(line, plain) for line in lines[start + 1 : end]).strip()
    if not body:
        raise LookupError(f"CHANGELOG.md's {version} section is empty")
    return body + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A release's notes from CHANGELOG.md.")
    parser.add_argument("version", help="the version, without its 'v'")
    parser.add_argument("--changelog", type=Path, default=ROOT / "CHANGELOG.md")
    parser.add_argument("--out", type=Path, help="write here, else to stdout")
    args = parser.parse_args(argv)
    try:
        text = notes(args.changelog.read_text(encoding="utf-8"), args.version)
    except (OSError, LookupError) as error:
        print(f"release_notes: {error}", file=sys.stderr)
        return 1
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
