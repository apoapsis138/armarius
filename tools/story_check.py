"""The checks after each slice of a story, in one call.

    uv run python tools/story_check.py

Runs, in order: the slice tests (`slice_tests.py`), `ruff format`,
`ruff check` and `pyright`. Each prints one line (ok, or the failing
test names / the first lines of the tool's output), and the exit code is
nonzero if any failed. When all pass it says to run the full suite once
(CLAUDE.md); a second full run in one story is for `--lf` only.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UV = ["uv", "run"]


def run(command: list[str]) -> tuple[int, str]:
    done = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return done.returncode, done.stdout + done.stderr


def failures(output: str) -> str:
    names = re.findall(r"^FAILED (\S+)", output, flags=re.MULTILINE)
    summary = output.strip().splitlines()[-1] if output.strip() else ""
    return "\n".join([*names[:20], summary])


def main() -> int:
    steps = [
        ("slice tests", [*UV, "python", "tools/slice_tests.py", "-q"], failures),
        ("ruff format", [*UV, "ruff", "format", "."], lambda o: o.strip()[-400:]),
        ("ruff check", [*UV, "ruff", "check", "."], lambda o: o.strip()[-800:]),
        ("pyright", [*UV, "pyright"], lambda o: o.strip()[-800:]),
    ]
    bad = 0
    for label, command, report in steps:
        code, output = run(command)
        if code == 0:
            print(f"ok    {label}")
        else:
            bad += 1
            print(f"FAIL  {label}\n{report(output)}")
    if bad:
        return 1
    print("\nAll clear. Story done? Run the full suite once; rerun only --lf after.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
