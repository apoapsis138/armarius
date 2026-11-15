"""tools/shards.py and pytest --shard=k/n: CI's four runners each take a
quarter of the suite, by time, and together run every test exactly once."""

from __future__ import annotations

import subprocess
import sys

import pytest
import shards

from ars_magica_manager import ROOT

#: A few quick files, enough for four shards to collect from each.
SAMPLE = (
    "tests/test_release_notes.py",
    "tests/test_changelog.py",
    "tests/test_version.py",
    "tests/test_shards.py",
    "tests/test_startup_weight.py",
)


def test_every_file_lands_in_exactly_one_shard_and_the_times_balance():
    durations = shards.load_durations()
    files = sorted({*durations, "tests/test_not_measured_yet.py"})
    placed = shards.assign(files, 4, durations)
    assert set(placed) == set(files)
    assert set(placed.values()) == {1, 2, 3, 4}
    totals = [
        sum(durations.get(f, 0.0) for f, k in placed.items() if k == shard)
        for shard in (1, 2, 3, 4)
    ]
    # The biggest file is far smaller than a quarter, so the shards come out
    # within a few percent of each other.
    assert max(totals) - min(totals) < 0.05 * sum(totals) / 4, totals


def test_the_split_is_the_same_whatever_order_the_files_come_in():
    durations = shards.load_durations()
    files = sorted(durations)
    assert shards.assign(files, 4, durations) == shards.assign(
        reversed(files), 4, durations
    )


def test_a_file_not_measured_yet_weighs_like_its_tier():
    durations = {"tests/test_a.py": 1.0, "tests/test_b.py": 1.0}
    placed = shards.assign(["tests/test_a.py", "tests/test_new.py"], 2, durations)
    assert sorted(placed.values()) == [1, 2]


@pytest.mark.parametrize("bad", ["", "4", "0/4", "5/4", "a/b", "2/"])
def test_a_bad_shard_is_refused(bad):
    with pytest.raises(ValueError, match="k/n"):
        shards.parse_shard(bad)


def test_reading_a_durations_report():
    report = (
        "======== slowest durations ========\n"
        "2.50s call     tests/test_x.py::test_one[a]\n"
        "0.25s setup    tests/test_x.py::test_one[a]\n"
        "1.00s call     tests\\test_y.py::test_two\n"
    )
    assert shards.record(report) == {"tests/test_x.py": 2.8, "tests/test_y.py": 1.0}


def _collected(*args: str) -> set[str]:
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:xdist"]
        + list(args),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
    return {line for line in done.stdout.splitlines() if "::" in line}


def test_the_shards_are_disjoint_and_together_the_whole_collection():
    whole = _collected(*SAMPLE)
    parts = [_collected(*SAMPLE, f"--shard={k}/4") for k in (1, 2, 3, 4)]
    assert sum(len(p) for p in parts) == len(whole)
    assert set().union(*parts) == whole
