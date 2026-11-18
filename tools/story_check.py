"""The checks after each slice of a story, in one call.

    uv run python tools/story_check.py          # a slice
    uv run python tools/story_check.py --full   # once per story
    uv run python tools/story_check.py --goldens  # regenerate the goldens

Runs, in order: the tests (the slice's from `slice_tests.py`, or with
--full the whole suite), ruff's import sorting (applied), `ruff format`,
`ruff check` and `pyright`, and with --full last `boot_smoke.py` (both
front-ends start). Each
prints one line (ok, or the failing test names / the first lines of the
tool's output), and the exit code is nonzero if any failed.

The folder is marked busy while it runs (`folder_busy.py`), so a thread
sharing it waits before a stash, pull, branch switch or reset. Its tests
wait for this computer's test-runner turn (`runner_turns.py`), so runs
from other worktrees don't compete for the CPU; the wait doesn't count
against the limits.

A test run past its limit (FULL_LIMIT, SLICE_LIMIT) is stopped with
every worker it started, and said; the conftest also fails a test whose
window waits for an answer no test gives.

A test that fails in the parallel run is run again once, alone, by its
exact id (tools/rerun_once.py, shared with CI). One that then passes is
flaky: it is named, noted (with the date) in FLAKY_LOG, the list of flaky
tests to fix, and the check still fails, since a flaky test is a bug in
its waits (CONTRIBUTING.md, "Textual and Pilot gotchas"). One that fails
again is real, and printed with why (its first `E ` line: a broken help
file or a failed assertion, in full).
"""

from __future__ import annotations

import datetime
import os
import subprocess
import sys

import runner_turns
from folder_busy import marked
from rerun_once import (
    ROOT,
    Failure,
    Outcome,
    RerunOnce,
    failed_lines,
    run,
    summary,
)

UV = ["uv", "run"]
#: Where flaky tests are noted, one line each (pytest's own ignored cache).
FLAKY_LOG = ROOT / ".pytest_cache" / "flaky_tests.txt"
PARALLEL = ["-q", "-n", "auto", "--dist", "worksteal"]


#: The longest a test run may take (seconds) before it is stopped, every
#: worker with it: the full suite takes about four minutes.
FULL_LIMIT = 600
SLICE_LIMIT = 420
#: How often a run waiting for another's test-runner turn looks again
#: (seconds); the wait doesn't count against the limits.
TURN_EVERY = 5.0


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


class LocalRerun(RerunOnce):
    """On your machine: every failure is tried again, and a flaky test
    fails the check as a real one does."""

    python = (*UV, "python")

    def reruns(self, failure: Failure) -> bool:
        return True

    def stopped(self, limit: float | None) -> str:
        return stopped(limit or 0)

    def verdict(self, outcome: Outcome) -> tuple[bool, str]:
        flaky = [failure.nodeid for failure in outcome.flaky]
        if flaky:
            FLAKY_LOG.parent.mkdir(parents=True, exist_ok=True)
            today = datetime.datetime.now(datetime.UTC).date().isoformat()
            with FLAKY_LOG.open("a", encoding="utf-8") as log:
                log.writelines(f"{today} {test}\n" for test in flaky)
        lines = [f"FLAKY {test} (failed in the run, passed alone)" for test in flaky]
        lines += failed_lines(outcome)
        lines.append(summary(outcome.output))
        if flaky:
            lines.append(
                f"{len(flaky)} flaky: a flaky test fails the check; fix its waits "
                f"(the list to fix: {FLAKY_LOG.relative_to(ROOT).as_posix()})."
            )
        return not outcome.real and not flaky, "\n".join(lines)


def tests_step(command: list[str], limit: float) -> tuple[bool, str]:
    """Run the tests; rerun each failure alone. (passed, what to print)."""
    if RUNNING.is_dir():
        for leftover in RUNNING.glob("*.txt"):
            try:
                leftover.unlink(missing_ok=True)
            except OSError:  # another run's, still open
                pass
    # `run` looked up now, so a test can stand in for it.
    return LocalRerun(lambda c, lim, env: run(c, lim, env)).check(command, limit)


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
    # Test runs on this computer take turns (runner_turns.py); the checks
    # after them don't wait.
    what = f"story_check {'--full' if full else '(slice)'} in {ROOT.name}"
    with runner_turns.turn(what, every=TURN_EVERY):
        passed, said = tests_step(tests, FULL_LIMIT if full else SLICE_LIMIT)
    label = "full suite" if full else "slice tests"
    if passed:
        print(f"ok    {label}" + (f"\n{said}" if full else ""))
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
    if full:
        # Both front-ends start, as a person would start them.
        tools.append(("boot", [*UV, "python", "tools/boot_smoke.py"], 1600))
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
    # The folder is marked busy for the whole run, so another thread
    # sharing it waits before a stash or pull (folder_busy.py).
    with marked("story_check " + " ".join(sys.argv[1:] or ["(slice)"])):
        sys.exit(main(sys.argv[1:]))
