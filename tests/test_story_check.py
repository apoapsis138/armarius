"""story_check's test step (tools/story_check.py): each failure is rerun
alone by its exact id, and a flaky test fails the check as a real one does.
The runs are faked; nothing here starts pytest."""

import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace

import conftest
import pytest
from rerun_fakes import FakeRuns
from rerun_once import FAILED_IDS_ENV, Failure, failures

TOOL = Path(__file__).resolve().parent.parent / "tools" / "story_check.py"
SPACED = "tests/test_dialog_contracts_magus.py::test_form_contract[add magus]"


@pytest.fixture
def check(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("story_check", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "FLAKY_LOG", tmp_path / ".pytest_cache" / "flaky.txt")
    monkeypatch.setattr(module, "RUNNING", tmp_path / "running")
    return module


def fake_runs(check, monkeypatch, failed: dict[str, bool]) -> FakeRuns:
    """Fake every run story_check makes (rerun_fakes.FakeRuns)."""
    runs = FakeRuns(failed)
    monkeypatch.setattr(check, "run", runs)
    return runs


def test_all_green_passes(check, monkeypatch) -> None:
    fake_runs(check, monkeypatch, {})
    assert check.main([]) == 0
    assert not check.FLAKY_LOG.exists()


def test_a_flaky_test_fails_the_check_and_is_logged(check, monkeypatch, capsys):
    fake_runs(check, monkeypatch, {"tests/test_a.py::test_b": False})
    assert check.main([]) == 1
    out = capsys.readouterr().out
    assert "FAIL  slice tests" in out
    assert "FLAKY tests/test_a.py::test_b (failed in the run, passed alone)" in out
    assert "a flaky test fails the check" in out
    assert check.FLAKY_LOG.read_text(encoding="utf-8").endswith(
        " tests/test_a.py::test_b\n"
    )


def test_a_real_failure_fails_with_why(check, monkeypatch) -> None:
    fake_runs(check, monkeypatch, {"tests/test_a.py::test_b": True})
    passed, said = check.tests_step(["pytest"], 10)
    assert not passed
    assert "FAILED tests/test_a.py::test_b\n      AssertionError: assert 1 == 2" in said
    assert "FLAKY" not in said


def test_an_id_with_spaces_and_brackets_is_rerun_whole(check, monkeypatch):
    runs = fake_runs(check, monkeypatch, {SPACED: False})
    passed, said = check.tests_step(["pytest"], 10)
    assert not passed and f"FLAKY {SPACED} " in said
    assert runs.reruns() == [SPACED]  # one argument, spaces and all


def test_the_run_notes_failed_ids_only_where_it_reports(tmp_path, monkeypatch):
    """tests/conftest.py writes each failure's phase and id, from xdist's
    controller (or a run without workers), never from a worker too; and
    rerun_once reads them back whole."""
    ids = tmp_path / "failed.txt"
    monkeypatch.setenv(FAILED_IDS_ENV, str(ids))
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    report = SimpleNamespace
    conftest.pytest_runtest_logreport(report(failed=True, nodeid=SPACED, when="call"))
    conftest.pytest_runtest_logreport(report(failed=False, nodeid="x", when="call"))
    conftest.pytest_runtest_logreport(report(failed=True, nodeid="s", when="setup"))
    conftest.pytest_collectreport(report(failed=True, nodeid="tests/t.py"))
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")
    conftest.pytest_runtest_logreport(report(failed=True, nodeid="y", when="call"))
    assert failures(ids) == [
        Failure(SPACED, "call"),
        Failure("s", "setup"),
        Failure("tests/t.py", "collect"),
    ]


def test_each_run_has_its_own_running_note(monkeypatch) -> None:
    """Two runs in one folder never share a note (on Windows the second
    couldn't replace or delete the first's while it was open)."""
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    assert conftest._running_file().name == f"main-{os.getpid()}.txt"
