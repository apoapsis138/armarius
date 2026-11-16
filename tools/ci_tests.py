"""The test step in CI (.github/workflows/checks.yml): pytest with the
arguments given, then each failed test once more, alone.

    uv run python tools/ci_tests.py -q -n auto --dist worksteal --shard=1/4

A test that passes alone is flaky: the job stays green, but the test is
marked with a warning on the pull request (`::warning title=Flaky
test::<id>`) and listed under "Flaky tests" in the job's summary, to be
made a story the same day (CONTRIBUTING.md). A test that fails again is
real, and the job fails. A collection, setup or teardown error is never
rerun: it fails the job. The rerun itself is tools/rerun_once.py's,
shared with story_check.
"""

from __future__ import annotations

import os
import subprocess
import sys

from rerun_once import ROOT, Failure, Outcome, RerunOnce, failed_lines, summary


def escaped(text: str) -> str:
    """`text` made safe for a GitHub workflow command's message."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


class CiRerun(RerunOnce):
    """In CI: only a test's own failure is tried again, and a flaky test
    passes the job with a warning and a line in its summary."""

    def run_suite(
        self, command: list[str], limit: float | None, env: dict[str, str]
    ) -> tuple[int, str]:
        # Shown as it runs, in the job's log; the output isn't needed.
        code = subprocess.run(command, cwd=ROOT, env=env, check=False).returncode
        return code, ""

    def run_alone(self, failure: Failure) -> tuple[int, str]:
        print(f"Rerunning alone: {failure.nodeid}", flush=True)
        code, said = super().run_alone(failure)
        print(said, flush=True)
        return code, said

    def reruns(self, failure: Failure) -> bool:
        return failure.phase == "call"

    def verdict(self, outcome: Outcome) -> tuple[bool, str]:
        lines: list[str] = []
        for failure in outcome.flaky:
            lines.append(f"::warning title=Flaky test::{escaped(failure.nodeid)}")
        self.summarize(outcome.flaky)
        lines += failed_lines(outcome)
        if outcome.flaky:
            lines.append(
                f"{len(outcome.flaky)} flaky (failed in the run, passed alone): "
                "make each a story today (CONTRIBUTING.md)."
            )
        if outcome.real:
            lines.append(f"{len(outcome.real)} failed again alone.")
        lines.append(summary(outcome.output))
        return not outcome.real, "\n".join(line for line in lines if line)

    def summarize(self, flaky: list[Failure]) -> None:
        """List the flaky tests in the job's summary page, if there is one."""
        path = os.environ.get("GITHUB_STEP_SUMMARY")
        if not flaky or not path:
            return
        with open(path, "a", encoding="utf-8") as page:
            page.write("## Flaky tests\n\n")
            page.write("Failed in the run, passed alone:\n\n")
            page.writelines(f"- `{failure.nodeid}`\n" for failure in flaky)
            page.write("\n")


def main(argv: list[str], rerun: RerunOnce | None = None) -> int:
    routine = rerun if rerun is not None else CiRerun()
    passed, said = routine.check([*routine.python, "-m", "pytest", *argv], None)
    print(said, flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
