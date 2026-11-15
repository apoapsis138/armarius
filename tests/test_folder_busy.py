"""The busy mark story_check leaves while it runs, so a thread sharing the
folder waits before a stash or pull (tools/folder_busy.py)."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "tools" / "folder_busy.py"


@pytest.fixture
def busy(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("folder_busy", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "MARK", tmp_path / "folder_busy.json")
    return module


def test_the_folder_is_busy_only_while_marked(busy) -> None:
    assert busy.busy() == ""
    with busy.marked("story_check --full"):
        assert busy.busy().startswith("story_check --full since ")
        assert busy.main() == 1
    assert busy.busy() == "" and not busy.MARK.exists()
    assert busy.main() == 0


def test_a_mark_left_by_an_ended_run_is_cleared(busy) -> None:
    finished = subprocess.Popen([sys.executable, "-c", "pass"])
    finished.wait()
    busy.MARK.write_text(
        json.dumps({"what": "story_check", "pid": finished.pid, "started": "x"}),
        encoding="utf-8",
    )
    assert busy.busy() == "" and not busy.MARK.exists()
    busy.MARK.write_text("{not json", encoding="utf-8")
    assert busy.busy() == "" and not busy.MARK.exists()
