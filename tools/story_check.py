"""The checks after each slice of a story, in one call.

    uv run python tools/story_check.py          # a slice
    uv run python tools/story_check.py --full   # once per story
    uv run python tools/story_check.py --goldens  # regenerate the goldens

Runs, in order: the tests (the slice's from `slice_tests.py`, or with
--full the whole suite), ruff's import sorting (applied), `ruff format`,
`ruff check` and `pyright`. Each
prints one line (ok, or the failing test names / the first lines of the
tool's output), and the exit code is nonzero if any failed.

A test run past its limit (FULL_LIMIT, SLICE_LIMIT) is stopped with
every worker it started, and said; the conftest also fails a test whose
window waits for an answer no test gives.

A test that fails in the parallel run is run again once, alone. One that
then passes is reported as flaky, not failed, and noted (with the date) in
FLAKY_LOG, so the worst offenders can be found and their waits fixed; one
that fails again is real, and printed with why (its first `E ` line: a
broken help file or a failed assertion, in full).
"""

from __future__ import annotations

import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UV = ["uv", "run"]
#: Where flaky tests are noted, one line each (pytest's own ignored cache).
FLAKY_LOG = ROOT / ".pytest_cache" / "flaky_tests.txt"
PARALLEL = ["-q", "-n", "auto", "--dist", "worksteal"]


#: The longest a test run may take (seconds) before it is stopped, every
#: worker with it: the full suite takes about four minutes.
FULL_LIMIT = 600
SLICE_LIMIT = 420


class TimedOut(Exception):
    """A run went past its limit; it and its workers were stopped."""


def stop_tree(pid: int) -> None:
    """End a process and every process it started (pytest's workers):
    ending only the parent leaves the workers running, holding files."""
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(pid)],
            check=False,
            capture_output=True,
        )
    else:
        subprocess.run(["pkill", "-KILL", "-P", str(pid)], check=False)
        subprocess.run(["kill", "-KILL", str(pid)], check=False)


def run(command: list[str], limit: float | None = None) -> tuple[int, str]:
    """Run `command`; its exit code and output. TimedOut past `limit`."""
    with subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    ) as process:
        try:
            output, _ = process.communicate(timeout=limit)
        except subprocess.TimeoutExpired:
            stop_tree(process.pid)
            process.communicate()
            raise TimedOut from None
        return process.returncode, output


def failed_tests(output: str) -> list[str]:
    return re.findall(r"^(?:FAILED|ERROR) (\S+)", output, flags=re.MULTILINE)


def reason(output: str) -> str:
    """Why a test failed, from its run alone: the first `E ` line (an
    assertion or the error raised), else the last line of output."""
    for line in output.splitlines():
        if line.startswith("E "):
            return line[1:].strip()[:300]
    return summary(output)


def summary(output: str) -> str:
    return output.strip().splitlines()[-1] if output.strip() else ""


#: Each pytest worker's test under way, written by tests/conftest.py.
RUNNING = ROOT / ".pytest_cache" / "running"


def still_running() -> list[str]:
    """The tests the workers were in when the run was stopped."""
    if not RUNNING.is_dir():
        return []
    return sorted(f.read_text(encoding="utf-8").strip() for f in RUNNING.glob("*.txt"))


def stopped(limit: float) -> str:
    """What to say of a run stopped at its limit: the tests it was in. A
    test seen there again on a rerun is stuck; a long list of different
    ones means the run is simply too big for the limit (run the files in
    smaller groups)."""
    running = still_running()
    lines = [f"stopped after {limit:.0f} s, every test process with it."]
    if running:
        lines.append("Still running then:")
        lines += [f"  {test}" for test in running]
        lines.append(
            "Run those alone with -p no:xdist: one that hangs is stuck (a "
            "window waiting for an answer, a wait that never ends); if each "
            "passes, the slice is too big for the limit."
        )
    return "\n".join(lines)


def tests_step(command: list[str], limit: float) -> tuple[bool, str]:
    """Run the tests; rerun each failure alone. (passed, what to print)."""
    if RUNNING.is_dir():
        for leftover in RUNNING.glob("*.txt"):
            leftover.unlink(missing_ok=True)
    try:
        code, output = run(command, limit)
    except TimedOut:
        return False, stopped(limit)
    if code == 0:
        return True, summary(output)
    failed = failed_tests(output)
    if not failed:
        return False, summary(output)
    real: list[tuple[str, str]] = []
    flaky: list[str] = []
    for test in failed:
        try:
            again, said = run(
                [*UV, "python", "-m", "pytest", "-q", "-p", "no:xdist", test],
                SLICE_LIMIT,
            )
        except TimedOut:
            again, said = 1, f"stopped after {SLICE_LIMIT} s: stuck"
        if again == 0:
            flaky.append(test)
        else:
            real.append((test, reason(said)))
    if flaky:
        FLAKY_LOG.parent.mkdir(parents=True, exist_ok=True)
        today = datetime.datetime.now(datetime.UTC).date().isoformat()
        with FLAKY_LOG.open("a", encoding="utf-8") as log:
            log.writelines(f"{today} {test}\n" for test in flaky)
    lines = [f"flaky (passed alone): {test}" for test in flaky]
    lines += [f"FAILED {test}\n      {why}" for test, why in real[:20]]
    lines.append(summary(output))
    return not real, "\n".join(lines)


#: Regenerating the golden files: the sheet text in parallel, and the
#: dispatch matrix in one process (its shards write one file), side by
#: side. The matrix takes about ten minutes; run this in the background.
GOLDENS = (
    [*UV, "python", "-m", "pytest", *PARALLEL, "tests/test_sheet_text.py"],
    [
        *UV,
        "python",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:xdist",
        "tests/test_dispatch_matrix.py",
    ],
)


def goldens() -> int:
    """Regenerate both golden files at once; then show what changed."""
    env = {**os.environ, "UPDATE_GOLDEN": "1"}
    processes = [
        subprocess.Popen(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for command in GOLDENS
    ]
    bad = 0
    for command, process in zip(GOLDENS, processes, strict=True):
        output, _ = process.communicate()
        name = command[-1]
        if process.returncode == 0:
            print(f"ok    {name}")
        else:
            bad += 1
            print(f"FAIL  {name}\n{output.strip()[-800:]}")
    _code, diff = run(["git", "diff", "--stat", "--", "tests/golden"])
    print(diff.strip() or "No golden changed.")
    print("Review the diff of tests/golden before committing.")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if "--goldens" in argv:
        return goldens()
    full = "--full" in argv
    if full:
        tests = [*UV, "python", "-m", "pytest", *PARALLEL]
    else:
        tests = [*UV, "python", "tools/slice_tests.py", *PARALLEL]
    bad = 0
    passed, said = tests_step(tests, FULL_LIMIT if full else SLICE_LIMIT)
    label = "full suite" if full else "slice tests"
    if passed:
        print(f"ok    {label}" + (f"\n{said}" if "flaky" in said or full else ""))
    else:
        bad += 1
        print(f"FAIL  {label}\n{said}")
    tools = [
        # Sorting imports is ruff's one fix applied here: always safe, and
        # otherwise the commonest reason to run the checks twice.
        (
            "ruff sort imports",
            [*UV, "ruff", "check", "--select", "I", "--fix", "."],
            400,
        ),
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
    else:
        print(
            "\nAll clear. On commit, the version: MINOR if the story adds or "
            "changes what the app does, PATCH for a fix, code health, tests "
            "or docs; stories committed together take the largest."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
