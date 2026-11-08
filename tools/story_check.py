"""The checks after each slice of a story, in one call.

    uv run python tools/story_check.py          # a slice
    uv run python tools/story_check.py --full   # once per story

Runs, in order: the tests (the slice's from `slice_tests.py`, or with
--full the whole suite), `ruff format`, `ruff check` and `pyright`. Each
prints one line (ok, or the failing test names / the first lines of the
tool's output), and the exit code is nonzero if any failed.

A test that fails in the parallel run is run again once, alone. One that
then passes is reported as flaky, not failed, and noted (with the date) in
FLAKY_LOG, so the worst offenders can be found and their waits fixed; one
that fails again is real.
"""

from __future__ import annotations

import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UV = ["uv", "run"]
#: Where flaky tests are noted, one line each (pytest's own ignored cache).
FLAKY_LOG = ROOT / ".pytest_cache" / "flaky_tests.txt"
PARALLEL = ["-q", "-n", "auto", "--dist", "worksteal"]


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


def failed_tests(output: str) -> list[str]:
    return re.findall(r"^(?:FAILED|ERROR) (\S+)", output, flags=re.MULTILINE)


def summary(output: str) -> str:
    return output.strip().splitlines()[-1] if output.strip() else ""


def tests_step(command: list[str]) -> tuple[bool, str]:
    """Run the tests; rerun each failure alone. (passed, what to print)."""
    code, output = run(command)
    if code == 0:
        return True, summary(output)
    failed = failed_tests(output)
    if not failed:
        return False, summary(output)
    real, flaky = [], []
    for test in failed:
        again, _ = run([*UV, "python", "-m", "pytest", "-q", "-p", "no:xdist", test])
        (flaky if again == 0 else real).append(test)
    if flaky:
        FLAKY_LOG.parent.mkdir(parents=True, exist_ok=True)
        today = datetime.datetime.now(datetime.UTC).date().isoformat()
        with FLAKY_LOG.open("a", encoding="utf-8") as log:
            log.writelines(f"{today} {test}\n" for test in flaky)
    lines = [f"flaky (passed alone): {test}" for test in flaky]
    lines += [f"FAILED {test}" for test in real[:20]]
    lines.append(summary(output))
    return not real, "\n".join(lines)


def main(argv: list[str]) -> int:
    full = "--full" in argv
    if full:
        tests = [*UV, "python", "-m", "pytest", *PARALLEL]
    else:
        tests = [*UV, "python", "tools/slice_tests.py", *PARALLEL]
    bad = 0
    passed, said = tests_step(tests)
    label = "full suite" if full else "slice tests"
    if passed:
        print(f"ok    {label}" + (f"\n{said}" if "flaky" in said or full else ""))
    else:
        bad += 1
        print(f"FAIL  {label}\n{said}")
    tools = [
        ("ruff format", [*UV, "ruff", "format", "."], 400),
        ("ruff check", [*UV, "ruff", "check", "."], 800),
        ("pyright", [*UV, "pyright"], 800),
    ]
    for name, command, keep in tools:
        code, output = run(command)
        if code == 0:
            print(f"ok    {name}")
        else:
            bad += 1
            print(f"FAIL  {name}\n{output.strip()[-keep:]}")
    if bad:
        return 1
    if not full:
        print("\nAll clear. Story done? Run it once with --full.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
