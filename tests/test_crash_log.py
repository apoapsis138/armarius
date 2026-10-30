"""A fatal crash leaves the Python stack in the data folder's crash.log.
Run in a process of its own: pytest keeps faulthandler for itself."""

from __future__ import annotations

import subprocess
import sys

from ars_magica_manager import crash_log, paths


def _run(tmp_path, *lines: str) -> subprocess.CompletedProcess[str]:
    script = "\n".join(
        [
            "import faulthandler, pathlib, sys",
            "from ars_magica_manager import crash_log, paths",
            "paths.use_data_dir(pathlib.Path(sys.argv[1]))",
            *lines,
        ]
    )
    return subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_log_is_in_the_data_folder():
    assert crash_log.log_path() == paths.data_dir() / "crash.log"


def test_starting_turns_on_the_trace_with_an_empty_log(tmp_path):
    run = _run(
        tmp_path,
        "crash_log.start()",
        "print(faulthandler.is_enabled())",
    )
    assert run.stdout.strip() == "True", run.stderr
    assert (tmp_path / "crash.log").read_text() == ""


def test_a_log_that_cannot_be_opened_leaves_the_app_running(tmp_path):
    (tmp_path / "crash.log").mkdir()
    run = _run(tmp_path, "crash_log.start()", "print('running')")
    assert run.stdout.strip() == "running", run.stderr
