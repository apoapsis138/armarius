"""CI's test step (tools/ci_tests.py): a failed test is rerun once, alone;
one that passes then keeps the job green with a warning and a line in the
job's summary, one that fails again, or a setup or collection error, fails
the job. The runs are faked; nothing here starts pytest."""

from pathlib import Path

import ci_tests
import pytest
from rerun_fakes import FakeRuns

SPACED = "tests/test_dialog_contracts_magus.py::test_form_contract[add magus]"


class Faked(ci_tests.CiRerun):
    """CI's routine, with the suite's run faked as the reruns are (the
    real one shows its output live rather than returning it)."""

    def run_suite(self, command, limit, env):
        return self.runner(command, limit, env)


@pytest.fixture
def page(tmp_path, monkeypatch) -> Path:
    """The job's summary page."""
    path = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(path))
    return path


def ci(runs: FakeRuns) -> int:
    return ci_tests.main(["-q", "--shard=1/4"], Faked(runs))


def test_all_green_passes_without_a_warning(page, capsys) -> None:
    assert ci(FakeRuns({})) == 0
    assert "::warning" not in capsys.readouterr().out
    assert not page.exists()


def test_a_flaky_test_passes_with_a_warning_and_a_summary(page, capsys) -> None:
    runs = FakeRuns({SPACED: False})
    assert ci(runs) == 0
    out = capsys.readouterr().out
    assert f"::warning title=Flaky test::{SPACED}\n" in out
    assert "## Flaky tests" in page.read_text(encoding="utf-8")
    assert f"- `{SPACED}`" in page.read_text(encoding="utf-8")
    assert runs.reruns() == [SPACED]  # one argument, spaces and all


def test_a_test_failing_twice_fails_the_job(page, capsys) -> None:
    runs = FakeRuns({"tests/test_a.py::test_b": True, SPACED: False})
    assert ci(runs) == 1
    out = capsys.readouterr().out
    assert "FAILED tests/test_a.py::test_b" in out
    assert "::warning title=Flaky test::" in out  # the other one still warned


def test_a_setup_or_collection_error_fails_and_is_not_rerun(page) -> None:
    runs = FakeRuns(
        {"tests/test_a.py::test_b": False, "tests/test_c.py": False},
        phases={"tests/test_a.py::test_b": "setup", "tests/test_c.py": "collect"},
    )
    assert ci(runs) == 1
    assert runs.reruns() == []


def test_an_interrupted_run_fails_even_if_its_failures_pass_alone(page) -> None:
    runs = FakeRuns({"tests/test_a.py::test_b": False}, code=2)
    assert ci(runs) == 1
    assert runs.reruns() == []


def test_the_whole_arguments_reach_pytest() -> None:
    runs = FakeRuns({})
    ci(runs)
    assert runs.commands[0][-4:] == ["-m", "pytest", "-q", "--shard=1/4"]


def test_a_warning_is_escaped() -> None:
    assert ci_tests.escaped("a%b\nc") == "a%25b%0Ac"
