"""Test runs on one computer take turns (tools/runner_turns.py): several
threads build stories side by side, and runs that compete for the CPU stop
at their limit and flake (STORY-2350)."""

import importlib.util
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "tools" / "runner_turns.py"


@pytest.fixture
def turns(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("runner_turns", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "LOCK", tmp_path / "runner.lock")
    return module


def test_a_second_run_waits_its_turn_and_says_whose_it_is(turns) -> None:
    said: list[str] = []
    order: list[str] = []
    first_in = threading.Event()
    release = threading.Event()

    def first() -> None:
        with turns.turn("story_check --full in armarius-a"):
            first_in.set()
            release.wait(10)
            order.append("first done")

    holder = threading.Thread(target=first)
    holder.start()
    assert first_in.wait(10)

    def second() -> None:
        with turns.turn("story_check in armarius-b", every=0.05, say=said.append):
            order.append("second in")

    waiter = threading.Thread(target=second)
    waiter.start()
    time.sleep(0.3)
    assert order == []  # still waiting
    release.set()
    holder.join(10)
    waiter.join(10)
    assert order == ["first done", "second in"]
    assert said and "story_check --full in armarius-a" in said[0]


def test_a_free_runner_is_taken_at_once_and_given_back(turns) -> None:
    said: list[str] = []
    with turns.turn("one", say=said.append):
        pass
    with turns.turn("two", say=said.append):
        pass
    assert said == []


def test_a_run_that_died_holding_its_turn_frees_it(turns) -> None:
    holder = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import importlib.util, sys, time\n"
            f"spec = importlib.util.spec_from_file_location('t', {str(TOOL)!r})\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            f"m.LOCK = __import__('pathlib').Path({str(turns.LOCK)!r})\n"
            "with m.turn('crashing run'):\n"
            "    print('in', flush=True)\n"
            "    time.sleep(60)\n",
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "in"
    finally:
        holder.kill()
        holder.wait(10)
    done = threading.Event()

    def after() -> None:
        with turns.turn("next run", every=0.05, say=lambda _line: None):
            done.set()

    threading.Thread(target=after, daemon=True).start()
    assert done.wait(10)
