"""A stand-in for pytest runs, for testing tools/rerun_once.py's callers
(story_check, ci_tests) without starting pytest."""

from __future__ import annotations

from pathlib import Path

from rerun_once import FAILED_IDS_ENV


class FakeRuns:
    """The first run (the one given FAILED_IDS_ENV) fails the tests in
    `failed`, writing them as tests/conftest.py does, as call failures
    unless `phases` says otherwise; a rerun alone passes when
    `failed[id]` is False. Any other command passes. `commands` lists
    every command run, in order."""

    def __init__(
        self,
        failed: dict[str, bool],
        phases: dict[str, str] | None = None,
        code: int = 1,
    ) -> None:
        self.failed = failed
        self.phases = phases or {}
        self.code = code
        self.commands: list[list[str]] = []

    def __call__(
        self,
        command: list[str],
        limit: float | None = None,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str]:
        self.commands.append(command)
        if env and FAILED_IDS_ENV in env:
            if not self.failed:
                return 0, "5 passed"
            Path(env[FAILED_IDS_ENV]).write_text(
                "".join(
                    f"{self.phases.get(test, 'call')}\t{test}\n" for test in self.failed
                ),
                encoding="utf-8",
            )
            return self.code, f"{len(self.failed)} failed, 5 passed"
        if "no:xdist" in command:
            if self.failed[command[-1]]:
                return 1, "E   AssertionError: assert 1 == 2\n1 failed"
            return 0, "1 passed"
        return 0, ""

    def reruns(self) -> list[str]:
        """The ids rerun alone, each as the command's last argument."""
        return [command[-1] for command in self.commands if "no:xdist" in command]
