"""Run the tests, then run each failed test once more, alone: one that
passes alone is flaky, one that fails again is real.

`RerunOnce.check` is the routine both callers share (a Template Method):
run the suite, read which tests failed, rerun each alone by its exact id,
sort them into flaky and real. What to do with the result is the caller's:

- tools/story_check.py, on your machine, fails the check on a flaky test
  as on a real one, and notes it in the list of flaky tests to fix.
- tools/ci_tests.py, in CI, passes on a flaky test but marks it with a
  warning on the pull request and a line in the job's summary, and never
  reruns a collection, setup or teardown error.

The failed tests come from the run itself: tests/conftest.py writes each
one to the file named by FAILED_IDS_ENV, a line each of its phase and id
separated by a tab, and each id is rerun as one argument, so an id with
spaces or brackets (`test_x[add magus]`) is rerun whole.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parent.parent

#: The environment variable naming the file tests/conftest.py writes each
#: failed test to.
FAILED_IDS_ENV = "RERUN_FAILED_IDS"

#: How long a test run alone may take (seconds).
RERUN_LIMIT = 420


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


def run(
    command: list[str],
    limit: float | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str]:
    """Run `command`; its exit code and output. TimedOut past `limit`."""
    with subprocess.Popen(
        command,
        cwd=ROOT,
        env=env,
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


#: A run's command, limit and environment to its exit code and output.
Runner = Callable[[list[str], float | None, dict[str, str] | None], tuple[int, str]]


@dataclass(frozen=True)
class Failure:
    """A test that failed, and in which phase: collect, setup, call or
    teardown."""

    nodeid: str
    phase: str = "call"


def failures(ids_file: Path) -> list[Failure]:
    """The failed tests, as the run wrote them, each once."""
    if not ids_file.is_file():
        return []
    seen: dict[str, Failure] = {}
    for line in ids_file.read_text(encoding="utf-8").splitlines():
        phase, _, nodeid = line.partition("\t")
        if nodeid.strip() and nodeid not in seen:
            seen[nodeid] = Failure(nodeid, phase)
    return list(seen.values())


def summary(output: str) -> str:
    return output.strip().splitlines()[-1] if output.strip() else ""


def reason(output: str) -> str:
    """Why a test failed, from its run alone: the first `E ` line (an
    assertion or the error raised), else the last line of output."""
    for line in output.splitlines():
        # Not `-q`'s progress line for an error ("E    [100%]").
        if line.startswith("E ") and not line.rstrip().endswith("%]"):
            return line[1:].strip()[:300]
    return summary(output)


@dataclass
class Outcome:
    """What the run and the reruns found."""

    output: str
    flaky: list[Failure]
    real: list[tuple[Failure, str]]


class RerunOnce:
    """The run-then-rerun-once routine. A caller fills in `python` (how
    to start Python), and the hooks: `reruns` (which failures to try
    again) and `verdict` (pass or fail, and what to say)."""

    #: How to start Python for pytest, before `-m pytest`.
    python: ClassVar[tuple[str, ...]] = (sys.executable,)

    def __init__(self, runner: Runner = run) -> None:
        self.runner = runner

    def check(self, command: list[str], limit: float | None) -> tuple[bool, str]:
        """Run `command`; rerun each failure alone. (passed, what to say)."""
        with tempfile.TemporaryDirectory() as folder:
            ids_file = Path(folder) / "failed.txt"
            env = {**self.environment(), FAILED_IDS_ENV: str(ids_file)}
            try:
                code, output = self.run_suite(command, limit, env)
            except TimedOut:
                return False, self.stopped(limit)
            failed = failures(ids_file)
        if code == 0:
            return True, summary(output)
        # 1 is "some tests failed"; anything else (an interrupted run, a
        # collection error, a usage error) is never put right by a rerun.
        if code != 1 or not failed:
            return False, summary(output) or f"pytest exited {code}"
        outcome = Outcome(output, [], [])
        for failure in failed:
            if not self.reruns(failure):
                outcome.real.append((failure, f"a {failure.phase} error: not rerun"))
                continue
            again, said = self.run_alone(failure)
            if again == 0:
                outcome.flaky.append(failure)
            else:
                outcome.real.append((failure, reason(said)))
        return self.verdict(outcome)

    def environment(self) -> dict[str, str]:
        return dict(os.environ)

    def run_suite(
        self, command: list[str], limit: float | None, env: dict[str, str]
    ) -> tuple[int, str]:
        return self.runner(command, limit, env)

    def run_alone(self, failure: Failure) -> tuple[int, str]:
        command = [*self.python, "-m", "pytest", "-q", "-p", "no:xdist"]
        try:
            return self.runner([*command, failure.nodeid], RERUN_LIMIT, None)
        except TimedOut:
            return 1, f"stopped after {RERUN_LIMIT} s: stuck"

    def stopped(self, limit: float | None) -> str:
        return f"stopped after {limit:.0f} s, every test process with it."

    # The hooks each caller fills in.

    def reruns(self, failure: Failure) -> bool:
        """Whether to try `failure` again alone."""
        raise NotImplementedError

    def verdict(self, outcome: Outcome) -> tuple[bool, str]:
        """Pass or fail, and what to say, once every rerun is done."""
        raise NotImplementedError


def failed_lines(outcome: Outcome) -> list[str]:
    """The real failures, each with why (the first twenty)."""
    return [f"FAILED {f.nodeid}\n      {why}" for f, why in outcome.real[:20]]
