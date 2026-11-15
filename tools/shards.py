"""Split the test suite into shards of about equal running time, for CI.

`pytest --shard=k/n` (tests/conftest.py) keeps only the k-th of n shards.
Whole test files are dealt out, longest first, each to the shard with the
least time so far (longest-processing-time first), so a file's fixtures and
app sessions stay in one shard. A file's time is read from
tools/test_durations.json, measured on the full suite; a file not in it yet
(new since the last measurement) counts as a typical file of its tier, so a
new screen test still weighs like one.

The split depends only on the files collected and the durations file, so
every runner computes the same shards, and together they are the whole
suite, each test in exactly one.

Measure again when the suite has changed a lot:

    uv run python -m pytest -q -n auto --dist worksteal --durations=0 \\
        --durations-min=0 > durations.txt
    uv run python tools/shards.py durations.txt
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from collections.abc import Iterable
from pathlib import Path

from tiers import is_screen_test_file

ROOT = Path(__file__).resolve().parent.parent
DURATIONS = ROOT / "tools" / "test_durations.json"

#: A --durations line: "1.23s call     tests/test_x.py::test_y[z]".
_LINE = re.compile(r"^\s*([\d.]+)s\s+(?:setup|call|teardown)\s+(\S+?)::")


def parse_shard(text: str) -> tuple[int, int]:
    """ "2/4" as (2, 4); ValueError unless 1 <= k <= n."""
    k, sep, n = text.partition("/")
    if not sep or not k.isdigit() or not n.isdigit() or not 1 <= int(k) <= int(n):
        raise ValueError(f"--shard wants k/n with 1 <= k <= n, not {text!r}")
    return int(k), int(n)


def load_durations(path: Path = DURATIONS) -> dict[str, float]:
    """Seconds per test file ("tests/test_x.py"), as last measured."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: expected an object of file -> seconds")
    return {str(name): float(seconds) for name, seconds in data.items()}


def _is_screen(name: str) -> bool:
    """Whether the test file `name` ("tests/test_x.py") is a screen test (a
    file measured once but gone since counts as not)."""
    path = ROOT / name
    return path.is_file() and is_screen_test_file(path)


def _typical(durations: dict[str, float], screen: bool) -> float:
    times = [t for name, t in durations.items() if _is_screen(name) == screen]
    return statistics.median(times) if times else (10.0 if screen else 0.5)


def assign(
    files: Iterable[str], shards: int, durations: dict[str, float]
) -> dict[str, int]:
    """Each file's shard, 1..`shards`, the shards' times kept about equal."""
    typical = {screen: _typical(durations, screen) for screen in (True, False)}

    def weight(name: str) -> float:
        if name in durations:
            return durations[name]
        return typical[_is_screen(name)]

    totals = [0.0] * shards
    placed: dict[str, int] = {}
    # Longest first; the name breaks ties, so every runner agrees.
    for name in sorted(set(files), key=lambda f: (-weight(f), f)):
        lightest = min(range(shards), key=lambda i: (totals[i], i))
        totals[lightest] += weight(name)
        placed[name] = lightest + 1
    return placed


def record(text: str) -> dict[str, float]:
    """Seconds per file from a `pytest --durations=0 --durations-min=0`
    report (setup, call and teardown added up)."""
    seconds: dict[str, float] = {}
    for line in text.splitlines():
        found = _LINE.match(line)
        if found:
            name = found.group(2).replace("\\", "/")
            seconds[name] = seconds.get(name, 0.0) + float(found.group(1))
    return {name: round(t, 1) for name, t in sorted(seconds.items())}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    measured = record(Path(argv[0]).read_text(encoding="utf-8", errors="replace"))
    if not measured:
        print("shards: no durations found in that report", file=sys.stderr)
        return 1
    DURATIONS.write_text(json.dumps(measured, indent=1) + "\n", encoding="utf-8")
    print(f"{len(measured)} files, {sum(measured.values()):.0f} s -> {DURATIONS.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
